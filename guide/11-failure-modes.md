# Chapter 11 -- Failure Modes: Common Mistakes and How to Avoid Them

> **Part 5: SUSTAIN** | Reference chapter

This chapter is a catalog. Each entry describes a failure mode: what it looks like, why it happens, and how to fix it.
Use this as a reference when something goes wrong, or read it end-to-end as a preventive measure before starting a
project.

The failure modes are ordered roughly by when you are most likely to encounter them, from early project setup through
active development to sustained maintenance.

---

## 1. The Kitchen Sink Session

### What it looks like

A single conversation with the agent that started with "implement the auth module," detoured into "fix the button
alignment on mobile," then shifted to "update the database migration for the new field," and is now trying to "write the
SSE streaming endpoint." The context window is full. The agent's responses are slow, unfocused, and occasionally
reference code from the button fix when discussing streaming.

### Why it happens

It is tempting to keep a productive session going. The agent is "warmed up." Switching feels like overhead. But every
unrelated task added to a session dilutes the context. The agent has no mechanism for forgetting — everything stays in
the window, competing for attention.

### How to fix it

`/clear` between unrelated tasks. Full stop. If the tasks are in different domains (backend vs. frontend), different
phases (B3 vs. B5), or different categories (feature work vs. bug fix), they belong in separate sessions.

The overhead of starting a fresh session is small: the agent re-reads CLAUDE.md and its agent memory. This takes seconds
and costs a few thousand tokens. The cost of a degraded context is much larger: wrong output, wasted corrections,
potential regressions.

**Rule of thumb**: one task per session. A "task" is a coherent unit of work with a single goal. If you cannot describe
the session's purpose in one sentence, it is a kitchen sink session.

---

## 2. The Correction Spiral

### What it looks like

The agent produces incorrect output. You correct it. The agent produces a different incorrect output that incorporates
half of your correction and half of the original mistake. You correct again. The agent produces a third variation. Each
attempt is slightly different but never right. Twenty minutes have passed and the code is worse than when you started.

### Why it happens

Each correction adds to the context. The agent now has three versions of the code (two wrong, one partially corrected)
plus two natural-language corrections plus the original prompt. It is pattern-matching against all of this
simultaneously, giving weight to the wrong versions because they occupy more of the context.

### How to fix it

**After two failed corrections, `/clear` and restart.** Do not attempt a third correction. The context is contaminated.

Before restarting:

1. Identify exactly what the agent got wrong
2. Write a skill or provide a concrete example of the correct pattern
3. Start a new session with the skill and a clearer prompt

The restart almost always works on the first attempt because the context contains only the correct pattern, not a
history of failed attempts.

### Prevention

Write clearer initial prompts. Include examples of the desired output. Reference skills that define the pattern. The
most common cause of correction spirals is an ambiguous initial prompt that the agent interprets differently than you
intended.

---

## 3. The Bloated CLAUDE.md

### What it looks like

Your CLAUDE.md has grown to 500+ lines. It covers every decision made since project inception, including decisions that
are no longer relevant. It contains detailed examples that belong in skills. It has a "lessons learned" section with
fifteen bullet points, half of which describe problems that were solved three phases ago.

Every agent invocation loads this entire file, costing thousands of tokens of context on instructions that are mostly
noise.

### Why it happens

It is always easier to add a line than to remove one. Every problem encountered becomes a rule. Every edge case becomes
a warning. The file grows monotonically because no one reviews it.

### How to fix it

Keep CLAUDE.md under 200 lines. This requires active gardening:

1. **Move domain-specific instructions to skills.** The 40-line section on error handling patterns? That is a skill.
   Replace it with one line: "Invoke the error-handling-patterns skill when implementing API endpoints."

2. **Move file-specific instructions to rules.** The instruction "always use CSS custom properties, never Tailwind
   defaults" does not need to be in CLAUDE.md. Put it in `.claude/rules/frontend-styles.md` with a glob pattern
   `apps/frontend/**/*.{tsx,css}`. It loads only when relevant files are touched.

3. **Remove rules for solved problems.** If the agent has not violated a rule in the last five phases, the rule is
   either internalized (the agent follows the pattern from the code) or irrelevant. Either way, remove it.

