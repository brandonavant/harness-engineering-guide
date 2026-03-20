# Chapter 07 -- Quality Gates: Verification, Enforcement, and Integration Testing

> **Part 3: HARNESS** | Maps to templates: `templates/.claude/hooks/README.md`,
`templates/scripts/integration-smoke-test.sh`, `templates/.claude/skills/example-checklist.md`

Give Claude a way to verify its work. This is the single highest-leverage thing you can do.

Without feedback loops, Claude produces plausible code. It compiles. It looks reasonable. It may even pass a
surface-level review. But plausible is not correct. Edge cases are missed. Integration boundaries break silently.
Security vulnerabilities replicate from training data patterns. Verification turns plausible into reliable.

This chapter covers the verification hierarchy — from automatic hooks that run after every file edit to integration
smoke tests that catch the failures unit tests cannot.

---

## Principles

**Verification compounds.** Each layer of verification catches a different class of error. Linters catch syntax and
style. Type checkers catch contract violations. Tests catch logic errors. Integration tests catch boundary failures. No
single layer is sufficient. Together, they form a safety net with very small holes.

**Automatic beats advisory.** A rule in CLAUDE.md says "run the linter." A hook runs the linter automatically after
every file edit. The rule depends on the agent remembering. The hook does not. For anything objective and deterministic,
prefer automatic enforcement.

**Fast feedback beats thorough feedback.** A linter that runs in 500ms after every file edit provides more value than a
full test suite that runs in 5 minutes at the end of a phase. The agent can correct course immediately rather than
accumulating errors.

---

## The Verification Hierarchy

### Level 1: Hooks — Automatic, After Every Edit

Hooks are scripts that run automatically after Claude Code edits a file. They are configured in `.claude/hooks/` and
execute without agent intervention. The agent sees the output — including errors — and can react immediately.

**What hooks are good for:**

- Linting (syntax errors, style violations, import ordering)
- Formatting (consistent code style)
- Type checking (contract violations, missing types)
- Quick validation (file structure, naming conventions)

**What hooks are NOT good for:**

- Full test suites (too slow for per-edit execution)
- Integration testing (requires running services)
- Subjective quality checks (design review, code architecture)

**Hook configuration:**

Claude Code hooks are defined in `.claude/hooks/` or in your project's Claude Code settings. They specify a trigger (
file pattern), a command, and an error behavior.

**Example: Python linting after every edit**

```json
{
  "hooks": {
    "afterEdit": [
      {
        "match": "**/*.py",
        "command": "ruff check --fix ${file}",
        "onError": "warn"
      }
    ]
  }
}
```

**Example: TypeScript type checking after edits**

```json
{
  "hooks": {
    "afterEdit": [
      {
        "match": "**/*.{ts,tsx}",
        "command": "tsc --noEmit --pretty",
        "onError": "warn"
      }
    ]
  }
}
```

**Error messages matter.** When a hook fails, the agent reads the error output. Well-formatted error messages that
include the file, line number, and remediation suggestion enable the agent to fix the issue immediately. Cryptic error
codes require the agent to search for documentation, wasting context and time.

Standard tools like `ruff`, `tsc`, and `eslint` already produce well-structured output with file paths, line numbers,
and rule descriptions — they handle this well out of the box. The risk arises when you write **custom hook scripts** for
project-specific validations: naming conventions, file structure checks, migration consistency, required headers, or
architecture boundary enforcement. These scripts are where terse, unhelpful error messages creep in, because there is no
linter framework generating the output for you — you write it yourself.

**Example: a custom naming-convention hook**

A well-written custom hook script produces output the agent can act on immediately:

```
apps/backend/src/routes/users.py:45:5: NAMING-001
  Endpoint function must use snake_case with HTTP verb prefix.
  Found: getUser
  Fix: Rename to get_user
```

Compare to what a lazily written version of the same script produces:

```
NAMING-001: naming violation at line 45
```

This requires the agent to read the file, figure out what is on line 45, and guess what "naming violation" means in this
context. For every custom hook script, invest the time to include the file path, the offending code, and a concrete fix
in the error output.

---

