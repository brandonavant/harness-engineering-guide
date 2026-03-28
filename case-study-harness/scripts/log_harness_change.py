#!/usr/bin/env python3
"""Log harness file changes detected by the PostToolUse hook.

Reads hook JSON from stdin, checks if the changed file is a harness file,
and appends a harness_change entry to data/harness-changes.jsonl.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
LOG_FILE: str = "harness-changes.jsonl"

HARNESS_PREFIXES: tuple[str, ...] = (".claude/",)
HARNESS_FILES: tuple[str, ...] = ("CLAUDE.md",)

TOOL_ACTION_MAP: dict[str, str] = {
    "Edit": "modified",
    "Write": "created",
}


def is_harness_file(relative_path: str) -> bool:
    """Check whether a repo-relative path is a harness file.

    Args:
        relative_path: File path relative to the repository root.

    Returns:
        True if the path is under a harness prefix or matches a harness filename.
    """
    for prefix in HARNESS_PREFIXES:
        if relative_path.startswith(prefix):
            return True
    return relative_path in HARNESS_FILES


def normalize_path(absolute_path: str, cwd: str) -> str:
    """Convert an absolute file path to a repo-relative path.

    Args:
        absolute_path: The absolute path from tool_input.
        cwd: The repository root directory from the hook payload.

    Returns:
        A path relative to the repository root.
    """
    return os.path.relpath(absolute_path, cwd)


def build_entry(relative_path: str, action: str, tool_name: str) -> dict[str, Any]:
    """Construct a harness_change JSONL entry.

    Args:
        relative_path: File path relative to the repository root.
        action: One of "created", "modified", "deleted".
        tool_name: The Claude Code tool that triggered the change.

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "harness_change",
        "source": "hook",
        "file_path": relative_path,
        "action": action,
        "summary": f"File {action} via {tool_name} tool",
        "commit_sha": None,
        "commit_msg": None,
    }


def main() -> None:
    """Read PostToolUse hook JSON from stdin and log harness file changes."""
    try:
        payload: dict[str, Any] = json.loads(sys.stdin.read())

        tool_name: str = payload.get("tool_name", "")
        tool_input: dict[str, Any] = payload.get("tool_input", {})
        cwd: str = payload.get("cwd", "")
        file_path: str = tool_input.get("file_path", "")

        if not file_path or not cwd:
            return

        relative_path = normalize_path(file_path, cwd)

        if not is_harness_file(relative_path):
            return

        action = TOOL_ACTION_MAP.get(tool_name, "modified")
        entry = build_entry(relative_path, action, tool_name)

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR / LOG_FILE, "a") as f:
            f.write(json.dumps(entry, default=str) + "\n")

    except Exception:
        pass


if __name__ == "__main__":
    main()
