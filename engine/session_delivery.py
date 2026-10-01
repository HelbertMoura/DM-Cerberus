"""Shared, content-free conversation accounting for hooks and MCP delivery."""
from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from contextlib import contextmanager
from pathlib import Path

DEFAULT_SESSION_CONTEXT_CHARS = 12000
CONTEXT_STATE_VERSION = 3
FINGERPRINT_METADATA = "_delivery_fingerprint"
_DIGEST = re.compile(r"[0-9a-f]{64}\Z")
_TOKEN = re.compile(r"cbr-[0-9a-f]{24}\Z")


def session_token(session_id: str) -> str:
    from engine.capture import redact_secrets
    if (not isinstance(session_id, str) or not session_id.strip() or len(session_id) > 512
            or any(ord(char) < 32 or ord(char) == 127 for char in session_id)):
        raise ValueError("Invalid session identity")
    if _TOKEN.fullmatch(session_id):
        return session_id
    if session_id.startswith("cbr-") or redact_secrets(session_id)[0] != session_id:
        raise ValueError("Invalid session identity")
    return "cbr-" + hashlib.sha256(session_id.encode("utf-8")).hexdigest()[:24]


def memory_fingerprint(item) -> str:
    """Hash canonical version fields, retaining an internal pre-preview fingerprint."""
    def field(name, default=""):
        return item.get(name, default) if isinstance(item, dict) else getattr(item, name, default)
    metadata = field("metadata", {})
    cached = metadata.get(FINGERPRINT_METADATA) if isinstance(metadata, dict) else None
    if isinstance(cached, str) and _DIGEST.fullmatch(cached):
        return cached
    canonical = {name: field(name) for name in ("memory_id", "project_id", "source_path", "title", "updated_at")}
    canonical["content"] = field("full_text") or field("snippet")
    return hashlib.sha256(json.dumps(canonical, ensure_ascii=False, sort_keys=True,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def atomic_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", dir=path.parent,
                                         suffix=".tmp", delete=False) as handle:
            temporary = Path(handle.name)
            json.dump(value, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temporary, path)
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)


@contextmanager
def _context_lock(path: Path):
    """An OS lock releases on process exit; contention blocks delivery."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a+b") as handle:
        handle.seek(0)
        if not handle.read(1):
            handle.write(b"\0")
            handle.flush()
        handle.seek(0)
        if os.name == "nt":
            import msvcrt
            msvcrt.locking(handle.fileno(), msvcrt.LK_NBLCK, 1)
        else:
            import fcntl
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        try:
            yield
        finally:
            handle.seek(0)
            if os.name == "nt":
                msvcrt.locking(handle.fileno(), msvcrt.LK_UNLCK, 1)
            else:
                fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def _load_context_state(path: Path, reset: bool) -> dict:
    fresh = {"schema_version": CONTEXT_STATE_VERSION, "used_chars": 0,
             "delivered": [], "hook_initialized": False}
    if reset or not path.exists():
        return fresh
    state = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(state, dict) and (state.get("schema_version") == 2 or
                                    ("schema_version" not in state and "digest" in state)):
        # Preview hashes cannot deduplicate canonical versions safely.
        return {**fresh, "used_chars": DEFAULT_SESSION_CONTEXT_CHARS, "hook_initialized": True}
    if (not isinstance(state, dict) or type(state.get("schema_version")) is not int or
            state.get("schema_version") != CONTEXT_STATE_VERSION or
            type(state.get("used_chars")) is not int or
            not 0 <= state["used_chars"] <= DEFAULT_SESSION_CONTEXT_CHARS or
            type(state.get("hook_initialized")) is not bool or
            not isinstance(state.get("delivered"), list) or
            len(state["delivered"]) > DEFAULT_SESSION_CONTEXT_CHARS or
            any(not isinstance(key, str) or not _DIGEST.fullmatch(key) for key in state["delivered"])):
        raise ValueError("Invalid context accounting")
    return state


class DeliveryTransaction:
    def __init__(self, path: Path, state: dict):
        self._path = path
        self._state = state
        self.seen = set(state["delivered"])
        self.remaining = DEFAULT_SESSION_CONTEXT_CHARS - state["used_chars"]
        self.hook_initialized = state["hook_initialized"]

    def commit(self, chars, keys, hook_initialized=False):
        if (type(chars) is not int or not 0 <= chars <= self.remaining or
                not isinstance(keys, (list, tuple, set)) or type(hook_initialized) is not bool or
                any(not isinstance(key, str) or not _DIGEST.fullmatch(key) for key in keys)):
            raise ValueError("Invalid delivery accounting")
        seen = self.seen | set(keys)
        if len(seen) > DEFAULT_SESSION_CONTEXT_CHARS:
            raise ValueError("Invalid delivery accounting")
        state = {"schema_version": CONTEXT_STATE_VERSION,
                 "used_chars": self._state["used_chars"] + chars, "delivered": sorted(seen),
                 "hook_initialized": self.hook_initialized or hook_initialized}
        atomic_json(self._path, state)
        self._state = state
        self.seen = seen
        self.remaining -= chars
        self.hook_initialized = state["hook_initialized"]


@contextmanager
def delivery_transaction(root, session_id, reset=False):
    if type(reset) is not bool:
        raise ValueError("Invalid reset flag")
    token = session_token(session_id)
    path = Path(root) / ".cerberus" / "hooks" / f"context-{token[4:]}.json"
    with _context_lock(path.with_suffix(".lock")):
        yield DeliveryTransaction(path, _load_context_state(path, reset))


def context_status(root, session_id, reset=False) -> dict:
    with delivery_transaction(root, session_id, reset=reset) as transaction:
        if reset:
            transaction.commit(0, [])
        return {"session_token": session_token(session_id),
                "used_chars": DEFAULT_SESSION_CONTEXT_CHARS - transaction.remaining,
                "remaining_chars": transaction.remaining, "delivered_items": len(transaction.seen),
                "hook_initialized": transaction.hook_initialized}
