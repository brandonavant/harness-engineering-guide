# Beacon -- Task Management SaaS

<!-- WHY THIS FILE EXISTS:
CLAUDE.md is the single entry point that Claude Code reads before every conversation.
It replaces the "tribal knowledge" problem -- instead of hoping agents discover conventions
by reading code, you declare them explicitly. Keep it under 200 lines; link to docs/ for
detail. Every section below has a specific job; removing one creates a blind spot. -->

## Project Context

<!-- WHY: Without context, Claude treats your project as a generic codebase. Two to three
sentences ground every decision the agent makes. -->

Beacon is a multi-tenant task management SaaS for small engineering teams. Users create
workspaces, organize tasks into projects, assign owners, set priorities, and track progress
through customizable board and list views. The product targets teams of 5-20 who want
structure without the overhead of enterprise project management tools.

**[CUSTOMIZE]** Replace with your product's identity -- what it is, who it serves, and
what makes it distinct. Be specific enough that an agent can distinguish "on-brand" from
"off-brand" decisions.

## Tech Stack

<!-- WHY: Prevents agents from introducing incompatible libraries or reimplementing what
the stack already provides. Pinned versions avoid silent breakage from upgrades. -->

| Layer      | Stack                                                                 |
|------------|-----------------------------------------------------------------------|
| Frontend   | Next.js 15, TypeScript, Tailwind CSS v4, shadcn/ui, TanStack Query v5 |
| Backend    | FastAPI, Python 3.12+, SQLAlchemy 2.0, Alembic                        |
| Database   | PostgreSQL 16                                                         |
| Auth       | Better Auth (session cookies)                                         |
| Deployment | Docker, GitHub Actions                                                |

**[CUSTOMIZE]** Replace with your actual stack. Pin major versions.

## Build / Test / Lint Commands

<!-- WHY: Agents need to verify their work. Without explicit commands, they guess --
and guesses break CI. List every command an agent might need during implementation. -->

```bash
# Full stack
docker compose up -d
docker compose run --rm backend alembic upgrade head

# Backend
cd apps/backend && python -m pytest tests/ -v          # all tests
cd apps/backend && python -m pytest tests/unit/ -v     # unit only
cd apps/backend && ruff check .                        # lint
cd apps/backend && ruff format --check .               # format check

# Frontend
cd apps/frontend && npm run build                      # build
cd apps/frontend && npm run test                       # tests
cd apps/frontend && npx tsc --noEmit                   # type check

# Integration
./scripts/integration-smoke-test.sh
```

**[CUSTOMIZE]** Replace with your project's actual commands.

## Design Docs

<!-- WHY: Agents must implement against specs, not invent requirements. Pointing to docs/
ensures they read the spec before writing code. "READ-ONLY" prevents agents from silently
editing requirements to match what they built instead of what was asked for. -->

Design docs live in `docs/` and are **READ-ONLY during implementation**:

- `docs/PRD.md` -- Product requirements
- `docs/architecture.md` -- Architecture and technical decisions
- `docs/ux-spec.md` -- UX specification
- `docs/brand-identity.md` -- Brand identity and design system

API contract is the source of truth for all endpoints:

- `contracts/openapi.yaml` -- Both backend and frontend implement against this spec

## Subagent Definitions

<!-- WHY: In multi-agent setups, each subagent needs to know its scope BEFORE starting work.
Without this, subagents overlap, conflict, or miss responsibilities. Subagent definitions
at `.claude/agents/` are autoloaded on invocation — no manual reading required. -->

Subagent definitions live in `.claude/agents/` and are loaded automatically when a subagent
is invoked:

- **Backend subagent:** `.claude/agents/backend-agent.md`
- **Frontend subagent:** `.claude/agents/frontend-agent.md`

Each subagent uses its agent memory (`.claude/agent-memory/<name>/`) for cross-session
continuity. Update your agent memory after completing each task.

## Critical Rules

<!-- WHY: These are the constraints that, if violated, cause bugs that are hard to detect
and expensive to fix. Each rule exists because it was learned the hard way. -->

### Never Deviate from the API Contract

Both agents implement exactly what `contracts/openapi.yaml` defines. If you need a change,
document it in your agent memory under "Contract Deviations" -- do not modify the spec
unilaterally.

### Territory Boundaries

- Backend agent owns: `apps/backend/`, `scripts/`, `infra/`
- Frontend agent owns: `apps/frontend/`, `packages/shared-types/`
- Neither agent touches the other's territory or the `docs/` directory.

**[CUSTOMIZE]** Define your project's territory map.

### No Hardcoded Secrets

Never commit API keys, tokens, passwords, or connection strings. Use environment variables.
If a file looks like it contains secrets (.env, credentials.json), warn the user before staging.

### Test Before Declaring Done

Every change must pass the relevant test suite. Run tests, verify the output, and include
results in your agent memory. Do not mark a task complete based on "it should work."

## Mandatory Skill Usage

<!-- WHY: Skills enforce quality gates that agents skip when under pressure to "just ship."
Making them mandatory means the gate runs every time, not just when the agent remembers. -->

### Design Enforcement -- `/design-check`

**REQUIRED** before building or modifying any component, page, or layout. Loads the
brand enforcement rules and anti-generic checklist.

### API Contract Check -- `/api-contract-check`

**REQUIRED** after implementing or modifying any API endpoint, schema, or frontend API call.
Validates implementation matches `contracts/openapi.yaml`.

**[CUSTOMIZE]** Name your actual skills. Add project-specific ones (e.g., `/db-migration-check`).

## Branching Policy

<!-- WHY: Without a branching policy, agents commit directly to main, creating a broken
trunk that blocks other agents. PRs create a review checkpoint. -->

- **Trunk-based development** on `main`.
- All changes go through **feature branches** and pull requests. No direct commits to `main`.
- Branch naming: `feat/`, `fix/`, `chore/`, `docs/` prefixes.
- CI must pass before merge.
- Agents must open a PR when finished with their work. Never merge directly.

## Integration Verification

<!-- WHY: Unit tests with mocked dependencies pass even when the real system is broken.
The smoke test catches cross-system failures that isolated tests miss. -->

After every implementation phase, run the integration smoke test:

```bash
./scripts/integration-smoke-test.sh
```

All checks must pass before proceeding to the next phase. If any check fails, fix the
integration issue before starting new work.
