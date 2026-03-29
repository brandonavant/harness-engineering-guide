#!/usr/bin/env python3
"""Read, validate, merge, and summarize all case study observation data.

Reads all five JSONL log files from the case study harness data directory,
validates each entry, merges them into a single chronological list, computes
summary statistics, and outputs a structured JSON report to stdout.

Usage:
    python3 read_observations.py [--data-dir PATH]

Args:
    --data-dir: Optional path to the data directory. Defaults to
        ``case-study-harness/data/`` relative to the project root.
"""

import json
import sys
from collections import Counter
from pathlib import Path
from typing import Any

LOG_FILES: dict[str, str] = {
    "harness-changes.jsonl": "harness_change",
    "friction-events.jsonl": "friction",
    "turn-summaries.jsonl": "turn_summary",
    "session-ends.jsonl": "session_end",
    "manual-observations.jsonl": "manual",
    "user-prompts.jsonl": "user_prompt",
    "tool-uses.jsonl": "tool_use",
}

DEFAULT_DATA_DIR: Path = (
    Path(__file__).resolve().parent.parent.parent.parent.parent
    / "case-study-harness"
    / "data"
)


def parse_args() -> Path:
    """Parse command-line arguments and return the data directory path.

    Returns:
        The resolved Path to the data directory.
    """
    args = sys.argv[1:]
    if "--data-dir" in args:
        idx = args.index("--data-dir")
        if idx + 1 >= len(args):
            print("ERROR: --data-dir requires a path argument.", file=sys.stderr)
            sys.exit(1)
        return Path(args[idx + 1]).resolve()
    return DEFAULT_DATA_DIR


def read_jsonl(filepath: Path) -> list[dict[str, Any]]:
    """Read a JSONL file and return a list of parsed entries.

    Skips malformed lines with a warning to stderr. Returns an empty list
    if the file does not exist.

    Args:
        filepath: Path to the JSONL file.

    Returns:
        A list of parsed JSON objects.
    """
    if not filepath.exists():
        print(f"WARNING: File not found, skipping: {filepath}", file=sys.stderr)
        return []

    entries: list[dict[str, Any]] = []
    with open(filepath) as f:
        for line_num, line in enumerate(f, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                entry = json.loads(stripped)
                entries.append(entry)
            except json.JSONDecodeError as exc:
                print(
                    f"WARNING: Malformed JSON at {filepath.name}:{line_num}: {exc}",
                    file=sys.stderr,
                )
    return entries


def compute_summary(entries: list[dict[str, Any]]) -> dict[str, Any]:
    """Compute summary statistics from merged observation entries.

    Args:
        entries: A list of parsed JSONL entries, sorted by timestamp.

    Returns:
        A dictionary of summary statistics.
    """
    total: int = len(entries)
    by_event_type: Counter[str] = Counter()
    by_manual_category: Counter[str] = Counter()
    friction_by_tool: Counter[str] = Counter()
    harness_change_by_file: Counter[str] = Counter()
    tool_use_by_tool: Counter[str] = Counter()
    session_ids: set[str] = set()

    for entry in entries:
        event_type = entry.get("event_type", "unknown")
        by_event_type[event_type] += 1

        if event_type == "manual":
            category = entry.get("category", "unknown")
            by_manual_category[category] += 1

        if event_type == "friction":
            tool = entry.get("tool_name", "unknown")
            friction_by_tool[tool] += 1

        if event_type == "harness_change":
            file_path = entry.get("file_path", "unknown")
            harness_change_by_file[file_path] += 1

        if event_type == "tool_use":
            tool = entry.get("tool_name", "unknown")
            tool_use_by_tool[tool] += 1

        sid = entry.get("session_id")
        if sid:
            session_ids.add(sid)

    timestamps = [e.get("timestamp", "") for e in entries if e.get("timestamp")]
    date_range: dict[str, str | None] = {
        "earliest": min(timestamps) if timestamps else None,
        "latest": max(timestamps) if timestamps else None,
    }

    return {
        "total_entries": total,
        "by_event_type": dict(by_event_type.most_common()),
        "by_manual_category": dict(by_manual_category.most_common()),
        "session_count": len(session_ids),
        "date_range": date_range,
        "friction_by_tool": dict(friction_by_tool.most_common()),
        "harness_change_by_file": dict(harness_change_by_file.most_common()),
        "tool_use_by_tool": dict(tool_use_by_tool.most_common()),
    }


def main() -> int:
    """Read all JSONL files, merge, summarize, and output JSON to stdout.

    Returns:
        0 on success, 1 if the data directory does not exist.
    """
    data_dir = parse_args()

    if not data_dir.exists():
        print(
            f"ERROR: Data directory does not exist: {data_dir}",
            file=sys.stderr,
        )
        return 1

    all_entries: list[dict[str, Any]] = []
    for filename, expected_type in LOG_FILES.items():
        filepath = data_dir / filename
        entries = read_jsonl(filepath)
        for entry in entries:
            actual_type = entry.get("event_type")
            if actual_type != expected_type:
                print(
                    f"WARNING: Entry in {filename} has event_type '{actual_type}', "
                    f"expected '{expected_type}'. Including anyway.",
                    file=sys.stderr,
                )
        all_entries.extend(entries)

    all_entries.sort(key=lambda e: e.get("timestamp", ""))

    summary = compute_summary(all_entries)

    report: dict[str, Any] = {
        "summary": summary,
        "entries": all_entries,
    }

    json.dump(report, sys.stdout, indent=2, default=str)
    print()
    return 0


if __name__ == "__main__":
    sys.exit(main())
