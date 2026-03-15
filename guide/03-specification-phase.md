# Chapter 03 -- Specification Phase: Producing Docs Agents Can Execute Against

> Part 2: Specify

**Entry point**: A repository with CLAUDE.md, an interview summary, and a working hello-world scaffold.
**Exit point**: A complete specification suite -- PRD, architecture doc, UX spec, API contract (OpenAPI YAML), brand/design direction doc -- that agents can implement against without ambiguity.

**Templates referenced**: `templates/docs/prd-template.md`, `templates/docs/architecture-template.md`, `templates/docs/ux-spec-template.md`, `templates/contracts/openapi-stub.yaml`, `templates/docs/brand-identity-template.md`

---

## 3.1 Why Specs Matter More in Agentic Coding

In traditional development, a surprising amount of product knowledge lives outside the codebase. It is in Slack threads, whiteboard photos, design tool files, meeting notes, and the heads of engineers who have been on the project since the beginning. A new developer absorbs this knowledge through osmosis over weeks.

An AI agent has none of this. Its entire understanding of your product comes from what is in the repository. If a design decision is not written down, it does not exist for the agent. If a constraint is mentioned in a Slack thread but not in a doc, the agent will violate it.

This makes specification documents the most leveraged work you can do. A well-written PRD saves dozens of correction cycles. A precise UX spec eliminates entire categories of "that's not what I meant" reviews. An API contract that both frontend and backend agents implement against prevents integration failures.

The standards for specification quality are also different. In a human team, a spec can be somewhat vague because the engineer will ask a colleague or check the design tool when they are unsure. An agent does not have that option. If the spec says "display the user's recipes," the agent will make decisions about layout, sorting, pagination, empty states, and error handling -- and those decisions may not match what you envisioned. The spec must be specific enough to constrain those decisions.

This does not mean specs must be exhaustive. It means they must be unambiguous about the things that matter and explicit about the things they leave open.

## 3.2 The Document Cascade

Each specification document feeds the next. The order is not arbitrary -- it reflects a dependency chain.

```
Interview Summary
      |
      v
    PRD (what are we building and why)
      |
      v
  Architecture (how do the systems connect)
      |
      v
   UX Spec (how does it look and behave)
      |
      v
  API Contract (the formal interface between systems)
      |
      v
  Brand Identity (how to avoid generic output)
```

**PRD** defines what the product is, who it is for, and what it must do. Everything downstream references it.

**Architecture** translates PRD requirements into technical decisions: which systems exist, how they communicate, what data they store, where they run. It depends on the PRD because you cannot design a system without knowing what it needs to do.

**UX Spec** defines every screen, interaction, and edge case. It depends on both the PRD (what features exist) and the architecture (what is technically feasible and where the data comes from).

**API Contract** formalizes the interface between frontend and backend (or between any two systems). It depends on the UX spec (what data the frontend needs) and the architecture (what the backend can provide).

**Brand Identity** defines the visual and tonal identity. It can be produced in parallel with the UX spec, but ideally feeds into it: the UX spec references brand tokens for colors, typography, and spacing.

Do not skip ahead. Do not write the API contract before the architecture is decided. Each document resolves ambiguities that the next document depends on.

## 3.3 Writing for Agents, Not Humans

Agent-readable documentation has specific qualities that differ from documentation written for human teams.

### Be Specific, Not Directional

Human-readable: "The recipe list should be clean and easy to scan."
Agent-readable: "The recipe list displays items in a vertical stack. Each item shows: recipe name (heading, one line, truncate with ellipsis), cuisine tag (pill badge, right-aligned), prep time (secondary text below the name). Items are sorted alphabetically by default. Empty state shows a centered illustration and the text 'No recipes yet. Add your first one.'"

The first version gives a human enough direction to make good design decisions. The second version gives an agent enough specificity to implement without guessing.

### Use Version Headers

Every design document should have a version number at the top. When you update a document, increment the version. This lets the agent (and you) know which version is current and whether the document has been updated since it was last read.

```markdown
# Product Requirements Document
> Version 2.1 -- Updated 2026-03-15
```

