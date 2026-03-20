# Chapter 10 -- Entropy Management: Fighting Drift in Agent-Generated Code

> **Part 5: SUSTAIN** | Templates: `CLAUDE.md`, `.claude/rules/`, `skills/`

Left unattended, agent-generated codebases degrade. Not because the agent writes bad code — it writes competent code that replicates whatever patterns it finds. The problem is that it replicates all patterns equally, including the suboptimal ones. Without active intervention, small inconsistencies compound into systemic drift. This chapter covers the practices that prevent that decay.

---

## Principles

**Entropy is the default.** Every session that does not explicitly reinforce standards introduces small deviations. These are invisible individually and devastating in aggregate.

**Clean sessions beat corrected sessions.** A fresh context with a good prompt produces better output than a long context with accumulated corrections. Session hygiene is not a convenience — it is a quality practice.

**Documentation rots.** Instructions that were accurate three phases ago may be wrong today. Rules that addressed real problems may now address solved problems. Stale documentation is worse than no documentation because it misdirects the agent with confidence.

**Skills compound; drift compounds.** Every skill you build eliminates a class of errors permanently. Every uncorrected pattern gets replicated. The question is which compounding force wins.

---

## 10.1 Session Hygiene

Session management is the first line of defense against entropy. Most quality problems trace back to a degraded context — a session that has been running too long, has accumulated too many corrections, or has drifted from its original purpose.

### The /clear discipline

Use `/clear` between unrelated tasks. This is not optional. A session that started with "implement the auth module" and pivoted to "fix the CSS on the settings page" carries auth-module context that is irrelevant to the CSS fix. That irrelevant context does not just waste tokens — it actively contaminates the agent's decisions. The agent may reference auth patterns when styling a button, not because the patterns are relevant, but because they are present.

Rules of thumb:
- **Different domain?** `/clear`. Backend work and frontend work are different domains even in the same project.
- **Different phase?** `/clear`. Phase B4 context does not help Phase B5.
- **Same task, but the agent is stuck?** `/clear` and restart with a better prompt.

### The two-correction rule

If you correct the agent twice on the same issue and it still gets it wrong, stop correcting. The context is degraded. The agent is pattern-matching against the earlier (wrong) attempts as much as against your corrections.

Instead:
1. `/clear`
2. Write a skill that encodes the correct pattern
3. Restart the task with the skill invocation in the prompt
4. The agent now has the correct pattern with zero noise

This feels slower. It is faster. The time you spend writing the skill is recouped on the current task and every future task.

### Using /compact effectively

When a task is genuinely ongoing and you cannot `/clear`, use `/compact` with specific focus instructions:

```
/compact Focus on: implementing the SSE streaming endpoint.
Retain: the message schema, the streaming protocol, the error handling pattern.
Discard: earlier exploration of WebSocket alternatives and the prompt builder discussion.
```

Without focus instructions, `/compact` compresses everything equally, which may preserve the noise you want to discard. With focus instructions, it prioritizes the signal.

**CLAUDE.md survives compaction.** After `/compact`, Claude Code re-reads your CLAUDE.md from disk and injects it fresh into the session. Instructions in CLAUDE.md are never lost to compaction. If an instruction disappeared after compacting, it was given only in conversation — add it to CLAUDE.md to make it persist across resets.

### What the Human Should Do

Develop a habit of starting each work block with a fresh context. Before giving the agent a task, ask: "Is the current context helping or hurting?" If the answer is not clearly "helping," `/clear`.

### What the Agent Should Do

When you notice your context growing large and your responses becoming less focused, suggest a `/compact` or `/clear` to the human. Better to acknowledge context degradation than to produce degraded output.

---

## 10.2 Doc Gardening

Your documentation — CLAUDE.md, rules, skills, design docs — is a living system. It requires regular maintenance, just like code.

### What to look for

**Solved problems still documented as rules.** In Phase 3, you added a rule: "Always use UTC timestamps, never local time." By Phase 6, every timestamp in the codebase is UTC. The agent follows the pattern from the code itself. The rule is now dead weight in your token budget. Remove it.

**Rules that no longer match the codebase.** You added a rule: "Use the `ApiError` class for all error responses." Then you refactored to use a different error handling approach. The rule now points the agent at a pattern that no longer exists. Worse, the agent may try to recreate the old pattern. Update or remove the rule.

