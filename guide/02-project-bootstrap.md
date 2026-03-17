# Chapter 02 -- Project Bootstrap: From Idea to First Agent Run

> Part 2: Specify

**Entry point**: You have nothing but an idea. No code, no specs, no repo.
**Exit point**: A git repository with an initial CLAUDE.md, a docs/ directory, and a verified first agent run.

**Templates referenced**: `templates/CLAUDE.md`

---

## 2.1 The Interview

The agent's first job is not writing code. It is not scaffolding a project. It is interviewing you.

This may feel unnatural. You came to build something, and the agent wants to ask questions. But this step exists because
the most common failure mode in agentic coding is starting implementation with an underspecified idea. The agent will
happily build whatever you describe, even if what you described is vague, contradictory, or missing critical details.
The interview catches those problems early, when fixing them costs a conversation turn instead of a rewrite.

### What the Interview Covers

The interview is a conversation, not a form. But it should touch on these areas:

**What are you building?**
A one-paragraph description. Not features -- the core experience. "A task manager" is too vague. "A task manager for
freelancers who need to track billable hours across multiple clients with weekly invoice generation" is specific enough
to build against.

**Who is it for?**
A target persona, even a rough one. Age range, technical sophistication, what they care about, what frustrates them
about existing solutions. This shapes every UX decision downstream.

**What is the core experience?**
If your product does one thing well, what is that thing? Everything else is secondary. The agent needs to know what to
optimize for.

**What tech stack do you prefer?**
If you have opinions, state them. "I want a Python backend with FastAPI and a Next.js frontend" is a decision. "Whatever
you think is best" is an abdication that leads to the agent picking whatever its training data over-represents. You do
not need to justify your choices to the agent -- you just need to make them.

**What are your non-negotiables?**
Constraints the agent must never violate. Examples: "Dark mode only," "All data stays on-device," "Must work on
Raspberry Pi," "Content must be appropriate for children," "No vendor lock-in." These become rules.

**What is out of scope?**
Equally important. If you know you do not want a mobile app, say so now. Non-goals prevent the agent from
over-engineering.

### Interview Output

The output of the interview is a structured summary document. It does not need to be long, but it needs to be specific.
Here is what a good output looks like:

```markdown
# Project Interview Summary

## Product Vision

A recipe management app for home cooks who want to organize family recipes,
scale ingredients for different serving sizes, and generate weekly meal plans.

## Target Persona

Home cooks aged 30-55 who maintain a personal recipe collection. Not professional
chefs. Moderate technical comfort (uses apps daily, not a developer). Primary
frustration: recipes scattered across bookmarks, screenshots, and paper.

## Core Experience

The user enters a recipe once and never has to re-enter it. Scaling, meal
planning, and grocery lists are derived automatically.

## Tech Stack Decisions

- Frontend: Next.js (TypeScript, Tailwind CSS)
- Backend: FastAPI (Python 3.12+)
- Database: PostgreSQL
- Deployment: Docker containers

## Non-Negotiables

- Must work offline after initial load (PWA)
- No account required for basic use (local storage first, sync optional)
- Metric and imperial unit support

## Non-Goals (MVP)

- Social features (sharing, commenting)
- Nutritional analysis
- Video or image recognition for recipe import
```

This document becomes the seed for everything that follows: the PRD, the architecture doc, the CLAUDE.md.

### Common Interview Mistakes

**Skipping it entirely.** You tell the agent "build me a recipe app" and it starts coding. The result works,
technically, but it reflects the agent's assumptions, not your vision. You spend more time correcting course than you
saved by skipping the interview.

**Being too vague.** "I want something modern" is not a decision. "I want Tailwind with a dark color scheme and serif
typography" is a decision. Vagueness does not give the agent creative freedom -- it gives it license to pick defaults.

**Treating it as a requirements document.** The interview summary is a conversation artifact, not a spec. It captures
intent. The formal specs come in Chapter 03. Do not try to make the interview output exhaustive.

## 2.2 Repository Scaffold

After the interview, the agent creates the repository structure. This is the physical harness -- the directory layout
that everything else builds on.

### The Ideal Initial Directory Tree

```
my-project/
  .claude/
    rules/          # Scoped rules (added as needed)
    skills/         # Custom skills (added as needed)
  .agent-instructions/
    backend-agent.md    # (if multi-agent; otherwise skip)
    frontend-agent.md
  .agent-state/
    backend-agent.md    # (if multi-agent; otherwise skip)
    frontend-agent.md
  contracts/
    openapi.yaml    # API contract (added in Chapter 03)
  docs/
    interview-summary.md
  scripts/          # Build, test, deploy scripts
  apps/             # Application code (structure depends on stack)
  CLAUDE.md
  .gitignore
  README.md
```

A few notes on this structure:

**`.claude/` is Claude Code's configuration directory.** Rules and skills placed here are automatically discovered. You
do not need to reference them in CLAUDE.md.

