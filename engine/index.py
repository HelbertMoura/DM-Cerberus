"""
Cerberus Memory Intelligence - SQLite FTS5 Persistent Storage & Index Engine
Propriedade Intelectual: Dev Maniac's Systems (Helbert Moura)
"""

import os
import sqlite3
import hashlib
import json
import re
from pathlib import Path
from contextlib import contextmanager
from typing import List, Dict, Any, Optional, Tuple, Generator
from engine.models import MemoryItem, SearchResult, SourceType, MemoryStatus, AuthorityLevel
from engine.parser import parse_markdown_file
from engine.capture import redact_secrets

SENSITIVE_FILE_FAMILY = re.compile(
    r"(?:^|[-_.])(?:env(?:ironment)?|tokens?|secrets?|credentials?|private[-_]?keys?)(?:[-_.]|$)",
    re.IGNORECASE,
)


def is_sensitive_filename(name: str) -> bool:
    folded = name.casefold()
    return folded in {"id_rsa", "id_ed25519"} or bool(SENSITIVE_FILE_FAMILY.search(folded))


def validate_root(root: Path, allowed_roots: List[Path]) -> Path:
    """Resolve an existing root and require it to stay inside an explicit allowlist."""
    resolved = Path(root).resolve(strict=True)
    allowed = [Path(value).resolve(strict=True) for value in allowed_roots]
    if not any(resolved == boundary or boundary in resolved.parents for boundary in allowed):
        raise ValueError(f"Root is outside allowed roots: {resolved}")
    return resolved


def normalize_roots(root_paths: List[Path]) -> List[Path]:
    """Return existing, resolved, non-overlapping roots in deterministic order."""
    resolved = sorted({Path(root).resolve() for root in root_paths if Path(root).exists()}, key=lambda p: (len(p.parts), str(p).casefold()))
    kept: List[Path] = []
    for candidate in resolved:
        if any(candidate == parent or parent in candidate.parents for parent in kept):
            continue
        kept.append(candidate)
    return kept