### Level 2: Skills — Mandatory, Invoked Before Work

Skills are checklists and validation workflows that the agent invokes before or after specific categories of work.
Unlike hooks, skills are not automatic — they require the agent to follow an instruction in CLAUDE.md or its subagent
definition.

**What skills are good for:**

- Design enforcement (Chapter 6)
- API contract validation
- Security review checklists
- Pre-commit quality gates
- Any check that requires reading multiple files and making a judgment

**Example: API contract check skill**

```markdown
# API Contract Check

## When to invoke

After implementing or modifying any API endpoint, request/response schema, or frontend API call.

## Process

1. Read contracts/openapi.yaml for the relevant endpoint.
2. Compare implementation against contract:
    - [ ] HTTP method and path match
    - [ ] Request body fields, types, and required/optional match
    - [ ] Response body fields and types match
    - [ ] All documented status codes are handled
    - [ ] Error response shape matches contract
3. If deviation found:
    - Do NOT modify the contract
    - Document in your agent memory under "Contract Deviations"
    - Continue implementation with the deviation noted
```

**The skill-to-hook promotion pattern:** Start a verification as a skill (advisory). If the agent repeatedly fails to
invoke it, or if violations accumulate, promote it to a hook (automatic). Skills are the staging area for enforcement
rules.

---

### Level 3: Test Suites — Agent-Run, Per Phase

The agent runs the project's test suite as part of its workflow. Tests verify logic, behavior, and contracts at a deeper
level than linting.

**Invest in making tests fast and reliable.** If your test suite takes 10 minutes, the agent will run it once at the end
of a phase and miss intermediate regressions. If it takes 30 seconds, the agent runs it after every significant change
and catches errors immediately.

**Test commands belong in CLAUDE.md and subagent definitions:**

```markdown
## Testing

- Backend: `pytest apps/backend/tests/ -v` (target: <60 seconds)
- Frontend: `npm test -- --watchAll=false` (target: <90 seconds)
- Run after completing each phase. All tests must pass before proceeding.
```

**Agent testing patterns that work:**

- Run the targeted test file after changing a module: `pytest apps/backend/tests/test_users.py -v`
- Run the full suite before marking a phase complete
- If a test fails, fix it before moving to the next task (do not accumulate failures)

**Agent testing antipatterns:**

- Mocking everything — tests pass but nothing actually works (see Level 4 below)
- Writing tests that only cover the happy path
- Skipping tests "because I'll fix them later"
- Running tests once at the end of a long phase instead of incrementally

---

### Level 4: Integration Smoke Tests — Human-Run, Between Phases

This is where the real failures hide.

**The fundamental problem with agent-written tests:** Agents mock the boundaries they do not own. The backend agent
mocks the database client. The frontend agent mocks the API. The tests pass in isolation. But when you connect the real
frontend to the real backend to the real database, four things can go wrong that no unit test would catch.

**Real-world integration failures caught by smoke tests, missed by 400+ passing unit tests:**

1. **Auth cookie format mismatch.** The auth library sent cookies in `token.signature` format. The backend split on `.`
   expecting `base64.hmac`. Both sides had passing tests with mocked auth. The real cookie was rejected.

2. **ORM/schema drift.** A migration was fixed to add a column, but the SQLAlchemy model was not updated. The migration
   ran fine. The model loaded fine in tests (which used a different fixture). The real query failed at runtime.

3. **Missing API proxy.** The frontend API client called `/api/users`. The frontend server had no proxy configured to
   forward these to the backend. Frontend tests used a mock server at the same origin. The real request returned a 404.

4. **Wrong build configuration.** A sidecar service's Dockerfile specified an incorrect build backend. Unit tests did
   not build the Docker image. The CI pipeline built it and it failed.

None of these are exotic. All of them are common in multi-agent development. All of them are caught by a smoke test that
exercises the real system.

**Smoke test structure:**