**`.agent-instructions/` and `.agent-state/` are for multi-agent setups.** If you are working with a single agent (most
projects start this way), you can skip these. They become important when you have separate agents for backend and
frontend work, each with their own scope and state tracking. We cover this in Chapter 05.

**`contracts/` is separate from `docs/`.** The API contract (OpenAPI YAML) is a formal interface specification, not a
design document. It is the source of truth that both frontend and backend implement against. Keeping it separate
reinforces its special status.

**`docs/` holds design documents.** The interview summary goes here first. The PRD, architecture doc, UX spec, and brand
identity doc will follow in Chapter 03.

**`scripts/` holds automation.** Build scripts, integration tests, deployment helpers. These are often produced by the
agent but reviewed by the human.

### Creating the Scaffold

Tell the agent:

> Initialize a git repository with the directory structure from the guide. Include a .gitignore appropriate
> for [your tech stack]. Place the interview summary in docs/. Create an initial CLAUDE.md based on the interview.

The agent should produce this in one step and commit it. Verify that the commit exists before moving on. Losing scaffold
work to an uncommitted state is a common early mistake.

## 2.3 Writing the Initial CLAUDE.md

CLAUDE.md is the most important file in your project. It is loaded into the agent's context at the start of every
conversation. It determines the baseline quality of every interaction.

And because it is loaded every time, every unnecessary line costs you -- in attention, in context window space, and in
money.

### The 200-Line Rule

Your initial CLAUDE.md should be under 200 lines. This is not arbitrary. In practice, CLAUDE.md files that exceed this
length start to suffer from dilution: important instructions get lost in a sea of nice-to-haves. You can grow it over
time as the project matures, but start lean.

For every line, ask: **"Would removing this cause Claude to make mistakes?"** If the answer is no, cut it.

### What to Include

An initial CLAUDE.md has five sections:

#### 1. Project Context (5-10 lines)

What the project is, in plain language. Not marketing copy -- a technical summary that gives the agent enough context to
make reasonable decisions.

```markdown
# RecipeVault -- Recipe Management App

A recipe management application for home cooks. Users enter recipes once and get
automatic scaling, meal planning, and grocery lists. PWA for offline use.

Built with Next.js (frontend), FastAPI (backend), PostgreSQL (database).
Deployed via Docker.
```

#### 2. Tech Stack (5-15 lines)

Every technology choice that has been decided. Be specific about versions when it matters.

```markdown
## Tech Stack

| Layer      | Technology                                     |
|------------|------------------------------------------------|
| Frontend   | Next.js 15, TypeScript, Tailwind CSS v4        |
| Backend    | FastAPI, Python 3.12+, SQLAlchemy 2.0, Alembic |
| Database   | PostgreSQL 16                                  |
| Auth       | Better Auth                                    |
| Deployment | Docker, Docker Compose                         |
```

#### 3. Build, Test, and Lint Commands (5-15 lines)

The agent needs to know how to run things. If these are missing, the agent will guess, and it will often guess wrong.

````markdown
## Commands

```bash
# Full stack
docker compose up -d
docker compose run --rm backend alembic upgrade head

# Backend tests
docker compose exec backend pytest

# Frontend dev
cd apps/frontend && npm run dev

# Lint
cd apps/backend && ruff check .
cd apps/frontend && npx tsc --noEmit
```
````

#### 4. Pointers to Docs (3-5 lines)

Do not duplicate your design documents in CLAUDE.md. Point to them.

```markdown
## Design Documents

- `docs/interview-summary.md` -- Project requirements and persona
- `contracts/openapi.yaml` -- API contract (source of truth for all endpoints)
- (More docs will be added in the specification phase)
```

#### 5. Critical Rules (10-30 lines)

Rules that, if violated, cause real problems. These are your non-negotiables from the interview, plus any technical
constraints the agent must always respect.

```markdown
## Critical Rules

- All API responses use snake_case field naming per the OpenAPI contract
- No direct commits to main. All changes go through feature branches and PRs
- Never store secrets in code. Use environment variables
- The API contract in contracts/openapi.yaml is the source of truth.
  Both frontend and backend implement against it. Neither modifies it unilaterally
- PostgreSQL migrations via Alembic only. Never modify the database schema manually
```

### What NOT to Include

- **Tutorials or explanations.** CLAUDE.md is not documentation for humans. It is operating instructions for an agent.
- **Aspirational guidelines.** "Try to write clean code" is meaningless. "All functions must have type hints" is
  enforceable.
- **Duplicated content.** If it is in a design doc, do not repeat it in CLAUDE.md. Point to the doc.
- **Temporary notes.** Use `.agent-state/` files for transient state, not CLAUDE.md.
- **Long lists of every technology, library, or pattern.** The agent can read package.json and requirements.txt.
  CLAUDE.md should contain decisions the agent cannot infer from the code itself.

### CLAUDE.md as a Living Document

CLAUDE.md will grow over the life of your project. That is expected. But it should grow because you are encoding lessons
learned and hard-won constraints, not because you are dumping every thought into it.

