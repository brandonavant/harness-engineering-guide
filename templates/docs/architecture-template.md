# Beacon -- Architecture Document

<!-- WHY THIS DOCUMENT EXISTS:
This is the technical blueprint. It records DECIDED choices, not debated options. Every
technology, pattern, and constraint listed here is final. Agents implement against this
document -- they do not propose alternatives or "improve" the stack.

[CUSTOMIZE] Replace all Beacon-specific content. Keep the structure and the level of
specificity. Vague architecture produces vague implementations. -->

## Document Header

| Field          | Value           |
|----------------|-----------------|
| Version        | v1.0            |
| Date           | 2025-01-15      |
| Author         | [CUSTOMIZE]     |
| Change Summary | Initial version |

---

## 1. Tech Stack Summary

<!-- WHY: A table of decided choices prevents agents from re-opening settled debates.
Every row is a constraint, not a suggestion. [CUSTOMIZE] Replace with your actual stack. -->

| Layer             | Technology     | Version | Notes                                             |
|-------------------|----------------|---------|---------------------------------------------------|
| Frontend          | Next.js        | 15.x    | App router, server components                     |
| Frontend language | TypeScript     | 5.x     | Strict mode enabled                               |
| Styling           | Tailwind CSS   | v4.x    | Design tokens in tokens.css                       |
| Component library | shadcn/ui      | Latest  | Customized to brand identity                      |
| State management  | TanStack Query | v5      | Server state only; local state via React useState |
| Backend           | FastAPI        | 0.115+  | Async endpoints                                   |
| Backend language  | Python         | 3.12+   | Modern syntax                                     |
| ORM               | SQLAlchemy     | 2.0+    | Async sessions, declarative models                |
| Migrations        | Alembic        | Latest  | Auto-generate, manual review                      |
| Database          | PostgreSQL     | 16      | Primary data store                                |
| Auth              | Better Auth    | 1.x     | Session cookies, email/password                   |
| Containerization  | Docker         | Latest  | docker-compose for local dev                      |
| CI/CD             | GitHub Actions | N/A     | Lint, test, build on PR; release on merge to main |

## 2. System Architecture

```
[Browser] --> [Next.js Frontend] --> [FastAPI Backend] --> [PostgreSQL]
                  |                        |
                  |-- Static assets        |-- Alembic migrations
                  |-- API proxy (/api/*)   |-- Auth middleware
                  |-- Auth UI              |-- Business logic
```

### Client Layer

- Next.js serves the frontend application.
- API calls from the frontend proxy through Next.js rewrites to the FastAPI backend.
  This avoids CORS issues and keeps the backend URL internal.
- Path: `/api/*` (except `/api/auth/*`) rewrites to `BACKEND_URL` environment variable.

### Application Layer

- FastAPI handles all business logic, data access, and authentication verification.
- Endpoints are organized by domain: `routers/tasks.py`, `routers/projects.py`, etc.
- Dependencies (DB session, current user, config) injected via `Depends()`.

### Data Layer

- PostgreSQL 16 is the single data store.
- All queries enforce workspace isolation via `workspace_id` filter.
- Soft deletes use a `deleted_at` timestamp column.

## 3. Data Models

<!-- [CUSTOMIZE] Define your core entities. Be precise about relationships, constraints,
and field types. Agents generate migrations from this section. -->

### User

| Field      | Type         | Constraints             |
|------------|--------------|-------------------------|
| id         | UUID         | PK, auto-generated      |
| email      | VARCHAR(255) | Unique, not null        |
| name       | VARCHAR(100) | Not null                |
| created_at | TIMESTAMP    | Not null, default now() |
| updated_at | TIMESTAMP    | Not null, auto-updated  |

### Workspace

| Field      | Type        | Constraints             |
|------------|-------------|-------------------------|
| id         | UUID        | PK, auto-generated      |
| name       | VARCHAR(50) | Not null, 3-50 chars    |
| created_by | UUID        | FK -> User, not null    |
| created_at | TIMESTAMP   | Not null, default now() |

