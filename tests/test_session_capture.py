import importlib.util
import io
import json
import os
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch
from pathlib import Path

HOOK_PATH = Path(__file__).resolve().parent.parent / "hooks" / "claude_session_capture.py"
_spec = importlib.util.spec_from_file_location("claude_session_capture", HOOK_PATH)
hook = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hook)


def _run_hook(payload: dict, argv: list[str] | None = None) -> str:
    stdout = io.StringIO()
    original_stdin, original_stdout = hook.sys.stdin, hook.sys.stdout

    class _FakeStdin:
        def __init__(self, data: str) -> None:
            self._data = data

        def isatty(self) -> bool:
            return False

        def read(self) -> str:
            return self._data

    try:
        hook.sys.stdin = _FakeStdin(json.dumps(payload))
        hook.sys.stdout = stdout
        exit_code = hook.main(argv=argv or ["--agent", "CLAUDE_CODE"])
    finally:
        hook.sys.stdin = original_stdin
        hook.sys.stdout = original_stdout
    assert exit_code == 0, "hook must never fail the agent session"
    return stdout.getvalue()


class TestSessionCaptureHook(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        self.engine = None
        self._original_root_env = os.environ.get("CERBERUS_CAPTURE_ROOT")
        os.environ["CERBERUS_CAPTURE_ROOT"] = str(self.root)

    def tearDown(self) -> None:
        if self._original_root_env is None:
            os.environ.pop("CERBERUS_CAPTURE_ROOT", None)
        else:
            os.environ["CERBERUS_CAPTURE_ROOT"] = self._original_root_env
        self.temp_dir.cleanup()

    def _engine(self):
        from engine.capture import AutoCaptureEngine
        if self.engine is None:
            self.engine = AutoCaptureEngine(cerebro_root=self.root)
        return self.engine

    def _transcript(self, text: str) -> str:
        path = self.root / "transcript.jsonl"
        entry = {"type": "assistant",
                 "message": {"role": "assistant",
                             "content": [{"type": "text", "text": text}]}}
        path.write_text(json.dumps(entry) + "\n", encoding="utf-8")
        return str(path)

    def test_structured_sections_become_candidates(self) -> None:
        transcript = self._transcript(
            "TASK: QA-FND-009\n"
            "## Learnings\n"
            "- Content-hash proof beats git diff when nothing was committed.\n"
            "## Gotchas\n"
            "- Rendering must be measured in a real browser, never asserted from source.\n"
        )
        out = _run_hook({"hook_event_name": "SessionEnd", "session_id": "abcd1234-eeee",
                         "transcript_path": transcript, "cwd": str(self.root)},
                        argv=["--agent", "CLAUDE_CODE"])
        result = json.loads(out)["cerberus_capture"]
        self.assertEqual(2, result["candidate_count"])
        items = self._engine().store.list()
        self.assertEqual({"QA-FND-009"}, {item.task_id for item in items})
        self.assertEqual({"CLAUDE_CODE"}, {item.agent for item in items})

    def test_raw_chat_without_sections_captures_nothing(self) -> None:
        transcript = self._transcript("Conversei bastante mas não registrei lições estruturadas.")
        out = _run_hook({"hook_event_name": "SessionEnd", "session_id": "abcd1234-ffff",
                         "transcript_path": transcript, "cwd": str(self.root)})
        self.assertEqual("", out.strip())
        self.assertEqual([], self._engine().store.list())

    def test_secret_in_section_is_quarantined_and_redacted(self) -> None:
        transcript = self._transcript(
            "TASK: TASK-SECRET\n"
            "## Findings\n"
            "- The service token was exposed as api_key: sk-abcdefghijklmnopqrstuvwx in logs.\n"
        )
        _run_hook({"hook_event_name": "SessionEnd", "session_id": "abcd1234-9999",
                   "transcript_path": transcript, "cwd": str(self.root)})
        items = self._engine().store.list()
        self.assertEqual(1, len(items))
        self.assertEqual("QUARANTINED", items[0].status.value)
        raw = items[0].to_dict()["content"]
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwx", raw)

    def test_missing_transcript_is_silent(self) -> None:
        out = _run_hook({"hook_event_name": "SessionEnd", "session_id": "abcd1234-0000",
                         "transcript_path": str(self.root / "missing.jsonl"),
                         "cwd": str(self.root)})
        self.assertEqual("", out.strip())
        self.assertEqual([], self._engine().store.list())

    def test_fallback_task_uses_session_id(self) -> None:
        transcript = self._transcript(
            "## Learnings\n- No explicit task id here but the lesson is worth filing.\n"
        )
        _run_hook({"hook_event_name": "SessionEnd", "session_id": "abcd1234-7777",
                   "transcript_path": transcript, "cwd": str(self.root)})
        items = self._engine().store.list()
        self.assertEqual(1, len(items))
        self.assertEqual("SES-abcd1234", items[0].task_id)

    def test_codex_rollout_reads_only_public_assistant_messages(self) -> None:
        path = self.root / "codex.jsonl"
        rows = [
            {"type": "response_item", "payload": {"type": "message", "role": "user",
                "content": [{"type": "input_text", "text": "## Learnings\n- User text must never become assistant evidence."}]}},
            {"type": "response_item", "payload": {"type": "reasoning",
                "summary": [{"type": "summary_text", "text": "Private reasoning must not be captured."}]}},
            {"type": "response_item", "payload": {"type": "message", "role": "assistant",
                "phase": "final", "content": [{"type": "output_text", "text":
                    "TASK: CODEX-FORMAT\n## Learnings\n- Native Codex wraps public messages in response_item.payload."}]}},
        ]
        path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
        out = _run_hook({"hook_event_name": "SessionEnd", "session_id": "native-codex",
                         "transcript_path": str(path), "cwd": str(self.root)}, ["--agent", "CODEX"])
        self.assertTrue(out.strip(), "native Codex assistant evidence was not captured")
        self.assertEqual(1, json.loads(out)["cerberus_capture"]["candidate_count"])
        self.assertEqual("CODEX-FORMAT", self._engine().store.list()[0].task_id)
        self.assertNotIn("User text", self._engine().store.list()[0].content)

    def test_claude_message_envelope_uses_nested_role(self) -> None:
        path = self.root / "nested.jsonl"
        path.write_text(json.dumps({"type": "message", "message": {"role": "assistant",
            "content": [{"type": "text", "text": "A public assistant message."}]}}), encoding="utf-8")
        self.assertEqual("A public assistant message.", hook._extract_assistant_text(str(path)))

    def test_codex_stop_uses_stable_message_field_and_deduplicates(self) -> None:
        payload = {"hook_event_name": "Stop", "session_id": "native-stop", "turn_id": "turn-1",
            "last_assistant_message": "## Learnings\n- Capture reusable findings without reopening the completed turn.",
            "cwd": str(self.root)}
        first = _run_hook(payload, ["--agent", "CODEX", "--quiet"])
        self.assertTrue(first.strip(), "Stop must emit a valid JSON response")
        self.assertNotIn("decision", json.loads(first))
        _run_hook(payload, ["--agent", "CODEX", "--quiet"])
        self.assertEqual(1, len(self._engine().store.list()))
        self.assertFalse((self.root / "LEARNINGS.md").exists())
        self.assertFalse((self.root / "DECISIONS.md").exists())

    def test_quiet_hook_records_health_without_transcript_content(self) -> None:
        _run_hook({"hook_event_name": "SessionEnd", "session_id": "missing-session",
            "transcript_path": str(self.root / "missing.jsonl")}, ["--agent", "CODEX", "--quiet"])
        receipts = list((self.root / ".cerberus" / "hooks").glob("*.json"))
        self.assertEqual(1, len(receipts), "silent hooks still need an observable receipt")
        receipt = json.loads(receipts[0].read_text(encoding="utf-8"))
        self.assertEqual("NO_ASSISTANT_TEXT", receipt["status"])
        self.assertNotIn("transcript_path", receipt)

    def test_malformed_event_never_breaks_a_session(self) -> None:
        self.assertEqual("", _run_hook({"hook_event_name": ["Stop"]}, ["--agent", "CODEX", "--quiet"]))

    def test_codex_stop_quarantines_secrets_and_keeps_health_clean(self) -> None:
        _run_hook({"hook_event_name": "Stop", "session_id": "secret-stop", "cwd": str(self.root),
            "last_assistant_message": "## Learnings\n- Service token: sk-abcdefghijklmnopqrstuvwx must be rotated."},
            ["--agent", "CODEX", "--quiet"])
        items = self._engine().store.list()
        self.assertEqual("QUARANTINED", items[0].status.value)
        health = list((self.root / ".cerberus" / "hooks").glob("run-*.json"))[0].read_text(encoding="utf-8")
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwx", health)

    def test_capture_exception_is_observable_without_secret_detail(self) -> None:
        with patch("engine.capture.AutoCaptureEngine.ingest_report", side_effect=ValueError("NEVER-LOG-THIS")):
            output = _run_hook({"hook_event_name": "Stop", "session_id": "error-stop",
                "last_assistant_message": "## Learnings\n- An actual finding whose capture unexpectedly fails."}, ["--agent", "CODEX"])
        self.assertNotIn("NEVER-LOG-THIS", output)

    def test_native_stop_accepts_unescaped_utf8_even_with_windows_stdio_defaults(self) -> None:
        lesson = "Memória compartilhada exige proveniência correta e revisão humana."
        payload = {"hook_event_name": "Stop", "session_id": "unicode-native",
            "last_assistant_message": "## Learnings\n- " + lesson}
        env = dict(os.environ, CERBERUS_CAPTURE_ROOT=str(self.root), PYTHONIOENCODING="cp1252")
        process = subprocess.run([sys.executable, str(HOOK_PATH), "--agent", "CODEX", "--quiet"],
            input=json.dumps(payload, ensure_ascii=False).encode("utf-8"), env=env,
            capture_output=True, timeout=10)
        self.assertEqual(0, process.returncode, process.stderr)
        self.assertEqual({}, json.loads(process.stdout.decode("utf-8")))
        self.assertEqual(lesson, self._engine().store.list()[0].content)


if __name__ == "__main__":
    unittest.main()
