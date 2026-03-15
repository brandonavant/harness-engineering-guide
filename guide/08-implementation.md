# Chapter 8: Implementation — The Human-Agent Loop

> **Part 4: BUILD** | Templates: `.agent-instructions/*.md`, `.agent-state/*.md`, `scripts/integration-smoke-test.sh`

This is the chapter where the real work happens. Everything before this — the harness, the specs, the design system — was scaffolding. Implementation is where you spend 80% of your time, and it is where most guides go silent. They show you how to set up a project and then skip to maintenance, as if the months of building in between are self-explanatory.

They are not. Building a production application with Claude Code requires a specific rhythm: decompose work into phases, execute each phase through a disciplined loop, verify integration at every boundary, and build skills reactively as you discover gaps. This chapter covers all of it.

---

## Principles

**Small phases, tight feedback loops.** A phase that takes more than three agent sessions is too large. You lose coherence, context, and the ability to course-correct.

**Integration is the only truth.** Agent tests pass against mocks. Your unit tests pass against stubs. The only test that matters is the one where real services talk to each other. Run the integration gate after every phase — no exceptions.

**Skills compound; corrections do not.** Every time you correct the agent, ask yourself: will this come up again? If yes, encode it as a skill or rule. A correction made once in a skill applies to every future component. A correction made in chat applies to nothing.

**The human provides judgment; the agent provides output.** You decide what to build, in what order, and whether the result is good enough. The agent decides how to implement it, what tests to write, and how to structure the code. Blurring this boundary — micromanaging implementation or rubber-stamping PRs — leads to worse outcomes.

---

## 8.1 Decomposing Work into Phases

Break your project into numbered implementation phases. Each phase is a coherent unit of work — something that could be described in a sentence and verified with a specific set of tests.

### Sizing phases

