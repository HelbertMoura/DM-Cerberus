TASK-ID:
CERBERUS-MEMORY-AUTOMATION-HARDENING-002

PROJECT:
Dev Maniac's Cerberus Memory Intelligence

MODEL:
OpenAI Codex

ROLE:
Principal AI Infrastructure Engineer
+
MCP Integration Architect
+
Memory Safety Engineer
+
Windows Tooling Engineer
+
Adversarial QA Engineer

CANONICAL ROOT:
C:\DevManiacs\DM-Cerebro

RELATED PROJECT ROOT:
C:\DevManiacs\migra\dm-erp

CURRENT IMPLEMENTATION:
engine/
  models.py
  parser.py
  index.py
  retrieval.py
  capture.py
  installer.py
  mcp_server.py
  cli.py

MISSION:

Audit, harden and complete the Cerberus Memory Intelligence
automation so it is:

- safe
- idempotent
- agent-agnostic
- Windows-native
- usable from any terminal
- usable from MCP-capable agents
- automatically fed from approved operational artifacts
- resistant to canonical-memory contamination

DO NOT assume the previous "completed" report is correct.

Verify everything empirically.

==================================================
0 — CRITICAL GOVERNANCE CORRECTION
==================================================

Previous implementation introduced MCP write capabilities:

cerberus_capture_learning
cerberus_ingest_report

and may write directly into canonical Markdown memory.

This MUST be reviewed.

Canonical Cerberus Markdown is SOURCE OF TRUTH.

Agents must NOT be able to promote arbitrary observations directly
into canonical memory.

Introduce explicit lifecycle:

CAPTURED
→ CANDIDATE
→ VERIFIED
→ CANONICAL

Also support:

SUPERSEDED
REJECTED
ARCHIVED

Default automatic capture destination:

.cerberus/inbox/

or equivalent isolated candidate store.

Automatic capture MUST NOT directly mutate canonical:

MEMORY.md
DECISIONS.md
LEARNINGS.md
project canonical memories

unless an explicit safe promotion policy allows it.

==================================================
1 — DISCOVER CURRENT REAL STATE
==================================================

Before editing:

inspect:

git status
git diff
current branch
all engine files
all tests
all installer-created configuration
all .bak-cerberus backups

Inventory actual integrations.

Verify real paths for:

Claude Code
Codex
Cursor
OpenCode
Maestri
Gemini/Antigravity if applicable

Do not trust paths printed in previous reports.

Verify filesystem existence.

==================================================
2 — UNIVERSAL CLIENT STRATEGY
==================================================

Define support tiers.

TIER A:
MCP-native clients.

TIER B:
CLI-capable clients without MCP.

TIER C:
clients with lifecycle hooks.

Do NOT claim "works with every CLI" literally.

Instead guarantee:

Any environment capable of invoking a local command
can use the Cerberus CLI.

Any compatible MCP client can use Cerberus MCP.

==================================================
3 — CERBERUS GLOBAL CLI
==================================================

Ensure a robust global command exists:

cerberus

Commands:

cerberus status
cerberus doctor
cerberus search
cerberus context-pack
cerberus capture
cerberus ingest-report
cerberus inbox
cerberus review
cerberus promote
cerberus reject
cerberus index
cerberus index --rebuild
cerberus mcp

Must work from:

PowerShell
cmd.exe
Windows Terminal

and from arbitrary CWD.

No dependency on user manually setting PYTHONPATH.

==================================================
4 — PYTHON RUNTIME ROBUSTNESS
==================================================

Do not depend on whichever "python" happens to be first in PATH.

Determine a reliable runtime strategy.

Prefer one of:

dedicated .venv
Python launcher py.exe
documented absolute interpreter

Installer must verify:

Python version
SQLite FTS5 availability
required packages
UTF-8 behavior

Create:

cerberus doctor

which reports:

runtime
Python
FTS5
index
canonical roots
MCP config state
write permissions
candidate inbox
Git state

