"""Phase P4 hybrid lexical/vector retrieval regression tests."""

import json
import math
import socket
import tempfile
import threading
import unittest
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

from engine.embeddings import (
    EmbeddingProvider,
    HashingDenseEmbeddingProvider,
    VectorStore,
)
from engine.index import SQLiteMemoryIndex
from engine.mcp_server import CerberusMCPServer
from engine.retrieval import CerberusMemoryService
from engine.search import reciprocal_rank_fusion
from engine.server import DEFAULT_HOST, UI_HTML, make_server


class TestHashingDenseEmbeddingProvider(unittest.TestCase):
    def test_vectors_are_deterministic_normalized_and_fixed_size(self) -> None:
        provider = HashingDenseEmbeddingProvider(dimension=64)
        first = provider.embed("Criptografia AES-256 para certificados")
        second = provider.embed("Criptografia AES-256 para certificados")
        self.assertIsInstance(provider, EmbeddingProvider)
        self.assertEqual(first, second)
        self.assertEqual(64, len(first))
        self.assertAlmostEqual(1.0, math.sqrt(sum(v * v for v in first)), places=6)

    def test_subword_features_relate_morphological_variants(self) -> None:
        provider = HashingDenseEmbeddingProvider(dimension=128)
        query = provider.embed("criptografico")
        related = provider.embed("criptografia")
        unrelated = provider.embed("horticultura")
        related_score = sum(a * b for a, b in zip(query, related))
        unrelated_score = sum(a * b for a, b in zip(query, unrelated))
        self.assertGreater(related_score, unrelated_score)


