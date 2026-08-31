"""Lightweight dense embeddings and SQLite float32 vector persistence."""

from __future__ import annotations

import hashlib
import heapq
import math
import re
import sqlite3
import struct
import time
from abc import ABC, abstractmethod
from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
from typing import Generator, Iterable, List, Optional, Sequence, Set


_TOKEN_RE = re.compile(r"\w+", re.UNICODE)


def _normalize(vector: Sequence[float]) -> List[float]:
    values = [float(value) for value in vector]
    if not values or not all(math.isfinite(value) for value in values):
        raise ValueError("vector must contain finite values")
    norm = math.sqrt(sum(value * value for value in values))
    if norm == 0.0:
        return values
    return [value / norm for value in values]


class EmbeddingProvider(ABC):
    """Extensible contract for local or optional external embedders."""

    @property
    @abstractmethod
    def dimension(self) -> int:
        raise NotImplementedError

    @abstractmethod
    def embed(self, text: str) -> List[float]:
        raise NotImplementedError

    def embed_batch(self, texts: Iterable[str]) -> List[List[float]]:
        return [self.embed(text) for text in texts]


class HashingDenseEmbeddingProvider(EmbeddingProvider):
    """Deterministic token/subword feature hashing into a dense unit vector."""

    def __init__(self, dimension: int = 256) -> None:
        if not isinstance(dimension, int) or dimension < 8:
            raise ValueError("dimension must be an integer >= 8")
        self._dimension = dimension

    @property
    def dimension(self) -> int:
        return self._dimension

    def _features(self, text: str) -> Iterable[tuple[str, float]]:
        for token in _TOKEN_RE.findall((text or "").casefold()):
            yield "tok:" + token, 1.0
            padded = "^" + token + "$"
            if len(padded) >= 3:
                for offset in range(len(padded) - 2):
                    yield "tri:" + padded[offset:offset + 3], 0.35

    def embed(self, text: str) -> List[float]:
        vector = [0.0] * self.dimension
        for feature, weight in self._features(text):
            digest = hashlib.blake2b(feature.encode("utf-8"), digest_size=8).digest()
            raw = int.from_bytes(digest, "little")
            index = raw % self.dimension
            vector[index] += weight if raw & (1 << 63) else -weight
        return _normalize(vector)


@dataclass(frozen=True)
class VectorMatch:
    doc_id: str
    project_id: str
    score: float


