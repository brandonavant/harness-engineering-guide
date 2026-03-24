# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a documentation-only repository — a prescriptive guide for building production software using Claude Code with
zero manually-written code. It teaches "harness engineering": designing the environment (CLAUDE.md, rules, skills,
hooks, specs, contracts) that makes AI agents productive, rather than writing code directly.

## Repository Structure

The repo contains no application code, no build system, and no tests. It is organized as:

- `guide/` — The 11-chapter guide, ordered by lifecycle phase (Foundations → Specification → Harness → Build → Sustain)
- `templates/` — Starter files users copy into their projects: CLAUDE.md template, doc templates (PRD, architecture, UX
  spec, brand identity), OpenAPI stub, skill/rule/hook examples, CI workflow, subagent definition templates
- `case-study/` — Placeholder for a case study (WIP, will be populated after guide validation)
- `checklists/` — Standalone checklists for project kickoff, phase completion, context reset, and pre-merge
- `README.md` — Entry point with guide structure, quick start options, and sources

## Key Architectural Concepts

The guide teaches a **five-tier context hierarchy** (Chapter 4) that is central to all recommendations:

1. **CLAUDE.md** — Always loaded, under 200 lines, serves as a map not an encyclopedia
2. **Rules** (`.claude/rules/`) — Path-scoped on file pattern match, or global at session start when `paths` is omitted
3. **Skills** (`.claude/skills/`) — Loaded on demand for specific work types
4. **Discoverable docs** (`docs/`, `contracts/`) — Read through Tier 1 pointers
5. **Memory** — Persistent across sessions for institutional knowledge

The guide follows a **document cascade** (Chapter 3): Interview Summary → PRD → Architecture → UX Spec → API Contract →
Brand Identity. Each document feeds the next.

## Writing Conventions

- Chapters use `##` for major sections and `###` for subsections
- Each chapter has: entry/exit points, principles, human instructions, agent instructions, common mistakes
- Templates contain `**[CUSTOMIZE]**` markers where users replace example content
- Code examples use fenced blocks with language identifiers
- When nesting fenced code blocks (e.g., showing Markdown that itself contains code blocks), the outer fence must use
  more backticks than the inner fence (e.g., ```````` for the outer when the inner uses ```)
- Cross-references between chapters use relative Markdown links (`[Chapter 02](02-project-bootstrap.md)`)
- Chapter filenames follow `NN-slug.md` pattern (e.g., `01-foundations.md`)

## Scripting Conventions

- All scripts in this repo use **Python 3** (never shell/bash). Use `#!/usr/bin/env python3` shebangs.
- Use **Google-style docstrings** for modules, classes, and functions. Include a summary line, then
  `Args:`, `Returns:`/`Yields:`, and `Raises:` sections as applicable. Omit sections that would be empty.
- Use **type hints** on function signatures and where they aid readability.

## Research Before Reasoning About Claude Code

This guide teaches Claude Code features (rules, skills, hooks, CLAUDE.md). Any time a task involves reasoning about
how Claude Code features work — whether answering a question, evaluating a design, or creating or modifying a harness
file — fetch the relevant official documentation first. Do not rely on training knowledge, MCP index tools, or the
guide's own examples, which may be outdated.

**Authoritative source:** Fetch directly from `https://code.claude.com/docs/en/` using WebFetch. Key pages:

- **Memory & rules**: `https://code.claude.com/docs/en/memory` (CLAUDE.md format, `.claude/rules/` frontmatter)
- **Skills**: `https://code.claude.com/docs/en/skills` (SKILL.md format, directory structure, frontmatter)
- **Hooks**: `https://code.claude.com/docs/en/hooks` (hook types, settings.json schema, allowed fields)
- **Settings**: `https://code.claude.com/docs/en/settings` (settings.json structure, permissions)

Do NOT use MCP index tools or training knowledge as the primary source for Claude Code feature formats. These sources
may return results from internal plugins, third-party examples, or outdated training data that use different
conventions than the official user-facing documentation.

## When Editing Content

- The guide is opinionated and prescriptive — maintain that voice. Avoid hedging language ("you might consider") in
  favor of direct statements ("do this").
- Chapters 04-11 are complete. Chapters 01-03 were the initial release.
- The case study is currently a placeholder (WIP). It will be populated after the guide is validated on a real
  production application.
- Templates in `templates/` use a fictional "Beacon" task management SaaS as the example project. Guide chapters use a
  fictional "RecipeVault" recipe app.

## Rules and Skills

This repo uses its own harness features. Rules autoload by path; skills are invoked on demand.

- **Rules** (`.claude/rules/`):
    - `guide-chapter.md` — Voice enforcement, structure requirements, cross-reference protocol for `guide/**`
    - `template-file.md` — Beacon examples, CUSTOMIZE markers, rename protocol for `templates/**`
    - `root-files.md` — Title sync, line limits, canonical term consistency for `README.md` and `CLAUDE.md`
- **Skills** (`.claude/skills/`):
    - `cross-reference-check/` — Validates all cross-references repo-wide (titles, paths, terms, links)
    - `edit-chapter/` — Guided before/during/after workflow for safe chapter editing

## Cross-Reference Registry

Sources of truth and their dependents. Check dependents after any change to the source.

| Source of Truth                         | Dependents to Check                                                 |
|-----------------------------------------|---------------------------------------------------------------------|
| Chapter H1 titles (`guide/*.md` line 1) | `README.md` lines 45-93, `CLAUDE.md`, `CHEATSHEET.md`, "Next:" link in prior chapter |
| Template paths (referenced in chapters) | Actual files in `templates/`, `CHEATSHEET.md`                       |
| "five-tier context hierarchy" (Ch 04)   | `CLAUDE.md`, `README.md`                                            |
| "document cascade" (Ch 03)              | `CLAUDE.md`, `README.md`, `templates/docs/README.md`                |
| Template filenames                      | Chapter metadata lines, template `README.md` files                  |
| Checklist filenames (`checklists/`)     | `README.md`                                                         |
