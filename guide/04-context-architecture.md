# Chapter 04 -- Context Architecture: The Progressive Disclosure Hierarchy

> **Part 3: HARNESS** | Maps to templates: `templates/CLAUDE.md`, `templates/.claude/rules/example-backend.md`

Context is the single most expensive resource in agent-driven development. Every token of context you load competes for
attention, costs money, and — past a certain volume — degrades the quality of the agent's output. The architecture of
*when* and *how* context enters the agent's window is not a detail. It is a first-order engineering decision.

This chapter covers the five-tier context hierarchy in Claude Code, how to structure each tier, and the golden rule that
governs all of it: never load everything at once.

---

## Principles

**Progressive disclosure beats front-loading.** The agent should receive the minimum context required for the task at
hand, loaded at the moment of maximum relevance. A frontend styling task should not load backend deployment config. A
database migration should not load brand typography rules.

**Context has a cost function with three variables.** Token cost (you pay per input token), attention dilution (more
context means lower signal-to-noise), and staleness (outdated context causes outdated decisions). Good context
architecture minimizes all three simultaneously.

**Structure beats volume.** A 150-line CLAUDE.md that serves as a precise map outperforms a 2,000-line dump of every
decision ever made. The agent needs to know *where to look*, not *everything at once*.

---

## The Five Tiers of Context

### Tier 1: CLAUDE.md — Always Loaded (~200 lines)

CLAUDE.md sits at your project root. Claude Code loads it automatically at the start of every session. It is the most
valuable and most constrained piece of context you will write.

**What it is:** A table of contents and a set of invariant rules. Not an encyclopedia.

**What belongs in CLAUDE.md:**

- Project identity (one sentence: what this is)
- Tech stack summary (table format, scannable)
- Critical rules that apply to ALL work (branching policy, commit conventions, territory boundaries)
- Pointers to deeper context ("Read `.agent-instructions/backend-agent.md` before starting backend work")
- Local development commands (docker compose, test runners, migration commands)
- Mandatory skill invocations ("You MUST invoke `/design-check` before any frontend work")

**What does NOT belong in CLAUDE.md:**

- Architecture decisions (put in `docs/architecture.md`, reference it)
- Detailed API contracts (put in `contracts/openapi.yaml`, reference it)
- Historical debugging notes (put in memory or docs)
- Phase-by-phase task lists (put in `.agent-instructions/`)
- Brand guidelines (put in `docs/brand-identity.md`, load via skill)

**The litmus test:** For every line in CLAUDE.md, ask: "Would removing this line cause Claude to make a mistake in the
*next* session?" If the answer is no, move it to a deeper tier.

**Example structure (abbreviated):**

```markdown
# MyProject — Short Description

## Tech Stack

| Layer    | Stack                            |
|----------|----------------------------------|
| Frontend | Next.js, TypeScript, Tailwind    |
| Backend  | FastAPI, Python 3.12, SQLAlchemy |
| Database | PostgreSQL 16                    |

## Agent Identification

- Backend agent: Read `.agent-instructions/backend-agent.md` first.
- Frontend agent: Read `.agent-instructions/frontend-agent.md` first.

## Mandatory Skills

- `/design-check` — REQUIRED before any frontend component work.
- `/api-contract-check` — REQUIRED after any API surface change.

## Critical Rules

- Never commit directly to main. Feature branches + PRs only.
- API contract in `contracts/openapi.yaml` is source of truth.
- Neither agent modifies the other's territory.

## Local Development

docker compose up -d
docker compose run --rm backend alembic upgrade head
npm run dev # frontend
```

Notice what is *absent*: no architecture rationale, no design token values, no deployment procedures. Those live in
deeper tiers.

