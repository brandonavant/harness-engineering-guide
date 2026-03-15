# Case Study: CLAUDE.md -- The Table of Contents Pattern

The CLAUDE.md file for this production application is 199 lines long. That number is not accidental. Every line was evaluated against a single question: "Would removing this cause Claude to make mistakes?" Anything that could live in a rule, skill, or design document was moved there. What remained was a table of contents -- pointers, commands, and non-negotiable constraints that the agent needs at session start.

This file documents the structure, explains why each section exists, and identifies the key insight that emerged from iterating on it across 19 phases.

---

## The Structure

Here is the CLAUDE.md, section by section, with annotations.

### Section 1: Project Context (4 lines)

```
# [Project Name] -- [One-line description]

## Project Context

This is a [genre] application called [Name]. It is NOT a chatbot, NOT a generic AI app.
Every implementation decision must reinforce [the core brand identity].
```

**Why it exists**: The agent needs to know what it is building in two sentences. Without this, Claude defaults to generic patterns. The explicit "NOT a chatbot" framing prevented the agent from treating the application as a chat interface, which would have produced entirely wrong UI patterns.

**Key detail**: The negative framing ("NOT a chatbot, NOT a generic AI app") was added after the agent produced chatbot-style UI in an early phase. Telling Claude what something *is not* is sometimes more effective than telling it what it is.

### Section 2: Design Docs Pointer (5 lines)

```
**Design docs are READ-ONLY during implementation:**
- `docs/PRD.md` -- Product requirements
- `docs/ux-spec.md` -- UX specification
- `docs/architecture.md` -- Architecture
- `docs/brand-identity.md` -- Brand identity & design system
```

**Why it exists**: The agent needs to know where requirements live. The "READ-ONLY" marker prevents the agent from editing design documents during implementation -- a behavior that occurred when it was not explicitly prohibited. Design docs are inputs to implementation, not outputs of it.

### Section 3: API Contract Pointer (2 lines)

```
**API contract is the source of truth:**
- `contracts/openapi.yaml` -- Both agents implement against this spec.
```

**Why it exists**: When two agents (frontend and backend) must produce compatible code, they need a shared source of truth. This line points to it and establishes its authority. See the [API contract case study](api-contract.md) for details.

### Section 4: Agent Identification (5 lines)

```
## Agent Identification

If you are working on this project as an implementation agent, read your instruction file first:
- **Backend agent:** Read `.agent-instructions/backend-agent.md`
- **Frontend agent:** Read `.agent-instructions/frontend-agent.md`
```

**Why it exists**: When running multiple agents (one for backend, one for frontend), each agent needs to know which instruction file to read. This section acts as a router. It also establishes the concept of agent identity -- the backend agent knows it is the backend agent and should not touch frontend files.

### Section 5: Mandatory Skill Usage (20 lines)

```
## Mandatory Skill Usage

### Frontend Work -- /skill-name
**REQUIRED** before building or modifying any component, page, or layout.
You MUST invoke /skill-name when: [list of triggers]
Do NOT skip this skill because you "already know the brand."
```

**Why it exists**: Skills load context at the moment of maximum relevance. But agents will skip optional steps when context is crowded. Making skills mandatory and listing the specific triggers ("when creating a new component," "when modifying visual appearance") removes ambiguity. The phrase "Do NOT skip this skill because you already know the brand" was added after the agent rationalized skipping the skill in a late-phase session.

### Section 6: Integration Gate (25 lines)

```
## Integration Gate (Mandatory)

After every agent phase, the human MUST run the integration smoke test.

### Process
1. Ensure stack is running
2. Run migrations
3. Run the smoke test script
4. All checks must pass before proceeding
```

**Why it exists**: This is the most critical section in the file. It establishes the human's verification role and makes it non-negotiable. Without this, agents would mark phases complete after unit tests pass. See the [integration gate case study](integration-gate.md) for the failures this caught.

### Section 7: Critical Rules (30 lines)

```
## Critical Rules

### Never Deviate from the Contract
### Territory Boundaries
### Brand Enforcement
### Content Policy
### Prompt Caching (Cost-Critical)
```

**Why it exists**: These are constraints so important that violating any one of them causes cascading failures. The prompt caching section, for example, documents invariants whose violation silently disables caching with no error -- just a 10x cost increase. These rules are in CLAUDE.md because they cross all file boundaries and all agent identities. A rule scoped to `*.py` files would miss the half of the caching invariant that lives in the frontend.

### Section 8: Tech Stack Summary (10 lines)

A table of technology choices with no discussion, no alternatives, no "consider using." Decided, not debated.

**Why it exists**: The agent needs to know the stack to make implementation decisions. If the table says "PostgreSQL 16," the agent uses PostgreSQL 16. It does not suggest MongoDB. The absence of alternatives is the point.

### Section 9: Local Development (8 lines)

```
## Local Development
docker compose up -d
docker compose run --rm backend alembic upgrade head
./scripts/integration-smoke-test.sh
```

**Why it exists**: The agent needs to know how to run the project. These exact commands, in this exact order, bring up the full stack. Agents that guess at run commands waste context on trial and error.

---

## The Key Insight: Table of Contents, Not Encyclopedia

The CLAUDE.md grew to over 400 lines during the middle phases of the project. Quality degraded. The agent started ignoring rules that appeared late in the file. Instructions that worked in phase 5 stopped working in phase 10, not because they were wrong, but because they were buried.

The fix was aggressive pruning. Every line was evaluated:

- Is this a command the agent needs at session start? **Keep in CLAUDE.md.**
- Is this a constraint that applies to specific file types? **Move to a rule in `.claude/rules/`.**
- Is this a procedure the agent should follow for a specific task? **Move to a skill.**
- Is this context the agent can read on demand from a document? **Move to `docs/` and add a pointer.**
- Is this a decision record that matters for future context? **Move to auto-memory.**

The result was 199 lines. Dense, high-signal, no filler. For each remaining line, removing it would cause the agent to make a specific, identifiable mistake. That is the bar.