class TestVectorStore(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "vectors.db"
        self.store = VectorStore(self.db_path)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_float32_roundtrip_and_dimension_validation(self) -> None:
        self.store.upsert("doc-a", "alpha", [1.0, 0.0, 0.0])
        vector = self.store.get("doc-a")
        self.assertEqual(3, len(vector))
        self.assertAlmostEqual(1.0, vector[0], places=6)
        with self.assertRaises(ValueError):
            self.store.upsert("bad", "alpha", [])

    def test_similarity_search_filters_project_and_is_deterministic(self) -> None:
        self.store.upsert("doc-b", "alpha", [1.0, 0.0])
        self.store.upsert("doc-a", "alpha", [1.0, 0.0])
        self.store.upsert("doc-global", "_global", [0.8, 0.6])
        self.store.upsert("doc-other", "beta", [1.0, 0.0])
        matches = self.store.search(
            [1.0, 0.0], project_id="alpha", include_global=True, limit=3
        )
        self.assertEqual(["doc-a", "doc-b", "doc-global"],
                         [match.doc_id for match in matches])
        self.assertNotIn("doc-other", [match.doc_id for match in matches])

    def test_delete_missing_prunes_stale_vectors(self) -> None:
        self.store.upsert("keep", "alpha", [1.0, 0.0])
        self.store.upsert("stale", "alpha", [0.0, 1.0])
        self.assertEqual(1, self.store.delete_missing({"keep"}))
        self.assertIsNone(self.store.get("stale"))


class TestRRF(unittest.TestCase):
    def test_formula_weights_and_tie_break_are_deterministic(self) -> None:
        fused = reciprocal_rank_fusion(
            lexical_ids=["lex-only", "both", "tie-b"],
            semantic_ids=["sem-only", "both", "tie-a"],
            k=60,
            lexical_weight=1.0,
            semantic_weight=1.0,
        )
        expected_both = 1.0 / 62.0 + 1.0 / 62.0
        self.assertAlmostEqual(expected_both, fused[0].score)
        self.assertEqual("both", fused[0].doc_id)
        tied = [entry.doc_id for entry in fused if entry.doc_id.startswith("tie-")]
        self.assertEqual(["tie-a", "tie-b"], tied)


class TestHybridServiceIntegration(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        project = self.root / "projects" / "alpha"
        project.mkdir(parents=True)
        (project / "architecture.md").write_text(
            "# Segurança Criptográfica\n\nCriptografia forte protege certificados.\n",
            encoding="utf-8",
        )
        other = self.root / "projects" / "beta"
        other.mkdir(parents=True)
        (other / "architecture.md").write_text(
            "# Outro Projeto\n\nCriptografia exclusiva do projeto beta.\n",
            encoding="utf-8",
        )
        self.index = SQLiteMemoryIndex(self.root / "index.db")
        self.index.rebuild([self.root])
        self.service = CerberusMemoryService(self.index)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_service_supports_all_modes_and_project_isolation(self) -> None:
        lexical = self.service.search("criptografia", "alpha", mode="lexical")
        semantic = self.service.search("criptografico", "alpha", mode="semantic")
        hybrid = self.service.search("criptografia", "alpha", mode="hybrid")
        self.assertTrue(lexical)
        self.assertTrue(semantic)
        self.assertTrue(hybrid)
        for result in lexical + semantic + hybrid:
            self.assertIn(result.item.project_id, {"alpha", "_global"})
        self.assertEqual("semantic", semantic[0].search_mode)
        self.assertEqual("hybrid", hybrid[0].search_mode)

    def test_invalid_mode_fails_closed(self) -> None:
        with self.assertRaises(ValueError):
            self.service.search("query", mode="invalid")

    def test_semantic_backfill_refreshes_changed_document_vector(self) -> None:
        self.service.search("criptografia", "alpha", mode="semantic")
        item = next(item for item in self.index.all_items()
                    if item.project_id == "alpha")
        before = self.service.hybrid_search.vector_store.get(item.memory_id)
        source = self.root / "projects" / "alpha" / "architecture.md"
        source.write_text(
            "# Segurança Botânica\n\nHorticultura, sementes e irrigação.\n",
            encoding="utf-8",
        )
        self.index.rebuild([self.root])
        self.service.search("horticultura", "alpha", mode="semantic")
        after = self.service.hybrid_search.vector_store.get(item.memory_id)
        self.assertNotEqual(before, after)


class _ServerHandle:
    def __init__(self, root: Path, service: CerberusMemoryService) -> None:
        sock = socket.socket()
        sock.bind((DEFAULT_HOST, 0))
        self.port = sock.getsockname()[1]
        sock.close()
        self.server = make_server(DEFAULT_HOST, self.port, root,
                                  service=service, auth_disabled=True)
        self.thread = threading.Thread(target=self.server.serve_forever,
                                       daemon=True)

    def __enter__(self):
        self.thread.start()
        return self

    def __exit__(self, *_args):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def get(self, path: str):
        try:
            with urllib.request.urlopen(
                    f"http://{DEFAULT_HOST}:{self.port}{path}", timeout=10) as response:
                return response.status, json.loads(response.read())
        except urllib.error.HTTPError as exc:
            return exc.code, json.loads(exc.read())


class TestHybridAPIAndMCP(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "LEARNINGS.md").write_text(
            "# Criptografia\n\nCertificados criptográficos seguros.\n", encoding="utf-8"
        )
        self.index = SQLiteMemoryIndex(self.root / "index.db")
        self.index.rebuild([self.root])
        self.service = CerberusMemoryService(self.index)

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_api_accepts_modes_and_rejects_invalid_mode(self) -> None:
        with _ServerHandle(self.root, self.service) as server:
            for mode in ("hybrid", "lexical", "semantic"):
                status, payload = server.get(
                    "/api/search?q=criptografia&mode=" + mode
                )
                self.assertEqual(200, status)
                self.assertEqual(mode, payload["mode"])
            status, _ = server.get("/api/search?q=x&mode=invalid")
            self.assertEqual(400, status)

    def test_mcp_schema_and_call_support_mode(self) -> None:
        server = CerberusMCPServer(service=self.service)
        definition = next(tool for tool in server.get_tool_definitions()
                          if tool["name"] == "cerberus_search_memory")
        self.assertEqual(["hybrid", "lexical", "semantic"],
                         definition["inputSchema"]["properties"]["mode"]["enum"])
        payload = server.handle_tool_call("cerberus_search_memory", {
            "query": "criptografia", "mode": "semantic", "limit": 5,
        })
        self.assertTrue(payload)
        self.assertEqual("semantic", payload[0]["search_mode"])

    def test_inspector_exposes_mode_selector_and_score_metadata(self) -> None:
        self.assertIn('id="search-mode"', UI_HTML)
        self.assertIn('value="hybrid"', UI_HTML)
        self.assertIn("item.search_mode", UI_HTML)
        self.assertIn("item.final_score", UI_HTML)


if __name__ == "__main__":
    unittest.main()
