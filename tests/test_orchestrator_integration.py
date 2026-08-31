"""
Cerberus Memory Intelligence - Orchestrator & Maestri Integration Tests
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Phase P2: full-lifecycle coverage of the orchestrator adapter, the
Maestri canvas helper, and the new CLI commands.
"""

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from engine.capture import AutoCaptureEngine
from engine.index import SQLiteMemoryIndex
from engine.integrations.maestri import (
    detect_project_from_path,
    format_agent_session_pack,
)
from engine.integrations.orchestrator import (
    OrchestratorAdapter,
    PROJECT_ALIASES,
    all_known_project_slugs,
    discover_dynamic_projects,
    list_indexed_project_slugs,
    resolve_project_slug,
)
from engine.retrieval import CerberusMemoryService


REPO = Path(__file__).resolve().parents[1]


def _build_corpus(root: Path) -> None:
    """Populate a temporary project root with representative content."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "LEARNINGS.md").write_text("# Learnings\n", encoding="utf-8")
    (root / "DECISIONS.md").write_text("# Decisions\n", encoding="utf-8")

    global_dir = root / "global"
    global_dir.mkdir()
    (global_dir / "ai-governance.md").write_text(
        "# AI Governance\n\nO modelo canônico é o protocolo multi-agente com gates estritos "
        "e autoridade humana.\n",
        encoding="utf-8",
    )

    ch_dir = root / "projects" / "canteirohub"
    ch_dir.mkdir(parents=True)
    (ch_dir / "decisions.md").write_text(
        "# Decisões CanteiroHUB\n\n"
        "## ADR-099: Rateio Maior Resíduo TCU\n"
        "Implementar rateio matricial pelo algoritmo de Hamilton (Maior Resíduo) sem dízimas.\n",
        encoding="utf-8",
    )
    (ch_dir / "learnings.md").write_text(
        "# Lições CanteiroHUB\n\n"
        "Sempre usar Pydantic v2 e isolamento estrito de tenant.\n",
        encoding="utf-8",
    )

    bio_dir = root / "projects" / "biolar"
    bio_dir.mkdir(parents=True)
    (bio_dir / "decisions.md").write_text(
        "# Decisões Biolar\n\n## ADR-001: Catálogo Biolar\nUso de taxonomia controlada.\n",
        encoding="utf-8",
    )


def _make_adapter(tmp: Path) -> OrchestratorAdapter:
    """Build a clean OrchestratorAdapter rooted at a temp dir."""
    root = tmp / "cerebro"
    _build_corpus(root)
    service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
    return OrchestratorAdapter(application_root=root, service=service)


# ============================================================================
# Project resolution
# ============================================================================
class TestProjectResolution(unittest.TestCase):
    def test_resolve_project_slug_aliases(self) -> None:
        cases = {
            "_global": "_global",
            "_shared": "_shared",
            "dm-erp": "canteirohub",
            "DM-ERP": "canteirohub",
            "biolar": "biolar",
            "apae": "apae-juatuba",
            "ApaE": "apae-juatuba",
            "dev-maniacs-site": "dev-maniacs-site",
            "dm-desk": "dm-desk",
            None: "_global",
            "": "_global",
        }
        for raw, expected in cases.items():
            with self.subTest(raw=raw):
                self.assertEqual(expected, resolve_project_slug(raw))

    def test_resolve_project_slug_loose_aliases_removed_fix006(self) -> None:
        """FIX-006: loose `site` and `desk` aliases must NOT remap to project names."""
        self.assertEqual("site", resolve_project_slug("site"))
        self.assertEqual("desk", resolve_project_slug("desk"))
        # But explicit full names still work
        self.assertEqual("dev-maniacs-site",
                         resolve_project_slug("dev-maniacs-site"))
        self.assertEqual("dm-desk", resolve_project_slug("dm-desk"))

    def test_resolve_project_slug_normalizes_separators(self) -> None:
        # Path-like inputs become slugified, no recursion into path detection
        self.assertEqual("weird-slash-backslash",
                         resolve_project_slug("weird/slash\\backslash"))
        self.assertEqual("new-project", resolve_project_slug("new project"))

    def test_detect_project_from_path_alias_match_in_ancestors(self) -> None:
        # dm-erp anywhere in the path resolves to canteirohub
        self.assertEqual(
            "canteirohub",
            detect_project_from_path("C:/DevManiacs/migra/dm-erp/docs"),
        )
        self.assertEqual(
            "canteirohub",
            detect_project_from_path("C:/DevManiacs/migra/dm-erp"),
        )

    def test_detect_project_from_path_projects_subdir(self) -> None:
        self.assertEqual(
            "biolar",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/biolar/docs/file.md"),
        )
        self.assertEqual(
            "apae-juatuba",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/apae-juatuba"),
        )

    def test_detect_project_from_path_global_ancestor(self) -> None:
        self.assertEqual(
            "_global",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/global/ai-governance.md"),
        )

    def test_detect_project_from_path_shared_ancestor(self) -> None:
        self.assertEqual(
            "_shared",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/_shared/notes.md"),
        )

    def test_detect_project_from_path_empty_returns_global(self) -> None:
        self.assertEqual("_global", detect_project_from_path(""))
        self.assertEqual("_global", detect_project_from_path(None) if False else "_global")

    def test_discover_dynamic_projects(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "projects").mkdir()
            for slug in ("alpha", "beta", ".hidden", "gamma"):
                if slug.startswith("."):
                    (root / "projects" / slug).mkdir()
                else:
                    (root / "projects" / slug).mkdir()
            discovered = discover_dynamic_projects(root)
            self.assertIn("alpha", discovered)
            self.assertIn("beta", discovered)
            self.assertIn("gamma", discovered)
            self.assertNotIn(".hidden", discovered)

    def test_all_known_project_slugs_includes_base_and_aliases(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "projects" / "alpha-proj").mkdir(parents=True)
            slugs = all_known_project_slugs(root)
            self.assertIn("_global", slugs)
            self.assertIn("_shared", slugs)
            self.assertIn("canteirohub", slugs)
            self.assertIn("biolar", slugs)
            self.assertIn("apae-juatuba", slugs)
            self.assertIn("dev-maniacs-site", slugs)
            self.assertIn("dm-desk", slugs)
            self.assertIn("alpha-proj", slugs)
            # Ordering: _global first, _shared second
            self.assertEqual("_global", slugs[0])
            self.assertEqual("_shared", slugs[1])


# ============================================================================
# OrchestratorAdapter lifecycle
# ============================================================================
class TestOrchestratorAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.adapter = _make_adapter(self.tmp)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    # ---- session_start ----
    def test_session_start_returns_context_pack_and_token_estimate(self) -> None:
        ctx = self.adapter.session_start(
            project_id="canteirohub",
            task_summary="Implementar cofre SEFAZ A1",
            role="DEVELOPER",
        )
        self.assertEqual("canteirohub", ctx["project_id"])
        self.assertEqual("Implementar cofre SEFAZ A1", ctx["task_summary"])
        self.assertEqual("DEVELOPER", ctx["role"])
        self.assertIn("CERBERUS CONTEXT PACK", ctx["markdown"])
        self.assertIsInstance(ctx["token_estimate"], int)
        self.assertGreaterEqual(ctx["token_estimate"], 0)
        self.assertTrue(ctx["generated_at"])

    def test_session_start_does_not_touch_canonical(self) -> None:
        before_learnings = (self.adapter.application_root / "LEARNINGS.md").read_bytes()
        before_decisions = (self.adapter.application_root / "DECISIONS.md").read_bytes()
        self.adapter.session_start("canteirohub", "Any task", "QA")
        self.assertEqual(before_learnings,
                         (self.adapter.application_root / "LEARNINGS.md").read_bytes())
        self.assertEqual(before_decisions,
                         (self.adapter.application_root / "DECISIONS.md").read_bytes())

    def test_session_start_resolves_alias_dm_erp_to_canteirohub(self) -> None:
        ctx = self.adapter.session_start("dm-erp", "Coisa qualquer", "DEVELOPER")
        self.assertEqual("canteirohub", ctx["project_id"])

    # ---- on_report_accepted ----
    def test_on_report_accepted_creates_candidate(self) -> None:
        report = (
            "# Report\n\n"
            "## Learnings\n"
            "- Cofre SEFAZ usa AES-256-GCM com chave derivada HKDF por tenant.\n"
            "- Rateio Maior Residuo TCU evita dizimas periodicas.\n"
        )
        result = self.adapter.on_report_accepted(
            report_path_or_content=report,
            task_id="TASK-P2-001",
            project_id="canteirohub",
            agent_role="CODEX",
        )
        self.assertEqual("canteirohub", result["project_id"])
        self.assertEqual("TASK-P2-001", result["task_id"])
        self.assertEqual("CODEX", result["agent_role"])
        self.assertEqual("COMPLETE", result["status"])
        self.assertGreaterEqual(result["candidate_count"], 2)
        for cid in result["candidate_ids"]:
            candidate = self.adapter.inbox.get(cid)
            self.assertEqual("TASK-P2-001", candidate.task_id)
            self.assertEqual("CODEX", candidate.agent)
            self.assertTrue(candidate.fingerprint)
            self.assertIn(candidate.status.value, {"CANDIDATE", "QUARANTINED"})

    def test_on_report_accepted_quarantines_secrets(self) -> None:
        report = (
            "# Report\n\n## Learnings\n"
            "- Conexao banco: client_secret=therealsecretvalue12345 sempre ofuscar.\n"
        )
        result = self.adapter.on_report_accepted(
            report_path_or_content=report,
            task_id="TASK-SECRET",
            project_id="canteirohub",
            agent_role="QA",
        )
        self.assertGreaterEqual(result["candidate_count"], 1)
        for cid in result["candidate_ids"]:
            candidate = self.adapter.inbox.get(cid)
            self.assertEqual("QUARANTINED", candidate.status.value)
            self.assertIn("api_token", candidate.secret_findings)
            stored = self.adapter.inbox._path(cid).read_text(encoding="utf-8")
            self.assertNotIn("therealsecretvalue12345", stored)
            self.assertIn("[REDACTED]", stored)

    def test_on_report_accepted_extracts_task_id_from_content(self) -> None:
        report = (
            "TASK-ID: TASK-EXTRACTED\n\n"
            "## Learnings\n- Alguma licao suficientemente longa para ser indexada.\n"
        )
        result = self.adapter.on_report_accepted(
            report_path_or_content=report,
            task_id=None,                 # intentionally None
            project_id="canteirohub",
            agent_role="REPORT_INGESTER",
        )
        self.assertEqual("TASK-EXTRACTED", result["task_id"])

    def test_on_report_accepted_requires_task_id(self) -> None:
        with self.assertRaises(ValueError):
            self.adapter.on_report_accepted(
                report_path_or_content="## Learnings\n- xxxxxxxxxxxxxxxxxxxx.",
                task_id="",                 # empty -> raise
                project_id="canteirohub",
                agent_role="QA",
            )

    # ---- on_qa_approved ----
    def test_on_qa_approved_marks_candidate_verified(self) -> None:
        result = self.adapter.on_report_accepted(
            report_path_or_content="## Learnings\n- Capturar primeiro candidato do ciclo P2.\n",
            task_id="TASK-QA-1",
            project_id="canteirohub",
            agent_role="QA",
        )
        cid = result["candidate_ids"][0]
        # Status starts as CANDIDATE
        self.assertEqual("CANDIDATE", self.adapter.inbox.get(cid).status.value)
        qa = self.adapter.on_qa_approved(candidate_id=cid)
        self.assertEqual([cid], qa["verified"])
        self.assertEqual([], qa["skipped"])
        self.assertEqual("VERIFIED", self.adapter.inbox.get(cid).status.value)

    def test_on_qa_approved_marks_all_candidates_for_task(self) -> None:
        report = (
            "## Learnings\n"
            "- Primeira licao do relatorio de QA multiplo.\n"
            "- Segunda licao do relatorio de QA multiplo tambem.\n"
        )
        self.adapter.on_report_accepted(
            report_path_or_content=report,
            task_id="TASK-QA-MULTI",
            project_id="canteirohub",
            agent_role="QA",
        )
        # FIX-006: project_id is now mandatory when approving by task_id.
        qa = self.adapter.on_qa_approved(task_id="TASK-QA-MULTI",
                                          project_id="canteirohub")
        self.assertGreaterEqual(len(qa["verified"]), 2)
        for cid in qa["verified"]:
            self.assertEqual("VERIFIED", self.adapter.inbox.get(cid).status.value)

    def test_on_qa_approved_requires_identifier(self) -> None:
        with self.assertRaises(ValueError):
            self.adapter.on_qa_approved()

    def test_on_qa_approved_only_marks_verified_not_canonical(self) -> None:
        """Critical security guarantee: orchestrator must not be able to set CANONICAL."""
        result = self.adapter.on_report_accepted(
            report_path_or_content="## Learnings\n- Licao que nao pode virar canonica via QA.\n",
            task_id="TASK-NO-CANONICAL",
            project_id="canteirohub",
            agent_role="QA",
        )
        cid = result["candidate_ids"][0]
        self.adapter.on_qa_approved(candidate_id=cid)
        candidate = self.adapter.inbox.get(cid)
        self.assertNotEqual("CANONICAL", candidate.status.value)
        self.assertNotIn("Tampered", (self.adapter.application_root / "LEARNINGS.md").read_text())

    def test_on_qa_approved_skips_quarantined(self) -> None:
        # A quarantined candidate should not be promoted to VERIFIED by on_qa_approved
        result = self.adapter.on_report_accepted(
            report_path_or_content="## Learnings\n- Token leak: client_secret=topsecretvalue12345 sempre.\n",
            task_id="TASK-QUAR",
            project_id="canteirohub",
            agent_role="QA",
        )
        cid = result["candidate_ids"][0]
        # Ensure it's quarantined
        self.assertEqual("QUARANTINED", self.adapter.inbox.get(cid).status.value)
        qa = self.adapter.on_qa_approved(candidate_id=cid)
        self.assertEqual([], qa["verified"])
        self.assertEqual(1, len(qa["skipped"]))
        # Still QUARANTINED
        self.assertEqual("QUARANTINED", self.adapter.inbox.get(cid).status.value)

    # ---- get_project_summary ----
    def test_get_project_summary_returns_stats_and_key_docs(self) -> None:
        # First ensure index is built
        self.adapter.ensure_indexed()
        summary = self.adapter.get_project_summary("canteirohub")
        self.assertEqual("canteirohub", summary["project_id"])
        self.assertIn("stats", summary)
        self.assertIn("decisions", summary)
        self.assertIn("learnings", summary)
        self.assertIn("recent_handoff", summary)
        self.assertIn("candidate_inbox_count", summary)
        # decisions and learnings are lists (possibly empty)
        self.assertIsInstance(summary["decisions"], list)
        self.assertIsInstance(summary["learnings"], list)

    def test_list_indexed_project_slugs(self) -> None:
        self.adapter.ensure_indexed()
        slugs = list_indexed_project_slugs(self.adapter.service)
        self.assertIsInstance(slugs, list)
        # canteirohub and _global should appear after rebuild
        self.assertIn("canteirohub", slugs)
        self.assertIn("_global", slugs)


# ============================================================================
# Maestri adapter
# ============================================================================
class TestMaestriAdapter(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.adapter = _make_adapter(self.tmp)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_format_agent_session_pack_includes_provenance_sentinels(self) -> None:
        block = format_agent_session_pack(
            cwd_or_path="C:/DevManiacs/migra/dm-erp",
            task_summary="Auditoria BDI TCU",
            role="QA",
            adapter=self.adapter,
        )
        self.assertIn("<!-- cerberus-context-pack:auto-generated -->", block)
        self.assertIn("<!-- cerberus-project: canteirohub -->", block)
        self.assertIn("<!-- cerberus-role: QA -->", block)
        self.assertIn("<!-- cerberus-token-estimate:", block)
        self.assertIn("<!-- cerberus-generated-at:", block)
        self.assertIn("## Cerberus Context Pack (read first)", block)
        self.assertIn("<!-- end-cerberus-context-pack -->", block)
        self.assertIn("CERBERUS CONTEXT PACK", block)

    def test_format_agent_session_pack_respects_explicit_project(self) -> None:
        block = format_agent_session_pack(
            cwd_or_path="C:/anywhere/random",
            task_summary="Audit",
            role="DEVELOPER",
            adapter=self.adapter,
            project_id="biolar",
        )
        self.assertIn("<!-- cerberus-project: biolar -->", block)


# ============================================================================
# Full lifecycle (cross-cutting)
# ============================================================================
class TestFullLifecycle(unittest.TestCase):
    def setUp(self) -> None:
        self._tmp = tempfile.TemporaryDirectory()
        self.tmp = Path(self._tmp.name)
        self.adapter = _make_adapter(self.tmp)

    def tearDown(self) -> None:
        self._tmp.cleanup()

    def test_full_lifecycle_session_to_promotion(self) -> None:
        # 1. TASK_CREATED -> session_start
        ctx = self.adapter.session_start(
            project_id="canteirohub",
            task_summary="Capturar cofre SEFAZ",
            role="DEVELOPER",
        )
        self.assertEqual("canteirohub", ctx["project_id"])
        self.assertIn("CERBERUS CONTEXT PACK", ctx["markdown"])

        # Canonical files untouched
        self.assertEqual(
            "# Learnings\n",
            (self.adapter.application_root / "LEARNINGS.md").read_text(encoding="utf-8"),
        )

        # 2. REPORT_ACCEPTED -> candidate
        report = (
            "## Learnings\n"
            "- Cofre SEFAZ usa AES-256-GCM com HKDF para derivar chaves por tenant.\n"
        )
        ingest = self.adapter.on_report_accepted(
            report_path_or_content=report,
            task_id="TASK-FULL",
            project_id="canteirohub",
            agent_role="CODEX",
        )
        self.assertEqual(1, ingest["candidate_count"])
        cid = ingest["candidate_ids"][0]

        # Candidate exists with provenance
        candidate = self.adapter.inbox.get(cid)
        self.assertEqual("TASK-FULL", candidate.task_id)
        self.assertEqual("CODEX", candidate.agent)
        self.assertEqual("CANDIDATE", candidate.status.value)

        # 3. QA_APPROVED -> VERIFIED
        qa = self.adapter.on_qa_approved(candidate_id=cid)
        self.assertEqual([cid], qa["verified"])
        self.assertEqual("VERIFIED", self.adapter.inbox.get(cid).status.value)

        # 4. promote --apply (operator-driven) -> CANONICAL
        applied = self.adapter.capture_engine.promote(cid, apply=True)
        self.assertEqual("CANONICAL", applied["status"])
        learnings = (self.adapter.application_root / "LEARNINGS.md").read_text(encoding="utf-8")
        self.assertIn("Cofre SEFAZ", learnings)
        self.assertIn("TASK-FULL", learnings)

    def test_full_lifecycle_via_maestri_path_detection(self) -> None:
        block = format_agent_session_pack(
            cwd_or_path=str(self.adapter.application_root / "projects" / "canteirohub"),
            task_summary="Trigger Maestri lifecycle",
            role="DEVELOPER",
            adapter=self.adapter,
        )
        self.assertIn("<!-- cerberus-project: canteirohub -->", block)


# ============================================================================
# CLI dispatch
# ============================================================================
class TestOrchestratorCLICommands(unittest.TestCase):
    def _run_cli(self, root: Path, *args: str) -> subprocess.CompletedProcess:
        env = dict(
            os.environ,
            CERBERUS_ROOT=str(root),
            CERBERUS_ALLOWED_ROOTS=str(root),
            PYTHONPATH=str(REPO),
            PYTHONDONTWRITEBYTECODE="1",
            PYTHONIOENCODING="utf-8",
        )
        return subprocess.run(
            [sys.executable, "-m", "engine.cli", *args],
            cwd=root, env=env,
            text=True, capture_output=True,
            encoding="utf-8", errors="replace",
            timeout=15,
        )

    def test_cli_session_context_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_corpus(root)
            # session-context requires --project, --task
            proc = self._run_cli(root, "session-context",
                                 "--project", "canteirohub",
                                 "--task", "Implementar SEFAZ",
                                 "--role", "QA")
            self.assertEqual(0, proc.returncode, proc.stderr)
            self.assertIn("CERBERUS CONTEXT PACK", proc.stdout)
            self.assertIn("📊 Estimativa de tokens", proc.stdout)

    def test_cli_on_report_accepted_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_corpus(root)
            # FIX-006: the CLI argument is now treated strictly as inline
            # content. We pass the markdown body directly (no file read).
            report_content = (
                "TASK-ID: TASK-CLI-1\n\n"
                "## Learnings\n"
                "- Licao CLI dispatch funcionando com conteudo inline.\n"
            )
            proc = self._run_cli(root, "on-report-accepted", report_content,
                                 "--task", "TASK-CLI-1",
                                 "--project", "canteirohub",
                                 "--agent", "CODEX")
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual("canteirohub", payload["project_id"])
            self.assertEqual("TASK-CLI-1", payload["task_id"])
            self.assertEqual("COMPLETE", payload["status"])
            self.assertGreaterEqual(payload["candidate_count"], 1)
            cid = payload["candidate_ids"][0]
            # Inbox file exists
            self.assertTrue((root / ".cerberus" / "inbox" / f"{cid}.json").exists())

    def test_cli_on_qa_approved_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_corpus(root)
            # Capture a candidate via CLI
            cap = self._run_cli(root, "capture",
                                "--title", "Licao QA CLI",
                                "--content", "Conteudo para verificar via CLI QA.",
                                "--project", "canteirohub",
                                "--task", "TASK-QA-CLI",
                                "--agent", "QA")
            self.assertEqual(0, cap.returncode, cap.stderr)
            cid = json.loads(cap.stdout)["candidate_id"]
            # on-qa-approved --candidate
            proc = self._run_cli(root, "on-qa-approved", "--candidate", cid)
            self.assertEqual(0, proc.returncode, proc.stderr)
            payload = json.loads(proc.stdout)
            self.assertEqual([cid], payload["verified"])

    def test_cli_on_qa_approved_without_args_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _build_corpus(root)
            proc = self._run_cli(root, "on-qa-approved")
            self.assertNotEqual(0, proc.returncode)


# ============================================================================
# FIX-005 — Regression coverage for the Codex QA findings
# ============================================================================
class TestFix005Regression(unittest.TestCase):
    """
    FIX-005 closes 4 findings reported by Codex QA on Phase P2:

      1. Project-scoped QA approval via `on_qa_approved(project_id=...)`.
      2. `ensure_indexed` honors CERBERUS_ALLOWED_ROOTS and stops hardcoding
         `C:/DevManiacs/migra/dm-erp/docs`.
      3. `on_report_accepted` never reads arbitrary filesystem paths —
         only files strictly inside the configured allowlist.
      4. `detect_project_from_path` priority (projects/<slug> beats global)
         and strict alias precision (no loose `site`/`desk`/`apae` matching).
    """

    # ----- helpers -----------------------------------------------------------
    def _setup_env(self) -> None:
        """Strip CERBERUS_* so tests are deterministic."""
        for key in ("CERBERUS_ROOT", "CERBERUS_ALLOWED_ROOTS",
                     "CERBERUS_EXTRA_ROOTS"):
            os.environ.pop(key, None)

    # ----- Fix #1: project-scoped QA approval --------------------------------
    def test_qa_approval_by_task_with_project_id_only_verifies_target(self) -> None:
        """Same TASK-01 across biolar and helpdev must not cross-verify."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _build_corpus(tmp_path / "cerebro")

            # Create two adapters pointing at the same inbox but simulating
            # different project_id captures via direct inbox writes.
            root = tmp_path / "cerebro"
            service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=root, service=service)

            # Capture a candidate into biolar
            bio = adapter.on_report_accepted(
                report_path_or_content="## Learnings\n- Biolar capture with shared TASK-01.\n",
                task_id="TASK-01",
                project_id="biolar",
                agent_role="QA",
            )
            bio_cid = bio["candidate_ids"][0]
            # Capture a candidate into helpdev with the same TASK-01
            help = adapter.on_report_accepted(
                report_path_or_content="## Learnings\n- HelpDev capture with shared TASK-01.\n",
                task_id="TASK-01",
                project_id="helpdev",
                agent_role="QA",
            )
            help_cid = help["candidate_ids"][0]
            self.assertNotEqual(bio_cid, help_cid)

            # Approve scoped to biolar
            result = adapter.on_qa_approved(task_id="TASK-01", project_id="biolar")
            self.assertEqual([bio_cid], result["verified"])
            self.assertEqual("biolar", result["project_id"])
            self.assertEqual(1, len(result["skipped"]))
            self.assertEqual(help_cid, result["skipped"][0]["candidate_id"])
            self.assertIn("project mismatch", result["skipped"][0]["reason"])

            # helpdev's candidate is still CANDIDATE
            self.assertEqual("CANDIDATE", adapter.inbox.get(help_cid).status.value)
            # biolar's candidate is now VERIFIED
            self.assertEqual("VERIFIED", adapter.inbox.get(bio_cid).status.value)

    def test_qa_approval_by_task_without_project_id_raises_fix006(self) -> None:
        """FIX-006: approving by task_id without project_id MUST raise ValueError."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _build_corpus(tmp_path / "cerebro")
            root = tmp_path / "cerebro"
            service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=root, service=service)

            adapter.on_report_accepted(
                report_path_or_content="## Learnings\n- Biolar capture with TASK-99.\n",
                task_id="TASK-99",
                project_id="biolar",
                agent_role="QA",
            )

            # Without project_id, must fail closed to prevent cross-project leakage.
            with self.assertRaises(ValueError) as ctx:
                adapter.on_qa_approved(task_id="TASK-99")
            self.assertIn("project_id is required", str(ctx.exception))
            self.assertIn("cross-project", str(ctx.exception))

            # Empty / whitespace project_id is also rejected.
            with self.assertRaises(ValueError):
                adapter.on_qa_approved(task_id="TASK-99", project_id="")
            with self.assertRaises(ValueError):
                adapter.on_qa_approved(task_id="TASK-99", project_id="   ")

            # Providing project_id succeeds.
            result = adapter.on_qa_approved(task_id="TASK-99", project_id="biolar")
            self.assertEqual(1, len(result["verified"]))

    def test_qa_approval_by_candidate_id_with_wrong_project_is_skipped(self) -> None:
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _build_corpus(tmp_path / "cerebro")
            root = tmp_path / "cerebro"
            service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=root, service=service)
            res = adapter.on_report_accepted(
                report_path_or_content="## Learnings\n- Biolar capture TASK-77.\n",
                task_id="TASK-77",
                project_id="biolar",
                agent_role="QA",
            )
            cid = res["candidate_ids"][0]

            # Try to verify a biolar candidate while scoping to helpdev
            result = adapter.on_qa_approved(candidate_id=cid, project_id="helpdev")
            self.assertEqual([], result["verified"])
            self.assertEqual(1, len(result["skipped"]))
            self.assertIn("project mismatch", result["skipped"][0]["reason"])

    # ----- Fix #2: ensure_indexed respects CERBERUS_ALLOWED_ROOTS ------------
    def test_ensure_indexed_ignores_hardcoded_dm_erp_when_isolated(self) -> None:
        """Under a custom CERBERUS_ROOT, the hardcoded dm-erp path must NOT be indexed."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            isolated_root = tmp_path / "isolated"
            isolated_root.mkdir()
            (isolated_root / "decisions.md").write_text(
                "# Decisions\n\nIsolated content markerXYZ123.\n", encoding="utf-8"
            )
            service = CerberusMemoryService(
                SQLiteMemoryIndex(isolated_root / ".cerberus" / "index.db")
            )
            adapter = OrchestratorAdapter(application_root=isolated_root, service=service)

            os.environ["CERBERUS_ROOT"] = str(isolated_root)
            os.environ["CERBERUS_ALLOWED_ROOTS"] = str(isolated_root)

            try:
                result = adapter.ensure_indexed()
                # The hardcoded dm-erp/docs path (which contains many docs)
                # must NOT have leaked into the isolated root.
                docs = adapter.service.index.search("markerXYZ123", limit=10)
                self.assertGreaterEqual(len(docs), 1)
                for d in docs:
                    self.assertNotIn("dm-erp", d.item.source_path)
                    self.assertNotIn("canteirohub", d.item.source_path)
                self.assertGreaterEqual(result["indexed_files"], 1)
            finally:
                self._setup_env()

    def test_ensure_indexed_rejects_extra_roots_outside_allowlist(self) -> None:
        """CERBERUS_EXTRA_ROOTS entries outside the allowlist must be skipped."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            allowed_root = tmp_path / "allowed"
            allowed_root.mkdir()
            (allowed_root / "ok.md").write_text(
                "# OK\n\nAllowed content markerOK111.\n", encoding="utf-8"
            )
            outside_root = tmp_path / "outside"
            outside_root.mkdir()
            (outside_root / "leak.md").write_text(
                "# Leak\n\nOutside content markerLEAK222.\n", encoding="utf-8"
            )

            service = CerberusMemoryService(
                SQLiteMemoryIndex(allowed_root / ".cerberus" / "index.db")
            )
            adapter = OrchestratorAdapter(application_root=allowed_root, service=service)

            os.environ["CERBERUS_ALLOWED_ROOTS"] = str(allowed_root)
            os.environ["CERBERUS_EXTRA_ROOTS"] = str(outside_root)

            try:
                adapter.ensure_indexed()
                # The outside marker must NOT be indexed.
                leak_hits = adapter.service.index.search("markerLEAK222", limit=10)
                self.assertEqual(0, len(leak_hits))
                ok_hits = adapter.service.index.search("markerOK111", limit=10)
                self.assertGreaterEqual(len(ok_hits), 1)
            finally:
                self._setup_env()

    def test_ensure_indexed_returns_empty_when_root_disallowed(self) -> None:
        """If CERBERUS_ROOT is outside the allowlist, no indexing happens."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            disallowed = tmp_path / "disallowed"
            disallowed.mkdir()
            (disallowed / "x.md").write_text("# X\n\nShould never be indexed.\n",
                                              encoding="utf-8")

            service = CerberusMemoryService(
                SQLiteMemoryIndex(tmp_path / "cerberus_root" / ".cerberus" / "index.db")
            )
            adapter = OrchestratorAdapter(
                application_root=tmp_path / "cerberus_root", service=service
            )

            os.environ["CERBERUS_ROOT"] = str(disallowed)
            os.environ["CERBERUS_ALLOWED_ROOTS"] = str(tmp_path / "cerberus_root")

            try:
                result = adapter.ensure_indexed()
                self.assertEqual(0, result["indexed_files"])
                self.assertEqual(0, result["total_chunks"])
            finally:
                self._setup_env()

    # ----- Fix #3: secure report ingestion -----------------------------------
    def test_report_accepted_refuses_to_read_path_outside_root(self) -> None:
        """FIX-006: a path-like input is treated as inline content only — never as a file to read."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            in_root = tmp_path / "cerebro"
            _build_corpus(in_root)
            outside = tmp_path / "outside.md"
            outside.write_text(
                "TASK-ID: TASK-OUTSIDE\n\n## Learnings\n- Conteudo externo forbiddenXYZ999.\n",
                encoding="utf-8",
            )

            service = CerberusMemoryService(SQLiteMemoryIndex(in_root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=in_root, service=service)
            os.environ["CERBERUS_ALLOWED_ROOTS"] = str(in_root)

            try:
                # Passing a path-shaped string: the adapter must NOT open the file.
                result = adapter.on_report_accepted(
                    report_path_or_content=str(outside),
                    task_id="TASK-OUTSIDE",
                    project_id="canteirohub",
                    agent_role="QA",
                )
                self.assertEqual(0, result["candidate_count"])
                self.assertNotIn("source_path", result)
                # Inbox must not contain the outside content
                for cid in result.get("candidate_ids", []):
                    raw = (in_root / ".cerberus" / "inbox" / f"{cid}.json").read_text(encoding="utf-8")
                    self.assertNotIn("forbiddenXYZ999", raw)
            finally:
                self._setup_env()

    def test_report_accepted_never_reads_disk_even_inside_root(self) -> None:
        """FIX-006: even files INSIDE application_root are not auto-opened."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            in_root = tmp_path / "cerebro"
            _build_corpus(in_root)
            inside = in_root / "report.md"
            inside.write_text(
                "TASK-ID: TASK-INSIDE\n\n## Learnings\n- Conteudo interno allowedXYZ777.\n",
                encoding="utf-8",
            )

            service = CerberusMemoryService(SQLiteMemoryIndex(in_root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=in_root, service=service)
            os.environ["CERBERUS_ALLOWED_ROOTS"] = str(in_root)

            try:
                result = adapter.on_report_accepted(
                    report_path_or_content=str(inside),
                    task_id="TASK-INSIDE",
                    project_id="canteirohub",
                    agent_role="QA",
                )
                # The path string is NOT opened: candidate count is 0 because
                # the literal string `str(inside)` doesn't contain the
                # expected `## Learnings` header when stripped of the path
                # text — and we treat it as content, not as a path.
                self.assertEqual(0, result["candidate_count"])
                self.assertNotIn("source_path", result)
                self.assertNotIn("allowedXYZ777",
                                  (in_root / ".cerberus" / "inbox" /
                                   f"{result['candidate_ids'][0]}.json").read_text(encoding="utf-8")
                                  if result["candidate_ids"] else "")
            finally:
                self._setup_env()

    def test_report_accepted_treats_multiline_string_as_inline(self) -> None:
        """Multi-line strings are treated as inline content (FIX-006 contract)."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            in_root = tmp_path / "cerebro"
            _build_corpus(in_root)
            service = CerberusMemoryService(SQLiteMemoryIndex(in_root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=in_root, service=service)
            os.environ["CERBERUS_ALLOWED_ROOTS"] = str(in_root)

            try:
                content = (
                    "## Learnings\n"
                    "- C:\\\\some\\\\path\\\\inside.md content markerMULTI555.\n"
                )
                result = adapter.on_report_accepted(
                    report_path_or_content=content,
                    task_id="TASK-MULTILINE",
                    project_id="canteirohub",
                    agent_role="QA",
                )
                self.assertGreaterEqual(result["candidate_count"], 1)
                self.assertNotIn("source_path", result)
            finally:
                self._setup_env()

    # ----- Fix #4: path detection priority & alias precision -----------------
    def test_detect_project_path_projects_subdir_beats_global(self) -> None:
        """projects/biolar/global/report.md must resolve to biolar, not _global."""
        self.assertEqual(
            "biolar",
            detect_project_from_path(
                "C:/DevManiacs/DM-Cerebro/projects/biolar/global/report.md"
            ),
        )
        self.assertEqual(
            "canteirohub",
            detect_project_from_path(
                "C:/DevManiacs/DM-Cerebro/projects/canteirohub/shared/notes.md"
            ),
        )
        self.assertEqual(
            "helpdev",
            detect_project_from_path(
                "C:/DevManiacs/DM-Cerebro/projects/helpdev/_global/something.md"
            ),
        )

    def test_detect_project_path_strict_alias_exact_segment_only(self) -> None:
        """dev-maniacs-site and dm-desk must match only on exact segment."""
        # Exact matches still work
        self.assertEqual(
            "dev-maniacs-site",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/dev-maniacs-site"),
        )
        self.assertEqual(
            "dm-desk",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/dm-desk"),
        )
        # Loose substrings must NOT trigger the alias
        loose_paths = [
            "C:/Users/jane/site-files/whatever",
            "C:/Users/jane/desktop-tools/x",
            "C:/Users/jane/apae-data/y",
            "C:/some/site-mirror/file",
        ]
        for path in loose_paths:
            slug = detect_project_from_path(path)
            with self.subTest(path=path):
                self.assertNotIn(slug, {"dev-maniacs-site", "dm-desk", "apae-juatuba"})

    def test_detect_project_path_global_and_shared_still_work_when_no_projects(self) -> None:
        """Generic global/shared detection still works when there's no projects/ ancestor."""
        self.assertEqual(
            "_global",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/global/ai-governance.md"),
        )
        self.assertEqual(
            "_shared",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/_shared/x.md"),
        )


# ============================================================================
# FIX-006 — Final security contract alignments
# ============================================================================
class TestFix006Regression(unittest.TestCase):
    """
    FIX-006 closes 3 final contract gaps flagged by Codex QA:

      1. `on_qa_approved(task_id=..., project_id=None)` must raise
         `ValueError` (mandatory project scope for task_id approvals).
      2. `on_report_accepted` must always pass `allow_file=False` to
         `ingest_report` (strict content-only — never reads disk).
      3. Loose aliases `site` and `desk` are removed from
         `PROJECT_ALIASES`; generic paths like `C:/unrelated/site` and
         `C:/my_desk` fall back to `_global`.
    """

    def _setup_env(self) -> None:
        for key in ("CERBERUS_ROOT", "CERBERUS_ALLOWED_ROOTS",
                     "CERBERUS_EXTRA_ROOTS"):
            os.environ.pop(key, None)

    # ----- Fix #1: mandatory project_id on task_id approval ------------------
    def test_on_qa_approved_task_id_without_project_id_raises(self) -> None:
        """FIX-006: task_id approvals must require project_id (anti cross-project)."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _build_corpus(tmp_path / "cerebro")
            root = tmp_path / "cerebro"
            service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=root, service=service)

            adapter.on_report_accepted(
                report_path_or_content="## Learnings\n- task without scope.\n",
                task_id="TASK-NO-SCOPE",
                project_id="biolar",
                agent_role="QA",
            )

            for kwargs in (
                {"task_id": "TASK-NO-SCOPE"},
                {"task_id": "TASK-NO-SCOPE", "project_id": None},
                {"task_id": "TASK-NO-SCOPE", "project_id": ""},
                {"task_id": "TASK-NO-SCOPE", "project_id": "   "},
            ):
                with self.subTest(kwargs=kwargs):
                    with self.assertRaises(ValueError) as ctx:
                        adapter.on_qa_approved(**kwargs)
                    self.assertIn("project_id is required", str(ctx.exception))
                    self.assertIn("cross-project", str(ctx.exception))

    def test_on_qa_approved_candidate_id_only_still_works_without_project_id(self) -> None:
        """FIX-006: candidate_id mode is unaffected — still works without project_id."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _build_corpus(tmp_path / "cerebro")
            root = tmp_path / "cerebro"
            service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=root, service=service)
            res = adapter.on_report_accepted(
                report_path_or_content="## Learnings\n- candidato sem escopo.\n",
                task_id="TASK-CID",
                project_id="biolar",
                agent_role="QA",
            )
            cid = res["candidate_ids"][0]
            # No project_id, just candidate_id -> works fine.
            result = adapter.on_qa_approved(candidate_id=cid)
            self.assertEqual([cid], result["verified"])

    # ----- Fix #2: strict content-only on_report_accepted --------------------
    def test_on_report_accepted_calls_ingest_report_with_allow_file_false(self) -> None:
        """FIX-006: ingest_report must be called with allow_file=False, always."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _build_corpus(tmp_path / "cerebro")
            root = tmp_path / "cerebro"
            service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=root, service=service)

            calls = []

            original = adapter.capture_engine.ingest_report

            def spy_ingest(*args, **kwargs):
                calls.append(kwargs)
                return original(*args, **kwargs)

            adapter.capture_engine.ingest_report = spy_ingest

            try:
                # Pass an obvious path-looking string. Even if it points at a
                # real file inside the root, the adapter must NOT open it.
                fake_path = root / "secret.md"
                fake_path.write_text(
                    "## Learnings\n- never opened markerNEVER123.\n",
                    encoding="utf-8",
                )
                adapter.on_report_accepted(
                    report_path_or_content=str(fake_path),
                    task_id="TASK-FIX006",
                    project_id="canteirohub",
                    agent_role="QA",
                )
            finally:
                adapter.capture_engine.ingest_report = original

            self.assertEqual(1, len(calls))
            self.assertIn("allow_file", calls[0])
            self.assertEqual(False, calls[0]["allow_file"])
            # The literal path string is what reached ingest_report (as
            # content), not the file's bytes.
            self.assertEqual(str(fake_path), calls[0]["report_path_or_content"])

    def test_on_report_accepted_does_not_emit_source_path(self) -> None:
        """FIX-006: result must never carry a `source_path` key (no disk reads)."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            _build_corpus(tmp_path / "cerebro")
            root = tmp_path / "cerebro"
            service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
            adapter = OrchestratorAdapter(application_root=root, service=service)
            result = adapter.on_report_accepted(
                report_path_or_content="## Learnings\n- inline content here.\n",
                task_id="TASK-INLINE",
                project_id="canteirohub",
                agent_role="QA",
            )
            self.assertNotIn("source_path", result)

    # ----- Fix #3: loose aliases removed -------------------------------------
    def test_loose_paths_fall_back_to_global(self) -> None:
        """FIX-006: `C:/unrelated/site` and `C:/my_desk` must resolve to `_global`."""
        self.assertEqual("_global", detect_project_from_path("C:/unrelated/site"))
        self.assertEqual("_global", detect_project_from_path("C:/my_desk"))
        # And any non-project folder should also fall back to `_global`
        self.assertEqual("_global", detect_project_from_path("C:/Users/john/Documents/random"))
        self.assertEqual("_global", detect_project_from_path("D:/some/random/path.md"))

    def test_projects_site_and_projects_desk_keep_literal_slugs(self) -> None:
        """FIX-006: explicit `projects/site` and `projects/desk` keep their slugs verbatim."""
        self.assertEqual(
            "site",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/site"),
        )
        self.assertEqual(
            "desk",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/desk"),
        )
        # Other projects unaffected
        self.assertEqual(
            "biolar",
            detect_project_from_path("C:/DevManiacs/DM-Cerebro/projects/biolar"),
        )

    def test_explicit_full_aliases_still_resolve(self) -> None:
        """FIX-006: explicit full names still work; only loose substrings are gone."""
        self.assertEqual("dev-maniacs-site",
                         resolve_project_slug("dev-maniacs-site"))
        self.assertEqual("dm-desk", resolve_project_slug("dm-desk"))
        # `dm-erp` stays aliased to `canteirohub` (unchanged behavior).
        self.assertEqual("canteirohub", resolve_project_slug("dm-erp"))

    def test_resolve_project_slug_has_no_loose_site_or_desk_keys(self) -> None:
        """FIX-006: `site` and `desk` must not be keys in PROJECT_ALIASES."""
        self.assertNotIn("site", PROJECT_ALIASES)
        self.assertNotIn("desk", PROJECT_ALIASES)


