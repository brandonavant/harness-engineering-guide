# Case Study: Agent Instructions -- Territorial Boundaries

This production application was built by two agents: a backend agent and a frontend agent. They worked across 19 implementation phases, touching hundreds of files, and never had a merge conflict. That outcome was not accidental. It was the result of territorial boundaries defined before the first line of code was written.

---

## The Two-Agent Setup

The project split naturally along the system boundary:

- **Backend agent**: Owned the API server, database models, migrations, AI inference pipeline, sidecar services, infrastructure definitions, and scripts
- **Frontend agent**: Owned the web application, shared type definitions, UI components, design system, and all user-facing pages

Each agent had its own instruction file (`.agent-instructions/backend-agent.md` and `.agent-instructions/frontend-agent.md`) and its own state file (`.agent-state/backend-agent.md` and `.agent-state/frontend-agent.md`).

## How Territories Were Defined

The boundaries were directory-level and absolute:

| Agent | Owned Directories |
|-------|-------------------|
| Backend | `apps/backend/`, `graphiti-sidecar/`, `scripts/`, `infra/` |
| Frontend | `apps/frontend/`, `packages/shared-types/` |
| Neither | `docs/`, `contracts/`, `.agent-instructions/` |

The rule was simple: **neither agent touches the other's territory or the docs directory.** The API contract (`contracts/openapi.yaml`) was shared but read-only for both agents. If either agent needed a contract change, it documented the deviation in its state file for human review.

This level of rigidity might seem excessive for a solo project. It was not. Even with one human orchestrating both agents, overlapping file ownership would have created confusion: which agent's version is correct? Which session had the latest change? Territorial boundaries eliminated an entire class of coordination problems.

## Instruction File Structure

Each agent's instruction file followed the same structure:

### 1. Identity and Context
A brief statement of who the agent is and what the project is. This repeated key context from CLAUDE.md so the agent had it immediately after reading its instruction file, without needing to re-read the root config.

### 2. Territory Declaration
The explicit list of directories the agent owns, and the explicit statement that other directories are off-limits. Redundant with CLAUDE.md, but redundancy in boundaries is cheap and violations are expensive.

### 3. Tech Stack (Agent-Specific)
The backend agent's instruction file listed Python, FastAPI, SQLAlchemy, and the testing stack. The frontend agent's listed TypeScript, Next.js, Tailwind, and the component library. Each agent only saw the technologies it needed to use.

### 4. Testing Requirements
Each agent had specific testing standards:
- Backend: pytest, 80%+ coverage target, test files mirroring source structure
- Frontend: type-checking via TypeScript, build verification, visual verification via Playwright screenshots

The testing requirements also included what to mock and what not to mock. The backend agent was told to mock external APIs (LLM calls, image services) but never the database. The frontend agent was told to use the Prism mock server for API responses but never to skip build verification.

### 5. Integration Verification Requirement
This was the most important section. Every agent instruction file included a mandatory integration verification step:

> Before marking any phase complete, you MUST:
> 1. Docker build all affected services
> 2. Run migrations against a fresh database
> 3. Start the full stack and verify health endpoints
> 4. Run the relevant smoke test checks

This requirement existed because agents naturally stop at "tests pass." Integration verification forced them to go further -- to verify that their code worked not just in isolation but as part of the running system.

### 6. Phase List
A numbered list of all planned phases, with brief descriptions. This gave the agent a sense of the project's trajectory and helped it make decisions that would not conflict with future phases. An agent implementing database models in phase 2 could see that phase 7 would add a knowledge graph, and design the models to accommodate that future integration.

## How State Files Tracked Progress

Each agent maintained a state file that was updated after every phase. The structure was:

```markdown
## Phase [N]: [Title]
**Status**: Complete | In Progress | Blocked

### Completed Tasks
- [x] Task description
- [x] Task description

### Test Results
- Backend: 287 tests, all passing
- Integration: 16/16 checks passing

### Files Modified
- apps/backend/src/models/campaign.py (new)
- apps/backend/src/api/routes/campaigns.py (new)
- apps/backend/tests/test_campaigns.py (new)

### Integration Verification
- Docker build: pass
- Migrations: pass (fresh DB)
- Health check: pass
- Smoke test: 16/16

### Contract Deviations
- Added `narrative` type to ParsedSegment enum (not in OpenAPI spec)
  - Reason: needed for AI output parsing
  - Impact: frontend needs to handle this type
  - Status: awaiting human review
```

This format served three purposes:

1. **Continuity across sessions.** When an agent started a new session (after /clear or a fresh start), reading the state file told it exactly where the previous session left off.
2. **Cross-agent visibility.** The frontend agent could read the backend agent's state file to see what had been built, what deviations existed, and what integration status looked like.
3. **Human oversight.** The human could review state files to understand project progress without re-reading code diffs.

## The Key Lesson: Territorial Boundaries Scale

Across 19 phases, two agents modified hundreds of files. The boundaries held. There were zero merge conflicts, zero cases of one agent overwriting the other's work, and zero cases of territory confusion.

The boundaries also made debugging faster. When the integration smoke test failed, the human could immediately narrow the investigation to one agent's territory based on which system boundary was broken. A failing API response meant looking at the backend agent's latest phase. A failing page load meant looking at the frontend agent's work.

The pattern generalizes beyond two agents. Any project that splits into independent subsystems -- and most do -- can benefit from explicit territorial boundaries. The boundaries do not need to be enforced programmatically (though file-level permissions could do that). They just need to be stated clearly enough that the agent treats them as inviolable.

The cost is minimal: a few extra lines in each instruction file. The benefit is coordination at scale without coordination overhead.
