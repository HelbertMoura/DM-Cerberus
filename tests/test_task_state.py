"""Operational task checkpoints, always exercised in temporary roots."""
import importlib.util
import json
import os
import subprocess
import tempfile
import unittest
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch


def _save_checkpoint(arguments):
    from engine.task_state import TaskStateStore
    directory, number = arguments
    return TaskStateStore(directory).save("alpha", "TASK-1", f"Objetivo {number}",
                                         decisions=[f"Decisão {number}"], next_step=str(number))


class TestTaskState(unittest.TestCase):
    def setUp(self):
        from engine.task_state import TaskStateStore
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.store = TaskStateStore(self.root)

    def state_path(self):
        return next((self.root / ".cerberus" / "task_state").rglob("*.json"))

    def test_save_then_get_roundtrip_and_missing_task(self):
        self.assertIsNotNone(importlib.util.find_spec("engine.task_state"),
                             "TaskStateStore must provide task checkpoints")
        from engine.task_state import TaskStateStore

        with tempfile.TemporaryDirectory() as directory:
            store = TaskStateStore(Path(directory))
            self.assertEqual({"found": False, "project_id": "alpha", "task_id": "TASK-1"},
                             store.get("alpha", "TASK-1"))
            receipt = store.save("alpha", "TASK-1", "Corrigir retomada",
                                 ["Usar stdlib"], ["engine/task_state.py"],
                                 ["Testes focais"], "Integrar MCP")
            state = store.get("alpha", "TASK-1")
            self.assertTrue(receipt["saved"])
            self.assertTrue(state["found"])
            self.assertEqual("Corrigir retomada", state["objective"])
            self.assertEqual(["Usar stdlib"], state["decisions"])
            self.assertEqual(["engine/task_state.py"], state["files"])
            self.assertEqual(["Testes focais"], state["validation"])
            self.assertEqual("Integrar MCP", state["next_step"])
            self.assertEqual("in_progress", state["status"])
            self.assertEqual(1, receipt["version"])
            self.assertEqual(receipt["hash"], state["hash"])

    def test_updates_are_versioned_and_projects_and_tasks_are_isolated(self):
        self.store.save("alpha", "TASK-1", "Primeiro")
        self.store.save("beta", "TASK-1", "Outro projeto")
        self.store.save("alpha", "TASK-2", "Outra tarefa")
        receipt = self.store.save("alpha", "TASK-1", "Atualizado", status="paused")
        self.assertEqual(2, receipt["version"])
        self.assertEqual("Atualizado", self.store.get("alpha", "TASK-1")["objective"])
        self.assertEqual("paused", self.store.get("alpha", "TASK-1")["status"])
        self.assertEqual("Outro projeto", self.store.get("beta", "TASK-1")["objective"])
        self.assertEqual("Outra tarefa", self.store.get("alpha", "TASK-2")["objective"])
        self.assertFalse(self.store.get("ALPHA", "TASK-1")["found"])

    def test_invalid_identifiers_do_not_create_state(self):
        for identifier in ("", "../outside", "..", "a/b", "a\\b", "a:stream", " x", "a" * 97,
                           True, 12, None, "sk-abcdefghijklmnopqrstuvwx"):
            for project, task in ((identifier, "TASK-1"), ("alpha", identifier)):
                with self.subTest(project=project, task=task):
                    with self.assertRaises(ValueError):
                        self.store.save(project, task, "Objetivo")
                    with self.assertRaises(ValueError):
                        self.store.get(project, task)
        self.assertEqual([], list(self.root.iterdir()))

    def test_invalid_fields_do_not_persist(self):
        invalid = [dict(objective=None), dict(objective="  "), dict(objective=True),
                   dict(objective="x" * 200001), dict(decisions="texto"),
                   dict(files=[Path("reference.md")]), dict(validation=[False]),
                   dict(decisions=["ok"] * 12 + [5]), dict(next_step=[]),
                   dict(status="unknown"), dict(status=[]), dict(status=True)]
        for fields in invalid:
            with self.subTest(fields=list(fields)), self.assertRaises(ValueError):
                self.store.save("alpha", "TASK-1", **(dict(objective="Objetivo") | fields))
        self.assertEqual([], list(self.root.iterdir()))

    def test_non_directory_storage_component_is_rejected(self):
        barrier = self.root / ".cerberus"
        barrier.write_text("Preservar", encoding="utf-8")
        with self.assertRaises(ValueError):
            self.store.save("alpha", "TASK-1", "Operação")
        with self.assertRaises(ValueError):
            self.store.get("alpha", "TASK-1")
        self.assertEqual("Preservar", barrier.read_text(encoding="utf-8"))

    def test_secrets_are_redacted_in_every_persisted_text_field(self):
        secrets = ["sk-abcdefghijklmnopqrstuvwx", "ghp_abcdefghijklmnopqrstuvwxyz",
                   "tiny-password", "temporary-bearer-token", "db-secret"]
        self.store.save("alpha", "TASK-1", "Revisar " + secrets[0],
                        decisions=["password=" + secrets[2]],
                        files=["postgres://user:" + secrets[4] + "@host/db", "Revisar " + secrets[1]],
                        validation=["Authorization: Bearer " + secrets[3]],
                        next_step="client_secret=hidden-next-secret")
        serialized = self.state_path().read_text(encoding="utf-8")
        for secret in secrets + ["hidden-next-secret"]:
            self.assertNotIn(secret, serialized)
        self.assertIn("[REDACTED]", serialized)
        self.assertTrue(self.store.get("alpha", "TASK-1")["redacted"])

    def test_reference_urls_with_credentials_and_query_tokens_are_redacted(self):
        self.store.save("alpha", "TASK-1", "Referências", files=[
            "https://user:secret-reference-password@example.org/a?token=secret-query-token",
            "https://example.org/a?api_key=secret-api-key&public=yes"])
        serialized = self.state_path().read_text(encoding="utf-8")
        for secret in ("secret-reference-password", "secret-query-token", "secret-api-key"):
            self.assertNotIn(secret, serialized)

    def test_quoted_secrets_and_unterminated_private_keys_are_redacted(self):
        self.store.save("alpha", "TASK-1", 'Config "password": "two word secret"',
            decisions=["secret='small generic secret'"],
            validation=['{"api_key": "json-secret-value"}'],
            next_step="-----BEGIN PRIVATE KEY-----\nunterminated-secret-key")
        serialized = self.state_path().read_text(encoding="utf-8")
        for secret in ("two word secret", "small generic secret", "json-secret-value",
                       "unterminated-secret-key"):
            self.assertNotIn(secret, serialized)

    def test_escaped_quotes_do_not_leave_secret_suffixes_in_saved_or_read_state(self):
        values = [json.dumps({"api_key": 'QA-SYNTHETIC-ONE "QA-SYNTHETIC-TWO" \\ QA-SYNTHETIC-THREE'}),
                  r"token='QA-SYNTHETIC-ONE \'QA-SYNTHETIC-TWO\' \\ QA-SYNTHETIC-THREE'"]
        for value in values:
            with self.subTest(quoted=value[:10]):
                self.store.save("alpha", "TASK-1", value, decisions=[value], files=[value],
                                validation=[value], next_step=value)
                state = self.store.get("alpha", "TASK-1")
                persisted = self.state_path().read_text(encoding="utf-8")
                for secret in ("QA-SYNTHETIC-ONE", "QA-SYNTHETIC-TWO", "QA-SYNTHETIC-THREE"):
                    self.assertNotIn(secret, persisted)
                    self.assertNotIn(secret, json.dumps(state))
                self.assertTrue(state["redacted"])

    def test_escaped_secret_is_redacted_before_field_length_cut(self):
        value = json.dumps({"api_key": 'QA-SYNTHETIC-ONE "QA-SYNTHETIC-TWO" ' + "x" * 1000})
        self.store.save("alpha", "TASK-1", "a" * 560 + value, decisions=["b" * 200 + value])
        state = self.store.get("alpha", "TASK-1")
        self.assertTrue(state["redacted"])
        self.assertFalse(state["truncated"])
        self.assertIn("[REDACTED]", state["objective"])
        self.assertIn("[REDACTED]", state["decisions"][0])
        self.assertNotIn("QA-SYNTHETIC", self.state_path().read_text(encoding="utf-8"))

    def test_unterminated_quoted_secrets_redact_the_remaining_value(self):
        values = [r'api_key="QA-SYNTHETIC-ONE \"QA-SYNTHETIC-TWO\" QA-SYNTHETIC-THREE',
                  r"token='QA-SYNTHETIC-ONE \'QA-SYNTHETIC-TWO\' QA-SYNTHETIC-THREE"]
        for value in values + [value + chr(92) for value in values]:
            with self.subTest(quoted=value[:10], trailing_backslash=value.endswith(chr(92))):
                self.store.save("alpha", "TASK-1", value, next_step=value)
                state = self.store.get("alpha", "TASK-1")
                self.assertTrue(state["redacted"])
                self.assertNotIn("QA-SYNTHETIC", json.dumps(state))
                self.assertNotIn("QA-SYNTHETIC", self.state_path().read_text(encoding="utf-8"))

    def test_state_budget_accounts_for_json_escaping_and_array_overflow(self):
        for character in ("ç", "\x00", "\\", '"'):
            with self.subTest(character=character):
                receipt = self.store.save("alpha", "TASK-1", character * 10000,
                    decisions=[character * 10000] * 100, files=[character * 10000] * 100,
                    validation=[character * 10000] * 100, next_step=character * 10000)
                state = self.store.get("alpha", "TASK-1")
                self.assertTrue(receipt["truncated"])
                self.assertLessEqual(len(json.dumps(state, ensure_ascii=False, indent=2)), 6000)
                self.assertLessEqual(len(self.state_path().read_text(encoding="utf-8")), 6000)
                for name in ("decisions", "files", "validation"):
                    self.assertLessEqual(len(state[name]), 12)

    def test_references_are_not_opened_or_written_and_canonical_files_unchanged(self):
        canonical = self.root / "AGENTS.md"
        canonical.write_text("Conteúdo canônico", encoding="utf-8")
        self.store.save("alpha", "TASK-1", "Operação", files=[str(canonical),
                        "../../outside.md", "C:\\Windows\\system.ini"], status="done")
        self.assertEqual("Conteúdo canônico", canonical.read_text(encoding="utf-8"))
        self.assertEqual("done", self.store.get("alpha", "TASK-1")["status"])
        self.assertEqual({"AGENTS.md", ".cerberus"}, {path.name for path in self.root.iterdir()})

    def test_corrupt_or_tampered_state_is_rejected_without_overwriting(self):
        self.store.save("alpha", "TASK-1", "Estado íntegro")
        path = self.state_path()
        original = json.loads(path.read_text(encoding="utf-8"))
        for document in ("not-json", "[]", json.dumps(original | {"objective": "Alterado"}),
                         json.dumps(original | {"transcript": "chat bruto"}), "x" * 6001):
            path.write_text(document, encoding="utf-8")
            with self.subTest(document=document[:30]):
                with self.assertRaises(ValueError):
                    self.store.get("alpha", "TASK-1")
                with self.assertRaises(ValueError):
                    self.store.save("alpha", "TASK-1", "Novo")
                self.assertEqual(document, path.read_text(encoding="utf-8"))

    def test_atomic_replace_failure_preserves_previous_checkpoint(self):
        self.store.save("alpha", "TASK-1", "Antes")
        with patch("engine.task_state.os.replace", side_effect=OSError("simulated failure")):
            with self.assertRaises(OSError):
                self.store.save("alpha", "TASK-1", "Depois")
        self.assertEqual("Antes", self.store.get("alpha", "TASK-1")["objective"])
        self.assertEqual([], list(self.state_path().parent.glob("*.tmp")))

    def test_thread_writers_keep_coherent_state_and_unique_versions(self):
        with ThreadPoolExecutor(max_workers=8) as pool:
            receipts = list(pool.map(_save_checkpoint, [(str(self.root), number) for number in range(24)]))
        self.assertEqual(list(range(1, 25)), sorted(receipt["version"] for receipt in receipts))
        state = self.store.get("alpha", "TASK-1")
        number = state["next_step"]
        self.assertEqual(24, state["version"])
        self.assertEqual(f"Objetivo {number}", state["objective"])
        self.assertEqual([f"Decisão {number}"], state["decisions"])

    def test_process_writers_serialize_versions(self):
        with ProcessPoolExecutor(max_workers=4) as pool:
            receipts = list(pool.map(_save_checkpoint, [(str(self.root), number) for number in range(12)]))
        self.assertEqual(list(range(1, 13)), sorted(receipt["version"] for receipt in receipts))
        self.assertEqual(12, self.store.get("alpha", "TASK-1")["version"])

    def test_symlinked_state_directory_cannot_escape_root(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / ".cerberus").mkdir()
            try:
                (self.root / ".cerberus" / "task_state").symlink_to(outside, target_is_directory=True)
            except OSError as error:
                self.skipTest(f"Symlink unavailable: {error.winerror if hasattr(error, 'winerror') else error.errno}")
            with self.assertRaises(ValueError):
                self.store.save("alpha", "TASK-1", "Escape")
            with self.assertRaises(ValueError):
                self.store.get("alpha", "TASK-1")
            self.assertEqual([], list(Path(outside).iterdir()))

    def test_symlinked_checkpoint_cannot_read_or_replace_canonical_file(self):
        self.store.save("alpha", "TASK-1", "Inicial")
        canonical = self.root / "canonical.md"
        canonical.write_text("Canônico intacto", encoding="utf-8")
        path = self.state_path()
        path.unlink()
        try:
            path.symlink_to(canonical)
        except OSError as error:
            self.skipTest(f"Symlink unavailable: {getattr(error, 'winerror', error.errno)}")
        with self.assertRaises(ValueError):
            self.store.get("alpha", "TASK-1")
        with self.assertRaises(ValueError):
            self.store.save("alpha", "TASK-1", "Novo")
        self.assertEqual("Canônico intacto", canonical.read_text(encoding="utf-8"))

    def test_hardlinked_checkpoint_is_rejected(self):
        self.store.save("alpha", "TASK-1", "Inicial")
        path = self.state_path()
        canonical = self.root / "canonical.md"
        os.link(path, canonical)
        with self.assertRaises(ValueError):
            self.store.get("alpha", "TASK-1")
        with self.assertRaises(ValueError):
            self.store.save("alpha", "TASK-1", "Novo")

    @unittest.skipUnless(os.name == "nt", "Windows junction fixture")
    def test_windows_junction_cannot_redirect_state_storage(self):
        with tempfile.TemporaryDirectory() as outside:
            (self.root / ".cerberus").mkdir()
            junction = self.root / ".cerberus" / "task_state"
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(junction), outside],
                                    capture_output=True)
            self.assertEqual(0, result.returncode, "Temporary junction fixture must be created")
            with self.assertRaises(ValueError):
                self.store.save("alpha", "TASK-1", "Escape")
            with self.assertRaises(ValueError):
                self.store.get("alpha", "TASK-1")
            self.assertEqual([], list(Path(outside).iterdir()))

    def test_state_with_valid_hash_still_requires_valid_fields(self):
        import hashlib

        self.store.save("alpha", "TASK-1", "Inicial")
        path = self.state_path()
        original = json.loads(path.read_text(encoding="utf-8"))
        for changes in (dict(version=True), dict(status="invalid"), dict(files=None),
                        dict(decisions=[True]), dict(objective="password=hidden-secret"),
                        dict(validation=["x"] * 13), dict(objective="x" * 601),
                        dict(project_id="beta"), dict(redacted="yes")):
            state = original | changes
            state["hash"] = hashlib.sha256(json.dumps({key: value for key, value in state.items()
                if key != "hash"}, ensure_ascii=False, indent=2, sort_keys=True).encode("utf-8")).hexdigest()
            path.write_text(json.dumps(state), encoding="utf-8")
            with self.subTest(changes=list(changes)), self.assertRaises(ValueError):
                self.store.get("alpha", "TASK-1")

    def test_hardlinked_lock_file_is_rejected_before_write(self):
        self.store.save("alpha", "TASK-1", "Inicial")
        lock = self.state_path().with_suffix(".lock")
        canonical = self.root / "canonical.md"
        os.link(lock, canonical)
        with self.assertRaises(ValueError):
            self.store.save("alpha", "TASK-1", "Novo")
        with self.assertRaises(ValueError):
            self.store.get("alpha", "TASK-1")


if __name__ == "__main__":
    unittest.main()
