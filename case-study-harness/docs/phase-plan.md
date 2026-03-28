# Case Study Harness -- Phase Plan

## Document Header

| Field          | Value                                            |
|----------------|--------------------------------------------------|
| Version        | v1.2                                                                                |
| Date           | 2026-03-28                                                                          |
| Author         | Brandon Avant                                                                       |
| Change Summary | Fix hook types: split Stop/SessionEnd, rename session_summary to turn_summary |

---

## Overview

The MVP is decomposed into four phases. Each phase produces a working increment that can be tested
independently before moving to the next. Dependencies flow strictly downward: Phase 2 depends on Phase 1,
Phase 3 depends on Phases 1-2, and Phase 4 depends on Phase 1 only.

```
Phase 1: Data Foundation & Logging Scripts
    ↓
Phase 2: Automatic Detection Layer (hooks + rule)
    ↓
Phase 3: Skills (capture + synthesize)

Phase 1 ──▶ Phase 4: Install Script (parallel with 2-3)
```

---

## Phase 1: Data Foundation & Logging Scripts

**Goal:** Establish the directory structure, data format, and all Python logging scripts. After this phase,
every script can be invoked from the command line and produces valid JSONL output.

**Delivers:** F-01 (partial), F-02 (partial), F-03 (partial) -- the logging logic, without the hook wiring.

### Work Items

1. Create directory structure: `case-study-harness/scripts/`, `case-study-harness/hooks/`,
   `case-study-harness/data/`.
2. Add `.gitignore` entry for `case-study-harness/data/` so log files are never committed.
3. Implement `scripts/log_harness_change.py` -- reads hook environment/arguments, appends one
   `harness_change` entry to `data/harness-changes.jsonl`.
4. Implement `scripts/log_friction.py` -- reads hook environment/arguments, appends one `friction` entry
   to `data/friction-events.jsonl`.
5. Implement `scripts/log_turn_summary.py` -- reads Stop hook JSON from stdin, appends one
   `turn_summary` entry to `data/turn-summaries.jsonl`. The Stop hook fires after each Claude response.
6. Implement `scripts/log_session_end.py` -- reads SessionEnd hook JSON from stdin, appends one
   `session_end` entry to `data/session-ends.jsonl`. The SessionEnd hook fires when a session terminates.
7. Implement `scripts/log_git_harness_change.py` -- reads the most recent commit, checks for harness file
   changes, appends `harness_change` entries (with `commit_sha` and `commit_msg`) to
   `data/harness-changes.jsonl`.

### Acceptance Criteria

- [x] **P1-AC-01:** Each script runs without error when invoked with valid arguments and produces a
  single-line JSON object appended to the correct file.
- [x] **P1-AC-02:** Every JSONL entry contains the base fields (`timestamp`, `event_type`, `source`) plus
  the category-specific fields defined in the architecture data schema (Section 4).
- [x] **P1-AC-03:** `log_harness_change.py` writes entries with `event_type: "harness_change"` and
  `source: "hook"`.
- [x] **P1-AC-04:** `log_friction.py` writes entries with `event_type: "friction"` and `source: "hook"`.
- [x] **P1-AC-05:** `log_turn_summary.py` writes entries with `event_type: "turn_summary"` and
  `source: "hook"`, including `session_id`.
- [x] **P1-AC-10:** `log_session_end.py` writes entries with `event_type: "session_end"` and
  `source: "hook"`, including `session_id`, `reason`, and `token_usage` (null when not available).
- [x] **P1-AC-06:** `log_git_harness_change.py` writes entries with `event_type: "harness_change"` and
  `source: "git_hook"`, including `commit_sha` and `commit_msg`.
- [x] **P1-AC-07:** `log_git_harness_change.py` produces no output and exits cleanly when the commit
  contains no harness file changes.
- [x] **P1-AC-08:** `case-study-harness/data/` is gitignored.
- [x] **P1-AC-09:** All scripts use Python 3, `#!/usr/bin/env python3` shebangs, Google-style docstrings,
  and type hints.

