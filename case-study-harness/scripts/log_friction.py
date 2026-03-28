#!/usr/bin/env python3
"""Log friction events detected by the PostToolUseFailure hook.

Reads hook JSON from stdin and appends a friction entry to
data/friction-events.jsonl.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
LOG_FILE: str = "friction-events.jsonl"

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


def extract_context(tool_input: dict[str, Any]) -> str:
    """Derive a brief context string from the tool input.

    Args:
        tool_input: The tool_input dict from the hook payload.

    Returns:
        A human-readable string describing what the agent was attempting.
    """
    if "command" in tool_input:
        return truncate(f"Running: {tool_input['command']}")
    if "file_path" in tool_input:
        return truncate(f"Operating on {tool_input['file_path']}")
    return truncate(json.dumps(tool_input, default=str))


def build_entry(tool_name: str, error_summary: str, context: str) -> dict[str, Any]:
    """Construct a friction JSONL entry.

    Args:
        tool_name: The tool that failed.
        error_summary: Condensed error message.
        context: What the agent was attempting.

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "friction",
        "source": "hook",
        "tool_name": tool_name,
        "error_summary": error_summary,
        "context": context,
    }


def main() -> None:
    """Read PostToolUseFailure hook JSON from stdin and log friction events."""
    try:
        payload: dict[str, Any] = json.loads(sys.stdin.read())

        tool_name: str = payload.get("tool_name", "unknown")
        error: str = payload.get("error", "")
        tool_input: dict[str, Any] = payload.get("tool_input", {})

        error_summary = truncate(error)
        context = extract_context(tool_input)
        entry = build_entry(tool_name, error_summary, context)

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR / LOG_FILE, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    except Exception:
        pass


if __name__ == "__main__":
    main()
