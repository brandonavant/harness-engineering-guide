# Case Study Harness -- Architecture Document

## Document Header

| Field          | Value                                                                         |
|----------------|-------------------------------------------------------------------------------|
| Version        | v1.3                                                                          |
| Date           | 2026-03-28                                                                    |
| Author         | Brandon Avant                                                                 |
| Change Summary | Add UserPromptSubmit and general PostToolUse hooks; enrich turn_summary and friction schemas |

---

## 1. Tech Stack Summary

This is not an application. It is a set of Claude Code harness mechanisms and supporting scripts. Every row below is a
constraint, not a suggestion.

| Layer             | Technology           | Notes                                                                   |
|-------------------|----------------------|-------------------------------------------------------------------------|
| Rules             | `.claude/rules/`     | One global rule; no path-scoped rules                                   |
| Skills            | `.claude/skills/`    | `/case-study-capture`, `/case-study-synthesize`                         |
| Hooks             | Claude Code hooks    | `UserPromptSubmit`, `PostToolUse`, `PostToolUseFailure`, `Stop`, `SessionEnd` |
| Git hook          | Native `post-commit` | Detects harness file changes in commits made outside Claude Code        |
| Scripts           | Python 3             | Hook handlers that write JSONL entries; install script                  |
| Data store        | JSONL files          | One file per event category, append-only                                |
| Install mechanism | Python 3 script      | Seeds meta-harness into target repo via symlinks and directory creation |

## 2. System Architecture

```
Claude Code Session
├── UserPromptSubmit hook (fires when user submits a prompt)
│   └── scripts/log_user_prompt.py     ──▶  data/user-prompts.jsonl
├── PostToolUse hook (Edit/Write on harness paths)
│   └── scripts/log_harness_change.py  ──▶  data/harness-changes.jsonl
├── PostToolUse hook (all tools -- general activity trail)
│   └── scripts/log_tool_use.py        ──▶  data/tool-uses.jsonl
├── PostToolUseFailure hook
│   └── scripts/log_friction.py        ──▶  data/friction-events.jsonl
├── Stop hook (fires after each Claude response)
│   └── scripts/log_turn_summary.py    ──▶  data/turn-summaries.jsonl
├── SessionEnd hook (fires when session terminates)
│   └── scripts/log_session_end.py     ──▶  data/session-ends.jsonl
├── /case-study-capture skill
│   └── (agent writes directly)        ──▶  data/manual-observations.jsonl
└── /case-study-synthesize skill
    └── (agent reads all data/*.jsonl)  ──▶  case study + improvement plan

Git (outside Claude Code)
└── .git/hooks/post-commit (symlink)
    └── scripts/log_git_harness_change.py ──▶  data/harness-changes.jsonl
```

### Hook Layer

Hooks fire automatically during Claude Code sessions. Each hook invokes a Python script that appends a single JSONL
entry to the appropriate log file. Hook scripts are fast, side-effect-free (append-only I/O), and never modify the
main harness or working tree.

### Skill Layer

Skills are invoked on demand by the user. `/case-study-capture` writes one entry.
`/case-study-synthesize` reads all log files and produces deliverables.

### Git Hook Layer

The native `post-commit` hook covers harness changes made outside Claude Code (e.g., manual editor tweaks). It writes
to the same `harness-changes.jsonl` file as the `PostToolUse` hook, using the same schema with an additional
`commit_sha`
field. Because the entry is written after the commit, it lands in a subsequent commit -- acceptable since the entry
references the source SHA for traceability.

### Data Layer

All observation data lives on disk as JSONL files in `data/`. No data is stored in conversation context, memory, or
any external system. Sessions can be cleared or compacted without data loss (PRD N-02).

## 3. File Placement Strategy

The meta-harness must be clearly separable from the host repo's main harness (PRD N-04). The harness source code lives
in the guide repo under `case-study-harness/`, but the guide repo has its own `.claude/` directory for guide authoring.
To avoid activating case-study mechanisms in the wrong environment, rules, skills, and hook config are stored as
**source files** under `case-study-harness/claude/` and deployed to a target repo's `.claude/` directory by the
`install` script.

### Source layout (in the guide repo)

```
case-study-harness/
├── claude/                                     ◀ source files for deployment (inert here)
│   ├── rules/
│   │   └── case-study-observer.md
│   ├── skills/
│   │   ├── case-study-capture/
│   │   │   └── SKILL.md
│   │   └── case-study-synthesize/
│   │       └── SKILL.md
│   └── hooks-config.json                       ◀ hook entries to merge into settings.json
├── scripts/
│   ├── log_user_prompt.py
│   ├── log_tool_use.py
│   ├── log_harness_change.py
│   ├── log_friction.py
│   ├── log_turn_summary.py
│   ├── log_session_end.py
│   └── log_git_harness_change.py
├── hooks/
│   └── post-commit                             ◀ symlink source
├── data/                                       ◀ gitignored; created by install script
└── install.py
```

