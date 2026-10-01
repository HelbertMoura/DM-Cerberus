import tempfile
import unittest
from pathlib import Path

from engine.handoffs import HandoffStatus, HandoffStore


class TestHandoffStore(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.root = Path(self.temp_dir.name)
        (self.root / "LEARNINGS.md").write_text("# Learnings\n", encoding="utf-8")
        self.store = HandoffStore(cerebro_root=self.root)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    # ------------------------------------------------------------- creation
    def test_create_starts_open_with_typed_id(self) -> None:
        handoff = self.store.create(project_id="canteirohub", task_id="TASK-1",
                                    summary="Implementar endpoint X",
                                    from_agent="MAESTRO", to_role="QA")
        self.assertEqual(HandoffStatus.OPEN.value, handoff["status"])
        self.assertRegex(handoff["handoff_id"], r"^HDO-[a-f0-9]{12}$")
        self.assertEqual("MAESTRO", handoff["from_agent"])
        self.assertIsNone(handoff["claim"])
        self.assertTrue((self.root / ".cerberus" / "handoffs" / f"{handoff['handoff_id']}.json").exists())

    def test_create_requires_full_provenance(self) -> None:
        with self.assertRaises(ValueError):
            self.store.create(project_id="canteirohub", task_id="  ",
                              summary="Resumo", from_agent="MAESTRO")

    # ------------------------------------------------------------ claim-once
    def test_claim_is_exclusive_second_claimer_loses(self) -> None:
        handoff = self.store.create(project_id="biolar", task_id="TASK-2",
                                    summary="Corrigir template", from_agent="MAESTRO")
        winner = self.store.claim(handoff["handoff_id"], agent="M3")
        self.assertEqual(HandoffStatus.CLAIMED.value, winner["status"])
        self.assertEqual("M3", winner["claim"]["agent"])
        with self.assertRaises(ValueError) as ctx:
            self.store.claim(handoff["handoff_id"], agent="FLASH")
        self.assertIn("CLAIMED", str(ctx.exception))

    def test_claim_marker_gate_rejects_when_marker_preexists(self) -> None:
        handoff = self.store.create(project_id="biolar", task_id="TASK-2b",
                                    summary="Corrida de claims", from_agent="MAESTRO")
        # Simula a corrida: outro processo criou o marker O_EXCL mas o JSON
        # ainda está OPEN — o gate atômico deve barrar com "already claimed".
        marker = self.root / ".cerberus" / "handoffs" / f"{handoff['handoff_id']}.claim"
        marker.write_text('{"agent": "OUTRO"}', encoding="utf-8")
        with self.assertRaises(ValueError) as ctx:
            self.store.claim(handoff["handoff_id"], agent="M3")
        self.assertIn("already claimed", str(ctx.exception))
        item = self.store.get(handoff["handoff_id"])
        self.assertEqual(HandoffStatus.OPEN.value, item["status"])

    def test_claim_rejects_non_open(self) -> None:
        handoff = self.store.create(project_id="biolar", task_id="TASK-3",
                                    summary="Ajuste", from_agent="MAESTRO")
        self.store.claim(handoff["handoff_id"], agent="M3")
        self.store.complete(handoff["handoff_id"], agent="M3")
        with self.assertRaises(ValueError):
            self.store.claim(handoff["handoff_id"], agent="FLASH")

    def test_reserved_role_blocks_other_agents(self) -> None:
        handoff = self.store.create(project_id="helpdev", task_id="TASK-4",
                                    summary="Onda mobile", from_agent="MAESTRO",
                                    to_role="QA")
        with self.assertRaises(ValueError):
            self.store.claim(handoff["handoff_id"], agent="M3")
        claimed = self.store.claim(handoff["handoff_id"], agent="qa")
        self.assertEqual("qa", claimed["claim"]["agent"])

    # --------------------------------------------------------------- closing
    def test_complete_requires_claiming_agent(self) -> None:
        handoff = self.store.create(project_id="helpdev", task_id="TASK-5",
                                    summary="Deploy gate", from_agent="MAESTRO")
        self.store.claim(handoff["handoff_id"], agent="M3")
        with self.assertRaises(ValueError):
            self.store.complete(handoff["handoff_id"], agent="FLASH")
        done = self.store.complete(handoff["handoff_id"], agent="M3", result="Suíte verde")
        self.assertEqual(HandoffStatus.DONE.value, done["status"])
        self.assertEqual("Suíte verde", done["done"]["result"])

    def test_cancel_open_by_any_agent_and_claimed_by_owner_only(self) -> None:
        open_handoff = self.store.create(project_id="apae-juatuba", task_id="TASK-6",
                                         summary="Publicar aviso", from_agent="MAESTRO")
        cancelled = self.store.cancel(open_handoff["handoff_id"], agent="FLASH")
        self.assertEqual(HandoffStatus.CANCELLED.value, cancelled["status"])

        claimed = self.store.create(project_id="apae-juatuba", task_id="TASK-7",
                                    summary="Corrigir link", from_agent="MAESTRO")
        self.store.claim(claimed["handoff_id"], agent="M3")
        with self.assertRaises(ValueError):
            self.store.cancel(claimed["handoff_id"], agent="FLASH")
        cancelled_owner = self.store.cancel(claimed["handoff_id"], agent="M3")
        self.assertEqual(HandoffStatus.CANCELLED.value, cancelled_owner["status"])

    # ------------------------------------------------------------ queries/id
    def test_list_filters_by_status(self) -> None:
        a = self.store.create(project_id="biolar", task_id="TASK-8", summary="A", from_agent="M")
        self.store.create(project_id="biolar", task_id="TASK-9", summary="B", from_agent="M")
        self.store.claim(a["handoff_id"], agent="M3")
        open_items = self.store.list(status=HandoffStatus.OPEN.value)
        claimed_items = self.store.list(status=HandoffStatus.CLAIMED.value)
        self.assertEqual(1, len(open_items))
        self.assertEqual(1, len(claimed_items))
        self.assertEqual("TASK-8", claimed_items[0]["task_id"])

    def test_find_open_by_task(self) -> None:
        handoff = self.store.create(project_id="canteirohub", task_id="TASK-10",
                                    summary="Prova de render", from_agent="MAESTRO")
        found = self.store.find_open_by_task("TASK-10", project_id="canteirohub")
        self.assertEqual([handoff["handoff_id"]], [h["handoff_id"] for h in found])
        self.assertEqual([], self.store.find_open_by_task("TASK-10", project_id="biolar"))

    def test_invalid_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            self.store.get("../escape")
        with self.assertRaises(ValueError):
            self.store.get("HDO-zzzz")

    def test_store_never_touches_canonical_markdown(self) -> None:
        before = (self.root / "LEARNINGS.md").read_bytes()
        handoff = self.store.create(project_id="biolar", task_id="TASK-11",
                                    summary="Nada canônico", from_agent="M")
        self.store.claim(handoff["handoff_id"], agent="M3")
        self.store.complete(handoff["handoff_id"], agent="M3")
        self.assertEqual(before, (self.root / "LEARNINGS.md").read_bytes())


if __name__ == "__main__":
    unittest.main()
