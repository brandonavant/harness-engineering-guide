# Project Kickoff Checklist -- Before the First Agent Run

Use this checklist before you give Claude Code its first real task on a new project. Every item here prevents a class of early mistakes that are expensive to fix later. Skipping items does not save time -- it shifts the cost to debugging sessions that could have been avoided.

---

- [ ] **Claude Code CLI installed and working**
  Run `claude --version` and confirm output. If you cannot run the CLI, nothing else matters. Verify your authentication is configured and you can reach the model.

- [ ] **Git repo initialized with main branch**
  The agent needs version control from the first commit. It uses `git diff` and `git log` to understand what has changed. An uninitialized repo means the agent has no history to reason about and you have no safety net for rollbacks.

- [ ] **CLAUDE.md written (under 200 lines)**
  This is the agent's entry point. It should include: what the project is (2-3 sentences), the tech stack (decided, not debated), build/run commands, and pointers to deeper docs. Keep it under 200 lines. Everything that can live in a rule, skill, or doc should live there instead. The goal is a table of contents, not an encyclopedia.

- [ ] **docs/ directory created with at least one design document**
  The agent needs somewhere to look for requirements, architecture decisions, and specifications. Even a single document with your initial requirements is enough. The key is that the agent knows where to find project context beyond CLAUDE.md.

- [ ] **.claude/ directory structure in place**
  Create `.claude/rules/`, `.claude/skills/`, and configure any hooks you need. Even if these directories are empty at kickoff, their existence signals to the agent (and to you) that this is where scoped instructions will live. You will populate them as patterns emerge.

- [ ] **Tech stack decided**
  Agents implement decisions. They do not make them well. If you leave the tech stack open ("choose a good database"), the agent will pick whatever its training data suggests is most common. Decide on your framework, language, database, auth approach, and deployment target before the first agent run. Write these decisions into CLAUDE.md.

- [ ] **Initial requirements conversation completed**
  Before the agent writes code, you should have a clear picture of what you are building. This can be a formal PRD, an interview transcript, or a bullet list of features. The format matters less than the completeness. The agent needs a target to aim at.

- [ ] **First test run: Claude can read CLAUDE.md and scaffold a hello-world**
  Give the agent a trivial task: "Read CLAUDE.md and scaffold a minimal hello-world for this project." This verifies that the CLI works, the agent can read your files, and your CLAUDE.md is parseable. If this fails, fix the environment before attempting real work.

- [ ] **Initial commit pushed**
  Commit everything -- CLAUDE.md, docs, directory structure, any scaffolding from the test run. This gives you a clean baseline to diff against and ensures the agent starts from a known state. Every subsequent agent session will have this commit as its foundation.