### Deployed layout (after install, in the target repo)

```
target-repo/
├── .claude/
│   ├── rules/
│   │   └── case-study-observer.md              ◀ copied from source by install script
│   ├── skills/
│   │   ├── case-study-capture/
│   │   │   └── SKILL.md                        ◀ copied from source by install script
│   │   └── case-study-synthesize/
│   │       └── SKILL.md                        ◀ copied from source by install script
│   └── settings.json                           ◀ hook entries merged by install script
├── .git/hooks/
│   └── post-commit                             ◀ symlink → case-study-harness/hooks/post-commit
├── case-study-harness/
│   ├── claude/                                 ◀ source files (remain here as reference)
│   ├── scripts/
│   ├── hooks/
│   │   └── post-commit                         ◀ symlink source
│   ├── data/
│   │   ├── user-prompts.jsonl
│   │   ├── tool-uses.jsonl
│   │   ├── harness-changes.jsonl
│   │   ├── friction-events.jsonl
│   │   ├── turn-summaries.jsonl
│   │   ├── session-ends.jsonl
│   │   └── manual-observations.jsonl
│   └── install.py
```

**Separability rules:**

- All scripts, source files, and data live under `case-study-harness/`. Removing this directory removes the bulk of the
  meta-harness.
- The `install` script is the single entry point for deploying `.claude/` files into a target repo. It copies rules and
  skills and merges hook definitions into `settings.json`.
- Rules and skills use the `case-study-` prefix so they are visually and programmatically distinguishable from the host
  repo's own harness files.
- Hook definitions in `settings.json` are additive. They can be identified by their script paths
  (`case-study-harness/scripts/`) and removed without affecting other hooks.
- The Git hook symlink points into `case-study-harness/hooks/`. Removing the directory breaks the symlink, which Git
  treats as a missing hook (no-op).
- Full removal: delete the `case-study-` prefixed rules and skills from `.claude/`, remove the case-study hook entries
  from `.claude/settings.json`, delete the `.git/hooks/post-commit` symlink, and delete `case-study-harness/`.

## 4. Data Schema

All JSONL entries share a common base structure. Each event category extends it.

### Base Fields

| Field        | Type   | Description                                                                   |
|--------------|--------|-------------------------------------------------------------------------------|
| `timestamp`  | string | ISO 8601 UTC (e.g., `2026-03-27T19:30:00Z`)                                   |
| `event_type` | string | One of: `user_prompt`, `tool_use`, `harness_change`, `friction`, `turn_summary`, `session_end`, `manual` |
| `source`     | string | One of: `hook`, `git_hook`, `skill`                                           |

### user_prompt

| Field        | Type   | Description                                         |
|--------------|--------|-----------------------------------------------------|
| `session_id` | string | Links the prompt to its session for correlation     |
| `prompt`     | string | The user's prompt text (max 2000 chars)             |

### tool_use

| Field          | Type   | Description                                         |
|----------------|--------|-----------------------------------------------------|
| `session_id`   | string | Links the tool use to its session for correlation   |
| `tool_name`    | string | The Claude Code tool that was invoked               |
| `tool_summary` | string | Brief description of what the tool did (max 200 chars) |

### harness_change

| Field        | Type   | Description                                      |
|--------------|--------|--------------------------------------------------|
| `file_path`  | string | Path relative to repo root                       |
| `action`     | string | One of: `created`, `modified`, `deleted`         |
| `summary`    | string | Brief description of what changed                |
| `commit_sha` | string | Present only when source is `git_hook`; nullable |
| `commit_msg` | string | Present only when source is `git_hook`; nullable |

### friction

| Field           | Type   | Description                                       |
|-----------------|--------|---------------------------------------------------|
| `session_id`    | string | Links the friction event to its session            |
| `tool_name`     | string | The tool that failed                               |
| `error_summary` | string | Condensed error message                            |
| `context`       | string | What the agent was attempting                      |

### turn_summary

| Field              | Type    | Description                                                  |
|--------------------|---------|--------------------------------------------------------------|
| `session_id`       | string  | Links the turn to its session for correlation                |
| `description`      | string  | High-level summary of what Claude responded (max 2000 chars) |
| `stop_hook_active` | boolean | Whether the stop hook is active (mid-turn vs. complete)      |

### session_end

| Field         | Type   | Description                                                          |
|---------------|--------|----------------------------------------------------------------------|
| `session_id`  | string | The session that ended                                               |
| `reason`      | string | Why the session ended (e.g., `prompt_input_exit`, `clear`, `logout`) |
| `token_usage` | object | Nullable; `{"input": int, "output": int}` if available from session  |