### Cross-Reference Everything

Documents should reference each other explicitly. If the UX spec describes a screen that shows data from an API endpoint, it should name that endpoint and link to the API contract:

```markdown
The recipe detail screen loads data from `GET /api/recipes/{id}`
(see contracts/openapi.yaml, RecipeDetail schema).
```

This prevents the agent from inventing an endpoint that does not exist or using a response shape that does not match the contract.

### Include Acceptance Criteria

For every feature or screen, state what "done" looks like. This gives the agent a concrete target and gives you a concrete checklist for review.

```markdown
### Recipe Scaling

**Acceptance criteria:**
- User can select a serving size from 1 to 20 via a numeric stepper
- All ingredient quantities recalculate proportionally on change
- Fractional quantities display as fractions (1/2, 1/3, 3/4), not decimals
- The original serving size is shown as the default
- Scaling does not modify the stored recipe
```

### State Non-Goals Explicitly

An agent will try to build a complete feature. If you do not want social sharing in the MVP, say so in the PRD:

```markdown
## Non-Goals (MVP)
- Social features (recipe sharing, commenting, following)
- Nutritional analysis or calorie counting
- AI-generated recipe suggestions
- Multi-language support
```

Without this, an agent may add a "Share" button because it seems like a natural feature for a recipe app. Non-goals are boundaries.

## 3.4 PRD: The Product Requirements Document

The PRD answers: what are we building, who is it for, and what must it do?

### Structure

A good PRD has these sections:

**Vision** (1 paragraph). The elevator pitch. What the product is and why it exists.

**Target Persona** (3-5 sentences). Who the user is, what they care about, what frustrates them. This shapes every feature and UX decision downstream.

**Core Features** (the bulk of the document). Each feature gets:
- A unique identifier (e.g., F-01, F-02) for cross-referencing
- A description of what it does, from the user's perspective
- Acceptance criteria
- Priority (must-have, should-have, nice-to-have)

**Content Policy** (if applicable). What content is allowed, what is not, how moderation works. This is especially important for AI-powered products.

**Constraints** (5-15 items). Technical or business constraints that affect all features. Examples: "Must run on ARM64," "Must support offline use," "Maximum API latency of 500ms."

**Non-Goals** (5-10 items). What this product explicitly does not do, at least for the MVP. Prevents scope creep.

### PRD Quality Checklist

- [ ] Every feature has a unique identifier
- [ ] Every feature has acceptance criteria
- [ ] Priorities are assigned and consistent
- [ ] Non-goals are stated explicitly
- [ ] The target persona is specific enough to make design decisions against
- [ ] Constraints include technical, budget, and timeline considerations
- [ ] The document is versioned

### A Note on Completeness

The PRD does not need to describe every edge case. It needs to describe every feature and its expected behavior clearly enough that the architecture and UX spec authors can ask the right follow-up questions. Trying to make the PRD exhaustive leads to a 50-page document that no one (human or agent) reads carefully.

## 3.5 Architecture Document

The architecture document translates PRD requirements into technical decisions. It answers: how do the systems connect?

### Decisions, Not Debates

A critical principle: the architecture document records decisions. It does not present options. By the time this document exists, the human has chosen the tech stack, the deployment model, the data storage approach, and the communication patterns. The agent implements decisions. It does not evaluate tradeoffs.

If you are unsure about a decision, use the agent as a thought partner in conversation. Ask it to present tradeoffs. But once you decide, the architecture doc records the decision as settled fact.

### Structure

**System Overview** (diagram or description). What systems exist, how they communicate. Even a text description of "Frontend sends HTTP requests to Backend. Backend reads/writes PostgreSQL. Backend calls external LLM API" is better than nothing.

**Tech Stack** (table). Every technology choice, with version numbers where they matter.

**Data Model** (entity descriptions). What entities exist, what fields they have, how they relate. This does not need to be a full database schema -- it needs to be detailed enough that the agent can design the schema.

