# Beacon -- Brand Identity and Design System

<!-- WHY THIS DOCUMENT EXISTS:
AI coding agents produce visually functional UIs that all look the same. Without a
brand identity document, every agent-built app converges on gray cards, Inter font,
rounded-lg everything, and p-4 gap-4 spacing. This document defines what makes YOUR
product visually distinct and gives agents concrete rules to follow.

HOW TO USE THIS TEMPLATE:
1. Every section heading below represents a category your brand identity MUST address.
   Do not skip sections -- even brief coverage is better than silence. An agent that
   sees no guidance on corner radii will apply rounded-lg everywhere.
2. [CUSTOMIZE] markers indicate where to replace Beacon's example content with your own.
3. Beacon is a utilitarian productivity tool, so its brand content is intentionally
   restrained. If your product has a stronger visual personality (consumer apps, creative
   tools, editorial products), expand each section well beyond what Beacon demonstrates.
4. Keep Section 1 (antipatterns) and Section 11 (checklist) -- they are universal. -->

## Document Header

| Field          | Value           |
|----------------|-----------------|
| Version        | v1.0            |
| Date           | 2025-01-15      |
| Author         | [CUSTOMIZE]     |
| Change Summary | Initial version |

### Document Coverage

Every brand identity document should address these categories. Check each off as you
complete it. If a section does not apply to your product, state why -- do not silently
omit it.

- [ ] Antipattern awareness (Section 1)
- [ ] Brand direction and positioning (Section 2)
- [ ] Color system with approved pairings (Section 3)
- [ ] Typography with type scale (Section 4)
- [ ] Spacing and layout (Section 5)
- [ ] Visual language: radii, elevation, borders (Section 6)
- [ ] Iconography (Section 7)
- [ ] Imagery and illustration (Section 8)
- [ ] Motion, animation, and loading states (Section 9)
- [ ] Voice and tone (Section 10)
- [ ] Anti-generic checklist (Section 11)

---

## Section 1: Why AI-Coded Apps Look Generic

Before defining what Beacon should look like, we must catalog what it should NOT look
like. These five antipatterns appear in virtually every AI-coded application. Recognizing
them is the first step to avoiding them.

### 1.1 Tailwind Default Syndrome

The agent uses the same utility classes on every component:

- `rounded-lg` on buttons, cards, inputs, avatars, modals -- all identical radius
- `bg-gray-50` and `bg-gray-100` as the only surface colors
- `p-4 gap-4` as universal spacing -- everything 16px apart, zero rhythm
- `shadow-sm` on every elevated surface
- `text-gray-500` as the only secondary text color

**Why it happens:** Agents optimize for "working correctly" not "looking intentional."
Tailwind defaults are safe -- they never look broken, so agents never move past them.

### 1.2 Typography Flatness

- System font or Inter everywhere -- headings, body, labels, buttons, all the same face
- Two sizes: "normal" and "a bit bigger"
- No weight variation (everything is `font-medium`)
- No letter-spacing, no line-height differences, no typographic hierarchy
- Headings look like body text that got bigger

**Why it happens:** Agents treat typography as content delivery, not as a design element.
They size text to fit, not to create visual hierarchy.

### 1.3 Layout Monotony

- Everything in a CSS grid of equal-width cards
- All content centered in the viewport
- Same gap between every element on the page
- No asymmetry, no sidebar variation, no intentional whitespace
- Mobile layout is just the desktop layout reflowed into a single column

**Why it happens:** Grid layouts are the easiest to get right. Agents avoid asymmetry
because it is harder to make responsive.

### 1.4 Missing Personality

- Generic button text: "Submit", "Cancel", "Save", "Delete"
- Empty states: "No items found" with a gray icon
- Loading: centered spinner, nothing else
- Hover effects: lighter background color, nothing more
- No transitions, no motion, no delight anywhere

**Why it happens:** Personality requires understanding the product and its users. Agents
do not have that context unless you provide it explicitly in this document.

### 1.5 Dark Mode Failures