```bash
#!/bin/bash
# integration-smoke-test.sh — run after every agent phase
set -e

PASS=0
FAIL=0
TOTAL=0

check() {
  TOTAL=$((TOTAL + 1))
  local description="$1"
  shift
  if "$@" > /dev/null 2>&1; then
    echo "  PASS: $description"
    PASS=$((PASS + 1))
  else
    echo "  FAIL: $description"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Integration Smoke Test ==="
echo ""

# Service health
echo "--- Service Health ---"
check "Backend is running" curl -sf http://localhost:8000/health
check "Frontend is running" curl -sf -o /dev/null http://localhost:3000

# Auth flow
echo ""
echo "--- Auth Flow ---"
REGISTER_RESPONSE=$(curl -sf -X POST http://localhost:3000/api/auth/sign-up \
  -H "Content-Type: application/json" \
  -d '{"email":"smoke@test.com","password":"TestPass123!","name":"Smoke Test"}' \
  2>/dev/null || echo "FAILED")
check "User registration" [ "$REGISTER_RESPONSE" != "FAILED" ]

# Extract session cookie for subsequent requests
SESSION_COOKIE=$(echo "$REGISTER_RESPONSE" | jq -r '.sessionToken // empty')
check "Session token received" [ -n "$SESSION_COOKIE" ]

# API endpoints through proxy
echo ""
echo "--- API Through Proxy ---"
check "List resources via frontend proxy" \
  curl -sf http://localhost:3000/api/resources \
  -H "Cookie: session=$SESSION_COOKIE"

check "Create resource via frontend proxy" \
  curl -sf -X POST http://localhost:3000/api/resources \
  -H "Cookie: session=$SESSION_COOKIE" \
  -H "Content-Type: application/json" \
  -d '{"name":"Smoke Test Resource"}'

# Frontend pages load
echo ""
echo "--- Frontend Pages ---"
check "Home page loads" curl -sf -o /dev/null http://localhost:3000/
check "Dashboard page loads" curl -sf -o /dev/null http://localhost:3000/dashboard
check "Settings page loads" curl -sf -o /dev/null http://localhost:3000/settings

# Summary
echo ""
echo "=== Results: $PASS/$TOTAL passed, $FAIL failed ==="
[ "$FAIL" -eq 0 ] || exit 1
```

**When to run it:**

- After every agent phase completes
- Before starting the next phase
- After merging worktree branches
- After any infrastructure change (Docker config, proxy config, auth config)

**Who runs it:** The human (or the orchestrating session). Not the individual agents. Agents work in isolation and may
not have the full stack running.

**Extending the smoke test:** As new features land, add checks for those flows. The smoke test should grow with the
project. A new API endpoint? Add a check. A new page? Verify it loads. A new auth flow? Exercise it end to end.

---

### Level 5: CI Pipeline — Automatic on PR

The CI pipeline runs automatically when a pull request is opened. It is the final gate before code reaches the main
branch.

**A minimal CI pipeline for agent-driven development:**

```yaml
# .github/workflows/ci.yml
name: CI
on:
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Backend lint
        run: ruff check apps/backend/
      - name: Frontend lint
        run: |
          cd apps/frontend && npm ci && npm run lint
      - name: Type check
        run: |
          cd apps/frontend && npx tsc --noEmit

  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Backend tests
        run: pytest apps/backend/tests/ -v
      - name: Frontend tests
        run: |
          cd apps/frontend && npm ci && npm test -- --watchAll=false

  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - name: Build backend image
        run: docker build -t backend apps/backend/
      - name: Build frontend image
        run: docker build -t frontend apps/frontend/
```

**CI is the backstop, not the primary defense.** If your CI catches a linting error, the hook should have caught it
first. If CI catches a test failure, the agent should have run the tests during development. CI exists to catch what
slips through — the rate of CI failures should decrease as your hooks and skills mature.

---

## The Enforcement Escalation Pattern

Not every rule starts at the highest enforcement level. Rules evolve through three stages:

**Advisory (Tier: CLAUDE.md, docs/)**
The rule exists in documentation. The agent should follow it. There is no mechanical enforcement.

```markdown
# In CLAUDE.md

- Prefer named exports over default exports in TypeScript files.
```

**Mandatory (Tier: Skills)**
The rule is part of a skill checklist. The agent must invoke the skill and verify compliance.

