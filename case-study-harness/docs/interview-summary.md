# Case Study Harness -- Project Interview Summary

## Product Vision

The case study harness is a meta-harness: a supplementary set of Claude Code mechanisms (rules, skills, hooks, scripts)
that sits alongside a project's main operational harness and observes how that harness is used. It captures structured
data about what works, what fails, and why -- mostly automatically, with an opt-in manual capture skill for ambiguous
or noteworthy moments the automation can't detect.

The problem it solves: the Harness Engineering Guide (this repo) lacks a feedback loop. Engineers follow the guide,
build software, and learn things that should improve the guide and produce case studies -- but there's no systematic way
to capture that signal during the build. Without it, lessons evaporate across sessions and the guide can't improve from
real-world use.

## Target Persona

The primary user is a harness engineer (the guide's author) who is building an application using the harness
engineering methodology. They seed the meta-harness into their app repo before starting, and it runs alongside
their normal harness throughout development. They are deeply familiar with Claude Code mechanisms (rules, skills,
hooks, memory) and don't need hand-holding, but they also don't want the observation layer to distract from the
actual build work.

Expected effort level: near-zero for automatic capture. The user accepts occasional prompts for clarification on
ambiguous events and can invoke a manual capture skill when they notice something noteworthy. They should not need
to memorize categories, fill in templates, or run scripts by hand during normal development.

## Core Experience

The user copies the meta-harness into their app repo. From that point forward, it quietly captures structured
observations as JSONL log entries:

- **Harness file changes** -- when CLAUDE.md, rules, skills, hooks, or settings.json are added, modified, or removed
- **Agent friction events** -- moments where the agent misunderstood, went off-track, needed correction, or hit a wall
- **Successful patterns** -- things the agent did well that were directly attributable to a harness decision
- **Human overrides** -- times the user stepped in to correct something the harness should have prevented
- **Context architecture decisions** -- why something was placed in a rule vs. skill vs. CLAUDE.md, and whether that
  choice held up

Most capture is automatic (via hooks that fire on tool use, session events, and harness file changes). Human overrides
and subjective observations are captured via a manual `/case-study-capture` skill invoked within the context window
where the event occurred. The system may also proactively ask for clarification when it detects ambiguous signals.

When the build is complete (or at any milestone), a `/case-study-synthesize` skill reads all captured data and drafts
two deliverables: a case study and a harness guide improvement plan.

## Tech Stack Decisions

This is not an application -- it is a set of Claude Code harness mechanisms and supporting scripts:

- **Rules** (`.claude/rules/`) -- a global rule that primes the agent to be observation-aware during sessions
- **Skills** (`.claude/skills/`) -- `/case-study-capture` for manual observation logging;
  `/case-study-synthesize` for end-of-project synthesis into case study and improvement plan
- **Hooks** -- `PostToolUse` hooks (matched on Edit/Write to harness file paths) for automatic change detection;
  `Stop` hooks for session-level summary capture; `PostToolUseFailure` for friction event detection
- **Scripts** -- Python 3 scripts that hooks invoke to write structured JSONL log entries
- **Native Git hook** -- a `post-commit` hook that detects when harness files (`.claude/`, `CLAUDE.md`,
  `settings.json`) were changed in a commit and logs the SHA, changed files, and commit message as a JSONL entry.
  Covers harness changes made outside Claude Code sessions (e.g., manual editor tweaks). Note: the JSONL entry is
  written after the commit, so it lands in a subsequent commit -- acceptable since log entries reference the source
  SHA for traceability
- **Install script** -- a single Python script that seeds the meta-harness into a target repo: symlinks the Git
  hook, creates data directories, and prints confirmation. Keeps setup to one command
- **Data store** -- JSONL files accumulating observations across sessions, designed for machine consumption
  (AI and/or deterministic Python scripts), not human reading

## Non-Negotiables

- **Must not interfere with the main harness.** The observation layer cannot break, slow down, or alter the behavior
  of the actual build work. It is strictly additive.
- **Must be fast to seed.** If setup takes more than a few minutes, it has failed. Copy the directory, merge a few
  files, start building.
- **Must survive context compaction.** All captured data lives on disk as JSONL files, not in conversation context.
  Sessions can be cleared or compacted without data loss.
- **Must be simple enough to understand in minutes.** The previous attempt (V1, stashed) failed this test -- 15
  journal categories, 5 Python scripts, Markdown templates with frontmatter, phase metrics. The meta-harness must
  be simpler to understand than the thing it observes.
- **Must be clearly separable from the main harness.** The meta-harness's files should be discernible from main
  harness files and removable once the case study is complete. Exact placement strategy is a design decision to be
  resolved during architecture planning.

## Non-Goals (MVP)

- **No per-phase ceremony.** No mandatory retrospectives or phase gates. Continuous logging only.
- **No category taxonomy the user must memorize.** The system determines event types, not the human.
- **No metrics dashboards or intermediate aggregation.** Raw JSONL in, synthesized deliverables out. No intermediate
  "project metrics" or "phase metrics" step.
- **No Markdown templates for humans to fill in.** Structured JSON written by scripts, not humans copying templates.
- **No real-time reporting or visualization.** The data is consumed at synthesis time, not during the build.

## Deployment Target

The meta-harness is developed in this repository (`harness-engineering-guide`) under `case-study-harness/` and is
designed to be copied into new repositories that use harness engineering. The first target is an existing application
the author originally started building by hand and plans to rebuild using the harness engineering methodology.

The meta-harness produces two deliverables at synthesis time:

1. **Case study** -- fills out the `case-study/` placeholders in the harness engineering guide repo with a real,
   evidence-backed narrative covering successes, failures, and how failures were addressed
2. **Harness guide improvement plan** -- actionable changes to guide chapters based on issues encountered during
   the build