The feedback loop from Chapter 01 applies directly here. Every time the agent makes a mistake that a CLAUDE.md entry
would have prevented, add that entry. Over time, your CLAUDE.md becomes a precise description of "everything Claude
needs to know to work on this project correctly."

## 2.4 First Successful Run

Before moving to the specification phase, verify that the harness works. This is a smoke test for your environment, not
for application code.

### The Test

Tell the agent:

> Read CLAUDE.md and the interview summary. Then scaffold a minimal hello-world application in the chosen tech stack.
> The backend should serve a single health check endpoint at GET /health that returns {"status": "ok"}. The frontend
> should render a single page that displays the project name.

Then verify:

1. The agent read CLAUDE.md without being reminded to
2. The agent used the correct tech stack (not a different framework, not a different language)
3. The application runs (docker compose up, visit localhost, see the page)
4. The health endpoint returns the expected JSON
5. The agent committed its work to a branch (not directly to main, if that is your rule)

### What Failure Tells You

- If the agent uses the wrong tech stack, your CLAUDE.md tech stack section is unclear or missing.
- If the agent does not commit to a branch, your branching rules are missing or buried.
- If the agent cannot run the application, your build commands are wrong or incomplete.
- If the agent reads the wrong files or seems confused about the project, your project context section needs work.

Each failure is diagnostic. Fix the CLAUDE.md, not the symptom. Then try again.

### Commit the Scaffold

Once the first run succeeds, commit everything. This is your baseline. Every future conversation starts from this state.

```bash
git add -A
git commit -m "Initial scaffold: CLAUDE.md, docs, hello-world app"
```

> :warning: Do not skip this step. We have seen projects lose hours of scaffold work because the agent started a new
> conversation
> and the working directory was not committed. Git is your safety net. Use it early and often.

## 2.5 Common Mistakes

### CLAUDE.md That Is Too Long

You put everything in CLAUDE.md because it feels important. The agent's attention is now spread across 400 lines, and it
misses your critical rules. Start with under 200 lines. Move supplementary guidance into `.claude/rules/` files scoped
to specific file patterns.

### CLAUDE.md That Is Too Vague

"Use best practices" means nothing. "Follow RESTful conventions" means whatever the agent's training data suggests is
most common. Be specific: "All endpoints return HTTP 201 for successful creation, with the created resource in the
response body."

### Missing Build Commands

The agent needs to know how to build, test, and lint the project. If you do not provide these commands, the agent will
try to figure them out from config files, and it will sometimes get them wrong -- especially for Docker-based setups
where the commands run inside containers.

### Skipping the Interview

You have a clear vision in your head, and you want to start building. The problem is that your head is not in the
agent's
context. The interview externalizes your vision into a document the agent can reference. Skip it, and the agent fills in
blanks with assumptions.

### Not Committing Before Moving On

The scaffold works. You are excited. You jump into specs. Three hours later, you realize the scaffold was never
committed and an errant git clean just wiped it. Commit after every milestone, no matter how small.

### Over-Scaffolding

You try to create the entire final directory structure in the bootstrap phase -- every module, every component
directory, every utility file. This is premature. Scaffold what you need now (the harness structure and a hello-world
app). The implementation phases will create the rest.

---

## What the Agent Should Do

If you are an AI agent executing the bootstrap phase, here is your checklist:

1. **Interview the human.** Ask about the product vision, target persona, core experience, tech stack preferences,
   non-negotiables, and non-goals. Do not start building until you have clear answers. If the human gives you a vague
   answer, ask a follow-up.

2. **Produce a structured interview summary.** Write it as a Markdown document in `docs/interview-summary.md`. Include
   all six sections (vision, persona, core experience, tech stack, non-negotiables, non-goals). Commit it.

3. **Create the repository scaffold.** Initialize git (if not already initialized), create the directory structure (
   `.claude/`, `docs/`, `contracts/`, `scripts/`, `apps/`), add a `.gitignore` appropriate for the tech stack, and
   create CLAUDE.md.

4. **Write a focused CLAUDE.md.** Under 200 lines. Include project context, tech stack, build/test/lint commands, doc
   pointers, and critical rules. Do not pad it. Every line must earn its place.

5. **Implement a hello-world application.** A health check endpoint on the backend, a single-page render on the
   frontend. Use the tech stack from the interview. Make it run.

6. **Verify everything works.** Build succeeds. Backend serves the health endpoint. Frontend renders. Tests pass (even
   if there is only one test).

7. **Commit everything.** One clean commit on a feature branch (if branching rules exist) or on main (if this is the
   initial commit). Do not leave uncommitted work.

8. **Report what you produced.** Tell the human: here is the repo structure, here is how to run it, here is CLAUDE.md,
   here are the decisions I made and why.

If at any point you are unsure about a decision -- tech stack, directory structure, naming convention -- ask the human.
Do not guess. The cost of a question is one conversation turn. The cost of a wrong guess is a correction that propagates
through the entire project.

---

Next: [Chapter 03 -- Specification Phase: Producing Docs Agents Can Execute Against](03-specification-phase.md)
