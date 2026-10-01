"""Candidate-only capture, ingestion, and operator-gated promotion."""
from __future__ import annotations

import datetime as dt
import difflib
import hashlib
import json
import os
import re
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

from engine.models import Candidate, CandidateStatus

SECRET_PATTERNS = (
    ("private_key", re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", re.I)),
    ("authorization", re.compile(r"(?i)\b(?:authorization\s*:\s*(?:bearer|basic)\s+)[^\s]+")),
    ("password", re.compile(r"(?im)\b(password|passwd|pwd)\s*[:=]\s*[^\s]+")),
    ("connection_string", re.compile(r"(?i)\b(?:postgres(?:ql)?|mysql|mongodb(?:\+srv)?|redis)://[^\s]+")),
    ("api_token", re.compile(
        r"(?im)\b(api[_-]?key|access[_-]?token|auth[_-]?token|client[_-]?secret|secret[_-]?key|token)"
        r"\s*[:=]\s*['\"]?[^\s'\"]+"
    )),
    ("provider_token", re.compile(r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|sk-(?:proj-)?[A-Za-z0-9_-]{20,}|AKIA[A-Z0-9]{16})\b")),
    ("jwt", re.compile(r"\beyJ[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\.[A-Za-z0-9_-]{10,}\b")),
)


def _normalize(value: str) -> str:
    return " ".join(value.casefold().split())


def _fingerprint(project_id: str, kind: str, title: str, content: str) -> str:
    payload = "\x1f".join(map(_normalize, (project_id, kind, title, content)))
    return hashlib.sha256(payload.encode()).hexdigest()


def redact_secrets(text: str) -> tuple[str, List[str]]:
    findings: List[str] = []
    redacted = text
    for name, pattern in SECRET_PATTERNS:
        if pattern.search(redacted):
            findings.append(name)
            redacted = pattern.sub("[REDACTED]", redacted)
    return redacted, findings


class CandidateStore:
    def __init__(self, inbox_dir: Path, canonical_root: Path) -> None:
        self.inbox_dir = Path(inbox_dir).resolve()
        self.canonical_root = Path(canonical_root).resolve()
        self.inbox_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, candidate_id: str) -> Path:
        if not re.fullmatch(r"[a-f0-9]{16}|broken", candidate_id):
            raise ValueError("Invalid candidate id")
        path = (self.inbox_dir / f"{candidate_id}.json").resolve()
        if path.parent != self.inbox_dir:
            raise ValueError("Candidate path escapes inbox")
        return path

    def save(self, candidate: Candidate, *, create_only: bool = False) -> Optional[Path]:
        target = self._path(candidate.candidate_id)
        temp = target.with_name(f"{target.name}.{uuid.uuid4().hex}.tmp")
        try:
            temp.write_text(json.dumps(candidate.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            if create_only:
                try:
                    # Publish a complete file atomically without replacing another writer's candidate.
                    os.link(temp, target)
                except FileExistsError:
                    return None
            else:
                os.replace(temp, target)
            return target
        finally:
            temp.unlink(missing_ok=True)

    def get(self, candidate_id: str) -> Candidate:
        try:
            data = json.loads(self._path(candidate_id).read_text(encoding="utf-8"))
            item = Candidate.from_dict(data)
        except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Candidate store entry is invalid: {candidate_id}") from exc
        if item.candidate_id != candidate_id:
            raise ValueError("Candidate identity mismatch")
        return item

    def find_by_fingerprint(self, fingerprint: str) -> Optional[Candidate]:
        for path in sorted(self.inbox_dir.glob("*.json")):
            try:
                item = self.get(path.stem)
            except ValueError:
                continue
            if item.fingerprint == fingerprint:
                return item
        return None

    def list(self) -> List[Candidate]:
        candidates: List[Candidate] = []
        for path in sorted(self.inbox_dir.glob("*.json")):
            try:
                candidates.append(self.get(path.stem))
            except ValueError:
                continue
        return candidates


class AutoCaptureEngine:
    def __init__(self, service: Any = None, cerebro_root: Optional[Path] = None) -> None:
        self.service = service
        self.cerebro_root = Path(cerebro_root or Path(__file__).resolve().parent.parent).resolve()
        self.store = CandidateStore(self.cerebro_root / ".cerberus" / "inbox", self.cerebro_root)

    def capture_learning(self, title: str, content: str, category: str = "learning",
                         project_id: Optional[str] = None, task_id: Optional[str] = None,
                         agent_role: str = "", source: str = "manual_capture",
                         source_path: Optional[str] = None, confidence: float = 0.5,
                         authority_hint: str = "AGENT_OBSERVATION") -> Dict[str, Any]:
        project = (project_id or "_global").strip()
        if not title.strip() or not content.strip():
            raise ValueError("title and content are required")
        if not task_id or not task_id.strip() or not agent_role.strip():
            raise ValueError("task_id and agent_role provenance are required")
        clean_title, title_secrets = redact_secrets(title.strip())
        clean_content, content_secrets = redact_secrets(content.strip())
        findings = sorted(set(title_secrets + content_secrets))
        fingerprint = _fingerprint(project, category, clean_title, clean_content)
        existing = self.store.find_by_fingerprint(fingerprint)
        if existing:
            return {"status": "SKIPPED_DUPLICATE", "candidate_id": existing.candidate_id}
        item = Candidate(
            candidate_id=fingerprint[:16], project_id=project, type=category,
            title=clean_title, content=clean_content, source=source,
            source_path=source_path, task_id=task_id.strip(), agent=agent_role.strip(),
            created_at=dt.datetime.now(dt.timezone.utc).isoformat(),
            confidence=max(0.0, min(1.0, float(confidence))), authority_hint=authority_hint,
            fingerprint=fingerprint,
            status=CandidateStatus.QUARANTINED if findings else CandidateStatus.CANDIDATE,
            secret_findings=findings,
        )
        path = self.store.save(item, create_only=True)
        if path is None:
            published = self.store.get(item.candidate_id)
            if published.fingerprint != item.fingerprint:
                raise ValueError("Candidate identity collision")
            return {"status": "SKIPPED_DUPLICATE", "candidate_id": published.candidate_id}
        return {"status": item.status.value, "candidate_id": item.candidate_id, "candidate_path": str(path)}

    def ingest_report(self, report_path_or_content: str, task_id: Optional[str] = None,
                      project_id: str = "dm-cerebro", agent_role: str = "REPORT_INGESTER",
                      allow_file: bool = True) -> Dict[str, Any]:
        source_path = None
        content = report_path_or_content
        path = Path(report_path_or_content)
        if allow_file and path.is_file():
            source_path = str(path.resolve())
            content = path.read_text(encoding="utf-8", errors="replace")
        if not task_id:
            match = re.search(r"(?im)^\s*TASK(?:-ID)?\s*:\s*([^\s]+)", content)
            task_id = match.group(1) if match else None
        if not task_id:
            raise ValueError("task_id provenance is required")
        ids: List[str] = []
        pattern = re.compile(r"(?ims)^#{1,3}\s+(?:Learnings|Lições Aprendidas|Gotchas|Findings)\s*$([\s\S]*?)(?=^#{1,3}\s|\Z)")
        for section in pattern.findall(content):
            for value in re.findall(r"(?m)^\s*(?:[-*]|\d+\.)\s+(.+)$", section):
                if len(value.strip()) < 20:
                    continue
                result = self.capture_learning(value.split(":", 1)[0][:80], value, project_id=project_id,
                    task_id=task_id, agent_role=agent_role, source="report", source_path=source_path,
                    authority_hint="OPERATIONAL_REPORT")
                if result["status"] in {"CANDIDATE", "QUARANTINED"}:
                    ids.append(result["candidate_id"])
        return {"status": "COMPLETE", "candidate_count": len(ids), "candidate_ids": ids}

    def promote(self, candidate_id: str, apply: bool = False) -> Dict[str, Any]:
        item = self.store.get(candidate_id)
        expected_fingerprint = _fingerprint(item.project_id, item.type, item.title, item.content)
        if not item.fingerprint or item.fingerprint != expected_fingerprint:
            raise ValueError("Candidate fingerprint mismatch")
        clean_title, title_findings = redact_secrets(item.title)
        clean_content, content_findings = redact_secrets(item.content)
        findings = sorted(set(title_findings + content_findings))
        if findings:
            item.title = clean_title
            item.content = clean_content
            item.secret_findings = sorted(set(item.secret_findings + findings))
            item.status = CandidateStatus.QUARANTINED
            self.store.save(item)
            raise ValueError("Quarantined candidates cannot be promoted")
        if item.status == CandidateStatus.QUARANTINED:
            raise ValueError("Quarantined candidates cannot be promoted")
        if not item.task_id or not item.agent or not item.fingerprint:
            raise ValueError("Complete provenance is required for promotion")
        target_name = "DECISIONS.md" if item.type.casefold() in {"decision", "adr"} else "LEARNINGS.md"
        target = (self.cerebro_root / target_name).resolve()
        if target.parent != self.cerebro_root or target.name not in {"LEARNINGS.md", "DECISIONS.md"}:
            raise ValueError("Promotion target is not allowlisted")
        entry = (f"\n### {item.title}\n> **Proveniência:** Task `{item.task_id}` · Agente `{item.agent}` · "
                 f"Projeto `{item.project_id}` · Capturado `{item.created_at}` · Fingerprint `{item.fingerprint}`\n\n{item.content}\n")
        before = target.read_text(encoding="utf-8") if target.exists() else ""
        diff = "\n".join(difflib.unified_diff(before.splitlines(), (before + entry).splitlines(),
                                                fromfile=target.name, tofile=target.name, lineterm=""))
        if not apply:
            return {"status": "PREVIEW", "candidate_id": candidate_id, "target_file": str(target), "diff": diff}
        if item.status == CandidateStatus.CANONICAL:
            return {"status": "CANONICAL", "candidate_id": candidate_id, "target_file": str(target), "already_applied": True}
        if item.status != CandidateStatus.VERIFIED:
            raise ValueError("Candidate must be VERIFIED before canonical promotion")
        temp = target.with_suffix(target.suffix + ".tmp")
        temp.write_text(before + entry, encoding="utf-8")
        os.replace(temp, target)
        item.status = CandidateStatus.CANONICAL
        item.canonical_path = str(target)
        self.store.save(item)
        return {"status": "CANONICAL", "candidate_id": candidate_id, "target_file": str(target), "already_applied": False}

    def verify(self, candidate_id: str) -> Dict[str, Any]:
        item = self.store.get(candidate_id)
        if item.status != CandidateStatus.CANDIDATE:
            raise ValueError("Only CANDIDATE items can be verified")
        item.status = CandidateStatus.VERIFIED
        self.store.save(item)
        return {"status": "VERIFIED", "candidate_id": candidate_id}

    def reject(self, candidate_id: str) -> Dict[str, Any]:
        item = self.store.get(candidate_id)
        if item.status == CandidateStatus.CANONICAL:
            raise ValueError("Canonical candidates cannot be rejected")
        item.status = CandidateStatus.REJECTED
        self.store.save(item)
        return {"status": "REJECTED", "candidate_id": candidate_id}