```markdown
# In a skill file

- [ ] All TypeScript exports are named (no default exports)
```

**Mechanical (Tier: Hooks, CI)**
The rule is enforced by tooling. The agent cannot produce output that violates it.

```json
// ESLint rule
{
  "import/no-default-export": "error"
}
```

**When to promote:**

- Advisory to Mandatory: When you observe the agent violating the rule repeatedly despite it being documented
- Mandatory to Mechanical: When the rule is objective, deterministic, and critical — and a tool can enforce it

**When NOT to promote:**

- Subjective rules ("the design should feel premium") cannot be mechanically enforced
- Rules that have legitimate exceptions should stay advisory or mandatory, not mechanical
- Rules that are expensive to check (full build required) should not be hooks (run on every edit)

---

## Security in Quality Gates

Agent-generated code is susceptible to the same vulnerabilities as human-written code — with one additional risk: agents
replicate patterns from training data, including insecure ones. If the training data contains SQL injection patterns,
the agent may reproduce them.

**Security is not a phase — it is a property of every phase.**

**Security-focused skill:**

```markdown
# Security Review

Invoke after implementing any of:

- User input handling
- Database queries
- Authentication/authorization
- File uploads or downloads
- External API calls
- Environment variable usage

## Checklist

- [ ] All user input is validated (type, length, format)
- [ ] Database queries use parameterized statements (no string interpolation)
- [ ] Authentication checks on every protected endpoint
- [ ] Authorization checks (user can only access their own resources)
- [ ] No secrets in source code (API keys, passwords, connection strings)
- [ ] Error responses do not leak internal details (stack traces, SQL, file paths)
- [ ] File uploads validated (type, size, content)
- [ ] CORS configured to allow only expected origins
- [ ] Rate limiting on authentication endpoints
- [ ] HTTPS enforced in production configuration
```

**Secret scanning hook:**

```json
{
  "hooks": {
    "preCommit": [
      {
        "command": "git diff --cached --diff-filter=d | grep -iE '(api_key|secret|password|token)\\s*=\\s*[\"\\x27][^\"\\x27]+' && echo 'BLOCKED: Possible secret in commit' && exit 1 || exit 0",
        "onError": "block"
      }
    ]
  }
}
```

**OWASP Top 10 awareness:** Include a brief reference to OWASP Top 10 in your security skill. The agent does not need
the full spec — it needs the category names and one-sentence descriptions so it can recognize when it is implementing
something that touches a risk area.

```markdown
## OWASP Top 10 Quick Reference

When your code touches any of these areas, apply extra scrutiny:

1. Broken Access Control — verify authorization on every endpoint
2. Cryptographic Failures — never store plaintext secrets, use strong hashing
3. Injection — parameterize all queries, validate all input
4. Insecure Design — validate business logic, not just input format
5. Security Misconfiguration — review default settings, disable debug in prod
6. Vulnerable Components — pin dependency versions, check for known CVEs
7. Authentication Failures — rate limit, enforce strong passwords, secure sessions
8. Data Integrity Failures — validate data at boundaries, sign where needed
9. Logging Failures — log security events, never log secrets
10. SSRF — validate and restrict outbound requests from server
```

**The cost argument:** Security is cheaper to build in from the start than to retrofit. A security skill invoked during
implementation costs one skill load per session. A security audit after 8 phases of implementation costs a full codebase
review and potentially rewriting endpoints. Front-load the investment.

---

## Hook Configuration in Detail

Hooks in Claude Code run scripts at defined trigger points. The key trigger points:

**afterEdit** — Runs after Claude edits a file. Best for: linting, formatting, quick type checks.

**preCommit** — Runs before Claude creates a commit. Best for: secret scanning, test execution, build verification.

**Configuration patterns:**

```json
{
  "hooks": {
    "afterEdit": [
      {
        "match": "**/*.py",
        "command": "ruff check --fix ${file} && ruff format ${file}",
        "onError": "warn"
      },
      {
        "match": "**/*.{ts,tsx}",
        "command": "npx eslint --fix ${file}",
        "onError": "warn"
      },
      {
        "match": "**/*.{ts,tsx}",
        "command": "npx tsc --noEmit --pretty 2>&1 | head -20",
        "onError": "warn"
      }
    ],
    "preCommit": [
      {
        "command": "pytest apps/backend/tests/ -x -q --tb=short",
        "onError": "block"
      }
    ]
  }
}
```

