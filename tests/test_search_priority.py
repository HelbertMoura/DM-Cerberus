import tempfile
import unittest
from pathlib import Path

from engine.index import SQLiteMemoryIndex


class TestRareTermSearchPriority(unittest.TestCase):
    """Regressão: termo raro/distintivo deve vencer repetição de termos comuns.

    Caso real (2026-09-08): buscar "DORMENTES QA independente" não trazia o
    chunk promovido em LEARNINGS.md — chunks que só repetiam "QA"/
    "independente" ganhavam o viés de tf/título do BM25.
    """

    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "qa-policy.md").write_text(
            "# QA Policy\n\n"
            "## Pipeline de QA independente\n\n"
            "O QA independente revisa cada task. O QA independente aprova. "
            "O QA independente rejeita. QA independente é obrigatório em todo "
            "pipeline de QA independente.\n",
            encoding="utf-8",
        )
        (self.root / "learnings.md").write_text(
            "# Base de Conhecimento\n\n"
            "## 5. Motor de Memória\n\n"
            "Conteúdo genérico do motor de memória corporativa.\n\n"
            "### Defeitos dormentes\n\n"
            "Todos eram defeitos DORMENTES: passavam em teste, build e lint — "
            "só o QA independente e a leitura da fonte primária pegaram.\n",
            encoding="utf-8",
        )
        self.index = SQLiteMemoryIndex(self.root / "index.db")
        self.index.rebuild([self.root])

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def _paths(self, query: str, limit: int = 5) -> list:
        results = self.index.search(query, limit=limit)
        return [r.item.source_path for r in results]

    def test_rare_allcaps_term_wins_over_common_repetition(self) -> None:
        paths = self._paths("DORMENTES QA independente")
        self.assertTrue(paths)
        self.assertTrue(paths[0].startswith("learnings.md"),
                        f"esperado learnings.md primeiro, veio: {paths}")

    def test_long_lowercase_rare_word_also_gets_priority(self) -> None:
        (self.root / "learnings2.md").write_text(
            "# Lições\n\n## Sessão de orquestração\n\n"
            "Três falhas vieram de briefing subespecificado do maestro.\n",
            encoding="utf-8",
        )
        self.index.index_roots([self.root])
        paths = self._paths("briefing subespecificado maestro")
        self.assertTrue(paths)
        self.assertTrue(paths[0].startswith("learnings2.md"),
                        f"esperado learnings2.md primeiro, veio: {paths}")

    def test_short_common_query_keeps_plain_behavior(self) -> None:
        paths = self._paths("QA pipeline")
        self.assertTrue(paths)
        self.assertTrue(all(".md" in p for p in paths))

    def test_no_match_stays_empty(self) -> None:
        self.assertEqual([], self._paths("ZZZNOMATCH"))

    def test_hybrid_fusion_keeps_rare_match_on_top(self) -> None:
        from engine.search import HybridSearchEngine

        engine = HybridSearchEngine(self.index)
        results = engine.search("DORMENTES QA independente", limit=3)
        self.assertTrue(results)
        top = results[0]
        self.assertTrue(top.item.source_path.startswith("learnings.md"),
                        f"esperado learnings.md primeiro no hybrid, veio: "
                        f"{[r.item.source_path for r in results]}")
        self.assertIsNotNone(top.priority_rank)


if __name__ == "__main__":
    unittest.main()
