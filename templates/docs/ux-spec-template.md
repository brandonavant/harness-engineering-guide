# Beacon -- UX Specification

<!-- WHY THIS DOCUMENT EXISTS:
Without screen-by-screen specs, agents invent UI behavior. They make reasonable guesses
that conflict with each other and with user expectations. This document specifies exactly
what each screen shows, how interactions work, and what happens in edge cases.

[CUSTOMIZE] Replace screen specs with your product's actual screens. Keep the level
of detail -- specify behavior, not just layout. -->

## Document Header

| Field | Value |
|-------|-------|
| Version | v1.0 |
| Date | 2025-01-15 |
| Author | [CUSTOMIZE] |
| Change Summary | Initial version |

---

## 1. Navigation and Layout

### Global Layout
- **Top bar:** Logo (left), workspace switcher (center), user avatar menu (right).
- **Sidebar (desktop):** Collapsible, 240px default width. Contains: project list,
  view switcher (Board / List), search trigger.
- **Main content area:** Fills remaining viewport width. Scrollable independently of sidebar.
- **No bottom navigation** on desktop. On mobile (< 768px), sidebar collapses to a
  hamburger menu in the top bar.

### Responsive Breakpoints
| Breakpoint | Width | Layout Change |
|------------|-------|---------------|
| Mobile | < 768px | Sidebar hidden, hamburger menu, single-column content |
| Tablet | 768px - 1024px | Sidebar collapsed (icons only), two-column board |
| Desktop | > 1024px | Full sidebar, multi-column board |

## 2. Screen Specifications

### 2.1 Board View (Default)

<!-- [CUSTOMIZE] Replace with your product's primary screen. Be specific about what
each element shows, how it behaves, and what happens on interaction. -->

**URL:** `/workspace/:id/board`

**Layout:** Three columns: Open, In Progress, Done. Each column has a header with the
status name and a count of tasks in that status.

**Task cards:**
- Title (truncated at 2 lines with ellipsis).
- Priority indicator: colored left border (low=green, medium=blue, high=amber, urgent=red).
- Assignee avatar (24px circle) in bottom-right corner. Unassigned shows a dashed circle.
- Created date in relative format ("2h ago", "3d ago") as secondary text.

**Interactions:**
- **Drag and drop:** Cards can be dragged between columns. On drop, task status updates
  via PATCH request. Optimistic update with rollback on failure.
- **Click card:** Opens task detail panel (slide-in from right, 480px width on desktop,
  full-screen on mobile).
- **"+ New task" button:** At the bottom of each column. Opens inline input field
  (title only). Press Enter to create, Escape to cancel. New task gets the column's status.
- **Column overflow:** Columns scroll independently when content exceeds viewport height.

**Filters (top bar above columns):**
- Project dropdown (default: all projects).
- Assignee dropdown (default: all members).
- Priority dropdown (default: all priorities).
- Filters apply immediately. URL query params update to reflect active filters.

**States:**
- **Loading:** Skeleton columns matching board layout, 3 placeholder cards per column.
- **Empty (no tasks):** Centered message with icon and "Create a task" action (see Section 3).
- **Error (load failure):** Inline error banner above columns with retry button.

### 2.2 List View

**URL:** `/workspace/:id/list`

**Layout:** Full-width table with columns: checkbox, title, status, priority, assignee,
project, created date.

**Interactions:**
- **Sort:** Click column header to sort. Click again to reverse. Active sort column
  shows an arrow indicator.
- **Bulk actions:** Select multiple tasks via checkboxes. Bulk actions bar appears at
  top: "Change status", "Change priority", "Delete" (soft).
- **Inline edit:** Double-click task title to edit inline. Press Enter to save, Escape to cancel.
- **Click row:** Opens task detail panel (same as board view).

**Pagination:** 50 tasks per page. "Load more" button at bottom (not numbered pages).

**States:**
- **Loading:** Skeleton table rows matching column layout, 5 placeholder rows.
- **Empty (no tasks):** Full-width centered message with "Create a task" action (see Section 3).
- **Error (load failure):** Inline error banner above table with retry button.

### 2.3 Task Detail Panel

**URL:** No URL change (panel overlays current view).

**Layout:** Slide-in panel from right side. 480px wide on desktop, full-screen on mobile.

**Sections:**
- **Header:** Title (editable inline), close button (X).
- **Metadata bar:** Status dropdown, priority dropdown, assignee dropdown, project dropdown.
  Changes save immediately on selection (no save button).
