"""
Cerberus Token-Ledger & Anti-Loop Engine (OpenWolf / Pro 5x Telemetry)
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)

Módulo local-first e ultraleve (SQLite stdlib) para auditoria de consumo
de tokens (Prompt, Completion, Reasoning) no plano OpenAI Pro 5x e
observação de sequências de re-leitura quando chamadas explicitamente.
"""
from __future__ import annotations

import datetime as dt
import json
import math
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Dict, Generator, List, Optional, Tuple

DEFAULT_LEDGER_DB_NAME = "token_ledger.db"
DEFAULT_WINDOW_HOURS = 24
LOOP_THRESHOLD = 3

# No inferred prices: callers may explicitly configure rates per million tokens.
MODEL_PRICING: dict = {}


def _token_count(value: Any, name: str) -> Optional[int]:
    if value is None:
        return None
    if isinstance(value, bool) or not isinstance(value, int) or value < 0:
        raise ValueError(f"{name} must be a non-negative integer")
    return value


def normalize_usage(usage: dict) -> Dict[str, Any]:
    """Normalize provider output totals; reasoning is a subset, never added twice."""
    def first(*keys):
        return next((usage[k] for k in keys if k in usage), None)
    details = usage.get("completion_tokens_details") or usage.get("output_tokens_details") or {}
    reasoning = first("reasoning_tokens", "reasoning")
    if reasoning is None and isinstance(details, dict):
        reasoning = details.get("reasoning_tokens")
    return {
        "prompt_tokens": _token_count(first("prompt_tokens", "input_tokens"), "prompt_tokens"),
        "completion_tokens": _token_count(first("completion_tokens", "output_tokens"), "completion_tokens"),
        "reasoning_tokens": _token_count(reasoning, "reasoning_tokens"),
        "total_tokens": _token_count(first("total_tokens"), "total_tokens"),
    }


def get_ledger_db_path(root: Optional[Path] = None) -> Path:
    base = Path(root or os.environ.get("CERBERUS_ROOT") or Path(__file__).resolve().parent.parent)
    return base / ".cerberus" / DEFAULT_LEDGER_DB_NAME


@contextmanager
def db_connection(path: Path) -> Generator[sqlite3.Connection, None, None]:
    con = sqlite3.connect(str(path), timeout=10.0)
    try:
        yield con
        con.commit()
    finally:
        con.close()


