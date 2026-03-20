---
paths:
  - "README.md"
  - "CLAUDE.md"
  - "CHEATSHEET.md"
---

# Root File Editing Rules

## README.md

The chapter listing (lines 45-93) must match the H1 titles in `guide/*.md` exactly. After updating a chapter title,
update the corresponding README entry.

## CLAUDE.md

- Must stay under 200 lines total
- The Cross-Reference Registry section is the authoritative map of dependencies — keep it current when adding or
  renaming files

## CHEATSHEET.md

- Must stay under 200 lines total
- Contains exactly 9 phases (0-8), each with: human action, blockquote prompt, verify step, and chapter link
- Prompts use `[square bracket placeholders]` for project-specific values — no fictional examples

## Canonical Terms

These terms have authoritative definitions. When used anywhere, they must match:

- **"five-tier context hierarchy"** — defined in Chapter 04 (`guide/04-context-architecture.md`)
- **"document cascade"** — defined in Chapter 03 (`guide/03-specification-phase.md`)

If you change these terms in their authoritative source, search and update all occurrences in README.md, CLAUDE.md, and
any other files that reference them.
