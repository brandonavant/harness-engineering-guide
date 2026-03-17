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
  spec, brand identity), OpenAPI stub, skill/rule/hook examples, CI workflow, agent instruction/state templates
- `case-study/` — Placeholder for a case study (WIP, will be populated after guide validation)
- `checklists/` — Standalone checklists for project kickoff, phase completion, context reset, and pre-merge
- `README.md` — Entry point with guide structure, quick start options, and sources

## Key Architectural Concepts

The guide teaches a **five-tier context hierarchy** (Chapter 4) that is central to all recommendations:

1. **CLAUDE.md** — Always loaded, under 200 lines, serves as a map not an encyclopedia
2. **Path-scoped rules** (`.claude/rules/`) — Auto-loaded on file pattern match
3. **Skills** (`.claude/skills/`) — Loaded on demand for specific work types
4. **Discoverable docs** (`docs/`, `contracts/`, `.agent-instructions/`) — Read through Tier 1 pointers
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

## When Editing Content

- The guide is opinionated and prescriptive — maintain that voice. Avoid hedging language ("you might consider") in
  favor of direct statements ("do this").
- Chapters 04-11 are complete. Chapters 01-03 were the initial release. The README's "coming soon" markers for chapters
  04-11 are outdated.
- The case study is currently a placeholder (WIP). It will be populated after the guide is validated on a real
  production application.
- Templates in `templates/` use a fictional "Beacon" task management SaaS as the example project. Guide chapters use a
  fictional "RecipeVault" recipe app.
