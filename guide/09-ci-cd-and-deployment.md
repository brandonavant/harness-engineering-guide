# Chapter 09 -- CI/CD and Deployment: Pipelines for Agent-Generated Code

> **Part 4: BUILD** | Templates: `templates/.github/workflows/ci.yml`

Agent-generated code needs the same CI rigor as human-written code. Arguably more. When a human writes code, they carry
context about what they changed and why. When an agent writes code, that context exists only in the session — and the
session ends. CI is the persistent verification layer that catches what vanishes with the context window.

This chapter covers the CI/CD pipeline design, release automation, deployment patterns, and the boundary between what
the agent writes and what the human executes.

---

## Principles

**CI is the safety net, not the agent.** Agents produce plausible code that compiles and often works. But "often" is
not "always." Lint, test, and build on every PR. No exceptions.

**Pin your tools.** Agents use the latest version of everything. CI needs reproducibility. A linter that adds new rules
in a patch release will break your build on code that passed yesterday. Pin versions explicitly.

**The agent writes the config; the human provides the secrets.** CI/CD configuration is code and lives in the repo.
Secrets (API keys, registry tokens, deploy credentials) never touch the repo. The agent defines what secrets are needed.
The human provisions them.

**Deployment is not the agent's job.** The agent can write deployment scripts, Dockerfiles, and compose files. But the
agent should not execute deployments, apply infrastructure, or access production systems. The human reviews and runs.

---

## 9.1 CI for Agent-Generated Code

Every pull request triggers the CI pipeline. The pipeline must answer three questions:

1. Is the code well-formed? (lint)
2. Does it work correctly? (test)
3. Can it be shipped? (build)

### Pipeline structure

Separate these into distinct jobs. Lint runs first because it is fast and catches obvious issues before burning test
compute.

```yaml
# .github/workflows/ci.yml
name: CI

on:
  pull_request:
    branches: [ main ]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Backend lint
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: pip install ruff==0.11.13
      - run: ruff check apps/backend/
      - run: ruff format --check apps/backend/

      # Frontend lint
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: cd apps/frontend && npm ci
      - run: cd apps/frontend && npx tsc --noEmit

  test-backend:
    needs: lint
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:16
        env:
          POSTGRES_USER: test
          POSTGRES_PASSWORD: test
          POSTGRES_DB: test
        ports: [ "5432:5432" ]
        options: >-
          --health-cmd="pg_isready"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=5
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.12"
      - run: cd apps/backend && pip install -e ".[test]"
      - run: cd apps/backend && pytest --tb=short -q
        env:
          DATABASE_URL: postgresql://test:test@localhost:5432/test

  test-frontend:
    needs: lint
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: "22"
      - run: cd apps/frontend && npm ci
      - run: cd apps/frontend && npm test

  build:
    needs: [ test-backend, test-frontend ]
    runs-on: ubuntu-latest
    strategy:
      matrix:
        service: [ backend, frontend ]
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - run: docker build -f apps/${{ matrix.service }}/Dockerfile .
```

### Key decisions in this pipeline

**Pin tool versions.** The `ruff==0.11.13` pin is not arbitrary. We discovered that newer ruff versions added rules that
flagged existing code. Without the pin, CI would break on unchanged code because the linter moved under us. Pin every
tool that has opinions about your code.

**Test jobs run in parallel.** Backend and frontend tests are independent. Running them in parallel cuts pipeline time
roughly in half. They both depend on lint passing first.

**Build uses Docker.** Even if you deploy differently, building Docker images in CI verifies that the Dockerfile,
dependencies, and build steps all work. A Dockerfile that builds locally but fails in CI is a common agent mistake —
usually caused by missing system dependencies or incorrect COPY paths.

**Services for integration.** Backend tests need a real Postgres instance, not SQLite. The CI pipeline provides this via
service containers. This catches SQL-dialect differences that mocks hide.

---

## 9.2 Handling CI Failures from Agent Code

Agent-generated code fails CI for predictable reasons. Knowing the patterns helps you fix them quickly.

**Import ordering and formatting.** The agent writes code that works but may not match your linter's expectations. Fix
this with pre-commit hooks (Chapter 6) so formatting issues never reach CI.

**Missing dependencies.** The agent uses a library in code but does not add it to `requirements.txt` or `package.json`.
The fix: include dependency management in your CLAUDE.md or subagent definitions. "When you import a new package, add it
to the dependency file."

**Type errors in TypeScript.** The agent produces code that runs but does not type-check. This is especially common with
complex generics, union types, and third-party library types. Running `tsc --noEmit` in CI catches this. The agent
should run the same check locally before opening a PR.