without exposing secrets.

==================================================
5 — INSTALLER IDEMPOTENCY
==================================================

installer.py must be safe to execute repeatedly.

Running:

cerberus install

twice must NOT:

duplicate MCP entries
destroy unrelated configs
duplicate PATH entries
overwrite user configuration
create endless backup files

Implement:

detect
merge
backup
validate
rollback

For every modified config:

backup BEFORE modification.

Preserve unrelated user fields byte/semantically where possible.

==================================================
6 — CLIENT ADAPTERS
==================================================

Implement/configure explicit adapters for clients that actually exist
on this machine.

At minimum audit:

Codex
Claude Code
Cursor
OpenCode

Also detect:

Gemini/Antigravity
Maestri

but do NOT invent integration formats.

If a client has no verified config schema:

report UNSUPPORTED/NEEDS_ADAPTER.

Never write guessed configuration.

==================================================
7 — MCP READ TOOLS
==================================================

Read tools may remain directly accessible:

cerberus_search_memory
cerberus_get_context_pack
cerberus_get_decisions
cerberus_get_learnings
cerberus_get_project_context
cerberus_get_stats

Review rebuild_index carefully.

If exposed via MCP, classify it as a maintenance mutation,
not ordinary read.

Prefer restricting it or making it local-admin only.

==================================================
8 — MCP WRITE SAFETY
==================================================

Change current write semantics.

cerberus_capture_learning

must create a CANDIDATE by default.

cerberus_ingest_report

must:

parse report
extract candidate knowledge
deduplicate
store provenance
create candidates

It must NOT silently promote directly to canonical Markdown.

Add explicit promotion tool only if governance allows it.

Preferred:

NO MCP promotion in this phase.

Promotion should happen through CLI/local operator:

cerberus review
cerberus promote <candidate_id>

==================================================
9 — CANDIDATE CONTRACT
==================================================

Each candidate requires:

candidate_id
project_id
type
title
summary/content
source
source_path if applicable
task_id
agent
created_at
confidence
authority_hint
fingerprint
status

Statuses:

CANDIDATE
VERIFIED
CANONICAL
REJECTED
SUPERSEDED

==================================================
10 — PROVENANCE
==================================================

Every candidate must answer:

who generated it
from which task/report
from which project
when
from what evidence

No provenance:

no promotion.

==================================================
11 — DEDUPLICATION
==================================================

Current title/content dedupe must be independently tested.

Handle:

exact duplicate
same idea differently worded
same decision with new evidence
contradictory decision
superseding ADR

Never silently merge contradictory information.

Create conflict state where appropriate.

==================================================
12 — AUTOMATIC FEEDING
==================================================

Automate MEMORY INPUT from high-quality artifacts.

Preferred sources:

Task reports
QA reports
RCA reports
approved handovers
approved ADRs
Orchestrator lifecycle events

Do NOT capture raw chats automatically.

==================================================
13 — FILE WATCHER / EVENT INGEST
==================================================

Design lightweight automatic ingestion.

Possible mechanisms:

filesystem watcher
scheduled incremental scan
AI Orchestrator event adapter

Prefer simple/reliable mechanism.

Detect newly created or modified:

REPORT*.md
HANDOVER.md
ADR*.md
QA reports
RCA reports

On detection:

extract candidate knowledge
→ inbox

Do NOT canonicalize automatically.

==================================================
14 — ORCHESTRATOR INTEGRATION
==================================================

Integrate loosely with AI Orchestrator.

Desired future flow:

TASK_CREATED
→ Cerberus context pack

REPORT_ACCEPTED
→ Cerberus candidate extraction

QA_APPROVED
→ candidate authority increases

PROJECT_CLOSED
→ final context snapshot

Do NOT modify Orchestrator state machine.

Use adapter/event boundary.

==================================================
15 — AUTOMATIC CONTEXT AT SESSION START
==================================================

