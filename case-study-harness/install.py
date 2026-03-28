#!/usr/bin/env python3
"""Install the case-study meta-harness into a target repository.

Seeds observation infrastructure (rules, skills, hooks, Git hook) into a
target repo so that Claude Code sessions and Git commits are automatically
logged to case-study-harness/data/.
"""

import filecmp
import json
import os
import shutil
import sys
from pathlib import Path
from typing import Any

HARNESS_DIR: Path = Path(__file__).resolve().parent
HOOK_SOURCE: Path = HARNESS_DIR / "hooks" / "post-commit"
HOOKS_CONFIG: Path = HARNESS_DIR / "claude" / "hooks-config.json"
RULES_SOURCE: Path = HARNESS_DIR / "claude" / "rules"
SKILLS_SOURCE: Path = HARNESS_DIR / "claude" / "skills"
SKILL_DIRS: tuple[str, ...] = ("case-study-capture", "case-study-synthesize")


def validate_target(target: Path) -> None:
    """Verify the target path exists and contains a Git repository.

    Args:
        target: Absolute path to the target repository.

    Raises:
        SystemExit: If the target path or .git/ directory is missing.
    """
    if not target.is_dir():
        print(f"ERROR: Target path does not exist: {target}", file=sys.stderr)
        sys.exit(1)
    if not (target / ".git").is_dir():
        print(f"ERROR: No .git/ directory found in {target}", file=sys.stderr)
        sys.exit(1)


def check_existing_hook(target: Path) -> bool:
    """Check whether a post-commit hook already exists in the target repo.

    If the hook is already a symlink to our source, returns True (idempotent).
    If the hook exists but is not our symlink, exits fatally per AD-09.

    Args:
        target: Absolute path to the target repository.

    Returns:
        True if our symlink already exists (skip installation), False if no
        hook exists (proceed with installation).

    Raises:
        SystemExit: If an existing non-matching post-commit hook is found.
    """
    hook_path = target / ".git" / "hooks" / "post-commit"
    if not hook_path.exists() and not hook_path.is_symlink():
        return False
    if hook_path.is_symlink() and hook_path.resolve() == HOOK_SOURCE.resolve():
        return True
    print(
        f"ERROR: Existing post-commit hook found at {hook_path}. "
        "Remove it manually before installing the case-study harness.",
        file=sys.stderr,
    )
    sys.exit(1)


def create_data_dir(target: Path) -> str | None:
    """Create the case-study-harness/data/ directory in the target repo.

    Args:
        target: Absolute path to the target repository.

    Returns:
        A summary string if the directory was created, None if it already existed.
    """
    data_dir = target / "case-study-harness" / "data"
    if data_dir.is_dir():
        return None
    data_dir.mkdir(parents=True, exist_ok=True)
    return f"Created {data_dir.relative_to(target)}"


def install_hook(target: Path) -> str | None:
    """Symlink .git/hooks/post-commit to the harness post-commit hook.

    Creates the .git/hooks/ directory if it does not exist. Uses a relative
    symlink for portability.

    Args:
        target: Absolute path to the target repository.

    Returns:
        A summary string if the symlink was created, None if it already existed.
    """
    hook_path = target / ".git" / "hooks" / "post-commit"
    if hook_path.is_symlink() and hook_path.resolve() == HOOK_SOURCE.resolve():
        return None
    hook_path.parent.mkdir(parents=True, exist_ok=True)
    relative_target = os.path.relpath(HOOK_SOURCE, hook_path.parent)
    os.symlink(relative_target, hook_path)
    return f"Symlinked .git/hooks/post-commit -> {relative_target}"


def copy_rules(target: Path) -> list[str]:
    """Copy rule files into the target repo's .claude/rules/ directory.

    Skips files that already exist with identical content. Warns and skips
    files that exist with different content.

    Args:
        target: Absolute path to the target repository.

    Returns:
        A list of action summary strings.
    """
    actions: list[str] = []
    dest_dir = target / ".claude" / "rules"
    dest_dir.mkdir(parents=True, exist_ok=True)

    for src_file in sorted(RULES_SOURCE.iterdir()):
        if not src_file.is_file():
            continue
        dest_file = dest_dir / src_file.name
        if dest_file.exists():
            if filecmp.cmp(str(src_file), str(dest_file), shallow=False):
                continue
            print(
                f"WARNING: Rule file already exists (different content), skipping: {dest_file.relative_to(target)}",
                file=sys.stderr,
            )
            actions.append(f"Skipped rule (conflict): {src_file.name}")
            continue
        shutil.copy2(str(src_file), str(dest_file))
        actions.append(f"Copied rule: {src_file.name} -> .claude/rules/")

    return actions