class SQLiteMemoryIndex:
    def __init__(self, db_path: Optional[Path] = None):
        if db_path is None:
            # Default to C:\DevManiacs\DM-Cerebro\.cerberus\index.db
            base_dir = Path(__file__).resolve().parent.parent
            cerberus_dir = base_dir / ".cerberus"
            cerberus_dir.mkdir(parents=True, exist_ok=True)
            self.db_path = cerberus_dir / "index.db"
        else:
            self.db_path = Path(db_path)
            self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self._init_db()

    @contextmanager
    def _get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA journal_mode = WAL;")
        con.execute("PRAGMA busy_timeout = 5000;")
        con.execute("PRAGMA synchronous = NORMAL;")
        try:
            yield con
        finally:
            con.close()

    def _init_db(self):
        with self._get_connection() as con:
            con.execute("""
            CREATE TABLE IF NOT EXISTS file_meta (
                file_path TEXT PRIMARY KEY,
                mtime REAL,
                sha256 TEXT,
                indexed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            """)

            con.execute("""
            CREATE TABLE IF NOT EXISTS documents (
                memory_id TEXT PRIMARY KEY,
                project_id TEXT,
                source_path TEXT,
                source_type TEXT,
                title TEXT,
                authority_level INTEGER,
                tags TEXT,
                snippet TEXT,
                full_text TEXT,
                updated_at TEXT,
                status TEXT,
                metadata TEXT
            );
            """)

            con.execute("""
            CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts USING fts5(
                memory_id UNINDEXED,
                title,
                tags,
                snippet,
                full_text,
                content='documents',
                content_rowid='rowid',
                tokenize='porter unicode61'
            );
            """)

            # Triggers to keep FTS in sync
            con.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                INSERT INTO documents_fts(rowid, memory_id, title, tags, snippet, full_text)
                VALUES (new.rowid, new.memory_id, new.title, new.tags, new.snippet, new.full_text);
            END;
            """)

            con.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, rowid, memory_id, title, tags, snippet, full_text)
                VALUES('delete', old.rowid, old.memory_id, old.title, old.tags, old.snippet, old.full_text);
            END;
            """)

            con.execute("""
            CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                INSERT INTO documents_fts(documents_fts, rowid, memory_id, title, tags, snippet, full_text)
                VALUES('delete', old.rowid, old.memory_id, old.title, old.tags, old.snippet, old.full_text);
                INSERT INTO documents_fts(rowid, memory_id, title, tags, snippet, full_text)
                VALUES (new.rowid, new.memory_id, new.title, new.tags, new.snippet, new.full_text);
            END;
            """)
            con.commit()

    def rebuild(self, root_paths: List[Path]) -> Dict[str, Any]:
        """
        Wipes index tables and rebuilds from scratch.
        """
        with self._get_connection() as con:
            con.execute("DELETE FROM documents;")
            con.execute("DELETE FROM file_meta;")
            con.execute("INSERT INTO documents_fts(documents_fts) VALUES('rebuild');")
            con.commit()

        return self.index_roots(root_paths, force_reindex=True)

    def index_roots(self, root_paths: List[Path], force_reindex: bool = False) -> Dict[str, Any]:
        """
        Scans given root directories and indexes all markdown files.
        """
        stats = {"indexed_files": 0, "skipped_files": 0, "total_chunks": 0, "errors": 0}

        ignore_dirs = {".git", "node_modules", ".trash", ".wolf", "__pycache__", "venv", ".venv", ".cerberus"}

        normalized_roots = normalize_roots(root_paths)
        seen_files: set[str] = set()
        with self._get_connection() as con:
            for root in normalized_roots:
                if not root.exists():
                    continue

                for dirpath, dirnames, filenames in os.walk(root):
                    # Filter out ignored directories
                    safe_dirs = []
                    for dirname in sorted(dirnames):
                        child = Path(dirpath) / dirname
                        try:
                            resolved_child = child.resolve()
                        except OSError:
                            continue
                        if (dirname in ignore_dirs or dirname.startswith(".") or
                                is_sensitive_filename(dirname) or child.is_symlink()):
                            continue
                        if root != resolved_child and root not in resolved_child.parents:
                            continue
                        safe_dirs.append(dirname)
                    dirnames[:] = safe_dirs

                    for fname in sorted(filenames):
                        if not fname.lower().endswith(".md"):
                            continue

                        fpath = Path(dirpath) / fname
                        relative_parts = fpath.relative_to(root).parts[:-1]
                        if (is_sensitive_filename(fname) or
                                any(is_sensitive_filename(part) for part in relative_parts) or
                                fpath.is_symlink()):
                            continue
                        try:
                            resolved_file = fpath.resolve()
                        except OSError:
                            continue
                        if root != resolved_file and root not in resolved_file.parents:
                            continue
                        absolute_path = str(resolved_file)
                        seen_files.add(absolute_path)
                        try:
                            mtime = fpath.stat().st_mtime
                        except Exception:
                            continue

                        # Check if file changed
                        if not force_reindex:
                            cur = con.execute("SELECT mtime, sha256 FROM file_meta WHERE file_path = ?", (str(fpath),))
                            row = cur.fetchone()
                            if row and abs(row[0] - mtime) < 0.001:
                                stats["skipped_files"] += 1
                                continue

                        try:
                            content_bytes = fpath.read_bytes()
                            file_hash = hashlib.sha256(content_bytes).hexdigest()
                        except Exception:
                            stats["errors"] += 1
                            continue

                        decoded = content_bytes.decode("utf-8", errors="replace")
                        _, secret_findings = redact_secrets(decoded)
                        if secret_findings:
                            secret_key = hashlib.sha256(absolute_path.casefold().encode("utf-8")).hexdigest()[:16]
                            con.execute("DELETE FROM documents WHERE memory_id LIKE ?", (f"{secret_key}::%",))
                            con.execute("DELETE FROM file_meta WHERE file_path = ?", (absolute_path,))
                            stats["errors"] += 1
                            continue
                        file_key = hashlib.sha256(absolute_path.casefold().encode("utf-8")).hexdigest()[:16]
                        con.execute("DELETE FROM documents WHERE memory_id LIKE ?", (f"{file_key}::%",))
                        parsed_items = parse_markdown_file(fpath, root)
                        if parsed_items:
                            for item in parsed_items:
                                item.memory_id = f"{file_key}::{item.memory_id}"
                                con.execute("""
                                INSERT OR REPLACE INTO documents 
                                (memory_id, project_id, source_path, source_type, title, authority_level, tags, snippet, full_text, updated_at, status, metadata)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                                """, (
                                    item.memory_id,
                                    item.project_id,
                                    item.source_path,
                                    item.source_type.value if isinstance(item.source_type, SourceType) else str(item.source_type),
                                    item.title,
                                    item.authority_level,
                                    json.dumps(item.tags, ensure_ascii=False),
                                    item.snippet,
                                    item.full_text,
                                    item.updated_at,
                                    item.status.value if isinstance(item.status, MemoryStatus) else str(item.status),
                                    json.dumps(item.metadata, ensure_ascii=False)
                                ))
                                stats["total_chunks"] += 1

                            con.execute("INSERT OR REPLACE INTO file_meta (file_path, mtime, sha256) VALUES (?, ?, ?)",
                                        (str(fpath), mtime, file_hash))
                            stats["indexed_files"] += 1

            for (tracked_path,) in con.execute("SELECT file_path FROM file_meta").fetchall():
                tracked = Path(tracked_path)
                in_scope = any(root == tracked or root in tracked.parents for root in normalized_roots)
                if in_scope and str(tracked.resolve()) not in seen_files:
                    stale_key = hashlib.sha256(str(tracked.resolve()).casefold().encode("utf-8")).hexdigest()[:16]
                    con.execute("DELETE FROM documents WHERE memory_id LIKE ?", (f"{stale_key}::%",))
                    con.execute("DELETE FROM file_meta WHERE file_path = ?", (tracked_path,))

            con.commit()
            stats["total_chunks"] = con.execute("SELECT count(*) FROM documents").fetchone()[0]

        return stats

    def search(
        self,
        query: str,
        project_id: Optional[str] = None,
        source_types: Optional[List[str]] = None,
        limit: int = 10,
        include_global: bool = True,
        min_authority: int = 0
    ) -> List[SearchResult]:
        """
        Executes an FTS5 search with BM25 ranking and authority score boosting.
        """
        clean_query = query.strip().replace("'", " ").replace('"', " ").replace(":", " ").replace("-", " ")
        terms = [t for t in clean_query.split() if len(t) > 1]
        if not terms:
            return []

        # Construct FTS MATCH expression: prefix matching on terms (e.g. 'sefaz*' OR 'rateio*')
        fts_query = " OR ".join([f'"{t}"*' for t in terms])

        where_clauses = ["documents_fts MATCH ?"]
        params: List[Any] = [fts_query]

        # Project filtering
        if project_id:
            if include_global:
                where_clauses.append("(d.project_id = ? OR d.project_id = '_global')")
                params.append(project_id)
            else:
                where_clauses.append("d.project_id = ?")
                params.append(project_id)

        # Source type filtering
        if source_types:
            placeholders = ",".join(["?"] * len(source_types))
            where_clauses.append(f"d.source_type IN ({placeholders})")
            params.extend(source_types)

        # Authority threshold
        if min_authority > 0:
            where_clauses.append("d.authority_level >= ?")
            params.append(min_authority)

        where_sql = " AND ".join(where_clauses)

        sql = f"""
        SELECT 
            d.memory_id,
            d.project_id,
            d.source_path,
            d.source_type,
            d.title,
            d.authority_level,
            d.tags,
            d.snippet,
            d.full_text,
            d.updated_at,
            d.status,
            d.metadata,
            bm25(documents_fts, 5.0, 3.0, 1.5, 1.0) AS bm25_rank,
            snippet(documents_fts, 3, '<b>', '</b>', '...', 32) AS highlighted_snippet
        FROM documents_fts
        JOIN documents d ON documents_fts.rowid = d.rowid
        WHERE {where_sql}
        ORDER BY bm25_rank ASC
        LIMIT ?;
        """
        params.append(limit * 2)  # fetch extra for re-ranking

        results: List[SearchResult] = []
        with self._get_connection() as con:
            cur = con.execute(sql, params)
            for row in cur.fetchall():
                try:
                    tags = json.loads(row[6]) if row[6] else []
                except Exception:
                    tags = []
                try:
                    meta = json.loads(row[11]) if row[11] else {}
                except Exception:
                    meta = {}

                item = MemoryItem(
                    memory_id=row[0],
                    project_id=row[1],
                    source_path=row[2],
                    source_type=SourceType(row[3]) if row[3] in [s.value for s in SourceType] else SourceType.UNKNOWN,
                    title=row[4],
                    authority_level=row[5],
                    tags=tags,
                    snippet=row[7],
                    full_text=row[8],
                    updated_at=row[9],
                    status=MemoryStatus(row[10]) if row[10] in [s.value for s in MemoryStatus] else MemoryStatus.ACTIVE,
                    metadata=meta
                )

                # In SQLite FTS5 bm25(), lower values are more relevant
                raw_bm25 = row[12]
                lexical_score = max(0.1, 10.0 / (1.0 + max(0.0, raw_bm25)))
                authority_boost = 1.0 + (item.authority_level / 100.0)
                final_score = lexical_score * authority_boost

                highlight = row[13] if row[13] else item.snippet

                results.append(SearchResult(
                    item=item,
                    lexical_score=lexical_score,
                    authority_boost=authority_boost,
                    final_score=final_score,
                    matched_snippets=[highlight]
                ))

        # Re-sort by final combined score descending
        results.sort(key=lambda x: x.final_score, reverse=True)
        return results[:limit]

    def get_stats(self) -> Dict[str, Any]:
        with self._get_connection() as con:
            total_docs = con.execute("SELECT count(*) FROM documents;").fetchone()[0]
            total_files = con.execute("SELECT count(*) FROM file_meta;").fetchone()[0]
            projects = [r[0] for r in con.execute("SELECT DISTINCT project_id FROM documents;").fetchall()]
            types = {r[0]: r[1] for r in con.execute("SELECT source_type, count(*) FROM documents GROUP BY source_type;").fetchall()}

        return {
            "total_files": total_files,
            "total_documents": total_docs,
            "indexed_projects": projects,
            "types_breakdown": types,
            "db_path": str(self.db_path)
        }
