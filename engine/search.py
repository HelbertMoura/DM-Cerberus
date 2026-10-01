"""Hybrid BM25/vector search with deterministic Reciprocal Rank Fusion."""

from __future__ import annotations

import hashlib
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional

from engine.embeddings import (
    EmbeddingProvider,
    HashingDenseEmbeddingProvider,
    VectorStore,
)
from engine.index import SQLiteMemoryIndex
from engine.models import MemoryItem, MemoryStatus, SearchResult


VALID_SEARCH_MODES = {"hybrid", "lexical", "semantic"}


@dataclass(frozen=True)
class FusedRank:
    doc_id: str
    score: float
    lexical_rank: Optional[int]
    semantic_rank: Optional[int]


def reciprocal_rank_fusion(lexical_ids: Iterable[str],
                           semantic_ids: Iterable[str], *,
                           priority_ids: Optional[Iterable[str]] = None,
                           k: int = 60,
                           lexical_weight: float = 1.0,
                           semantic_weight: float = 1.0,
                           priority_weight: float = 3.0) -> List[FusedRank]:
    if k < 0 or lexical_weight < 0 or semantic_weight < 0 or priority_weight < 0:
        raise ValueError("RRF parameters must be non-negative")
    lexical = {doc_id: rank for rank, doc_id in enumerate(lexical_ids, 1)}
    semantic = {doc_id: rank for rank, doc_id in enumerate(semantic_ids, 1)}
    priority = {doc_id: rank for rank, doc_id in enumerate(priority_ids or [], 1)}
    fused = []
    for doc_id in lexical.keys() | semantic.keys() | priority.keys():
        lexical_rank = lexical.get(doc_id)
        semantic_rank = semantic.get(doc_id)
        score = 0.0
        priority_rank = priority.get(doc_id)
        if priority_rank is not None:
            score += priority_weight / (k + priority_rank)
        if lexical_rank is not None:
            score += lexical_weight / (k + lexical_rank)
        if semantic_rank is not None:
            score += semantic_weight / (k + semantic_rank)
        fused.append(FusedRank(doc_id, score, lexical_rank, semantic_rank))
    return sorted(fused, key=lambda entry: (-entry.score, entry.doc_id))


