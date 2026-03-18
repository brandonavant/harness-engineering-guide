# Harness Engineering Guide for Claude Code

A prescriptive, step-by-step guide for building production software
using [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with zero manually-written code.

This guide covers the complete lifecycle from "I have nothing but an idea" to "I have a maintained product." It is
written for both the human engineers who steer the process and the AI agents who execute it.

---

## What This Is

Most agentic coding advice is scattered across blog posts, Twitter threads, and case studies that assume unlimited
budgets and enterprise tooling. This guide is different. It is a single, opinionated playbook for a specific tool (
Claude Code) and a specific workflow (human steers, agent builds everything).

The core insight: **your job is no longer writing code. It is designing the environment that makes the agent productive.
** That environment -- your CLAUDE.md, rules, skills, hooks, design docs, and contracts -- is what we call the **harness
**. This guide teaches you how to build one.

## Who This Is For

- **Engineers adopting agentic coding** who want a structured approach instead of trial and error
- **AI agents operating inside Claude Code** who need to understand their operating constraints, feedback channels, and
  the principles behind the harness they work within
- **Technical leads evaluating** whether agentic coding can work for their team or product

You should have basic familiarity with git, a terminal, and at least one modern tech stack. You do not need prior
experience with AI coding tools.

## What You Will Learn

- The paradigm shift from writing code to designing agent environments
- How to go from a rough idea to a complete specification suite that agents can execute against
- How to configure Claude Code's harness features (CLAUDE.md, rules, skills, hooks) for reliable output
- How to manage multi-phase implementation with integration gates and quality checkpoints
- How to sustain a codebase long-term: feedback loops, context management, cost control, and iterative improvement

## Guide Structure

The guide follows five parts, each building on the last.

### Part 1: Understand

**[Chapter 01 -- Foundations: The Harness Engineering Paradigm](guide/01-foundations.md)**
The mental model shift. What harness engineering is, why context is your scarcest resource, the human engineer's new
role, cost realities, and the feedback loop that makes corrections compound.

### Part 2: Specify

**[Chapter 02 -- Project Bootstrap: From Idea to First Agent Run](guide/02-project-bootstrap.md)**
Starting from nothing. The interview process, repository scaffolding, writing your initial CLAUDE.md, and verifying the
setup with a first successful agent run.

**[Chapter 03 -- Specification Phase: Producing Docs Agents Can Execute Against](guide/03-specification-phase.md)**
The document cascade: PRD, architecture, UX spec, API contract, brand identity. How to write specs that agents can
implement against without ambiguity.

### Part 3: Harness

**[Chapter 04 -- Context Architecture: The Progressive Disclosure Hierarchy](guide/04-context-architecture.md)**
The five-tier context hierarchy, how to structure each tier, and the golden rule: never load everything at once.

**[Chapter 05 -- Agent Orchestration: From Single Session to Teams](guide/05-agent-orchestration.md)**
When and how to scale from a single session to multi-agent coordination: territory boundaries, shared contracts,
worktree isolation, and integration gates.

**[Chapter 06 -- Design Intent Preservation: The Anti-Slop System](guide/06-design-intent.md)**
A five-layer defense system that prevents generic, "vibe-coded" output and makes the agent's path of least resistance
match your brand's requirements.

**[Chapter 07 -- Quality Gates: Verification, Enforcement, and Integration Testing](guide/07-quality-gates.md)**
The verification hierarchy from automatic hooks to integration smoke tests. Linters, type checkers, tests, and the
feedback loops that turn plausible code into reliable code.

### Part 4: Build

**[Chapter 08 -- Implementation: The Human-Agent Loop](guide/08-implementation.md)**
The build rhythm: decompose work into phases, execute through a disciplined loop, verify integration at every boundary,
and build skills reactively as gaps emerge.

**[Chapter 09 -- CI/CD and Deployment: Pipelines for Agent-Generated Code](guide/09-ci-cd-and-deployment.md)**
CI/CD pipeline design, release automation, deployment patterns, and the boundary between what the agent writes and what
the human executes.

### Part 5: Sustain

**[Chapter 10 -- Entropy Management: Fighting Drift in Agent-Generated Code](guide/10-entropy-management.md)**
Practices that prevent codebase decay: session hygiene, documentation maintenance, and active intervention against
pattern drift.

**[Chapter 11 -- Failure Modes: Common Mistakes and How to Avoid Them](guide/11-failure-modes.md)**
A catalog of failure modes ordered by project phase — what each looks like, why it happens, and how to fix it.

## Checklists

Standalone checklists for key moments in the project lifecycle:

- [Project Kickoff](checklists/project-kickoff.md) — Pre-flight checks before starting a new project
- [Phase Completion](checklists/phase-completion.md) — Verification steps at the end of each implementation phase
- [Context Reset](checklists/context-reset.md) — What to do when starting a fresh agent session mid-project
- [Pre-Merge](checklists/pre-merge.md) — Final checks before merging agent-generated code

## Quick Start

**Option A: Read the guide from the beginning.**
Start with [Chapter 01](guide/01-foundations.md) and follow the sequence.

**Option B: Copy the templates into an existing project.**
Browse the [`templates/`](templates/) directory for starter files you can drop into your repo: CLAUDE.md templates, doc
templates, OpenAPI stubs, and skill definitions.

**Option C: Jump to a specific topic.**
Each chapter is self-contained enough to read independently, though the concepts build on each other.

## Sources and Further Reading

This guide draws on research and published guidance from multiple sources:

- [Harness Engineering](https://www.linkedin.com/pulse/harness-engineering-new-discipline-behind-openais-million-line-raza-5s8yf/) --
  The concept of designing environments for AI agent productivity, informed by OpenAI's experience building large-scale
  codebases with Codex
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) -- Anthropic's research
  on context engineering, prompt design, and agent architecture patterns
- [Claude Code Best Practices](https://docs.anthropic.com/en/docs/claude-code/best-practices) -- Anthropic's official
  guidance on CLAUDE.md structure, rules, skills, hooks, and agent configuration
- [Agents](https://www.anthropic.com/engineering/an-introduction-to-agents) -- Anthropic's introduction to the agentic
  paradigm and design principles
- [Agents Companion](https://google.github.io/adk-docs/agents/) -- Google's agent development patterns, tool design, and
  multi-agent coordination strategies

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*This guide is a living document. Contributions, corrections, and experience reports are welcome.*
