# Chapter 05 -- Agent Orchestration: Sessions, Subagents, and Worktrees

> **Part 3: HARNESS** | Maps to templates: `templates/.claude/agents/agent-template.md`,
`templates/contracts/README.md`

Most Claude Code work happens in a single session. One human, one agent, one context window. This is the default for
good reason — it is simple, predictable, and sufficient for the majority of tasks.

But real products have multiple domains. A frontend and a backend. A database layer and an API layer. A design system
and a CI pipeline. When you need parallel progress across domains, subagents and worktrees provide isolation without
coordination overhead. This chapter covers how — and more importantly, when — to move beyond a single session.

---

## Principles

**Start simple, scale deliberately.** The overhead of multi-agent orchestration is real: context duplication, conflict
resolution, integration verification. A single session that takes twice as long often produces better results than two
subagents that step on each other.

**Agents are specialists, not generalists.** When you do scale, each agent should own a clear domain. Overlap creates
conflicts. Ambiguity creates inconsistency. Territorial boundaries are not bureaucracy — they are the primary mechanism
for preventing agents from undoing each other's work.

**The interface is the contract.** When two subagents share a boundary (an API, a database schema, a type definition),
that boundary must be governed by an explicit contract that neither subagent modifies unilaterally. Without this,
Subagent A implements the API one way while Subagent B consumes it another way, and you discover the mismatch only at
integration time.

---

## Level 1: Single Session

A single Claude Code session — one human, one agent, one context window — handles most work effectively.

**Good for:**

- Project scaffolding and initial setup
- Single-domain features (a new API endpoint, a new page, a new migration)
- Bug investigation and fixes
- Documentation and configuration changes
- Refactoring within one domain

**How to use it well:**

- Keep the session focused. One task or closely related group of tasks.
- Use skills to load context at the right moment rather than dumping everything upfront.
- Commit frequently. If a session goes long, intermediate commits create save points.
- If you find yourself saying "now switch to the frontend," consider whether that is a new session rather than a
  continuation.

**When to move beyond single session:**

- You have two or more domains that need parallel progress and have minimal file overlap
- A single session's context window is becoming saturated (you are loading many large files)
- You want exploration or research done without polluting the main working context

---

## Level 2: Subagents

Subagents are delegated tasks within a single Claude Code session. The main agent spawns a subagent to investigate a
question, perform a focused task, or explore an approach. The subagent's deep context stays isolated — only the summary
returns to the main agent.

**Good for:**

- Investigation without context pollution ("go read these 15 test files and summarize the patterns")
- Parallel research ("check if the auth library supports this feature")
- Focused sub-tasks where the detail is not needed in the main context
- Keeping the main agent's context window clean for the primary task

### Built-in subagents

Claude Code ships three subagents available immediately in any project with no configuration required:

- **Explore** — Read-only, runs on Haiku. Use for investigation tasks: reading files, grepping for patterns,
  summarizing codebases.
- **Plan** — Read-only, for design reasoning. Use before committing to an implementation approach.
- **General-purpose** — Full tool access, default model. Use for tasks that require both reading and writing.

Start with built-ins. Define custom subagents only when you need specific tool restrictions, a persistent
description, or a different model than the defaults.

### Custom subagent definition

Custom subagents are Markdown files with YAML frontmatter stored in `.claude/agents/` (project-level) or
`~/.claude/agents/` (user-level, available across all projects).

Each file follows the same pattern as a skill — frontmatter governs behavior, the Markdown body provides
instructions:

`````markdown
---
name: recipe-investigator
description: Investigates RecipeVault's recipe parsing pipeline and ingredient normalization logic. Use
  this subagent when analyzing how recipes are parsed, how ingredients are matched, or how units are
  converted. Use proactively when the user asks questions about ingredient handling.
tools: Read, Glob, Grep
model: haiku
---

You are a read-only research subagent for the RecipeVault project.

When invoked:

1. Read the files relevant to the investigation.
2. Trace the code paths specified in the task.
3. Return a structured summary: what you found, the patterns, and any inconsistencies.

Do not modify files. Report findings only.
`````

