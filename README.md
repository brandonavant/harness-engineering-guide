# Harness Engineering Guide for Claude Code

A prescriptive, step-by-step guide for building production software using [Claude Code](https://docs.anthropic.com/en/docs/claude-code) with zero manually-written code.

This guide covers the complete lifecycle from "I have nothing but an idea" to "I have a maintained product." It is written for both the human engineers who steer the process and the AI agents who execute it.

---

## What This Is

Most agentic coding advice is scattered across blog posts, Twitter threads, and case studies that assume unlimited budgets and enterprise tooling. This guide is different. It is a single, opinionated playbook for a specific tool (Claude Code) and a specific workflow (human steers, agent builds everything).

The core insight: **your job is no longer writing code. It is designing the environment that makes the agent productive.** That environment -- your CLAUDE.md, rules, skills, hooks, design docs, and contracts -- is what we call the **harness**. This guide teaches you how to build one.

Every technique in this guide was validated by building a production application across 19 implementation phases, producing 434+ backend tests and a full frontend, with zero lines of manually-written code.

## Who This Is For

- **Engineers adopting agentic coding** who want a structured approach instead of trial and error
- **AI agents operating inside Claude Code** who need to understand their operating constraints, feedback channels, and the principles behind the harness they work within
- **Technical leads evaluating** whether agentic coding can work for their team or product

You should have basic familiarity with git, a terminal, and at least one modern tech stack. You do not need prior experience with AI coding tools.

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
The mental model shift. What harness engineering is, why context is your scarcest resource, the human engineer's new role, cost realities, and the feedback loop that makes corrections compound.

### Part 2: Specify

**[Chapter 02 -- Project Bootstrap: From Idea to First Agent Run](guide/02-project-bootstrap.md)**
Starting from nothing. The interview process, repository scaffolding, writing your initial CLAUDE.md, and verifying the setup with a first successful agent run.

**[Chapter 03 -- Specification Phase: Producing Docs Agents Can Execute Against](guide/03-specification-phase.md)**
The document cascade: PRD, architecture, UX spec, API contract, brand identity. How to write specs that agents can implement against without ambiguity.

### Part 3: Harness

**Chapter 04 -- Configuring the Claude Code Harness** *(coming soon)*
Deep dive into CLAUDE.md structure, .claude/rules/, custom skills, hooks (pre/post-commit, build verification), and the agent instruction pattern.

**Chapter 05 -- Multi-Agent Coordination** *(coming soon)*
Territory boundaries, shared contracts, worktree isolation, state files, and the integration gate pattern.

### Part 4: Build

**Chapter 06 -- Implementation Phases** *(coming soon)*
Phase planning, the build-test-verify cycle, mock-first development, managing agent context across long sessions, and when to start a new conversation.

**Chapter 07 -- Quality Gates and Integration Testing** *(coming soon)*
Smoke tests, contract validation, visual verification, and the principle that agent tests pass even when real integration is broken.

### Part 5: Sustain

**Chapter 08 -- Feedback Loops and Iterative Improvement** *(coming soon)*
Turning mistakes into permanent fixes via CLAUDE.md updates, new rules, and refined skills. Memory files, lessons-learned patterns, and context pruning.

**Chapter 09 -- CI/CD and Deployment** *(coming soon)*
Automating the pipeline: CI on PR, release on merge, container builds, auto-deployment, and production smoke tests.

## Quick Start

**Option A: Read the guide from the beginning.**
Start with [Chapter 01](guide/01-foundations.md) and follow the sequence.

**Option B: Copy the templates into an existing project.**
Browse the [`templates/`](templates/) directory for starter files you can drop into your repo: CLAUDE.md templates, doc templates, OpenAPI stubs, and skill definitions.

**Option C: Jump to a specific topic.**
Each chapter is self-contained enough to read independently, though the concepts build on each other.

## Built With This Guide

The techniques in this guide were developed and validated while building a production application: a multi-character AI story engine with a FastAPI backend, Next.js frontend, PostgreSQL + Neo4j data layer, and real-time SSE streaming. The project was completed across 19 agent phases (8 backend, 11 frontend) with:

- 434+ backend tests, 16-check integration smoke test
- Full CI/CD pipeline with ARM64 container builds and automated deployment
- Zero lines of manually-written code throughout the entire implementation

The guide generalizes those lessons into patterns any project can use.

## Sources and Further Reading

This guide draws on research and published guidance from multiple sources:

- [Harness Engineering](https://www.linkedin.com/pulse/harness-engineering-new-discipline-behind-openais-million-line-raza-5s8yf/) -- The concept of designing environments for AI agent productivity, informed by OpenAI's experience building large-scale codebases with Codex
- [Building Effective Agents](https://www.anthropic.com/engineering/building-effective-agents) -- Anthropic's research on context engineering, prompt design, and agent architecture patterns
- [Claude Code Best Practices](https://docs.anthropic.com/en/docs/claude-code/best-practices) -- Anthropic's official guidance on CLAUDE.md structure, rules, skills, hooks, and agent configuration
- [Agents](https://www.anthropic.com/engineering/an-introduction-to-agents) -- Anthropic's introduction to the agentic paradigm and design principles
- [Agents Companion](https://google.github.io/adk-docs/agents/) -- Google's agent development patterns, tool design, and multi-agent coordination strategies

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*This guide is a living document. Contributions, corrections, and experience reports are welcome.*
