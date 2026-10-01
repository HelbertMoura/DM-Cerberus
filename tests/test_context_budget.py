import json
import tempfile
import unittest
from pathlib import Path

from engine.context_budget import context_pack_result, fit_context_pack
from engine.index import SQLiteMemoryIndex
from engine.mcp_server import CerberusMCPServer
from engine.models import ContextPack, MemoryItem, MemoryStatus, SourceType
from engine.retrieval import CerberusMemoryService
from engine.search import HybridSearchEngine


class TestContextPackBudget(unittest.TestCase):
    def item(self, number, source=None):
        return MemoryItem(memory_id=f"memory-{number}", project_id="biolar",
            source_path=source or f"projects/biolar/wiki/topic-{number}.md",
            source_type=SourceType.WIKI, title="Arquitetura com acentuação " * 40,
            snippet="Evidência íntegra com aspas \" e barra \\ " * 40)

    def test_complete_serialized_results_fit_all_supported_budgets(self):
        for budget in (256, 257, 500, 1000, 1500):
            for text in ("Revisar arquitetura " * 300, "\x00\n\t\"\\" * 300):
                with self.subTest(budget=budget, controls=text.startswith("\x00")):
                    pack = ContextPack(project_id=text, role=text, task_summary=text,
                        relevant_architecture=[self.item(n) for n in range(20)])
                    result = context_pack_result(fit_context_pack(pack, budget))
                    serialized = json.dumps(result, ensure_ascii=False, indent=2)
                    self.assertLessEqual(len(serialized), budget * 4)
                    self.assertEqual((len(serialized) + 3) // 4, result["token_estimate"])
                    self.assertTrue(result["truncated"])

    def test_budget_fitting_preserves_sources_and_does_not_modify_input(self):
        entry = self.item(1)
        pack = ContextPack(project_id="biolar", role="DEVELOPER", task_summary="Arquitetura",
                           relevant_architecture=[entry])
        original = entry.to_dict()
        bounded = fit_context_pack(pack, 1500)
        self.assertIn(entry.source_path, bounded.to_markdown())
        self.assertEqual(original, entry.to_dict())
        self.assertIsNot(entry, bounded.relevant_architecture[0])

    def test_oversized_source_is_omitted_without_breaking_json(self):
        pack = ContextPack(project_id="biolar", role="QA", task_summary="Revisar fontes",
            relevant_architecture=[self.item(1, "projects/biolar/" + "x" * 10000 + ".md"), self.item(2)])
        result = context_pack_result(fit_context_pack(pack, 1500))
        self.assertIn("topic-2.md", result["markdown"])
        self.assertNotIn("x" * 10000, result["markdown"])
        self.assertTrue(result["truncated"])
        self.assertLessEqual(len(json.dumps(result, ensure_ascii=False, indent=2)), 6000)

    def test_duplicate_memory_is_not_repeated_across_groups(self):
        entry = self.item(1)
        pack = ContextPack(project_id="biolar", role="QA", task_summary="Arquitetura",
            relevant_decisions=[entry], relevant_architecture=[entry], relevant_learnings=[entry])
        result = context_pack_result(fit_context_pack(pack, 1500))
        self.assertEqual(1, result["markdown"].count(entry.source_path))

    def test_sensitive_task_text_is_redacted(self):
        secret = "sk-abcdefghijklmnopqrstuvwx"
        pack = ContextPack(project_id="biolar", role="QA", task_summary="Revisar token: " + secret)
        self.assertNotIn(secret, context_pack_result(fit_context_pack(pack, 1500))["markdown"])

    def test_quoted_secrets_are_redacted_before_pack_trim_and_hook_delivery(self):
        from engine.agent_hooks import _render_context
        from engine.session_delivery import session_token
        entry = self.item(1)
        entry.title = "Referência curta"
        entry.snippet = '{"password": "' + ("private value " * 60) + '"}'
        pack = ContextPack(project_id="biolar", role="QA", task_summary="Arquitetura",
                           relevant_architecture=[entry])
        bounded = fit_context_pack(pack, 1500)
        for rendered in (bounded.to_markdown(),
                         _render_context(pack, 6000, set(), True, session_token("test-redaction"))[0]):
            self.assertNotIn("private value", rendered)
            self.assertIn("[REDACTED]", rendered)

    def test_invalid_budget_cannot_disable_the_cap(self):
        pack = ContextPack(project_id="biolar", role="QA", task_summary="Arquitetura")
        for value in (-1, 0, 255, 1501, True, "1500", None):
            with self.subTest(value=value), self.assertRaises(ValueError):
                fit_context_pack(pack, value)


class TestCurrentMemoryAndMCP(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        for status in ("ativo", "superseded", "deprecated", "draft", "proposta"):
            path = self.root / "projects/biolar/wiki" / f"{status}.md"
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(f"---\nstatus: {status}\n---\n# Arquitetura {status}\n\n"
                            f"Arquitetura banco memória ONLY-{status}.", encoding="utf-8")
        self.index = SQLiteMemoryIndex(self.root / ".cerberus/index.db")
        self.index.index_roots([self.root])
        self.service = CerberusMemoryService(self.index)
        self.server = CerberusMCPServer(service=self.service)

    def call(self, name, arguments):
        return self.server.handle_message({"jsonrpc": "2.0", "id": 1, "method": "tools/call",
            "params": {"name": name, "arguments": arguments}})

    def test_all_search_modes_exclude_inactive_memory_and_preserve_history(self):
        for mode in ("lexical", "semantic", "hybrid"):
            with self.subTest(mode=mode):
                results = self.service.search("arquitetura banco memória", project_id="biolar", mode=mode)
                self.assertTrue(results)
                self.assertTrue(all(row.item.status == MemoryStatus.ACTIVE for row in results))
                self.assertEqual({"projects/biolar/wiki/ativo.md"}, {row.item.source_path for row in results})
        self.assertEqual(5, len(self.index.all_items()))
        self.assertTrue((self.root / "projects/biolar/wiki/superseded.md").exists())

    def test_semantic_refresh_removes_newly_deprecated_vectors(self):
        engine = HybridSearchEngine(self.index)
        engine.search("arquitetura banco", project_id="biolar", mode="semantic")
        active_ids = engine.vector_store.ids()
        self.assertTrue(active_ids)
        path = self.root / "projects/biolar/wiki/ativo.md"
        path.write_text("---\nstatus: deprecated\n---\n# Arquitetura antiga\n\nArquitetura banco memória.", encoding="utf-8")
        self.index.index_roots([self.root], force_reindex=True)
        self.assertEqual([], engine.search("arquitetura banco", project_id="biolar", mode="semantic"))
        self.assertEqual(set(), engine.vector_store.ids())
        self.assertEqual(5, len(self.index.all_items()))

    def test_context_pack_and_mcp_search_return_only_active_sources(self):
        for name, args in (("cerberus_get_context_pack", {"project_id": "biolar", "task_summary": "arquitetura banco"}),
                           ("cerberus_search_memory", {"project_id": "biolar", "query": "arquitetura banco"})):
            with self.subTest(tool=name):
                response = self.call(name, args)
                text = response["result"]["content"][0]["text"]
                self.assertIn("ativo.md", text)
                for status in ("superseded", "deprecated", "draft", "proposta"):
                    self.assertNotIn(f"{status}.md", text)

    def test_mcp_wire_content_obeys_requested_budget_and_reports_it(self):
        for budget in (256, 1500):
            with self.subTest(budget=budget):
                response = self.call("cerberus_get_context_pack", {"project_id": "biolar",
                    "task_summary": "arquitetura banco " + "linha\n" * 3000, "max_tokens": budget})
                text = response["result"]["content"][0]["text"]
                result = json.loads(text)
                self.assertLessEqual(len(text), budget * 4)
                self.assertEqual(budget * 4, result["budget_chars"])
                self.assertEqual((len(text) + 3) // 4, result["token_estimate"])

    def test_mcp_rejects_budgets_and_counts_outside_declared_range(self):
        cases = [("cerberus_get_context_pack", {"project_id": "biolar", "task_summary": "arquitetura", "max_tokens": value})
                 for value in (255, 1501, True)]
        cases += [(tool, {**args, "limit": value})
                  for tool, args in (("cerberus_search_memory", {"query": "arquitetura"}),
                                     ("cerberus_get_decisions", {})) for value in (-1, 0, 21, True)]
        for tool, args in cases:
            with self.subTest(tool=tool, args=args):
                self.assertEqual(-32602, self.call(tool, args)["error"]["code"])

    def test_local_architecture_precedes_global_competitors(self):
        for number in range(4):
            path = self.root / "wiki" / f"global-{number}.md"
            path.parent.mkdir(exist_ok=True)
            path.write_text("# Arquitetura banco memória\n\n" + "Arquitetura banco memória " * 10, encoding="utf-8")
        self.index.index_roots([self.root], force_reindex=True)
        pack = self.service.build_context_pack("biolar", "arquitetura banco memória")
        self.assertTrue(pack.relevant_architecture)
        self.assertEqual("biolar", pack.relevant_architecture[0].project_id)
