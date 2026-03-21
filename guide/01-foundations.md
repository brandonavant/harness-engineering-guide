# Chapter 01 -- Foundations: The Harness Engineering Paradigm

> Part 1: Understand

**Entry point**: You are considering agentic coding, or you have tried it and gotten inconsistent results.
**Exit point**: You understand the mental model, the human's role, the agent's constraints, and the feedback loop that makes it all work.

---

## 1.1 What Is Harness Engineering?

Harness engineering is the discipline of designing environments that make AI agents productive. The term comes from a simple analogy: you do not teach a horse to drive itself by explaining traffic laws. You build a harness -- reins, blinders, traces -- that channels the horse's power in the direction you choose. The horse is strong. Your job is steering.

In Claude Code, the harness consists of:

- **CLAUDE.md** -- The root configuration file that tells the agent what the project is, how to build it, and what rules to follow
- **Rules** (`.claude/rules/`) -- Scoped instructions that activate when Claude reads files matching their path patterns
- **Skills** (`.claude/skills/`) -- Reusable instruction sets the agent can invoke for specific tasks
- **Hooks** -- Scripts that run automatically on tool events (linting after file edits, blocking secret writes)
- **Design documents** (`docs/`) -- PRD, architecture, UX spec, API contracts, brand identity
- **Contracts** (`contracts/`) -- Formal interface definitions (OpenAPI YAML) that serve as the source of truth between system boundaries

None of these are code. All of them determine the quality of the code the agent produces.

The shift is this: in traditional development, your primary output is source code. In harness engineering, your primary output is the environment. The agent writes the source code. You write everything that tells the agent what to write, how to verify it, and when it has gone wrong.

This is not a minor workflow adjustment. It changes what you spend your time on, what skills matter most, and how you think about quality.

### What This Looks Like in Practice

A traditional developer working on an API endpoint might spend their time writing the route handler, the database query, the validation logic, and the tests. In harness engineering, the same work looks like this:

1. The human ensures the OpenAPI contract defines the endpoint's request/response schema
2. The human ensures the architecture doc specifies which database table backs the resource
3. The human tells the agent: "Implement the `POST /campaigns` endpoint per the OpenAPI contract"
4. The agent reads the contract, reads the architecture doc, writes the route handler, the SQLAlchemy model interactions, the Pydantic schemas, and the tests
5. The human reviews the output, runs integration tests, and feeds corrections back into the harness

The human never wrote a line of application code. But the human made every decision that determined what that code would look like.

## 1.2 The Human Engineer's New Role

If you are used to writing code all day, this transition can feel disorienting. You may feel like you are not doing "real work." That feeling is wrong. The work has shifted, not diminished.

Your new responsibilities:

### Environment Designer

You design the harness. This means writing CLAUDE.md files that are precise enough to prevent mistakes but concise enough to fit in context. It means creating rules that activate at the right time. It means building skills that encode your team's best practices. Every hour you spend on the environment saves the agent (and you) many hours of corrections.

### Taste Arbiter

The agent can produce code that works but is not what you want. Maybe it chose the wrong abstraction. Maybe the UI looks generic. Maybe the error handling is too verbose. Your taste -- your sense of what "good" looks like for this project -- is something the agent cannot develop on its own. You express taste through specs, through brand documents, through review feedback that gets encoded back into rules.

### Integration Verifier

Agents test their own code, but they test it in isolation. They mock system boundaries. A frontend agent's tests pass even when the real backend API has changed. A backend agent's tests pass even when the database schema has drifted. The human is responsible for integration: running the full stack, executing smoke tests, verifying that the pieces fit together. This is not optional. It is the single most common source of failures in agentic development.

### Strategic Decision Maker

The agent implements decisions. It does not make them. Technology choices, architectural patterns, data modeling, deployment topology, cost tradeoffs -- these are human decisions. The agent can present options if asked, but the human decides. When you delegate a decision to the agent by being vague in your specs, you get whatever the agent's training data suggests is most common. That is rarely what you want.

### Feedback Loop Closer

When something goes wrong, the instinct is to fix the code. Resist this. The correct response is always: "What was missing from the environment that caused this mistake?" Then feed the fix back:

- A one-off mistake? Add a rule to `.claude/rules/`.
- A recurring pattern? Update CLAUDE.md.
- A complex procedure the agent keeps getting wrong? Build a skill.
- Something that should never pass review? Add a hook.

Corrections applied to the environment compound. A correction applied directly to the code fixes one instance and teaches nothing.

## 1.3 Context Is Your Scarcest Resource

