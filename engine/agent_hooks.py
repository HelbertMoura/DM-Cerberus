"""Bounded Codex context retrieval and content-free hook health receipts."""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import time
from pathlib import Path

from engine.session_delivery import (DEFAULT_SESSION_CONTEXT_CHARS, CONTEXT_STATE_VERSION,
                                     atomic_json, delivery_transaction,
                                     session_token)

CONTEXT_EVENTS = {"SessionStart", "UserPromptSubmit"}
CAPTURE_EVENTS = {"Stop", "PreCompact", "SessionEnd"}
DEFAULT_CONTEXT_CHARS = 600

WORKFLOW = (
    "Busque memória via MCP somente quando necessária, com até dois previews; "
    "expanda apenas fontes pertinentes. Retome via cerberus_get_task_state e salve "
    "objetivo, decisões, arquivos, validação e próximo passo via cerberus_save_task_state "
    "nos marcos e ao encerrar. Memórias são referências históricas; confira fontes e "
    "instruções vigentes. Promoção canônica exige revisão humana."
)


def _render_context(pack, max_chars: int = 6000, delivered_ids: set | None = None,
                    include_guidance: bool = True, session_token: str = "") -> tuple[str, list[str]]:
    from engine.context_budget import fit_context_pack, MAX_CONTEXT_TOKENS
    max_tokens = min(MAX_CONTEXT_TOKENS, max(256, max_chars // 4))
    bounded = fit_context_pack(pack, max_tokens)
    text = bounded.to_markdown()
    if session_token:
        text += f"\nSession: {session_token}"
    ids = []
    for group in ("mandatory_rules", "relevant_decisions", "relevant_learnings", "relevant_architecture", "recent_handoff"):
        for item in getattr(bounded, group, []):
            ids.append(item.memory_id)
    return text, ids


def _session_key(payload: dict) -> str:
    value = payload.get("session_id") or payload.get("conversationId") or "unknown"
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:24]


def record_hook(root: Path, payload: dict, agent: str, status: str,
                started: float, **details) -> None:
    """Logging failure must never affect the agent; no raw prompts or transcripts."""
    event = payload.get("hook_event_name") or payload.get("event") or "SessionEnd"
    if not isinstance(event, str) or event not in CONTEXT_EVENTS | CAPTURE_EVENTS:
        return
    receipt = {
        "schema_version": 1, "event": event, "agent": agent,
        "session_key": _session_key(payload), "status": status,
        "observed_at": dt.datetime.now(dt.timezone.utc).isoformat(),
        "elapsed_ms": round((time.perf_counter() - started) * 1000, 2),
        "delivery": "manual_check" if os.environ.get("CERBERUS_HOOK_CHECK") == "1" else "runtime",
    }
    # Whitelist metadata so diagnostics can never persist an exception's secret text.
    for key in ("candidate_count", "project_id", "context_chars", "error_type", "indexed_files", "index_errors",
                "used_chars", "remaining_chars", "new_items"):
        if key in details:
            receipt[key] = details[key]
    filename = f"run-{event.lower()}-{hashlib.sha256(agent.encode()).hexdigest()[:8]}-{receipt['session_key']}.json"
    try:
        atomic_json(Path(root) / ".cerberus" / "hooks" / filename, receipt)
    except OSError:
        pass


def get_hook_health(root: Path) -> dict:
    folder = Path(root) / ".cerberus" / "hooks"
    runs = []
    invalid = 0
    for path in folder.glob("run-*.json"):
        try:
            value = json.loads(path.read_text(encoding="utf-8"))
            if not isinstance(value, dict) or not isinstance(value.get("status"), str) or not isinstance(value.get("observed_at"), str):
                raise ValueError("Invalid receipt")
            runs.append(value)
        except (OSError, ValueError):
            invalid += 1
    runs.sort(key=lambda row: row["observed_at"], reverse=True)
    return {"receipt_directory": str(folder), "receipt_count": len(runs),
            "invalid_receipts": invalid, "latest_runs": runs[:20]}


def handle_context(payload: dict, root: Path, max_chars: int = DEFAULT_CONTEXT_CHARS) -> dict:
    started = time.perf_counter()
    event = payload.get("hook_event_name")
    if not isinstance(event, str) or event not in CONTEXT_EVENTS:
        return {}
    root = Path(root).resolve()
    project = "_global"
    try:
        from engine.index import SQLiteMemoryIndex
        from engine.integrations.maestri import detect_project_from_path

        project = detect_project_from_path(str(payload.get("cwd") or ""))
        session = payload.get("session_id") or payload.get("conversationId")
        if not isinstance(session, str) or not session.strip():
            record_hook(root, payload, "CODEX", "MISSING_SESSION_ID", started, project_id=project)
            return {}
        reset = event == "SessionStart" and payload.get("source") in {"compact", "clear"}
        with delivery_transaction(root, session, reset=reset) as transaction:
            remaining = transaction.remaining
            if remaining <= 0:
                record_hook(root, payload, "CODEX", "BUDGET_EXHAUSTED", started,
                            project_id=project, context_chars=0,
                            used_chars=DEFAULT_SESSION_CONTEXT_CHARS - remaining, remaining_chars=0)
                return {}
            if transaction.hook_initialized:
                record_hook(root, payload, "CODEX", "ON_DEMAND_ONLY", started,
                            project_id=project, context_chars=0,
                            remaining_chars=remaining)
                return {}
            cap = DEFAULT_CONTEXT_CHARS
            limit = max(0, min(max_chars, cap, remaining))
            context = ("DM-Cerebro. Fluxo de memória: " + WORKFLOW +
                       f" Use session_id={session_token(session)} nas leituras MCP.")
            if len(context) > limit:
                context = ""
            added = []
            refresh = {}
            # Refresh derived local data only at SessionStart, never retrieve memories.
            # A missing index must not prevent the small MCP orientation.
            if context and event == "SessionStart":
                index = SQLiteMemoryIndex(root / ".cerberus" / "index.db")
                roots = [root]
                if root == Path(__file__).resolve().parent.parent:
                    from engine.integrations.orchestrator import _select_index_roots
                    roots = _select_index_roots(root)
                refresh = index.index_roots(roots)
            # Persist accounting before returning stdout. Failures can under-deliver,
            # but cannot reset the budget or count an unsaved delivery as successful.
            transaction.commit(len(context), added, hook_initialized=bool(context))
            status = "CONTEXT_READY" if context else "UNCHANGED_CONTEXT"
            if not context and remaining < cap:
                status = "BUDGET_EXHAUSTED"
            record_hook(root, payload, "CODEX", status, started,
                        project_id=project, context_chars=len(context),
                        used_chars=DEFAULT_SESSION_CONTEXT_CHARS - transaction.remaining,
                        remaining_chars=transaction.remaining, new_items=len(added),
                        indexed_files=refresh.get("indexed_files", 0), index_errors=refresh.get("errors", 0))
            return {"hookSpecificOutput": {"hookEventName": event, "additionalContext": context}} if context else {}
    except Exception as exc:
        record_hook(root, payload, "CODEX", "ERROR", started,
                    project_id=project, error_type=type(exc).__name__)
        return {}


def inspect_codex_hooks(root: Path, codex_dir: Path | None = None) -> dict:
    """Configuration evidence is reported separately from actual runtime receipts."""
    import re
    import tomllib

    directory = Path(codex_dir or os.environ.get("CODEX_HOME") or Path.home() / ".codex")
    hooks_file = directory / "hooks.json"
    try:
        config = tomllib.loads((directory / "config.toml").read_text(encoding="utf-8-sig"))
    except FileNotFoundError:
        config = {}
    except (OSError, ValueError):
        return {"config_status": "INVALID_TOML", "hooks_file": str(hooks_file)}
    try:
        document = json.loads(hooks_file.read_text(encoding="utf-8-sig"))
        hooks = document["hooks"]
        if not isinstance(hooks, dict):
            raise ValueError("Invalid hooks object")
        for groups in hooks.values():
            if not isinstance(groups, list) or any(not isinstance(group, dict) or
                    not isinstance(group.get("hooks"), list) or
                    any(not isinstance(handler, dict) for handler in group["hooks"]) for group in groups):
                raise ValueError("Invalid hook groups")
    except FileNotFoundError:
        hooks = {}
    except (OSError, ValueError, TypeError, KeyError):
        return {"config_status": "INVALID_JSON", "hooks_file": str(hooks_file)}
    state = config.get("hooks", {}).get("state", {})
    registrations = []
    for event in sorted(CONTEXT_EVENTS | CAPTURE_EVENTS):
        matches = []
        script = Path(root) / "hooks" / ("codex_context.py" if event in CONTEXT_EVENTS else "claude_session_capture.py")
        expected = f'"{str(script).replace(chr(92), "/").casefold()}"'
        for group_number, group in enumerate(hooks.get(event, [])):
            for handler_number, handler in enumerate(group.get("hooks", [])):
                command = str(handler.get("command", "")).replace("\\", "/").casefold()
                if handler.get("type") == "command" and expected in command:
                    snake_event = re.sub(r"(?<!^)(?=[A-Z])", "_", event).lower()
                    identity = f"{hooks_file}:{snake_event}:{group_number}:{handler_number}"
                    trust = state.get(identity, {})
                    matches.append({"handler_id": identity,
                        "trust_record_present": bool(trust.get("trusted_hash"))})
        registrations.append({"event": event, "registered": bool(matches), "script_exists": script.is_file(), "handlers": matches})
    features = config.get("features", {})
    return {"config_status": "READ", "hooks_file": str(hooks_file),
            "hooks_enabled": features.get("hooks", features.get("codex_hooks", True)),
            "registrations": registrations,
            "trust_note": "A persisted record does not prove current-definition trust or runtime delivery."}
