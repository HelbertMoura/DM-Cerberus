"""BM25 relevance and authority regressions using temporary SQLite indexes."""

import tempfile
import unittest
from pathlib import Path

from engine.index import SQLiteMemoryIndex
from engine.search import HybridSearchEngine


class TestBM25Ranking(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.index = SQLiteMemoryIndex(Path(temporary.name) / "index.db")

    def add_document(self, memory_id, text, authority=50):
        with self.index._get_connection() as connection:
            connection.execute(
                "INSERT INTO documents (memory_id, project_id, source_path, "
                "source_type, title, authority_level, tags, snippet, full_text, "
                "updated_at, status, metadata) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (memory_id, "alpha", f"projects/alpha/{memory_id}.md", "wiki",
                 "Reference", authority, "[]", "", text, "", "ativo", "{}"),
            )
            connection.commit()

    def add_relevance_pair(self, strong_authority=50, weak_authority=50):
        self.add_document("strong", "cache sql " * 20, strong_authority)
        self.add_document("weak", "cache sql " + "background " * 1000, weak_authority)

    def test_common_negative_bm25_scores_preserve_relevance(self):
        self.add_relevance_pair()
        results = self.index.search("cache", project_id="alpha")
        self.assertEqual(["strong", "weak"], [row.item.memory_id for row in results])
        self.assertIsNone(results[0].priority_rank)
        self.assertGreater(results[0].lexical_score, results[1].lexical_score)
        self.assertGreater(results[1].lexical_score, 0)
        self.assertGreater(results[0].final_score, results[1].final_score)

    def test_strong_match_can_outrank_weak_match_with_higher_authority(self):
        self.add_relevance_pair(strong_authority=30, weak_authority=100)
        results = self.index.search("sql", project_id="alpha")
        self.assertEqual(["strong", "weak"], [row.item.memory_id for row in results])
        self.assertGreater(results[0].final_score, results[1].final_score)

    def test_common_term_serialized_scores_remain_positive_and_distinct(self):
        self.add_relevance_pair()
        results = self.index.search("cache", project_id="alpha")
        serialized = [row.to_dict() for row in results]
        for field in ("lexical_score", "final_score"):
            with self.subTest(field=field):
                self.assertGreater(serialized[1][field], 0)
                self.assertGreater(serialized[0][field], serialized[1][field])
                for row, payload in zip(results, serialized):
                    self.assertEqual(getattr(row, field), payload[field])

    def test_equal_relevance_still_uses_authority_multiplier(self):
        self.add_document("low", "cache sql reference", authority=30)
        self.add_document("high", "cache sql reference", authority=100)
        results = self.index.search("cache", project_id="alpha")
        self.assertEqual(["high", "low"], [row.item.memory_id for row in results])
        self.assertEqual(results[0].lexical_score, results[1].lexical_score)
        self.assertGreater(results[0].final_score, results[1].final_score)
        self.assertAlmostEqual(2.0 / 1.3, results[0].final_score / results[1].final_score)

    def test_short_terms_keep_relevance_ranks_in_lexical_and_hybrid_search(self):
        self.add_relevance_pair(strong_authority=30, weak_authority=100)
        search = HybridSearchEngine(self.index)
        for query in ("cache", "sql"):
            for mode in ("lexical", "hybrid"):
                with self.subTest(query=query, mode=mode):
                    results = search.search(query, project_id="alpha", mode=mode, limit=2)
                    self.assertEqual(2, len(results))
                    by_id = {row.item.memory_id: row for row in results}
                    self.assertEqual(1, by_id["strong"].lexical_rank)
                    self.assertEqual(2, by_id["weak"].lexical_rank)
                    self.assertEqual("strong", results[0].item.memory_id)
                    self.assertTrue(all(row.priority_rank is None for row in results))
                    self.assertTrue(all(row.search_mode == mode for row in results))


if __name__ == "__main__":
    unittest.main()