class VectorStore:
    """SQLite-backed float32 vector store with bounded cosine top-K search."""

    def __init__(self, db_path: Path) -> None:
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _connect(self) -> Generator[sqlite3.Connection, None, None]:
        con = sqlite3.connect(self.db_path)
        con.execute("PRAGMA journal_mode = WAL")
        con.execute("PRAGMA busy_timeout = 5000")
        try:
            yield con
            con.commit()
        except Exception:
            con.rollback()
            raise
        finally:
            con.close()

    def _init_db(self) -> None:
        with self._connect() as con:
            con.execute("""
                CREATE TABLE IF NOT EXISTS cerberus_vectors (
                    doc_id TEXT PRIMARY KEY,
                    project_id TEXT NOT NULL,
                    dimension INTEGER NOT NULL,
                    vector_blob BLOB NOT NULL,
                    updated_at REAL NOT NULL
                )
            """)
            con.execute("""
                CREATE INDEX IF NOT EXISTS idx_cerberus_vectors_project
                ON cerberus_vectors(project_id)
            """)
            con.execute("""
                CREATE TABLE IF NOT EXISTS cerberus_vector_meta (
                    doc_id TEXT PRIMARY KEY,
                    fingerprint TEXT NOT NULL,
                    FOREIGN KEY(doc_id) REFERENCES cerberus_vectors(doc_id)
                        ON DELETE CASCADE
                )
            """)

    @staticmethod
    def _pack(vector: Sequence[float]) -> tuple[int, bytes]:
        normalized = _normalize(vector)
        return len(normalized), struct.pack(f"<{len(normalized)}f", *normalized)

    @staticmethod
    def _unpack(dimension: int, blob: bytes) -> List[float]:
        expected = dimension * 4
        if dimension <= 0 or len(blob) != expected:
            raise ValueError("invalid vector blob or dimension")
        return list(struct.unpack(f"<{dimension}f", blob))

    def upsert(self, doc_id: str, project_id: str,
               vector: Sequence[float], fingerprint: Optional[str] = None) -> None:
        if not doc_id or not project_id:
            raise ValueError("doc_id and project_id are required")
        dimension, blob = self._pack(vector)
        with self._connect() as con:
            con.execute("""
                INSERT INTO cerberus_vectors
                    (doc_id, project_id, dimension, vector_blob, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    project_id=excluded.project_id,
                    dimension=excluded.dimension,
                    vector_blob=excluded.vector_blob,
                    updated_at=excluded.updated_at
            """, (doc_id, project_id, dimension, blob, time.time()))
            if fingerprint is not None:
                con.execute("""
                    INSERT INTO cerberus_vector_meta (doc_id, fingerprint)
                    VALUES (?, ?)
                    ON CONFLICT(doc_id) DO UPDATE SET
                        fingerprint=excluded.fingerprint
                """, (doc_id, fingerprint))

    def upsert_many(self, rows: Iterable[tuple]) -> int:
        packed = []
        metadata = []
        now = time.time()
        for row in rows:
            if len(row) not in {3, 4}:
                raise ValueError("vector row must have 3 or 4 fields")
            doc_id, project_id, vector = row[:3]
            fingerprint = row[3] if len(row) == 4 else None
            if not doc_id or not project_id:
                raise ValueError("doc_id and project_id are required")
            dimension, blob = self._pack(vector)
            packed.append((doc_id, project_id, dimension, blob, now))
            if fingerprint is not None:
                metadata.append((doc_id, fingerprint))
        if not packed:
            return 0
        with self._connect() as con:
            con.executemany("""
                INSERT INTO cerberus_vectors
                    (doc_id, project_id, dimension, vector_blob, updated_at)
                VALUES (?, ?, ?, ?, ?)
                ON CONFLICT(doc_id) DO UPDATE SET
                    project_id=excluded.project_id,
                    dimension=excluded.dimension,
                    vector_blob=excluded.vector_blob,
                    updated_at=excluded.updated_at
            """, packed)
            if metadata:
                con.executemany("""
                    INSERT INTO cerberus_vector_meta (doc_id, fingerprint)
                    VALUES (?, ?)
                    ON CONFLICT(doc_id) DO UPDATE SET
                        fingerprint=excluded.fingerprint
                """, metadata)
        return len(packed)

    def get(self, doc_id: str) -> Optional[List[float]]:
        with self._connect() as con:
            row = con.execute(
                "SELECT dimension, vector_blob FROM cerberus_vectors WHERE doc_id = ?",
                (doc_id,),
            ).fetchone()
        return None if row is None else self._unpack(row[0], row[1])

    def ids(self) -> Set[str]:
        with self._connect() as con:
            return {row[0] for row in con.execute(
                "SELECT doc_id FROM cerberus_vectors"
            ).fetchall()}

    def fingerprints(self) -> dict[str, str]:
        with self._connect() as con:
            return dict(con.execute(
                "SELECT doc_id, fingerprint FROM cerberus_vector_meta"
            ).fetchall())

    def delete_missing(self, valid_doc_ids: Set[str]) -> int:
        with self._connect() as con:
            existing = [row[0] for row in con.execute(
                "SELECT doc_id FROM cerberus_vectors"
            ).fetchall()]
            stale = [(doc_id,) for doc_id in existing if doc_id not in valid_doc_ids]
            if stale:
                con.executemany(
                    "DELETE FROM cerberus_vectors WHERE doc_id = ?", stale
                )
                con.executemany(
                    "DELETE FROM cerberus_vector_meta WHERE doc_id = ?", stale
                )
        return len(stale)

    def search(self, query_vector: Sequence[float], *,
               project_id: Optional[str] = None,
               include_global: bool = True,
               limit: int = 20) -> List[VectorMatch]:
        if limit <= 0:
            return []
        query = _normalize(query_vector)
        if not any(query):
            return []
        clauses = ["dimension = ?"]
        params: List[object] = [len(query)]
        if project_id:
            if include_global:
                clauses.append("project_id IN (?, '_global')")
            else:
                clauses.append("project_id = ?")
            params.append(project_id)
        sql = ("SELECT doc_id, project_id, dimension, vector_blob "
               "FROM cerberus_vectors WHERE " + " AND ".join(clauses)
               + " ORDER BY doc_id")
        candidates = []
        with self._connect() as con:
            for doc_id, candidate_project, dimension, blob in con.execute(sql, params):
                vector = self._unpack(dimension, blob)
                score = sum(left * right for left, right in zip(query, vector))
                candidates.append(VectorMatch(doc_id, candidate_project, score))
        top = heapq.nlargest(limit, candidates, key=lambda match: match.score)
        return sorted(top, key=lambda match: (-match.score, match.doc_id))