### manual

| Field              | Type   | Description                                                                                         |
|--------------------|--------|-----------------------------------------------------------------------------------------------------|
| `category`         | string | Agent-assigned: `successful_pattern`, `human_override`, `context_architecture`, `friction`, `other` |
| `user_description` | string | The observation as described by the user                                                            |
| `context_summary`  | string | Agent-generated context from the conversation                                                       |

## 5. JSONL Log File Strategy

Observations are split into separate files by event category (one file per `event_type`):

| File                        | Written by                                           | Event type       |
|-----------------------------|------------------------------------------------------|------------------|
| `user-prompts.jsonl`        | `log_user_prompt.py`                                 | `user_prompt`    |
| `tool-uses.jsonl`           | `log_tool_use.py`                                    | `tool_use`       |
| `harness-changes.jsonl`     | `log_harness_change.py`, `log_git_harness_change.py` | `harness_change` |
| `friction-events.jsonl`     | `log_friction.py`                                    | `friction`       |
| `turn-summaries.jsonl`      | `log_turn_summary.py`                                | `turn_summary`   |
| `session-ends.jsonl`        | `log_session_end.py`                                 | `session_end`    |
| `manual-observations.jsonl` | `/case-study-capture` skill                          | `manual`         |

**Why separate files over one unified log:** Each file can be read independently during synthesis (e.g., "show me all
friction events" is a single file read, not a filter across a large log). It also makes it obvious at a glance what
kinds of data have been captured -- an empty file means no events of that type. The tradeoff is that chronological
ordering across categories requires merging by timestamp, but synthesis is the only consumer, and it handles that.

## 6. Install Script Behavior

`install.py` seeds the meta-harness into a target repo. It is idempotent -- running it twice produces the same result.

**Inputs:** Target repo path (positional argument).

**Actions:**

1. Create `<target>/.claude/` directory if it does not exist.
2. Create `case-study-harness/data/` in the target repo if it does not exist.
3. Symlink `.git/hooks/post-commit` → `case-study-harness/hooks/post-commit`. If an existing hook is found or `.git/`
   is missing, print a warning and exit without modifying the target repo (per AD-09).
4. Copy `case-study-harness/claude/rules/` into `<target>/.claude/rules/`. If a file with the same name already exists,
   warn and skip that file.
5. Copy `case-study-harness/claude/skills/case-study-capture/` and
   `case-study-harness/claude/skills/case-study-synthesize/`
   into `<target>/.claude/skills/`. If a skill directory with the same name already exists, warn and skip it.
6. Merge hook definitions from `case-study-harness/claude/hooks-config.json` into `<target>/.claude/settings.json`. This
   is an additive merge: read the existing file (or create a new one), add the case-study hook entries without removing
   existing entries. Skip entries whose commands are already present.
7. Print confirmation listing what was set up.

**Idempotency:** Running the script twice produces the same result. File copies skip files with identical content. Hook
config merge skips entries already present. The Git hook symlink check is inherently idempotent.

**Conflict handling:** The Git hook conflict is fatal -- the script exits without modifying the target repo (AD-09).
Rule
and skill conflicts are non-fatal -- the script warns and skips the conflicting file but continues with remaining
actions. A single rule name collision should not prevent skill deployment.

**What it does NOT do:**

- Copy Python scripts. They are referenced by relative path from `case-study-harness/scripts/`, which is already in the
  target repo alongside the rest of the harness.
- Modify the target repo's `CLAUDE.md`.
- Commit anything.

## 7. Architecture Decisions

### AD-01: Symlinks for Git Hooks Over Copying

**Decision:** The `install` script symlinks the `post-commit` hook rather than copying it.
**Reasoning:** A symlink stays in sync with the source. If the hook script is updated in `case-study-harness/hooks/`,
every repo that symlinked it gets the fix immediately -- no re-install step. A copied hook is a snapshot that drifts
silently. Since the meta-harness is developed in one repo and seeded into others, single-source-of-truth matters.

### AD-02: Separate JSONL Files Per Event Category

**Decision:** One JSONL file per event type, not a single unified log.
**Reasoning:** Separate files make targeted reads trivial (one `open()` call, no filtering) and provide at-a-glance
visibility into what has been captured. The only downside -- cross-category chronological ordering -- is a merge-by-
timestamp operation that the synthesis skill handles once at read time.

### AD-03: Scripts Invoked by Hooks, Not Inline Logic

**Decision:** Hooks invoke standalone Python scripts rather than embedding logic in hook definitions or shell
one-liners.
**Reasoning:** Python scripts are testable, readable, and follow the repo's scripting convention (Python 3, Google-style
docstrings, type hints). Shell one-liners in hook config are fragile and hard to debug. Each script does one thing:
read inputs, append one JSONL line, exit.