class HybridSearchEngine:
    def __init__(self, index: SQLiteMemoryIndex, *,
                 provider: Optional[EmbeddingProvider] = None,
                 vector_store: Optional[VectorStore] = None,
                 rrf_k: int = 60,
                 lexical_weight: float = 1.0,
                 semantic_weight: float = 1.0,
                 priority_weight: float = 3.0) -> None:
        self.index = index
        self.provider = provider or HashingDenseEmbeddingProvider()
        self.vector_store = vector_store or VectorStore(index.db_path)
        self.rrf_k = rrf_k
        self.lexical_weight = lexical_weight
        self.semantic_weight = semantic_weight
        self.priority_weight = priority_weight

    @staticmethod
    def _embedding_text(item: MemoryItem) -> str:
        return "\n".join((item.title, " ".join(item.tags),
                          item.snippet, item.full_text))

    def ensure_indexed(self) -> None:
        # Keep obsolete/draft documents available to administrative inspection,
        # but remove their derived vectors from operational retrieval.
        items = [item for item in self.index.all_items() if item.status == MemoryStatus.ACTIVE]
        stored_fingerprints = self.vector_store.fingerprints()
        current = {}
        for item in items:
            text = self._embedding_text(item)
            fingerprint = hashlib.sha256(
                (self.provider.__class__.__qualname__ + ":"
                 + str(self.provider.dimension) + ":" + text).encode("utf-8")
            ).hexdigest()
            current[item.memory_id] = (item, text, fingerprint)
        changed = [value for doc_id, value in current.items()
                   if stored_fingerprints.get(doc_id) != value[2]]
        self.vector_store.upsert_many(
            (item.memory_id, item.project_id,
             self.provider.embed(text), fingerprint)
            for item, text, fingerprint in changed
        )
        self.vector_store.delete_missing(set(current))

    def _semantic(self, query: str, project_id: Optional[str], *,
                  source_types: Optional[List[str]], limit: int,
                  include_global: bool, min_authority: int) -> List[SearchResult]:
        self.ensure_indexed()
        matches = self.vector_store.search(
            self.provider.embed(query), project_id=project_id,
            include_global=include_global, limit=max(limit * 8, 100),
        )
        items = self.index.get_items_by_ids([match.doc_id for match in matches])
        by_id = {item.memory_id: item for item in items}
        results = []
        for rank, match in enumerate(matches, 1):
            item = by_id.get(match.doc_id)
            if item is None or item.status != MemoryStatus.ACTIVE or item.authority_level < min_authority:
                continue
            if source_types and str(item.source_type.value) not in source_types:
                continue
            results.append(SearchResult(
                item=item, lexical_score=0.0, semantic_score=match.score,
                authority_boost=1.0 + item.authority_level / 100.0,
                final_score=match.score, semantic_rank=rank,
                search_mode="semantic", matched_snippets=[item.snippet],
            ))
            if len(results) >= limit:
                break
        return results

    def search(self, query: str, project_id: Optional[str] = None, *,
               source_types: Optional[List[str]] = None,
               limit: int = 20, mode: str = "hybrid",
               include_global: bool = True,
               min_authority: int = 0) -> List[SearchResult]:
        mode = (mode or "hybrid").casefold()
        if mode not in VALID_SEARCH_MODES:
            raise ValueError("mode must be hybrid, lexical, or semantic")
        if limit <= 0:
            return []
        lexical = self.index.search(
            query, project_id=project_id, source_types=source_types,
            limit=max(limit * 4, limit), include_global=include_global,
            min_authority=min_authority,
        )
        if mode == "lexical":
            for rank, result in enumerate(lexical[:limit], 1):
                result.lexical_rank = rank
                result.search_mode = "lexical"
            return lexical[:limit]
        semantic = self._semantic(
            query, project_id, source_types=source_types,
            limit=max(limit * 4, limit), include_global=include_global,
            min_authority=min_authority,
        )
        if mode == "semantic":
            return semantic[:limit]
        priority_ids = [result.item.memory_id for result in lexical if result.priority_rank]
        fused = reciprocal_rank_fusion(
            [result.item.memory_id for result in lexical if not result.priority_rank],
            [result.item.memory_id for result in semantic],
            priority_ids=priority_ids,
            k=self.rrf_k, lexical_weight=self.lexical_weight,
            semantic_weight=self.semantic_weight,
            priority_weight=self.priority_weight,
        )
        priority_rank_by_id = {doc_id: rank for rank, doc_id in enumerate(priority_ids, 1)}
        lexical_by_id: Dict[str, SearchResult] = {
            result.item.memory_id: result for result in lexical
        }
        semantic_by_id: Dict[str, SearchResult] = {
            result.item.memory_id: result for result in semantic
        }
        results = []
        for entry in fused[:limit]:
            base = lexical_by_id.get(entry.doc_id) or semantic_by_id[entry.doc_id]
            semantic_result = semantic_by_id.get(entry.doc_id)
            results.append(SearchResult(
                item=base.item,
                lexical_score=(lexical_by_id.get(entry.doc_id).lexical_score
                               if entry.doc_id in lexical_by_id else 0.0),
                semantic_score=(semantic_result.semantic_score
                                if semantic_result else 0.0),
                authority_boost=base.authority_boost,
                final_score=entry.score,
                rrf_score=entry.score,
                lexical_rank=entry.lexical_rank,
                semantic_rank=entry.semantic_rank,
                priority_rank=priority_rank_by_id.get(entry.doc_id),
                search_mode="hybrid",
                matched_snippets=base.matched_snippets,
            ))
        return results