**Conflicting rules.** One rule says "use Tailwind utility classes." Another, added later, says "use CSS modules for component-specific styles." Both were correct at different times. Together, they create inconsistency. Resolve the conflict.

**Overly verbose instructions.** Your CLAUDE.md grew to 500 lines. Half of it is context that was relevant during scaffolding but is no longer needed. The agent reads all 500 lines on every invocation. Trim it.

### The gardening cadence

After every 3-5 phases (roughly every 1-2 weeks of active development):

1. Read through CLAUDE.md. Remove anything the agent consistently gets right without being told.
2. Review `.claude/rules/`. Check each rule against the current codebase. Update or remove stale rules.
3. Review skills. Check each skill against the current patterns. Update examples that reference old code.
4. Check version numbers in design docs. If a doc says "v2.0" but has been updated since, bump the version.

### The 200-line budget

Keep CLAUDE.md under 200 lines. This is not an arbitrary limit — it is a practical constraint based on the token cost of loading instructions on every invocation and the diminishing returns of longer instruction sets.

When CLAUDE.md exceeds 200 lines:
- Move domain-specific instructions to skills (loaded on demand, not on every invocation)
- Move file-pattern-specific instructions to rules (loaded only when relevant files are edited)
- Remove instructions for patterns the agent has internalized

### What the Human Should Do

Schedule doc gardening. Put it on your calendar. It takes 15-30 minutes and prevents hours of debugging caused by stale instructions. If you cannot remember the last time you reviewed CLAUDE.md, it is overdue.

### What the Agent Should Do

When a rule or instruction seems to conflict with the current codebase, flag it. "The rule says to use `ApiError` but the codebase uses `AppException`. Should I follow the rule or the codebase?" This surfaces stale documentation immediately.

---

## 10.3 Golden Principles

Golden principles are opinionated, mechanical rules that keep the codebase legible. They are not architectural decisions — those belong in design docs. They are day-to-day coding standards that prevent the slow accumulation of inconsistency.

### Why mechanical rules matter

Claude produces working code. The problem is that "working" is a low bar. Code can work and be inconsistent, hard to read, or structured differently from module to module. Mechanical rules eliminate the variance.

### Example principles

**Prefer shared utilities over hand-rolled helpers.**

```python
# Bad: every module rolls its own timestamp formatting
def format_timestamp(dt):
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")

# Good: one utility, used everywhere
from app.utils.time import format_iso_timestamp
```

Why this matters: when you need to change timestamp formatting (and you will), you change it in one place. When every module has its own version, you change it in twenty places and miss three.

**Validate at boundaries, trust internal code.**

```python
# At the API boundary: validate everything
@router.post("/campaigns")
async def create_campaign(request: CreateCampaignRequest):
    # Pydantic validated the request. Internal code trusts the types.
    campaign = await campaign_service.create(request.name, request.character_id)
    return campaign

# Internal service: no defensive re-validation
async def create(self, name: str, character_id: UUID) -> Campaign:
    # Trust that name is a string and character_id is a UUID.
    # Do not re-validate here.
    ...
```

Why this matters: defensive programming everywhere makes code harder to read and creates false confidence. If you validate at every layer, you never know which layer is actually responsible.

**Structured logging with consistent field names.**

```python
# Bad: unstructured, inconsistent
logger.info(f"Created campaign {campaign.id} for user {user.id}")
logger.info(f"Campaign creation failed: {e}")

# Good: structured, consistent field names
logger.info("campaign.created", campaign_id=campaign.id, user_id=user.id)
logger.error("campaign.create_failed", error=str(e), user_id=user.id)
```

Why this matters: structured logs can be queried. When something breaks at 3 AM, you need `campaign_id=abc123` not a regex over prose.

**One pattern for error handling.**

```python
# Define once
class AppError(Exception):
    def __init__(self, code: str, message: str, status: int = 500):
        self.code = code
        self.message = message
        self.status = status

class NotFoundError(AppError):
    def __init__(self, resource: str, id: str):
        super().__init__(
            code="RESOURCE_NOT_FOUND",
            message=f"{resource} {id} not found",
            status=404,
        )

# Use everywhere
raise NotFoundError("Campaign", str(campaign_id))
```