### AD-04: Data Directory Gitignored, Structure Committed

**Decision:** `case-study-harness/data/` is gitignored. The directory is created by the `install` script. The rest of
the meta-harness structure (scripts, hooks, rules, skills) is committed.
**Reasoning:** JSONL log data is ephemeral, project-specific, and potentially large. It should not be committed to the
harness engineering guide repo or to target repos. The structure (scripts, skills, rules) is the reusable artifact.

### AD-05: Global Rule With No Path Scoping

**Decision:** The observation-awareness rule has no `paths:` frontmatter.
**Reasoning:** Path-scoped rules only inject when Claude reads a matching file -- too late for a behavioral policy that
should be active from session start. A global rule (no `paths:`) loads at session start, ensuring the agent is always
aware of the observation layer regardless of which files it touches.

### AD-06: Skills Write JSONL Directly, Not Via Scripts

**Decision:** The `/case-study-capture` skill writes JSONL entries directly (agent-generated) rather than invoking a
Python script.
**Reasoning:** The skill already runs within an agent context that has full understanding of the conversation. Routing
through a script would require serializing that context into arguments, adding complexity for no benefit. Hook scripts
need to be standalone because hooks run outside the agent's reasoning -- skills do not have that constraint.

## 8. Constraints and Invariants

- **Non-interference is the top constraint.** No hook, script, or rule in the meta-harness may alter the behavior of
  the main harness or the build work. All operations are append-only writes to `case-study-harness/data/`. Hook scripts
  must not modify the working tree, stage files, or write outside the data directory.
- **Hook scripts must be fast.** A slow hook degrades the Claude Code session experience. Each script appends one line
  and exits. No network calls, no file scanning, no aggregation.
- **JSONL entries are immutable.** Once written, log entries are never modified or deleted. Synthesis reads the full
  history. If an entry is wrong, a subsequent corrective entry can be appended, but the original stays.
- **Symlinks must point to committed files.** The Git hook symlink target (`case-study-harness/hooks/post-commit`) must
  exist in the repo. A broken symlink is a silent no-op, which means harness changes go unlogged without warning.

### AD-07: Two Hooks for Session-Level Data (Stop + SessionEnd)

**Decision:** The `Stop` hook captures per-turn summaries (`last_assistant_message` after each Claude response). The
`SessionEnd` hook captures session boundary events (when the session terminates). Token usage is recorded on the
`session_end` entry (nullable until the hook exposes it).
**Reasoning:** `Stop` fires after every Claude response — useful for logging what the agent did each turn, but not a
session boundary. `SessionEnd` fires once when the session actually ends, providing the structural marker that synthesis
needs to delineate sessions. Using both gives per-turn detail and session boundaries without losing information.

### AD-08: Synthesis Produces Generic Markdown in the Target Repo

**Decision:** `/case-study-synthesize` writes Markdown files into the target repo (e.g., `case-study-harness/output/`),
not directly into the guide repo's `case-study/` structure.
**Reasoning:** The meta-harness should not assume anything about the guide repo's location or structure. The engineer
moves the output into the guide repo manually. This keeps the meta-harness self-contained and the target repo unaware
of the guide's directory layout.

### AD-09: Install Script Bails on Git Hook Conflicts

**Decision:** If the `install` script encounters an existing `post-commit` hook, it prints a warning and exits without
modifying the target repo. No chaining, no overwriting. Rule and skill file conflicts are handled differently: the
script warns and skips the conflicting file but continues with remaining actions.
**Reasoning:** Hook chaining is fragile and adds complexity for a scenario that is unlikely in practice. The engineer
can resolve conflicts manually if they arise. Rule and skill conflicts are less dangerous -- a name collision likely
means the file was already installed, and skipping it does not break the rest of the deployment.

### AD-10: Source Files Stored Under `case-study-harness/claude/`, Not in Guide Repo `.claude/`

**Decision:** Rules, skills, and hook configuration are stored as source files under `case-study-harness/claude/` rather
than directly in the guide repo's `.claude/` directory. The `install` script copies them into the target repo's
`.claude/` at setup time.
**Reasoning:** The guide repo (`harness-engineering-guide`) has its own `.claude/` directory with rules, skills, and
settings that govern guide authoring. Placing case-study-harness files directly in `.claude/` would activate them in the
guide repo, which is not the target environment. The case-study-harness is designed to be deployed into a separate
application repo where the engineer is doing the actual build work. Storing source files under
`case-study-harness/claude/` keeps them inert in the guide repo and deployable to any target.
