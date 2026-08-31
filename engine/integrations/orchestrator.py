"""
Cerberus Memory Intelligence - Orchestrator Lifecycle Adapter
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Phase P2: bridges the Cerberus memory engine into the AI Orchestrator /
Gemini Maestro event flow:

  TASK_CREATED       -> session_start()
  REPORT_ACCEPTED    -> on_report_accepted()
  QA_APPROVED        -> on_qa_approved()
  PROJECT_CLOSED     -> get_project_summary()

The adapter never writes directly to canonical Markdown; it always lands
in `.cerberus/inbox/` and requires an explicit operator-driven promote
to cross into the canonic layer.
"""

from __future__ import annotations

import datetime as dt
import os
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.capture import AutoCaptureEngine, CandidateStore
from engine.index import SQLiteMemoryIndex, normalize_roots, validate_root
from engine.retrieval import CerberusMemoryService


PROJECT_ALIASES = {
    "_global": "_global",
    "_shared": "_shared",
    "global": "_global",
    "shared": "_shared",
    "canteirohub": "canteirohub",
    "dm-erp": "canteirohub",
    "dm_erp": "canteirohub",
    "biolar": "biolar",
    "helpdev": "helpdev",
    "dmpdv": "dmpdv",
    "apae-juatuba": "apae-juatuba",
    "apae_juatuba": "apae-juatuba",
    "apae": "apae-juatuba",
    "dev-maniacs-site": "dev-maniacs-site",
    "dev_maniacs_site": "dev-maniacs-site",
    "dm-desk": "dm-desk",
    "dm_desk": "dm-desk",
    # NOTE (FIX-006): The loose short aliases `site -> dev-maniacs-site`
    # and `desk -> dm-desk` were deliberately removed. Generic paths like
    # `C:/unrelated/site` or `C:/my_desk` must now fall back to the
    # closest folder / `_global`. To address a project literally named
    # `site` or `desk`, place it under `projects/site` or `projects/desk`
    # (the `projects/<slug>` rule already accepts arbitrary slugs verbatim).
}


# Strict alias set used by path detection (engine/integrations/maestri.py).
# Only full segment names that uniquely identify a known project. Loose
# substrings (e.g. `site`, `desk`, `apae`) are deliberately excluded so that
# an unrelated folder like `C:/Users/jane/site-files/...` is not silently
# classified as `dev-maniacs-site`.
STRICT_PATH_ALIASES = {
    "dm-erp": "canteirohub",
    "dm_erp": "canteirohub",
    "dev-maniacs-site": "dev-maniacs-site",
    "dev_maniacs_site": "dev-maniacs-site",
    "dm-desk": "dm-desk",
    "dm_desk": "dm-desk",
    "apae-juatuba": "apae-juatuba",
    "apae_juatuba": "apae-juatuba",
    "biolar": "biolar",
    "helpdev": "helpdev",
    "dmpdv": "dmpdv",
    "canteirohub": "canteirohub",
}


def _application_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _candidate_root(application_root: Path) -> Path:
    return application_root / ".cerberus" / "inbox"


def _resolve_root_or_default(application_root: Path) -> Path:
    configured = os.environ.get("CERBERUS_ROOT")
    if configured:
        allowed = os.environ.get("CERBERUS_ALLOWED_ROOTS")
        allowed_roots = (
            [Path(value) for value in allowed.split(os.pathsep) if value]
            if allowed
            else [application_root]
        )
        return validate_root(Path(configured), allowed_roots)
    return application_root


def _configured_allowed_roots(application_root: Path) -> List[Path]:
    """
    Parse CERBERUS_ALLOWED_ROOTS honoring the env override; fall back to
    `application_root` (the canonical self-root) so any custom environment
    stays inside the trusted boundary.
    """
    raw = os.environ.get("CERBERUS_ALLOWED_ROOTS")
    if raw:
        parsed = [Path(value).resolve() for value in raw.split(os.pathsep) if value]
        if parsed:
            return parsed
    return [application_root.resolve()]


def _select_index_roots(application_root: Path) -> List[Path]:
    """
    Build the list of roots to feed `SQLiteMemoryIndex.index_roots()`.

    Precedence:

    1. If `CERBERUS_ROOT` is set, **only** that root is eligible — no
       hardcoded fallback to external directories like
       `C:/DevManiacs/migra/dm-erp/docs`.
    2. If `CERBERUS_ROOT` is NOT set, include the canonical `application_root`
       only. Optional `CERBERUS_EXTRA_ROOTS` may list additional allowed
       directories (validated against `CERBERUS_ALLOWED_ROOTS`).
    3. Every candidate root must both (a) exist and (b) live inside the
       resolved allowlist. Anything else is dropped silently.
    """
    allowed = _configured_allowed_roots(application_root)
    candidates: List[Path] = []

    configured = os.environ.get("CERBERUS_ROOT")
    if configured:
        try:
            candidates.append(validate_root(Path(configured), allowed))
        except ValueError:
            return []
    else:
        candidates.append(application_root)
        extra_raw = os.environ.get("CERBERUS_EXTRA_ROOTS")
        if extra_raw:
            for value in extra_raw.split(os.pathsep):
                if not value:
                    continue
                try:
                    candidates.append(validate_root(Path(value), allowed))
                except ValueError:
                    continue

    seen: List[Path] = []
    for root in candidates:
        try:
            resolved = root.resolve(strict=True)
        except (OSError, FileNotFoundError):
            continue
        if not resolved.exists():
            continue
        if not any(resolved == boundary or boundary in resolved.parents
                    for boundary in allowed):
            continue
        if resolved not in seen:
            seen.append(resolved)
    return seen


