#!/usr/bin/env python3
"""Log tool activity captured by the PostToolUse hook.

Reads hook JSON from stdin and appends a tool_use entry to
data/tool-uses.jsonl. This general-purpose logger fires on every
successful tool invocation, creating an activity trail for synthesis.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
LOG_FILE: str = "tool-uses.jsonl"

MAX_SUMMARY_LENGTH: int = 200


def truncate(text: str, max_length: int = MAX_SUMMARY_LENGTH) -> str:
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


def extract_summary(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Derive a compact summary string from the tool name and input.

    Args:
        tool_name: The Claude Code tool that was invoked.
        tool_input: The tool_input dict from the hook payload.

    Returns:
        A brief human-readable description of what the tool did.
    """
    if tool_name == "Bash":
        command = tool_input.get("command", "")
        return truncate(f"Running: {command}")
    if tool_name == "Read":
        return truncate(f"Reading {tool_input.get('file_path', '')}")
    if tool_name == "Edit":
        return truncate(f"Editing {tool_input.get('file_path', '')}")
    if tool_name == "Write":
        return truncate(f"Writing {tool_input.get('file_path', '')}")
    if tool_name == "Glob":
        return truncate(f"Glob: {tool_input.get('pattern', '')}")
    if tool_name == "Grep":
        return truncate(f"Grep: {tool_input.get('pattern', '')}")
    if tool_name == "WebFetch":
        return truncate(f"Fetching {tool_input.get('url', '')}")
    if tool_name == "Agent":
        return truncate(f"Subagent: {tool_input.get('description', '')}")
    return tool_name


def build_entry(
    session_id: str, tool_name: str, tool_summary: str
) -> dict[str, Any]:
    """Construct a tool_use JSONL entry.

    Args:
        session_id: The session this tool use belongs to.
        tool_name: The tool that was invoked.
        tool_summary: Brief description of what the tool did.

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "tool_use",
        "source": "hook",
        "session_id": session_id,
        "tool_name": tool_name,
        "tool_summary": tool_summary,
    }


def main() -> None:
    """Read PostToolUse hook JSON from stdin and log tool activity."""
    try:
        payload: dict[str, Any] = json.loads(sys.stdin.read())

        session_id: str = payload.get("session_id", "")
        tool_name: str = payload.get("tool_name", "")
        tool_input: dict[str, Any] = payload.get("tool_input", {})

        tool_summary = extract_summary(tool_name, tool_input)
        entry = build_entry(session_id, tool_name, tool_summary)

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR / LOG_FILE, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    except (OSError, TypeError, ValueError):
        pass


if __name__ == "__main__":
    main()