def init_ledger_db(db_path: Optional[Path] = None) -> Path:
    path = Path(db_path or get_ledger_db_path()).resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    with db_connection(path) as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS token_ledger (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                project_id TEXT NOT NULL,
                agent TEXT NOT NULL,
                model TEXT NOT NULL,
                prompt_tokens INTEGER DEFAULT 0,
                completion_tokens INTEGER DEFAULT 0,
                reasoning_tokens INTEGER DEFAULT 0,
                total_tokens INTEGER DEFAULT 0,
                loops_prevented INTEGER DEFAULT 0,
                cost_estimated REAL DEFAULT 0.0,
                created_at TEXT NOT NULL
            )
        """)
        columns = {row[1] for row in con.execute("PRAGMA table_info(token_ledger)")}
        for name, sql_type in (("event_id", "TEXT"), ("usage_source", "TEXT"),
                               ("usage_status", "TEXT"), ("pricing_source", "TEXT")):
            if name not in columns:
                con.execute(f"ALTER TABLE token_ledger ADD COLUMN {name} {sql_type}")
        con.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_ledger_event ON token_ledger(session_id, agent, event_id) WHERE event_id IS NOT NULL")
        con.execute("CREATE INDEX IF NOT EXISTS idx_ledger_session ON token_ledger(session_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_ledger_project ON token_ledger(project_id)")
        con.execute("CREATE INDEX IF NOT EXISTS idx_ledger_created ON token_ledger(created_at)")

        con.execute("""
            CREATE TABLE IF NOT EXISTS file_access_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                file_path TEXT NOT NULL,
                turn_id TEXT DEFAULT '',
                has_writes INTEGER DEFAULT 0,
                created_at TEXT NOT NULL
            )
        """)
        columns = {row[1] for row in con.execute("PRAGMA table_info(file_access_log)")}
        for name, sql_type in (("read_count", "INTEGER DEFAULT 1"), ("is_loop", "INTEGER DEFAULT 0")):
            if name not in columns:
                con.execute(f"ALTER TABLE file_access_log ADD COLUMN {name} {sql_type}")
        con.execute("CREATE INDEX IF NOT EXISTS idx_access_session_file ON file_access_log(session_id, file_path)")
    return path


def estimate_token_cost(model: str, prompt: int, completion: int, reasoning: int = 0,
                        pricing: Optional[dict] = None) -> Optional[float]:
    """Optional explicitly configured estimate; output rate already covers reasoning."""
    prompt = _token_count(prompt, "prompt_tokens")
    completion = _token_count(completion, "completion_tokens")
    _token_count(reasoning, "reasoning_tokens")
    rates = pricing if pricing is not None else MODEL_PRICING.get(model.lower())
    if rates is None or prompt is None or completion is None:
        return None
    if not rates.get("source"):
        raise ValueError("pricing requires an explicit source")
    for key in ("prompt", "completion"):
        rate = rates.get(key)
        if isinstance(rate, bool) or not isinstance(rate, (int, float)) or not math.isfinite(rate) or rate < 0:
            raise ValueError("pricing rates must be finite non-negative numbers")
    return round((prompt * rates["prompt"] + completion * rates["completion"]) / 1_000_000, 8)


def record_turn_tokens(
    session_id: str, project_id: str, agent: str, model: str,
    prompt_tokens: Optional[int], completion_tokens: Optional[int],
    reasoning_tokens: Optional[int] = 0, loops_prevented: int = 0,
    db_path: Optional[Path] = None, *, total_tokens: Optional[int] = None,
    event_id: Optional[str] = None, usage_source: str = "manual",
    pricing: Optional[dict] = None,
) -> Dict[str, Any]:
    """Record measured tokens. Completion includes reasoning; unknown fields stay NULL.

    Repeated event_id within the same session/agent returns the original record.
    Callers without a provider ID must supply their own stable event fingerprint.
    """
    prompt = _token_count(prompt_tokens, "prompt_tokens")
    completion = _token_count(completion_tokens, "completion_tokens")
    reasoning = _token_count(reasoning_tokens, "reasoning_tokens")
    total = _token_count(total_tokens, "total_tokens")
    loops = _token_count(loops_prevented, "loops_prevented")
    if reasoning is not None and completion is not None and reasoning > completion:
        raise ValueError("reasoning_tokens cannot exceed completion_tokens")
    if prompt is not None and completion is not None:
        measured_total = prompt + completion
        if total is not None and total != measured_total:
            raise ValueError("total_tokens disagrees with input/output totals")
        total = measured_total
    if total is None and prompt is None and completion is None and reasoning is None:
        raise ValueError("usage is unavailable")
    status = "complete" if prompt is not None and completion is not None else "partial"
    cost = estimate_token_cost(model, prompt, completion, reasoning, pricing)
    rates = pricing if pricing is not None else MODEL_PRICING.get(model.lower())
    path = init_ledger_db(db_path)
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()
    with db_connection(path) as con:
        con.row_factory = sqlite3.Row
        cur = con.execute("""
            INSERT OR IGNORE INTO token_ledger (
                session_id, project_id, agent, model, prompt_tokens, completion_tokens,
                reasoning_tokens, total_tokens, loops_prevented, cost_estimated, created_at,
                event_id, usage_source, usage_status, pricing_source
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (str(session_id), str(project_id or "_global"), str(agent or "CODEX"),
              str(model or "unknown"), prompt, completion, reasoning, total, loops, cost,
              now_iso, event_id or None, usage_source, status,
              rates.get("source") if cost is not None else None))
        duplicate = cur.rowcount == 0
        if duplicate:
            row = con.execute("SELECT * FROM token_ledger WHERE session_id=? AND agent=? AND event_id=?",
                              (str(session_id), str(agent or "CODEX"), event_id)).fetchone()
        else:
            row = con.execute("SELECT * FROM token_ledger WHERE id=?", (cur.lastrowid,)).fetchone()
    return dict(row) | {"duplicate": duplicate, "cost_status": "configured_estimate" if row["pricing_source"] else "unavailable"}


