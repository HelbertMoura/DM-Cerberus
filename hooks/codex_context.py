"""Codex SessionStart/UserPromptSubmit command hook; always advisory."""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def main() -> int:
    try:
        for stream in (sys.stdin, sys.stdout):
            if hasattr(stream, "reconfigure"):
                stream.reconfigure(encoding="utf-8")
        from engine.agent_hooks import handle_context
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            return 0
        # Dedicated override for isolated checks; normal hooks use this installation.
        root = Path(os.environ.get("CERBERUS_HOOK_ROOT") or ROOT)
        print(json.dumps(handle_context(payload, root), ensure_ascii=False))
    except Exception:
        print("{}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
