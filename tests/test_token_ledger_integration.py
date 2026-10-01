"""Integration tests for Token Ledger, Cockpit API and Anti-Loop Radar."""
import tempfile
import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

from engine.token_ledger import (
    estimate_token_cost,
    get_ledger_stats,
    mark_file_write,
    record_file_access,
    record_turn_tokens,
)


class TestTokenLedgerAndAntiLoop(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)
        self.db_path = Path(self.temp_dir.name) / "test_ledger.db"

    def test_unconfigured_models_have_unknown_cost(self):
        for model in ("gpt-6.1-sol", "gpt-6-luna", "gpt-6-astra"):
            self.assertIsNone(estimate_token_cost(model, 1000, 500, 200))

    def test_hook_usage_without_text_and_duplicate_stop(self):
        root = Path(self.temp_dir.name)
        env = dict(os.environ, CERBERUS_CAPTURE_ROOT=str(root))
        payload = {"hook_event_name": "Stop", "session_id": "usage-only",
                   "usage": {"total_tokens": 120}}
        hook = Path(__file__).resolve().parents[1] / "hooks" / "claude_session_capture.py"
        for _ in range(2):
            result = subprocess.run([sys.executable, str(hook), "--agent", "CODEX", "--quiet"],
                                    input=json.dumps(payload), text=True, capture_output=True, env=env)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(json.loads(result.stdout), {})
        stats = get_ledger_stats(root / ".cerberus" / "token_ledger.db")
        self.assertEqual(stats["today"]["count"], 1)
        self.assertEqual(stats["today"]["total"], 120)
        self.assertIsNone(stats["today"]["completion"])
        self.assertEqual(stats["recent_sessions"][0]["usage_source"], "hook_payload")
        self.assertFalse((root / ".cerberus" / "inbox").exists())

    def test_record_turn_tokens_and_stats(self):
        rec1 = record_turn_tokens(
            session_id="ses-001",
            project_id="biolar",
            agent="CODEX",
            model="gpt-6.1-sol",
            prompt_tokens=1500,
            completion_tokens=400,
            reasoning_tokens=250,
            db_path=self.db_path,
        )
        self.assertEqual(rec1["total_tokens"], 1900)

        rec2 = record_turn_tokens(
            session_id="ses-002",
            project_id="integra",
            agent="LUNA",
            model="gpt-6-luna",
            prompt_tokens=800,
            completion_tokens=200,
            reasoning_tokens=0,
            db_path=self.db_path,
        )
        self.assertEqual(rec2["total_tokens"], 1000)

        stats = get_ledger_stats(db_path=self.db_path, days=7)
        self.assertEqual(stats["today"]["count"], 2)
        self.assertEqual(stats["today"]["total"], 2900)
        self.assertEqual(stats["today"]["reasoning"], 250)
        self.assertIsNone(stats["today"]["cost"])
        
        models = [m["model"] for m in stats["by_model"]]
        self.assertIn("gpt-6.1-sol", models)
        self.assertIn("gpt-6-luna", models)

        projects = [p["project_id"] for p in stats["by_project"]]
        self.assertIn("biolar", projects)
        self.assertEqual(len(stats["recent_sessions"]), 2)

    def test_anti_loop_radar(self):
        # 1st read: no loop
        r1 = record_file_access("ses-loop", "src/auth/login.py", db_path=self.db_path)
        self.assertFalse(r1["is_loop"])
        self.assertEqual(r1["read_count"], 1)

        # 2nd read: no loop
        r2 = record_file_access("ses-loop", "src/auth/login.py", db_path=self.db_path)
        self.assertFalse(r2["is_loop"])
        self.assertEqual(r2["read_count"], 2)

        # 3rd read: loop detected!
        r3 = record_file_access("ses-loop", "src/auth/login.py", db_path=self.db_path)
        self.assertTrue(r3["is_loop"])
        self.assertEqual(r3["read_count"], 3)
        self.assertIn("ANTI-LOOP", r3["warning"])

        # Write resets loop
        mark_file_write("ses-loop", "src/auth/login.py", db_path=self.db_path)

        # Next read starts at count 1
        r4 = record_file_access("ses-loop", "src/auth/login.py", db_path=self.db_path)
        self.assertFalse(r4["is_loop"])
        self.assertEqual(r4["read_count"], 1)


if __name__ == "__main__":
    unittest.main()