- Inverted light mode (swap white for near-black, call it done)
- All dark surfaces are the same shade -- no elevation hierarchy
- Pure white (#FFF) text on pure dark (#000) backgrounds -- harsh and fatiguing
- Accent colors at full saturation on dark backgrounds (vibrant to the point of glowing)
- Borders either invisible or too prominent

**Why it happens:** Agents apply dark mode as a color swap, not as a rethinking of
elevation, contrast, and visual weight.

---

## Section 2: Brand Direction

<!-- [CUSTOMIZE] Define the visual identity of your product. Be concrete -- adjectives
without examples are useless. Products with a strong visual personality (consumer apps,
creative tools, editorial products) should expand each subsection significantly. -->

### 2.1 Brand Essence

**[CUSTOMIZE]** Distill your product's visual identity into one sentence. This is the
anchor that every other decision in this document references.

**Beacon:** Clean productivity for small teams -- focused, fast, no visual noise.

### 2.2 Brand Attributes

| Attribute    | Beacon IS                               | Beacon IS NOT                     |
|--------------|-----------------------------------------|-----------------------------------|
| Mood         | Focused, calm, confident                | Playful, whimsical, heavy         |
| Density      | Compact but breathable                  | Cramped or wasteful               |
| Color        | Cool neutrals with a sharp accent       | Warm and cozy OR cold and sterile |
| Typography   | Modern, clean, hierarchy through weight | Decorative, serif, or monospaced  |
| Interactions | Responsive, quick, purposeful           | Bouncy, slow, or theatrical       |

### 2.3 Target Audience Aesthetic

**[CUSTOMIZE]** Describe your target user's visual taste. What adjacent products and
aesthetics do they already find appealing? This tells agents what "on-brand" feels like
to the people who will actually use the product.

Beacon's users are engineers who appreciate Linear, GitHub, and VS Code. They value
density and keyboard navigation over visual polish. They distrust products that feel
"designed" over "functional." Their aesthetic is developer-tool minimalism.

### 2.4 Competitive Visual Positioning

**[CUSTOMIZE]** Map your direct competitors and state how your product looks different.
This table prevents agents from accidentally reproducing a competitor's visual language.

| Competitor | Their Look                             | Our Differentiation                                |
|------------|----------------------------------------|----------------------------------------------------|
| Linear     | Cool, spacious, keyboard-first         | Similar density, warmer accent, more compact lists |
| Jira       | Enterprise, toolbar-heavy, blue        | Dramatically simpler chrome, no toolbars           |
| Notion     | Playful, emoji-heavy, whitespace       | No decorative elements, information-dense          |
| Asana      | Colorful, friendly, illustration-heavy | No illustrations, no color-coding by default       |

**Design references:** Linear (density and keyboard focus), Vercel (typography and spacing),
Raycast (dark UI with clear hierarchy).

---

## Section 3: Color System

<!-- [CUSTOMIZE] Replace with your product's actual color tokens. Define the semantic
role of each color, not just its hex value. Include contrast ratios for every text/background
pairing your product uses -- this is what prevents accessibility failures. -->

### 3.1 Core Palette

```css
:root {
    /* Background hierarchy (darkest to lightest) */
    --color-bg-base: #0C0D11; /* Page background */
    --color-bg-elevated: #14161E; /* Cards, panels */
    --color-bg-surface: #1C1F2A; /* Inputs, hover states */
    --color-bg-overlay: #252836; /* Dropdowns, modals */

    /* Text hierarchy */
    --color-text-primary: #E4E4E8; /* Headings, important content */
    --color-text-secondary: #8E8E9A; /* Descriptions, metadata */
    --color-text-tertiary: #5C5C6A; /* Placeholders, disabled */

    /* Accent */
    --color-accent: #5B7FFF; /* Primary actions, links, focus rings */
    --color-accent-hover: #7B9AFF; /* Hover state for accent elements */
    --color-accent-subtle: #5B7FFF1A; /* Accent backgrounds (10% opacity) */

    /* Semantic */
    --color-success: #34D399;
    --color-warning: #FBBF24;
    --color-error: #F87171;
    --color-info: #60A5FA;
}
```

### 3.2 Approved Color Pairings

<!-- [CUSTOMIZE] List every foreground/background combination your product uses. Run a
contrast checker (e.g., WebAIM) on each pairing. This table prevents agents from creating
ad-hoc color combinations that may fail accessibility requirements. -->

| Foreground         | Background       | Contrast | Usage                     | WCAG AA      |
|--------------------|------------------|----------|---------------------------|--------------|
| `--text-primary`   | `--bg-base`      | 15.4:1   | Primary body text         | Pass         |
| `--text-primary`   | `--bg-elevated`  | 13.1:1   | Text in cards/panels      | Pass         |
| `--text-secondary` | `--bg-base`      | 7.8:1    | Metadata on base          | Pass         |
| `--text-secondary` | `--bg-elevated`  | 6.6:1    | Metadata in cards         | Pass         |
| `--text-tertiary`  | `--bg-surface`   | 3.4:1    | Placeholders (decorative) | Exempt       |
| `--color-accent`   | `--bg-base`      | 5.2:1    | Accent text on base       | Pass         |
| `#FFFFFF`          | `--color-accent` | 4.6:1    | Button labels on accent   | Pass (large) |

**Rule:** Do not create pairings outside this table. If a new pairing is needed, add it
here with a verified contrast ratio first.

### 3.3 Banned Colors

Zero instances of these Tailwind defaults anywhere in the codebase:
`bg-gray-*`, `bg-zinc-*`, `bg-slate-*`, `bg-neutral-*`,
`text-gray-*`, `text-zinc-*`, `text-slate-*`, `text-neutral-*`,
`border-gray-*`, `border-zinc-*`, `border-slate-*`

Use `tokens.css` custom properties exclusively.

---

## Section 4: Typography

<!-- [CUSTOMIZE] Specify your actual font stack. Explain WHEN each typeface is used.
If your product has a distinct typographic personality, use different typefaces for display
and body -- and document why each was chosen. -->

| Role    | Typeface       | Weights  | Usage                         |
|---------|----------------|----------|-------------------------------|
| Display | Inter          | 600, 700 | Page titles, section headers  |
| Body    | Inter          | 400, 500 | Descriptions, content, labels |
| Mono    | JetBrains Mono | 400      | Code, IDs, timestamps         |

**[CUSTOMIZE]** If your product has a distinct typographic personality, use different
typefaces for display and body. Beacon uses Inter throughout because its brand is
utilitarian -- typography personality comes from weight and spacing variation, not
typeface contrast.

### Type Scale

| Token         | Size | Line Height | Weight | Usage                   |
|---------------|------|-------------|--------|-------------------------|
| `--text-2xl`  | 24px | 32px        | 600    | Page titles             |
| `--text-xl`   | 20px | 28px        | 600    | Section headers         |
| `--text-lg`   | 16px | 24px        | 500    | Card titles, emphasis   |
| `--text-base` | 14px | 20px        | 400    | Body text, descriptions |
| `--text-sm`   | 12px | 16px        | 400    | Metadata, timestamps    |
| `--text-xs`   | 11px | 14px        | 500    | Badges, labels          |

Every page must use at least 3 different sizes from this scale.

---

## Section 5: Spacing and Layout

### Spacing Scale

```css
--space-0:

0
px

;
--space-1:

4
px

;
--space-2:

8
px

;
--space-3:

12
px

;
--space-4:

16
px

;
--space-5:

20
px

;
--space-6:

24
px

;
--space-8:

32
px

;
--space-10:

40
px

;
--space-12:

48
px

;
--space-16:

64
px

;
```

**Rule:** Every screen must use at least 3 different spacing values. Uniform `p-4 gap-4`
everywhere is a brand violation.

### Layout Principles

- Content areas use asymmetric spacing (more space above sections than below).
- Group related items with tight spacing; separate sections with generous spacing.
- Sidebar width: 240px (desktop), 56px (collapsed), 0 (mobile).
- Maximum content width: 1200px for list views, uncapped for board views.

---

## Section 6: Visual Language

<!-- [CUSTOMIZE] This section defines HOW components look beyond color and typography.
Corner radii, elevation, borders, and gradients are the details agents most often get
wrong -- they apply uniform values everywhere. Define your rules per component type.

Products with dark UIs need particular attention to elevation: standard drop shadows are
invisible on dark backgrounds, so you must specify alternative strategies (luminance
borders, background color differentiation, subtle inner shadows). -->

### 6.1 Corner Radius Strategy

**[CUSTOMIZE]** Assign different radii to different component types. Uniform radius on
all components is a brand violation (see Section 1.1).

| Component        | Radius        | Rationale                                              |
|------------------|---------------|--------------------------------------------------------|
| Buttons          | 6px           | Sharp, utilitarian -- buttons are tools, not toys      |
| Cards / panels   | 8px           | Slightly softer for content containers                 |
| Inputs           | 6px           | Matches buttons -- inputs and buttons sit side-by-side |
| Modals / dialogs | 12px          | Larger containers get softer corners                   |
| Chips / badges   | 9999px (pill) | Small status elements use pill shape                   |
| Avatars          | 50% (circle)  | Standard for user representations                      |
| Tooltips         | 4px           | Tight, minimal -- tooltips are ephemeral               |

**Rule:** If a PR uses the same `border-radius` on buttons, cards, inputs, AND modals,
it must be revised.

### 6.2 Elevation and Shadows

<!-- [CUSTOMIZE] Define how your product communicates depth. Dark UIs should NOT rely on
Tailwind's shadow-sm/md/lg -- they produce muddy halos on dark backgrounds. Light UIs may
use Tailwind shadows but should still map each level to specific component types. -->

| Level   | Treatment                                                                           | Usage                 |
|---------|-------------------------------------------------------------------------------------|-----------------------|
| Level 0 | No shadow, no border. Flush with `--bg-base`.                                       | Background areas      |
| Level 1 | `1px` border at `rgba(255,255,255,0.06)`                                            | Cards, inputs, panels |
| Level 2 | `1px` border at `rgba(255,255,255,0.08)` + subtle `box-shadow`                      | Dropdowns, popovers   |
| Level 3 | `1px` border at `rgba(255,255,255,0.10)` + `box-shadow: 0 8px 24px rgba(0,0,0,0.4)` | Modals, overlays      |

**Banned on dark surfaces:** Tailwind's `shadow-sm`, `shadow-md`, `shadow-lg` -- these are
calibrated for light backgrounds.

### 6.3 Border Treatments

| Context           | Border                                        | Notes                                                   |
|-------------------|-----------------------------------------------|---------------------------------------------------------|
| Default border    | `rgba(255,255,255,0.06)`, `1px`               | Barely visible, defines edges without drawing attention |
| Divider lines     | Same as default border                        | Used sparingly -- between major sections only           |
| Input (unfocused) | `rgba(255,255,255,0.10)`, `1px`               | Slightly more visible than cards                        |
| Input (focused)   | `--color-accent`, `2px`                       | Accent color signals active state                       |
| Focus rings       | `--color-accent`, `2px outline`, `2px offset` | Use `outline` not `box-shadow` to avoid layout shift    |

### 6.4 Gradients

<!-- [CUSTOMIZE] Define functional gradients only. If your product overlays text on images,
you need a scrim gradient. If your product has no image content, this subsection may be
brief. Decorative gradients (purple-to-blue hero backgrounds) are an AI antipattern. -->

Beacon uses minimal gradients:

- **Scroll fade:** `linear-gradient(to bottom, transparent, --color-bg-base)` at the bottom
  of scrollable lists to indicate more content.
- **No decorative gradients.** Beacon's visual identity is flat and utilitarian.

---

## Section 7: Iconography

<!-- [CUSTOMIZE] Every product with a UI uses icons. Without explicit guidance, agents pick
inconsistent libraries, sizes, and styles -- or mix multiple libraries on the same page.
Define your icon system here. -->

### Icon Library

**Library:** Lucide Icons (lucide.dev)

**Why:** Clean stroke-based icons on a 24px grid. Maintained fork of Feather Icons with
better coverage. NOT Heroicons (signals "Tailwind template"), NOT Font Awesome (too heavy,
mixed styles).

**[CUSTOMIZE]** Choose one library and commit to it. Mixing icon libraries is a brand
violation.

### Icon Sizing

| Context           | Size | Notes                                        |
|-------------------|------|----------------------------------------------|
| Navigation        | 20px | Sidebar and top bar icons                    |
| Inline actions    | 16px | Icons next to text (edit, copy, link)        |
| Empty states      | 40px | Large decorative icons, in `--text-tertiary` |
| Status indicators | 14px | Small inline indicators (priority, type)     |

### Style Rules

- **Stroke weight:** 1.5px (Lucide default). Increase to 1.75px on `--bg-base` if icons
  feel thin against the darkest background.
- **Color:** Icons inherit text color. Never apply accent color to icons unless the icon
  represents an interactive element in its active state.
- **Fill vs. stroke:** Stroke-only by default. Use filled variants only for selected/active
  states (e.g., filled star for "favorited").

---

## Section 8: Imagery and Illustration

<!-- [CUSTOMIZE] This section varies widely by product type. A productivity SaaS may have
minimal imagery. A consumer app may need extensive art direction for photos, illustrations,
or generated images. Define what applies to your product.

At minimum, every product needs: empty state visual treatments and avatar/fallback rules.
Products with richer visual identities should also cover: illustration style, photography
direction, background imagery, and (if applicable) AI-generated content art direction. -->

### 8.1 Empty State Treatments

**[CUSTOMIZE]** Empty states are high-frequency UI moments that agents handle poorly.
Define the visual treatment, not just the copy.

| Context             | Icon                              | Heading                             | Action                 |
|---------------------|-----------------------------------|-------------------------------------|------------------------|
| No tasks in project | `clipboard-list` (40px, tertiary) | "No tasks yet"                      | "Create a task" button |
| No search results   | `search` (40px, tertiary)         | "No results for '{query}'"          | "Clear filters" link   |
| Empty board column  | None                              | "Drag tasks here" (tertiary, small) | None                   |
| No projects         | `folder-plus` (40px, tertiary)    | "Create your first project"         | "New project" button   |

**Layout:** Icon centered above heading, both horizontally centered in the empty container.
Heading uses `--text-secondary` at `--text-base`. Action appears `--space-2` below.

### 8.2 Avatars and User-Generated Content

- **User avatars:** Circle-cropped, 32px in lists, 24px in comments. Fallback: initials
  on `--color-bg-surface` in `--text-secondary`.
- **No illustrations.** Beacon's brand is text-first. Empty states use icons, not
  illustrations.
- **No hero images.** The product is a tool, not a destination.

**[CUSTOMIZE]** Products with richer visual identities should expand this section to cover:
illustration style and library, photography art direction (lighting, subjects, color
grading), and rules for any AI-generated visual content.

---

## Section 9: Motion and Animation

<!-- [CUSTOMIZE] Define your product's motion language. At minimum, specify duration ranges,
easing functions, what animates, and what loading states look like. Products where motion
is a brand pillar (consumer apps, creative tools) should define custom easing curves with
cubic-bezier values and per-component animation tables with exact timing. -->

### 9.1 Transition Rules

- **Duration:** Fast (100ms) for hover states, medium (200ms) for panels and dropdowns,
  slow (300ms) for page transitions. Never exceed 400ms.
- **Easing:** `ease-out` for entrances, `ease-in` for exits, `ease-in-out` for transforms.
- **What animates:** opacity transitions, slide-ins (panels), scale (modals), height changes
  (expanding sections).
- **What does NOT animate:** color changes on text, layout reflows, scroll position.
- **Reduced motion:** Respect `prefers-reduced-motion`. Replace all animations with instant
  state changes.

**[CUSTOMIZE]** If motion is a core part of your brand, define custom easing curves using
`cubic-bezier` values and specify per-component animation tables with exact timing, trigger
events, and easing per animation.

### 9.2 Loading States

<!-- [CUSTOMIZE] Without explicit guidance, agents default to centered spinners or generic
skeleton screens. Define what loading looks like in your product. -->

| Context                      | Treatment                                                                             |
|------------------------------|---------------------------------------------------------------------------------------|
| Page load                    | Skeleton layout matching content shape, pulsing at 1.5s cycle in `--color-bg-surface` |
| Inline action (save, delete) | Button enters disabled state with a 16px spinner replacing the icon                   |
| Data table loading           | Skeleton rows matching column widths, 5 placeholder rows                              |
| Async search                 | Input shows a small spinner in the trailing icon position                             |

**[CUSTOMIZE]** Some products deliberately avoid skeleton screens in favor of atmospheric
or branded loading treatments. If yours does, state it explicitly and define the alternative.

---

## Section 10: Voice and Tone

<!-- [CUSTOMIZE] Define how your product speaks. This guides agents when they write button
labels, error messages, empty states, tooltips, and all other user-facing text. -->

- **Concise:** "Task created" not "Your task has been successfully created!"
- **Specific:** "Title is required" not "Please fill in all required fields."
- **Confident:** "Delete task" not "Are you sure you want to delete this task?"
  (Use a confirmation dialog, but the button label is direct.)
- **No AI language** (unless AI is the product): avoid "generate", "model", "prompt",
  "AI-powered" in user-facing text.
- **No corporate filler:** avoid "leverage", "streamline", "empower", "unlock".

Button label examples:

- "Create task" (not "Submit")
- "Save changes" (not "Update")
- "Remove from project" (not "Delete")
- "Sign in" (not "Login")

---

## Section 11: Anti-Generic Checklist

Run every item against each component or page. All Typography, Color, Layout, and Visual
Language items must pass. Interaction and Voice items should pass but can be deferred
with justification.

### Typography (7 items)

1. [ ] At least 3 distinct font sizes are used on this screen.
2. [ ] At least 2 distinct font weights are visible.
3. [ ] Letter-spacing or tracking varies between headings and body.
4. [ ] Line-height differs between headings and body text.
5. [ ] No text uses Tailwind default `text-gray-*` colors.
6. [ ] Heading hierarchy is visually clear without relying on size alone.
7. [ ] Monospace font is used for code, IDs, or timestamps (where applicable).

### Color (6 items)

8. [ ] Zero instances of banned Tailwind default color utilities.
9. [ ] Accent color appears in 1-2 focal points per screen, not everywhere.
10. [ ] Body text contrast is 4.5:1 or higher (WCAG AA).
11. [ ] Surface colors create 3+ distinct elevation levels.
12. [ ] Interactive elements have visible hover, focus, and active states.
13. [ ] Every text/background pairing exists in the approved pairings table.

### Layout (5 items)

14. [ ] At least 3 different spacing values used on this screen.
15. [ ] Related items are visually grouped (tighter spacing within, more between).
16. [ ] Layout is NOT a centered column of uniform-width cards.
17. [ ] Mobile and desktop layouts differ meaningfully.
18. [ ] Intentional whitespace exists (some areas are dense, some breathe).

### Visual Language (4 items)

19. [ ] Corner radii vary by component type (not uniform across all elements).
20. [ ] Elevation is communicated through the defined system (not ad-hoc shadows).
21. [ ] Focus rings use the specified treatment (not browser defaults).
22. [ ] Icons are from the designated library at the specified sizes.

### Interaction (4 items)

23. [ ] Button labels are specific to their action.
24. [ ] At least one micro-interaction exists (hover, transition, animation).
25. [ ] Loading states match the defined treatment (not generic spinners).
26. [ ] Empty states include a visual treatment and a suggested next action.

### Voice (3 items)

27. [ ] No user-facing text uses forbidden terms (AI, generate, model, prompt).
28. [ ] Error messages are specific and actionable.
29. [ ] Placeholder text is realistic and helpful.

### Visual Verification (3 items)

30. [ ] Page is visually distinguishable from a competitor's equivalent page.
31. [ ] Brand is evident even with the logo hidden.
32. [ ] No clipping, overflow, or collapse at 375px and 1280px viewports.

**Minimum passing score:** 27/32. All Typography, Color, Layout, and Visual Language
items are mandatory.