4. **Remove stale context.** The section explaining why you chose PostgreSQL over MongoDB? That was useful in Phase 1.
   By Phase 6, no one is reconsidering the database. Remove it.

### Prevention

Review CLAUDE.md after every 3-5 phases. Budget 15 minutes. Ask: "If I were the agent reading this for the first time,
which lines would actually change my output?" Keep those. Remove the rest.

---

## 4. Trust Without Verification

### What it looks like

The agent produces clean, well-structured code. It compiles. It looks correct. You merge the PR. A week later, you
discover that the pagination endpoint returns all results when `page_size` is 0 instead of raising a validation error,
that the auth middleware does not check token expiration, and that the file upload endpoint accepts files of any size.

### Why it happens

Agent-generated code is plausible by default. It handles the happy path competently. It often looks better-structured
than human-written code. This creates a trust bias: the code looks good, so it must be good.

But the agent does not adversarially test its own code. It does not think, "What happens if the user sends a negative
page number?" It implements the described behavior and stops.

### How to fix it

Give the agent verification tools and require their use:

- **Tests**: require tests for every endpoint, including edge cases (empty input, maximum values, invalid types, missing
  auth)
- **Linters**: catch code quality issues automatically
- **Pre-commit hooks**: run checks before every commit
- **Type checking**: TypeScript strict mode, Python type annotations with mypy or pyright

And in your phase kickoff, explicitly list edge cases to test:

```
Acceptance criteria:
- Pagination: page_size=0 returns 422, page_size=-1 returns 422
- Auth: expired token returns 401, missing token returns 401
- File upload: files > 10MB return 413, non-image MIME types return 415
```

The agent will test what you ask it to test. If you do not ask, it tests the happy path.

### Prevention

Include edge cases in every phase's acceptance criteria. Build a testing skill that lists the categories of edge cases
to always consider: boundary values, auth failures, invalid input, concurrent access, empty state.

---

## 5. The Mocked Integration

### What it looks like

All tests pass. CI is green. The agent reports everything is working. You deploy. The frontend gets 502 errors because
the API proxy is misconfigured. The auth flow fails because the cookie format from Better Auth does not match what the
backend expects. The database migration runs but the SQLAlchemy models still have the old column names.

### Why it happens

Agent tests mock system boundaries. Frontend tests mock the API with a tool like Prism. Backend tests use test databases
or mock external services. These mocks are correct representations of the *expected* behavior, but they do not verify
that the *actual* system behaves as expected.

Every cross-system integration failure we encountered passed all agent tests:

- Auth cookie format mismatch: frontend test mocked the cookie, backend test mocked the cookie parsing — neither tested
  the actual cookie
- API proxy missing: frontend tests called the mock directly, never going through Next.js rewrites
- Model/schema mismatch: backend tests used the model definition, not the actual database schema

### How to fix it

The integration smoke test (Chapter 8, Section 4). Run it after every phase. It tests real services talking to real
services with real data flowing through real proxies.

Additionally:

- Run database migrations against a real PostgreSQL instance in CI, not SQLite
- Test auth flows end-to-end, not in isolation
- Verify that every frontend API call goes through the proxy configuration

### Prevention

Build the integration smoke test early (Phase 1 or 2) and extend it as features land. The test should be trivial to
run (`./scripts/integration-smoke-test.sh`) and mandatory after every phase.

---

## 6. Premature Multi-Agent

### What it looks like

You set up a backend agent and a frontend agent from the start, give them separate worktrees, and launch them
simultaneously. They produce code that does not integrate. The backend agent invented request shapes that the frontend
agent does not expect. The frontend agent calls endpoints that do not exist. Merging their work requires a full day of
conflict resolution.

### Why it happens

Multi-agent workflows are appealing because they promise parallel progress. But parallelism only works when the
interfaces between agents are precisely defined and stable. In early phases, interfaces are still being discovered.

### How to fix it

Start with a single agent. Use it for Phases 1-3 (at minimum: data layer, core API, basic UI). This establishes the
patterns, interfaces, and conventions that multi-agent work depends on.

Graduate to multi-agent only when:

- The API contract is stable and tested
- Both sides of every interface have at least one working implementation
- Territory boundaries are clear (which files each agent owns)
- The integration smoke test covers the critical cross-agent flows

### Prevention