Key frontmatter fields: `name` (unique identifier), `description` (routing trigger — see below), `tools`
(allowlist; omit to inherit all tools), `model` (`haiku`, `sonnet`, `opus`, or `inherit`), `background`
(`true` to run async), `isolation` (`worktree` for an isolated git worktree), `memory` (persistence scope:
`user`, `project`, or `local` — stored at `.claude/agent-memory/<name>/`), `skills` (list of skills to
preload into the subagent's context). See the
[official subagent documentation](https://code.claude.com/docs/en/sub-agents) for the full field reference.

**The definition body is the system prompt.** The Markdown below the frontmatter is the subagent's complete
briefing — identity, territory, rules, phases. For implementation subagents that need parallel work across
domains, write the body as a full briefing document:

``````markdown
---
name: recipe-backend
description: "Backend implementation agent for RecipeVault. Use when implementing API
  endpoints, database models, migrations, or backend business logic. Use proactively
  when the user starts backend work."
tools: Read, Edit, Write, Bash, Glob, Grep
model: inherit
memory: project
skills:
  - api-contract-check
---

# Identity

You are the backend implementation agent for RecipeVault. You implement server-side
logic, API endpoints, database models, and background tasks. You implement against
the design documents and API contract — you do not invent requirements.

## Territory

### Files You Own

- apps/backend/ — all source code, tests, and configuration
- scripts/ — build and deployment scripts
- alembic/ — database migrations

### Shared (Read-Only)

- contracts/openapi.yaml — implement against this, never modify
- docker-compose.yml — read for service configuration, never modify

### Off Limits

- apps/frontend/ — owned by frontend subagent
- packages/shared-types/ — owned by frontend subagent
- docs/ — owned by human, read-only for all agents

## Implementation Rules

- Every endpoint must have request/response Pydantic schemas
- All database operations use async SQLAlchemy sessions
- Test coverage required for all new endpoints
- Run `ruff check` before considering any change complete

## Phases

### Phase 1: Models and Schemas

- Database models for Recipe, Ingredient, MealPlan
- Pydantic schemas matching openapi.yaml
- Alembic migration for initial tables

### Phase 2: Core Endpoints

- GET/POST/PATCH/DELETE for each resource
- Auth middleware integration
- Request validation
``````

The subagent reads its entire definition — frontmatter and body — before starting work.

### The description field

The `description` field is not a label — it is the routing mechanism. Claude reads every subagent's description
to decide whether to delegate automatically. Write it as a precise trigger: what the subagent does and when to
use it. Include "use proactively" to signal delegation without waiting to be asked.

This is the same principle as the skill `description` field in [Chapter 04](04-context-architecture.md). A
vague description produces inconsistent delegation; a precise one routes the right work to the right subagent.

### Invocation

Three ways to invoke a subagent:

- **Natural language:** "Use the recipe-investigator subagent to trace how ingredient quantities are normalized."
- **@-mention:** `@"recipe-investigator (agent)"` — direct delegation mid-conversation.
- **Session flag:** `claude --agent recipe-investigator` — starts the entire session inside that subagent.

**How it works:**
The main agent delegates a task with a clear prompt. The subagent runs in its own inference, reads whatever
files it needs, and returns a summary. The main agent sees only the summary — not the full trace of files
read and code analyzed.

**Example delegation patterns:**

```
"Use the recipe-investigator subagent to read all files in
apps/backend/recipes/parsing/ and summarize: what normalization steps
happen, what external libraries are called, and whether ingredient
quantities and units are separated before or after lookup."

"Investigate the auth middleware in apps/backend/middleware/auth.py and
all files that import from it. Summarize: what session format does it
expect, what validation does it perform, and what error codes does it
return."

"Search the codebase for all uses of the Ingredient type. Report which
files import it, whether any extend or modify it, and whether the shape
is consistent across all usages."
```

### Persistent memory

The `memory` frontmatter field gives subagents cross-session continuity. When set to `project` (recommended),
Claude Code stores the subagent's memory at `.claude/agent-memory/<name>/`. This directory is automatically
loaded on each invocation — the subagent picks up where it left off.

**How it works:**

- The subagent's `MEMORY.md` index (first 200 lines) is autoloaded at startup
- The subagent reads and writes memory files in its `.claude/agent-memory/<name>/` directory
- Memory persists across sessions — shut down, restart, and the subagent remembers

**What to store in agent memory:**

- Completed phases and task status
- Test results and verification outcomes
- Contract deviations flagged for human review
- Known issues, blockers, and workarounds
- Decisions made during implementation and their rationale

The subagent's built-in memory system provides cross-session continuity automatically.

---

## Level 3: Worktree Isolation

For maximum isolation, each subagent gets its own copy of the repository via Git worktrees. Each subagent works on its
own branch in its own directory. No file conflicts are possible because subagents operate on physically separate file
trees.

**When to use worktrees:**

- Subagents are making large-scale changes across many files in their domain
- You need true parallel execution without any risk of file contention
- The project is large enough that context isolation matters for performance

**Starting a worktree session:**

Use the `claude --worktree <name>` flag to start a Claude Code session in an isolated worktree:

```bash
claude --worktree backend-agent    # named worktree at .claude/worktrees/backend-agent/
claude --worktree                  # auto-generated name (e.g., bright-running-fox)
```

Claude Code creates the worktree at `.claude/worktrees/<name>/`, branching from the default remote branch. Add
`.claude/worktrees/` to your `.gitignore` to prevent worktree contents from appearing as untracked files.

For monorepos with large shared directories (e.g., `node_modules`), configure `worktree.symlinkDirectories` in
`settings.json` to symlink them into each worktree rather than duplicating them.

**The critical workflow — memorize this sequence:**

```
1. Subagents commit all changes to their worktree branch
2. Subagents shut down
3. Merge each subagent's branch into main (or target branch)
4. Delete worktrees (manual cleanup)
```

**NEVER delete a worktree with unmerged work.** Worktree deletion removes the directory and can remove the branch. Any
uncommitted or unmerged changes are permanently lost. This is not recoverable.

**Before shutting down any subagent in a worktree**, instruct it to:

1. Stage and commit all changes
2. Report its branch name
3. Confirm the commit hash

**Before cleaning up worktrees:**

```bash
# List all worktrees and their branches
git worktree list

# Verify each branch has been merged
git log main..<branch-name> --oneline
# If this shows commits, the branch has unmerged work. Merge first.

# Only after all branches are merged:
git worktree remove <path>
```

---

## Territorial Boundaries

When multiple subagents work on the same codebase, territorial boundaries prevent conflicts. Each subagent's definition
specifies exactly what it owns and what it must not touch.

**Example territory definition:**

```markdown
## Your Territory (files you own)

- apps/backend/ — all source code, tests, and configuration
- scripts/ — build and deployment scripts
- infra/ — infrastructure-as-code files

## Shared (read-only for you)

- contracts/openapi.yaml — read and implement against this, never modify
- docker-compose.yml — read for service configuration, never modify

## Off Limits (never touch)

- apps/frontend/ — owned by frontend subagent
- packages/shared-types/ — owned by frontend subagent
- docs/ — owned by human, read-only for all agents
```

**Why this matters:** Without boundaries, Subagent A refactors a shared utility that Subagent B depends on. Subagent B's
tests break. Subagent B "fixes" them by reverting Subagent A's change. You end up with merge conflicts and wasted work.
Territorial boundaries eliminate this category of failure entirely.

**The contract layer:** For boundaries that subagents share (like an API), use an explicit contract file that neither
subagent modifies. Both subagents implement *against* the contract. If a subagent discovers it needs a contract change,
it documents the need in its agent memory — the human decides whether to update the contract.

---

## Contract Governance for Multi-Agent Work

When multiple subagents share an interface, the interface definition must be treated as an immutable contract during
implementation.

**The contract pattern:**

```
contracts/
  openapi.yaml        # API contract between frontend and backend
  database-schema.sql  # Database contract (or use migrations as source of truth)
  shared-types.ts      # Type definitions consumed by multiple subagents
```

**Rules:**

1. The contract is written before subagents begin implementation (by the human or a design phase)
2. Both subagents implement *against* the contract, not against each other's code
3. Neither subagent modifies the contract unilaterally
4. If a subagent needs a contract change, it documents the need in its agent memory under "Contract Deviations"
5. The human reviews deviations and decides whether to update the contract
6. After a contract update, both subagents are informed

**Why unilateral changes are forbidden:** If the backend subagent adds a field to the API response, the frontend
subagent does not know about it. If the frontend subagent changes the expected request body shape, the backend
subagent's validation rejects it. Contract stability is what makes parallel work possible.

**Practical workflow:**

```
Phase start:
  Human reviews contract, confirms it is current

During phase:
  Backend subagent implements endpoints matching contract
  Frontend subagent implements API calls matching contract
  Both subagents document any needed changes in their agent memory

Phase end:
  Human reviews agent memory for contract deviations
  If changes needed: update contract, notify both subagents
  Run integration smoke test to verify alignment
```

---

## What the Human Should Do

1. **Start with single sessions.** Build the first features in single sessions to establish patterns and conventions.
   Define subagents only when you have genuinely independent domains that benefit from parallel work.

2. **Define subagents in `.claude/agents/` before launching parallel work.** Write the definition files. Specify
   identity, territory, rules, and phases. Resolve any ambiguous boundaries before subagents start work.

3. **Write the contract first.** For multi-agent work, the API spec, database schema, or shared type definitions must
   exist before subagents begin implementing. Do not let subagents discover the interface by implementing both sides.

4. **Run integration verification between phases.** Subagents test in isolation. They mock the boundaries they do not
   own. Integration failures only surface when you test the real system. This is your job.

5. **Review agent memory between phases.** After each subagent phase, review the subagent's memory for contract
   deviations, known issues, and test gaps. Address deviations before starting the next phase.

6. **Merge carefully.** When using worktree isolation, merge one branch at a time. Run tests after each merge. If there
   are conflicts, resolve them before merging the next branch.

---

## What the Agent Should Do

1. **Follow your definition's system prompt.** Before starting any work, read and follow the instructions in your
   subagent definition. Use your agent memory for cross-session continuity — read it at session start to understand
   what has been completed.

2. **Stay in your territory.** Do not modify files outside your ownership. If you need a change in another subagent's
   territory, document it in your agent memory and flag it for the human.

3. **Implement against the contract.** Read the contract (API spec, schema definition) and match it exactly. If your
   implementation needs something the contract does not provide, document the deviation — do not change the contract.

4. **Update your agent memory after completing each phase.** Log what was done, test results, and any issues or
   deviations. This is not optional — it is how continuity works across sessions.

5. **Commit before shutdown.** If working in a worktree, always commit all changes and report your branch name before
   the session ends. Uncommitted work in a worktree can be lost permanently.

6. **Do not assume what the other subagent did.** If you need to know whether the backend implemented an endpoint, check
   the contract — not the other subagent's code (which you may not even have access to in a worktree). The contract is
   the shared truth.

---

Next: [Chapter 06 -- Design Intent Preservation: The Anti-Slop System](06-design-intent.md)
