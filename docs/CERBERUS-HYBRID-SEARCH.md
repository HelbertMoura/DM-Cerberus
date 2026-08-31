# Cerberus Hybrid Search

Phase P4 adds deterministic hybrid retrieval without native extensions or
heavy machine-learning dependencies. Markdown remains the source of truth;
both FTS5 and vector tables are derived indexes in the existing SQLite file.

## Architecture

The retrieval path has four components:

1. `SQLiteMemoryIndex.search()` supplies the lexical BM25 ranking, including
   the existing authority boost and project isolation rules.
2. `EmbeddingProvider` defines the extension point for embedding backends.
   The default `HashingDenseEmbeddingProvider` hashes normalized word and
   character-trigram features into a fixed 256-dimensional dense vector and
   applies L2 normalization. Optional ONNX or FastEmbed providers can implement
   the same interface without changing retrieval or persistence.
3. `VectorStore` persists normalized vectors as little-endian float32 blobs and
   performs bounded cosine top-K search in Python. Project filtering happens in
   SQL before similarity calculation.
4. `HybridSearchEngine` combines lexical and semantic ranks with Reciprocal
   Rank Fusion. It lazily backfills vectors and uses content/provider
   fingerprints to update only new or changed documents and prune deleted IDs.

No filesystem paths, shell commands, network calls, or external model downloads
are exposed by this subsystem.

## Reciprocal Rank Fusion

For document `d`, with one-based ranks, the default score is:

```text
RRF(d) = w_lexical / (60 + rank_lexical(d))
       + w_semantic / (60 + rank_semantic(d))
```

A missing rank contributes zero. Both weights default to `1.0`. Results sort by
descending RRF score and then ascending `doc_id`, producing deterministic ties.

## SQLite schema

```sql
CREATE TABLE cerberus_vectors (
    doc_id TEXT PRIMARY KEY,
    project_id TEXT NOT NULL,
    dimension INTEGER NOT NULL,
    vector_blob BLOB NOT NULL,
    updated_at REAL NOT NULL
);
```

`vector_blob` contains exactly `dimension * 4` bytes encoded with
`struct.pack("<...f")`. `cerberus_vector_meta` is an auxiliary fingerprint
table used to invalidate stale vectors without changing the required vector
schema. `idx_cerberus_vectors_project` supports pre-similarity project pruning.

## Python API

```python
service.search(
    query="cofre certificado",
    project_id="canteirohub",
    mode="hybrid",       # hybrid | lexical | semantic
    limit=20,
)
```

Unknown modes raise `ValueError`. Python/MCP project searches include `_global`
by the existing service default and never include another project. Callers can
set `include_global=False`; the HTTP project filter does so for strict results.
Serialized results include `search_mode`, `lexical_score`, `semantic_score`,
`rrf_score`, `lexical_rank`, `semantic_rank`, and `final_score`.

## HTTP API

```text
GET /api/search?q=<query>&project=<slug>&mode=<hybrid|lexical|semantic>
```

`q` is required. `mode` defaults to `hybrid`; an invalid value returns HTTP
400. The response echoes `query`, `project_id`, and `mode` with up to 20
results. The Inspector exposes the same three modes in its search selector.

## MCP contract

`cerberus_search_memory` accepts:

- `query` — required string;
- `project_id` — optional project slug;
- `mode` — optional enum `hybrid`, `lexical`, or `semantic`;
- `limit` — optional integer, default 5.

Invalid types, unknown arguments, and values outside the mode enum fail with
JSON-RPC error `-32602` before tool execution.
