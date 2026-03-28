# Cheatsheet: Full-Lifecycle Quick Reference

Copy-paste prompts for every phase of a harness-engineered project. Each phase gives you one human
action, one agent prompt, and one verification step. For depth, follow the chapter link.

---

## Phase 0: Prerequisites

- Claude Code CLI installed and authenticated
- Git initialized (or ready to init)
- A rough idea of what you want to build
- **Seed the template files** into your project so the prompts below can reference them:

  ```bash
  curl -O https://raw.githubusercontent.com/brandonavant/harness-engineering-guide/main/scripts/init-project.py
  python3 init-project.py .
  ```

  This creates a `templates/` directory in your project with starter files for docs, contracts,
  harness configuration, and scripts. Every phase below references files from this directory.

## Phase 1: Interview (Chapter 02)

**You:** Sit down and answer the agent's questions about your project. Do not skip this — the interview
summary feeds every document that follows.

> Run a structured interview to understand my project idea. Ask me questions one at a time covering:
> problem statement, target users, core features for the MVP, tech stack preferences, known
> constraints, non-goals / out-of-scope items, and deployment target. When done, write the summary
> to `docs/interview-summary.md` using the template at `templates/docs/interview-summary-template.md`.

**Verify:** `docs/interview-summary.md` exists and covers all seven areas.
**Depth:** [Chapter 02 -- Project Bootstrap](guide/02-project-bootstrap.md)

## Phase 2: Scaffold (Chapter 02)

**You:** Let the agent create the repo skeleton, initial CLAUDE.md, and a hello-world that proves the
stack works end to end.

> Bootstrap this project based on `docs/interview-summary.md`. Create the directory structure,
> initialize the tech stack, write a CLAUDE.md under 200 lines, and produce a minimal hello-world
> that I can run to verify the stack works.

**Verify:** You can run the hello-world locally and see output. CLAUDE.md exists at the repo root.
**Note:** This verifies framework scaffolding only, not integration boundaries (DB, frontend↔backend, auth). Those are covered by the integration smoke test in [Chapter 07](guide/07-quality-gates.md).
**Depth:** [Chapter 02 -- Project Bootstrap](guide/02-project-bootstrap.md)

## Phase 3: Specify (Chapter 03)

**You:** Generate the full document cascade. Review each document before the agent writes the next one.

> Read `docs/interview-summary.md` and produce the specification documents in this order, waiting for
> my approval after each one:
>
> 1. `docs/prd.md` — Product Requirements Document
> 2. `docs/architecture.md` — Architecture and tech decisions
> 3. `docs/ux-spec.md` — UX specification with screen inventory
> 4. `contracts/api.yaml` — OpenAPI contract
> 5. `docs/brand-identity.md` — Visual language and component conventions
> 6. `.claude/skills/doc-review/SKILL.md` — Skill that validates spec documents against the interview
>    summary for completeness and consistency
>
> Use the corresponding templates in `templates/docs/` and `templates/contracts/`. Each document
> should reference the ones before it, not reinvent details.

**Verify:** All five spec documents exist, are internally consistent, and reference each other. Run the
new `doc-review` skill against each document to confirm.
**Depth:** [Chapter 03 -- Specification Phase](guide/03-specification-phase.md)

## Phase 4: Build the Harness (Chapters 04, 06, 07)

**You:** Set up the context hierarchy, design-intent rules, and quality gates before writing any
application code.

> Based on the specification documents in `docs/` and `contracts/`, create the harness:
>
> 1. Path-scoped rules in `.claude/rules/` for backend, frontend, testing, and database conventions
> 2. A design-intent skill in `.claude/skills/` that enforces brand identity on UI work
> 3. Hook configurations in `.claude/settings.json` for linting and type-checking after file edits
> 4. Update CLAUDE.md to reference these new harness files
> 5. A security-review skill in `.claude/skills/` covering input validation, parameterized queries,
>    auth checks, and OWASP Top 10 awareness
> 6. A `PreToolUse` hook that blocks file writes containing hardcoded secrets (API keys, tokens, passwords)
>
> Do not write application code yet — this phase is infrastructure only.

**Verify:** Rules autoload when you touch a matching path. Hooks fire on tool events (file edits, shell commands).
CLAUDE.md stays under 200 lines.
**Depth:** [Chapter 04 -- Context Architecture](guide/04-context-architecture.md) |
[Chapter 06 -- Design Intent Preservation](guide/06-design-intent.md) |
[Chapter 07 -- Quality Gates](guide/07-quality-gates.md)

## Phase 5: Orchestrate (Chapter 05)

**You:** Define agent boundaries and shared contracts. Skip this phase for single-domain projects where
one agent session handles all work.

> Set up multi-agent orchestration for this project:
>
> 1. Create subagent definitions in `.claude/agents/` — one per domain (e.g., backend, frontend,
>    data). Use `templates/.claude/agents/agent-template.md` as the starting point. Each definition
>    must declare its territory (which files/dirs it owns) and its read-only dependencies.
> 2. Place shared type definitions and contracts in `contracts/` so every subagent reads from the
>    same source of truth.
> 3. Add a contract governance rule to CLAUDE.md: changes to `contracts/` require human approval.
> 4. Verify that no two agent territories overlap on the same files.

**Verify:** Each agent definition has clear territory boundaries. Contracts are in `contracts/` and
referenced by CLAUDE.md.
**Depth:** [Chapter 05 -- Agent Orchestration](guide/05-agent-orchestration.md)

## Phase 6: Decompose (Chapter 08)

