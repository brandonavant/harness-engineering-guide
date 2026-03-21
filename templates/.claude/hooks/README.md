# Claude Code Hooks

<!-- WHY HOOKS EXIST:
Hooks are deterministic scripts that run automatically on tool events (before/after
file edits, command execution, etc.). Unlike skills (which rely on the agent choosing
to invoke them), hooks fire mechanically every time. Use them for guardrails that must
never be skipped: linting after edits, blocking secret writes, enforcing file boundaries. -->

## What Are Hooks?

Hooks are commands configured in `.claude/settings.json` that run on specific Claude Code tool
events. They execute outside the LLM -- they are deterministic scripts, not AI-generated responses.
This makes them reliable for enforcement tasks.

**Key event types:**
- `PreToolUse` -- runs BEFORE a tool executes (can block the action with exit code 2)
- `PostToolUse` -- runs AFTER a tool succeeds (output added to agent context)
- `PostToolUseFailure` -- runs AFTER a tool fails

Other events include `Stop`, `SubagentStop`, `Notification`, `UserPromptSubmit`, and more. See the
[official hooks documentation](https://code.claude.com/docs/en/hooks) for the complete list.

**Matching:** Hooks specify a `matcher` (a regex pattern matched against the tool name) to scope
when they fire. For example, `Edit|Write` matches file edit tools, `Bash` matches shell commands,
and `mcp__.*` matches any MCP tool.

## Configuration

Add hooks to `.claude/settings.json`:

**[CUSTOMIZE]** Replace the linter commands, directory paths, and script paths below with your
project's actual tools and structure.

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "cd apps/backend && ruff check --fix . 2>&1 | head -20",
            "timeout": 30,
            "statusMessage": "Linting Python files..."
          }
        ]
      },
      {
        "matcher": "Edit|Write",
        "hooks": [
          {
            "type": "command",
            "command": "cd apps/frontend && npx tsc --noEmit 2>&1 | head -20",
            "timeout": 60,
            "statusMessage": "Type-checking TypeScript..."
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "Write",
        "hooks": [
          {
            "type": "command",
            "command": "scripts/check-for-secrets.sh",
            "statusMessage": "Scanning for hardcoded secrets..."
          }
        ]
      }
    ]
  }
}
```

## Hook Examples

### PostToolUse: Lint Python Files

Runs ruff on the backend directory after any file edit. Catches lint errors before they
accumulate. The `--fix` flag auto-corrects simple issues.

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": "cd apps/backend && ruff check --fix . 2>&1 | tail -5",
      "timeout": 30
    }
  ]
}
```

### PostToolUse: Type-Check TypeScript

Runs the TypeScript compiler in check mode after any file edit. Catches type errors
immediately instead of discovering them at build time.

```json
{
  "matcher": "Edit|Write",
  "hooks": [
    {
      "type": "command",
      "command": "cd apps/frontend && npx tsc --noEmit 2>&1 | head -20",
      "timeout": 60
    }
  ]
}
```

### PreToolUse: Block Secret Writes

Inspects proposed file content before it is written. The hook receives tool input as JSON on
stdin (including `tool_input.content` for Write). Exit code 2 blocks the write; exit 0 allows it.

```json
{
  "matcher": "Write",
  "hooks": [
    {
      "type": "command",
      "command": "scripts/check-for-secrets.sh",
      "statusMessage": "Scanning for hardcoded secrets..."
    }
  ]
}
```

## When to Use Hooks vs. Skills vs. CI

| Mechanism | Timing | Deterministic? | Use For |
|-----------|--------|----------------|---------|
| **Hooks** | Every tool event | Yes | Linting, type-checking, secret scanning |
| **Skills** | Agent invokes explicitly | No (agent must choose) | Checklists, design review, contract validation |
| **CI** | On push / PR | Yes | Full test suite, build verification, integration tests |

**Rule of thumb:**
- If it must run on EVERY edit and requires no judgment: **hook**.
- If it requires reading context and making assessments: **skill** (make it mandatory in CLAUDE.md).
- If it takes more than a few seconds or needs the full codebase: **CI**.

## Hook Input and Output

Hooks receive JSON on stdin with context about the tool invocation:

```json
{
  "session_id": "abc123",
  "cwd": "/path/to/project",
  "tool_name": "Edit",
  "tool_input": {
    "file_path": "/path/to/file.py",
    "old_string": "...",
    "new_string": "..."
  }
}
```

**Exit codes:**

| Exit Code | Meaning | Behavior |
|-----------|---------|----------|
| **0** | Success | Stdout added to agent context (parsed as JSON if valid) |
| **2** | Block | For PreToolUse: blocks the tool call. Stderr shown as error. |
| **Other** | Non-blocking error | Stderr shown in verbose mode. Execution continues. |

The `$CLAUDE_PROJECT_DIR` environment variable provides the project root path.

## Tips

- Keep hooks fast (under 2 seconds). Slow hooks degrade the development experience.
- For PostToolUse hooks, exit 0 so output reaches the agent. Use `|| true` if the check itself
  might return a non-zero exit.
- Pipe output through `head` or `tail` to keep hook output concise.
- Test hooks manually before adding them: run the command and pipe sample JSON to stdin.
- Hooks run in the project root directory. Use `cd` to change to subdirectories if needed.
- Set explicit `timeout` values to prevent runaway commands (default is 600 seconds).