def _dirs_identical(dir_a: Path, dir_b: Path) -> bool:
    """Recursively compare two directories for identical file content.

    Args:
        dir_a: First directory to compare.
        dir_b: Second directory to compare.

    Returns:
        True if all files match in name and content, False otherwise.
    """
    for src_file in dir_a.rglob("*"):
        if not src_file.is_file():
            continue
        relative = src_file.relative_to(dir_a)
        dest_file = dir_b / relative
        if not dest_file.exists():
            return False
        if not filecmp.cmp(str(src_file), str(dest_file), shallow=False):
            return False

    for dest_file in dir_b.rglob("*"):
        if not dest_file.is_file():
            continue
        relative = dest_file.relative_to(dir_b)
        if not (dir_a / relative).exists():
            return False

    return True


def copy_skills(target: Path) -> list[str]:
    """Copy skill directories into the target repo's .claude/skills/ directory.

    Skips directories that already exist with identical content. Warns and
    skips directories that exist with different content.

    Args:
        target: Absolute path to the target repository.

    Returns:
        A list of action summary strings.
    """
    actions: list[str] = []
    dest_dir = target / ".claude" / "skills"
    dest_dir.mkdir(parents=True, exist_ok=True)

    for skill_name in SKILL_DIRS:
        src_skill = SKILLS_SOURCE / skill_name
        dest_skill = dest_dir / skill_name
        if dest_skill.exists():
            if _dirs_identical(src_skill, dest_skill):
                continue
            print(
                f"WARNING: Skill directory already exists (different content), skipping: "
                f"{dest_skill.relative_to(target)}",
                file=sys.stderr,
            )
            actions.append(f"Skipped skill (conflict): {skill_name}")
            continue
        shutil.copytree(str(src_skill), str(dest_skill))
        actions.append(f"Copied skill: {skill_name} -> .claude/skills/")

    return actions


def _collect_existing_commands(entries: list[dict[str, Any]]) -> set[str]:
    """Extract all command strings from a list of hook entries.

    Args:
        entries: List of hook entry dicts, each with a "hooks" list.

    Returns:
        A set of command strings found across all entries.
    """
    commands: set[str] = set()
    for entry in entries:
        for hook in entry.get("hooks", []):
            cmd = hook.get("command")
            if isinstance(cmd, str):
                commands.add(cmd)
    return commands


def merge_hooks_config(target: Path) -> list[str]:
    """Merge case-study hook definitions into the target's settings.json.

    Performs an additive merge: existing hook entries are preserved, and
    case-study entries are added only if their commands are not already present.
    Creates settings.json if it does not exist.

    Args:
        target: Absolute path to the target repository.

    Returns:
        A list of action summary strings.
    """
    actions: list[str] = []
    settings_path = target / ".claude" / "settings.json"
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    source_config: dict[str, Any] = json.loads(HOOKS_CONFIG.read_text())
    source_hooks: dict[str, list[dict[str, Any]]] = source_config.get("hooks", {})

    if settings_path.exists():
        settings: dict[str, Any] = json.loads(settings_path.read_text())
    else:
        settings = {}
        actions.append("Created .claude/settings.json")

    if "hooks" not in settings:
        settings["hooks"] = {}

    for event_type, source_entries in source_hooks.items():
        existing_entries: list[dict[str, Any]] = settings["hooks"].get(event_type, [])
        existing_commands = _collect_existing_commands(existing_entries)

        for source_entry in source_entries:
            source_commands = {
                hook.get("command")
                for hook in source_entry.get("hooks", [])
                if isinstance(hook.get("command"), str)
            }
            if source_commands and source_commands.issubset(existing_commands):
                continue
            existing_entries.append(source_entry)
            actions.append(f"Added hook: {event_type}")

        settings["hooks"][event_type] = existing_entries

    settings_path.write_text(json.dumps(settings, indent=2) + "\n")
    return actions


def print_summary(actions: list[str]) -> None:
    """Print a confirmation listing of all actions taken.

    Args:
        actions: List of action summary strings.
    """
    if not actions:
        print("case-study-harness: already installed, nothing to do.")
        return
    print("case-study-harness: installation complete.")
    for action in actions:
        print(f"  - {action}")


def main() -> int:
    """Install the case-study meta-harness into a target repository.

    Returns:
        Exit code (0 for success, 1 for fatal error).
    """
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        print(f"Usage: {sys.argv[0]} <target-repo-path>", file=sys.stderr)
        return 1 if len(sys.argv) != 2 else 0

    target = Path(sys.argv[1]).resolve()

    validate_target(target)
    hook_already_installed = check_existing_hook(target)

    actions: list[str] = []

    data_action = create_data_dir(target)
    if data_action:
        actions.append(data_action)

    if not hook_already_installed:
        hook_action = install_hook(target)
        if hook_action:
            actions.append(hook_action)

    actions.extend(copy_rules(target))
    actions.extend(copy_skills(target))
    actions.extend(merge_hooks_config(target))

    print_summary(actions)
    return 0


if __name__ == "__main__":
    sys.exit(main())