A good phase is:
- **Small enough** to complete in 1-3 agent sessions (a session being roughly one context window's worth of work)
- **Large enough** to be a meaningful increment (produces working code, not just scaffolding)
- **Independently verifiable** (has clear acceptance criteria and testable outcomes)

### Naming convention

Use prefixed numbering to identify the domain:

```
B1: Database models, schemas, app factory
B2: GET endpoints, auth integration
B3: Admin auth, rate limiting, persona management API
B4: Annotation parser, output parser, prompt builder, SSE streaming
F1: Design system, shell layout, navigation
F2: Auth pages (login, register, forgot password)
F3: Persona management UI
F4: Character discovery (grid, filters, search, detail sheet)
```

The `B` prefix is backend, `F` is frontend. If you have a single-stack app, use sequential numbers. The prefixes matter when you have multiple agents working in parallel — they prevent territorial confusion.

### Ordering phases

Dependencies dictate order. A phase that requires the database cannot come before the phase that defines the schema. Within those constraints, prefer this ordering:

1. **Data layer first** — models, migrations, schemas
2. **Core business logic** — the parts that are unique to your application
3. **API endpoints** — expose the business logic
4. **UI** — consume the endpoints
5. **Polish** — accessibility, animation, error states
6. **Infrastructure** — CI/CD, deployment, monitoring

This is not rigid. You will interleave frontend and backend work. But the dependency direction should always flow downward through this list.

### What the Human Should Do

Write down the phase list before implementation begins. Keep it in your project memory or a planning document. Expect it to change — phases will split, merge, reorder, and expand as you learn. The point is not a perfect plan; it is a shared understanding of what comes next.

### What the Agent Should Do

When you kick off a phase, the agent should confirm its understanding of scope before writing code. If the phase description is ambiguous, the agent should ask clarifying questions. After confirmation, the agent plans the approach, breaks it into increments, and begins.

---

## 8.2 Anatomy of a Phase

Every phase follows the same lifecycle:

```
Plan → Implement → Test → Integrate → Review → Merge
```

### Plan

The agent reads the relevant design docs, the API contract, and the current state file. It proposes an approach: what files will be created or modified, what tests will be written, what order the work will proceed in.

The human reviews the plan and approves or redirects. This takes five minutes and saves hours.

### Implement

The agent works in increments. Each increment is a logical unit — a model and its migration, an endpoint and its tests, a component and its stories. After each increment, the agent runs the relevant test suite.

```
# Agent's internal rhythm:
1. Write the model → run model tests
2. Write the endpoint → run endpoint tests
3. Write the integration test → run full suite
4. Update the state file
```

### Test

Tests are not optional. Every phase should increase the test count. Track this explicitly:

```markdown
## Phase B4 Results
- Tests before: 170
- Tests after: 268
- New tests: 98
- All passing: yes
```

The agent should run tests after each increment, not just at the end. Catching a regression immediately is minutes of work. Catching it after three more increments is hours.

### Integrate

After the code is written and tests pass, verify integration. This means:
- Docker builds succeed
- Migrations run cleanly
- Services start and respond to health checks
- The integration smoke test passes

The agent should do as much of this as possible. The human runs the final integration gate.

### Review

The agent opens a pull request. The PR description should include:
- What was implemented
- What tests were added
- What integration checks passed
- Any known limitations or follow-up work

The human reviews the PR for correctness, taste, and architectural alignment. This is where human judgment is irreplaceable — the agent can produce working code that is architecturally wrong.

### Merge

After approval, merge to main. The CI pipeline runs. The release pipeline builds and deploys. The human verifies the production smoke test.

---

## 8.3 The Human-Agent Loop During Active Coding

This is the daily rhythm of building with Claude Code.

### Kicking off a phase

Give the agent a clear scope message. Include:
- **What to build**: specific features, endpoints, components
- **What NOT to build**: boundaries matter as much as goals
- **Acceptance criteria**: how you will know it is done
- **Relevant context**: design doc sections, API contract paths, existing patterns to follow

Example:

```
Phase B4: Annotation parser, output parser, prompt builder, SSE streaming.

Build:
- Annotation parser that handles *action* and (( annotation )) syntax
- Output parser that splits AI responses into narrative/dialogue/action segments
- Prompt builder with static/dynamic split for caching
- SSE streaming endpoint for character responses
- Scene opener generation (non-streaming)

Do NOT build:
- Multi-character routing (Phase B7)
- Phrase bank or repetition detection (Phase B8)
- Any frontend changes

Acceptance criteria:
- All parser edge cases tested (empty input, nested syntax, malformed input)
- Prompt builder produces correct Anthropic API format
- SSE endpoint streams tokens to a curl client
- Scene opener returns complete formatted response
- Docker build succeeds, migrations clean, smoke test passes

Reference: docs/architecture.md Section 4.3, contracts/openapi.yaml paths /campaigns/*/messages
```

### Agent autonomy during implementation

Once kicked off, the agent should work autonomously. It reads the relevant files, implements in increments, runs tests, and updates its state file. You do not need to supervise each line of code.

The agent should use subagents for:
- **Research**: reading multiple files to understand an existing pattern before replicating it
- **Parallel exploration**: investigating two possible approaches simultaneously
- **Keeping exploration out of the main context**: a subagent that reads 20 files and returns a summary is cheaper than loading all 20 files into the main context

### Human review points

You engage at specific moments:
1. **Phase kickoff**: provide scope and context
2. **PR review**: evaluate the output for correctness, taste, and alignment
3. **Integration gate**: run the smoke test
4. **Course corrections**: when something is going wrong mid-phase

### When to course-correct

Watch for these signals:
- The agent is going in circles, making and reverting the same change
- Test failures are accumulating rather than decreasing
- The agent is building something outside the phase scope
- The output "feels wrong" — generic, over-engineered, or inconsistent with the project's character

When you see these, either:
- Provide a targeted correction if the issue is small
- `/clear` and restart the phase with a better prompt if the issue is fundamental

After two failed corrections on the same issue, always `/clear`. A fresh start with a refined prompt almost always outperforms accumulated corrections in a degraded context.

---

## 8.4 The Integration Gate Ritual

This is the single most important practice in the entire guide. After every phase, the human runs the integration smoke test. No exceptions. No shortcuts.

### Why agent tests are not enough

Agent tests mock system boundaries. The frontend tests mock the API. The backend tests mock the database (or use a test database). This means:
- Frontend tests pass even when the API proxy is misconfigured
- Backend tests pass even when the database schema does not match the models
- Both pass even when auth cookies are formatted differently than expected

These are not hypothetical failures. We hit every single one of these during development:

```
Known integration failures caught by the smoke test:
- Better Auth cookie format (token.signature) not parsed by backend auth dependency
- SQLAlchemy models not matching actual Postgres schema after migration fix
- No API proxy from Next.js to FastAPI (api-client.ts called /api/* on frontend server)
- Graphiti sidecar Dockerfile had wrong build-backend value
```

Every one of these passed agent tests. Every one would have been a production outage.

### The smoke test structure

A good integration smoke test covers:
1. **Service health**: all services respond to health checks
2. **Auth flow**: register a user, get a session, verify cookies propagate
3. **Core CRUD**: create, read, update, delete the primary entities
4. **Page loads**: every frontend route returns 200
5. **Cross-service flows**: operations that span multiple services

```bash
#!/bin/bash
# integration-smoke-test.sh — run after every phase
set -euo pipefail

PASS=0
FAIL=0

check() {
  local desc="$1"; shift
  if "$@" > /dev/null 2>&1; then
    echo "PASS: $desc"
    ((PASS++))
  else
    echo "FAIL: $desc"
    ((FAIL++))
  fi
}

# Service health
check "Backend health" curl -sf http://localhost:8000/health
check "Frontend loads" curl -sf -o /dev/null http://localhost:3000

# Auth flow
REGISTER_RESP=$(curl -sf -X POST http://localhost:3000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"name":"Smoke Test","email":"smoke@test.com","password":"Test1234!"}')
check "User registration" [ -n "$REGISTER_RESP" ]

SESSION_COOKIE=$(echo "$REGISTER_RESP" | jq -r '.token // empty')
check "Session cookie present" [ -n "$SESSION_COOKIE" ]

# Core CRUD through the proxy
check "List personas" curl -sf -H "Cookie: session=$SESSION_COOKIE" \
  http://localhost:3000/api/personas

# Frontend pages
for path in / /discover /personas /stories /account; do
  check "Page loads: $path" curl -sf -o /dev/null "http://localhost:3000$path"
done

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ] || exit 1
```

### Extending the smoke test

As you add features, extend the smoke test. Every new cross-service flow gets a check. The smoke test should grow with the application — if it stays static while the app expands, it is no longer catching integration failures.

### What the Human Should Do

Run the smoke test after every phase. If any check fails, stop. Do not start the next phase. Fix the integration issue first. This feels slow, but it is dramatically faster than discovering integration failures three phases later.

### What the Agent Should Do

Before opening a PR, verify that Docker builds succeed and services start. Run whatever subset of integration checks can be automated within the agent's environment. Document in the PR which integration checks you verified and which require the human to run.

---

## 8.5 Reactive Skill-Building

You will not anticipate every pattern the agent needs to follow. Some patterns only become obvious after seeing the agent get them wrong. This is normal and expected. The key is to encode corrections as skills the moment you identify a recurring issue.

### The pattern

1. **Phase N**: agent produces inconsistent error handling across three endpoints
2. **You notice**: during PR review, you see three different error response shapes
3. **You build a skill**: `skills/error-handling-patterns.md` that defines the canonical error response shape, the exception hierarchy, and examples
4. **Phase N+1 onward**: agent uses the skill, error handling is consistent

### When to build a skill vs. add a rule

**Build a skill** when the guidance is domain-specific, involves multiple examples, and exceeds a few lines. Skills are loaded on demand and do not consume your CLAUDE.md budget.

```markdown
# skills/error-handling-patterns.md
# Error Handling Patterns

## Response Shape
All error responses MUST use this structure:
{
  "error": {
    "code": "RESOURCE_NOT_FOUND",
    "message": "Human-readable description",
    "details": {}  // optional, for validation errors
  }
}

## Exception Hierarchy
- AppError (base) → 500
  - NotFoundError → 404
  - ValidationError → 422
  - AuthError → 401
  - ForbiddenError → 403

## Examples
[... concrete code examples ...]
```

**Add a rule** when the guidance is short, universal, and always relevant. Rules go in `.claude/rules/` and are loaded automatically when files matching their glob are edited.

```markdown
# .claude/rules/api-endpoints.md
# globs: apps/backend/src/api/**/*.py

- All endpoints return the standard error shape defined in skills/error-handling-patterns.md
- Never return raw exception messages to clients
- Always validate request body before business logic
```

### Skill velocity over time

In early phases, you will build 2-3 skills per phase. By the middle of the project, you will build maybe one per phase. By the end, you rarely need new skills because the library covers most patterns.

This is the compounding effect in action. Each skill you build makes the next phase smoother. A project that invested in skills through Phase 3 will move significantly faster through Phases 6-8 than one that corrected the same issues every phase.

### What the Human Should Do

During every PR review, ask: "Did I correct the same thing last time?" If yes, build a skill. Maintain a lightweight log of corrections — even a checklist — to spot recurring patterns.

### What the Agent Should Do

When given a skill, follow it precisely. If a skill conflicts with another skill or rule, flag the conflict rather than silently choosing one. After completing a phase, note in the state file which skills were used and whether any gaps were discovered.

---

## 8.6 Handling Blocked Phases

Not every phase can proceed to completion. External dependencies, ambiguous requirements, and cross-agent conflicts all create blockers. The worst thing an agent can do is silently work around a blocker.

### External service dependencies

Many features require live API credentials that do not exist during early development. The agent mocks these in tests, which is correct for unit testing but masks integration failures.

```
| Blocker                  | What's Needed                        |
|--------------------------|--------------------------------------|
| LLM integration          | ANTHROPIC_API_KEY                    |
| Embedding search         | AZURE_OPENAI_ENDPOINT, AZURE_OPENAI_KEY |
| Image generation         | BFL_API_KEY                          |
| Content moderation       | AZURE_CONTENT_SAFETY_ENDPOINT        |
| Blob storage             | AZURE_STORAGE_CONNECTION_STRING      |
```

When the agent hits a phase that cannot be fully tested without live services, it must STOP and notify the human. The agent documents the blocker in its state file:

```markdown
## Phase B6: Portrait Generation Pipeline
Status: BLOCKED
Blocker: BFL API key required for end-to-end image generation testing.
  Mocked tests pass (14/14), but real API integration is unverified.
Action needed: Human provisions BFL API key and sets BFL_API_KEY env var.
```

### Ambiguous requirements

When the design doc is unclear about a specific behavior, the agent should not guess. It should document the ambiguity and ask:

```
The UX spec says "display relationship status" but doesn't specify:
1. Where on the character card (header? footer? badge?)
2. What states are possible (the enum isn't defined in the contract)
3. Whether it's visible before the first interaction

Which of these should I decide vs. wait for clarification?
```

### Cross-agent conflicts

When multiple agents work on the same codebase, they can produce conflicting changes. Common conflicts:
- Both agents modify the same shared type
- Backend changes the response shape without updating the contract
- Frontend adds an API call to an endpoint that does not exist yet

Prevent this with territory boundaries in agent instructions and the API contract as the source of truth. When conflicts occur, the human arbitrates.

### What the Human Should Do

Check state files regularly for blockers. Provision external services proactively — if Phase 6 needs an API key, get it before Phase 6 starts. When ambiguities surface, make a decision quickly and record it in the design doc.

### What the Agent Should Do

Never mock your way past a real dependency without flagging it. Document every blocker immediately. Continue working on non-blocked tasks within the phase if possible, but clearly mark what is incomplete and why.

---

## 8.7 Cost Management During Implementation

Building an application with Claude Code is not free. Token costs accumulate across phases, and without deliberate cost management, they can surprise you. This section covers the practical strategies that make the difference.

### Prompt caching

If your application uses the Anthropic API (as many AI-powered apps do), prompt caching is the single highest-leverage cost optimization. It reduces input token costs by roughly 90% on cache hits.

The architecture:

```
System prompt (STATIC — cached across turns)
├── Character personality
├── World rules
├── Writing style guidelines
└── Response format instructions

Last user message (DYNAMIC — rebuilt each turn)
├── Knowledge graph facts for this scene
├── Relationship state
├── Recent context summary
└── User's actual message
```

**The key invariant**: static parts do not change between turns. Dynamic parts are injected only into the last message and are never persisted. On the next turn, the message is loaded clean from the database, preserving the cache prefix.

**Verifying caching works**: check your logs for token usage. On cache hits, `cache_read` should be large and `input` should be small. On misses, `cache_read` is zero and `cache_write` is the full prefix.

```
# Good (cache hit):
Token usage: input=2,100 cache_read=45,000 cache_write=0 output=850

# Bad (cache miss — something broke the prefix):
Token usage: input=47,100 cache_read=0 cache_write=45,000 output=850
```

### Model selection

Not every task needs the most capable model.

| Task | Recommended Model | Why |
|------|-------------------|-----|
| Architecture, complex specification | Opus | Needs deep reasoning across many constraints |
| Standard implementation | Sonnet | Good balance of capability and cost |
| Simple fixes, doc review, formatting | Haiku | Fast, cheap, sufficient for mechanical tasks |
| Subagent research tasks | Sonnet or Haiku | Depends on complexity of what's being read |

Context management IS cost management. A 100K-token context costs more per inference than a 20K-token context. Use `/clear` aggressively. Use `/compact` with focus instructions when the task is ongoing but context is growing.

### Subagent cost awareness

Each subagent call is a separate inference call with its own context. Use subagents deliberately:

**Good uses**: parallel research across multiple files, keeping large file reads out of the main context, exploring two approaches simultaneously.

**Bad uses**: reflexive delegation ("let me have a subagent check that"), trivial lookups that could be done with a simple file read, spawning subagents for tasks that take fewer tokens than the subagent overhead.

A subagent that reads 10 files and returns a 200-word summary is cheaper than loading all 10 files into the main context. A subagent that reads one file and returns its contents is more expensive than reading the file directly.

### What the Human Should Do

Monitor token usage across phases. If costs spike unexpectedly, investigate: is the context growing too large? Are subagents being spawned excessively? Is prompt caching broken? Set a per-phase budget expectation and flag deviations.

### What the Agent Should Do

Prefer targeted file reads over broad searches. Use `/compact` proactively when context is growing. When spawning subagents, state the purpose explicitly. Keep state files updated so the human can restart a session without rebuilding context from scratch.

---

## 8.8 State Tracking

Agent state files create accountability and continuity. They are the bridge between sessions — when you `/clear` or start a new conversation, the state file tells the next session what has been done.

### State file structure

```markdown
# Backend Agent State

## Current Phase
B4: Annotation parser, output parser, prompt builder, SSE streaming

## Completed Tasks
- [x] Annotation parser with full test suite (28 tests)
- [x] Output parser with segment classification (19 tests)
- [x] Prompt builder with static/dynamic split (31 tests)
- [ ] SSE streaming endpoint
- [ ] Scene opener generation

## Test Results
- Total tests: 198 (170 before phase + 28 new)
- All passing: yes

## Integration Status
- Docker build: passing
- Migrations: clean
- Smoke test: 14/16 passing (SSE and scene opener not yet implemented)

## Files Modified
- apps/backend/src/parsers/annotation.py (new)
- apps/backend/src/parsers/output.py (new)
- apps/backend/src/prompt/builder.py (new)
- apps/backend/tests/parsers/ (new, 47 tests)
- apps/backend/tests/prompt/ (new, 31 tests)

## Blockers
None

## Contract Deviations
- Added `narrative` type to ParsedSegment enum (not in OpenAPI spec yet)
```

### Why this matters

Without state files, every new session starts from zero. The agent has to re-read the codebase, re-discover what has been done, and re-infer the current state. This wastes tokens and introduces errors.

With state files, the agent reads its state, confirms it matches reality (a quick check of test counts and file existence), and resumes.

### What the Human Should Do

Glance at state files between sessions. They tell you whether the agent's work is safe to merge, what blockers exist, and whether the agent is on track. If the state file looks incomplete or inaccurate, ask the agent to update it before proceeding.

### What the Agent Should Do

Update the state file after completing each task within a phase. Be precise about test counts, file lists, and integration status. When you discover a blocker or deviation, record it immediately — not at the end of the session.

---

## 8.9 Common Mistakes

These are the implementation mistakes we have seen repeatedly. Awareness is the first defense.

**Phases that are too large.** A phase that takes 3+ sessions loses coherence. The agent forgets context, the human loses track of what has been reviewed, and integration failures accumulate. Split large phases proactively.

**Not running the integration gate.** "The tests pass, so it must work." No. Agent tests pass against mocks. The integration gate catches the failures that mocks hide. Run it every time.

**Ignoring test failures.** "It is just a flake." Maybe. But a test that fails intermittently is a test that is telling you something. Investigate immediately. Flaky tests erode trust in the entire test suite.

**Not committing before context resets.** If the agent's work is not committed before you `/clear` or switch tasks, it exists only in the agent's context — and that context is about to be destroyed. Always ensure work is committed to a branch before any context reset.

**Not building skills reactively.** Every correction that is not encoded in a skill will be repeated. The third time you correct the same pattern, you have wasted two corrections' worth of tokens and review time.

**Rubber-stamping PRs.** The agent produces plausible-looking code. It compiles. Tests pass. It is tempting to merge without careful review. Do not. The agent makes systematic errors that only human judgment catches: wrong abstraction level, inconsistent naming, architectural drift, missing edge cases.

**Micromanaging implementation.** The opposite failure. Telling the agent exactly which lines to write defeats the purpose. Give scope and constraints, then let the agent work. Review the output, not the process.

**Skipping the plan step.** Jumping straight to "implement this phase" without reviewing the agent's approach. The five minutes you spend reviewing the plan saves the hours you would spend correcting a wrong approach mid-implementation.