def record_file_access(
    session_id: str,
    file_path: str,
    turn_id: str = "",
    db_path: Optional[Path] = None,
    threshold: int = LOOP_THRESHOLD,
) -> Dict[str, Any]:
    """
    Registra acesso a um arquivo e detecta se há loop de leituras consecutivas
    sem modificação. Retorna aviso anti-loop se ultrapassar o limiar.
    """
    path = init_ledger_db(db_path)
    normalized_file = os.path.normcase(os.path.normpath(str(file_path).strip()))
    now_iso = dt.datetime.now(dt.timezone.utc).isoformat()

    with db_connection(path) as con:
        threshold = _token_count(threshold, "threshold")
        if not threshold:
            raise ValueError("threshold must be positive")
        # Only uninterrupted reads of the same path in this session form a streak.
        previous = con.execute("SELECT file_path, has_writes, read_count FROM file_access_log WHERE session_id=? ORDER BY id DESC LIMIT 1", (str(session_id),)).fetchone()
        count = previous[2] + 1 if previous and previous[0] == normalized_file and not previous[1] else 1
        con.execute("""
            INSERT INTO file_access_log (session_id, file_path, turn_id, has_writes, created_at, read_count, is_loop)
            VALUES (?, ?, ?, 0, ?, ?, ?)
        """, (str(session_id), normalized_file, str(turn_id), now_iso, count, int(count >= threshold)))

        is_loop = count >= threshold
        warning = ""
        if is_loop:
            fname = Path(normalized_file).name
            warning = (
                f"[CERBERUS ANTI-LOOP]: O arquivo '{fname}' foi lido {count} vezes nesta "
                f"sessão sem alterações. Evite re-leituras desnecessárias; consolide os dados."
            )

    return {
        "session_id": session_id,
        "file_path": normalized_file,
        "read_count": count,
        "is_loop": is_loop,
        "warning": warning,
        "mode": "observational",
        "prevented": False,
    }


def mark_file_write(
    session_id: str,
    file_path: str,
    db_path: Optional[Path] = None,
) -> None:
    """Marca que um arquivo foi escrito/modificado, resetando a contagem de re-leitura."""
    path = init_ledger_db(db_path)
    normalized_file = os.path.normcase(os.path.normpath(str(file_path).strip()))
    with db_connection(path) as con:
        con.execute("""
            UPDATE file_access_log SET has_writes = 1
            WHERE session_id = ? AND file_path = ?
        """, (str(session_id), normalized_file))