```markdown
### Entities

**Recipe**
- id (UUID, primary key)
- user_id (FK to User)
- title (string, max 200 chars)
- description (text, optional)
- servings (integer, default 4)
- prep_time_minutes (integer, nullable)
- cook_time_minutes (integer, nullable)
- created_at, updated_at (timestamps)

**Ingredient**
- id (UUID, primary key)
- recipe_id (FK to Recipe)
- name (string, max 100 chars)
- quantity (decimal)
- unit (enum: cup, tbsp, tsp, oz, g, kg, lb, ml, l, piece, pinch)
- order (integer, for display ordering)
```

**API Design** (high-level). REST vs GraphQL, authentication mechanism, pagination strategy, error format. The formal API contract (OpenAPI) comes next, but the architecture doc establishes the patterns.

**Deployment Architecture**. Where things run, how they are built, how they are deployed. Docker Compose for local development, container registry for CI/CD, target hosting platform.

**Constraints and Invariants**. Technical rules that must hold across the entire system. Examples:
- "All timestamps are stored in UTC"
- "All IDs are UUIDs v4"
- "Database migrations are forward-only; never modify an existing migration"

### Architecture Quality Checklist

- [ ] Every technology choice is decided, not "TBD"
- [ ] Data model covers all entities needed by PRD features
- [ ] API design patterns are specified (REST, auth, errors, pagination)
- [ ] Deployment architecture is defined for both local dev and production
- [ ] System boundaries are clear (what talks to what, how)
- [ ] Constraints and invariants are documented

## 3.6 UX Specification

The UX spec defines every screen, every interaction, and every edge case. If the PRD says "users can manage recipes," the UX spec says exactly how: what the list looks like, what happens when you tap an item, what the edit form contains, what happens when you delete, what the empty state shows.

### Why This Level of Detail?

Because agents cannot look at a Figma file. They cannot intuit what "clean and modern" means for your specific product. They will produce something, and without a detailed UX spec, that something will be a generic default that you spend hours tweaking.

A detailed UX spec does not mean a long one. It means a precise one. For each screen, specify:

**Layout** -- What elements appear, in what order, in what arrangement.

**Content** -- Exact labels, placeholder text, empty states, error messages. If the button says "Add Recipe," write "Add Recipe" in the spec, not "a button to add recipes."

**Behavior** -- What happens on tap/click, what loads, what animates, what the loading state looks like, what happens on error.

**Responsive considerations** -- If the product has a UI, how does it adapt to different screen sizes? At minimum, define mobile (375px) and desktop (1280px) behaviors.

**Edge cases** -- Empty states, error states, long content truncation, maximum limits.

### Example: Recipe List Screen

```markdown
## 2.1 Recipe List (authenticated)

**Route**: /recipes

**Layout**: Vertical scrolling list. Top bar with app title (left) and "Add"
button (right, icon + text). Search field below the top bar (full width, with
magnifying glass icon and placeholder "Search recipes..."). Recipe cards in a
vertical stack below search.

**Recipe card**: Full width. Displays:
- Recipe title (heading, single line, ellipsis overflow at 40 characters)
- Cuisine tag (pill badge, top right of card)
- Prep time in minutes (secondary text, format: "25 min prep")
- Cook time in minutes (secondary text, format: "45 min cook")

**Sorting**: Alphabetical by title (default). Sort menu accessible via icon
button in top bar. Options: Alphabetical, Recently Added, Prep Time.

**Empty state**: Centered illustration (placeholder), heading "No recipes yet",
body text "Add your first recipe to get started", primary button "Add Recipe"
that navigates to the create form.

**Error state**: If the recipe list fails to load, show a centered error message
with a "Try Again" button. Do not show a blank screen.

**Loading state**: Skeleton cards (3) matching the recipe card layout.
```

This level of detail means the agent produces something close to correct on the first try. Without it, you are reviewing and correcting the layout, the copy, the behavior, the edge cases -- each one a round-trip.

### UX Spec Quality Checklist

- [ ] Every screen has a route/URL
- [ ] Every screen describes layout, content, and behavior
- [ ] Every interactive element specifies what happens on interaction
- [ ] Empty states, loading states, and error states are defined
- [ ] Copy is exact (labels, placeholders, messages), not described
- [ ] Responsive behavior is specified for at least two breakpoints
- [ ] Cross-references PRD feature identifiers
- [ ] Cross-references brand identity for colors, typography, spacing