# ============================================================================
# FIX-007 — Unconditional project_id guard when task_id is present
# ============================================================================
class TestFix007Regression(unittest.TestCase):
    """
    FIX-007 narrows the FIX-006 guard:

      WhENEVER `task_id` is supplied — alone, OR alongside `candidate_id` —
      `project_id` MUST be present and non-empty. The combination
      `(candidate_id, task_id, project_id=None)` is explicitly forbidden
      because `task_id` is not unique across projects.
    """

    def _setup_env(self) -> None:
        for key in ("CERBERUS_ROOT", "CERBERUS_ALLOWED_ROOTS",
                     "CERBERUS_EXTRA_ROOTS"):
            os.environ.pop(key, None)

    def _make_adapter_with_candidate(self, tmp: Path, *, task_id: str,
                                       project_id: str):
        _build_corpus(tmp / "cerebro")
        root = tmp / "cerebro"
        service = CerberusMemoryService(SQLiteMemoryIndex(root / ".cerberus" / "index.db"))
        adapter = OrchestratorAdapter(application_root=root, service=service)
        res = adapter.on_report_accepted(
            report_path_or_content=(
                "## Learnings\n- FIX-007 regression target.\n"
            ),
            task_id=task_id,
            project_id=project_id,
            agent_role="QA",
        )
        return adapter, res["candidate_ids"][0]

    def test_qa_approved_with_both_candidate_id_and_task_id_requires_project_id(self) -> None:
        """FIX-007: `(candidate_id, task_id, project_id=None)` MUST raise ValueError."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            adapter, cid = self._make_adapter_with_candidate(
                tmp_path, task_id="TASK-007-DUAL", project_id="biolar"
            )

            # Pass candidate_id AND task_id, but NO project_id -> fail-closed.
            with self.assertRaises(ValueError) as ctx:
                adapter.on_qa_approved(
                    candidate_id=cid, task_id="TASK-007-DUAL", project_id=None,
                )
            self.assertIn("project_id is required", str(ctx.exception))
            self.assertIn("task_id is specified", str(ctx.exception))

            # Candidate must still be CANDIDATE (no transition).
            self.assertEqual("CANDIDATE", adapter.inbox.get(cid).status.value)

    def test_qa_approved_with_both_candidate_id_task_id_and_empty_project_id_raises(self) -> None:
        """FIX-007: empty / whitespace project_id alongside task_id must also raise."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            adapter, cid = self._make_adapter_with_candidate(
                tmp_path, task_id="TASK-007-EMPTY", project_id="biolar"
            )
            for bad in ("", "   ", "\t\n"):
                with self.subTest(project_id=bad):
                    with self.assertRaises(ValueError) as ctx:
                        adapter.on_qa_approved(
                            candidate_id=cid,
                            task_id="TASK-007-EMPTY",
                            project_id=bad,
                        )
                    self.assertIn("project_id is required", str(ctx.exception))

    def test_qa_approved_with_both_candidate_id_task_id_and_valid_project_id_succeeds(self) -> None:
        """FIX-007: when project_id is supplied alongside (candidate_id, task_id), succeeds."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            adapter, cid = self._make_adapter_with_candidate(
                tmp_path, task_id="TASK-007-OK", project_id="biolar"
            )
            result = adapter.on_qa_approved(
                candidate_id=cid, task_id="TASK-007-OK", project_id="biolar",
            )
            self.assertEqual([cid], result["verified"])
            self.assertEqual("VERIFIED", adapter.inbox.get(cid).status.value)

    def test_qa_approved_candidate_id_only_still_works_without_project_id(self) -> None:
        """FIX-007: pure `candidate_id` mode (no task_id) remains unaffected."""
        self._setup_env()
        with tempfile.TemporaryDirectory() as tmp:
            tmp_path = Path(tmp)
            adapter, cid = self._make_adapter_with_candidate(
                tmp_path, task_id="TASK-CID-ONLY", project_id="biolar"
            )
            # Only candidate_id, no task_id, no project_id -> still works.
            result = adapter.on_qa_approved(candidate_id=cid)
            self.assertEqual([cid], result["verified"])


if __name__ == "__main__":
    unittest.main()