### WorkspaceMember

| Field        | Type      | Constraints                 |
|--------------|-----------|-----------------------------|
| workspace_id | UUID      | FK -> Workspace, PK         |
| user_id      | UUID      | FK -> User, PK              |
| role         | ENUM      | 'owner', 'member'; not null |
| joined_at    | TIMESTAMP | Not null, default now()     |

### Project

| Field        | Type         | Constraints               |
|--------------|--------------|---------------------------|
| id           | UUID         | PK, auto-generated        |
| workspace_id | UUID         | FK -> Workspace, not null |
| name         | VARCHAR(100) | Not null                  |
| description  | TEXT         | Nullable                  |
| archived_at  | TIMESTAMP    | Nullable (soft archive)   |
| created_at   | TIMESTAMP    | Not null, default now()   |

### Task

| Field        | Type         | Constraints                                         |
|--------------|--------------|-----------------------------------------------------|
| id           | UUID         | PK, auto-generated                                  |
| workspace_id | UUID         | FK -> Workspace, not null                           |
| project_id   | UUID         | FK -> Project, nullable                             |
| title        | VARCHAR(200) | Not null, 1-200 chars                               |
| description  | TEXT         | Nullable, max 5000 chars                            |
| status       | ENUM         | 'open', 'in_progress', 'done'; default 'open'       |
| priority     | ENUM         | 'low', 'medium', 'high', 'urgent'; default 'medium' |
| assignee_id  | UUID         | FK -> User, nullable                                |
| created_by   | UUID         | FK -> User, not null                                |
| deleted_at   | TIMESTAMP    | Nullable (soft delete)                              |
| created_at   | TIMESTAMP    | Not null, default now()                             |
| updated_at   | TIMESTAMP    | Not null, auto-updated                              |

**Indexes:**

- `task_workspace_status_idx` on (workspace_id, status) -- board view queries
- `task_workspace_assignee_idx` on (workspace_id, assignee_id) -- "my tasks" queries
- `task_workspace_project_idx` on (workspace_id, project_id) -- project view queries

## 4. API Design

All endpoints are defined in `contracts/openapi.yaml`. This document does not duplicate
the spec -- refer to the contract for endpoint details, request/response schemas, and
error formats.

**Conventions:**

- All endpoints are prefixed with `/api/`.
- Authentication: session cookie (`session`) required on all endpoints except `/api/health`.
- Pagination: `limit` and `offset` query parameters. Response includes `total` count.
- Error responses: `{"detail": "Human-readable error message"}` with appropriate HTTP status code.
- IDs: UUID v4, generated server-side.

## 5. Authentication and Authorization

- **Provider:** Better Auth (session-based, email/password).
- **Session storage:** Database-backed sessions in a `sessions` table.
- **Cookie:** `session` cookie, HttpOnly, Secure (in production), SameSite=Lax.
- **Backend verification:** Every protected endpoint uses a `get_current_user` dependency
  that reads the session cookie, looks up the session in the database, and returns the
  authenticated User or raises 401.
- **Authorization:** Workspace-level. Users can only access resources in workspaces where
  they are members. Enforced at the query level (every query includes `workspace_id` filter).

## 6. Deployment Architecture

### Local Development

```bash
docker compose up -d     # Starts: postgres, backend, frontend
```

- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- PostgreSQL: localhost:5432

### Production

- Container images built by GitHub Actions on merge to main.
- Images pushed to GitHub Container Registry (GHCR).
- Deployed via docker-compose on the target host.
- Environment variables stored in `.env.production` (not committed to repo).

## 7. Constraints and Invariants

<!-- WHY: These are things that break SILENTLY if violated. Unlike bugs that throw errors,
invariant violations produce wrong behavior that looks correct until you dig deeper.
Each one is listed because it was discovered the hard way. -->

