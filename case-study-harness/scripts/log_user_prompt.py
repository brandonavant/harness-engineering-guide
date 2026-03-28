#!/usr/bin/env python3
"""Log user prompts captured by the UserPromptSubmit hook.

Reads hook JSON from stdin and appends a user_prompt entry to
data/user-prompts.jsonl. The UserPromptSubmit hook fires when
the user submits a prompt.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
LOG_FILE: str = "user-prompts.jsonl"

MAX_LENGTH: int = 2000


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


def build_entry(session_id: str, prompt: str) -> dict[str, Any]:
    """Construct a user_prompt JSONL entry.

    Args:
        session_id: The session this prompt belongs to.
        prompt: The user's prompt text.

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "user_prompt",
        "source": "hook",
        "session_id": session_id,
        "prompt": prompt,
    }


def main() -> None:
    """Read UserPromptSubmit hook JSON from stdin and log the user prompt."""
    try:
        payload: dict[str, Any] = json.loads(sys.stdin.read())

        session_id: str = payload.get("session_id", "")
        prompt: str = payload.get("prompt", "")
        prompt = truncate(prompt)
        entry = build_entry(session_id, prompt)

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR / LOG_FILE, "a") as file:
            file.write(json.dumps(entry, default=str) + "\n")

    except (OSError, TypeError, ValueError):
        pass


if __name__ == "__main__":
    main()