Resist the temptation to parallelize early. A single agent working sequentially through the first few phases produces a
coherent foundation. Two agents working in parallel on a foundation that does not exist produce two incompatible halves.

---

## 7. The Runaway Subagent

### What it looks like

Token usage spikes. The agent spawns subagents for every file read, every code search, every minor decision. Each
subagent has its own context, its own inference cost, and its own latency. A task that should take one session takes
three, not because the task is complex but because the agent is delegating reflexively.

### Why it happens

Subagents are useful for specific purposes: parallel research, keeping large file reads out of the main context,
exploring multiple approaches simultaneously. But the agent sometimes over-indexes on delegation, spawning subagents for
tasks that would be cheaper and faster to do directly.

### How to fix it

Add guidance to your CLAUDE.md or subagent definitions:

```markdown
## Subagent Usage

Use subagents for:

- Reading 5+ files to synthesize a pattern (keeps main context clean)
- Parallel exploration of two approaches
- Research tasks that might need multiple search rounds

Do NOT use subagents for:

- Reading a single file
- Simple code searches
- Tasks that take fewer tokens than the subagent overhead
```

### Prevention

Monitor token usage across sessions. If you see a spike that does not correlate with task complexity, check for
excessive subagent spawning. A subagent that reads one file and returns its contents costs more than reading the file
directly — the subagent has its own system prompt, context setup, and inference cost.

---

## 8. Design Drift / AI Slop

### What it looks like

Your application looks like every other AI-built application. Gray backgrounds, default shadcn/ui components, generic
spacing, system fonts. The design doc specifies a distinctive aesthetic, but the implementation looks like a Tailwind
template. Users cannot tell your product from a tech demo.

### Why it happens

Claude's training data includes thousands of generic web applications. Without strong constraints, it gravitates toward
the median — the most common patterns from its training data. These patterns are competent but undifferentiated.

Design systems in documentation are necessary but not sufficient. The agent reads the design doc, acknowledges the
aesthetic, and then produces `bg-gray-900` because that is the most common dark background in its training data.

### How to fix it

A three-layer defense:

1. **Design token system.** Define CSS custom properties for every color, spacing value, font, and shadow. The agent
   uses tokens, not raw values.

```css
/* tokens.css */
:root {
    --bg-primary: #0D0A0F;
    --bg-secondary: #171318;
    --bg-tertiary: #1E1921;
    --accent: #C4536A;
    --text-primary: #F2E8E1;
}
```

2. **Design enforcement skill.** A skill that the agent must invoke before building or modifying any component. The
   skill contains banned patterns, required tokens, and a checklist:

```markdown
# Banned patterns (zero tolerance):

- bg-gray-*, bg-zinc-*, text-gray-* (use tokens)
- font-sans without explicit font-family override
- rounded-lg without design-system border radius token
- Any color literal (#xxx) not in tokens.css

# Required patterns:

- All backgrounds use --bg-* tokens
- Headings use Cormorant Garamond
- Body text uses Source Serif 4
- UI elements use Inter
```

3. **Measurable checklist.** After every component, verify:

```
[ ] Zero instances of Tailwind default colors
[ ] Correct typeface for each text role
[ ] Spacing uses design tokens, not arbitrary values
[ ] Component could not be mistaken for a generic template
```

### Prevention

Build the design enforcement skill before Phase F1. Require it on every frontend task. Review screenshots (not just
code) during PR review. The checklist catches drift that accumulates over time — even a well-instructed agent will
occasionally fall back to defaults.

---

## 9. Stale Documentation

### What it looks like

The agent follows an instruction from CLAUDE.md that contradicts the current codebase. It produces code using a pattern
that was correct three phases ago but has since been refactored. You spend 20 minutes debugging before realizing the
agent was following an outdated rule.

### Why it happens

Documentation is never maintained proactively. It is only updated when someone notices it is wrong — and by then, the
damage is done. In an agent workflow, the damage is worse because the agent follows stale instructions with full
confidence. There is no internal doubt, no "this seems different from what I see in the code."

### How to fix it

Doc gardening (Chapter 10, Section 2). Review CLAUDE.md, rules, and skills every 3-5 phases. Remove rules for solved
problems. Update rules that no longer match the codebase. Version-track design docs so staleness is visible.

