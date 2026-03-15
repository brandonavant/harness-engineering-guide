# Case Study: Building a Production Application with Zero Manually-Written Code

This case study documents the development of a production web application built entirely through harness engineering with Claude Code. Every line of application code -- backend, frontend, database migrations, tests, CI/CD pipelines -- was written by Claude. The human engineer wrote zero application code. The human's output was the harness: CLAUDE.md, agent instructions, design documents, skills, rules, and the integration verification layer.

This is not a prototype. The application ships, deploys, and serves users.

---

## What Was Built

A full-stack web application with the following architecture:

- **Frontend**: Next.js (TypeScript), Tailwind CSS, shadcn/ui component library, Zustand state management, TanStack Query for data fetching
- **Backend**: FastAPI (Python 3.12+), SQLAlchemy 2.0 ORM, Alembic migrations
- **Database**: PostgreSQL 16 with pgvector extension for vector similarity search
- **Knowledge Graph**: Neo4j (via a sidecar service) for entity relationship tracking and memory
- **Real-time**: Server-Sent Events (SSE) for streaming responses
- **Auth**: Better Auth (frontend) with custom session validation (backend)
- **AI Integration**: Claude as the primary LLM, with prompt caching optimization for cost reduction
- **Image Pipeline**: External API integration for image generation, content safety moderation, cloud storage
- **Deployment**: ARM64 container images (GHCR), automated release pipeline, Watchtower auto-pull on production hardware

The application is a dark-themed literary application with strict brand identity requirements, WCAG 2.1 AA accessibility compliance, and a custom design system.

## The Team

One human engineer and Claude Code. No other developers, designers, or QA engineers. The human acted as environment designer, taste arbiter, integration verifier, and strategic decision maker. Claude acted as the implementation agent across 19 phases.

## Key Metrics

| Metric | Value |
|--------|-------|
| Backend tests | 434+ |
| Sidecar tests | 15+ |
| Integration smoke test checks | 16 |
| Implementation phases | 19 (8 backend, 11 frontend) |
| Lines of manually-written application code | 0 |
| CI jobs per PR | 3 (lint, test, build) |
| Container images built per release | 3 (backend, frontend, sidecar) |
| Integration failures caught by smoke test (missed by unit tests) | 4 critical |
| Mandatory skills | 2 active, 6 identified retroactively |

## Timeline

The project spanned several months from empty repository to production deployment. The progression was:

1. **Requirements and design** (Phases 0-1): Interview, PRD, architecture doc, UX specification, brand identity document
2. **Scaffold and foundation** (Phases 2-3): Models, schemas, app factory, design system shell, auth integration
3. **Core features** (Phases 4-9): API endpoints, UI pages, real-time streaming, knowledge graph, multi-entity routing
4. **Advanced features** (Phases 10-15): Content generation pipeline, image handling, full CRUD flows, messaging, onboarding
5. **Polish and deployment** (Phases 16-19): Account management, admin portal, accessibility audit, CI/CD pipeline

Each phase followed the same cycle: human defines scope, agent implements, human verifies integration, human reviews and merges.

## Key Outcomes

- **The application works.** It is not a demo or a proof of concept. It runs on production hardware, handles real user interactions, and persists data across sessions.
- **The harness compounds.** Each phase was faster than the last because the harness -- CLAUDE.md, rules, skills, agent instructions -- accumulated project knowledge. By phase 15, the agent needed less guidance per task than in phase 3.
- **Integration testing is non-negotiable.** Four critical cross-system failures were caught only by the integration smoke test. All four had passing unit tests on both sides of the boundary. Without the smoke test, these would have been discovered by users.
- **Brand enforcement works when loaded at the right time.** The mandatory design skill, invoked before every frontend task, produced a visually distinct application that does not look like a default template. This was cited as the most successful part of the entire project.

## How to Read This Case Study

The remaining files in this directory each examine one aspect of the project in detail:

- [CLAUDE.md structure](claude-md.md) -- How the root configuration file was organized
- [Agent instructions](agent-instructions.md) -- How territorial boundaries prevented conflicts
- [API contract](api-contract.md) -- How OpenAPI prevented frontend/backend drift
- [Integration gate](integration-gate.md) -- The failures that unit tests missed
- [Brand enforcement](brand-enforcement.md) -- The five-layer system that prevented generic output
- [Timeline](timeline.md) -- 19 phases from empty repo to production, with lessons per cluster
