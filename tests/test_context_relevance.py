"""Task-specific context selection against real, temporary Markdown indexes."""

import json
import tempfile
import unittest
from pathlib import Path

from engine.context_budget import context_pack_result
from engine.index import SQLiteMemoryIndex
from engine.retrieval import CerberusMemoryService


GROUP_FILES = {
    "relevant_decisions": "decisions.md",
    "relevant_architecture": "architecture.md",
    "relevant_learnings": "learnings.md",
}


class TestContextRelevance(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.write("projects/alpha/decisions.md", "ADR decisao")
        self.write("projects/alpha/architecture.md", "arquitetura stack banco")
        self.write("projects/alpha/learnings.md", "gotchas gotcha erro licao")
        self.write("global/ai-governance.md", "governance modelo routing autoridade")
        self.write("projects/alpha/handover.md", "handover continuidade estado atual")
        self.index = SQLiteMemoryIndex(self.root / ".cerberus/index.db")
        self.service = CerberusMemoryService(self.index)

    def write(self, path, text, status="ativo"):
        source = self.root / path
        source.parent.mkdir(parents=True, exist_ok=True)
        source.write_text(f"---\nstatus: {status}\n---\n# Registro\n\n{text}.\n", encoding="utf-8")

    def write_topic(self, directory, text="laser", status="ativo"):
        for filename in GROUP_FILES.values():
            self.write(f"{directory}/{filename}", text, status)

    def pack(self, query, budget=1500):
        self.index.index_roots([self.root], force_reindex=True)
        return self.service.build_context_pack("alpha", query, max_tokens=budget)

    def assert_empty_task_groups(self, pack):
        for group in GROUP_FILES:
            with self.subTest(group=group):
                self.assertEqual([], getattr(pack, group))

    def test_unmatched_task_omits_generic_sources_but_keeps_general_context(self):
        pack = self.pack("zeppelinx")
        self.assert_empty_task_groups(pack)
        self.assertEqual(["global/ai-governance.md"], [item.source_path for item in pack.mandatory_rules])
        self.assertEqual(["projects/alpha/handover.md"], [item.source_path for item in pack.recent_handoff])

    def test_empty_task_has_no_task_specific_sources(self):
        for query in ("", "   "):
            with self.subTest(query=query):
                self.assert_empty_task_groups(self.pack(query))

    def test_real_task_match_returns_each_source_type(self):
        self.write_topic("projects/alpha/topic")
        pack = self.pack("laser")
        for group, filename in GROUP_FILES.items():
            with self.subTest(group=group):
                self.assertEqual([f"projects/alpha/topic/{filename}"],
                                 [item.source_path for item in getattr(pack, group)])

    def test_relevant_global_sources_fill_when_local_sources_only_match_generic_words(self):
        self.write_topic("shared")
        pack = self.pack("laser")
        for group, filename in GROUP_FILES.items():
            with self.subTest(group=group):
                self.assertEqual([f"shared/{filename}"],
                                 [item.source_path for item in getattr(pack, group)])

    def test_relevant_local_sources_precede_relevant_global_sources(self):
        self.write_topic("projects/alpha/topic")
        self.write_topic("shared", "laser " * 20)
        pack = self.pack("laser")
        for group, filename in GROUP_FILES.items():
            with self.subTest(group=group):
                self.assertEqual([f"projects/alpha/topic/{filename}", f"shared/{filename}"],
                                 [item.source_path for item in getattr(pack, group)])

    def test_inactive_and_other_project_matches_are_excluded(self):
        self.write_topic("projects/alpha/old", status="deprecated")
        self.write_topic("projects/beta/topic")
        self.assert_empty_task_groups(self.pack("laser"))

    def test_task_context_preserves_supported_json_budgets(self):
        self.write_topic("projects/alpha/topic", "laser " + "evidence " * 100)
        for budget in (256, 1500):
            with self.subTest(budget=budget):
                pack = self.pack("laser " * 1000, budget)
                result = context_pack_result(pack)
                serialized = json.dumps(result, ensure_ascii=False, indent=2)
                self.assertLessEqual(len(serialized), budget * 4)
                self.assertEqual(budget * 4, result["budget_chars"])
                self.assertEqual((len(serialized) + 3) // 4, result["token_estimate"])


if __name__ == "__main__":
    unittest.main()
