# Chapter 5: Agent Orchestration — From Single Session to Teams

> **Part 3: HARNESS** | Maps to templates: `templates/.agent-instructions/agent-template.md`, `templates/.agent-state/agent-template.md`, `templates/contracts/README.md`

Most Claude Code work happens in a single session. One human, one agent, one context window. This is the default for good reason — it is simple, predictable, and sufficient for the majority of tasks.

But real products have multiple domains. A frontend and a backend. A database layer and an API layer. A design system and a CI pipeline. When you need parallel progress across domains, you scale from one session to many. This chapter covers how — and more importantly, when — to make that transition.

---

## Principles

**Start simple, scale deliberately.** The overhead of multi-agent orchestration is real: context duplication, conflict resolution, integration verification. A single session that takes twice as long often produces better results than two agents that step on each other.

**Agents are specialists, not generalists.** When you do scale, each agent should own a clear domain. Overlap creates conflicts. Ambiguity creates inconsistency. Territorial boundaries are not bureaucracy — they are the primary mechanism for preventing agents from undoing each other's work.

**The interface is the contract.** When two agents share a boundary (an API, a database schema, a type definition), that boundary must be governed by an explicit contract that neither agent modifies unilaterally. Without this, Agent A implements the API one way while Agent B consumes it another way, and you discover the mismatch only at integration time.

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
- If you find yourself saying "now switch to the frontend," consider whether that is a new session rather than a continuation.

**When to move beyond single session:**
- You have two or more domains that need parallel progress and have minimal file overlap
- A single session's context window is becoming saturated (you are loading many large files)
- You want exploration or research done without polluting the main working context

---

## Level 2: Subagents

Subagents are delegated tasks within a single Claude Code session. The main agent spawns a subagent to investigate a question, perform a focused task, or explore an approach. The subagent's deep context stays isolated — only the summary returns to the main agent.

**Good for:**
- Investigation without context pollution ("go read these 15 test files and summarize the patterns")
- Parallel research ("check if the auth library supports this feature")
- Focused sub-tasks where the detail is not needed in the main context
- Keeping the main agent's context window clean for the primary task

**How it works:**
The main agent delegates a task with a clear prompt. The subagent runs in its own inference, reads whatever files it needs, and returns a summary. The main agent sees only the summary — not the full trace of files read and code analyzed.

**Cost awareness:** Each subagent is a separate inference call. Subagents that read many files consume significant input tokens. Use them deliberately for tasks where the isolation benefit justifies the cost. Do not spawn a subagent to read one file — just read it directly.

**Example delegation patterns:**

```
"Investigate the auth middleware in apps/backend/middleware/auth.py and
all files that import from it. Summarize: what session format does it
expect, what validation does it perform, and what error codes does it
return."

"Read all test files in apps/frontend/tests/components/ and summarize
the testing patterns: what utilities are used, how mocking works, and
what assertion styles are followed."

"Search the codebase for all uses of the UserProfile type. Report
which files import it, whether any extend or modify it, and whether
the shape is consistent across all usages."
```

---

## Level 3: Agent Teams

Agent teams run multiple named teammates, each with their own context window, working in parallel on different domains of the same project.

**Good for:**
- Frontend + backend in parallel
- Multiple independent features that touch different files
- Large refactoring across separate domains
- Competing implementation approaches (try two designs, pick the best)

**Team sizing guidelines:**
- 3-5 teammates per team. More than 5 creates coordination overhead that outweighs the parallelism benefit.
- 5-6 tasks per teammate per phase. Smaller task lists keep each agent focused.
- Each teammate should own different files. If two teammates need to edit the same file, restructure the work so they do not.

**Setting up a team:**

Each teammate gets:
1. An **agent instruction file** (`.agent-instructions/<agent-name>.md`) defining identity, territory, and tasks
2. An **agent state file** (`.agent-state/<agent-name>.md`) for tracking progress and logging deviations
3. Clear **territorial boundaries** — files they own and files they must not touch

