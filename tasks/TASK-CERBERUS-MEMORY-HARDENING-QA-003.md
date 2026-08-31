TASK-ID:
CERBERUS-MEMORY-HARDENING-QA-003

PROJECT:
Dev Maniac's Cerberus Memory Intelligence

ROLE:
Independent Senior QA Engineer
+
Memory Safety Auditor
+
MCP Protocol Reviewer

CANONICAL ROOT:
C:\DevManiacs\DM-Cerebro

SOURCE:
TASK-CERBERUS-MEMORY-AUTOMATION-HARDENING-002
REPORT-HARDENING-002.md

MISSION:

Perform a STRICT READ-ONLY independent QA of HARDENING-002.

Do NOT implement fixes.
Do NOT commit.
Do NOT push.

Verify independently:

- agents cannot write directly to canonical memory
- all automatic captures land in isolated candidate inbox
- candidate lifecycle is enforced
- promote without --apply is preview-only
- promote with --apply is explicit and auditable
- quarantined secret candidates cannot be promoted
- secret redaction is safe
- duplicate/overlapping roots are eliminated
- rebuild is deterministic
- deleted files are pruned correctly
- global CLI works from arbitrary CWD
- doctor/inbox/review/promote/reject behave correctly
- MCP protocol is valid
- MCP stdout contains no debug/log noise
- project isolation holds
- no arbitrary filesystem/shell capability exists
- installer/config integrations remain intact
- no unrelated drift

Run the full test suite and add adversarial tests if needed.

FINAL REPORT:

HARDENING_QA:
APPROVED / NEEDS_FIXES

CANONICAL_WRITE_PROTECTION:
PASS / FAIL

CANDIDATE_INBOX:
PASS / FAIL

PROMOTION_GATE:
PASS / FAIL

SECRET_QUARANTINE:
PASS / FAIL

ROOT_DEDUP:
PASS / FAIL

INDEX_DETERMINISM:
PASS / FAIL

CLI_GLOBAL:
PASS / FAIL

MCP_PROTOCOL:
PASS / FAIL

PROJECT_ISOLATION:
PASS / FAIL

FILESYSTEM_SAFETY:
PASS / FAIL

TESTS:
[...]

BLOCKERS:
NONE / list

HIGH:
NONE / list

MEDIUM:
NONE / list

READY_FOR_COMMIT:
YES / NO

NO IMPLEMENTATION
NO COMMIT
NO PUSH