**Design principles for hooks:**

1. **Keep them fast.** Hooks run frequently. A hook that takes 10 seconds disrupts the flow. Target under 2 seconds for
   afterEdit hooks, under 30 seconds for preCommit hooks.

2. **Use `warn` for non-critical issues.** The agent sees the warning and can fix it. Use `block` only for issues that
   must be fixed before proceeding (secrets in commits, failing critical tests).

3. **Include remediation in error output.** The agent reads hook error messages. A good error message tells the agent
   exactly what to do. A bad error message requires the agent to investigate.

4. **Scope narrowly with `match` patterns.** A Python linter should not run when the agent edits a TypeScript file. Use
   file patterns to trigger hooks only for relevant files.

5. **Auto-fix when possible.** `ruff check --fix` and `eslint --fix` correct issues automatically. The agent does not
   need to manually fix formatting or import ordering if the tool can do it.

---

## What the Human Should Do

1. **Set up hooks early.** Before the first agent session, configure afterEdit hooks for linting and formatting. This is
   15 minutes of setup that prevents hundreds of manual corrections.

2. **Write the integration smoke test.** Start with health checks and auth flow. Expand as features land. Run it after
   every agent phase — this is your responsibility, not the agent's.

3. **Set up CI before the first PR.** Even a minimal pipeline (lint + test + build) catches issues before they reach
   main.

4. **Create the security skill.** Use the OWASP Top 10 reference, add project-specific security rules, make it mandatory
   for auth, input handling, and database code.

5. **Review hook failure patterns.** If the same hook failure keeps recurring, the rule may need to be clearer, or it
   may need to be promoted from hook to CI (if it is too slow for per-edit execution).

6. **Do not skip the smoke test.** It is tempting to skip "just this once" when the agent says all tests pass. The smoke
   test catches the failures that agent tests cannot. Run it every time.

---

## What the Agent Should Do

1. **Fix hook failures immediately.** When an afterEdit hook reports an error, fix it in the next edit. Do not
   accumulate lint errors across a phase.

2. **Run tests incrementally.** After changing a module, run its test file. After completing a phase, run the full
   suite. Do not wait until the end to discover 15 test failures.

3. **Invoke security skills when touching sensitive code.** Auth endpoints, database queries, user input handling, file
   operations — these all warrant a security skill invocation.

4. **Do not suppress or ignore hook output.** Hook warnings exist for a reason. Even if the code "works," a warning
   indicates something that will cause problems later.

5. **Include verification results in your agent memory.** After each phase, log: linter status, test count (pass/fail),
   any hook failures encountered and how they were resolved. This creates an audit trail.

6. **Treat CI failure as your bug.** If CI fails on your PR, do not assume it is a flaky test. Investigate, fix, and
   push. The PR should not be reviewed until CI is green.

---

## Putting It All Together

The verification hierarchy forms a pipeline. Each level catches what the previous level missed:

```
Edit a file
  └─ Hook runs linter/formatter (catches syntax, style)
      └─ Agent runs targeted test (catches logic errors)
          └─ Agent invokes skill checklist (catches design/contract drift)
              └─ Agent runs full test suite (catches regressions)
                  └─ Human runs smoke test (catches integration failures)
                      └─ CI runs on PR (catches anything that slipped through)
```

No single level is sufficient. The linter does not catch logic errors. Tests do not catch integration failures. The
smoke test does not catch style violations. Together, they form a defense that catches the vast majority of issues
before they reach production.

The investment is front-loaded. Setting up hooks, writing the smoke test, configuring CI, and creating security skills
takes time upfront. But the return compounds across every session, every phase, and every agent that works on the
project. Verification infrastructure is the gift that keeps giving.

---

Next: [Chapter 08 -- Implementation: The Human-Agent Loop](08-implementation.md)