The orchestrating session (human or team lead) assigns work, monitors progress, and runs integration verification between phases.

---

## Level 4: Worktree Isolation

For maximum isolation, each agent gets its own copy of the repository via Git worktrees. Each agent works on its own branch in its own directory. No file conflicts are possible because agents operate on physically separate file trees.

**When to use worktrees:**
- Agents are making large-scale changes across many files in their domain
- You need true parallel execution without any risk of file contention
- The project is large enough that context isolation matters for performance

**The critical workflow — memorize this sequence:**

```
1. Agents commit all changes to their worktree branch
2. Agents shut down
3. Merge each agent's branch into main (or target branch)
4. Delete worktrees (TeamDelete or manual cleanup)
```

**NEVER delete a worktree with unmerged work.** Worktree deletion removes the directory and can remove the branch. Any uncommitted or unmerged changes are permanently lost. This is not recoverable.

**Before shutting down any agent in a worktree**, instruct it to:
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

When multiple agents work on the same codebase, territorial boundaries prevent conflicts. Each agent's instruction file specifies exactly what it owns and what it must not touch.

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
- apps/frontend/ — owned by frontend agent
- packages/shared-types/ — owned by frontend agent
- docs/ — owned by human, read-only for all agents
```

**Why this matters:** Without boundaries, Agent A refactors a shared utility that Agent B depends on. Agent B's tests break. Agent B "fixes" them by reverting Agent A's change. You end up with merge conflicts and wasted work. Territorial boundaries eliminate this category of failure entirely.

**The contract layer:** For boundaries that agents share (like an API), use an explicit contract file that neither agent modifies. Both agents implement *against* the contract. If an agent discovers it needs a contract change, it documents the need in its state file — the human decides whether to update the contract.

---

## Agent Instruction Files

Each agent gets an instruction file at `.agent-instructions/<agent-name>.md`. This is the agent's briefing document — it reads this before starting work.

**Structure of an agent instruction file:**

```markdown
# <Agent Name> — Implementation Agent

## Identity
You are the backend implementation agent for [Project]. You implement
server-side logic, API endpoints, database models, and background tasks.

## Tech Stack
- Python 3.12+, FastAPI, SQLAlchemy 2.0, Alembic
- PostgreSQL 16 with pgvector extension
- pytest for testing, ruff for linting

## Territory
### Your Files
- apps/backend/

### Off Limits
- apps/frontend/
- docs/ (read-only)

## Implementation Rules
- Every endpoint must have request/response Pydantic schemas
- All database operations use async SQLAlchemy sessions
- Test coverage required for all new endpoints
- Run `ruff check` before considering any change complete

## Testing Requirements
- Unit tests for all business logic
- Integration tests for API endpoints (use TestClient)
- Run full suite: `pytest apps/backend/tests/ -v`
- All tests must pass before marking a phase complete

## Verification Steps
After completing each phase:
1. Run linter: `ruff check apps/backend/`
2. Run tests: `pytest apps/backend/tests/ -v`
3. Verify Docker build: `docker compose build backend`
4. Update your state file with results

## Phase List
### Phase 1: Models and Schemas
- Database models for User, Character, Campaign
- Pydantic schemas matching openapi.yaml
- Alembic migration for initial tables

### Phase 2: Core Endpoints
- GET/POST/PATCH/DELETE for each resource
- Auth middleware integration
- Request validation

[... additional phases ...]
```

**Key elements:**
- **Identity** — tells the agent what it is and sets the frame for all decisions
- **Territory** — prevents file conflicts (covered above)
- **Rules** — domain-specific conventions that apply to all work
- **Testing** — how to verify, what commands to run, what "done" means
- **Phases** — ordered task list so the agent knows what to work on

---

## Agent State Files

Each agent maintains a state file at `.agent-state/<agent-name>.md`. This is a living log of what has been done, what was found, and what deviates from expectations.

**What goes in the state file:**

```markdown
# Backend Agent — State