def resolve_project_slug(value: Optional[str]) -> str:
    """
    Normalize a free-form project identifier to a canonical slug.

    Recognizes aliases (e.g. `dm-erp` -> `canteirohub`) and falls back to
    a slugified version of the input. `_global` and `_shared` are passed
    through verbatim.
    """
    if value is None:
        return "_global"
    candidate = value.strip()
    if not candidate:
        return "_global"
    folded = candidate.casefold()
    if folded in PROJECT_ALIASES:
        return PROJECT_ALIASES[folded]
    slug = candidate.casefold().replace(" ", "-").replace("/", "-").replace("\\", "-")
    slug = "-".join(part for part in slug.split("-") if part)
    return slug or "_global"


def list_indexed_project_slugs(service: CerberusMemoryService) -> List[str]:
    stats = service.index.get_stats()
    seen: List[str] = []
    for pid in stats.get("indexed_projects", []):
        if pid and pid not in seen:
            seen.append(pid)
    if not seen:
        seen.append("_global")
    return seen


def discover_dynamic_projects(application_root: Path) -> List[str]:
    projects_dir = application_root / "projects"
    if not projects_dir.exists():
        return []
    discovered: List[str] = []
    for child in sorted(projects_dir.iterdir()):
        if not child.is_dir() or child.name.startswith("."):
            continue
        discovered.append(child.name)
    return discovered


def all_known_project_slugs(application_root: Path,
                             service: Optional[CerberusMemoryService] = None) -> List[str]:
    base = {"_global", "_shared"}
    base.update(PROJECT_ALIASES.values())
    base.update(discover_dynamic_projects(application_root))
    if service is not None:
        try:
            base.update(list_indexed_project_slugs(service))
        except Exception:
            pass
    ordered = sorted(base)
    if "_global" in ordered:
        ordered.remove("_global")
        ordered.insert(0, "_global")
    if "_shared" in ordered:
        ordered.remove("_shared")
        ordered.insert(1, "_shared")
    return ordered


