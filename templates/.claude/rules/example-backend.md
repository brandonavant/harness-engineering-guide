---
paths:
  - "apps/backend/**"
  - "src/backend/**"
---

# Backend Code Conventions

<!-- This is a path-scoped rule. Claude Code loads it automatically when editing files
that match the paths above. Use rules for conventions that must apply consistently
to every edit in a directory -- they fire without the agent needing to remember. -->

## Python / FastAPI Conventions

- Python 3.12+ required. Use modern syntax: `str | None` not `Optional[str]`, `list[int]` not `List[int]`.
- All endpoints return Pydantic response models. Never return raw dicts.
- Use `Depends()` for dependency injection (DB sessions, auth, config). Do not instantiate dependencies manually.
- Endpoint functions are `async def`. Use `await` for all I/O operations.
- Route definitions use APIRouter, not the app instance directly. Group by domain (e.g., `routers/tasks.py`).

## Error Handling

- Raise `HTTPException` with specific status codes. Never return 200 with an error body.
- Use custom exception classes in `exceptions.py` for domain errors. Map them to HTTP status codes in exception handlers.
- All 4xx/5xx responses must include a `detail` field matching the OpenAPI error schema.
- Never expose stack traces, internal paths, or implementation details in error responses.

## Import Ordering

Enforce with ruff (isort rules). The order is:
1. Standard library
2. Third-party packages
3. Local application imports (absolute paths from project root)

Never use relative imports (`from .models import ...`). Always use absolute imports.

## Testing Requirements

- Every endpoint requires at least one happy-path and one error-path test.
- Use pytest fixtures for DB sessions, authenticated clients, and test data.
- Test files mirror the source structure: `routers/tasks.py` -> `tests/routers/test_tasks.py`.
- Use `httpx.AsyncClient` with the FastAPI test app for endpoint tests. Do not use `requests`.
- Factories (in `tests/factories/`) create test entities. Never hardcode entity data in test functions.

## Database / SQLAlchemy

- Models use SQLAlchemy 2.0 declarative style with `mapped_column()`.
- All queries use the async session pattern: `async with session.begin():`.
- Never use raw SQL strings. Use SQLAlchemy expression language or ORM queries.
- Alembic migrations are auto-generated but always reviewed. Migration files must have descriptive names.
- After changing a model, immediately generate and verify the migration: `alembic revision --autogenerate -m "description"`.

## [CUSTOMIZE]

Replace the conventions above with your project's actual backend standards. Keep the
structure: language rules, error handling, imports, testing, database. Add sections for
any patterns specific to your stack (e.g., background tasks, caching, rate limiting).