**You:** Break the PRD into numbered implementation phases before building anything.

> Read `docs/prd.md` and `docs/architecture.md`. Decompose the MVP into numbered implementation
> phases (aim for 3-6). Each phase should be independently testable and produce a working increment.
> Write the phase plan to `docs/phase-plan.md` with acceptance criteria for each phase.

**Verify:** Each phase has clear boundaries, acceptance criteria, and no circular dependencies.
**Depth:** [Chapter 08 -- Implementation](guide/08-implementation.md)

## Phase 7: Implement — Repeat Per Phase (Chapter 08)

**You:** Execute one phase at a time. Do not skip the acceptance criteria check.

> Implement Phase [N] from `docs/phase-plan.md`.
>
> **Plan:** Read the phase description, acceptance criteria, and all referenced spec documents.
> Outline your implementation approach and wait for my approval before writing code.
>
> **Build:** Implement the phase. Run all linters, type checkers, and tests before marking it
> complete.
>
> **Do NOT:** Modify code outside this phase's scope. Skip tests. Add features not in the spec.
> Disable linters or type checkers to make code pass. Use `any` types or `@ts-ignore` as shortcuts.
>
> **Acceptance criteria:** All items from the phase plan pass. The integration smoke test passes.
> No regressions in prior phases.

**Verify:** Run `templates/scripts/integration-smoke-test.sh` against real services — you run it, not
the agent. Walk the [phase completion checklist](checklists/phase-completion.md) (11 items). If you
corrected the same pattern twice during this phase, build a skill before starting the next one.
**Depth:** [Chapter 08 -- Implementation](guide/08-implementation.md)

## Phase 8: Ship (Chapter 09)

**You:** Set up CI/CD and deployment configuration. The agent writes the pipeline; you execute the
deployment.

> Create the CI/CD pipeline and deployment configuration:
>
> 1. `.github/workflows/ci.yml` — lint, type-check, test on every PR
> 2. `.github/workflows/release.yml` — build and publish on tag
> 3. `Dockerfile` and `docker-compose.yml` for production deployment
> 4. Environment variable documentation in `docs/deployment.md`
> 5. Pin all tool and dependency versions in CI — no `latest` tags, no floating ranges
> 6. Agent writes config only — you provision secrets and execute deployments
>
> Reference `docs/architecture.md` for infrastructure decisions. Do not hardcode secrets — use
> environment variable placeholders.

**Verify:** CI passes on a test PR. Docker build succeeds locally.
**Depth:** [Chapter 09 -- CI/CD and Deployment](guide/09-ci-cd-and-deployment.md)

## Phase 9: Sustain (Chapter 10)

**You:** Establish the practices that prevent codebase decay over time.

> Review the current state of the codebase and set up sustainability practices:
>
> 1. Verify CLAUDE.md is current and under 200 lines
> 2. Check that all rules and skills still match the actual codebase patterns
> 3. Create any missing skills for patterns that required manual correction more than once
> 4. Update `docs/` to reflect what was actually built vs. what was planned
> 5. Run a refactoring pass: naming consistency, error shapes, dead code removal
> 6. Walk the entropy management checklist from Chapter 10 Section 10.8

**Verify:** A fresh Claude Code session can orient itself using only CLAUDE.md and the harness files.
Review the [context reset checklist](checklists/context-reset.md) for session hygiene practices.
**Depth:** [Chapter 10 -- Entropy Management](guide/10-entropy-management.md)

---

## Recurring Practices

These cross-cutting concerns apply throughout the lifecycle, not to a single phase.

**Feedback loop** — When something goes wrong, fix the environment, not just the code. Escalate
through the feedback ladder: conversation correction → path-scoped rule → CLAUDE.md update → skill →
hook → memory. See [Chapter 01 Section 1.5](guide/01-foundations.md).

**Session hygiene** — Run `/clear` between tasks and between phases. If you correct the agent twice
for the same issue, stop and build a rule or skill. Use `/compact` with focus instructions to preserve
key context. See the [context reset checklist](checklists/context-reset.md).

**Integration gate** — Run `templates/scripts/integration-smoke-test.sh` after every phase, after
merging worktree branches, and after infrastructure changes. You run it, not the agent. This is the
single most important practice in the guide. See [Chapter 08](guide/08-implementation.md).

**Security** — Invoke the security-review skill for any code touching input handling, database
queries, authentication, file uploads, or external APIs. The pre-commit secret-scanning hook is a
backstop, not a replacement for review. See [Chapter 07](guide/07-quality-gates.md).

**Reactive skill-building** — After each phase ask: "Did I correct the same thing last time?" If yes,
build a skill now. Early phases produce 2-3 new skills; late phases produce nearly none. That
compounding effect is the goal.

---

## Further Reading

- [Chapter 01 -- Foundations](guide/01-foundations.md) — The harness engineering paradigm and feedback loop
- [Chapter 11 -- Failure Modes](guide/11-failure-modes.md) — What goes wrong and how to fix it
- [Project Kickoff checklist](checklists/project-kickoff.md) — Pre-flight checks before starting a new project
- [Phase Completion checklist](checklists/phase-completion.md) — 11-item gate to run after each implementation phase
- [Context Reset checklist](checklists/context-reset.md) — Session hygiene when switching tasks or hitting context limits
- [Pre-Merge checklist](checklists/pre-merge.md) — Final verification before merging a feature branch
- [`templates/`](templates/) — Starter files for CLAUDE.md, spec documents, contracts, and harness configuration
