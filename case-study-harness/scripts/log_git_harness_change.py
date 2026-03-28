#!/usr/bin/env python3
"""Log harness file changes detected by the Git post-commit hook.

Inspects the most recent commit for harness file changes and appends
harness_change entries to data/harness-changes.jsonl. Exits silently
when no harness files were changed.
"""

import json
import os
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

DATA_DIR: Path = Path(__file__).resolve().parent.parent / "data"
LOG_FILE: str = "harness-changes.jsonl"

HARNESS_PREFIXES: tuple[str, ...] = (".claude/",)
HARNESS_FILES: tuple[str, ...] = ("CLAUDE.md",)

GIT_STATUS_MAP: dict[str, str] = {
    "A": "created",
    "M": "modified",
    "D": "deleted",
    "R": "modified",
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


def get_changed_files() -> list[tuple[str, str]]:
    """Get the list of changed files in the most recent commit.

    Returns:
        A list of (status, filepath) tuples from git diff-tree.

    Raises:
        subprocess.CalledProcessError: If the git command fails.
    """
    result = subprocess.run(
        ["git", "diff-tree", "--no-commit-id", "--name-status", "-r", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    changes: list[tuple[str, str]] = []
    for line in result.stdout.strip().splitlines():
        parts = line.split("\t")
        if len(parts) < 2:
            continue
        status = parts[0][0]  # First char handles R100, C100, etc.
        file_path = parts[-1]  # Last element handles renames (old\tnew)
        changes.append((status, file_path))
    return changes


def get_commit_info() -> tuple[str, str]:
    """Get the SHA and message of the most recent commit.

    Returns:
        A tuple of (full_sha, first_line_of_commit_message).

    Raises:
        subprocess.CalledProcessError: If the git command fails.
    """
    sha_result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    msg_result = subprocess.run(
        ["git", "log", "-1", "--format=%s", "HEAD"],
        capture_output=True,
        text=True,
        check=True,
    )
    return sha_result.stdout.strip(), msg_result.stdout.strip()


def build_entry(
    file_path: str,
    action: str,
    commit_sha: str,
    commit_msg: str,
) -> dict[str, Any]:
    """Construct a harness_change JSONL entry for a git-detected change.

    Args:
        file_path: File path relative to the repository root.
        action: One of "created", "modified", "deleted".
        commit_sha: The full SHA of the commit.
        commit_msg: The first line of the commit message.

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "harness_change",
        "source": "git_hook",
        "file_path": file_path,
        "action": action,
        "summary": f"File {action} in commit {commit_sha[:8]}",
        "commit_sha": commit_sha,
        "commit_msg": commit_msg,
    }


def main() -> None:
    """Inspect the latest commit and log any harness file changes."""
    try:
        changes = get_changed_files()
        harness_changes = [
            (status, fp) for status, fp in changes if is_harness_file(fp)
        ]

        if not harness_changes:
            return

        commit_sha, commit_msg = get_commit_info()

        os.makedirs(DATA_DIR, exist_ok=True)
        with open(DATA_DIR / LOG_FILE, "a") as f:
            for status, file_path in harness_changes:
                action = GIT_STATUS_MAP.get(status, "modified")
                entry = build_entry(file_path, action, commit_sha, commit_msg)
                f.write(json.dumps(entry, default=str) + "\n")

    except subprocess.CalledProcessError:
        pass
    except Exception:
        print("case-study-harness: unexpected error in git hook logger", file=sys.stderr)


if __name__ == "__main__":
    main()
