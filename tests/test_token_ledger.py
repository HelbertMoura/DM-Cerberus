"""Tests for Cerberus Token-Ledger & Anti-Loop module."""
import tempfile
import sqlite3
import datetime as dt
import unittest
from pathlib import Path

from engine.token_ledger import (
    estimate_token_cost,
    get_ledger_stats,
    init_ledger_db,
    mark_file_write,
    normalize_usage,
    record_file_access,
    record_turn_tokens,
)


class TestTokenLedger(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = Path(self.temp_dir.name) / "test_ledger.db"

    def test_database_initialization_and_turn_recording(self):
        init_ledger_db(self.db_path)
        self.assertTrue(self.db_path.exists())

        rec = record_turn_tokens(
            session_id="sess-001",
            project_id="dm-erp",
            agent="Maestro",
            model="gpt-6.1-sol",
            prompt_tokens=1500,
            completion_tokens=600,
            reasoning_tokens=300,
            loops_prevented=1,
            db_path=self.db_path,
        )
        self.assertEqual(rec["total_tokens"], 2100)
        self.assertIsNone(rec["cost_estimated"])

        stats = get_ledger_stats(self.db_path)
        self.assertEqual(stats["today"]["total"], 2100)
        self.assertEqual(stats["today"]["prompt"], 1500)
        self.assertEqual(stats["today"]["completion"], 600)
        self.assertEqual(stats["today"]["reasoning"], 300)
        self.assertEqual(stats["today"]["loops"], 1)
        self.assertEqual(len(stats["by_model"]), 1)
        self.assertEqual(stats["by_model"][0]["model"], "gpt-6.1-sol")
        self.assertEqual(len(stats["by_project"]), 1)
        self.assertEqual(stats["by_project"][0]["project_id"], "dm-erp")

    def test_anti_loop_detection_triggers_at_threshold(self):
        sess = "sess-loop-test"
        fpath = "C:/DevManiacs/migra/dm-erp/backend/models.py"

        # 1st read: no loop
        r1 = record_file_access(sess, fpath, turn_id="t1", db_path=self.db_path)
        self.assertFalse(r1["is_loop"])
        self.assertEqual(r1["read_count"], 1)
        self.assertEqual(r1["warning"], "")

        # 2nd read: no loop
        r2 = record_file_access(sess, fpath, turn_id="t2", db_path=self.db_path)
        self.assertFalse(r2["is_loop"])
        self.assertEqual(r2["read_count"], 2)

        # 3rd read: LOOP TRIGGERED
        r3 = record_file_access(sess, fpath, turn_id="t3", db_path=self.db_path)
        self.assertTrue(r3["is_loop"])
        self.assertEqual(r3["read_count"], 3)
        self.assertIn("[CERBERUS ANTI-LOOP]", r3["warning"])
        self.assertIn("models.py", r3["warning"])

        # Write occurs: resets loop state
        mark_file_write(sess, fpath, db_path=self.db_path)

        # 4th read (after write): no loop!
        r4 = record_file_access(sess, fpath, turn_id="t4", db_path=self.db_path)
        self.assertFalse(r4["is_loop"])
        self.assertEqual(r4["read_count"], 1)

    def test_cost_estimation(self):
        self.assertIsNone(estimate_token_cost("unknown", 10000, 2000, 0))
        pricing = {"prompt": 1.0, "completion": 2.0, "source": "test fixture"}
        self.assertEqual(estimate_token_cost("test", 10000, 2000, 1000, pricing), 0.014)
        with self.assertRaises(ValueError):
            estimate_token_cost("test", 1, 1, pricing={"prompt": 1, "completion": 2})

    def test_partial_usage_and_dedup(self):
        counts = normalize_usage({"total_tokens": 120})
        first = record_turn_tokens("s", "p", "a", "unknown", **counts,
                                   event_id="event-1", db_path=self.db_path)
        second = record_turn_tokens("s", "p", "a", "unknown", **counts,
                                    event_id="event-1", db_path=self.db_path)
        self.assertEqual(first["id"], second["id"])
        self.assertTrue(second["duplicate"])
        stats = get_ledger_stats(self.db_path)
        self.assertEqual(stats["today"]["count"], 1)
        self.assertEqual(stats["today"]["total"], 120)
        self.assertIsNone(stats["today"]["prompt"])
        self.assertEqual(stats["usage_status"], "partial")

    def test_reasoning_is_output_subset(self):
        counts = normalize_usage({"input_tokens": 100, "output_tokens": 50,
                                  "output_tokens_details": {"reasoning_tokens": 20}})
        rec = record_turn_tokens("s", "p", "a", "m", **counts, db_path=self.db_path)
        self.assertEqual(rec["total_tokens"], 150)
        self.assertEqual(rec["reasoning_tokens"], 20)

    def test_invalid_usage_rejected_before_writing(self):
        for value in (-1, "12", 1.5, True):
            with self.subTest(value=value), self.assertRaises(ValueError):
                record_turn_tokens("s", "p", "a", "m", value, 10, db_path=self.db_path)
        with self.assertRaises(ValueError):
            record_turn_tokens("s", "p", "a", "m", 10, 5, 6, db_path=self.db_path)
        with self.assertRaises(ValueError):
            record_turn_tokens("s", "p", "a", "m", 10, 5, total_tokens=20, db_path=self.db_path)
        self.assertFalse(self.db_path.exists())

    def test_interleaved_reads_and_sessions_do_not_form_loop(self):
        for path in ("a", "b", "a", "c", "a"):
            result = record_file_access("s", path, db_path=self.db_path)
            self.assertFalse(result["is_loop"])
            self.assertEqual(result["read_count"], 1)
        record_file_access("other", "a", db_path=self.db_path)
        self.assertEqual(record_file_access("s", "a", db_path=self.db_path)["read_count"], 2)
        result = record_file_access("s", "a", db_path=self.db_path)
        self.assertTrue(result["is_loop"])
        self.assertFalse(result["prevented"])
        self.assertEqual(get_ledger_stats(self.db_path)["loops_detected"], 1)
        mark_file_write("s", "a", db_path=self.db_path)
        self.assertEqual(record_file_access("s", "a", db_path=self.db_path)["read_count"], 1)

    def test_legacy_schema_migration_preserves_records_without_trusting_prices(self):
        with sqlite3.connect(self.db_path) as con:
            con.execute("""CREATE TABLE token_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT, session_id TEXT NOT NULL,
                project_id TEXT NOT NULL, agent TEXT NOT NULL, model TEXT NOT NULL,
                prompt_tokens INTEGER DEFAULT 0, completion_tokens INTEGER DEFAULT 0,
                reasoning_tokens INTEGER DEFAULT 0, total_tokens INTEGER DEFAULT 0,
                loops_prevented INTEGER DEFAULT 0, cost_estimated REAL DEFAULT 0.0,
                created_at TEXT NOT NULL)""")
            con.execute("""INSERT INTO token_ledger (session_id, project_id, agent, model,
                        prompt_tokens, completion_tokens, total_tokens, cost_estimated, created_at)
                        VALUES ('legacy', 'p', 'a', 'm', 10, 5, 15, 123.45,
                                strftime('%Y-%m-%dT%H:%M:%f+00:00', 'now'))""")
        con.close()
        init_ledger_db(self.db_path)
        stats = get_ledger_stats(self.db_path)
        self.assertEqual(stats["today"]["total"], 15)
        self.assertIsNone(stats["today"]["cost"])
        self.assertIsNone(stats["recent_sessions"][0]["cost_estimated"])
        self.assertEqual(stats["usage_status"], "partial")
        record_turn_tokens("new", "p", "a", "m", 10, 5, event_id="e", db_path=self.db_path)
        self.assertEqual(get_ledger_stats(self.db_path)["today"]["count"], 2)

    def test_recent_records_respect_selected_period(self):
        for session in ("old", "new"):
            record_turn_tokens(session, "p", "a", "m", 10, 5, db_path=self.db_path)
            for _ in range(3):
                record_file_access(session, "a", db_path=self.db_path)
        old_date = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=20)).isoformat()
        with sqlite3.connect(self.db_path) as con:
            con.execute("UPDATE token_ledger SET created_at=? WHERE session_id='old'", (old_date,))
            con.execute("UPDATE file_access_log SET created_at=? WHERE session_id='old'", (old_date,))
        con.close()
        week = get_ledger_stats(self.db_path, days=7)
        month = get_ledger_stats(self.db_path, days=30)
        self.assertEqual([r["session_id"] for r in week["recent_sessions"]], ["new"])
        self.assertEqual([r["session_id"] for r in week["recent_loops"]], ["new"])
        self.assertEqual(len(month["recent_sessions"]), 2)
        self.assertEqual(len(month["recent_loops"]), 2)