Design practical ways for agents to obtain context automatically.

Preferred behavior:

Agent opens project
→ detects project_id/CWD
→ calls cerberus_get_context_pack
→ receives relevant context

Do NOT force giant context into every session.

Target compact context.

==================================================
16 — PROJECT AUTO-DETECTION
==================================================

Implement robust project resolution using:

cwd
known roots
project metadata
explicit --project override

Explicit project always wins.

Never accidentally resolve one project as another.

==================================================
17 — CONTEXT PACK QUALITY
==================================================

Pack should rank:

MANDATORY
HIGH_RELEVANCE
SUPPLEMENTAL

Authority must matter.

Example:

PO decision
must outrank
recent agent observation.

Use role-aware retrieval:

CTO
PM
DEVELOPER
QA
STAFF
SECURITY

==================================================
18 — INDEX CONSISTENCY
==================================================

Validate discrepancy in previous report:

initial rebuild said:
185 files / 794 chunks

status later said:
165 files / 533 chunks

Determine why.

Potential causes:

duplicate roots
nested root overlap
filters
incremental pruning
bug

Index metrics must be deterministic.

Same canonical corpus + same config
must produce stable counts.

==================================================
19 — OVERLAPPING ROOTS
==================================================

Previous roots included:

dm-erp/docs/brain

AND

dm-erp/docs

which may cause duplicate indexing.

Detect and normalize overlapping roots.

A file must never be indexed twice.

==================================================
20 — AUTHORITY BOOST VALIDATION
==================================================

Test that authority weighting improves ranking
without completely overpowering relevance.

A totally unrelated governance document must NOT rank above a directly
relevant lower-authority project document merely because it has high
authority.

==================================================
21 — SECURITY
==================================================

MCP/CLI must NEVER expose arbitrary:

read_file
write_file
shell
exec
filesystem traversal

Canonical roots must be allowlisted.

Block:

..
UNC escape
symlink/junction escape
environment file access

Do not index:

.env
credentials
secrets
private keys
token files
Git internals
.cerberus internal DB

==================================================
22 — AUTOMATIC SECRET FILTER
==================================================

Add ingestion filtering for likely secrets.

At minimum detect/reject/redact:

API tokens
password-like assignments
private keys
authorization headers
connection strings

Candidate with suspected secret:

quarantine
do not canonicalize
do not index sensitive value

==================================================
23 — MCP PROTOCOL VALIDATION
==================================================

Do not merely call mcp_server.py "MCP".

Verify against actual MCP protocol expectations.

Test initialization
tools/list
tools/call
error responses
stdio framing
stdout cleanliness

IMPORTANT:

MCP stdio server must NEVER print logs/debug text to stdout.

Logs go stderr.

==================================================
24 — INTEGRATION TESTS
==================================================

Create isolated integration tests that launch the MCP server as a real
subprocess.

Verify:

initialize
list tools
search call
context-pack call
bad tool
bad args
server shutdown

No hanging process.

==================================================
25 — CONFIGURATION TESTS
==================================================

For each supported client:

install into temporary fake config

verify merge

run installer twice

verify same result

uninstall

verify original config restored/preserved

Do NOT rely only on real user config for tests.

==================================================
26 — WINDOWS TESTING
==================================================

Test paths containing:

spaces
accented PT-BR characters
long paths where feasible

Test from:

repo root
C:\
another project directory

CLI must resolve correctly.

==================================================
27 — FAILURE MODES
==================================================

Test:

index missing
index corrupt
candidate store corrupt
canonical root unavailable
SQLite locked
MCP client disconnect
Ctrl+C
invalid UTF-8 document
huge markdown
malformed YAML frontmatter

Fail safe.

==================================================
28 — PERFORMANCE
==================================================

Benchmark actual corpus.

Report:

full rebuild time
incremental scan time
search p50
search p95
context pack p50/p95
DB size

Do not invent values.

