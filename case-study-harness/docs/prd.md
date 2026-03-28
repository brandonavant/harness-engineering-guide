# Case Study Harness -- Product Requirements Document

## Document Header

| Field          | Value                                   |
|----------------|-----------------------------------------|
| Version        | v1.0                                    |
| Date           | 2026-03-27                              |
| Author         | Brandon Avant                           |
| Change Summary | Initial version, derived from interview |

---

## 1. Vision and Overview

The case study harness is a meta-harness: a supplementary set of Claude Code mechanisms (rules, skills, hooks, scripts)
that sits alongside a project's main operational harness and observes how that harness is used. It captures structured
data about what works, what fails, and why -- mostly automatically, with an opt-in manual capture skill for ambiguous
or noteworthy moments the automation cannot detect.

The problem: the Harness Engineering Guide lacks a feedback loop. Engineers follow the guide, build software, and learn
things that should improve the guide and produce case studies -- but there is no systematic way to capture that signal
during the build. Without it, lessons evaporate across sessions and the guide cannot improve from real-world use.

## 2. Target Persona

**Primary persona: The Harness Engineer (guide author)**

- Deeply familiar with Claude Code mechanisms: rules, skills, hooks, memory, CLAUDE.md.
- Building an application using the harness engineering methodology from this guide.
- Seeds the meta-harness into their app repo before starting; it runs alongside the main harness throughout development.
- Does not need hand-holding on Claude Code features, but does not want the observation layer to distract from build
  work.
- Expected effort: near-zero for automatic capture. Accepts occasional clarification prompts on ambiguous events. Can
  invoke a manual capture skill when they notice something noteworthy.
- **Experience breakers:** Needing to memorize categories, fill in templates manually, run scripts by hand during normal
  development, or stop mid-task to journal observations.

## 3. Feature Requirements

### F-01: Automatic Harness Change Detection

Hooks detect when harness files are added, modified, or removed and log the event without user intervention.

- **AC-01:** `PostToolUse` hooks fire on Edit/Write operations targeting harness file paths (`.claude/`, `CLAUDE.md`,
  `settings.json`).
- **AC-02:** Each event is written as a single JSONL entry containing: timestamp, event type, file path, and a summary
  of what changed.
- **AC-03:** A native Git `post-commit` hook detects harness file changes in commits made outside Claude Code sessions
  (e.g., manual editor tweaks) and logs the SHA, changed files, and commit message as a JSONL entry.
- **AC-04:** The Git hook log entry references the source commit SHA for traceability. The entry itself lands in a
  subsequent commit -- this is acceptable and expected.

### F-02: Friction Event Detection

Hooks detect moments where the agent misunderstood, went off-track, needed correction, or hit a wall.

- **AC-01:** `PostToolUseFailure` hooks capture tool failures and log them as friction events.
- **AC-02:** Each friction entry includes: timestamp, event type, tool name, error summary, and surrounding context
  (what the agent was trying to do).

### F-03: Session Summary Capture

At the end of each session, the system captures a summary of what happened.

- **AC-01:** A `Stop` hook fires when a session ends and writes a summary JSONL entry.
- **AC-02:** The summary includes: timestamp, session duration estimate, high-level description of work performed, and
  any harness-related observations from the session.

### F-04: Manual Observation Capture (`/case-study-capture`)

A skill that the user invokes within the current context window to log subjective or ambiguous observations the
automation cannot detect.

- **AC-01:** Invoked via `/case-study-capture` within the active session.
- **AC-02:** The skill reads the current conversation context to understand what happened.
- **AC-03:** The user provides a brief description of the observation; the skill classifies the event type (successful
  pattern, human override, context architecture decision, friction, or other).
- **AC-04:** The observation is written as a JSONL entry with: timestamp, event type, user description, and
  agent-generated context summary.
- **AC-05:** The user does not need to memorize category names. The system determines the event type.