## 3.7 API Contract (OpenAPI)

The API contract is the formal interface between frontend and backend. It is not a design document -- it is a specification that both sides implement against. This distinction matters.

### Define Before Implement

Write the OpenAPI YAML before either side writes implementation code. This seems backwards ("how can I define the API before I know what the code looks like?") but it is the most important sequencing decision in multi-agent development.

Without a contract:
- The backend agent invents response shapes based on the data model
- The frontend agent invents request shapes based on the UX spec
- They do not match
- You spend hours debugging integration failures

With a contract:
- Both agents implement against the same spec
- Mismatches are caught by contract validation, not by manual testing
- Changes go through a governance process, not unilateral edits

### Contract Governance

Rules for managing the API contract:

1. **The contract lives in `contracts/openapi.yaml`.** Not in docs/, not inline in code.
2. **Neither agent modifies it unilaterally.** If an agent needs a contract change, it documents the need in its state file. The human reviews and updates the contract.
3. **The contract is versioned.** Use the `info.version` field in the OpenAPI spec.
4. **Deviations are tracked.** If an agent must deviate from the contract during implementation (e.g., an enum value the contract does not define), it documents the deviation. These are reconciled before the next phase.

### What to Specify

A useful API contract covers:

**Endpoints** -- Every route, method, path parameters, and query parameters.

**Request bodies** -- Schema for POST/PUT/PATCH requests, with field types, required fields, and validation constraints.

**Response schemas** -- Shape of successful responses (200, 201) and error responses (400, 404, 422, 500).

**Authentication** -- How auth is handled (cookie, bearer token, API key) and which endpoints require it.

**Pagination** -- Pattern for paginated endpoints (cursor-based, offset-based), with response envelope.

**Common patterns** -- Error response shape, timestamp format, ID format, enum values.

### Example: Minimal OpenAPI Stub

```yaml
openapi: 3.1.0
info:
  title: RecipeVault API
  version: 0.1.0
  description: Backend API for the RecipeVault recipe management application.

servers:
  - url: http://localhost:8000
    description: Local development

paths:
  /health:
    get:
      summary: Health check
      operationId: healthCheck
      responses:
        '200':
          description: Service is healthy
          content:
            application/json:
              schema:
                type: object
                properties:
                  status:
                    type: string
                    example: ok

  /api/recipes:
    get:
      summary: List recipes for the authenticated user
      operationId: listRecipes
      security:
        - cookieAuth: []
      parameters:
        - name: sort
          in: query
          schema:
            type: string
            enum: [title, created_at, prep_time]
            default: title
        - name: search
          in: query
          schema:
            type: string
      responses:
        '200':
          description: List of recipes
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/RecipeSummary'
        '401':
          $ref: '#/components/responses/Unauthorized'

components:
  schemas:
    RecipeSummary:
      type: object
      required: [id, title, servings, created_at]
      properties:
        id:
          type: string
          format: uuid
        title:
          type: string
          maxLength: 200
        cuisine_tag:
          type: string
          nullable: true
        prep_time_minutes:
          type: integer
          nullable: true
        cook_time_minutes:
          type: integer
          nullable: true
        servings:
          type: integer
        created_at:
          type: string
          format: date-time

  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            type: object
            properties:
              detail:
                type: string
                example: Not authenticated

  securitySchemes:
    cookieAuth:
      type: apiKey
      in: cookie
      name: session_token
```

This is a starting point, not the full contract. It establishes the patterns (response shapes, error format, auth mechanism) that the rest of the API follows.

## 3.8 Brand / Design Direction

Any project with a user interface needs a brand direction document. Without one, the agent produces output that looks like every other default Tailwind/shadcn application: gray backgrounds, blue buttons, system fonts. If that is what you want, skip this section. If you want your product to have a distinct identity, this document is required.

### At Minimum

Even a brief brand direction is better than none:

**Color palette** -- Primary, secondary, accent, background, and surface colors. Provide exact hex codes or CSS custom properties, not descriptions like "a warm blue."

