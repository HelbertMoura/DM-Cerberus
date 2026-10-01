import json
import tempfile
import threading
import unittest
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest.mock import patch

from engine.context_budget import fit_context_pack
from engine.models import ContextPack, MemoryItem, SourceType

try:
    from engine import session_delivery as delivery
except ImportError:
    delivery = None


class TestSessionDelivery(unittest.TestCase):
    def setUp(self):
        self.assertIsNotNone(delivery, "shared session delivery is missing")
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)

    def item(self):
        return MemoryItem("memory-1", "biolar", "projects/biolar/a.md",
                          SourceType.ARCHITECTURE, "Arquitetura", snippet="evidência " * 100,
                          full_text="versão canônica " * 100, updated_at="2026-09-30")

    def test_public_token_and_native_id_share_ledger_without_raw_id(self):
        session = "private-native-conversation"
        token = delivery.session_token(session)
        self.assertRegex(token, r"^cbr-[0-9a-f]{24}$")
        with delivery.delivery_transaction(self.root, session) as transaction:
            transaction.commit(100, ["a" * 64])
        with delivery.delivery_transaction(self.root, token) as transaction:
            self.assertEqual(11900, transaction.remaining)
            self.assertEqual({"a" * 64}, transaction.seen)
        files = list((self.root / ".cerberus/hooks").glob("*.json"))
        self.assertEqual(1, len(files))
        self.assertNotIn(session, files[0].read_text(encoding="utf-8"))

    def test_budget_rejects_overspend_and_other_session_is_independent(self):
        with delivery.delivery_transaction(self.root, "first") as transaction:
            transaction.commit(12000, ["a" * 64])
        with delivery.delivery_transaction(self.root, "first") as transaction:
            self.assertEqual(0, transaction.remaining)
            with self.assertRaises(ValueError):
                transaction.commit(1, ["b" * 64])
        self.assertEqual(12000, delivery.context_status(self.root, "other")["remaining_chars"])

    def test_mcp_spend_does_not_initialize_hook(self):
        with delivery.delivery_transaction(self.root, "conversation") as transaction:
            transaction.commit(200, ["a" * 64])
        with delivery.delivery_transaction(self.root, "conversation") as transaction:
            self.assertFalse(transaction.hook_initialized)
            transaction.commit(0, [], hook_initialized=True)
        with delivery.delivery_transaction(self.root, "conversation") as transaction:
            self.assertTrue(transaction.hook_initialized)
            self.assertEqual(11800, transaction.remaining)

    def test_preview_preserves_canonical_version_without_mutating_source(self):
        item = self.item()
        key = delivery.memory_fingerprint(item)
        pack = fit_context_pack(ContextPack("biolar", "arquitetura", "DEVELOPER",
                                           relevant_architecture=[item]), 1500)
        preview = pack.relevant_architecture[0]
        self.assertLess(len(preview.snippet), len(item.snippet))
        self.assertEqual(key, delivery.memory_fingerprint(preview))
        self.assertNotIn("_delivery_fingerprint", item.metadata)
        item.full_text += " nova decisão"
        self.assertNotEqual(key, delivery.memory_fingerprint(item))

    def test_legacy_and_corrupt_state_never_restore_budget_without_reset(self):
        token = delivery.session_token("conversation")
        path = self.root / ".cerberus/hooks" / f"context-{token[4:]}.json"
        path.parent.mkdir(parents=True)
        for document in ({"digest": "old"}, {"schema_version": 2, "used_chars": 10, "delivered": []}):
            path.write_text(json.dumps(document), encoding="utf-8")
            self.assertEqual(0, delivery.context_status(self.root, token)["remaining_chars"])
        path.write_text("{broken", encoding="utf-8")
        with self.assertRaises(ValueError):
            delivery.context_status(self.root, token)
        self.assertEqual(12000, delivery.context_status(self.root, token, reset=True)["remaining_chars"])
        self.assertEqual(12000, delivery.context_status(self.root, "conversation")["remaining_chars"])

    def test_persistence_failure_blocks_commit_and_keeps_previous_spend(self):
        with delivery.delivery_transaction(self.root, "conversation") as transaction:
            transaction.commit(40, [])
        with patch("engine.session_delivery.atomic_json", side_effect=OSError("private error")):
            with self.assertRaises(OSError):
                with delivery.delivery_transaction(self.root, "conversation") as transaction:
                    transaction.commit(60, ["a" * 64])
        status = delivery.context_status(self.root, "conversation")
        self.assertEqual(40, status["used_chars"])
        self.assertNotIn("private error", json.dumps(status))

    def test_concurrent_duplicate_delivers_once(self):
        ready = threading.Barrier(2)
        def deliver():
            ready.wait(timeout=5)
            try:
                with delivery.delivery_transaction(self.root, "conversation") as transaction:
                    if "a" * 64 in transaction.seen:
                        return False
                    transaction.commit(100, ["a" * 64])
                    return True
            except OSError:
                return False
        with ThreadPoolExecutor(max_workers=2) as pool:
            outputs = list(pool.map(lambda _: deliver(), range(2)))
        self.assertEqual(1, sum(outputs))
        self.assertEqual(100, delivery.context_status(self.root, "conversation")["used_chars"])

    def test_invalid_ids_are_rejected_without_echo(self):
        for session in ("", " ", "x" * 513, "raw\nconversation", "cbr-not-valid", "sk-abcdefghijklmnopqrstuvwx", 3):
            with self.subTest(session_type=type(session).__name__):
                with self.assertRaises(ValueError) as error:
                    delivery.session_token(session)
                self.assertEqual("Invalid session identity", str(error.exception))

    def test_invalid_commit_does_not_change_state(self):
        with delivery.delivery_transaction(self.root, "conversation") as transaction:
            for chars, keys in ((True, []), (-1, []), (1, ["raw-memory"]), (1, "a" * 64)):
                with self.assertRaises(ValueError):
                    transaction.commit(chars, keys)
            self.assertEqual(12000, transaction.remaining)

    def test_malformed_current_state_blocks_delivery(self):
        with delivery.delivery_transaction(self.root, "conversation") as transaction:
            transaction.commit(100, [])
        path = next((self.root / ".cerberus/hooks").glob("context-*.json"))
        valid = json.loads(path.read_text(encoding="utf-8"))
        for field, value in (("schema_version", 3.0), ("used_chars", True),
                             ("hook_initialized", "false"), ("delivered", ["not-a-hash"])):
            with self.subTest(field=field):
                path.write_text(json.dumps({**valid, field: value}), encoding="utf-8")
                with self.assertRaises(ValueError):
                    delivery.context_status(self.root, "conversation")
