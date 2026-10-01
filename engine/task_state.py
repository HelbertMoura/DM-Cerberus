"""Short operational checkpoints; file references are never opened."""
from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import tempfile
import threading
import time
from contextlib import contextmanager
from pathlib import Path

from engine.capture import redact_secrets


MAX_STATE_CHARS = 6000
_STATUSES = {"in_progress", "paused", "done"}
_ID = re.compile(r"[A-Za-z0-9][A-Za-z0-9_.-]{0,95}\Z")
_THREAD_LOCK = threading.RLock()
_TEXT_FIELDS = ("objective", "decisions", "files", "validation", "next_step", "status")
_STATE_KEYS = set(_TEXT_FIELDS) | {"project_id", "task_id", "version", "hash", "truncated", "redacted"}
_URL_CREDENTIALS = re.compile(r"(?i)([a-z][a-z0-9+.-]*://)[^/\s@]+:[^/\s@]+@")
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(?<!\w)['\"]?(?:password|passwd|pwd|secret|private[_-]?key|"
    r"api[_-]?(?:key|token)|access[_-]?token|auth[_-]?token|client[_-]?secret|secret[_-]?key|token)"
    r"['\"]?\s*[:=]\s*(?:\"(?:\\[\s\S]|[^\"\\])*(?:\"|(?:\\)?$)"
    r"|'(?:\\[\s\S]|[^'\\])*(?:'|(?:\\)?$)|[^\s,;&]+)"
)
_PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?"
    r"(?:-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|$)", re.I
)


def _redact(value):
    clean, private_key = _PRIVATE_KEY.subn("[REDACTED]", value)
    clean, assignments = _SECRET_ASSIGNMENT.subn("[REDACTED]", clean)
    clean, credentials = _URL_CREDENTIALS.subn(r"\1[REDACTED]@", clean)
    clean, findings = redact_secrets(clean)
    return clean, bool(private_key or assignments or credentials or findings)


def _clip(value, limit):
    marker = "… [truncated]"
    return value[:max(0, limit - len(marker))] + marker if len(value) > limit else value


def _json(value):
    return json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True)


def _identifier(value):
    if not isinstance(value, str) or not _ID.fullmatch(value) or ".." in value:
        raise ValueError("Invalid task checkpoint identifier")
    if redact_secrets(value)[1]:
        raise ValueError("Sensitive task checkpoint identifier")
    return value


def _hash(state):
    return hashlib.sha256(_json({key: value for key, value in state.items()
                               if key not in {"hash", "found"}}).encode("utf-8")).hexdigest()


def _fields(objective, decisions, files, validation, next_step, status):
    truncated = redacted = False

    def text(value, limit):
        nonlocal truncated, redacted
        if not isinstance(value, str) or len(value) > 200000:
            raise ValueError("Checkpoint text must be a bounded string")
        clean, sensitive = _redact(value.strip())
        try:
            clean.encode("utf-8")
        except UnicodeError:
            raise ValueError("Checkpoint text must be valid UTF-8") from None
        redacted |= sensitive
        if len(clean) > limit:
            truncated = True
            clean = _clip(clean, limit)
        return clean

    result = {"objective": text(objective, 600), "next_step": text(next_step, 600)}
    if not result["objective"] or not isinstance(status, str) or status not in _STATUSES:
        raise ValueError("Checkpoint objective and status are required")
    result["status"] = status
    for name, values in (("decisions", decisions), ("files", files), ("validation", validation)):
        values = [] if values is None else values
        if not isinstance(values, list) or any(not isinstance(value, str) for value in values):
            raise ValueError("Checkpoint arrays must contain strings")
        truncated |= len(values) > 12
        result[name] = [text(value, 240) for value in values[:12]]
    result.update(truncated=truncated, redacted=redacted)
    return result


