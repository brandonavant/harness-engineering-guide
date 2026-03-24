# Harness File Format Enforcement

> **Note for human engineers**: This rule intentionally has no `paths:` frontmatter. Path-scoped rules only inject into
> context when Claude reads a matching file — too late for a pre-task behavioral policy. Without `paths:`, it loads
> globally at session start.

Before creating or modifying any Claude Code harness file, you MUST fetch the relevant official documentation
page and verify your changes follow the exact format prescribed there. Do not rely on training knowledge,
examples elsewhere in this repo, or MCP index tools.

## Documentation Lookup Table

| File Type                                | Fetch This URL                               |
|------------------------------------------|----------------------------------------------|
| CLAUDE.md                                | `https://code.claude.com/docs/en/memory`     |
| Path-scoped rules (`.claude/rules/`)     | `https://code.claude.com/docs/en/memory`     |
| Skills (`.claude/skills/`)               | `https://code.claude.com/docs/en/skills`     |
| Hooks                                    | `https://code.claude.com/docs/en/hooks`      |
| Settings (`settings.json`)               | `https://code.claude.com/docs/en/settings`   |
| Subagent definitions (`.claude/agents/`) | `https://code.claude.com/docs/en/sub-agents` |

## What to Verify

- **Frontmatter fields**: Use only fields documented in the official docs. Do not invent fields.
- **Directory structure**: Place files in the exact directories the docs specify (e.g., `SKILL.md` as the
  entry point, not `skill.md` or `index.md`).
- **File naming**: Follow documented naming conventions exactly.
- **YAML syntax**: Ensure frontmatter is valid YAML between `---` markers.
- **Supported values**: Use only documented values for fields like `model`, `isolation`, `memory`.

## Process

1. Identify which harness feature is involved.
2. Fetch the corresponding documentation URL from the table above using WebFetch.
3. Verify your changes match the documented format exactly.
4. If the docs contradict what exists in this repo, follow the docs — the repo may be outdated.
