#!/usr/bin/env python3
"""Cross-reference validation for the Harness Engineering Guide repo.

Runs deterministic checks and reports findings.
Exit 0 = clean, exit 1 = issues found.
Output is pipe-delimited: TYPE|FILE|LINE|ISSUE|FIX
"""

import re
import sys
from collections.abc import Iterator
from pathlib import Path

REPO_ROOT: Path = Path(__file__).resolve().parents[4]
LINK_PATTERN: re.Pattern[str] = re.compile(r"\[([^]]+)]\(([^)]+\.md)\)")
NEXT_PATTERN: re.Pattern[str] = re.compile(r"^Next: \[([^]]+)]\(([^)]+)\)\s*$", re.MULTILINE)
FINAL_CHAPTER: str = "11-failure-modes.md"
CHEATSHEET_PATH: Path = REPO_ROOT / "CHEATSHEET.md"
README_CHAPTER_LINK: re.Pattern[str] = re.compile(
    r"\*\*\[([^]]+)]\(guide/([^)]+\.md)\)\*\*"
)
CHEATSHEET_CHAPTER_LINK: re.Pattern[str] = re.compile(
    r"\[(Chapter \d+ -- [^]]+)]\(guide/([^)]+\.md)\)"
)
REGISTRY_ROW: re.Pattern[str] = re.compile(r'\|\s*"([^"]+)"\s*\|[^|]+\|\s*(.+?)\s*\|')
INLINE_CODE: re.Pattern[str] = re.compile(r"(`+)(.+?)\1")
CANONICAL_TERMS: dict[str, list[Path]] = {
    "five-tier context hierarchy": [
        REPO_ROOT / "CLAUDE.md",
        REPO_ROOT / "README.md",
    ],
    "document cascade": [
        REPO_ROOT / "CLAUDE.md",
        REPO_ROOT / "README.md",
        REPO_ROOT / "templates/docs/README.md",
    ],
}


def find_md_files() -> Iterator[Path]:
    """Yield all Markdown files in the repo, excluding ignored directories.

    Yields:
        Path objects for each .md file found, excluding .git and node_modules.
    """
    for path in REPO_ROOT.rglob("*.md"):
        if ".git" not in path.parts and "node_modules" not in path.parts:
            yield path


def _fenced_code_lines(lines: list[str]) -> list[bool]:
    """Return per-line booleans indicating fenced code block membership.

    Handles backtick and tilde fences of any length, matching the closing
    fence to the opening fence character and minimum length per CommonMark.

    Args:
        lines: File content split into lines.

    Returns:
        List of booleans, one per line, True if inside a fenced code block.
    """
    result: list[bool] = []
    in_block = False
    fence_char = ""
    fence_len = 0
    for line in lines:
        stripped = line.lstrip()
        if not in_block:
            m = re.match(r"(`{3,}|~{3,})", stripped)
            if m:
                fence_char = m.group(1)[0]
                fence_len = len(m.group(1))
                in_block = True
                result.append(True)
            else:
                result.append(False)
        else:
            result.append(True)
            m = re.match(r"(`{3,}|~{3,})\s*$", stripped)
            if m and m.group(1)[0] == fence_char and len(m.group(1)) >= fence_len:
                in_block = False
    return result


def check_internal_links(issues: list[str]) -> None:
    """Verify every [text](path.md) link resolves to an existing file.

    Scans all Markdown files for relative links and checks that each target
    exists on disk. Appends pipe-delimited findings to the issues list.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    for md_file in find_md_files():
        parent = md_file.parent
        lines = md_file.read_text().splitlines()
        in_fence = _fenced_code_lines(lines)
        for lineno, line in enumerate(lines, start=1):
            if in_fence[lineno - 1]:
                continue
            cleaned = INLINE_CODE.sub("", line)
            for _, link in LINK_PATTERN.findall(cleaned):
                target = (parent / link).resolve()
                if not target.is_file():
                    rel = md_file.relative_to(REPO_ROOT)
                    issues.append(
                        f"BROKEN_LINK|{rel}|{lineno}"
                        f"|Link to {link} does not resolve"
                        f"|Verify path or update link"
                    )


def check_chapter_readme_listing(issues: list[str]) -> None:
    """Verify every chapter file is listed in README.md.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    readme_text = (REPO_ROOT / "README.md").read_text()
    for chapter in sorted((REPO_ROOT / "guide").glob("*.md")):
        if chapter.name not in readme_text:
            issues.append(
                f"MISSING_README_ENTRY|guide/{chapter.name}|1"
                f"|Chapter not listed in README.md"
                f"|Add entry for {chapter.name}"
            )