**Typography** -- Heading font, body font, UI font (for buttons, labels). Specify the actual typeface names and where to load them from.

**Spacing scale** -- Base unit and scale. Even "use a 4px base grid" is enough to prevent spacing chaos.

**Voice and tone** -- How the product communicates. Formal or casual? Concise or verbose? This affects every label, error message, and empty state.

### Design Tokens

The most effective approach is to define a set of CSS custom properties (design tokens) that the agent uses instead of raw values:

```css
:root {
  --color-bg-primary: #1a1a2e;
  --color-bg-surface: #232340;
  --color-text-primary: #e8e6f0;
  --color-text-secondary: #a09cb0;
  --color-accent: #c4536a;

  --font-display: 'Cormorant Garamond', serif;
  --font-body: 'Source Serif 4', serif;
  --font-ui: 'Inter', sans-serif;

  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;

  --radius-sm: 0.25rem;
  --radius-md: 0.5rem;
  --radius-lg: 1rem;
}
```

When the agent uses `var(--color-accent)` instead of hardcoding `#c4536a`, you can change the accent color in one place and it propagates everywhere. More importantly, it prevents the agent from inventing colors that are not in your palette.

### Anti-Generic Checklist

If your product has a distinct identity, include a checklist of things the agent must never do:

```markdown
## Anti-Generic Checklist

Before marking any UI work as complete, verify:
- [ ] No framework default colors (no bg-gray-*, no bg-zinc-*, no text-gray-*)
- [ ] Correct typefaces applied (headings use display font, body uses body font)
- [ ] Spacing uses design tokens, not arbitrary values
- [ ] No placeholder copy ("Lorem ipsum", "Click here", "Untitled")
- [ ] Empty states have product-specific illustrations or copy, not generic icons
```

This checklist is also a candidate for a Claude Code skill or rule, which we cover in Chapter 04.

## 3.9 The Doc-Review Skill

At this stage, you have produced several substantial documents. This is a good time to build your first custom Claude Code skill: a doc-review skill that checks each spec for completeness and consistency.

### Why a Skill?

You could review the docs manually. But a skill encodes your review criteria so that the agent can self-check before presenting docs for your review. This catches obvious gaps (missing acceptance criteria, unversioned documents, broken cross-references) before they waste your time.

### What the Skill Checks

A doc-review skill should verify:

- Every document has a version header
- Every PRD feature has an identifier and acceptance criteria
- The architecture doc has no "TBD" entries
- The UX spec references PRD feature identifiers
- The UX spec defines empty, loading, and error states for every screen
- The API contract is valid OpenAPI (use a linter)
- Cross-references between documents resolve to real sections
- Non-goals are stated in the PRD

### Skill Definition Example

Create `.claude/skills/doc-review.md`:

```markdown
# Doc Review Skill

Review all specification documents in docs/ and contracts/ for completeness
and consistency.

## Steps

1. Read each document in docs/ and contracts/openapi.yaml
2. For each document, check:
   - Has a version header (e.g., "Version X.Y")
   - No "TBD", "TODO", or placeholder sections
3. For docs/prd.md:
   - Every feature has a unique identifier (F-XX)
   - Every feature has acceptance criteria
   - Non-goals section exists and is non-empty
4. For docs/architecture.md:
   - Tech stack table has no TBD entries
   - Data model covers entities referenced in PRD features
   - Deployment architecture is defined
5. For docs/ux-spec.md:
   - Every screen has a route
   - Every screen defines layout, behavior, empty state, error state
   - Cross-references PRD feature identifiers
6. For contracts/openapi.yaml:
   - Valid OpenAPI 3.x (run openapi-lint if available)
   - Every endpoint has request/response schemas
   - Error responses are defined
7. For docs/brand-identity.md (if exists):
   - Color palette has hex codes, not descriptions
   - Typography specifies actual typeface names
8. Report findings organized by document, with specific issues and suggestions.
```

This skill pays for itself the first time it catches a missing error state or an unresolved cross-reference.

## 3.10 Common Mistakes

