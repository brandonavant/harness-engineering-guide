# Beacon -- Project Interview Summary

<!-- WHY THIS DOCUMENT EXISTS:
This is the output of the structured interview that kicks off every project. It captures
the human's intent before any formal specification begins. The PRD, architecture doc, and
every downstream document build on this summary. If this is wrong or vague, everything
downstream inherits that problem.

[CUSTOMIZE] Replace all Beacon-specific content with your project. Keep the structure. -->

## Product Vision

<!-- [CUSTOMIZE] 2-4 sentences describing WHAT the product is and WHY it exists.
Be specific about the problem being solved. -->

Beacon is a task management application for small engineering teams (5-20 people) who
need lightweight project tracking without the overhead of enterprise tools. Teams abandon
heavy tools because the setup cost exceeds the value. Beacon provides 80% of the
functionality with 20% of the configuration.

## Target Persona

<!-- [CUSTOMIZE] Describe the primary user: role, team size, pain points, existing
workflow, what they care about, what they do NOT care about. -->

Tech leads managing teams of 5-15 engineers. Currently tracks work in a mix of GitHub
Issues, Slack threads, and spreadsheets. Wants visibility into what is in progress and
what is blocked. Does NOT want to spend time configuring workflows, custom fields, or
automation rules. Values speed and keyboard navigation over visual richness.

## Core Experience

<!-- [CUSTOMIZE] If the product does one thing well, what is that thing? Everything
else is secondary. -->

The user creates a workspace, adds their team, and starts tracking tasks in under two
minutes. No setup wizards, no onboarding tours, no mandatory configuration. Board view
and list view are immediately usable with opinionated defaults.

## Tech Stack Decisions

<!-- [CUSTOMIZE] State your choices explicitly. Vagueness here leads to the agent
picking whatever its training data over-represents. Pin major versions. -->

- Frontend: Next.js 15, TypeScript, Tailwind CSS v4, shadcn/ui
- Backend: FastAPI, Python 3.12+, SQLAlchemy 2.0, Alembic
- Database: PostgreSQL 16
- Auth: Better Auth (session cookies)
- Deployment: Docker containers, GitHub Actions CI

## Non-Negotiables

<!-- [CUSTOMIZE] Constraints the agent must never violate. These become rules. -->

- Multi-tenant workspace isolation enforced at the query level
- No plaintext passwords; CSRF protection on all forms
- WCAG 2.1 AA accessibility compliance
- All interactive elements keyboard-navigable
- Page loads under 2 seconds on 3G

## Non-Goals (MVP)

<!-- [CUSTOMIZE] Explicitly state what is out of scope. Without this list, agents
over-engineer. -->

- Time tracking or time estimation on tasks
- Gantt charts or timeline views
- Automation rules or webhooks
- Custom fields on tasks
- File attachments
- Mobile native app (responsive web only)
- Public-facing API