### F-05: Synthesis (`/case-study-synthesize`)

A skill that reads all captured data and produces two deliverables.

- **AC-01:** Invoked via `/case-study-synthesize` at build completion or any milestone.
- **AC-02:** Reads all JSONL log files accumulated across sessions.
- **AC-03:** Produces a **case study** draft: an evidence-backed narrative covering successes, failures, and how
  failures were addressed. Designed to populate the `case-study/` placeholders in the harness engineering guide repo.
- **AC-04:** Produces a **harness guide improvement plan**: actionable changes to guide chapters based on issues
  encountered during the build.
- **AC-05:** Both deliverables cite specific log entries as evidence (by timestamp and event type).

### F-06: Install Script

A single Python script that seeds the meta-harness into a target repository.

- **AC-01:** Run as one command from the harness engineering guide repo.
- **AC-02:** Symlinks the Git `post-commit` hook into the target repo's `.git/hooks/`.
- **AC-03:** Creates required data directories for JSONL log storage.
- **AC-04:** Prints a confirmation message listing what was set up.
- **AC-05:** Total setup completes in under 2 minutes.

### F-07: Observation-Aware Global Rule

A global rule that primes the agent to be observation-aware during sessions.

- **AC-01:** Loaded at session start (no `paths:` scoping).
- **AC-02:** Makes the agent aware that the observation layer exists and that it should not interfere with its
  operation.
- **AC-03:** Does not alter the agent's behavior on build tasks -- strictly informational context.

## 4. Non-Functional Requirements

- **N-01: Non-interference** -- The observation layer must not break, slow down, or alter the behavior of the main
  harness or the actual build work. It is strictly additive.
- **N-02: Context compaction survival** -- All captured data lives on disk as JSONL files, not in conversation context.
  Sessions can be cleared or compacted without data loss.
- **N-03: Simplicity** -- The entire meta-harness must be understandable in minutes. Fewer moving parts than the
  system it observes.
- **N-04: Separability** -- The meta-harness's files must be clearly discernible from main harness files and removable
  once the case study is complete.
- **N-05: Fast setup** -- If seeding takes more than a few minutes, it has failed.

## 5. Data Format

- All observations are stored as JSONL (one JSON object per line, one file per event category or one unified log).
- Data is designed for machine consumption (AI-driven synthesis and/or deterministic Python scripts), not human reading.
- No intermediate aggregation, metrics dashboards, or Markdown templates for humans to fill in.

## 6. Non-Goals (Explicit)

The following are explicitly NOT in scope:

- Per-phase ceremony: no mandatory retrospectives or phase gates. Continuous logging only.
- Category taxonomy the user must memorize: the system determines event types, not the human.
- Metrics dashboards or intermediate aggregation: raw JSONL in, synthesized deliverables out.
- Markdown templates for humans to fill in: structured JSON written by scripts, not humans copying templates.
- Real-time reporting or visualization: data is consumed at synthesis time, not during the build.
- Multi-user support: single harness engineer is the only user.
- Configuration UI: all configuration is in harness files (rules, skills, hooks, scripts).

## 7. Deliverables

The meta-harness produces two outputs at synthesis time:

1. **Case study** -- fills out the `case-study/` placeholders in the harness engineering guide repo with a real,
   evidence-backed narrative.
2. **Harness guide improvement plan** -- actionable changes to guide chapters based on issues encountered during
   the build.

## 8. Open Questions

- **OQ-01:** Should JSONL logs use one unified file or separate files per event category? (Design decision for
  architecture.)
- **OQ-02:** Exact placement strategy for meta-harness files within the target repo -- how to keep them clearly
  separable from the main harness. (Design decision for architecture.)
- **OQ-03:** Should the `Stop` hook session summary include token/cost estimates if available, or just activity
  descriptions?
- **OQ-04:** Should `/synthesize` produce output as Markdown files, or write directly into the guide repo structure?
