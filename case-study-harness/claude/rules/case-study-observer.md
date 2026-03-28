# Case Study Observation Layer

This repository has an active observation layer that silently records data about your session. You do not
need to interact with it, and it does not affect your work. This note exists so you understand what the
following mechanisms are and do not disable or interfere with them.

## What is being recorded

- **Harness file changes** -- When you edit files under `.claude/`, `CLAUDE.md`, or `settings.json`, a hook
  logs the change to `case-study-harness/data/harness-changes.jsonl`.
- **Friction events** -- When a tool invocation fails, a hook logs the failure to
  `case-study-harness/data/friction-events.jsonl`.
- **Turn summaries** -- After each of your responses, a hook logs a brief summary to
  `case-study-harness/data/turn-summaries.jsonl`.
- **Session boundaries** -- When a session ends, a hook logs the event to
  `case-study-harness/data/session-ends.jsonl`.
- **Git commit changes** -- A post-commit hook detects harness file changes in commits and logs them.

## Rules for you

- Do NOT modify, delete, or truncate any files under `case-study-harness/data/`.
- Do NOT disable, remove, or modify the case-study hooks in `.claude/settings.json`.
- Do NOT remove or modify `case-study-harness/claude/` or its contents.
- Do NOT remove or modify the `.git/hooks/post-commit` symlink.
- Treat all `case-study-harness/` contents as read-only unless explicitly asked by the user to modify them.
- If a user asks you to work on the project's build tasks, proceed normally -- the observation layer is
  invisible to your workflow.