- **Workspace isolation is enforced at the query level.** Every database query that returns
  user-facing data MUST include a `WHERE workspace_id = :workspace_id` clause. There is
  no application-level filter -- the query is the only enforcement point.
- **Soft deletes must be excluded from default queries.** Every query against a soft-deletable
  table MUST include `WHERE deleted_at IS NULL` unless explicitly querying deleted records.
- **Session cookie format:** Better Auth uses the format `token.hmac_signature`. The backend
  must split on `.` and use only the token portion for database lookup.
- **Migration and model sync:** After any Alembic migration, verify that SQLAlchemy models
  match the actual database schema. Migrations change the DB but do not auto-update models.

## 8. Architecture Decisions

<!-- [CUSTOMIZE] Record key decisions and their reasoning. Agents need to understand WHY
a choice was made to avoid "improving" it into something incompatible. -->

### AD-01: Next.js API Proxy Instead of Direct Backend Calls

**Decision:** Frontend API calls go through Next.js rewrites, not directly to FastAPI.
**Reasoning:** Avoids CORS configuration, keeps the backend URL internal, and allows
the frontend to add headers or transform requests if needed.

### AD-02: PostgreSQL Only (No Redis, No External Cache)

**Decision:** Use PostgreSQL for all data storage including sessions. No Redis.
**Reasoning:** Reduces operational complexity for small teams. PostgreSQL handles the
expected load. Add caching only when profiling shows a need.

### AD-03: Session Cookies Over JWTs

**Decision:** Use database-backed session cookies, not JWTs.
**Reasoning:** Sessions can be revoked immediately (important for security). JWTs require
a revocation list that adds the same complexity as sessions. For a server-rendered app,
cookies are simpler.

**[CUSTOMIZE]** Add your project's key architectural decisions with reasoning.

## 9. Security Considerations

<!-- WHY: Agents mention security generically but miss the enforcement patterns that matter
in multi-tenant SaaS. This section consolidates scattered security references (Sections 2,
5, 7) into explicit requirements. [CUSTOMIZE] Replace Beacon-specific details with your
application's security requirements. -->

### Tenant Data Isolation

- Every database query returning user-facing data includes a `WHERE workspace_id = :workspace_id`
  clause. There is no application-level fallback -- the query is the sole enforcement point.
- API endpoints resolve the workspace from the authenticated session. Users cannot pass an
  arbitrary workspace ID to access another tenant's data.

**[CUSTOMIZE]** Define your tenant isolation boundary and enforcement mechanism.

### Input Validation

- All user input is validated server-side. Client-side validation exists for UX responsiveness
  but is never trusted.
- Text fields (task titles, descriptions) are sanitized to prevent stored XSS. HTML is stripped
  on write, not on read.

**[CUSTOMIZE]** Specify which inputs are sanitized, what sanitization method is used, and
where validation rules are enforced.

### Rate Limiting

- Authentication endpoints (login, register) are rate-limited per IP to prevent credential
  stuffing.
- API endpoints are rate-limited per authenticated user to prevent abuse.
- Rate limit responses return `429 Too Many Requests` with a `Retry-After` header.

**[CUSTOMIZE]** Define your rate limits (requests per window) and which endpoints are
protected.

### Secrets Management

- Secrets (database credentials, API keys, session signing keys) are provided via environment
  variables. No secrets are committed to the repository.
- `.env` files are listed in `.gitignore`. Production secrets are managed through the
  deployment platform's secret store.

**[CUSTOMIZE]** Specify your secrets management approach and which secrets the application
requires.

### Transport Security

- All production traffic is served over HTTPS. HTTP requests redirect to HTTPS.
- Session cookies use `HttpOnly`, `Secure` (production), and `SameSite=Lax` attributes.
- CORS is not configured on the backend; the Next.js API proxy eliminates cross-origin
  requests.

**[CUSTOMIZE]** Define your transport security requirements, cookie attributes, and CORS
policy.