Additionally, add a meta-rule to CLAUDE.md:

```markdown
If a rule in this file conflicts with the pattern established in the existing
codebase (3+ consistent examples), flag the conflict rather than following
the rule. The codebase may have evolved past the rule.
```

### Prevention

Treat documentation as code. It needs review, it needs updates, and it needs someone accountable for its accuracy.
Schedule regular reviews.

---

## 10. Security as an Afterthought

### What it looks like

Phase 8 of the project. A security review reveals: API endpoints that do not check authorization, user input passed
directly to database queries, secrets logged in plain text, CORS configured to allow all origins, file uploads with no
size or type validation.

Fixing these requires touching every endpoint, every query, every logging call. It takes longer than writing them
correctly would have.

### Why it happens

Security is not the agent's default priority. Without explicit instructions, the agent produces code that works — and "
works" does not include "resists adversarial input." The agent will implement an endpoint that returns data to anyone
who asks, because the task description said "implement the endpoint," not "implement the endpoint with authorization."

### How to fix it

Security skills and hooks from Phase 1:

```markdown
# skills/security-patterns.md

## Authentication

Every endpoint except /health and /auth/* requires a valid session.
Use the `get_current_user` dependency on every protected route.

## Authorization

After authentication, verify the user has access to the requested resource.
A user can only access their own data. Admin endpoints require admin role.

## Input validation

All input is validated by Pydantic models before reaching business logic.
File uploads: max 10MB, allowed MIME types only, virus scan if applicable.

## Logging

Never log: passwords, tokens, API keys, session IDs, PII.
Always log: user_id (for audit), action (for tracing), result (for debugging).

## CORS

Production: allow only your domain.
Development: allow localhost origins.
Never: allow all origins (*).
```

### Prevention

Add security checks to your integration smoke test. Verify that unauthenticated requests to protected endpoints return
401. Verify that user A cannot access user B's data. These checks catch authorization regressions automatically.

---

## 11. The Lost Worktree

### What it looks like

You used worktree-based agent isolation. Two subagents worked in separate worktrees on separate branches. You shut down
the subagents and ran worktree cleanup. The worktree directories are deleted. The branches are deleted. The subagents'
uncommitted work is gone. The subagents' unmerged commits are gone.

### Why it happens

Worktree cleanup is destructive by design — it removes the isolated environment. If the agent did not commit, the
changes exist only in the worktree directory. If the agent committed but you did not merge, the commits exist only on
the worktree branch. Both are deleted by cleanup.

### How to fix it

Strict ordering:

```
1. Agent commits all changes to its worktree branch
2. Agent shuts down
3. Human merges each worktree branch into main (or target branch)
4. Human verifies merge is complete (git log, git diff)
5. Human runs cleanup (worktree removal)
```

Never run cleanup while worktree branches have unmerged work. Never assume the agent committed — verify with `git log`
on the worktree branch before cleanup.

### Prevention

Add the commit-before-shutdown instruction to your CLAUDE.md or subagent definitions:

```markdown
Before shutting down, you MUST:

1. Commit all changes to your worktree branch
2. Push the branch to the remote
3. Report the branch name in your final message
```

And before cleanup, verify:

```bash
# List worktrees and their branches
git worktree list

# For each worktree branch, check if it's been merged
git log main..worktree-branch-name --oneline
# If this shows commits, they need to be merged first
```

---

## 12. Scope Creep Through Agents

### What it looks like

You asked the agent to implement a pagination endpoint. The PR includes: the pagination endpoint, a caching layer you
did not request, a refactoring of the query builder "while I was in there," an update to the API documentation, and a
new utility function "in case we need it later."

Every addition is competent. None was requested. The PR is now three times larger than it should be, harder to review,
and touches files outside the phase scope.

### Why it happens

The agent optimizes for "helpful." When it sees an opportunity to improve something adjacent to its task, it does so —
because its training reward is for being thorough and proactive. Without explicit boundaries, the agent's definition
of "done" expands to include everything it can see from the current task.

### How to fix it

Explicit scope in every phase kickoff:

