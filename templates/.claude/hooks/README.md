# Claude Code Hooks

<!-- WHY HOOKS EXIST:
Hooks are deterministic scripts that run automatically on tool events (before/after
file edits, command execution, etc.). Unlike skills (which rely on the agent choosing
to invoke them), hooks fire mechanically every time. Use them for guardrails that must
never be skipped: linting after edits, blocking secret commits, enforcing file boundaries. -->

## What Are Hooks?

Hooks are shell commands configured in `.claude/settings.json` that run on specific
Claude Code tool events. They execute outside the LLM -- they are deterministic scripts,
not AI-generated responses. This makes them reliable for enforcement tasks.

**Hook types:**
- `PreToolUse` -- runs BEFORE a tool executes (can block the action)
- `PostToolUse` -- runs AFTER a tool executes (can report issues)

**Matching:** Hooks specify a `matcher` (the tool name) and optional `filePath` patterns
to scope when they fire.

## Configuration

Add hooks to `.claude/settings.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Edit|Write",
        "hook": "cp \"$CLAUDE_FILE_PATH\" \"$CLAUDE_FILE_PATH.bak\" 2>/dev/null || true",
        "description": "Backup file before modification"
      }
    ],
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "filePath": "\\.py$",
        "hook": "cd apps/backend && ruff check --fix \"$CLAUDE_FILE_PATH\" 2>&1 | tail -5",
        "description": "Auto-lint Python files after edit"
      },
      {
        "matcher": "Edit|Write",
        "filePath": "\\.(ts|tsx)$",
        "hook": "cd apps/frontend && npx tsc --noEmit 2>&1 | head -20",
        "description": "Type-check TypeScript files after edit"
      },
      {
        "matcher": "Edit|Write",
        "hook": "grep -rn 'AKIA\\|sk-\\|password\\s*=' \"$CLAUDE_FILE_PATH\" && echo 'WARNING: Possible hardcoded secret detected' || true",
        "description": "Scan for hardcoded secrets after any file edit"
      }
    ]
  }
}
```

## Hook Examples

### Pre-Edit: Backup Before Modification

Creates a `.bak` copy of any file before Claude edits it. Useful during early development
when you want an easy rollback path.

```json
{
  "matcher": "Edit|Write",
  "hook": "cp \"$CLAUDE_FILE_PATH\" \"$CLAUDE_FILE_PATH.bak\" 2>/dev/null || true"
}
```

### Post-Edit: Lint Python Files

Runs ruff on any Python file immediately after it is modified. Catches lint errors before
they accumulate. The `--fix` flag auto-corrects simple issues.

```json
{
  "matcher": "Edit|Write",
  "filePath": "\\.py$",
  "hook": "cd apps/backend && ruff check --fix \"$CLAUDE_FILE_PATH\" 2>&1 | tail -5"
}
```

### Post-Edit: Type-Check TypeScript

Runs the TypeScript compiler in check mode after any `.ts` or `.tsx` edit. Catches type
errors immediately instead of discovering them at build time.

```json
{
  "matcher": "Edit|Write",
  "filePath": "\\.(ts|tsx)$",
  "hook": "cd apps/frontend && npx tsc --noEmit 2>&1 | head -20"
}
```

### Post-Edit: Secret Detection

Scans edited files for patterns that look like hardcoded secrets (AWS keys, API keys,
password assignments). Prints a warning if found. Does not block the edit -- just alerts.

```json
{
  "matcher": "Edit|Write",
  "hook": "grep -rn 'AKIA\\|sk-\\|password\\s*=' \"$CLAUDE_FILE_PATH\" && echo 'WARNING: Possible hardcoded secret detected' || true"
}
```

## When to Use Hooks vs. Skills vs. CI

| Mechanism | Timing | Deterministic? | Use For |
|-----------|--------|----------------|---------|
| **Hooks** | Every tool event | Yes | Linting, type-checking, secret scanning, file backups |
| **Skills** | Agent invokes explicitly | No (agent must choose) | Checklists, design review, contract validation |
| **CI** | On push / PR | Yes | Full test suite, build verification, integration tests |

**Rule of thumb:**
- If it must run on EVERY edit and requires no judgment: **hook**.
- If it requires reading context and making assessments: **skill** (make it mandatory in CLAUDE.md).
- If it takes more than a few seconds or needs the full codebase: **CI**.

## Environment Variables Available to Hooks

| Variable | Description |
|----------|-------------|
| `CLAUDE_FILE_PATH` | Absolute path of the file being edited |
| `CLAUDE_TOOL_NAME` | Name of the tool being used (Edit, Write, Bash, etc.) |

## Tips

- Keep hooks fast (under 2 seconds). Slow hooks degrade the development experience.
- Use `|| true` at the end if the hook should warn but not block.
- Pipe output through `head` or `tail` to keep hook output concise.
- Test hooks manually before adding them to settings: run the command with a real file path.
- Hooks run in the project root directory. Use `cd` to change to subdirectories if needed.