---

## Phase 2: Automatic Detection Layer

**Goal:** Wire the scripts into Claude Code hooks, create the native Git hook, and add the global
observation-awareness rule. After this phase, observations are captured automatically during Claude Code
sessions and on Git commits.

**Delivers:** F-01, F-02, F-03, F-07 -- automatic capture is fully operational.

### Work Items

1. Define `PostToolUse` hook entry in `case-study-harness/claude/hooks-config.json` that fires on Edit/Write
   operations targeting harness paths (`.claude/`, `CLAUDE.md`, `settings.json`) and invokes
   `scripts/log_harness_change.py`.
2. Define `PostToolUseFailure` hook entry in `case-study-harness/claude/hooks-config.json` that invokes
   `scripts/log_friction.py`.
3. Define `Stop` hook entry in `case-study-harness/claude/hooks-config.json` that invokes
   `scripts/log_turn_summary.py`.
4. Define `SessionEnd` hook entry in `case-study-harness/claude/hooks-config.json` that invokes
   `scripts/log_session_end.py`.
5. Create `case-study-harness/hooks/post-commit` -- a thin wrapper that invokes
   `scripts/log_git_harness_change.py`. Must be executable.
6. Create `case-study-harness/claude/rules/case-study-observer.md` -- global rule (no `paths:` frontmatter)
   that makes the agent aware of the observation layer without altering build behavior.

### Acceptance Criteria

> **Testing note:** These criteria describe behavior after the source files are deployed to a target repo.
> Verify by manually placing the files in a test repo's `.claude/` directory or by running the Phase 4
> install script if it is available.

- [ ] **P2-AC-01:** Editing a harness file (e.g., `.claude/rules/`) in the target repo during a Claude Code
  session produces a `harness_change` entry in `data/harness-changes.jsonl`.
- [ ] **P2-AC-02:** A tool failure during a Claude Code session produces a `friction` entry in
  `data/friction-events.jsonl`.
- [ ] **P2-AC-03:** Ending a Claude Code session produces a `session_end` entry in
  `data/session-ends.jsonl`.
- [ ] **P2-AC-08:** Each Claude Code response produces a `turn_summary` entry in
  `data/turn-summaries.jsonl`.
- [ ] **P2-AC-04:** Committing a harness file change via Git (outside Claude Code) produces a
  `harness_change` entry with `source: "git_hook"` and a valid `commit_sha`.
- [ ] **P2-AC-05:** Committing a non-harness file change via Git produces no log entry.
- [ ] **P2-AC-06:** The global rule loads at session start and does not alter agent behavior on build tasks.
- [ ] **P2-AC-07:** Hook scripts do not modify the working tree, stage files, or write outside
  `case-study-harness/data/`.

---

## Phase 3: Skills

**Goal:** Implement the two user-invoked skills: manual observation capture and end-of-build synthesis.
After this phase, the full observation + synthesis pipeline is operational.

**Delivers:** F-04, F-05 -- manual capture and synthesis are available.

### Work Items

1. Create `case-study-harness/claude/skills/case-study-capture/SKILL.md` -- the `/case-study-capture` skill
   that reads conversation context, accepts a user description, classifies the event type, and writes a
   `manual` entry to `data/manual-observations.jsonl`.
2. Create `case-study-harness/claude/skills/case-study-synthesize/SKILL.md` -- the `/case-study-synthesize`
   skill that reads all `data/*.jsonl` files, produces a case study draft and a harness guide improvement
   plan, writes both to `case-study-harness/output/`.

### Acceptance Criteria

- [ ] **P3-AC-01:** `/case-study-capture` is invocable during a Claude Code session.
- [ ] **P3-AC-02:** The capture skill writes a valid `manual` JSONL entry with `category`,
  `user_description`, and `context_summary` fields.
- [ ] **P3-AC-03:** The skill determines the `category` value -- the user does not need to specify or
  memorize category names.
