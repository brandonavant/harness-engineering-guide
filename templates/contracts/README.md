# API Contract Governance

<!-- WHY THIS EXISTS:
Without a single source of truth, frontend and backend diverge silently. The frontend
adds a field the backend does not return; the backend renames a field the frontend still
reads. This directory and these rules prevent that drift. -->

## The Rule

`openapi.yaml` is the **authoritative specification** for every API endpoint, request
body, response schema, and error format. Both backend and frontend implement against it.
Neither agent modifies it unilaterally.

## Versioning Policy

- **Patch-level changes** (additive, non-breaking): new optional fields, new endpoints,
  expanded enums. Bump the patch version in the spec's `info.version`.
- **Minor-level changes** (breaking): renamed fields, removed endpoints, changed required
  fields, altered response structure. Bump the minor version. All agents must update
  their implementations.
- **Proposing a change:** Record the proposed change in your agent memory under
  "Contract Deviations." The team lead reviews and applies changes to the spec.

## Usage Commands

```bash
# Generate TypeScript types from the spec (frontend)
npx openapi-typescript contracts/openapi.yaml -o packages/shared-types/api.d.ts

# Run a mock API server for frontend development (Prism)
npx @stoplight/prism-cli mock contracts/openapi.yaml --port 4010

# Lint the spec for errors
npx @redocly/cli lint contracts/openapi.yaml

# Preview interactive docs
npx @redocly/cli preview contracts/openapi.yaml
```

## Adding New Endpoints

1. Define the endpoint, request/response schemas, and error responses in `openapi.yaml`.
2. Get team lead approval on the spec change.
3. Both agents implement against the updated spec.
4. Run the API contract check skill (`/api-contract-check`) after implementation.
