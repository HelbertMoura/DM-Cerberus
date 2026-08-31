"""
Unit & Integration Tests for Cerberus Memory Intelligence Engine
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

import unittest
import tempfile
import shutil
import json
from pathlib import Path

from engine.models import MemoryItem, SourceType, AuthorityLevel, MemoryStatus
from engine.parser import parse_frontmatter, parse_markdown_file, resolve_project_and_type
from engine.index import SQLiteMemoryIndex
from engine.retrieval import CerberusMemoryService
from engine.mcp_server import CerberusMCPServer


class TestParser(unittest.TestCase):
    def test_parse_frontmatter(self):
        content = """---
titulo: Teste Frontmatter
tags: [arquitetura, sefaz, tcu]
atualizado: 2026-08-30
status: ativo
---
# Document Body
Texto explicativo aqui."""
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["titulo"], "Teste Frontmatter")
        self.assertEqual(fm["tags"], ["arquitetura", "sefaz", "tcu"])
        self.assertEqual(fm["status"], "ativo")
        self.assertIn("Texto explicativo aqui.", body)

    def test_resolve_project_and_type(self):
        root = Path("C:/DevManiacs/DM-Cerebro")
        p_path = root / "projects" / "canteirohub" / "arquitetura.md"
        proj, stype, auth = resolve_project_and_type(p_path, root)
        self.assertEqual(proj, "canteirohub")
        self.assertEqual(stype, SourceType.ARCHITECTURE)
        self.assertEqual(auth, AuthorityLevel.ARCHITECTURE.value)

        g_path = root / "global" / "ai-governance.md"
        proj, stype, auth = resolve_project_and_type(g_path, root)
        self.assertEqual(proj, "_global")
        self.assertEqual(stype, SourceType.GOVERNANCE)
        self.assertEqual(auth, AuthorityLevel.GOVERNANCE.value)


class TestIndexAndRetrieval(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "test_index.db"
        self.index = SQLiteMemoryIndex(db_path=self.db_path)

        # Create mock project files
        self.mock_root = self.temp_dir / "brain_mock"
        self.mock_root.mkdir()

        # Global governance doc
        global_dir = self.mock_root / "global"
        global_dir.mkdir()
        (global_dir / "ai-governance.md").write_text("""---
titulo: AI Governance
tags: [governance, ai, triade]
---
# AI Governance
O modelo canônico é o protocolo multi-agente com gates estritos e autoridade humana.
""", encoding="utf-8")

        # Project ADR doc
        proj_dir = self.mock_root / "projects" / "canteirohub"
        proj_dir.mkdir(parents=True)
        (proj_dir / "decisions.md").write_text("""---
titulo: ADRs CanteiroHUB
tags: [adr, decisoes]
---
# Decisões do Projeto

## ADR-012: Cofre Criptográfico A1 SEFAZ
Implementar criptografia AES-256-GCM com HKDF e chaves derivadas por tenant para DF-e.

## ADR-004: Rateio de Nota Fiscal Maior Resíduo TCU
Implementar rateio matricial pelo algoritmo de Hamilton (Maior Resíduo) sem dízimas.
""", encoding="utf-8")

        # Learnings doc
        (self.mock_root / "learnings.md").write_text("""---
titulo: Lições Aprendidas Corporativas
tags: [godot, django, tdd]
---
# Lições Aprendidas
Em Godot 4.x usar sempre TABS e Sinais tipados para evitar get_parent.
Em Django usar Pydantic v2 e isolamento estrito de tenant.
""", encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_indexing_and_search(self):
        stats = self.index.index_roots([self.mock_root])
        self.assertGreaterEqual(stats["indexed_files"], 3)
        self.assertGreaterEqual(stats["total_chunks"], 3)

        # Test search SEFAZ
        results = self.index.search("SEFAZ AES", project_id="canteirohub")
        self.assertTrue(len(results) > 0)
        self.assertIn("ADR-012", results[0].item.title)
        self.assertEqual(results[0].item.source_type, SourceType.CANONICAL_ADR)

        # Test search Godot
        results_godot = self.index.search("Godot TABS sinais")
        self.assertTrue(len(results_godot) > 0)
        self.assertIn("Lições Aprendidas", results_godot[0].item.title)

    def test_project_isolation(self):
        self.index.index_roots([self.mock_root])

        # Search within canteirohub with global included
        res = self.index.search("AI Governance", project_id="canteirohub", include_global=True)
        self.assertTrue(len(res) > 0)
        self.assertEqual(res[0].item.project_id, "_global")

        # Search within biolar should NOT find canteirohub specific ADRs when include_global=False
        res_biolar = self.index.search("Cofre Criptográfico A1", project_id="biolar", include_global=False)
        self.assertEqual(len(res_biolar), 0)

    def test_context_pack_generation(self):
        self.index.index_roots([self.mock_root])
        service = CerberusMemoryService(index=self.index)

        pack = service.build_context_pack(
            project_id="canteirohub",
            task_summary="Implementar Cofre Criptográfico SEFAZ",
            role="DEVELOPER"
        )
        self.assertIsNotNone(pack)
        self.assertTrue(len(pack.relevant_decisions) > 0)
        md = pack.to_markdown()
        self.assertIn("CERBERUS CONTEXT PACK", md)
        self.assertIn("ADR-012", md)


class TestMCPServer(unittest.TestCase):
    def setUp(self):
        self.temp_dir = Path(tempfile.mkdtemp())
        self.db_path = self.temp_dir / "mcp_index.db"
        self.index = SQLiteMemoryIndex(db_path=self.db_path)
        self.service = CerberusMemoryService(index=self.index)
        self.server = CerberusMCPServer(service=self.service)

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_initialize_and_tools_list(self):
        init_req = {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}}
        init_resp = self.server.handle_message(init_req)
        self.assertEqual(init_resp["result"]["serverInfo"]["name"], "cerberus-memory-engine")

        tools_req = {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}}
        tools_resp = self.server.handle_message(tools_req)
        tool_names = [t["name"] for t in tools_resp["result"]["tools"]]
        self.assertIn("cerberus_search_memory", tool_names)
        self.assertIn("cerberus_get_context_pack", tool_names)
        self.assertIn("cerberus_get_decisions", tool_names)
        self.assertIn("cerberus_get_learnings", tool_names)


if __name__ == "__main__":
    unittest.main()