class TaskStateStore:
    def __init__(self, root):
        self.root = Path(root).resolve()

    def _path(self, project_id, task_id):
        _identifier(project_id)
        _identifier(task_id)
        project_key = hashlib.sha256(project_id.encode("utf-8")).hexdigest()
        task_key = hashlib.sha256(task_id.encode("utf-8")).hexdigest()
        return self.root / ".cerberus" / "task_state" / project_key / f"{task_key}.json"

    def _safe(self, path, create=False):
        """Reject links, junctions, special files and paths outside the trusted root."""
        current = self.root
        for component in path.relative_to(self.root).parts:
            current = current / component
            try:
                if current.is_symlink() or current.resolve() != current:
                    raise ValueError("Checkpoint path contains a link")
            except (OSError, RuntimeError):
                raise ValueError("Invalid checkpoint path") from None
            if current == path:
                if current.exists():
                    info = current.stat()
                    if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
                        raise ValueError("Checkpoint path must be an unlinked regular file")
            elif create:
                if current.exists() and not current.is_dir():
                    raise ValueError("Invalid checkpoint directory")
                current.mkdir(exist_ok=True)
                if current.resolve() != current or not current.is_dir():
                    raise ValueError("Invalid checkpoint directory")
            elif current.exists() and not current.is_dir():
                raise ValueError("Invalid checkpoint directory")

    def _open(self, path, flags):
        self._safe(path)
        fd = os.open(path, flags | getattr(os, "O_NOFOLLOW", 0), 0o600)
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            os.close(fd)
            raise ValueError("Checkpoint path must be an unlinked regular file")
        try:
            self._safe(path)
        except BaseException:
            os.close(fd)
            raise
        return fd

    @contextmanager
    def _locked(self, path):
        with _THREAD_LOCK:
            self._safe(path, create=True)
            lock_path = path.with_suffix(".lock")
            fd = self._open(lock_path, os.O_CREAT | os.O_RDWR)
            with os.fdopen(fd, "r+b") as stream:
                if not os.fstat(stream.fileno()).st_size:
                    stream.write(b"\0")
                    stream.flush()
                acquired = False
                deadline = time.monotonic() + 5
                try:
                    while not acquired:
                        stream.seek(0)
                        try:
                            if os.name == "nt":
                                import msvcrt
                                msvcrt.locking(stream.fileno(), msvcrt.LK_NBLCK, 1)
                            else:
                                import fcntl
                                fcntl.flock(stream.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
                            acquired = True
                        except OSError:
                            if time.monotonic() >= deadline:
                                raise OSError("Checkpoint lock unavailable") from None
                            time.sleep(0.01)
                    self._safe(path)
                    self._safe(lock_path)
                    yield
                finally:
                    if acquired:
                        stream.seek(0)
                        if os.name == "nt":
                            msvcrt.locking(stream.fileno(), msvcrt.LK_UNLCK, 1)
                        else:
                            fcntl.flock(stream.fileno(), fcntl.LOCK_UN)

    def _read(self, path, project_id, task_id):
        self._safe(path)
        try:
            fd = self._open(path, os.O_RDONLY)
        except FileNotFoundError:
            return {"found": False, "project_id": project_id, "task_id": task_id}
        try:
            with os.fdopen(fd, "r", encoding="utf-8") as stream:
                payload = stream.read(MAX_STATE_CHARS + 1)
            if len(payload) > MAX_STATE_CHARS:
                raise ValueError("Checkpoint exceeds the state budget")
            state = json.loads(payload)
            if not isinstance(state, dict) or set(state) != _STATE_KEYS:
                raise ValueError("Invalid checkpoint schema")
            if state["project_id"] != project_id or state["task_id"] != task_id:
                raise ValueError("Checkpoint identity mismatch")
            if (type(state["version"]) is not int or not 1 <= state["version"] < 2**63
                    or type(state["truncated"]) is not bool or type(state["redacted"]) is not bool):
                raise ValueError("Invalid checkpoint metadata")
            clean = _fields(**{key: state[key] for key in _TEXT_FIELDS})
            if clean["redacted"] or any(state[key] != clean[key] for key in _TEXT_FIELDS):
                raise ValueError("Checkpoint contains invalid or sensitive fields")
            if not isinstance(state["hash"], str) or state["hash"] != _hash(state):
                raise ValueError("Checkpoint integrity mismatch")
            result = dict(state, found=True)
            if len(_json(result)) > MAX_STATE_CHARS:
                raise ValueError("Checkpoint exceeds the state budget")
            return result
        except (ValueError, TypeError, UnicodeError):
            raise ValueError("Invalid task checkpoint") from None

    def save(self, project_id, task_id, objective, decisions=None, files=None,
             validation=None, next_step="", status="in_progress"):
        path = self._path(project_id, task_id)
        state = _fields(objective, decisions, files, validation, next_step, status)
        with self._locked(path):
            previous = self._read(path, project_id, task_id)
            state.update(project_id=project_id, task_id=task_id,
                         version=previous.get("version", 0) + 1)
            if state["version"] >= 2**63:
                raise ValueError("Checkpoint version limit reached")
            state["hash"] = _hash(state)
            while len(_json(dict(state, found=True))) > MAX_STATE_CHARS:
                arrays = [name for name in ("decisions", "files", "validation") if state[name]]
                if arrays:
                    largest = max(arrays, key=lambda name: len(_json(state[name])))
                    state[largest].pop()
                else:
                    largest = max(("objective", "next_step"), key=lambda name: len(_json(state[name])))
                    state[largest] = _clip(state[largest], max(40, len(state[largest]) // 2))
                state["truncated"] = True
                state["hash"] = _hash(state)
            self._safe(path)
            fd, temporary = tempfile.mkstemp(dir=path.parent, prefix=".checkpoint-", suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as stream:
                    stream.write(_json(state))
                    stream.flush()
                    os.fsync(stream.fileno())
                self._safe(path)
                self._safe(Path(temporary))
                os.replace(temporary, path)
            finally:
                self._safe(Path(temporary))
                Path(temporary).unlink(missing_ok=True)
        return {key: state[key] for key in ("project_id", "task_id", "version", "hash", "truncated", "redacted")} | {"saved": True}

    def get(self, project_id, task_id):
        path = self._path(project_id, task_id)
        with _THREAD_LOCK:
            self._safe(path)
            if not path.exists():
                return {"found": False, "project_id": project_id, "task_id": task_id}
            with self._locked(path):
                return self._read(path, project_id, task_id)