```
Build:
- Pagination endpoint for campaigns list
- Request/response schemas per OpenAPI contract
- Tests for pagination edge cases

Do NOT build:
- Caching layer (Phase B7)
- Query builder refactoring (separate task)
- API documentation updates (handled by doc generation)
- Utility functions for future use

If you see something that needs fixing outside this scope,
note it in your agent memory under "Observed Issues" — do not fix it.
```

And in your CLAUDE.md or subagent definitions:

```markdown
## Scope Discipline

Implement exactly what the phase specifies. If you notice improvements
outside the scope, document them in your agent memory under "Observed Issues."
Do not implement them. Do not refactor adjacent code. Do not add utilities
"for later." The human will prioritize observed issues for future phases.
```

### Prevention

Review PRs against the phase scope, not just for correctness. If the diff includes files outside the scope, ask why.
Sometimes there is a genuine dependency. Often, it is scope creep.

---

## 13. Cost Surprise

### What it looks like

Your weekly token bill is three times what you expected. Or a single session costs more than the previous five combined.
The project is not proportionally further along.

### Why it happens

Several compounding factors:

- **Broken prompt caching.** If you are using the Anthropic API in your application, a broken cache prefix means every
  turn pays full input cost instead of 10% of input cost. A 10x cost increase with no visible error.
- **Growing context windows.** A session that accumulates 100K tokens of context costs more per inference than a session
  with 20K. Without `/clear` discipline, context grows monotonically.
- **Reflexive subagent usage.** Each subagent is a separate inference call. Five subagents reading one file each costs
  more than reading five files in the main context.
- **Large phases without checkpoints.** A phase that runs for three sessions without committing risks redoing work if
  the context degrades — doubling or tripling the token cost.

### How to fix it

**Prompt caching.** Verify it is working by checking token usage logs. On cache hits, `cache_read` should be large and
`input` should be small. If `cache_read` is consistently zero, something is breaking the prefix. Common causes: dynamic
data in the system prompt, non-deterministic message ordering, modifying messages before passing them to the API.

**Context management.** `/clear` between tasks. `/compact` with focus instructions when context is growing. Start each
work block with a fresh session.

**Model selection.** Use Opus for complex specification and architecture work where the reasoning depth justifies the
cost. Use Sonnet for standard implementation. Use Haiku for mechanical tasks (formatting, simple fixes, doc review). Do
not use Opus for tasks that Sonnet handles well.

**Subagent discipline.** Use subagents for parallel research and large file reads. Do not use them for trivial tasks.
Monitor usage and add guardrails to your CLAUDE.md or subagent definitions if needed.

**Phase sizing.** Small phases with committed checkpoints. If a session goes badly, you lose at most one session's work,
not three sessions'.

### Prevention

Set a per-phase budget expectation. Track actual costs. When costs exceed expectations, investigate immediately. Cost
surprises get worse over time, not better — the pattern that caused the spike will repeat in every future phase.

---

## Quick Reference

| #  | Failure Mode               | First Sign                           | Immediate Action                         |
|----|----------------------------|--------------------------------------|------------------------------------------|
| 1  | Kitchen Sink Session       | Context feels slow and unfocused     | `/clear`, one task per session           |
| 2  | Correction Spiral          | Third correction on same issue       | `/clear`, write a skill, restart         |
| 3  | Bloated CLAUDE.md          | File exceeds 200 lines               | Move detail to skills and rules          |
| 4  | Trust Without Verification | Edge case bugs in production         | Add edge cases to acceptance criteria    |
| 5  | Mocked Integration         | Tests pass, deploy fails             | Integration smoke test after every phase |
| 6  | Premature Multi-Agent      | Merge conflicts on first integration | Single agent for Phases 1-3 minimum      |
| 7  | Runaway Subagent           | Token usage spike                    | Add subagent guidelines to instructions  |
| 8  | Design Drift               | App looks generic                    | Design enforcement skill + token system  |
| 9  | Stale Documentation        | Agent follows outdated pattern       | Doc gardening every 3-5 phases           |
| 10 | Security Afterthought      | Late-stage security audit failures   | Security skills from Phase 1             |
| 11 | Lost Worktree              | Unmerged branches deleted            | Commit, merge, then cleanup              |
| 12 | Scope Creep                | PR larger than expected              | Explicit scope and "do NOT build" list   |
| 13 | Cost Surprise              | Bill exceeds budget                  | Check caching, context, model selection  |