### Encoding golden principles

Put golden principles in CLAUDE.md if they are universal and short:

```markdown
## Golden Principles
- Prefer shared utilities over hand-rolled helpers.
- Validate at boundaries, trust internal code.
- Structured logging: `logger.info("event.name", key=value)`.
- One error hierarchy: AppError → domain-specific subclasses.
```

Put detailed examples in a skill if the principle needs illustration:

```markdown
# skills/error-handling.md
[... examples, exception hierarchy, response format ...]
```

---

## 10.4 Refactoring Passes

After shipping a feature, review the output for drift. Not every line — that defeats the purpose of using an agent. Focus on the patterns that accumulate variance.

### What to look for

**Naming inconsistency.** The agent used `get_campaign` in one module and `fetch_campaign` in another. Both work. The inconsistency makes the codebase harder to navigate.

**Abstraction drift.** Phase B3 introduced a `BaseRepository` pattern. Phase B5 introduced endpoints that bypass the repository and query the database directly. Both work. The inconsistency means some business logic lives in repositories and some in route handlers.

**Dead code.** The agent refactored a utility but left the old version in place. Both exist. Nothing calls the old one. It will confuse future sessions.

**Inconsistent error handling.** One endpoint returns `{"error": "Not found"}`. Another returns `{"detail": "Not found"}`. Another returns `{"message": "Resource not found", "code": 404}`. All are "correct." The inconsistency makes the frontend's error handling a mess.

### How to refactor

Open targeted refactoring tasks. Each task addresses one specific pattern:

```
Refactor: Normalize error responses across all endpoints.

All endpoints should use the AppError hierarchy and return the standard
error shape: {"error": {"code": "...", "message": "...", "details": {...}}}.

Check every endpoint in apps/backend/src/api/. Fix any that deviate.
Run the full test suite after changes. Update tests that assert on the
old error shapes.
```

Small, focused refactoring tasks are easy to review and safe to merge. Large "clean up everything" tasks are dangerous and rarely finish.

### Cadence

After every 2-3 phases, allocate one session to refactoring. This is not a luxury — it is maintenance. If you skip it, the next feature phase will be slower because the agent is navigating an inconsistent codebase.

The key is regularity. Fifteen minutes of refactoring after every few phases is dramatically better than a painful quarterly cleanup sprint.

### What the Human Should Do

During PR reviews, note patterns that are drifting. Keep a lightweight list. When the list has 3-5 items, open a refactoring task. Do not let the list grow to 20 items.

### What the Agent Should Do

When you notice inconsistency during implementation (a module that does things differently from its neighbors), flag it. "I notice `user_service.py` uses a different error pattern than `campaign_service.py`. Should I normalize this now or add it to the refactoring backlog?" This surfaces drift at discovery time, when it is cheapest to fix.

---

## 10.5 Version Tracking in Documents

Every design document should carry metadata:

```markdown
---
version: 3.0
date: 2026-03-10
author: Architecture Agent
change_summary: Revised for Phase 4b decisions (Neo4j choice, BFL integration, Better Auth)
---
```

This serves three purposes:

**Audit trail.** When something looks wrong, you can trace when and why it changed. "The architecture doc says to use WebSockets, but we are using SSE. When did this change?" Check the version history.

**Drift detection.** If a design doc says "v2.0" and the implementation has deviated significantly, the doc is stale. Either update the doc to reflect reality or bring the implementation back in line.

**Agent context.** When the agent reads a design doc, the version metadata tells it how current the information is. A doc dated six months ago in an active project is probably stale. A doc dated last week is probably current.

### What the Human Should Do

When you make a decision that changes the architecture or design, update the relevant doc. Bump the version. Write a change summary. This takes two minutes and saves hours of confusion later.

### What the Agent Should Do

When you modify a design doc, update the version metadata. When you read a design doc that conflicts with the current codebase, flag the discrepancy. Never silently follow a stale doc — the human needs to know the doc is out of date.

---

## 10.6 Automated Cleanup

Some entropy can be detected and fixed automatically. This is the highest-leverage form of maintenance because it scales without human attention.

### Pre-commit hooks

Chapter 6 covered hooks in detail. In the context of entropy management, hooks serve as automatic formatters:

```yaml
# .pre-commit-config.yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.11.13
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/mirrors-prettier
    rev: v4.0.0
    hooks:
      - id: prettier
        types_or: [javascript, typescript, css, json, yaml]
```

These catch formatting drift on every commit. The agent never has to think about import ordering or line length — the hook fixes it automatically.

### Background agent tasks

For patterns that hooks cannot catch, consider periodic background tasks:

```
Scan all API endpoints for deviation from the standard error response shape.
For each deviation:
1. Create a targeted fix
2. Open a PR with the fix
3. Include before/after examples in the PR description
```

These tasks can be run on a schedule (weekly) or triggered by milestones (after every third phase). Most produce small, reviewable PRs that can be merged in under a minute.

### What patterns are automatable?

- **Formatting and import ordering** (pre-commit hooks)
- **Naming convention enforcement** (custom linter rules)
- **Unused import/variable detection** (standard linter rules)
- **Error response shape validation** (custom test or script)
- **Design token usage** (grep for banned color values, check for correct CSS custom properties)
- **Documentation freshness** (script that checks doc versions against recent commit dates)

### What patterns require human judgment?

- Abstraction level (is this over-engineered or appropriately generalized?)
- Naming quality (the name is consistent but is it clear?)
- Architecture alignment (the code works but does it fit the architecture?)
- User experience (the component renders but does it feel right?)

Automate what you can. The time saved on mechanical checks frees you to focus on judgment calls.

---

## 10.7 The Compounding Effect

This is the key insight of entropy management: skills, rules, and hooks compound in your favor. Every investment you make in the harness pays dividends on every future task.

### The skill library as institutional knowledge

By Phase 8 of a project, your skill library might look like this:

```
skills/
  error-handling-patterns.md
  api-endpoint-structure.md
  component-architecture.md
  test-patterns.md
  database-migration-guide.md
  streaming-protocol.md
  auth-integration.md
  design-token-usage.md
```

Each of these encodes knowledge that was earned through correction. The error handling skill exists because Phase 3 produced inconsistent errors. The streaming protocol skill exists because Phase 4 had three attempts at SSE before the pattern was right.

A new agent session — even with a different model version, even months later — picks up these skills and produces output that reflects all of that accumulated learning. This is how agent-generated code gets better over time, not worse.

### Measuring the compounding effect

Track two metrics across phases:

**Corrections per phase.** In early phases, you might make 10-15 corrections per PR review. By late phases, this should drop to 2-3. If it is not dropping, you are not building skills from your corrections.

**Time to complete a phase.** Early phases take longer because you are building the harness alongside the code. Late phases should be faster because the agent has better instructions, more skills, and more consistent patterns to follow.

If both metrics are trending in the right direction, your harness is working. If they are flat or worsening, something is rotting — probably stale documentation or missing skills.

### The alternative

Without active entropy management, the compounding works against you. Each phase introduces small inconsistencies. The agent replicates those inconsistencies in the next phase. By Phase 8, the codebase has eight phases' worth of accumulated drift, and every new feature is harder to build because the agent cannot tell which pattern to follow.

This is not hypothetical. Teams that use AI coding tools without a harness report spending increasing time on "cleanup" as projects progress. The cleanup is addressing drift that was never prevented. With a harness, the drift is caught at the source.

---

## 10.8 Entropy Management Checklist

Use this checklist after every 3-5 phases:

```
[ ] Review CLAUDE.md — remove solved rules, update stale instructions
[ ] Review .claude/rules/ — check each rule against current codebase
[ ] Review skills/ — update examples, remove obsolete skills
[ ] Check design doc versions — update any that lag behind implementation
[ ] Run a naming consistency scan — grep for variant names of the same concept
[ ] Run an error response shape scan — verify all endpoints match the standard
[ ] Check test count trend — is it growing with each phase?
[ ] Check corrections per phase — is it decreasing?
[ ] Review token usage — any unexpected spikes?
[ ] Schedule next gardening session
```

Fifteen to thirty minutes, every couple of weeks. This is the cost of keeping a codebase healthy. The cost of not doing it is much higher — you just pay it later, all at once, when the codebase is too inconsistent for the agent to navigate.

---

Next: [Chapter 11 -- Failure Modes: Common Mistakes and How to Avoid Them](11-failure-modes.md)
