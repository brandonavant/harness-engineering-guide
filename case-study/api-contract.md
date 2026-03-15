# Case Study: API Contract -- How OpenAPI Prevented Drift

The production application had two agents building opposite sides of the same API: a backend agent implementing FastAPI endpoints and a frontend agent consuming them via TypeScript fetch calls. Across 19 phases, neither agent ever communicated directly with the other. They never shared a session, never read each other's code, never coordinated in real time. Yet the frontend and backend were compatible at every integration checkpoint.

The reason was a single file: an OpenAPI YAML specification that served as the contract between them.

---

## The Contract

The OpenAPI spec defined every endpoint the application exposed: paths, HTTP methods, request schemas, response schemas, query parameters, error codes, and authentication requirements. It was approximately 2,000 lines of YAML and covered around 30 endpoints spanning user management, content CRUD, real-time streaming, image handling, and admin operations.

The spec was written during the design phase, before either agent wrote a line of implementation code. It was stored in `contracts/openapi.yaml` and referenced in CLAUDE.md as the "source of truth."

## How Each Agent Used the Contract

### Backend Agent

The backend agent read the OpenAPI spec when implementing each endpoint. Its instruction file told it to create Pydantic request and response models that matched the spec's schemas, FastAPI route handlers that matched the spec's paths and methods, and tests that verified the response structure against the spec.

The spec was not generated from the backend code. The backend code was generated from the spec. This distinction matters. When the spec is derived from implementation, it documents what was built. When the implementation is derived from the spec, the spec governs what gets built. The former is a mirror. The latter is a blueprint.

### Frontend Agent

The frontend agent read the same spec when building API client functions and data fetching hooks. It used the spec's schemas to define TypeScript types for request payloads and response bodies. The types were not copied from the backend's Python models -- they were independently derived from the same YAML source.

### Prism Mock Server

During frontend development phases, the backend was often not yet built or was being modified in a parallel session. The frontend agent used Prism, an OpenAPI mock server, to develop against the contract without needing the real backend. Prism reads the OpenAPI spec and returns valid mock responses that match the defined schemas.

This meant the frontend agent could build complete UI flows -- forms, data tables, error handling, loading states -- without waiting for the backend agent to finish. When the backend was ready, the frontend already worked against the contract. Integration was a matter of switching from mock to real, not rewriting.

The Docker Compose file included a mock-api profile specifically for this workflow:

```bash
docker compose --profile mock up postgres frontend mock-api
```

## Contract Governance

Neither agent was allowed to modify the OpenAPI spec. This was stated in CLAUDE.md and reinforced in each agent's instruction file. The governance model was:

1. **Agent discovers a needed change**: e.g., the backend agent needs a field not in the spec, or the frontend agent needs an endpoint that does not exist.
2. **Agent documents the deviation**: In its state file, under "Contract Deviations," the agent records what it needed, why, and what it did instead.
3. **Human reviews the deviation**: During the phase review, the human reads the deviation, decides whether to update the spec, and either applies the change or tells the agent to find another approach.

This process was used several times during the project. The most notable case involved a response type that the backend agent needed for AI output parsing. The OpenAPI spec defined a set of content segment types (dialogue, action, thought), but the backend's output parser needed an additional type (narrative) to handle a category of AI output that the spec had not anticipated.

The agent did not modify the spec. It added the type to its implementation, documented the deviation in its state file with a clear explanation, and flagged it for human review. The human reviewed the deviation, agreed it was necessary, and updated the spec. The frontend agent then picked up the new type in its next phase.

This process added maybe 10 minutes of overhead across the entire project. The alternative -- agents silently modifying the contract -- would have caused drift that could take hours to diagnose when the two sides stopped agreeing.

## A Mandatory Skill for Contract Validation

The project included a mandatory skill (`/api-contract-check`) that agents were required to invoke after implementing or modifying any API surface. The skill loaded the OpenAPI spec and compared it against the implementation, checking for:

- Endpoints in the spec that were not implemented
- Endpoints in the code that were not in the spec
- Request/response schema mismatches
- Missing error codes

This skill was invoked dozens of times across the project. It caught several minor drifts -- a query parameter with the wrong name, a response field with the wrong type -- before they became integration failures.

## The Key Lesson: Contracts Prevent the Telephone Game

In a traditional two-developer project, the developers can talk. They can say "I changed the response format" and the other developer can update their code. In agentic development, agents do not talk. They run in isolated sessions with no shared state except the files on disk.

Without a contract, the communication channel between agents is the codebase itself -- and that channel is noisy, ambiguous, and easy to misread. An agent reading another agent's Python code to infer an API schema is playing a telephone game. The contract eliminates the intermediary. Both agents read the same spec, in the same format, with the same semantics.

Across 19 phases, the contract prevented an unknowable number of integration failures. We know it worked because the failures we did see (documented in the [integration gate case study](integration-gate.md)) were all at layers the contract did not cover: cookie formats, proxy configurations, Docker build settings. At the API schema layer, where the contract governed, there were no integration failures after the contract was established.
