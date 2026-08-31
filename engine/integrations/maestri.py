"""
Cerberus Memory Intelligence - Maestri Canvas Helper
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Phase P2: lightweight helpers that the Maestri canvas / connected agent
terminals invoke when an agent opens a project, so the agent boots with
the right context without manual setup.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import Optional

from engine.integrations.orchestrator import (
    OrchestratorAdapter,
    resolve_project_slug,
)


def _normalize_path(cwd_or_path: str) -> Path:
    return Path(os.path.expandvars(os.path.expanduser(str(cwd_or_path)))).resolve()


def detect_project_from_path(cwd_or_path: str) -> str:
    """
    Resolve a project slug from a filesystem path.

    Recognition order (highest priority first):

    1. `projects/<slug>/...` ancestor        -> `<slug>`
       (Specific project wins over generic `_global` / `_shared`.)
    2. `_global` or `global` ancestor        -> `_global`
    3. `_shared` or `shared` ancestor        -> `_shared`
    4. Exact-segment match against
       `STRICT_PATH_ALIASES` (closest ancestor wins).
       Loose substrings like `site`, `desk`, `apae` are intentionally
       excluded — see FIX-006.
    5. Nothing matched                       -> `_global`

    Generic paths that don't match any of the above (e.g.
    `C:/unrelated/site` or `C:/my_desk`) deliberately fall back to
    `_global` rather than guessing the closest folder name. This avoids
    silently mis-classifying unrelated trees that happen to share a
    folder name with a known project.
    """
    raw = str(cwd_or_path or "").strip()
    if not raw:
        return "_global"

    try:
        path = _normalize_path(raw)
    except OSError:
        return resolve_project_slug(raw)

    parts = list(path.parts)
    parts_lower = [part.casefold() for part in parts]

    # 1. projects/<slug>/... (must beat generic global/shared)
    if "projects" in parts_lower:
        idx = parts_lower.index("projects")
        if idx + 1 < len(parts_lower):
            return resolve_project_slug(parts_lower[idx + 1])

    # 2. global
    if "_global" in parts_lower or "global" in parts_lower:
        return "_global"

    # 3. shared
    if "_shared" in parts_lower or "shared" in parts_lower:
        return "_shared"

    # 4. strict alias match (full-segment only, closest ancestor wins)
    from engine.integrations.orchestrator import STRICT_PATH_ALIASES
    for ancestor in reversed(parts):
        slug = STRICT_PATH_ALIASES.get(ancestor.casefold())
        if slug and slug not in {"_global", "_shared"}:
            return slug

    # 5. nothing matched → _global (FIX-006: never guess from folder name)
    return "_global"


def format_agent_session_pack(cwd_or_path: str, task_summary: str,
                                role: str = "DEVELOPER",
                                adapter: Optional[OrchestratorAdapter] = None,
                                project_id: Optional[str] = None) -> str:
    """
    Build a prompt-ready markdown block the agent can prepend to its
    session. Resolves the project slug from the path, then calls
    `OrchestratorAdapter.session_start()` and prefixes the block with
    explicit provenance so downstream agents know it came from Cerberus.
    """
    slug = project_id or detect_project_from_path(cwd_or_path)
    orchestrator = adapter or OrchestratorAdapter()
    pack = orchestrator.session_start(
        project_id=slug, task_summary=task_summary, role=role
    )
    header = [
        "<!-- cerberus-context-pack:auto-generated -->",
        f"<!-- cerberus-project: {pack['project_id']} -->",
        f"<!-- cerberus-role: {pack['role']} -->",
        f"<!-- cerberus-token-estimate: {pack['token_estimate']} -->",
        f"<!-- cerberus-generated-at: {pack['generated_at']} -->",
        "",
        "## Cerberus Context Pack (read first)",
        "",
        pack["markdown"],
        "",
        "<!-- end-cerberus-context-pack -->",
        "",
    ]
    return "\n".join(header)
