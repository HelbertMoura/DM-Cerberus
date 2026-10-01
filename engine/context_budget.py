"""Character budgets for complete MCP context results; token costs are estimates."""
from __future__ import annotations

import json
from dataclasses import replace

from engine.response_budget import redact_text
from engine.models import ContextPack
from engine.session_delivery import FINGERPRINT_METADATA, memory_fingerprint

MIN_CONTEXT_TOKENS = 256
MAX_CONTEXT_TOKENS = 1500
GROUPS = ("mandatory_rules", "relevant_decisions", "relevant_learnings",
          "relevant_architecture", "recent_handoff")


def context_pack_result(pack: ContextPack) -> dict:
    """Use the same JSON representation as the MCP text content envelope."""
    result = {"markdown": pack.to_markdown(), "token_estimate": pack.token_estimate,
              "budget_chars": pack.budget_chars, "truncated": pack.truncated}
    for _ in range(3):
        result["token_estimate"] = (len(json.dumps(result, ensure_ascii=False, indent=2)) + 3) // 4
    return result


def fit_context_pack(pack: ContextPack, max_tokens: int) -> ContextPack:
    if type(max_tokens) is not int or not MIN_CONTEXT_TOKENS <= max_tokens <= MAX_CONTEXT_TOKENS:
        raise ValueError("max_tokens must be an integer between 256 and 1500 (estimated budget)")
    budget = max_tokens * 4

    def safe(value: str, limit: int) -> str:
        text = redact_text(value)
        return text if len(text) <= limit else text[:limit - 1] + "…"

    bounded = replace(pack, project_id=safe(pack.project_id, 80), role=safe(pack.role, 40),
                      task_summary=safe(pack.task_summary, 200), token_estimate=0,
                      budget_chars=budget, **{group: [] for group in GROUPS})
    bounded.truncated = any(getattr(bounded, name) != getattr(pack, name)
                            for name in ("project_id", "role", "task_summary"))
    if len(json.dumps(context_pack_result(bounded), ensure_ascii=False, indent=2)) > budget:
        # JSON escaping can expand even short caller-supplied strings.
        bounded.project_id, bounded.role, bounded.task_summary = "projeto", "agente", ""
        bounded.truncated = True
    seen = set()
    for group in GROUPS:
        selected = getattr(bounded, group)
        for item in getattr(pack, group):
            if item.memory_id in seen:
                continue
            seen.add(item.memory_id)
            source = redact_text(item.source_path)
            entry = replace(item, title=safe(item.title, 160), snippet=safe(item.snippet, 350), source_path=source,
                            metadata={**item.metadata, FINGERPRINT_METADATA: memory_fingerprint(item)})
            selected.append(entry)
            if len(json.dumps(context_pack_result(bounded), ensure_ascii=False, indent=2)) > budget:
                selected.pop()
                bounded.truncated = True
            elif entry.title != item.title or entry.snippet != item.snippet or entry.source_path != item.source_path:
                bounded.truncated = True
    bounded.token_estimate = context_pack_result(bounded)["token_estimate"]
    return bounded
