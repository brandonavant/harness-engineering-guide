#!/usr/bin/env python3
"""Log session end events captured by the SessionEnd hook.

Reads hook JSON from stdin and appends a session_end entry to
data/session-ends.jsonl. The SessionEnd hook fires when a session
terminates (exit, /clear, resume, logout).
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
LOG_FILE: str = "session-ends.jsonl"


def build_entry(session_id: str, reason: str) -> dict[str, Any]:
    """Construct a session_end JSONL entry.

    Args:
        session_id: The session that ended.
        reason: Why the session ended (e.g., prompt_input_exit, clear, logout).

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "session_end",
        "source": "hook",
        "session_id": session_id,
        "reason": reason,
        "token_usage": None,
    }


def main() -> None:
    """Read SessionEnd hook JSON from stdin and log the session end."""
    try:
        payload: dict[str, Any] = json.loads(sys.stdin.read())

        session_id: str = payload.get("session_id", "")
        reason: str = payload.get("reason", "")
        entry = build_entry(session_id, reason)

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR / LOG_FILE, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    except Exception:
        pass


if __name__ == "__main__":
    main()
