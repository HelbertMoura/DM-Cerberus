"""Typed handoffs with claim-exactly-once semantics.

Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Inspired by the ai-memory handoff protocol (akitaonrails): a handoff is a
typed, owned record that exactly one worker can claim. This module only
manages operational workflow state in ``.cerberus/handoffs/``; it never
touches canonical Markdown. Canonical promotion remains the exclusive
domain of the candidate pipeline (``engine.capture``).
"""
from __future__ import annotations

import datetime as dt
import hashlib
import json
import os
import re
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class HandoffStatus(str, Enum):
    OPEN = "OPEN"
    CLAIMED = "CLAIMED"
    DONE = "DONE"
    CANCELLED = "CANCELLED"


class HandoffStore:
    """File-backed handoff store with atomic claim markers.

    Claim atomicity relies on exclusive creation (``O_CREAT | O_EXCL``),
    which is atomic on both POSIX and Windows NTFS: when two workers race
    to claim the same handoff, exactly one creates the ``<id>.claim``
    marker and owns the handoff.
    """

    def __init__(self, cerebro_root: Path) -> None:
        self.cerebro_root = Path(cerebro_root).resolve()
        self.store_dir = self.cerebro_root / ".cerberus" / "handoffs"
        self.store_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ paths
    def _validate_id(self, handoff_id: str) -> str:
        if not re.fullmatch(r"HDO-[a-f0-9]{12}", handoff_id or ""):
            raise ValueError("Invalid handoff id")
        return handoff_id

    def _path(self, handoff_id: str) -> Path:
        self._validate_id(handoff_id)
        path = (self.store_dir / f"{handoff_id}.json").resolve()
        if path.parent != self.store_dir:
            raise ValueError("Handoff path escapes store")
        return path

    def _claim_path(self, handoff_id: str) -> Path:
        self._validate_id(handoff_id)
        path = (self.store_dir / f"{handoff_id}.claim").resolve()
        if path.parent != self.store_dir:
            raise ValueError("Claim path escapes store")
        return path

    # ------------------------------------------------------------------- io
    @staticmethod
    def _write_atomic(path: Path, payload: str) -> None:
        temp = path.with_suffix(path.suffix + ".tmp")
        temp.write_text(payload, encoding="utf-8")
        os.replace(temp, path)

    def _save(self, handoff: Dict[str, Any]) -> None:
        self._write_atomic(self._path(handoff["handoff_id"]),
                           json.dumps(handoff, ensure_ascii=False, indent=2) + "\n")

    def get(self, handoff_id: str) -> Dict[str, Any]:
        path = self._path(handoff_id)
        try:
            handoff = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            raise ValueError(f"Handoff entry is invalid or missing: {handoff_id}") from exc
        if handoff.get("handoff_id") != handoff_id:
            raise ValueError("Handoff identity mismatch")
        return handoff

    def list(self, status: Optional[str] = None) -> List[Dict[str, Any]]:
        items: List[Dict[str, Any]] = []
        for path in sorted(self.store_dir.glob("HDO-*.json")):
            try:
                item = self.get(path.stem)
            except ValueError:
                continue
            if status is None or item.get("status") == status:
                items.append(item)
        return items

    # ------------------------------------------------------------- lifecycle
    def create(self, project_id: str, task_id: str, summary: str,
               from_agent: str, to_role: str = "") -> Dict[str, Any]:
        if not all(str(v or "").strip() for v in (project_id, task_id, summary, from_agent)):
            raise ValueError("project_id, task_id, summary and from_agent are required")
        created_at = dt.datetime.now(dt.timezone.utc).isoformat()
        digest = hashlib.sha256(
            "\x1f".join((project_id.strip(), task_id.strip(), created_at, summary.strip())).encode()
        ).hexdigest()
        handoff = {
            "handoff_id": f"HDO-{digest[:12]}",
            "project_id": project_id.strip(),
            "task_id": task_id.strip(),
            "summary": summary.strip(),
            "from_agent": from_agent.strip(),
            "to_role": (to_role or "").strip(),
            "status": HandoffStatus.OPEN.value,
            "created_at": created_at,
            "claim": None,
            "done": None,
        }
        self._save(handoff)
        return handoff

    def find_open_by_task(self, task_id: str, project_id: Optional[str] = None) -> List[Dict[str, Any]]:
        matches = [h for h in self.list(status=HandoffStatus.OPEN.value)
                   if h.get("task_id") == (task_id or "").strip()
                   and (project_id is None or h.get("project_id") == project_id.strip())]
        return matches

    def claim(self, handoff_id: str, agent: str) -> Dict[str, Any]:
        if not (agent or "").strip():
            raise ValueError("agent is required to claim a handoff")
        handoff = self.get(handoff_id)
        if handoff["status"] != HandoffStatus.OPEN.value:
            raise ValueError(f"Handoff {handoff_id} is {handoff['status']}, not OPEN")
        if handoff.get("to_role") and handoff["to_role"].casefold() != agent.strip().casefold() \
                and "*" not in handoff["to_role"]:
            raise ValueError(f"Handoff {handoff_id} is reserved for role {handoff['to_role']}")
        # Atomic gate: exactly one process ever creates the claim marker.
        claim_path = self._claim_path(handoff_id)
        marker = json.dumps({"agent": agent.strip(),
                             "claimed_at": dt.datetime.now(dt.timezone.utc).isoformat()},
                            ensure_ascii=False)
        try:
            fd = os.open(str(claim_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
        except FileExistsError as exc:
            raise ValueError(f"Handoff {handoff_id} was already claimed") from exc
        try:
            os.write(fd, marker.encode("utf-8"))
        finally:
            os.close(fd)
        handoff["status"] = HandoffStatus.CLAIMED.value
        handoff["claim"] = json.loads(claim_path.read_text(encoding="utf-8"))
        self._save(handoff)
        return handoff

    def complete(self, handoff_id: str, agent: str, result: str = "") -> Dict[str, Any]:
        handoff = self.get(handoff_id)
        if handoff["status"] != HandoffStatus.CLAIMED.value:
            raise ValueError(f"Handoff {handoff_id} is {handoff['status']}, not CLAIMED")
        owner = (handoff.get("claim") or {}).get("agent", "")
        if owner.casefold() != (agent or "").strip().casefold():
            raise ValueError(f"Only the claiming agent ({owner}) can complete this handoff")
        handoff["status"] = HandoffStatus.DONE.value
        handoff["done"] = {"agent": agent.strip(), "result": (result or "").strip(),
                           "done_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        self._save(handoff)
        return handoff

    def cancel(self, handoff_id: str, agent: str) -> Dict[str, Any]:
        handoff = self.get(handoff_id)
        if handoff["status"] not in {HandoffStatus.OPEN.value, HandoffStatus.CLAIMED.value}:
            raise ValueError(f"Handoff {handoff_id} is already {handoff['status']}")
        if handoff["status"] == HandoffStatus.CLAIMED.value:
            owner = (handoff.get("claim") or {}).get("agent", "")
            if owner.casefold() != (agent or "").strip().casefold():
                raise ValueError(f"Only the claiming agent ({owner}) can cancel this handoff")
        handoff["status"] = HandoffStatus.CANCELLED.value
        self._save(handoff)
        return handoff