def get_ledger_stats(db_path: Optional[Path] = None, days: int = 7) -> Dict[str, Any]:
    path = init_ledger_db(db_path)
    now = dt.datetime.now(dt.timezone.utc)
    today_start = dt.datetime(now.year, now.month, now.day, tzinfo=dt.timezone.utc).isoformat()
    period_start = (now - dt.timedelta(days=days)).isoformat()

    with db_connection(path) as con:
        con.row_factory = sqlite3.Row

        row_today = con.execute("""
            SELECT 
                SUM(prompt_tokens) as prompt,
                SUM(completion_tokens) as completion,
                SUM(reasoning_tokens) as reasoning,
                SUM(total_tokens) as total,
                COALESCE(SUM(loops_prevented), 0) as loops,
                CASE WHEN COUNT(*) = COUNT(pricing_source) THEN SUM(cost_estimated) END as cost,
                COUNT(*) as count,
                SUM(CASE WHEN usage_status = 'complete' THEN 1 ELSE 0 END) as complete_count
            FROM token_ledger WHERE created_at >= ?
        """, (today_start,)).fetchone()

        row_period = con.execute("""
            SELECT 
                SUM(prompt_tokens) as prompt,
                SUM(completion_tokens) as completion,
                SUM(reasoning_tokens) as reasoning,
                SUM(total_tokens) as total,
                COALESCE(SUM(loops_prevented), 0) as loops,
                CASE WHEN COUNT(*) = COUNT(pricing_source) THEN SUM(cost_estimated) END as cost,
                COUNT(*) as count,
                SUM(CASE WHEN usage_status = 'complete' THEN 1 ELSE 0 END) as complete_count
            FROM token_ledger WHERE created_at >= ?
        """, (period_start,)).fetchone()

        by_model = []
        for r in con.execute("""
            SELECT model, 
                   SUM(total_tokens) as total,
                   SUM(reasoning_tokens) as reasoning,
                   CASE WHEN COUNT(*) = COUNT(pricing_source) THEN SUM(cost_estimated) END as cost,
                   COUNT(*) as calls
            FROM token_ledger WHERE created_at >= ?
            GROUP BY model ORDER BY total DESC
        """, (period_start,)).fetchall():
            by_model.append({
                "model": r["model"],
                "total_tokens": r["total"],
                "reasoning_tokens": r["reasoning"],
                "cost_estimated": round(r["cost"], 4) if r["cost"] is not None else None,
                "calls": r["calls"]
            })

        by_project = []
        for r in con.execute("""
            SELECT project_id, 
                   SUM(total_tokens) as total,
                   SUM(loops_prevented) as loops,
                   COUNT(*) as calls
            FROM token_ledger WHERE created_at >= ?
            GROUP BY project_id ORDER BY total DESC
        """, (period_start,)).fetchall():
            by_project.append({
                "project_id": r["project_id"],
                "total_tokens": r["total"],
                "loops_prevented": r["loops"],
                "calls": r["calls"]
            })

        recent_sessions = []
        for r in con.execute("""
            SELECT session_id, project_id, agent, model,
                   prompt_tokens, completion_tokens, reasoning_tokens,
                   total_tokens, loops_prevented, CASE WHEN pricing_source IS NOT NULL THEN cost_estimated END as cost_estimated, created_at,
                   usage_source, usage_status, event_id, pricing_source
            FROM token_ledger WHERE created_at >= ? ORDER BY id DESC LIMIT 25
        """, (period_start,)).fetchall():
            recent_sessions.append(dict(r))

        loops_detected = con.execute("SELECT COUNT(*) FROM file_access_log WHERE is_loop=1 AND created_at>=?", (period_start,)).fetchone()[0]
        recent_loops = []
        for r in con.execute("""
            SELECT session_id, file_path, read_count as repeats, created_at as last_seen
            FROM file_access_log WHERE is_loop = 1 AND created_at >= ?
            ORDER BY id DESC LIMIT 10
        """, (period_start,)).fetchall():
            recent_loops.append({
                "session_id": r["session_id"],
                "file_path": r["file_path"],
                "repeats": r["repeats"],
                "last_seen": r["last_seen"]
            })

    return {
        "today": dict(row_today) if row_today else {},
        "period_days": days,
        "period": dict(row_period) if row_period else {},
        "by_model": by_model,
        "by_project": by_project,
        "recent_sessions": recent_sessions,
        "recent_loops": recent_loops,
        "loops_detected": loops_detected,
        "anti_loop_mode": "observational_unwired",
        "cost_status": "configured_estimate" if row_period["cost"] is not None else "unavailable",
        "usage_status": ("complete" if row_period["complete_count"] == row_period["count"] else "partial") if row_period["count"] else "unavailable",
    }
