#!/usr/bin/env python3
"""Seed a new project with template files from the Harness Engineering Guide.

Fetches the required template files from GitHub and copies them into the target
project directory, preserving the templates/ directory structure so that
CHEATSHEET.md references resolve correctly.

Usage:
    python3 init-project.py /path/to/my-project
    python3 init-project.py .                       # current directory
"""

import argparse
import sys
import urllib.error
import urllib.request
from pathlib import Path

REPO = "brandonavant/harness-engineering-guide"
BRANCH = "main"
BASE_URL = f"https://raw.githubusercontent.com/{REPO}/{BRANCH}"

# Every file under templates/ that should be seeded into the user's project.
TEMPLATE_FILES: list[str] = [
    # CLAUDE.md starter
    "templates/CLAUDE.md",
    # Documentation templates
    "templates/docs/README.md",
    "templates/docs/interview-summary-template.md",
    "templates/docs/prd-template.md",
    "templates/docs/architecture-template.md",
    "templates/docs/ux-spec-template.md",
    "templates/docs/brand-identity-template.md",
    # API contract
    "templates/contracts/README.md",
    "templates/contracts/openapi-stub.yaml",
    # Claude Code harness starters
    "templates/.claude/rules/example-backend.md",
    "templates/.claude/agents/agent-template.md",
    "templates/.claude/skills/design-enforcement/SKILL.md",
    "templates/.claude/skills/example-checklist/SKILL.md",
    "templates/.claude/hooks/README.md",
    # CI workflow
    "templates/.github/workflows/ci.yml",
    # Scripts
    "templates/scripts/integration-smoke-test.sh",
]


def fetch_file(relative_path: str) -> bytes:
    """Fetch a single file from the GitHub repository.

    Args:
        relative_path: Path relative to the repository root.

    Returns:
        The raw file content as bytes.

    Raises:
        SystemExit: If the file cannot be fetched.
    """
    url = f"{BASE_URL}/{relative_path}"
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            return response.read()
    except urllib.error.HTTPError as exc:
        print(f"  FAIL  {relative_path} (HTTP {exc.code})")
        raise SystemExit(1) from exc
    except urllib.error.URLError as exc:
        print(f"  FAIL  {relative_path} ({exc.reason})")
        raise SystemExit(1) from exc


def seed_project(target_dir: Path) -> None:
    """Fetch all template files and write them into the target directory.

    Args:
        target_dir: The root of the user's project.
    """
    if not target_dir.is_dir():
        print(f"Error: {target_dir} is not a directory.")
        raise SystemExit(1)

    print(f"\nSeeding templates into {target_dir.resolve()}\n")

    fetched = 0
    for relative_path in TEMPLATE_FILES:
        dest = target_dir / relative_path
        dest.parent.mkdir(parents=True, exist_ok=True)

        content = fetch_file(relative_path)
        dest.write_bytes(content)
        print(f"  OK    {relative_path}")
        fetched += 1

    print(f"\nDone. {fetched} files written to {target_dir / 'templates/'}")
    print(
        "\nNext step: open CHEATSHEET.md in the guide repo and follow Phase 1."
    )


def main() -> None:
    """Parse arguments and run the seeding process."""
    parser = argparse.ArgumentParser(
        description="Seed a project with Harness Engineering Guide templates.",
    )
    parser.add_argument(
        "target",
        type=Path,
        help="Path to the project directory to seed.",
    )
    args = parser.parse_args()
    seed_project(args.target)


if __name__ == "__main__":
    main()
