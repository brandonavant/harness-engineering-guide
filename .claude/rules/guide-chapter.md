---
paths:
  - "guide/**"
---

# Guide Chapter Editing Rules

## Voice

This guide is prescriptive. Use direct statements ("do this", "use X", "never Y").

Banned hedging phrases — rewrite any of these into direct instructions:

- "you might consider"
- "you could perhaps"
- "it may be worth"
- "you may want to"
- "consider doing"
- "it might be helpful"

## Chapter Structure

- Line 1 must be an H1 title starting with `# Chapter`
- Each chapter must contain these sections (as H2 or H3): Principles, What the Human Should Do, What the Agent Should Do
- Use `##` for major sections, `###` for subsections — never use H1 (`#`) after line 1

## Cross-Reference Protocol

After changing a chapter's H1 title:

1. Update the matching entry in `README.md` (lines 45-93)
2. Update `CLAUDE.md` if the chapter is referenced there
3. Update the "Next:" link in the prior chapter's footer

After changing template references or metadata:

1. Verify the referenced path exists in `templates/`
2. Grep other chapters for the old path

## Formatting

- Examples in guide chapters use the fictional **RecipeVault** recipe app (not "Beacon" — that is for templates only)
- Code blocks use fenced syntax with language identifiers
- When nesting fenced blocks, the outer fence must use more backticks than the inner
- Cross-references use relative Markdown links: `[Chapter 02](02-project-bootstrap.md)`
- Chapter filenames follow `NN-slug.md` (e.g., `01-foundations.md`)

## Checklists

The `checklists/` directory contains standalone checklists (project-kickoff, phase-completion, context-reset,
pre-merge). Reference these where relevant rather than duplicating their content.
