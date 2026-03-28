#!/usr/bin/env python3
"""Log per-turn summaries captured by the Stop hook.

Reads hook JSON from stdin and appends a turn_summary entry to
data/turn-summaries.jsonl. The Stop hook fires after each Claude
response (turn), not at session end.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
LOG_FILE: str = "turn-summaries.jsonl"

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


def build_entry(session_id: str, description: str) -> dict[str, Any]:
    """Construct a turn_summary JSONL entry.

    Args:
        session_id: The session this turn belongs to.
        description: High-level summary of what Claude responded.

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "turn_summary",
        "source": "hook",
        "session_id": session_id,
        "description": description,
    }


def main() -> None:
    """Read Stop hook JSON from stdin and log a turn summary."""
    try:
        payload: dict[str, Any] = json.loads(sys.stdin.read())

        session_id: str = payload.get("session_id", "")
        last_message: str = payload.get("last_assistant_message", "")
        description = truncate(last_message)
        entry = build_entry(session_id, description)

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR / LOG_FILE, "a") as file:
            file.write(json.dumps(entry, default=str) + "\n")

    except (OSError, TypeError, ValueError):
        pass


if __name__ == "__main__":
    main()
