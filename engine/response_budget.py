"""Bound complete JSON memory payloads while retaining their list/dict shapes."""
from __future__ import annotations

import json
import re

from engine.capture import redact_secrets

DEFAULT_MAX_CHARS = 1200
MIN_MAX_CHARS = 512
MAX_MAX_CHARS = 6000
IDENTITY_FIELDS = {"memory_id", "source_path"}
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(?<!\w)['\"]?(?:password|passwd|pwd|secret|private[_-]?key|"
    r"api[_-]?(?:key|token)|access[_-]?token|auth[_-]?token|client[_-]?secret|secret[_-]?key|token)"
    r"['\"]?\s*[:=]\s*(?:\"(?:\\[\s\S]|[^\"\\])*(?:\"|\\?\Z)|"
    r"'(?:\\[\s\S]|[^'\\])*(?:'|\\?\Z)|[^\s,;&]+)"
)
_PRIVATE_KEY = re.compile(
    r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----[\s\S]*?"
    r"(?:-----END (?:RSA |EC |OPENSSH )?PRIVATE KEY-----|$)", re.I
)
_URL_CREDENTIALS = re.compile(r"(?i)([a-z][a-z0-9+.-]*://)[^/\s@]+:[^/\s@]+@")


def redact_text(value: str) -> str:
    """Redact quoted assignments and incomplete keys before any boundary cut."""
    safe = _PRIVATE_KEY.sub("[REDACTED]", value)
    safe = _SECRET_ASSIGNMENT.sub("[REDACTED]", safe)
    safe = _URL_CREDENTIALS.sub(r"\1[REDACTED]@", safe)
    return redact_secrets(safe)[0]


def json_text(value) -> str:
    """The exact serialization used inside the MCP text block."""
    return json.dumps(value, ensure_ascii=False, indent=2)


def validate_max_chars(value: int) -> int:
    if type(value) is not int or not MIN_MAX_CHARS <= value <= MAX_MAX_CHARS:
        raise ValueError("max_chars must be an integer between 512 and 6000")
    return value


def query_text(value: str) -> str:
    # Redact the complete argument before slicing across a possible secret.
    safe = redact_text(value)
    return "".join(char if ord(char) >= 32 and char != "\\" else " " for char in safe)[:1500]


def search_text(value: str) -> str:
    # Repeating the same OR term hundreds of times adds no retrieval value.
    return " ".join(dict.fromkeys(query_text(value).split()))


def bounded_response(payload, max_chars: int = DEFAULT_MAX_CHARS, *, preview=True):
    """Drop records/fields that cannot fit; never slice serialized JSON or IDs."""
    validate_max_chars(max_chars)
    changed = False

    def clean(value, key=""):
        nonlocal changed
        if isinstance(value, str):
            safe = value if key == "memory_id" else redact_text(value)
            limit = 160 if key == "title" else 240
            if key not in IDENTITY_FIELDS and preview and len(safe) > limit:
                safe = safe[:limit - 1] + "…"
            changed |= safe != value
            return safe
        if isinstance(value, list):
            return [clean(entry) for entry in value]
        if isinstance(value, dict):
            result = {}
            record_changed = changed
            for field, entry in value.items():
                if field == "metadata" or (preview and (field == "full_text" or
                        ("memory_id" in value and field in {"lexical_score", "semantic_score",
                         "rrf_score", "lexical_rank", "semantic_rank", "authority_boost"}))):
                    changed = True
                    continue
                result[field] = clean(entry, field)
            if "memory_id" in result and (changed != record_changed or
                    any(result.get(k) != value.get(k) for k in result)):
                result["truncated"] = True
            return result
        return value

    result = clean(payload)

    def signal():
        if isinstance(result, dict):
            result["truncated"] = True
        elif isinstance(result, list) and (not result or result[-1] != {"truncated": True}):
            result.append({"truncated": True})

    if changed:
        signal()

    def shrink(value):
        if isinstance(value, list):
            # Prefer dropping a complete result over damaging its identity.
            end = len(value) - (bool(value) and value[-1] == {"truncated": True})
            if end:
                value.pop(end - 1)
                return True
        elif isinstance(value, dict):
            nested = [(key, entry) for key, entry in value.items()
                      if isinstance(entry, (dict, list)) and entry]
            nested.sort(key=lambda pair: len(json_text(pair[1])), reverse=True)
            for key, entry in nested:
                if shrink(entry):
                    return True
            disposable = [key for key in value if key not in IDENTITY_FIELDS | {"truncated"}]
            if disposable:
                value.pop(max(disposable, key=lambda key: len(json_text({key: value[key]}))))
                return True
        return False

    while len(json_text(result)) > max_chars:
        signal()
        if not shrink(result):
            # A record with an oversized source/ID is omitted as a whole.
            result = {"truncated": True} if isinstance(payload, dict) else [{"truncated": True}]
            break
    return result
