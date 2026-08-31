# Cerberus Memory Automation Hardening 002 Implementation Plan

> **For Codex:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Harden Cerberus so automated inputs create provenance-rich candidates, only an explicit local `promote --apply` mutates canonical memory, and indexing/integrations are deterministic and safe.

**Architecture:** Separate canonical Markdown from a filesystem-backed candidate inbox. Route MCP mutations exclusively through capture/ingestion services, keep promotion local to the CLI with preview-first semantics, normalize canonical roots before indexing, and enforce allowlists plus secret quarantine at every ingestion boundary.

**Tech Stack:** Python 3, stdlib dataclasses/argparse/sqlite3/pathlib/hashlib/json, SQLite FTS5, JSON-RPC 2.0 over stdio, unittest subprocess integration tests, Windows CMD/PowerShell launchers.

---

### Task 1: Candidate contract and safe store

**Files:** `engine/models.py`, `engine/capture.py`, `tests/test_candidate_pipeline.py`

1. Write failing tests for required provenance, stable fingerprints, CANDIDATE persistence, duplicate/conflict behavior, corruption fail-safe, and secret quarantine.
2. Run the focused tests and record expected failures.
3. Implement typed candidate models and atomic filesystem store under `.cerberus/inbox`.
4. Implement normalization, duplicate/conflict classification, and secret redaction/quarantine.
5. Re-run focused and baseline tests.

### Task 2: Preview-first promotion lifecycle

**Files:** `engine/capture.py`, `engine/cli.py`, `tests/test_candidate_pipeline.py`, `tests/test_cli_integration.py`

1. Write failing tests proving `promote <id>` never writes and displays a diff.
2. Write failing tests proving only `promote <id> --apply` writes allowlisted `LEARNINGS.md` or `DECISIONS.md` with complete provenance.
3. Test rejection, missing provenance, quarantined input, traversal, and repeat application.
4. Implement lifecycle transitions and atomic append behavior.
5. Re-run focused and regression tests.

### Task 3: MCP write safety and protocol compliance

**Files:** `engine/mcp_server.py`, `tests/test_mcp_protocol.py`

1. Write subprocess tests for initialize, tools/list, read calls, capture, report ingestion, bad tool/args, clean stdout, and shutdown.
2. Verify RED for direct canonical mutation and protocol gaps.
3. Route MCP capture/ingest into candidates only; expose no promotion tool.
4. Keep maintenance mutations explicitly classified/restricted and diagnostics on stderr.
5. Re-run subprocess tests with process timeouts.

### Task 4: Deterministic index and project resolution

**Files:** `engine/index.py`, `engine/parser.py`, `engine/retrieval.py`, `tests/test_index_hardening.py`

1. Write failing tests for nested-root normalization, one-file-one-index identity, stable rebuild counts, stale pruning, exclusions, symlink/junction escape, project override precedence, and authority/relevance balance.
2. Implement canonical path normalization and deterministic traversal.
3. Implement robust explicit/cwd/metadata/known-root project resolution.
4. Tune authority weighting without allowing irrelevant governance to dominate.
5. Re-run focused and full tests.

### Task 5: CLI, runtime doctor, auto-ingest, and Windows launchers

**Files:** `engine/cli.py`, `engine/auto_capture.py`, `bin/cerberus.cmd`, `bin/cerberus.ps1`, `tests/test_cli_integration.py`, `tests/test_windows_launchers.py`

1. Write failing tests for all commands, arbitrary CWD, spaces/accented paths, doctor checks, and incremental approved-artifact ingestion.
2. Implement compact status/doctor output without secrets.
3. Implement scheduled incremental scanning boundaries for approved artifact names only.
4. Harden launchers to use a verified interpreter without PYTHONPATH.
5. Re-run Windows integration tests.

### Task 6: Idempotent installer and verified adapters

**Files:** `engine/installer.py`, `tests/test_installer.py`

1. Write temporary-config tests for detect/merge/backup/validate/rollback/uninstall and double-install idempotency.
2. Encode only schemas empirically verified for present clients.
3. Mark unknown schemas `NEEDS_ADAPTER`; never guess or mutate them.
4. Re-run installer tests twice and compare bytes/semantics.

### Task 7: Documentation, performance, and final QA evidence

**Files:** required `docs/CERBERUS-*.md` files and `reports/REPORT-HARDENING-002.md`

1. Run the complete unit/integration matrix and security-focused tests.
2. Benchmark rebuild, incremental scan, search p50/p95, context-pack p95, and DB size on the actual corpus.
3. Audit real client state and launcher behavior from repository root, `C:\`, and another project directory.
4. Update required architecture, MCP, auto-capture, client support, operations, and security documentation.
5. Perform independent adversarial review, resolve critical/high findings, and record residual risks.
6. Audit `git status`/`git diff`; do not commit or push.

