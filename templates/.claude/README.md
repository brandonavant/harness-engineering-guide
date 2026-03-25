# Claude Code Harness Configuration

<!-- WHY THIS EXISTS:
This directory contains the Claude Code harness files that shape agent behavior.
Rules and skills are loaded automatically by Claude Code based on path matching
and invocation. Settings configure hooks and permissions. -->

## Directory Contents

| Path                  | Purpose                                                          |
|-----------------------|------------------------------------------------------------------|
| `rules/`              | Path-scoped and global rules loaded automatically                |
| `skills/`             | On-demand skills invoked by the agent or user                    |
| `agents/`             | Subagent definitions for delegated tasks                         |
| `settings.json`       | Hook configuration and project-level settings                    |
| `settings.local.json` | Machine-local settings overrides (gitignored)                    |

## Customization

**[CUSTOMIZE]** Replace the example rules, skills, agent definitions, and hook commands with
your project's actual tools and conventions. The examples use a fictional Beacon task management
SaaS as a starting point -- adapt them to your stack, directory structure, and workflows.

See the Harness Engineering Guide for the full context hierarchy (Chapter 04) and hook design
guidance (Chapter 07).
