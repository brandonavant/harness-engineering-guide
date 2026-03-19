# Cheatsheet: Full-Lifecycle Quick Reference

Copy-paste prompts for every phase of a harness-engineered project. Each phase gives you one human
action, one agent prompt, and one verification step. For depth, follow the chapter link.

---

## Phase 0: Prerequisites

- Claude Code CLI installed and authenticated
- Git initialized (or ready to init)
- A rough idea of what you want to build

## Phase 1: Interview (Chapter 02)

**You:** Sit down and answer the agent's questions about your project. Do not skip this — the interview
summary feeds every document that follows.

> Run a structured interview to understand my project idea. Ask me questions one at a time covering:
> problem statement, target users, core features for the MVP, tech stack preferences, known
> constraints, and deployment target. When done, write the summary to `docs/interview-summary.md`
> using the template at `templates/docs/interview-summary.md`.

**Verify:** `docs/interview-summary.md` exists and covers all six areas.
**Depth:** [Chapter 02 -- Project Bootstrap](guide/02-project-bootstrap.md)

## Phase 2: Scaffold (Chapter 02)

**You:** Let the agent create the repo skeleton, initial CLAUDE.md, and a hello-world that proves the
stack works end to end.

> Bootstrap this project based on `docs/interview-summary.md`. Create the directory structure,
> initialize the tech stack, write a CLAUDE.md under 200 lines, and produce a minimal hello-world
> that I can run to verify the stack works. Commit when done.

**Verify:** You can run the hello-world locally and see output. CLAUDE.md exists at the repo root.
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
>
> Use the corresponding templates in `templates/docs/` and `templates/contracts/`. Each document
> should reference the ones before it, not reinvent details.

**Verify:** All five documents exist, are internally consistent, and reference each other.
**Depth:** [Chapter 03 -- Specification Phase](guide/03-specification-phase.md)

## Phase 4: Build the Harness (Chapters 04, 06, 07)

**You:** Set up the context hierarchy, design-intent rules, and quality gates before writing any
application code.

> Based on the specification documents in `docs/` and `contracts/`, create the harness:
>
> 1. Path-scoped rules in `.claude/rules/` for backend, frontend, testing, and database conventions
> 2. A design-intent skill in `.claude/skills/` that enforces brand identity on UI work
> 3. Hook configurations for linting and type-checking on pre-commit
> 4. Update CLAUDE.md to reference these new harness files
>
> Do not write application code yet — this phase is infrastructure only.

**Verify:** Rules autoload when you touch a matching path. Hooks fire on commit. CLAUDE.md stays under
200 lines.
**Depth:** [Chapter 04 -- Context Architecture](guide/04-context-architecture.md) |
[Chapter 06 -- Design Intent](guide/06-design-intent.md) |
[Chapter 07 -- Quality Gates](guide/07-quality-gates.md)

## Phase 5: Decompose (Chapter 08)

**You:** Break the PRD into numbered implementation phases before building anything.

> Read `docs/prd.md` and `docs/architecture.md`. Decompose the MVP into numbered implementation
> phases (aim for 3-6). Each phase should be independently testable and produce a working increment.
> Write the phase plan to `docs/phase-plan.md` with acceptance criteria for each phase.

**Verify:** Each phase has clear boundaries, acceptance criteria, and no circular dependencies.
**Depth:** [Chapter 08 -- Implementation](guide/08-implementation.md)

## Phase 6: Implement — Repeat Per Phase (Chapter 08)

**You:** Execute one phase at a time. Do not skip the acceptance criteria check.

> Implement Phase [N] from `docs/phase-plan.md`.
>
> **Build:** Read the phase description, acceptance criteria, and all referenced spec documents.
> Implement the phase. Run all linters, type checkers, and tests before marking it complete.
>
> **Do NOT:** Modify code outside this phase's scope. Skip tests. Add features not in the spec.
> Disable linters or type checkers to make code pass. Use `any` types or `@ts-ignore` as shortcuts.
>
> **Acceptance criteria:** All items from the phase plan pass. The integration smoke test passes.
> No regressions in prior phases.

**Verify:** Run the integration smoke test. Manually verify the increment works end to end. Commit.
**Depth:** [Chapter 08 -- Implementation](guide/08-implementation.md)

## Phase 7: Ship (Chapter 09)

**You:** Set up CI/CD and deployment configuration. The agent writes the pipeline; you execute the
deployment.

> Create the CI/CD pipeline and deployment configuration:
>
> 1. `.github/workflows/ci.yml` — lint, type-check, test on every PR
> 2. `.github/workflows/release.yml` — build and publish on tag
> 3. `Dockerfile` and `docker-compose.yml` for production deployment
> 4. Environment variable documentation in `docs/deployment.md`
>
> Reference `docs/architecture.md` for infrastructure decisions. Do not hardcode secrets — use
> environment variable placeholders.

**Verify:** CI passes on a test PR. Docker build succeeds locally.
**Depth:** [Chapter 09 -- CI/CD and Deployment](guide/09-ci-cd-and-deployment.md)

## Phase 8: Sustain (Chapter 10)

**You:** Establish the practices that prevent codebase decay over time.

> Review the current state of the codebase and set up sustainability practices:
>
> 1. Verify CLAUDE.md is current and under 200 lines
> 2. Check that all rules and skills still match the actual codebase patterns
> 3. Create any missing skills for patterns that required manual correction more than once
> 4. Update `docs/` to reflect what was actually built vs. what was planned

**Verify:** A fresh Claude Code session can orient itself using only CLAUDE.md and the harness files.
**Depth:** [Chapter 10 -- Entropy Management](guide/10-entropy-management.md)

---

## Further Reading

- [Chapter 11 -- Failure Modes](guide/11-failure-modes.md) — What goes wrong and how to fix it
- [`checklists/`](checklists/) — Verification checklists for kickoff, phase completion, context reset, and pre-merge
- [`templates/`](templates/) — Starter files for CLAUDE.md, spec documents, contracts, and harness configuration
