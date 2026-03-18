# Pre-Merge Checklist -- Before Merging Agent-Generated PRs

Agent-generated code is code. It deserves the same review rigor as human-written code, and in some cases more. Agents
produce plausible-looking output that can pass a casual review while hiding subtle issues: scope creep, hardcoded
values, mocked-away problems, and overly clever abstractions. This checklist is your last gate before code enters the
main branch.

---

- [ ] **CI passes (all lint, test, build jobs green)**
  Do not merge with failing CI, even if the failure "looks unrelated." Agents sometimes introduce transitive failures --
  a type change in one file that breaks a test in another. Green CI is the minimum bar, not a guarantee of quality.

- [ ] **Changes reviewed by a human (or agent reviewer + human spot-check)**
  Someone needs to read the diff. If you use an agent to do a first-pass review, the human still needs to spot-check:
  verify the reviewer's findings, look at the files with the most changes, and check any files that touch security,
  auth, or data persistence.

- [ ] **No scope creep (changes match the phase scope)**
  Agents sometimes add "bonus improvements" -- refactoring a file they touched, adding a feature that seemed related, or
  upgrading a dependency. These changes are well-intentioned but dangerous. They introduce untested surface area and
  make the diff harder to review. If the change was not in the phase scope, it should not be in the PR.

- [ ] **No security concerns**
  Check for: hardcoded secrets or API keys, SQL injection vulnerabilities (raw string interpolation in queries), exposed
  debug endpoints, overly permissive CORS settings, missing auth checks on protected routes, and credentials logged to
  stdout. Agents do not think about security unless you tell them to.

- [ ] **Integration smoke test passes**
  Run the integration test against the merged code. This catches cross-system failures that CI cannot: broken API
  proxies, auth cookie mismatches, ORM-to-schema drift, and misconfigured service dependencies. If you can only do one
  thing on this list beyond reading the diff, do this.

- [ ] **Agent state file reflects the completed work**
  The agent state file should list what was done, what tests were run, and what files were changed. If the state file is
  stale or missing, future agents (and future you) will have to reverse-engineer the work from the diff.

- [ ] **CLAUDE.md, rules, and skills updated if changes affect them**
  If the PR introduces a new convention, a new mandatory check, or changes the build process, the harness must be
  updated to reflect it. Otherwise the next agent session will operate under stale assumptions. The harness is a living
  document, not a one-time setup.

- [ ] **Documentation updated if behavior changed**
  If the PR changes how a feature works, how an API endpoint behaves, or how the system is configured, the relevant
  documentation should be updated in the same PR. Documentation that drifts from implementation is worse than no
  documentation -- it actively misleads.

- [ ] **For worktree agents: branch is up to date with main**
  If the PR was authored by an agent running in a worktree, verify the branch has been rebased onto the latest main.
  Worktree agents work in isolation and can fall behind. A clean rebase confirms there are no merge conflicts hiding in
  the diff.
