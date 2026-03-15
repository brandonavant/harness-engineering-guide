# Phase Completion Checklist -- Before Marking a Phase Done

Use this checklist at the end of every implementation phase, before you declare it complete and move on. The cost of discovering a broken phase increases dramatically with each subsequent phase built on top of it. These checks take minutes. Fixing a missed integration failure three phases later takes hours.

---

- [ ] **All tasks for the phase are implemented**
  Review the phase scope against what was actually built. Compare the agent state file or task list to the delivered code. Partial implementations that "mostly work" become hidden debt in the next phase.

- [ ] **Tests pass (run the full test suite, not just new tests)**
  Run every test, not just the ones the agent wrote for this phase. Regressions in earlier code are common when agents modify shared utilities, database models, or configuration files. A green test suite for only the new code proves nothing about the system as a whole.

- [ ] **All mandatory skills invoked and passed**
  If your project has mandatory skills (design enforcement, API contract validation, accessibility checks), verify they were actually invoked during this phase. Agents sometimes skip skills when context is crowded. Check the session output or skill logs.

- [ ] **Agent state file updated**
  The agent should have updated its state file with: completed tasks (as a checklist), test results summary, files created or modified, and any deviations from the plan. If the state file is stale, future agents and future you will not know what was done.

- [ ] **Docker build succeeds (if applicable)**
  If your project uses containers, build all images from scratch. Do not rely on cached layers. A successful Docker build confirms that dependencies resolve, the application compiles, and the image is self-contained. Build failures caught here are trivial to fix; build failures caught in CI waste pipeline minutes and block the team.

- [ ] **Migrations apply cleanly to a fresh database**
  Drop your development database and run all migrations from zero. This catches migration ordering issues, missing dependencies between migrations, and schema assumptions that only work on an already-populated database. If you cannot get from empty to current in one pass, your migrations are broken.

- [ ] **Runtime smoke test passes (service starts, health check returns 200)**
  Start each service and hit its health endpoint. This verifies that the application boots, connects to its dependencies, and responds to requests. A passing test suite does not guarantee this -- tests often mock the very infrastructure that a health check validates.

- [ ] **Integration smoke test passes (human runs the script)**
  If you have an integration smoke test script, run it now. This is the human's responsibility, not the agent's. The script should exercise cross-system boundaries: frontend-to-backend API calls, auth cookie propagation, database CRUD through the full stack. Agents test in isolation. This test does not.

- [ ] **PR opened with descriptive title and summary**
  The agent should open a pull request, not merge directly. The PR title should describe what was built. The summary should list what changed and how to verify it. This gives you a review checkpoint and an audit trail.

- [ ] **No hardcoded secrets, API keys, or credentials in committed files**
  Search the diff for anything that looks like a secret: API keys, connection strings, passwords, tokens. Agents occasionally hardcode values they found in environment variables or configuration files. A single committed secret requires key rotation, which is always more expensive than catching it in review.

- [ ] **No TODO/FIXME items left unresolved**
  Search the codebase for TODO and FIXME comments. If they exist, they should either be resolved in this phase or explicitly documented in the agent state file as deferred work with a clear rationale. Undocumented TODOs become invisible tech debt.
