# Case Study: Integration Gate -- The Failures Unit Tests Missed

The production application had 434+ backend unit tests, 15+ sidecar tests, type-checking across the entire frontend, and build verification for all three container images. Every one of those checks passed. And the application was broken.

This happened four times across the project's 19 phases. Each time, the root cause was the same: agents mock system boundaries in their tests, and the mocks were correct while the real systems were not. The integration smoke test -- 16 checks run by the human after every agent phase -- was the only thing that caught these failures.

---

## The Smoke Test

The integration smoke test was a bash script that exercised the full running stack. It did not use mocks, test doubles, or simulated services. It started the real containers, hit real endpoints, and verified real responses. The 16 checks covered:

1. **Service health**: Backend returns 200 on `/health`, frontend returns 200 on `/`
2. **User registration**: POST to the auth endpoint creates a user and returns a session cookie
3. **Session propagation**: The session cookie from the frontend auth library is accepted by the backend API
4. **CRUD operations**: Create, read, update, and delete a resource through the full proxy chain (frontend -> API proxy -> backend -> database)
5. **Read-only endpoints**: Fetch paginated data from read-only endpoints
6. **Page loads**: Every major frontend page returns 200 (content discovery, user profiles, content management, account settings)

The script ran in under 30 seconds. It was required after every phase -- not optional, not "when convenient," not "if you think something might have broken." The requirement was written into CLAUDE.md and into each agent's instruction file.

## The Four Failures

### Failure 1: Auth Cookie Format Mismatch

**What broke**: Users could register and log in on the frontend, but every subsequent API call to the backend returned 401 Unauthorized.

**Root cause**: The frontend auth library stored session tokens in a specific cookie format: `token.hmac_signature`. The backend auth dependency expected to receive just the token portion. It was reading the full cookie value (including the signature) and looking it up in the database, where it did not exist.

**Why unit tests missed it**: The backend's auth unit tests created session tokens directly, without going through the frontend auth library. The tokens in the test database matched the tokens in the test requests. The cookie format was never part of the test.

**Why the smoke test caught it**: The smoke test registered a user through the frontend auth endpoint, captured the real cookie, and then used that cookie to hit a backend endpoint. The 401 was immediately visible.

**Fix**: The backend auth dependency was updated to split the cookie value on `.` and use only the token portion for database lookup. A one-line fix that was invisible to unit tests.

### Failure 2: ORM Model / Database Schema Mismatch

**What broke**: The backend started, passed all tests, and then returned 500 errors on any endpoint that touched a specific database table.

**Root cause**: A database migration had been fixed during a previous phase -- a column type was changed, a constraint was added. The migration was correct and applied cleanly. But the SQLAlchemy ORM model for that table still reflected the old schema. The ORM tried to query columns that no longer existed in the form it expected.

**Why unit tests missed it**: The backend tests used mock database sessions. The ORM models were never actually executed against a real PostgreSQL instance during the test run. The mocks returned whatever the test told them to return.

**Why the smoke test caught it**: The smoke test ran a CRUD operation against the real database. The SQLAlchemy query failed with a column mismatch error that appeared in the container logs.

**Fix**: The ORM models were updated to match the actual database schema. The lesson was encoded into CLAUDE.md: "SQLAlchemy models must match actual Postgres schema -- migration fixes don't auto-update models."

### Failure 3: Missing API Proxy

**What broke**: The frontend loaded, displayed pages, but every data fetch returned a 404 or CORS error.

**Root cause**: The frontend's API client called `/api/*` endpoints, expecting them to be proxied to the backend service. But no proxy was configured. The frontend's Next.js server received the `/api/*` requests and, having no matching route, returned 404. In development with the mock server, this was not an issue because the mock server ran on the same origin.

**Why unit tests missed it**: The frontend's data fetching tests used the Prism mock server, which ran at a known URL and did not require a proxy. The tests never exercised the Next.js server's routing behavior.

**Why the smoke test caught it**: The smoke test made API calls through the frontend's origin, the same way a real browser would. The 404 responses were immediately visible.

**Fix**: A `rewrites` configuration was added to `next.config.ts` to proxy `/api/*` requests (except auth routes) to the backend via the `BACKEND_URL` environment variable. Another small fix that was completely outside the scope of any unit test.

### Failure 4: Sidecar Dockerfile Configuration Error

**What broke**: The sidecar service (a knowledge graph integration layer) failed to build its Docker image. The service worked fine in local development (running directly via Python) and all its unit tests passed.

**Root cause**: The Dockerfile for the sidecar specified an incorrect build-backend configuration for the Python packaging tool. The package would not install inside the container.

**Why unit tests missed it**: The sidecar's tests ran directly in a Python environment, not inside a container. The Docker build was never part of the test pipeline at that phase.

**Why the smoke test caught it**: The smoke test required all services to be running via Docker Compose. The sidecar container failed to start, and the health check for that service failed.

**Fix**: The Dockerfile was corrected. The build-backend value was changed to the correct one for the packaging tool in use.

## The Pattern

All four failures share a common structure:

1. Two systems interact across a boundary (frontend/backend, ORM/database, code/container)
2. Each system is tested in isolation with mocks or stand-ins for the other
3. The mocks are correct -- they match what the developer *intended* the other system to do
4. The real system does something slightly different from what the mocks assume
5. Unit tests pass on both sides. The integration is broken.

This is not a failure of testing discipline. It is a structural limitation of isolated tests. Mocks are a developer's model of an external system. They are always a simplification, and the simplification always omits something. The integration smoke test does not use models. It uses the real systems. That is why it catches what unit tests cannot.

## The Key Lesson

The integration gate added roughly 2 minutes of human time per phase. Across 19 phases, that is about 40 minutes total. The four failures it caught would have taken hours each to diagnose if they had been discovered in a later phase, after other code had been built on top of the broken integration.

The math is unambiguous: run the integration test after every phase. Make it mandatory. Write it into CLAUDE.md. Do not let agents mark phases complete until the human has run it.

Agents are excellent at testing their own code in isolation. They are structurally incapable of testing integration, because integration requires running the real systems they only have mocks for. The human fills this gap. It is one of the human's most important roles in harness engineering.