## Completed Phases
### Phase 1: Models and Schemas (2024-03-10)
- Created 5 SQLAlchemy models
- Created 12 Pydantic schemas
- Migration 0001 applied successfully
- All 23 tests passing
- Linter clean

## Test Results (Latest)
- Total: 89 passing, 0 failing
- Coverage: 87% (apps/backend/src/)

## Contract Deviations
- Added `narrative` type to ParsedSegment enum — not in openapi.yaml.
  Reason: needed for AI output parsing. Flagged for human review.

## Known Issues
- Embedding service not available (requires Azure OpenAI provisioning).
  Using mock embeddings in tests. Blocked for live integration testing.

## Integration Verification
- Last smoke test: 16/16 passing (2024-03-10)
```

**Why state files matter:** When a new session starts (or a different agent needs to understand what happened), the state file provides continuity. It is the agent's work log.

---

## Contract Governance for Multi-Agent Work

When multiple agents share an interface, the interface definition must be treated as an immutable contract during implementation.

**The contract pattern:**

```
contracts/
  openapi.yaml        # API contract between frontend and backend
  database-schema.sql  # Database contract (or use migrations as source of truth)
  shared-types.ts      # Type definitions consumed by multiple agents
```

**Rules:**
1. The contract is written before agents begin implementation (by the human or a design phase)
2. Both agents implement *against* the contract, not against each other's code
3. Neither agent modifies the contract unilaterally
4. If an agent needs a contract change, it documents the need in its state file under "Contract Deviations"
5. The human reviews deviations and decides whether to update the contract
6. After a contract update, both agents are informed

**Why unilateral changes are forbidden:** If the backend agent adds a field to the API response, the frontend agent does not know about it. If the frontend agent changes the expected request body shape, the backend agent's validation rejects it. Contract stability is what makes parallel work possible.

**Practical workflow:**

```
Phase start:
  Human reviews contract, confirms it is current

During phase:
  Backend agent implements endpoints matching contract
  Frontend agent implements API calls matching contract
  Both agents document any needed changes in state files

Phase end:
  Human reviews state files for contract deviations
  If changes needed: update contract, notify both agents
  Run integration smoke test to verify alignment
```

---

## What the Human Should Do

1. **Start with single sessions.** Do not set up agent teams for a new project. Build the first few features in single sessions to establish patterns and conventions.

2. **Define territories before launching agents.** Write the agent instruction files. Specify ownership clearly. Resolve any ambiguous boundaries before agents start work.

3. **Write the contract first.** For multi-agent work, the API spec, database schema, or shared type definitions must exist before agents begin implementing. Do not let agents discover the interface by implementing both sides.

4. **Run integration verification between phases.** Agents test in isolation. They mock the boundaries they do not own. Integration failures only surface when you test the real system. This is your job.

5. **Review state files.** After each agent phase, read the state files. Look for contract deviations, known issues, and test gaps. Address deviations before starting the next phase.

6. **Merge carefully.** When using worktree isolation, merge one branch at a time. Run tests after each merge. If there are conflicts, resolve them before merging the next branch.

---

## What the Agent Should Do

1. **Read your instruction file first.** Before starting any work, read `.agent-instructions/<your-name>.md`. Follow its rules, respect its territory, work through its phases in order.

2. **Stay in your territory.** Do not modify files outside your ownership. If you need a change in another agent's territory, document it in your state file and flag it for the human.

3. **Implement against the contract.** Read the contract (API spec, schema definition) and match it exactly. If your implementation needs something the contract does not provide, document the deviation — do not change the contract.

4. **Update your state file.** After completing each phase, log what was done, test results, and any issues or deviations. This is not optional — it is how continuity works across sessions.

5. **Commit before shutdown.** If working in a worktree, always commit all changes and report your branch name before the session ends. Uncommitted work in a worktree can be lost permanently.

6. **Do not assume what the other agent did.** If you need to know whether the backend implemented an endpoint, check the contract — not the other agent's code (which you may not even have access to in a worktree). The contract is the shared truth.
