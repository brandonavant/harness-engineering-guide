#!/usr/bin/env python3
# noinspection PyUnresolvedReferences
"""Write a manual observation entry to the case study harness log.

Accepts a category, user description, and context summary as positional
arguments. Constructs a JSONL entry conforming to the ``manual`` event
schema and appends it to ``data/manual-observations.jsonl``.

Usage:
    python3 write_manual_entry.py <category> <user_description> <context_summary>

Args:
    category: One of ``successful_pattern``, ``human_override``,
        ``context_architecture``, ``friction``, ``other``.
    user_description: The observation as described by the user.
    context_summary: Agent-generated context from the conversation.
"""

import json
import os
import sys
from datetime import UTC, datetime
from pathlib import Path

VALID_CATEGORIES: frozenset[str] = frozenset(
    {
        "successful_pattern",
        "human_override",
        "context_architecture",
        "friction",
        "other",
    }
)

DATA_DIR: Path = Path(__file__).resolve().parent.parent.parent.parent.parent / "data"
LOG_FILE: str = "manual-observations.jsonl"


def build_entry(category: str, user_description: str, context_summary: str) -> dict[str, str]:
    """Construct a manual observation JSONL entry.

    Args:
        category: The observation category.
        user_description: The observation as described by the user.
        context_summary: Agent-generated context from the conversation.

    Returns:
        A dictionary ready for JSON serialization.
    """
    return {
        "timestamp": datetime.now(UTC).isoformat(),
        "event_type": "manual",
        "source": "skill",
        "category": category,
        "user_description": user_description,
        "context_summary": context_summary,
    }


def main() -> int:
    """Parse arguments, validate, and write the JSONL entry.

    Returns:
        0 on success, 1 on validation or I/O failure.
    """
    if len(sys.argv) != 4:
        print(
            f"Usage: {sys.argv[0]} <category> <user_description> <context_summary>",
            file=sys.stderr,
        )
        return 1

    category: str = sys.argv[1]
    user_description: str = sys.argv[2]
    context_summary: str = sys.argv[3]

    if category not in VALID_CATEGORIES:
        sorted_cats = ", ".join(sorted(VALID_CATEGORIES))
        print(
            f"ERROR: Invalid category '{category}'. Must be one of: {sorted_cats}",
            file=sys.stderr,
        )
        return 1

    entry = build_entry(category, user_description, context_summary)

    os.makedirs(DATA_DIR, exist_ok=True)
    with open(DATA_DIR / LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

    print(f"Logged manual observation: category={category}, timestamp={entry['timestamp']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
