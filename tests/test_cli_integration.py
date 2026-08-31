import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class TestCLIIntegration(unittest.TestCase):
    def run_cli(self, repo: Path, root: Path, *args: str) -> subprocess.CompletedProcess[str]:
        env = dict(os.environ, CERBERUS_ROOT=str(root), CERBERUS_ALLOWED_ROOTS=str(root), PYTHONPATH=str(repo))
        return subprocess.run([sys.executable, "-m", "engine.cli", *args], cwd=root,
                              env=env, text=True, encoding="utf-8", capture_output=True, timeout=10)

    def test_capture_inbox_preview_apply_and_doctor_from_arbitrary_cwd(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory(prefix="Cerberus ação ") as tmp:
            root = Path(tmp)
            learning = root / "LEARNINGS.md"
            learning.write_text("# Learnings\n", encoding="utf-8")
            (root / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
            captured = self.run_cli(repo, root, "capture", "--title", "CLI gate", "--content",
                                    "Promotion requires explicit apply.", "--project", "demo",
                                    "--task", "TASK-CLI", "--agent", "QA")
            self.assertEqual(0, captured.returncode, captured.stderr)
            candidate_id = json.loads(captured.stdout)["candidate_id"]
            self.assertEqual("# Learnings\n", learning.read_text(encoding="utf-8"))

            inbox = self.run_cli(repo, root, "inbox")
            self.assertIn(candidate_id, inbox.stdout)
            preview = self.run_cli(repo, root, "promote", candidate_id)
            self.assertEqual(0, preview.returncode, preview.stderr)
            self.assertIn("+### CLI gate", preview.stdout)
            self.assertEqual("# Learnings\n", learning.read_text(encoding="utf-8"))
            verified = self.run_cli(repo, root, "review", candidate_id, "--verify")
            self.assertEqual(0, verified.returncode, verified.stderr)
            applied = self.run_cli(repo, root, "promote", candidate_id, "--apply")
            self.assertEqual(0, applied.returncode, applied.stderr)
            self.assertIn("TASK-CLI", learning.read_text(encoding="utf-8"))

            doctor = self.run_cli(repo, root, "doctor")
            payload = json.loads(doctor.stdout)
            self.assertTrue(payload["python"]["fts5"])
            self.assertEqual(str(root.resolve()), payload["canonical_root"])

    def test_cli_rejects_root_outside_allowlist_before_creating_state(self) -> None:
        repo = Path(__file__).resolve().parents[1]
        with tempfile.TemporaryDirectory() as allowed_tmp, tempfile.TemporaryDirectory() as outside_tmp:
            env = dict(
                os.environ, CERBERUS_ROOT=outside_tmp, CERBERUS_ALLOWED_ROOTS=allowed_tmp,
                PYTHONPATH=str(repo), PYTHONDONTWRITEBYTECODE="1",
            )
            proc = subprocess.run(
                [sys.executable, "-m", "engine.cli", "doctor"], cwd=repo, env=env,
                text=True, capture_output=True, timeout=10,
            )
            self.assertNotEqual(0, proc.returncode)
            self.assertFalse((Path(outside_tmp) / ".cerberus").exists())


if __name__ == "__main__":
    unittest.main()