==================================================
29 — OBSERVABILITY
==================================================

cerberus status / doctor should expose:

index age
file count
chunk count
projects
candidate count
conflicts
quarantined items
last ingestion
MCP health where measurable

==================================================
30 — GIT SAFETY
==================================================

.cerberus/index.db
temporary files
candidate runtime locks

should not accidentally enter Git.

Determine which candidate/provenance artifacts SHOULD be versioned.

Do not assume all runtime state belongs in Git.

==================================================
31 — REQUIRED DOCUMENTATION
==================================================

Update/create:

docs/CERBERUS-MEMORY-ARCHITECTURE.md
docs/CERBERUS-MCP-INTEGRATION.md
docs/CERBERUS-AUTO-CAPTURE.md
docs/CERBERUS-CLIENT-SUPPORT.md
docs/CERBERUS-OPERATIONS.md
docs/CERBERUS-SECURITY.md

==================================================
32 — TEST MATRIX
==================================================

Minimum categories:

INDEX
SEARCH
PROJECT ISOLATION
AUTHORITY
CONTEXT PACK
CAPTURE
DEDUP
PROVENANCE
SECRET FILTER
CANDIDATE LIFECYCLE
INSTALLER
CLIENT CONFIG
MCP PROTOCOL
WINDOWS PATHS
REBUILD
CORRUPTION
FAILSAFE

==================================================
33 — DO NOT COMMIT YET
==================================================

No commit.
No push.

First return implementation + audit report.

==================================================
FINAL REPORT
==================================================

CERBERUS_AUTOMATION:
PASS / NEEDS_FIXES

CANONICAL_MEMORY_SAFE:
YES / NO

DIRECT_AGENT_CANONICAL_WRITE:
DISABLED / ENABLED

CANDIDATE_PIPELINE:
PASS / FAIL

AUTO_CAPTURE:
PASS / FAIL

AUTO_PROMOTION:
DISABLED / ENABLED + justification

PROVENANCE:
PASS / FAIL

DEDUP:
PASS / FAIL

SECRET_FILTER:
PASS / FAIL

PROJECT_ISOLATION:
PASS / FAIL

CLI_GLOBAL:
PASS / FAIL

POWERSHELL:
PASS / FAIL

CMD:
PASS / FAIL

ARBITRARY_CWD:
PASS / FAIL

PROJECT_AUTO_DETECTION:
PASS / FAIL

MCP_PROTOCOL:
PASS / FAIL

MCP_SUBPROCESS_TEST:
PASS / FAIL

CODEX:
SUPPORTED / FAILED / NOT_CONFIGURED

CLAUDE:
SUPPORTED / FAILED / NOT_CONFIGURED

CURSOR:
SUPPORTED / FAILED / NOT_CONFIGURED

OPENCODE:
SUPPORTED / FAILED / NOT_CONFIGURED

GEMINI_ANTIGRAVITY:
SUPPORTED / NEEDS_ADAPTER / NOT_PRESENT

MAESTRI:
SUPPORTED / NEEDS_ADAPTER / NOT_PRESENT

INSTALLER_IDEMPOTENT:
PASS / FAIL

INSTALLER_ROLLBACK:
PASS / FAIL

INDEX_DETERMINISTIC:
PASS / FAIL

OVERLAPPING_ROOTS:
RESOLVED / FOUND

REBUILD:
[...]

INCREMENTAL:
[...]

SEARCH_P50:
[...]

SEARCH_P95:
[...]

CONTEXT_PACK_P95:
[...]

TESTS:
[...]

BLOCKERS:
NONE / list

HIGH:
NONE / list

MEDIUM:
NONE / list

PO_DECISIONS_REQUIRED:
[...]

READY_FOR_CANONICAL_USE:
YES / NO

READY_FOR_AUTO_CAPTURE:
YES / NO

READY_FOR_MULTI_AGENT_ROLLOUT:
YES / NO

NO COMMIT
NO PUSH