**The OpenAI lesson:** The `AGENTS.md` pattern — one large file containing everything — emerged as an alternative
approach. As discussed in their [Harness Engineering](https://openai.com/index/harness-engineering/) blog, OpenAI found
that a single monolithic file degrades as projects grow. At 500+ lines, agents start missing rules buried in the middle.
The progressive disclosure model keeps Tier 1 lean and pushes detail to tiers that load
only when relevant.

---

### Tier 2: Path-Scoped Rules — Loaded on File Match

Path-scoped rules live in `.claude/rules/*.md`. Each file has YAML frontmatter specifying which file paths trigger it.
When Claude reads or edits a file matching the path pattern, the corresponding rule loads automatically.

**This is zero-cost context when irrelevant.** A backend rule scoped to `apps/backend/**` never loads during a
frontend-only session. You get precision without pollution.

**File format:**

```markdown
---
paths:
  - "apps/backend/**"
---

# Backend Rules

- All database queries use SQLAlchemy 2.0 async patterns.
- Every endpoint must have a corresponding Pydantic request/response schema.
- Use `Annotated[T, Depends(...)]` for dependency injection, never raw Depends().
- Test files go in `apps/backend/tests/` mirroring the source structure.
- Run `ruff check apps/backend/` before considering any Python change complete.
```

**Common rule scopes:**

```markdown
# .claude/rules/frontend.md
---
paths:

- "apps/frontend/**"

---

# Frontend conventions: component patterns, import ordering, etc.

# .claude/rules/testing.md
---
paths:

- "**/tests/**"
- "**/*.test.*"
- "**/*.spec.*"

---

# Testing conventions: fixture patterns, assertion style, mocking rules

# .claude/rules/database.md
---
paths:

- "**/migrations/**"
- "**/models/**"

---

# Database conventions: migration naming, model field ordering, index rules

# .claude/rules/ci.md
---
paths:

- ".github/workflows/**"

---

# CI/CD rules: workflow naming, secret handling, job dependencies
```

**What makes a good path-scoped rule:**

- It applies consistently to all files in the matched path
- It is specific enough to be actionable (not "write good code")
- It would cause real mistakes if forgotten (not nice-to-haves)
- It is 10-40 lines (keep it focused)

**Anti-pattern:** Do not create one rule file per source file. Rule files scope to directories and patterns, not
individual files. If you need that level of granularity, the rule probably belongs as a code comment.

---

### Tier 3: Skills — Loaded on Demand

Skills live in `.claude/skills/`. They are invoked explicitly by name before specific work — either by the agent
following a CLAUDE.md instruction, or by the human typing a slash command.

**Skills are the key to context-scoped loading.** A design-enforcement skill loads brand constraints, anti-pattern
catalogs, and visual checklists — not CI/CD config. An API validation skill loads the OpenAPI spec and schema rules —
not typography tokens. This separation is both context management and cost management.

**Skill file structure:**

```
.claude/skills/
  design-enforcement/
    SKILL.md
  api-contract-check/
    SKILL.md
    reference.md         # supplemental reference, loaded on demand
  security-review/
    SKILL.md
    scripts/
      run-audit.sh       # script Claude can execute
```

`SKILL.md` is the required entrypoint for every skill. Skills can also include supporting files — templates, example
outputs, scripts, reference docs — that `SKILL.md` references so Claude loads them only when needed. This keeps the main
file focused while making detailed material available on demand.

Each `SKILL.md` must begin with YAML frontmatter between `---` markers, followed by Markdown instructions. The
`description` field is the most important: Claude uses it to decide when to auto-invoke the skill.

**Example skill (API contract check):**

```markdown
---
name: api-contract-check
description: Validates implementation against the OpenAPI contract. Invoke after implementing or modifying any API endpoint, request/response schema, or frontend API call.
---

# API Contract Check

## Process

1. Read `contracts/openapi.yaml` for the relevant endpoint definition.
2. Compare your implementation against the contract:
    - HTTP method and path match exactly
    - Request body schema matches (field names, types, required/optional)
    - Response schema matches (field names, types, status codes)
    - Error responses match documented error shapes
3. If there is a deviation:
    - Do NOT modify the contract.
    - Document the deviation in your `.agent-state/*.md` under "Contract Deviations."
    - Flag it for human review.

## Checklist

- [ ] Path matches contract
- [ ] Request schema matches contract
- [ ] Response schema matches contract
- [ ] Error responses match contract
- [ ] No undocumented endpoints added
```

For the complete frontmatter reference — including `disable-model-invocation`, `allowed-tools`, `context: fork`, and
supporting file patterns — see the [official skills documentation](https://code.claude.com/docs/en/skills).

**When to use a skill vs. a path-scoped rule:**

- Rule: applies *automatically* when touching certain files. No agent action needed.
- Skill: applies *deliberately* before certain categories of work. Requires invocation.

If the context is always relevant to a file pattern, make it a rule. If it is relevant to a *type of work* (regardless
of which files), make it a skill.

---

### Tier 4: Discoverable Context — Read on Demand

This tier includes everything the agent can find and read but that does not load automatically:

- `docs/` — Architecture documents, design specs, brand guidelines
- `contracts/` — API specs, database schemas, interface definitions
- `.agent-instructions/` — Agent-specific instructions, phase lists
- Source code itself — the agent reads code as needed via Glob, Grep, and Read

**The agent discovers Tier 4 context through Tier 1 pointers.** CLAUDE.md says "Read
`.agent-instructions/backend-agent.md` before starting backend work." The agent follows the pointer. This is why
CLAUDE.md is a map, not a dump.

**Good Tier 4 documents are self-contained.** An architecture doc should make sense without reading CLAUDE.md. A brand
identity doc should contain everything needed for design enforcement. This independence means the agent can load exactly
one document and have full context for that domain.

**Organizational conventions that help discovery:**

```
docs/
  architecture.md        # System design, component relationships
  brand-identity.md      # Visual design system, tokens, voice
  prd.md                 # Product requirements
  ux-spec.md             # UX flows, wireframes, interaction specs
contracts/
  openapi.yaml           # API contract (source of truth)
.agent-instructions/
  backend-agent.md       # Backend agent scope, rules, phases
  frontend-agent.md      # Frontend agent scope, rules, phases
.agent-state/
  backend-agent.md       # Backend agent progress, test results
  frontend-agent.md      # Frontend agent progress, deviations
```

---

### Tier 5: Auto-Memory — Persistent Across Sessions

Claude Code maintains a memory file at `~/.claude/projects/<project-hash>/memory/MEMORY.md`. This persists across
sessions for the same project. The agent appends to it; you can also edit it manually.

**What to store in memory:**

- Project phase status ("Phase 3 complete, Phase 4 in progress")
- Key decisions made during sessions ("Chose PostgreSQL over MongoDB because...")
- Feedback and lessons learned ("Always verify models against actual schema after migration changes")
- Integration with external systems ("Pi server SSH: `ssh user@host`")
- References to non-obvious conventions that evolved during development

**What NOT to store in memory:**

- Anything derivable from the current codebase (function signatures, file locations)
- Git history (use `git log`)
- Debugging solutions for resolved issues (unless the pattern is likely to recur)
- Duplicates of what is already in CLAUDE.md or docs/

**Memory as institutional knowledge:** Over a multi-phase project, memory accumulates the "tribal knowledge" that would
otherwise live only in a human engineer's head. When a new session starts, memory provides continuity: what was tried,
what failed, what conventions emerged.

**Pruning:** Memory files grow. Periodically review and remove entries that are no longer relevant (completed phases,
resolved issues, superseded decisions). A lean memory file is more useful than a comprehensive one.

---

## What the Human Should Do

1. **Write CLAUDE.md first.** Before any implementation begins, write the Tier 1 file. Keep it under 200 lines. Focus on
   rules and pointers, not explanations.

2. **Design the rule scopes.** Decide which directories get path-scoped rules. The typical set: backend, frontend,
   tests, database, CI. Create the `.claude/rules/` files with YAML frontmatter.

3. **Identify the skills needed.** For each domain where quality matters (design, API contracts, security), create a
   skill. Write the checklist. Make invocation mandatory in CLAUDE.md.

4. **Organize Tier 4 documents.** Place architecture docs, design specs, and contracts in predictable locations. Ensure
   CLAUDE.md points to each one.

5. **Review memory periodically.** Read `MEMORY.md` after every few sessions. Remove stale entries. Add context the
   agent missed.

6. **Resist the urge to front-load.** When you learn something new about the project, ask: "Which tier does this belong
   in?" Default to the deepest tier that still works.

---

## What the Agent Should Do

1. **Read CLAUDE.md first in every session.** Follow its pointers before starting work.

2. **Never request more context than needed.** If working on a backend endpoint, do not read the brand identity doc. If
   working on CSS, do not read the database migration rules.

3. **Follow skill invocation mandates.** If CLAUDE.md says to invoke a skill before frontend work, invoke it. Do not
   skip it because you "already know" the rules. Skills load fresh context that corrects for drift.

4. **Update memory after significant discoveries.** When you learn something that will matter in future sessions (a
   convention, a gotcha, a decision), append it to memory. Be concise.

5. **Respect tier boundaries.** Do not paste Tier 4 content into CLAUDE.md to "save time." Do not inline skill content
   into path-scoped rules. The tiers exist to manage context load.

---

## The Golden Rule

**Never load everything at once.** Each session should have the minimum context needed for the task at hand. This is not
about saving tokens — though it does. It is about signal-to-noise. An agent with 200 lines of precise, relevant context
outperforms an agent with 2,000 lines of "everything we know about this project."

The five-tier hierarchy makes this possible: always-loaded rules stay small, path-scoped rules activate only when
relevant, skills load only when invoked, documents are discovered through pointers, and memory provides continuity
without repetition.

Context architecture is the foundation. Every subsequent chapter assumes you have this hierarchy in place.