def check_chapter_h1_format(issues: list[str]) -> None:
    """Verify every guide chapter starts with '# Chapter'.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    for chapter in sorted((REPO_ROOT / "guide").glob("*.md")):
        first_line = chapter.read_text().split("\n", 1)[0]
        if not first_line.startswith("# Chapter"):
            issues.append(
                f"BAD_H1|guide/{chapter.name}|1"
                f"|H1 does not start with '# Chapter': {first_line}"
                f"|Update title format"
            )


def check_template_paths(issues: list[str]) -> None:
    """Verify template paths referenced in guide chapters exist.

    Extracts paths matching ``templates/...`` from guide chapter content and
    checks that each referenced file or directory exists on disk.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    template_pattern = re.compile(r"templates/[a-zA-Z0-9_./-]+")
    seen: set[str] = set()
    for chapter in (REPO_ROOT / "guide").glob("*.md"):
        for match in template_pattern.findall(chapter.read_text()):
            if match.endswith("/") or match in seen:
                continue
            seen.add(match)
            if not (REPO_ROOT / match).exists():
                issues.append(
                    f"MISSING_TEMPLATE|guide/|0"
                    f"|Referenced path {match} does not exist"
                    f"|Update reference or create file"
                )


def check_checklist_references(issues: list[str]) -> None:
    """Verify each checklist file is referenced somewhere.

    Searches root-level and guide Markdown files for mentions of each
    filename in the ``checklists/`` directory.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    checklists_dir = REPO_ROOT / "checklists"
    if not checklists_dir.exists():
        return

    searchable = ""
    for md_file in REPO_ROOT.glob("*.md"):
        searchable += md_file.read_text()
    for md_file in (REPO_ROOT / "guide").glob("*.md"):
        searchable += md_file.read_text()

    for checklist in sorted(checklists_dir.glob("*.md")):
        if checklist.name not in searchable:
            issues.append(
                f"ORPHAN_CHECKLIST|checklists/{checklist.name}|0"
                f"|Not referenced from any guide chapter or root file"
                f"|Add reference"
            )


def check_canonical_terms(issues: list[str]) -> None:
    """Verify canonical terms appear in all required locations.

    Checks each term defined in ``CANONICAL_TERMS`` against its list of
    files that must contain it.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    for term, locations in CANONICAL_TERMS.items():
        for filepath in locations:
            if filepath.is_file() and term not in filepath.read_text():
                rel = filepath.relative_to(REPO_ROOT)
                issues.append(
                    f"TERM_MISSING|{rel}|0"
                    f"|Expected canonical term '{term}' not found"
                    f"|Add or verify term usage"
                )


def check_next_footers(issues: list[str]) -> None:
    """Verify every non-final chapter has a Next: footer linking to an existing file.

    Checks that each guide chapter except ``11-failure-modes.md`` contains a
    ``Next:`` footer link and that the linked file exists on disk.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    guide_dir = REPO_ROOT / "guide"
    for chapter in sorted(guide_dir.glob("*.md")):
        if chapter.name == FINAL_CHAPTER:
            continue
        content = chapter.read_text()
        rel = chapter.relative_to(REPO_ROOT)
        match = NEXT_PATTERN.search(content)
        if not match:
            issues.append(
                f"MISSING_NEXT_FOOTER|{rel}|0"
                f"|Chapter is missing a 'Next:' footer section"
                f"|Add '---\\n\\nNext: [Chapter NN -- Title](NN-slug.md)' at end of file"
            )
            continue
        linked_file = match.group(2)
        target = (chapter.parent / linked_file).resolve()
        if not target.is_file():
            lineno = content[: match.start()].count("\n") + 1
            issues.append(
                f"BROKEN_NEXT_LINK|{rel}|{lineno}"
                f"|Next: link to {linked_file} does not resolve"
                f"|Verify path or update link"
            )


def build_chapter_titles() -> dict[str, str]:
    """Return ``{filename: H1 title text}`` for each guide chapter.

    Returns:
        Mapping from chapter filename to its H1 title with the leading
        ``# `` stripped, e.g.
        ``{"01-foundations.md": "Chapter 01 -- Foundations: ..."}``.
    """
    titles: dict[str, str] = {}
    for chapter in sorted((REPO_ROOT / "guide").glob("*.md")):
        first_line = chapter.read_text().split("\n", 1)[0]
        if first_line.startswith("# "):
            titles[chapter.name] = first_line[2:]
    return titles


def check_chapter_title_wording(issues: list[str]) -> None:
    """Verify chapter H1 titles match their entries in README.md and CHEATSHEET.md.

    README.md entries must match the full H1 title. CHEATSHEET.md entries must
    match the H1 prefix before the colon.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    titles = build_chapter_titles()

    readme_text = (REPO_ROOT / "README.md").read_text()
    for match in README_CHAPTER_LINK.finditer(readme_text):
        link_title = match.group(1)
        filename = match.group(2)
        if filename in titles and link_title != titles[filename]:
            lineno = readme_text[: match.start()].count("\n") + 1
            issues.append(
                f"TITLE_MISMATCH|README.md|{lineno}"
                f"|Title '{link_title}' does not match H1 '{titles[filename]}'"
                f"|Update README.md entry for {filename}"
            )

    if not CHEATSHEET_PATH.is_file():
        return
    cheatsheet_text = CHEATSHEET_PATH.read_text()
    for match in CHEATSHEET_CHAPTER_LINK.finditer(cheatsheet_text):
        link_title = match.group(1)
        filename = match.group(2)
        if filename in titles:
            h1_prefix = (
                titles[filename].split(":")[0]
                if ":" in titles[filename]
                else titles[filename]
            )
            if link_title != h1_prefix:
                lineno = cheatsheet_text[: match.start()].count("\n") + 1
                issues.append(
                    f"TITLE_MISMATCH|CHEATSHEET.md|{lineno}"
                    f"|Title '{link_title}' does not match"
                    f" H1 prefix '{h1_prefix}'"
                    f"|Update CHEATSHEET.md entry for {filename}"
                )


