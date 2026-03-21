#!/usr/bin/env python3
"""Validate that a GitHub pull request's body matches a local source-of-truth file.

Fetches the live PR body via ``gh pr view`` and compares it against the
expected content on disk. Exits 0 on match, 1 on mismatch or fetch failure.

Usage:
    python3 validate_pr.py <pr-number> <expected-body-file>

Args:
    pr-number: The GitHub pull request number to validate.
    expected-body-file: Path to the Markdown file containing the expected body.
"""

import difflib
import subprocess
import sys
import time

MAX_FETCH_RETRIES = 2
RETRY_DELAY_SECONDS = 5


def fetch_pr_body(pr_number: str) -> str:
    """Fetch the body of a GitHub pull request.

    Args:
        pr_number: The PR number to fetch.

    Returns:
        The PR body as a string.

    Raises:
        RuntimeError: If the fetch fails after retries.
    """
    result = None
    for attempt in range(1, MAX_FETCH_RETRIES + 2):
        result = subprocess.run(
            ["gh", "pr", "view", pr_number, "--json", "body", "--jq", ".body"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        if result.returncode == 0 and result.stdout.strip():
            return result.stdout
        if attempt <= MAX_FETCH_RETRIES:
            print(
                f"Fetch attempt {attempt} failed (rc={result.returncode}), "
                f"retrying in {RETRY_DELAY_SECONDS}s..."
            )
            time.sleep(RETRY_DELAY_SECONDS)

    last_stderr = result.stderr.strip() if result else "no output captured"
    raise RuntimeError(
        f"Failed to fetch PR #{pr_number} after {MAX_FETCH_RETRIES + 1} attempts. "
        f"Last stderr: {last_stderr}"
    )


def normalize(text: str) -> str:
    """Normalize text for comparison by stripping trailing whitespace per line.

    Args:
        text: The raw text to normalize.

    Returns:
        Text with trailing whitespace stripped from each line and a single
        trailing newline.
    """
    lines = [line.rstrip() for line in text.splitlines()]
    while lines and not lines[-1]:
        lines.pop()
    return "\n".join(lines) + "\n" if lines else ""


def main() -> int:
    """Run the validation.

    Returns:
        0 if the PR body matches, 1 otherwise.
    """
    if len(sys.argv) != 3:
        print(f"Usage: {sys.argv[0]} <pr-number> <expected-body-file>")
        return 1

    pr_number = sys.argv[1]
    expected_path = sys.argv[2]

    try:
        with open(expected_path) as f:
            expected = f.read()
    except FileNotFoundError:
        print(f"ERROR: Expected body file not found: {expected_path}")
        return 1

    try:
        actual = fetch_pr_body(pr_number)
    except RuntimeError as exc:
        print(f"ERROR: {exc}")
        return 1

    expected_norm = normalize(expected)
    actual_norm = normalize(actual)

    if expected_norm == actual_norm:
        print(f"OK: PR #{pr_number} body matches expected content.")
        return 0

    print(f"MISMATCH: PR #{pr_number} body differs from expected content.\n")
    diff = difflib.unified_diff(
        expected_norm.splitlines(keepends=True),
        actual_norm.splitlines(keepends=True),
        fromfile="expected",
        tofile=f"pr-{pr_number}-actual",
    )
    sys.stdout.writelines(diff)
    return 1


if __name__ == "__main__":
    sys.exit(main())