**Flaky tests.** Tests that pass locally but fail in CI, or vice versa. Usually caused by timing dependencies, file
system assumptions, or port conflicts. Investigate immediately. Do not add retry logic to mask them.

**Docker build failures.** Common causes: multi-stage build referencing a stage that was renamed, COPY path that assumes
a different working directory, or a RUN command that requires a build argument not provided in CI. The agent should
verify Docker builds before opening a PR.

---

## 9.3 The Release Pipeline

When a PR merges to main, the release pipeline builds production artifacts. This is a separate workflow from CI.

```yaml
# .github/workflows/release.yml
name: Release

on:
  push:
    branches: [ main ]

permissions:
  contents: write
  packages: write

jobs:
  release:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      # Version from file + build number
      - name: Set version
        id: version
        run: |
          BASE=$(cat VERSION)
          echo "version=${BASE}.${GITHUB_RUN_NUMBER}" >> "$GITHUB_OUTPUT"

      # Build and push container images
      - uses: docker/login-action@v3
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/setup-buildx-action@v3
      - uses: docker/setup-qemu-action@v3  # For ARM64 cross-compilation

      - name: Build and push backend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: apps/backend/Dockerfile
          push: true
          platforms: linux/arm64  # Target platform
          tags: |
            ghcr.io/${{ github.repository }}/backend:latest
            ghcr.io/${{ github.repository }}/backend:${{ steps.version.outputs.version }}

      - name: Build and push frontend
        uses: docker/build-push-action@v5
        with:
          context: .
          file: apps/frontend/Dockerfile
          push: true
          platforms: linux/arm64
          tags: |
            ghcr.io/${{ github.repository }}/frontend:latest
            ghcr.io/${{ github.repository }}/frontend:${{ steps.version.outputs.version }}

      # Tag the commit
      - name: Create git tag
        run: |
          git tag "v${{ steps.version.outputs.version }}"
          git push origin "v${{ steps.version.outputs.version }}"
```

### Versioning strategy

Keep a `VERSION` file in the repo root with a semver base:

```
0.1.0-alpha
```

The release pipeline appends the build number: `0.1.0-alpha.42`. This gives you monotonically increasing versions tied
to specific commits without requiring manual version bumps.

The agent can update the `VERSION` file when you reach a milestone (alpha to beta, beta to stable), but the build number
is always automatic.

### Platform considerations

If your deployment target differs from your CI runner (e.g., deploying to ARM64 hardware from an x86 CI runner), you
need cross-compilation. QEMU handles this but is slow — expect 15-20 minutes for a Next.js build under emulation. This
is a known cost. Consider native ARM runners if build time becomes a bottleneck.

---

## 9.4 Deployment Patterns

### Docker Compose for simple deployments

For single-server deployments, Docker Compose is sufficient and straightforward. The production compose file references
container images from the registry rather than building locally:

```yaml
# docker-compose.prod.yml
services:
  backend:
    image: ghcr.io/yourorg/yourapp/backend:latest
    restart: unless-stopped
    env_file: .env.production
    ports:
      - "8000:8000"
    depends_on:
      postgres:
        condition: service_healthy

  frontend:
    image: ghcr.io/yourorg/yourapp/frontend:latest
    restart: unless-stopped
    env_file: .env.production
    ports:
      - "3000:3000"

  postgres:
    image: postgres:16
    restart: unless-stopped
    volumes:
      - pgdata:/var/lib/postgresql/data
    env_file: .env.production
    healthcheck:
      test: [ "CMD", "pg_isready" ]
      interval: 10s
      timeout: 5s
      retries: 5

volumes:
  pgdata:
```

### Continuous deployment with Watchtower

Watchtower monitors your running containers and automatically pulls new images when they appear in the registry.
Combined with the release pipeline, this gives you continuous deployment: merge to main, images build, Watchtower pulls,
containers restart.

```yaml
  watchtower:
    image: containrrr/watchtower
    restart: unless-stopped
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock
    environment:
      - WATCHTOWER_POLL_INTERVAL=300  # Check every 5 minutes
      - WATCHTOWER_CLEANUP=true       # Remove old images
```

This is a pragmatic choice for small deployments. For larger systems, use a proper orchestrator with health-checked
rolling deployments.

### Health checks

Every service should expose a health endpoint. The backend returns its version so you can verify which code is running:

```json
GET /health
{
  "status": "ok",
  "version": "0.1.0-alpha.42"
}
```