- **Description:** Editable text area. Saves on blur (debounced 1 second).
- **Activity log:** Shows status changes and assignments with timestamps.

**Close behavior:** Click X, press Escape, or click outside the panel.

**States:**
- **Loading:** Skeleton blocks matching section layout (title bar, metadata bar, description area).
- **Not found:** "This task no longer exists" message with "Go back" action.
- **Error (save failure):** Toast notification with retry; field reverts to previous value.

## 3. Interaction Patterns

### Keyboard Navigation
- `Tab` moves focus through interactive elements in document order.
- `Escape` closes any open panel, modal, or dropdown.
- `Ctrl+K` (or `Cmd+K`) opens the search dialog.
- `/` focuses the search input when no text field is focused.
- Arrow keys navigate within dropdowns and menus.
- `Enter` activates the focused element.

### Loading States
- **Page load:** Skeleton screens matching the content layout (not a centered spinner).
  Skeletons pulse with a subtle animation.
- **Action in progress:** Button shows a loading indicator (spinner replacing icon or
  label). Button is disabled during the action.
- **Optimistic updates:** Board drag-and-drop, status changes, and inline edits update
  the UI immediately. If the server rejects the change, revert the UI and show an error toast.

### Error States
- **Network error:** Toast notification at bottom-right. "Unable to save changes. Retrying..."
  Auto-retry 3 times with exponential backoff. After 3 failures: "Changes could not be saved.
  Please check your connection."
- **Validation error:** Inline error message below the input field. Red border on the field.
  Error text is specific ("Title must be between 1 and 200 characters" not "Invalid input").
- **404 / Not found:** Full-page message: "This task no longer exists. It may have been
  deleted." with a "Go back" button.
- **403 / Forbidden:** Full-page message: "You don't have access to this workspace."
  with a "Return to your workspaces" button.

### Empty States
- **No tasks in project:** Illustration (subtle, on-brand) with text: "No tasks yet.
  Create one to get started." and a primary action button.
- **No search results:** "No tasks match your search. Try different keywords."
- **No projects:** "Create your first project to start organizing tasks."

Empty states always include a clear next action. Never show just "No data."

## 4. Accessibility

<!-- [CUSTOMIZE] Choose your WCAG target (version and conformance level) and state it here.
The canonical WCAG specification (https://www.w3.org/TR/WCAG22/) is the authoritative
reference for success criteria -- this section should not attempt to enumerate them.
Instead, state your target, reference the spec, and call out product-specific accessibility
risks that agents are likely to miss. If you choose to omit accessibility coverage, document
the justification explicitly. -->

**Target:** WCAG **[CUSTOMIZE: version, e.g., 2.2]** Level **[CUSTOMIZE: conformance level,
e.g., AA]**. All success criteria for the chosen level apply. Reference the canonical WCAG
specification for the full list of requirements rather than maintaining a separate enumeration
here.

**Product-specific accessibility notes (Beacon):**
- Drag-and-drop on the board view must have a keyboard alternative (select card, use
  dropdown or keyboard shortcut to change status).
- Priority indicators use color-coded borders; priority must also be conveyed through a
  text label or icon so that no information is communicated by color alone.
- Focus indicators must be custom (not browser default) and clearly visible against both
  light and dark surface colors used in the application.
- Dynamic content updates (optimistic status changes, inline saves, toast notifications)
  must use appropriate ARIA live regions.

## 5. Responsive Behavior

| Component | Mobile (< 768px) | Tablet (768-1024px) | Desktop (> 1024px) |
|-----------|------------------|--------------------|--------------------|
| Sidebar | Hidden, hamburger menu | Collapsed (icons) | Full (240px) |
| Board columns | Horizontal scroll | 2 visible | 3 visible |
| Task detail | Full-screen | Full-screen | Side panel (480px) |
| Table (list) | Card layout | Condensed table | Full table |
| Filters | Collapsible section | Inline | Inline |

## 6. Error States Summary

<!-- Quick reference for agents implementing error handling. -->

| Error | Display | Recovery |
|-------|---------|----------|
| Network failure | Toast, auto-retry | "Check your connection" after 3 retries |
| Validation error | Inline below input | Fix input and resubmit |
| 401 Unauthorized | Redirect to login | Log in again |
| 403 Forbidden | Full-page message | "Return to workspaces" link |
| 404 Not Found | Full-page message | "Go back" button |
| 500 Server Error | Toast | "Something went wrong. Try again." |