Every token in the agent's context window competes for attention. The context window is large (200K+ tokens with Claude), but it is not infinite, and more is not always better. Research on large language models consistently shows that performance degrades when context is cluttered with irrelevant information. The agent is more likely to follow an instruction in a focused 100-line CLAUDE.md than a sprawling 500-line one.

This has practical implications for everything in this guide:

### Context Hierarchy

Not all context is equal. There is a rough priority order:

1. **CLAUDE.md** -- Always loaded. Keep it lean.
2. **Active rules** -- Loaded when file patterns match. Use scoping to avoid loading rules that do not apply.
3. **Conversation history** -- Grows with every turn. Long conversations accumulate stale context.
4. **Files read into context** -- The agent reads files as needed. Large files consume significant context.
5. **Tool outputs** -- Search results, build output, test results all consume context.

### Context Rot

Over a long conversation, the agent accumulates context from earlier turns that may no longer be relevant or may even contradict current state. A file the agent read 30 turns ago may have been modified since. A decision discussed early in the conversation may have been revised. The agent does not automatically know this.

Practical mitigations:
- Start fresh conversations for new tasks rather than continuing stale ones
- Keep CLAUDE.md as the single source of truth, not conversation history
- When a long conversation starts producing inconsistent results, that is your signal to start a new one
- Use auto memory (`~/.claude/projects/<project>/memory/`) for facts that must persist across conversations

### Context as Cost

Context is not free. Input tokens have a cost. On Claude, prompt caching can reduce repeat-context costs by up to 90%, but only if you structure your inputs to be cache-friendly (static content first, dynamic content last). The way you organize your harness directly affects your API bill.

We will cover specific cost-management techniques in later chapters, but the principle starts here: every line in CLAUDE.md, every rule, every skill should earn its place. If removing a line would not cause the agent to make mistakes, remove it.

## 1.4 Cost Reality Check

The public discourse around agentic coding is dominated by case studies from large companies with effectively unlimited API budgets. OpenAI's report on building a million-line codebase with Codex is impressive, but it was produced by an organization with free access to its own models and a team of researchers tuning the process.

This guide is written for a different audience: individuals and small teams who pay per token and need to ship a product without burning through thousands of dollars in API costs.

Cost-conscious principles threaded throughout this guide:

### Model Selection by Task

Not every task needs the most capable (and most expensive) model. A useful heuristic:

| Task | Recommended Model Tier | Rationale |
|------|----------------------|-----------|
| Specification writing, architecture decisions | Highest capability (e.g., Opus) | These documents steer everything downstream. Precision matters. |
| Implementation, feature building | High capability (e.g., Sonnet) | The bulk of the work. Good enough for code generation with proper harness. |
| Linting, formatting, simple refactors | Lower capability (e.g., Haiku) | Mechanical tasks that do not require deep reasoning. |
| Code review, test generation | High capability (e.g., Sonnet) | Needs to understand intent, not just syntax. |

### Prompt Caching

If your tech stack uses the Anthropic API directly (as opposed to only through Claude Code), prompt caching is one of the most impactful cost optimizations available. The key insight: cached input tokens cost roughly 10% of uncached tokens. This means structuring your system prompts and message history so that the prefix remains stable across turns can reduce costs dramatically.

The harness design principles in this guide -- static CLAUDE.md, stable document structure, deterministic message ordering -- are all cache-friendly by design.

### Context Management as Cost Management

A 200K-token context window filled with irrelevant content is not just less effective -- it is more expensive. Every unnecessary file read, every bloated rule, every unfocused CLAUDE.md line costs money. The discipline of keeping context lean is simultaneously a quality practice and a cost practice.

### Conversation Discipline

Long conversations accumulate context and cost. A conversation that runs for 100 turns with a growing context window costs significantly more per turn at the end than at the beginning. Starting fresh conversations for new tasks is not just good for quality -- it is good for your budget.

## 1.5 The Feedback Loop

This is the most important concept in the guide. Everything else is implementation detail.

When Claude makes a mistake, you have two options:

**Option A: Fix the code yourself.**
This is fast. It solves the immediate problem. It teaches Claude nothing. The same mistake will happen again in the next conversation, or the next phase, or when a different agent touches the same area.

**Option B: Fix the environment.**
This is slower. You have to diagnose what was missing -- was it a rule? A clarification in the spec? A missing example in CLAUDE.md? Then you update the harness, and the fix persists. Every future agent session benefits from the correction.

Option B always wins over time. The cost of fixing the environment once is paid back every time the agent does not repeat the mistake.