The frontend can display the version on an account or settings page. This is invaluable for debugging: "is the
deployment actually running the code I just merged?"

---

## 9.5 The Production Smoke Test

After every deployment, verify the stack works end-to-end. This is the production equivalent of the integration gate.

### What to verify

1. **Backend health**: the health endpoint returns 200 with the expected version
2. **Frontend loads**: the root page returns 200
3. **Auth works**: register a user, log in, verify session
4. **Core CRUD works**: create and read the primary entities
5. **AI integration works** (if applicable): send a message, verify the response streams back

### The golden rule

**Never make manual changes to production to work around issues.** No direct SQL edits. No manual file changes on the
server. No "just restart the container." If something is broken, fix it in the codebase, push to main, and let the
pipeline rebuild and redeploy.

This rule exists because manual changes create invisible state drift. The next deployment will overwrite your manual
fix, the bug will reappear, and no one will remember what the manual fix was.

### What the Human Should Do

SSH into the production server (or use your monitoring tools) after each deployment and run the production smoke test.
Automate this if you can, but manual verification is acceptable for small deployments. If any check fails, investigate
immediately — do not wait for users to report it.

### What the Agent Should Do

When writing the production compose file, include health checks for every service. When writing the deployment
documentation, include the production smoke test procedure. When modifying an endpoint that the smoke test covers,
verify the smoke test still passes.

---

## 9.6 Secrets Management

Secrets (API keys, database passwords, registry tokens) require careful handling in an agent workflow.

### Ground rules

- **Never commit secrets.** Not in code, not in config files, not in comments, not in test fixtures.
- **Use environment variables.** Services read secrets from env vars. Local dev uses `.env` files (gitignored). CI uses
  GitHub Actions secrets. Production uses `.env.production` files on the server (not in the repo).
- **Agent instructions specify variable names, not values.** The agent should know that `ANTHROPIC_API_KEY` is needed.
  The agent should never know the actual key.

### CI secrets

GitHub Actions secrets are set in the repository settings and referenced in workflows:

```yaml
env:
  ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
```

For container registry authentication, GitHub provides `GITHUB_TOKEN` automatically for GHCR. For other registries,
store credentials as repository secrets.

### Production secrets

For simple deployments, a `.env.production` file on the server:

```bash
# .env.production — on the server, NOT in the repo
DATABASE_URL=postgresql://user:pass@localhost:5432/myapp
ANTHROPIC_API_KEY=sk-ant-...
SESSION_SECRET=...
```

For more sophisticated setups, use a secrets manager (Vault, AWS Secrets Manager, Azure Key Vault). The choice depends
on your infrastructure.

### What the Human Should Do

Provision secrets. Rotate them periodically. Review any agent-generated code that handles secrets to ensure they are
read from environment variables, never hardcoded.

### What the Agent Should Do

When you need a new secret, document it: what the variable is called, what service provides it, and where it is used.
Never include placeholder values that look like real secrets (`sk-ant-abc123`). Use obviously fake values (
`your-api-key-here`) or empty strings.

---

## 9.7 The Agent's Role in CI/CD

The boundary is simple:

| Task                               | Who   |
|------------------------------------|-------|
| Write CI workflow YAML             | Agent |
| Write Dockerfiles                  | Agent |
| Write compose files (dev and prod) | Agent |
| Write deployment scripts           | Agent |
| Write health check endpoints       | Agent |
| Write smoke test scripts           | Agent |
| Provide secrets                    | Human |
| Review CI/CD config                | Human |
| Run infrastructure provisioning    | Human |
| Execute production deployments     | Human |
| Verify production health           | Human |

The agent produces all the configuration. The human reviews it, provides credentials, and executes anything that touches
production or infrastructure. This is not a trust issue — it is a safety boundary. An agent that can deploy can also
take down production.

### When the agent modifies CI/CD

Treat CI/CD changes with the same rigor as code changes. A broken CI pipeline blocks the entire team. When the agent
modifies a workflow:

1. Review the diff carefully — GitHub Actions YAML is sensitive to indentation and syntax
2. Check that pinned versions were not accidentally changed
3. Verify secrets are referenced correctly (typos in secret names fail silently)
4. If possible, test the workflow on a branch before merging to main

### Iterating on CI/CD

Expect to iterate. The first CI pipeline the agent produces will probably work for the happy path but miss edge cases:
caching, parallel jobs, service container configuration, platform-specific issues. Each failure teaches you something.
Encode the fix in a rule or the workflow itself, and move on.

---

Next: [Chapter 10 -- Entropy Management: Fighting Drift in Agent-Generated Code](10-entropy-management.md)