def check_next_footer_title_match(issues: list[str]) -> None:
    """Verify Next: footer link text matches the target chapter's actual H1.

    Skips chapters without a Next: footer — those are already caught by
    ``check_next_footers``.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    titles = build_chapter_titles()
    guide_dir = REPO_ROOT / "guide"

    for chapter in sorted(guide_dir.glob("*.md")):
        if chapter.name == FINAL_CHAPTER:
            continue
        content = chapter.read_text()
        match = NEXT_PATTERN.search(content)
        if not match:
            continue
        link_text = match.group(1)
        linked_file = match.group(2)
        if linked_file in titles and link_text != titles[linked_file]:
            rel = chapter.relative_to(REPO_ROOT)
            lineno = content[: match.start()].count("\n") + 1
            issues.append(
                f"NEXT_TITLE_MISMATCH|{rel}|{lineno}"
                f"|Next: text '{link_text}' does not match"
                f" target H1 '{titles[linked_file]}'"
                f"|Update Next: footer link text"
            )


def check_canonical_terms_registry(issues: list[str]) -> None:
    """Verify CANONICAL_TERMS dict matches references/canonical-terms.md.

    Parses the registry table and compares each term's dependent locations
    against the script's ``CANONICAL_TERMS`` dict, reporting any drift.

    Args:
        issues: Accumulator list for pipe-delimited issue strings.
    """
    registry_path = (
        Path(__file__).resolve().parent.parent / "references" / "canonical-terms.md"
    )
    if not registry_path.is_file():
        issues.append(
            "REGISTRY_DRIFT|references/canonical-terms.md|0"
            "|Registry file not found"
            "|Create references/canonical-terms.md"
        )
        return

    registry_text = registry_path.read_text()
    registry_terms: dict[str, set[str]] = {}
    for match in REGISTRY_ROW.finditer(registry_text):
        term = match.group(1)
        deps = set(re.findall(r"`([^`]+)`", match.group(2)))
        registry_terms[term] = deps

    script_terms: dict[str, set[str]] = {}
    for term, paths in CANONICAL_TERMS.items():
        script_terms[term] = {str(p.relative_to(REPO_ROOT)) for p in paths}

    all_terms = sorted(set(registry_terms) | set(script_terms))
    for term in all_terms:
        reg_deps = registry_terms.get(term, set())
        scr_deps = script_terms.get(term, set())
        if reg_deps != scr_deps:
            issues.append(
                f"REGISTRY_DRIFT|validate.py|0"
                f"|Dict/registry mismatch for '{term}': "
                f"script={sorted(scr_deps)}, registry={sorted(reg_deps)}"
                f"|Sync CANONICAL_TERMS with references/canonical-terms.md"
            )


def main() -> None:
    """Run all cross-reference checks and print results.

    Exits with code 0 if no issues are found, or code 1 with a summary
    line if any issues are detected.
    """
    issues: list[str] = []

    check_internal_links(issues)
    check_chapter_readme_listing(issues)
    check_chapter_h1_format(issues)
    check_template_paths(issues)
    check_checklist_references(issues)
    check_canonical_terms(issues)
    check_next_footers(issues)
    check_chapter_title_wording(issues)
    check_next_footer_title_match(issues)
    check_canonical_terms_registry(issues)

    for issue in issues:
        print(issue)

    if issues:
        print(f"\nSUMMARY: {len(issues)} issue(s) found.")
        sys.exit(1)
    else:
        print("ALL_CLEAR|All cross-references valid.")


if __name__ == "__main__":
    main()
