# Case Study: Timeline -- 19 Phases from Empty Repo to Production

This document traces the project's progression from an empty repository to a deployed production application across 19 phases. For each cluster of phases, it notes what skills were built (or should have been), what integration failures were caught, and what lessons were learned.

The timeline is presented in generalized terms. Specific feature names are omitted; the focus is on patterns and outcomes that apply to any project built with this approach.

---

## Phase 0: Interview and Requirements Extraction

**What happened**: The human conducted an extended requirements conversation with Claude, exploring the target audience, feature priorities, content policies, and competitive landscape. The output was a structured interview transcript that became the input for all subsequent design documents.

**Skills built**: None yet. This phase was conversational.

**Lessons learned**: The interview format worked better than writing requirements from scratch. Claude asked probing questions that surfaced edge cases the human had not considered. The key was treating Claude as an interviewer, not a scribe -- giving it permission to push back and explore alternatives.

## Phase 1: Specification Writing

**What happened**: Four design documents were produced: a Product Requirements Document, an Architecture document, a UX Specification, and a Brand Identity document. Each went through multiple revisions based on human review. A decision session resolved conflicts between documents and locked in technology choices.

**Skills built**: None. Skills were not yet part of the workflow.

**Retroactive insight**: A document-quality skill would have been valuable here -- one that checked for internal consistency, flagged vague requirements, and ensured every user-facing feature had acceptance criteria.

## Phases 2-3: Scaffold and Foundation

**What happened**: Database models, Pydantic schemas, application factory patterns, the design system shell (tokens, typography, color hierarchy), and authentication integration were built. The backend and frontend agents ran their first phases.

**Integration failures caught**: Two. The authentication library's cookie format was incompatible with the backend's session validation (Failure 1 from the [integration gate case study](integration-gate.md)). The frontend's auth configuration needed specific column name mappings to work with the backend's database schema.

**Skills built**: The brand enforcement skill was created during this cluster, initially as a simpler version that grew more sophisticated over time.

**Lessons learned**: Authentication is the first integration point and the most likely to break. The frontend and backend make different assumptions about cookie formats, session storage, and user schemas. Testing auth in isolation on both sides proves nothing about the integration. The smoke test's auth checks (register, get cookie, use cookie on protected endpoint) became the most important checks in the suite.

## Phases 4-6: Core Features

**What happened**: API endpoints for CRUD operations, the remaining auth integration, and the primary UI pages were built. The frontend agent developed against the Prism mock server while the backend agent built the real endpoints. The OpenAPI contract mediated between them.

**Integration failures caught**: One. The frontend called `/api/*` endpoints with no proxy configured to forward them to the backend (Failure 3). This was invisible during development because the mock server handled the requests.

**Skills built**: The API contract check skill was created during this cluster and made mandatory. It caught several minor schema mismatches (wrong field names, missing query parameters) before they reached integration.

**Lessons learned**: The mock server is a double-edged sword. It enables parallel frontend development, which is a significant productivity gain. But it also hides integration issues that only appear when the mock is replaced with the real backend. The solution is not to abandon the mock server -- it is to run the integration smoke test after every phase, not just phases where "something might have changed."

## Phases 7-9: Complex Features

**What happened**: Real-time streaming via Server-Sent Events, knowledge graph integration (Neo4j via a sidecar service), and multi-entity routing were built. These phases introduced the most architecturally complex features: long-running connections, graph queries, entity resolution, and streaming response parsing.

**Integration failures caught**: One. The sidecar service's Dockerfile had an incorrect build configuration (Failure 4). The service worked in local development but failed to build as a container.

**Skills built**: None new. The existing two skills (brand enforcement, contract check) were refined based on accumulated experience.

**Retroactive insight**: Three skills should have been built during this cluster:
1. **A streaming verification skill** that loaded the SSE protocol constraints and verified that the agent's implementation matched the expected event format
2. **A knowledge graph consistency skill** that checked entity isolation rules (entities from one context must not leak into another)
3. **A prompt engineering skill** that loaded the caching invariants and verified that any changes to the AI inference pipeline preserved the cache prefix

The prompt caching invariants were documented in CLAUDE.md but violated twice during later phases, requiring debugging. A skill that loaded those invariants at the moment the agent touched the inference pipeline would have prevented both incidents.

## Phases 10-12: Advanced Features

**What happened**: The content generation pipeline (AI text generation with structured output parsing), the image handling pipeline (external API for generation, content safety moderation, cloud storage, format conversion), and the repetition detection system (a multi-layer hybrid approach to preventing repetitive AI output) were built.

**Integration failures caught**: None in this cluster. The integration smoke test passed after every phase. By this point, the harness was mature enough that the agents produced integration-compatible code on the first attempt.

