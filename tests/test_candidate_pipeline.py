import json
import tempfile
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from threading import Barrier
from unittest.mock import patch

from engine.capture import AutoCaptureEngine, CandidateStore, _fingerprint, redact_secrets


class TestCandidatePipeline(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "LEARNINGS.md").write_text("# Learnings\n", encoding="utf-8")
        (self.root / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")
        self.engine = AutoCaptureEngine(cerebro_root=self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_capture_creates_candidate_without_canonical_write(self) -> None:
        before = (self.root / "LEARNINGS.md").read_bytes()
        result = self.engine.capture_learning(
            title="Use atomic writes",
            content="Write a temporary file and replace the destination atomically.",
            project_id="dm-cerebro",
            task_id="TASK-42",
            agent_role="CODEX",
        )
        self.assertEqual("CANDIDATE", result["status"])
        self.assertEqual(before, (self.root / "LEARNINGS.md").read_bytes())
        candidate = self.engine.store.get(result["candidate_id"])
        self.assertEqual("TASK-42", candidate.task_id)
        self.assertEqual("CODEX", candidate.agent)
        self.assertTrue(candidate.created_at)
        self.assertEqual(64, len(candidate.fingerprint))

    def test_missing_provenance_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.engine.capture_learning(
                title="Unsafe",
                content="No task provenance is supplied here.",
                project_id="dm-cerebro",
                task_id=None,
                agent_role="CODEX",
            )

    def test_secret_is_quarantined_and_value_not_persisted(self) -> None:
        secret = "Authorization: Bearer super-secret-token-value"
        result = self.engine.capture_learning(
            title="Leaked credential",
            content=secret,
            project_id="dm-cerebro",
            task_id="TASK-SECRET",
            agent_role="QA",
        )
        self.assertEqual("QUARANTINED", result["status"])
        raw = Path(result["candidate_path"]).read_text(encoding="utf-8")
        self.assertNotIn("super-secret-token-value", raw)
        self.assertIn("[REDACTED]", raw)

    def test_provider_token_is_quarantined(self) -> None:
        token = "ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ1234567890"
        result = self.engine.capture_learning(
            title="Provider token", content=f"GitHub token {token}", project_id="dm-cerebro",
            task_id="TASK-SECRET-2", agent_role="QA",
        )
        self.assertEqual("QUARANTINED", result["status"])
        self.assertNotIn(token, Path(result["candidate_path"]).read_text(encoding="utf-8"))

    def test_mcp_style_report_content_never_reads_a_path(self) -> None:
        outside = self.root.parent / "outside-report.md"
        outside.write_text("## Learnings\n- This outside file must never be read through MCP ingestion.\n", encoding="utf-8")
        try:
            result = self.engine.ingest_report(str(outside), task_id="TASK-PATH", allow_file=False)
            self.assertEqual(0, result["candidate_count"])
        finally:
            outside.unlink(missing_ok=True)

    def test_exact_duplicate_reuses_candidate(self) -> None:
        kwargs = dict(
            title="Stable roots",
            content="Normalize nested roots before walking files.",
            project_id="dm-cerebro",
            task_id="TASK-ROOTS",
            agent_role="CODEX",
        )
        first = self.engine.capture_learning(**kwargs)
        second = self.engine.capture_learning(**kwargs)
        self.assertEqual("SKIPPED_DUPLICATE", second["status"])
        self.assertEqual(first["candidate_id"], second["candidate_id"])

    def test_concurrent_duplicate_capture_publishes_once(self) -> None:
        original_lookup = self.engine.store.find_by_fingerprint
        barrier = Barrier(2)

        def lookup(fingerprint):
            found = original_lookup(fingerprint)
            barrier.wait(timeout=5)
            return found

        def capture(agent):
            return self.engine.capture_learning(title="Concurrent capture", content="Two hooks must publish one complete candidate.",
                project_id="dm-cerebro", task_id="TASK-CONCURRENT", agent_role=agent)

        results, failures = [], []
        with patch.object(self.engine.store, "find_by_fingerprint", side_effect=lookup):
            with ThreadPoolExecutor(max_workers=2) as pool:
                futures = [pool.submit(capture, agent) for agent in ("CODEX", "CLAUDE_CODE")]
                for future in futures:
                    try:
                        results.append(future.result())
                    except Exception as exc:
                        failures.append(type(exc).__name__)
        self.assertEqual([], failures, "parallel capture must not share a temporary filename")
        self.assertEqual(["CANDIDATE", "SKIPPED_DUPLICATE"], sorted(r["status"] for r in results))
        self.assertEqual(1, len(self.engine.store.list()))

    def test_capture_race_never_resets_a_verified_candidate(self) -> None:
        kwargs = dict(title="Review remains valid", content="An automatic capture must preserve a reviewed candidate.",
            project_id="dm-cerebro", task_id="TASK-ORIGINAL", agent_role="CODEX")
        captured = self.engine.capture_learning(**kwargs)
        self.engine.verify(captured["candidate_id"])
        # Simulate another writer publishing/reviewing after the lookup snapshot.
        with patch.object(self.engine.store, "find_by_fingerprint", return_value=None):
            result = self.engine.capture_learning(**{**kwargs, "task_id": "TASK-LATER"})
        self.assertEqual("SKIPPED_DUPLICATE", result["status"])
        stored = self.engine.store.get(captured["candidate_id"])
        self.assertEqual("VERIFIED", stored.status.value)
        self.assertEqual("TASK-ORIGINAL", stored.task_id)

    def test_promote_previews_by_default_and_only_apply_writes(self) -> None:
        captured = self.engine.capture_learning(
            title="Preview gate",
            content="Canonical writes require an explicit apply flag.",
            project_id="dm-cerebro",
            task_id="TASK-PROMOTE",
            agent_role="CODEX",
        )
        target = self.root / "LEARNINGS.md"
        before = target.read_bytes()
        preview = self.engine.promote(captured["candidate_id"], apply=False)
        self.assertEqual("PREVIEW", preview["status"])
        self.assertIn("+### Preview gate", preview["diff"])
        self.assertEqual(before, target.read_bytes())

        self.engine.verify(captured["candidate_id"])
        applied = self.engine.promote(captured["candidate_id"], apply=True)
        self.assertEqual("CANONICAL", applied["status"])
        self.assertIn("TASK-PROMOTE", target.read_text(encoding="utf-8"))

    def test_corrupt_candidate_fails_closed(self) -> None:
        store = CandidateStore(self.root / ".cerberus" / "inbox", self.root)
        bad = store.inbox_dir / "broken.json"
        bad.write_text("{not-json", encoding="utf-8")
        with self.assertRaises(ValueError):
            store.get("broken")

    def test_tampered_candidate_fingerprint_blocks_promotion(self) -> None:
        captured = self.engine.capture_learning(
            title="Integrity gate", content="Original reviewed content.", project_id="dm-cerebro",
            task_id="TASK-TAMPER", agent_role="QA",
        )
        self.engine.verify(captured["candidate_id"])
        path = self.engine.store._path(captured["candidate_id"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["content"] = "Tampered after review."
        path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "fingerprint"):
            self.engine.promote(captured["candidate_id"], apply=True)
        self.assertNotIn("Tampered after review", (self.root / "LEARNINGS.md").read_text(encoding="utf-8"))

    def test_tampered_secret_is_quarantined_even_with_recomputed_fingerprint(self) -> None:
        captured = self.engine.capture_learning(
            title="Secret recheck", content="Originally safe content.", project_id="dm-cerebro",
            task_id="TASK-SECRET-RECHECK", agent_role="QA",
        )
        self.engine.verify(captured["candidate_id"])
        path = self.engine.store._path(captured["candidate_id"])
        payload = json.loads(path.read_text(encoding="utf-8"))
        payload["content"] = "prefix Authorization: Bearer abcdefghijklmnop"
        payload["fingerprint"] = _fingerprint(
            payload["project_id"], payload["type"], payload["title"], payload["content"]
        )
        path.write_text(json.dumps(payload), encoding="utf-8")

        with self.assertRaisesRegex(ValueError, "Quarantined candidates cannot be promoted"):
            self.engine.promote(captured["candidate_id"], apply=True)
        stored = self.engine.store.get(captured["candidate_id"])
        self.assertEqual("QUARANTINED", stored.status.value)
        self.assertIn("authorization", stored.secret_findings)

    def test_inline_and_generic_secret_assignments_are_redacted(self) -> None:
        for value in (
            "prefix Authorization: Bearer abcdefghijklmnop",
            "client_secret=abcdefghijklmnop",
            "token=abcdefghijklmnop",
            "auth_token: abcdefghijklmnop",
        ):
            with self.subTest(value=value):
                redacted, findings = redact_secrets(value)
                self.assertTrue(findings)
                self.assertIn("[REDACTED]", redacted)
                self.assertNotIn("abcdefghijklmnop", redacted)


if __name__ == "__main__":
    unittest.main()