class OrchestratorAdapter:
    """
    High-level bridge that the AI Orchestrator calls whenever a lifecycle
    event fires. It composes the existing Cerberus services (memory,
    capture, retrieval) and never bypasses the inbox gate.
    """

    def __init__(self, application_root: Optional[Path] = None,
                 service: Optional[CerberusMemoryService] = None,
                 capture_engine: Optional[AutoCaptureEngine] = None) -> None:
        self.application_root = Path(application_root or _application_root()).resolve()
        self.service = service or CerberusMemoryService(
            SQLiteMemoryIndex(self._canonical_index_path())
        )
        self.capture_engine = capture_engine or AutoCaptureEngine(
            service=self.service, cerebro_root=self.application_root
        )
        self.inbox: CandidateStore = self.capture_engine.store

    def _canonical_index_path(self) -> Path:
        return self.application_root / ".cerberus" / "index.db"

    def ensure_indexed(self) -> Dict[str, Any]:
        roots = _select_index_roots(self.application_root)
        if not roots:
            return {"indexed_files": 0, "skipped_files": 0,
                    "total_chunks": 0, "errors": 0, "roots": []}
        return self.service.index.index_roots(roots)

    # ------------------------------------------------------------------
    # TASK_CREATED
    # ------------------------------------------------------------------
    def session_start(self, project_id: str, task_summary: str,
                      role: str = "DEVELOPER") -> Dict[str, Any]:
        slug = resolve_project_slug(project_id)
        self.ensure_indexed()
        pack = self.service.build_context_pack(
            project_id=slug, task_summary=task_summary, role=role
        )
        return {
            "project_id": slug,
            "task_summary": task_summary,
            "role": role,
            "markdown": pack.to_markdown(),
            "token_estimate": pack.token_estimate,
            "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        }

    # ------------------------------------------------------------------
    # REPORT_ACCEPTED
    # ------------------------------------------------------------------
    def on_report_accepted(self, report_path_or_content: str,
                            task_id: Optional[str], project_id: str,
                            agent_role: str = "REPORT_INGESTER") -> Dict[str, Any]:
        """
        Strictly content-only ingestion.

        `report_path_or_content` is treated as a literal markdown string
        regardless of whether it looks like a filesystem path. The adapter
        never opens files from disk — the underlying
        `AutoCaptureEngine.ingest_report()` is invoked with `allow_file=False`
        so that callers (CLI, MCP, Orchestrator) cannot trick the engine into
        reading arbitrary paths by passing a path-shaped string.
        """
        slug = resolve_project_slug(project_id)
        normalized_task = (task_id or "").strip() or None
        content = "" if report_path_or_content is None else str(report_path_or_content)

        # If task_id wasn't supplied, try to extract it from the report body
        # so the result reflects the canonical id used for candidate provenance.
        if not normalized_task:
            match = re.search(r"(?im)^\s*TASK(?:-ID)?\s*:\s*([^\s]+)", content)
            if match:
                normalized_task = match.group(1)

        # SECURITY CONTRACT (FIX-006):
        # `allow_file` is **always** False. The Orchestrator adapter never
        # touches the filesystem to read reports — the caller is responsible
        # for reading any file and passing the contents inline.
        result = self.capture_engine.ingest_report(
            report_path_or_content=content,
            task_id=normalized_task,
            project_id=slug,
            agent_role=agent_role,
            allow_file=False,
        )
        result["project_id"] = slug
        result["task_id"] = normalized_task or ""
        result["agent_role"] = agent_role
        return result

    # ------------------------------------------------------------------
    # QA_APPROVED
    # ------------------------------------------------------------------
    def on_qa_approved(self, candidate_id: Optional[str] = None,
                        task_id: Optional[str] = None,
                        project_id: Optional[str] = None) -> Dict[str, Any]:
        if not candidate_id and not task_id:
            raise ValueError("candidate_id or task_id is required")
        # WhENEVER `task_id` is supplied (alone, OR alongside `candidate_id`),
        # `project_id` is mandatory. The combination
        # `(candidate_id, task_id, project_id=None)` is explicitly forbidden
        # because `task_id` is not unique across projects — the caller could
        # inadvertently mass-verify a TASK-XX that exists in biolar, helpdev
        # etc. Failing-closed here is non-negotiable (FIX-007).
        if task_id and not (project_id and str(project_id).strip()):
            raise ValueError(
                "project_id is required whenever task_id is specified to "
                "prevent cross-project verification"
            )
        verified: List[str] = []
        skipped: List[str] = []
        target_slug: Optional[str] = None
        if project_id:
            target_slug = resolve_project_slug(project_id)
        if candidate_id:
            try:
                self._verify_within_project(candidate_id, target_slug)
                res = self.capture_engine.verify(candidate_id)
                verified.append(res["candidate_id"])
            except ValueError as exc:
                skipped.append({"candidate_id": candidate_id, "reason": str(exc)})
        if task_id:
            for candidate in list(self.inbox.list()):
                if candidate.task_id != task_id:
                    continue
                if target_slug and candidate.project_id != target_slug:
                    # Same task_id in a different project — skip explicitly.
                    skipped.append({"candidate_id": candidate.candidate_id,
                                     "reason": f"project mismatch (expected {target_slug})"})
                    continue
                if candidate.candidate_id in verified:
                    continue
                try:
                    res = self.capture_engine.verify(candidate.candidate_id)
                    verified.append(res["candidate_id"])
                except ValueError as exc:
                    skipped.append({"candidate_id": candidate.candidate_id,
                                     "reason": str(exc)})
        return {
            "verified": verified,
            "skipped": skipped,
            "mode": "candidate_id" if candidate_id else "task_id",
            "project_id": target_slug,
        }

    def _verify_within_project(self, candidate_id: str,
                                target_slug: Optional[str]) -> None:
        """Raise if a single-id verification falls outside the target project."""
        if not target_slug:
            return
        try:
            candidate = self.inbox.get(candidate_id)
        except ValueError as exc:
            raise ValueError(str(exc)) from exc
        if candidate.project_id != target_slug:
            raise ValueError(
                f"project mismatch (expected {target_slug}, "
                f"got {candidate.project_id})"
            )

    # ------------------------------------------------------------------
    # PROJECT_CLOSED
    # ------------------------------------------------------------------
    def get_project_summary(self, project_id: str) -> Dict[str, Any]:
        slug = resolve_project_slug(project_id)
        self.ensure_indexed()
        decisions = self.service.get_decisions(project_id=slug, limit=5)
        learnings = self.service.get_learnings(project_id=slug, limit=5)
        handoff = self.service.get_recent_handoff(project_id=slug)
        stats = self.service.index.get_stats()
        inbox_count = len(self.inbox.list()) if self.inbox.inbox_dir.exists() else 0
        return {
            "project_id": slug,
            "stats": stats,
            "decisions": [r.to_dict() for r in decisions],
            "learnings": [r.to_dict() for r in learnings],
            "recent_handoff": [r.to_dict() for r in handoff],
            "candidate_inbox_count": inbox_count,
        }


# Re-export detect_project_from_path so orchestrator callers can resolve
# paths without importing the maestri module separately.
def detect_project_from_path(path_like: str) -> str:
    from engine.integrations.maestri import detect_project_from_path as _impl
    return _impl(path_like)