**Skills built**: None new.

**Retroactive insight**: An image pipeline skill would have been valuable -- one that loaded the content safety constraints, the storage format requirements, and the CDN URL patterns. The image pipeline touched multiple external services, and the agent needed to read several documentation pages to get the integration right. A skill could have consolidated that context.

**Lessons learned**: The absence of integration failures in this cluster was notable. The harness was working. Rules, skills, agent instructions, and the contract were all mature enough to prevent the classes of errors that plagued earlier phases. This is the compounding effect of harness engineering: investment in the environment pays dividends in every subsequent phase.

## Phases 13-15: UI Completion

**What happened**: Full CRUD flows for user-created content, the messaging interface (message feed, input composition, character indicators), onboarding (splash screen, age verification, first-session guidance), and the character creation form (a multi-step wizard) were built.

**Integration failures caught**: None.

**Skills built**: The brand enforcement skill was refined during this cluster to include checks specific to form layouts and multi-step flows.

**Lessons learned**: The brand enforcement skill proved its value most clearly in this cluster. The frontend agent was building the most visually complex pages (messaging, onboarding, character creation), and every component passed the 27-item checklist. Without the skill, these pages would have defaulted to generic patterns. With it, they maintained the brand's distinctive visual identity. The contrast between early phases (before the skill was mature) and these later phases was visible and significant.

## Phases 16-17: Polish

**What happened**: Account management (profile editing, support contact, account deletion) and an admin portal (separate login, entity management, user management) were built.

**Integration failures caught**: None.

**Skills built**: None new.

**Lessons learned**: These phases went smoothly because they followed established patterns. The admin portal was a new UI surface, but it used the same design system, the same API patterns, and the same auth flow as the user-facing application. The harness made "another CRUD interface" a predictable task.

## Phase 18: Accessibility and Quality Audit

**What happened**: A full WCAG 2.1 AA audit was conducted. Color contrast ratios were verified against all background layers. Focus indicators were added. Keyboard navigation was tested. Motion and animation were polished. The anti-generic checklist was run across every page.

**Integration failures caught**: None.

**Skills built**: None, but the brand enforcement skill was extended to include accessibility checks.

**Retroactive insight**: An accessibility skill should have existed from Phase 2. Building accessibility in at the end works, but building it in from the start is cheaper. The skill would have loaded WCAG requirements at the same time as brand requirements, preventing the need for a dedicated audit phase.

## Phase 19: CI/CD Pipeline and Deployment

**What happened**: GitHub Actions workflows were created for CI (lint, test, build on every PR) and release (ARM64 container images to GHCR on merge to main). A production Docker Compose file was created for the deployment target. Watchtower was configured for automatic image pulls. Version management was implemented (a VERSION file with CI-appended build numbers).

**Integration failures caught**: Multiple build-related issues were caught during this phase, though they were CI/CD issues rather than application integration issues. ARM64 builds under QEMU emulation took significantly longer than expected. Dependency pinning requirements were discovered when newer tool versions introduced breaking rule changes.

**Skills built**: None.

**Lessons learned**: CI/CD is the final integration gate. It verifies not just that the code works, but that it can be built, packaged, and shipped. ARM64 cross-compilation added a layer of complexity that was not present in local development (where all builds were native). The lesson: always build for your production architecture in CI, even if it is slow.

---

## Summary Metrics

| Metric | Value |
|--------|-------|
| Total implementation phases | 19 (8 backend, 11 frontend) |
| Backend tests | 434+ |
| Sidecar tests | 15+ |
| Integration smoke test checks | 16, all passing after every phase |
| Critical integration failures caught (missed by unit tests) | 4 |
| Mandatory skills used | 2 (brand enforcement, API contract check) |
| Skills identified retroactively as should-haves | 6 (document quality, streaming verification, knowledge graph consistency, prompt engineering, image pipeline, accessibility) |
| CI jobs per PR | 3 (lint, test, build) |
| Container images per release | 3 (backend, frontend, sidecar) |
| Lines of manually-written application code | 0 |
| Merge conflicts between agents | 0 |

## The Key Lesson

The timeline shows a clear arc: early phases had more integration failures, more manual intervention, and more harness refinement. Later phases were faster, smoother, and produced fewer surprises. This is the compounding effect. Every rule added to CLAUDE.md, every skill created, every lesson encoded into agent instructions made the next phase incrementally better.

The two mandatory skills (brand enforcement and API contract check) were the highest-leverage investments. The six retroactively identified skills represent the project's main missed opportunity. Building skills proactively -- at the moment you realize a complex procedure will be repeated -- is one of the highest-return activities in harness engineering. The timeline makes this visible: the phases where skills existed went smoothly, and the phases where they were missing required more correction.
