# Beacon -- Product Requirements Document

<!-- WHY THIS DOCUMENT EXISTS:
This is the single source of truth for WHAT to build and WHY. Architecture says HOW,
UX spec says WHAT IT LOOKS LIKE, but the PRD says WHAT IT DOES and WHO IT IS FOR.
Without a PRD, agents fill in requirements gaps with assumptions -- and those assumptions
are usually wrong.

[CUSTOMIZE] Replace all Beacon-specific content with your product. Keep the structure. -->

## Document Header

| Field | Value |
|-------|-------|
| Version | v1.0 |
| Date | 2025-01-15 |
| Author | [CUSTOMIZE] |
| Change Summary | Initial version |

---

## 1. Vision and Overview

<!-- [CUSTOMIZE] 3-5 sentences describing WHAT the product is and WHY it exists.
Be specific about the problem being solved. "A better X" is not a vision. -->

Beacon is a task management application for small engineering teams (5-20 people) who
need lightweight project tracking without the overhead of enterprise tools. Teams create
workspaces, organize tasks into projects, assign work to team members, and track progress
through board and list views.

The core thesis: small teams abandon heavy tools (Jira, Asana) because the setup cost
exceeds the value. Beacon provides 80% of the functionality with 20% of the configuration.
Opinionated defaults over infinite customization.

## 2. Target Persona

<!-- [CUSTOMIZE] Describe the primary user. Be specific: role, team size, pain points,
existing workflow, what they care about, what they do NOT care about. A persona that
could describe anyone describes no one. -->

**Primary persona: The Tech Lead**

- Manages a team of 5-15 engineers.
- Currently tracks work in a mix of GitHub Issues, Slack threads, and spreadsheets.
- Wants visibility into what is in progress and what is blocked.
- Does NOT want to spend time configuring workflows, custom fields, or automation rules.
- Values speed and keyboard navigation over visual richness.
- Cares about: task assignment, status tracking, search, and a clean board view.
- Does NOT care about: Gantt charts, resource planning, time tracking, invoicing.

## 3. Feature Requirements

<!-- [CUSTOMIZE] List every feature with a unique ID, description, and acceptance criteria.
The agent implements against these -- vague features produce vague implementations.
Number them so agents can reference specific requirements in their state files. -->

### F-01: Workspace Management
Users can create and manage workspaces. Each workspace is an isolated tenant.
- **AC-01:** User can create a workspace with a name (3-50 characters).
- **AC-02:** User can invite members by email.
- **AC-03:** Workspace data is fully isolated -- no cross-workspace queries.

### F-02: Project Organization
Tasks are organized into projects within a workspace.
- **AC-01:** User can create a project with a name and optional description.
- **AC-02:** Projects belong to exactly one workspace.
- **AC-03:** User can archive a project (soft delete -- tasks preserved but hidden from default views).

### F-03: Task CRUD
Users can create, read, update, and delete tasks.
- **AC-01:** Task requires a title (1-200 characters). Description is optional (up to 5000 characters).
- **AC-02:** Tasks have a status: open, in_progress, done.
- **AC-03:** Tasks have a priority: low, medium (default), high, urgent.
- **AC-04:** Tasks can be assigned to one workspace member.
- **AC-05:** Deleting a task is a soft delete (recoverable for 30 days).

### F-04: Board View
Kanban-style board showing tasks grouped by status.
- **AC-01:** Columns: Open, In Progress, Done.
- **AC-02:** Tasks can be dragged between columns to change status.
- **AC-03:** Board respects active filters (project, assignee, priority).

### F-05: List View
Table-style view showing tasks in a sortable, filterable list.
- **AC-01:** Columns: title, status, priority, assignee, created date.
- **AC-02:** Sortable by any column.
- **AC-03:** Filterable by status, priority, assignee, project.

### F-06: Search
Full-text search across task titles and descriptions.
- **AC-01:** Search results appear as user types (debounced, 300ms).
- **AC-02:** Results show task title, project, status, and a snippet of matching description text.
- **AC-03:** Search is scoped to the active workspace.

### F-07: Authentication
Session-based authentication using Better Auth.
- **AC-01:** Users register with email and password.
- **AC-02:** Users log in and receive a session cookie.
- **AC-03:** All API endpoints (except health) require a valid session.
- **AC-04:** Users can log out (session invalidated server-side).

## 4. Non-Functional Requirements

<!-- These apply regardless of what features you are building. They are constraints
on HOW features work, not WHAT they do. -->

- **N-01: Performance** -- Page loads under 2 seconds on 3G. API responses under 500ms (p95).
- **N-02: Accessibility** -- WCAG 2.1 AA compliance. All interactive elements keyboard-navigable.
- **N-03: Security** -- No plaintext passwords. CSRF protection. Input sanitization on all user content.
- **N-04: Data Integrity** -- Foreign key constraints enforced at the database level. No orphaned records.
- **N-05: Multi-tenancy** -- Workspace isolation enforced at the query level (every query filters by workspace_id).

## 5. Content Policy and Constraints

<!-- [CUSTOMIZE] Define what the product will and will NOT allow in terms of user-generated
content, language, themes. Be explicit about legal or compliance requirements. -->

- Task content is user-generated text. No moderation required at MVP (internal team tool).
- No file uploads at MVP.
- No markdown rendering at MVP (plain text only).

## 6. Non-Goals (Explicit)

<!-- WHY: Agents are eager to "improve" things. Without explicit non-goals, they add
features that sound reasonable but are out of scope. -->

The following are explicitly NOT in scope for MVP:
- Time tracking or time estimation on tasks.
- Gantt charts or timeline views.
- Automation rules (e.g., "when status changes to Done, notify assignee").
- Custom fields on tasks.
- File attachments.
- Mobile native app (responsive web only).
- Public-facing API (internal use only).
- Webhooks or integrations with external tools.

## 7. Open Questions

<!-- Record unresolved decisions here. Agents must not guess at answers -- they should
flag the question and wait for resolution. -->

- **OQ-01:** Should archived projects be permanently deletable, or retained indefinitely?
- **OQ-02:** What is the maximum number of workspaces per user?
- **OQ-03:** Should task assignment trigger an email notification at MVP, or is in-app sufficient?
