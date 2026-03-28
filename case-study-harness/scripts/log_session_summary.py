#!/usr/bin/env python3
"""Log session summaries detected by the Stop hook.

Reads hook JSON from stdin and appends a session_summary entry to
data/session-summaries.jsonl.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
LOG_FILE: str = "session-summaries.jsonl"

MAX_LENGTH: int = 500


def truncate(text: str, max_length: int = MAX_LENGTH) -> str:
    """Truncate text to a maximum length with an ellipsis suffix.

    Args:
        text: The string to truncate.
        max_length: Maximum allowed length.

    Returns:
        The original string if within limits, or a truncated version with "...".
    """
    if len(text) <= max_length:
        return text
    return text[: max_length - 3] + "..."


def build_entry(description: str) -> dict[str, Any]:
    """Construct a session_summary JSONL entry.

    Args:
        description: High-level summary of work performed.

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "session_summary",
        "source": "hook",
        "description": description,
        "observations": "",
        "token_usage": None,
    }


def main() -> None:
    """Read Stop hook JSON from stdin and log a session summary."""
    try:
        payload: dict[str, Any] = json.loads(sys.stdin.read())

        last_message: str = payload.get("last_assistant_message", "")
        description = truncate(last_message)
        entry = build_entry(description)

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR / LOG_FILE, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    except Exception:
        pass


if __name__ == "__main__":
    main()