- [ ] **P3-AC-04:** `/case-study-synthesize` is invocable during a Claude Code session.
- [ ] **P3-AC-05:** The synthesize skill reads all five JSONL log files.
- [ ] **P3-AC-06:** The synthesize skill produces a case study Markdown file citing specific log entries
  (by timestamp and event type) as evidence.
- [ ] **P3-AC-07:** The synthesize skill produces a harness guide improvement plan Markdown file citing
  specific log entries as evidence.
- [ ] **P3-AC-08:** Both deliverables are written to `case-study-harness/output/`, not directly into the
  guide repo.

---

## Phase 4: Install Script

**Goal:** Implement the install script that seeds the meta-harness into a target repository. After this
phase, the full meta-harness can be deployed to any repo with a single command.

**Delivers:** F-06 -- install mechanism is operational.

### Work Items

1. Implement `case-study-harness/install.py` -- accepts a target repo path and performs: (a) creates
   `case-study-harness/data/` in the target repo, (b) symlinks `.git/hooks/post-commit` to
   `case-study-harness/hooks/post-commit`, (c) copies `case-study-harness/claude/rules/` into
   `<target>/.claude/rules/`, (d) copies `case-study-harness/claude/skills/case-study-capture/` and
   `case-study-harness/claude/skills/case-study-synthesize/` into `<target>/.claude/skills/`, (e) merges
   hook definitions from `case-study-harness/claude/hooks-config.json` into
   `<target>/.claude/settings.json` (additive -- does not remove existing entries), (f) prints
   confirmation listing what was set up.
2. Ensure idempotency: running the script twice produces the same result without errors. File copies skip
   files with identical content. Hook config merge skips entries already present.
3. Ensure safe failure: if an existing `post-commit` hook is detected, print a warning and exit without
   modifying the target repo. If a rule or skill with the same name already exists, warn and skip that
   file but continue with remaining actions.
4. Handle missing `<target>/.claude/` directory: create it if it does not exist. Handle missing
   `<target>/.claude/settings.json`: create a minimal valid JSON file containing only the case-study hook
   definitions.

### Acceptance Criteria

- [ ] **P4-AC-01:** `install.py` accepts a target repo path as a positional argument.
- [ ] **P4-AC-02:** Running the script creates `case-study-harness/data/` in the target repo.
- [ ] **P4-AC-03:** Running the script symlinks `.git/hooks/post-commit` to
  `case-study-harness/hooks/post-commit`.
- [ ] **P4-AC-04:** Running the script prints a confirmation listing what was set up.
- [ ] **P4-AC-05:** Running the script twice produces the same result (idempotent).
- [ ] **P4-AC-06:** If an existing `post-commit` hook exists, the script prints a warning and exits
  without modifying the target repo.
- [ ] **P4-AC-07:** If `.git/` does not exist in the target path, the script prints a warning and exits.
- [ ] **P4-AC-08:** The script uses Python 3, `#!/usr/bin/env python3` shebang, Google-style docstrings,
  and type hints.
- [ ] **P4-AC-09:** Total setup completes in under 2 minutes.
- [ ] **P4-AC-10:** Running the script copies `case-study-observer.md` into
  `<target>/.claude/rules/`.
- [ ] **P4-AC-11:** Running the script copies `case-study-capture/` and `case-study-synthesize/` skill
  directories into `<target>/.claude/skills/`.
- [ ] **P4-AC-12:** Running the script merges hook definitions from `hooks-config.json` into
  `<target>/.claude/settings.json` without removing existing entries.
- [ ] **P4-AC-13:** If `<target>/.claude/settings.json` does not exist, the script creates it with the
  case-study hook definitions.
- [ ] **P4-AC-14:** If a rule file or skill directory with the same name already exists in the target,
  the script prints a warning and skips that file/directory.
- [ ] **P4-AC-15:** After installation, starting a Claude Code session in the target repo loads the
  case-study rule and skills.
