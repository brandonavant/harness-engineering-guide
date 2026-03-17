# Case Study: Integration Gate — The Failures Unit Tests Missed

> **Work in progress.** This case study will be populated after the guide's techniques are validated on a real
> production application.

## What This Will Cover

- Specific cross-system integration failures that passed unit tests but broke the running application
- Why agents mock system boundaries in tests, and why those mocks diverge from real behavior
- The integration smoke test structure and why it must be mandatory after every agent phase