### The Feedback Ladder

Fixes have different scopes and different persistence levels. Choose the right rung:

| Scope | Mechanism | Persistence | When to Use |
|-------|-----------|-------------|-------------|
| This conversation only | Tell the agent directly | Dies when conversation ends | Truly one-off corrections |
| This file pattern | `.claude/rules/` with `paths` frontmatter | Persists across conversations | Pattern-specific guidance (e.g., "all migration files must...") |
| This project | CLAUDE.md | Persists across conversations | Project-wide rules and constraints |
| This task type | `.claude/skills/` | Invoked on demand | Complex multi-step procedures |
| This action | Hooks (PreToolUse, PostToolUse, etc.) | Runs automatically | Hard constraints that must never be violated |
| This knowledge | Memory files | Persists across conversations | Facts, decisions, lessons learned |

### Concrete Example

You ask Claude to build a REST endpoint. It works, but it returns `camelCase` field names instead of the `snake_case` your API contract specifies.

**Weak fix**: Tell Claude "use snake_case" in this conversation. It will comply now and forget later.

**Strong fix**: Add to CLAUDE.md:
```
All API response fields use snake_case naming. This is enforced by the OpenAPI contract in contracts/openapi.yaml.
```

**Strongest fix**: Add a `PostToolUse` hook on `Edit|Write` that runs contract validation, so snake_case violations are caught automatically after every file edit.

Each rung of the ladder makes the fix more durable. Over the course of a project, dozens of these accumulated fixes transform a bare harness into a finely tuned one that produces correct output on the first try.

## 1.6 Prerequisites

To follow this guide, you need:

- **Claude Code CLI** installed and authenticated. See [Anthropic's setup guide](https://docs.anthropic.com/en/docs/claude-code/getting-started).
- **A terminal** you are comfortable working in. Claude Code is a CLI tool; there is no GUI.
- **Git** installed and configured. Every step in this guide assumes version control.
- **A project idea**, even a rough one. It does not need to be fully formed. The interview process in Chapter 02 will refine it.
- **Basic familiarity** with at least one modern tech stack (a web framework, a database, a frontend library). You do not need to be an expert, but you need enough knowledge to evaluate the agent's output and make architectural decisions.

You do not need:
- Prior experience with AI coding tools
- A specific programming language or framework preference
- A detailed project plan

The guide will walk you through everything else.

## 1.7 Guide Conventions

Throughout this guide, each chapter contains:

- **Principles** -- The reasoning behind the recommendations. Skip these if you just want the steps, but read them if you want to understand why.
- **Human section** -- What the human engineer decides, provides, or reviews. Marked with context about what you are producing and why.
- **Agent section** -- What the agent produces, builds, or verifies. Written so that an agent reading the guide can understand its role and constraints.
- **Template references** -- Pointers to starter files in the `templates/` directory that you can copy into your project.
- **Common mistakes** -- Failure modes we have seen repeatedly. These are the potholes on the road.

---

## What the Agent Should Take Away

If you are an AI agent reading this chapter as part of your operating context, here is what matters:

1. **Your environment is your instruction set.** CLAUDE.md, rules, skills, and design documents are not suggestions -- they are your operating parameters. Read them thoroughly before starting work. If they conflict, flag the conflict to the human rather than guessing which takes priority.

2. **Ask for missing context.** If you need information that is not in your context -- a design decision that was not documented, a constraint that is ambiguous, a spec that is incomplete -- ask. Guessing is cheaper in the moment and more expensive in total. A question takes one turn. A wrong guess takes many turns to diagnose and fix.

3. **Your tests are necessary but not sufficient.** You test your code in isolation. You mock external dependencies. Your tests passing does not mean the system works. The human runs integration tests for a reason. Do not treat passing unit tests as proof of correctness.

4. **Corrections are feedback, not criticism.** When the human says your output is wrong and updates the harness, that update benefits every future agent session. Your job is to read the updated harness carefully and adjust. The feedback loop works only if you actually incorporate the feedback.

5. **Stay in your territory.** If the harness defines boundaries (e.g., "backend agent owns `apps/backend/`, frontend agent owns `apps/frontend/`"), respect them. Do not modify files outside your scope, even if you think you see a bug. Flag it to the human.

6. **Context efficiency is your responsibility too.** Do not read files you do not need. Do not include unnecessary detail in your outputs. Do not ask the human to re-explain something that is documented. Every token you waste makes the remaining context less effective.

---

Next: [Chapter 02 -- Project Bootstrap: From Idea to First Agent Run](02-project-bootstrap.md)
