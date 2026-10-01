import json
import tempfile
import unittest
import subprocess
import sys
from unittest.mock import patch
from pathlib import Path

from engine.index import SQLiteMemoryIndex
from engine.session_delivery import context_status, delivery_transaction, memory_fingerprint, session_token

try:
    from engine import agent_hooks
except ImportError:
    agent_hooks = None


class TestContextHooks(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(agent_hooks, "automatic context hooks are not implemented")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def seed(self):
        for slug in ("biolar", "helpdev"):
            path = self.root / "projects" / slug / "arquitetura.md"
            path.parent.mkdir(parents=True)
            path.write_text(f"# Arquitetura {slug}\n\nUsar arquitetura {slug} UNIQUE-{slug} para a tarefa.\n", encoding="utf-8")
        index = SQLiteMemoryIndex(self.root / ".cerberus" / "index.db")
        index.index_roots([self.root])

    def payload(self, event="UserPromptSubmit"):
        return {"hook_event_name": event, "session_id": "session-context", "turn_id": "turn-1",
            "cwd": str(self.root / "projects" / "biolar"), "prompt": "Revisar arquitetura biolar"}

    def test_context_is_project_scoped_bounded_and_never_promotes(self):
        self.seed()
        with patch("engine.retrieval.CerberusMemoryService.build_context_pack") as retrieve:
            text = self.text(agent_hooks.handle_context(self.payload(), self.root))
        retrieve.assert_not_called()
        self.assertIn("cerberus_get_task_state", text)
        self.assertNotIn("UNIQUE-", text)
        self.assertLessEqual(len(text), 600)
        self.assertFalse((self.root / "LEARNINGS.md").exists())


    def test_identical_context_is_suppressed_and_resume_keeps_history(self):
        self.seed()
        self.assertTrue(agent_hooks.handle_context(self.payload(), self.root))
        self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))
        startup = self.payload("SessionStart")
        startup["source"] = "resume"
        self.assertEqual({}, agent_hooks.handle_context(startup, self.root))
        startup["source"] = "compact"
        self.assertTrue(agent_hooks.handle_context(startup, self.root))

    def test_mcp_delivery_before_hook_keeps_first_instructions_and_public_token(self):
        self.seed()
        from engine.retrieval import CerberusMemoryService
        index = SQLiteMemoryIndex(self.root / ".cerberus/index.db")
        pack = CerberusMemoryService(index).build_context_pack("biolar", "Revisar arquitetura biolar", role="DEVELOPER")
        keys = [memory_fingerprint(item) for item in pack.relevant_architecture]
        with delivery_transaction(self.root, "session-context") as transaction:
            transaction.commit(200, keys)
        text = self.text(agent_hooks.handle_context(self.payload(), self.root))
        self.assertIn("Fluxo de memória:", text)
        self.assertIn(session_token("session-context"), text)
        self.assertNotIn("session-context", text)
        self.assertNotIn("UNIQUE-biolar", text)
        self.assertEqual(200 + len(text), context_status(self.root, "session-context")["used_chars"])
        self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))

    def test_hook_delivery_is_visible_to_mcp_ledger_with_canonical_key(self):
        self.seed()
        text = self.text(agent_hooks.handle_context(self.payload(), self.root))
        with delivery_transaction(self.root, session_token("session-context")) as transaction:
            self.assertTrue(transaction.hook_initialized)
            self.assertEqual(12000 - len(text), transaction.remaining)
            self.assertFalse(transaction.seen)


    def text(self, output):
        return output.get("hookSpecificOutput", {}).get("additionalContext", "")

    def test_returning_to_previous_project_does_not_repeat_old_memory(self):
        self.seed()
        self.assertTrue(agent_hooks.handle_context(self.payload(), self.root))
        other = {**self.payload(), "cwd": str(self.root / "projects" / "helpdev")}
        self.assertEqual({}, agent_hooks.handle_context(other, self.root))
        self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))


    def test_delta_sends_only_new_source_and_changed_versions(self):
        self.seed()
        agent_hooks.handle_context(self.payload("SessionStart"), self.root)
        source = self.root / "projects/biolar/arquitetura.md"
        source.write_text("# Arquitetura biolar\n\nUPDATED-VERSION", encoding="utf-8")
        SQLiteMemoryIndex(self.root / ".cerberus/index.db").index_roots([self.root], force_reindex=True)
        self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))


    def test_many_updates_share_budget_across_resume_and_reset_after_compaction(self):
        self.seed()
        initial = self.text(agent_hooks.handle_context(self.payload("SessionStart"), self.root))
        for version in range(35):
            self.assertEqual({}, agent_hooks.handle_context({**self.payload(), "prompt": f"nova tarefa {version}"}, self.root))
        self.assertEqual(len(initial), context_status(self.root, "session-context")["used_chars"])
        self.assertEqual({}, agent_hooks.handle_context({**self.payload("SessionStart"), "source": "resume"}, self.root))
        restored = self.text(agent_hooks.handle_context({**self.payload("SessionStart"), "source": "compact"}, self.root))
        self.assertEqual(initial, restored)
        self.assertEqual(len(restored), context_status(self.root, "session-context")["used_chars"])


    def test_truncated_budget_does_not_mark_unsent_memory_as_delivered(self):
        self.seed()
        self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root, max_chars=1))
        self.assertIn("cerberus_get_task_state", self.text(agent_hooks.handle_context(self.payload(), self.root)))

    def test_missing_session_identity_does_not_deliver_unbudgeted_context(self):
        self.seed()
        payload = self.payload()
        del payload["session_id"]
        self.assertEqual({}, agent_hooks.handle_context(payload, self.root))

    def test_corrupt_state_cannot_silently_reset_budget(self):
        self.seed()
        agent_hooks.handle_context(self.payload(), self.root)
        state = next((self.root / ".cerberus/hooks").glob("context-*.json"))
        state.write_text('{broken', encoding="utf-8")
        self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))
        self.assertTrue(agent_hooks.handle_context({**self.payload("SessionStart"), "source": "compact"}, self.root))

    def test_accounting_write_failure_prevents_context_delivery(self):
        self.seed()
        with patch("engine.session_delivery.atomic_json", side_effect=OSError("NEVER-LOG-WRITE-SECRET")):
            self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))
        self.assertIn("cerberus_get_task_state", self.text(agent_hooks.handle_context(self.payload(), self.root)))

    def test_invalid_accounting_values_do_not_reset_the_budget(self):
        self.seed()
        agent_hooks.handle_context(self.payload(), self.root)
        state = next((self.root / ".cerberus/hooks").glob("context-*.json"))
        for invalid in (-1, True, 12001, "0"):
            with self.subTest(used_chars=invalid):
                state.write_text(json.dumps({"schema_version": agent_hooks.CONTEXT_STATE_VERSION,
                                             "used_chars": invalid, "delivered": [],
                                             "hook_initialized": False}), encoding="utf-8")
                self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))

    def test_changing_session_gets_an_independent_budget(self):
        self.seed()
        agent_hooks.handle_context(self.payload(), self.root)
        other = {**self.payload(), "session_id": "independent-session"}
        self.assertIn("cerberus_get_task_state", self.text(agent_hooks.handle_context(other, self.root)))

    def test_session_clear_restores_memory_and_begins_a_new_budget(self):
        self.seed()
        agent_hooks.handle_context(self.payload(), self.root)
        self.assertIn("cerberus_get_task_state", self.text(agent_hooks.handle_context(
            {**self.payload("SessionStart"), "source": "clear"}, self.root)))

    def test_legacy_state_waits_for_compaction_instead_of_guessing_old_budget(self):
        self.seed()
        agent_hooks.handle_context(self.payload(), self.root)
        state = next((self.root / ".cerberus/hooks").glob("context-*.json"))
        state.write_text('{"digest":"old-history","project_id":"biolar"}', encoding="utf-8")
        self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))
        self.assertTrue(agent_hooks.handle_context({**self.payload("SessionStart"), "source": "compact"}, self.root))

    def test_concurrent_handlers_deliver_identical_memory_once(self):
        self.seed()
        from concurrent.futures import ThreadPoolExecutor
        import threading
        ready = threading.Barrier(2)

        def deliver():
            ready.wait(timeout=5)
            return agent_hooks.handle_context(self.payload(), self.root)

        with ThreadPoolExecutor(max_workers=2) as pool:
            outputs = list(pool.map(lambda _: deliver(), range(2)))
        self.assertEqual(1, sum(bool(self.text(output)) for output in outputs))

    def test_health_never_stores_prompt_or_credentials(self):
        self.seed()
        payload = self.payload()
        payload["prompt"] += " NEVER-STORE-PROMPT token: sk-abcdefghijklmnopqrstuvwx"
        agent_hooks.handle_context(payload, self.root)
        raw = "".join(p.read_text(encoding="utf-8") for p in (self.root / ".cerberus" / "hooks").glob("*.json"))
        self.assertNotIn("NEVER-STORE-PROMPT", raw)
        self.assertNotIn("sk-abcdefghijklmnopqrstuvwx", raw)

    def test_missing_index_is_visible_without_creating_a_database(self):
        text = self.text(agent_hooks.handle_context(self.payload(), self.root))
        self.assertIn("cerberus_get_task_state", text)
        self.assertLessEqual(len(text), 600)
        self.assertFalse((self.root / ".cerberus" / "index.db").exists())


    def test_changed_project_context_is_not_suppressed(self):
        self.seed()
        agent_hooks.handle_context(self.payload(), self.root)
        payload = {**self.payload(), "cwd": str(self.root / "projects" / "helpdev")}
        self.assertEqual({}, agent_hooks.handle_context(payload, self.root))


    def test_session_start_refreshes_changed_markdown_incrementally(self):
        self.seed()
        source = self.root / "projects" / "biolar" / "arquitetura.md"
        source.write_text("# Arquitetura biolar\n\nUPDATED-CANONICAL-EVIDENCE", encoding="utf-8")
        text = self.text(agent_hooks.handle_context(self.payload("SessionStart"), self.root))
        self.assertNotIn("UPDATED-CANONICAL-EVIDENCE", text)
        index = SQLiteMemoryIndex(self.root / ".cerberus/index.db")
        self.assertTrue(any("UPDATED-CANONICAL-EVIDENCE" in item.full_text for item in index.all_items()))


    def test_quiet_failures_are_visible_and_do_not_log_exception_content(self):
        self.seed()
        with patch("engine.agent_hooks.delivery_transaction",
                   side_effect=ValueError("NEVER-LOG-THIS-SECRET")):
            self.assertEqual({}, agent_hooks.handle_context(self.payload(), self.root))
        health = agent_hooks.get_hook_health(self.root)
        self.assertEqual("ERROR", health["latest_runs"][0]["status"])
        self.assertEqual("ValueError", health["latest_runs"][0]["error_type"])
        self.assertNotIn("NEVER-LOG-THIS-SECRET", json.dumps(health))

    def test_context_command_emits_native_json_contract(self):
        self.seed()
        import os
        env = dict(os.environ, CERBERUS_HOOK_ROOT=str(self.root), CERBERUS_HOOK_CHECK="1")
        script = Path(__file__).resolve().parent.parent / "hooks" / "codex_context.py"
        result = subprocess.run([sys.executable, str(script)], input=json.dumps(self.payload()),
            capture_output=True, text=True, encoding="utf-8", env=env, timeout=10)
        self.assertEqual(0, result.returncode, result.stderr)
        output = json.loads(result.stdout)
        self.assertEqual("UserPromptSubmit", output["hookSpecificOutput"]["hookEventName"])
        self.assertNotIn("decision", output)

    def test_doctor_handles_malformed_hook_configuration(self):
        folder = self.root / "codex"
        folder.mkdir()
        (folder / "hooks.json").write_text('{"hooks":{"Stop":{}}}', encoding="utf-8")
        self.assertEqual("INVALID_JSON", agent_hooks.inspect_codex_hooks(self.root, folder)["config_status"])

    def test_doctor_reports_absent_hooks_without_failing(self):
        result = agent_hooks.inspect_codex_hooks(self.root, self.root / "absent-codex")
        self.assertEqual(5, len(result["registrations"]))
        self.assertTrue(all(not row["registered"] for row in result["registrations"]))