### Specs That Are Too Vague to Implement Against

"The user can manage their recipes" is a feature description, not a spec. What does "manage" mean? Create, read, update, delete? What does the list look like? What happens on delete -- immediate or confirmation dialog? What about recipes with scheduled meal plans -- can those be deleted? Vague specs produce code that works but does not match your intent.

### Skipping the API Contract

"We'll figure out the API as we go." This works with a single developer who controls both sides. It does not work with two agents (or an agent and a human) implementing independently. The contract is the coordination mechanism. Without it, integration is a negotiation.

### Not Versioning Documents

You update the PRD to add a new feature. The architecture doc still references the old feature list. The agent reads the architecture doc and implements against stale requirements. Version headers and a disciplined update process prevent this. When you update one document, check whether downstream documents need updates.

### Treating All Docs as Immutable

The PRD is directional. The UX spec is detailed. The architecture doc records decisions. All of these can change as you learn more during implementation. The exception is the API contract: once agents start implementing against it, changes must go through governance. The contract is the contract. The rest are living documents.

### Writing Docs the Agent Never Reads

If a document exists but CLAUDE.md does not point to it, the agent may not find it. Every design document should be referenced in CLAUDE.md's "Design Documents" section with its file path and a one-line description.

### Gold-Plating the Specs

You spend two weeks writing a 100-page PRD with every conceivable edge case. Meanwhile, you have not written a line of code and you have no idea if your core assumptions are correct. Specs should be thorough enough to implement against, not so thorough that they delay implementation indefinitely. Start with the MVP features. Add detail for the features you are building next. Leave future features as stubs.

### Inconsistent Terminology

The PRD calls it a "recipe." The architecture doc calls it a "dish." The UX spec calls it a "meal." The agent implements three different models. Pick one term per concept and use it everywhere. Add a glossary to the PRD if the domain has any ambiguity.

---

## What the Agent Should Do

If you are an AI agent executing the specification phase, here is your workflow:

1. **Read the interview summary and CLAUDE.md.** These are your inputs. Everything you produce must be consistent with them.

2. **Produce documents in cascade order.** PRD first, then architecture, then UX spec, then API contract, then brand identity (if the project has a UI). Do not skip ahead. Each document depends on the ones before it.

3. **Use the templates.** If templates exist in `templates/docs/`, start from them. Do not invent your own structure. The templates encode the quality criteria described in this chapter.

4. **Be specific.** Replace every vague phrase with a concrete specification. "Display the user's recipes" becomes "Display a vertical scrolling list of recipe cards, each showing title (heading, single line, ellipsis at 40 chars), cuisine tag (pill badge), and prep time (secondary text, format '25 min prep')."

5. **Cross-reference aggressively.** Every UX screen should reference the PRD feature it implements. Every API endpoint should reference the UX screen that consumes it. Every data model should reference the PRD features it supports. Broken cross-references are broken context.

6. **Version everything.** Every document gets a version header. When you update a document, increment the version.

7. **State what is NOT included.** Non-goals in the PRD. "Not in MVP" markers on features. "Out of scope" notes on architectural decisions. The absence of a boundary is an invitation to scope creep.

8. **Validate the API contract.** Run an OpenAPI linter if available. Verify that every endpoint has defined request and response schemas. Verify that error responses are consistent.

9. **Build the doc-review skill.** Create `.claude/skills/doc-review.md` with the checklist from Section 3.9. Run it against your own output before presenting it for human review.

10. **Commit each document separately.** One commit per document, with a clear commit message. This makes review easier and provides clean rollback points.

11. **Present a summary.** When all documents are complete, tell the human: what was produced, what decisions were made, what questions remain, and what the recommended next step is (usually: human reviews all specs before implementation begins).

If a decision point arises that the existing context does not resolve -- for example, the interview summary does not specify whether the app should support multiple users or be single-user -- stop and ask the human. Do not make the decision yourself and bury it in a document. Surface it clearly: "The interview summary does not specify X. This affects Y and Z. Which do you prefer?"

---

Next: Chapter 04 -- Configuring the Claude Code Harness *(coming soon)*
