"""Session-end capture hook for AI coding harnesses.

Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Wired as a SessionEnd/Stop hook, with PreCompact support for Codex.
Codex Stop can use the stable last_assistant_message payload. Reads the harness hook
payload (JSON on stdin), extracts ONLY structured
Learnings/Lições/Gotchas/Findings sections from the session transcript
and files them as CANDIDATES in `.cerberus/inbox/` for human review
(`cerberus review/promote`).

Governance (hardening 002, unchanged):
- Raw chat is never a source: if no structured sections exist, nothing
  is captured.
- Automatic entries never write canonical Markdown; promotion stays
  human-gated.
- Secrets are redacted by the candidate pipeline (QUARANTINED status).

Harness payload compatibility:
- Claude Code / Qwen / Codex: snake_case stdin JSON
  (session_id, transcript_path, cwd, hook_event_name, reason).
- Antigravity/agy: camelCase stdin JSON
  (conversationId, transcriptPath, workspacePaths).
Unknown payload shapes degrade to "nothing captured" (silent exit 0).

This script must never break an agent session: every failure mode exits 0.
Use --quiet on harnesses whose Stop hooks interpret stdout (Antigravity).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

# Dedicated override for isolated tests (read lazily in main); CERBERUS_ROOT
# has index/allowlist semantics and must not be repurposed here.
OVERRIDE_ENV = "CERBERUS_CAPTURE_ROOT"

MAX_TRANSCRIPT_CHARS = 262_144   # read at most the tail 256KB of the transcript
MAX_ASSISTANT_BLOCKS = 12        # only the last N assistant text blocks

def _configure_stdio() -> None:
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        if hasattr(stream, "reconfigure"):
            try:
                stream.reconfigure(encoding="utf-8")
            except (OSError, ValueError):
                pass


def _read_payload() -> dict:
    raw = "" if sys.stdin.isatty() else sys.stdin.read()
    if not raw.strip():
        return {}
    try:
        payload = json.loads(raw)
        return payload if isinstance(payload, dict) else {}
    except json.JSONDecodeError:
        return {}


def _payload_field(payload: dict, *names: str) -> str:
    """Fetch the first present key (handles snake_case and camelCase)."""
    for name in names:
        value = payload.get(name)
        if isinstance(value, str) and value.strip():
            return value
    return ""


def _collect_text_blocks(entry: dict, found: list) -> None:
    """Read known public message envelopes; never collect user/tool/reasoning text."""
    if entry.get("type") == "response_item":
        message = entry.get("payload")
        if not isinstance(message, dict) or message.get("type") != "message":
            return
    else:
        message = entry.get("message") if isinstance(entry.get("message"), dict) else entry
    role = str(message.get("role") or entry.get("role") or entry.get("type") or "").casefold()
    if role not in {"assistant", "model"} or message.get("phase") == "analysis":
        return
    content = message.get("content")
    if isinstance(content, str) and content.strip():
        found.append(content)
    elif isinstance(content, list):
        for part in content:
            if isinstance(part, dict) and part.get("type") in (None, "text", "output_text") \
                    and isinstance(part.get("text"), str) and part["text"].strip():
                found.append(part["text"])


def _extract_assistant_text(transcript_path: str) -> str:
    """Collect assistant text blocks from the tail of a transcript (JSONL)."""
    path = Path(transcript_path)
    if not transcript_path or not path.is_file():
        return ""
    try:
        with path.open("rb") as handle:
            handle.seek(0, 2)
            size = handle.tell()
            start = max(0, size - MAX_TRANSCRIPT_CHARS)
            handle.seek(start)
            if start:
                handle.readline()  # discard the partial JSONL record at the byte boundary
            lines = handle.read().decode("utf-8-sig", errors="replace").splitlines()
    except OSError:
        return ""

    blocks: list[str] = []
    for line in lines:
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(entry, dict):
            _collect_text_blocks(entry, blocks)
    return "\n\n".join(blocks[-MAX_ASSISTANT_BLOCKS:])[-MAX_TRANSCRIPT_CHARS:]


def main(argv: list[str] | None = None) -> int:
    _configure_stdio()
    parser = argparse.ArgumentParser(description="Cerberus session-end capture hook")
    parser.add_argument("--agent", default="AGENT_SESSION",
                        help="Harness/papel de proveniência (ex: CLAUDE_CODE, QWEN, CODEX, AGY)")
    parser.add_argument("--quiet", action="store_true",
                        help="Não imprimir resultado no stdout (harnesses que interpretam output)")
    args = parser.parse_args(argv)
    started = time.perf_counter()
    payload = {}
    cerebro_root = Path(os.environ.get(OVERRIDE_ENV) or REPO_ROOT).resolve()
    from engine.agent_hooks import CAPTURE_EVENTS, record_hook
    try:
        payload = _read_payload()
        event = payload.get("hook_event_name") or payload.get("event") or ""
        if not isinstance(event, str) or (event and event not in CAPTURE_EVENTS):
            return 0
        transcript = _payload_field(payload, "transcript_path", "transcriptPath")
        # Codex's stable Stop payload works even when its transcript schema changes.
        latest = payload.get("last_assistant_message")
        text = latest[-MAX_TRANSCRIPT_CHARS:] if event == "Stop" and isinstance(latest, str) and latest.strip() else _extract_assistant_text(transcript)
        from engine.integrations.maestri import detect_project_from_path

        cwd = _payload_field(payload, "cwd", "workspacePaths")
        if not cwd:
            workspace = payload.get("workspacePaths")
            cwd = workspace[0] if isinstance(workspace, list) and workspace else ""
        project_id = detect_project_from_path(cwd)
        session_id = _payload_field(payload, "session_id", "conversationId")
        # Usage telemetry is independent of structured learning capture.
        try:
            from engine.token_ledger import normalize_usage, record_turn_tokens
            usage = payload.get("token_usage") or payload.get("usage")
            if isinstance(usage, dict) and usage:
                counts = normalize_usage(usage)
                provider_event_id = _payload_field(payload, "event_id", "turn_id", "response_id")
                fingerprint = hashlib.sha256(json.dumps(payload, sort_keys=True, ensure_ascii=False).encode("utf-8")).hexdigest()
                record_turn_tokens(
                    session_id=session_id or f"ses-{args.agent.lower()}",
                    project_id=project_id, agent=args.agent,
                    model=str(payload.get("model") or "unknown"),
                    **counts, event_id=provider_event_id or f"payload-{fingerprint}",
                    usage_source="hook_payload",
                    db_path=cerebro_root / ".cerberus" / "token_ledger.db",
                )
        except Exception:
            pass  # failed or malformed telemetry must never break a harness hook
        if not text.strip():
            record_hook(cerebro_root, payload, args.agent, "NO_ASSISTANT_TEXT", started,
                        project_id=project_id)
            return 0

        from engine.capture import AutoCaptureEngine
        engine = AutoCaptureEngine(cerebro_root=cerebro_root)
        match = re.search(r"(?im)^\s*TASK(?:-ID)?\s*:\s*([^\s]+)", text)
        if match:
            task_id = match.group(1)
        elif session_id:
            task_id = f"SES-{session_id[:8]}"
        else:
            task_id = f"SES-{args.agent}"
        result = engine.ingest_report(
            text,
            task_id=task_id,
            project_id=project_id,
            agent_role=args.agent,
            allow_file=False,      # content-only: never reads paths from disk
        )

        record_hook(cerebro_root, payload, args.agent,
                    "CAPTURED" if result.get("candidate_count") else "NO_NEW_CANDIDATES", started,
                    project_id=project_id, candidate_count=result.get("candidate_count", 0))
        if result.get("candidate_count") == 0:
            return 0  # nothing structured was found; raw chat is never a source
        if not args.quiet:
            print(json.dumps({"cerberus_capture": result, "project_id": project_id},
                             ensure_ascii=False))
    except Exception as exc:  # never break the agent session
        record_hook(cerebro_root, payload, args.agent, "ERROR", started, error_type=type(exc).__name__)
        if not args.quiet:
            print(json.dumps({"cerberus_capture": "ERROR", "error_type": type(exc).__name__},
                             ensure_ascii=False))
    finally:
        if args.quiet and args.agent == "CODEX" and payload.get("hook_event_name") == "Stop":
            print("{}")  # valid Stop output, with no continuation or blocking decision
    return 0


if __name__ == "__main__":
    sys.exit(main())
