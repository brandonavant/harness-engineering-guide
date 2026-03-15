# Beacon -- Brand Identity and Design System

<!-- WHY THIS DOCUMENT EXISTS:
AI coding agents produce visually functional UIs that all look the same. Without a
brand identity document, every agent-built app converges on gray cards, Inter font,
rounded-lg everything, and p-4 gap-4 spacing. This document defines what makes YOUR
product visually distinct and gives agents concrete rules to follow.

[CUSTOMIZE] Replace Section 2-7 with your product's actual brand. Keep Section 1
(anti-patterns) and Section 8 (checklist) -- they are universal. -->

## Document Header

| Field | Value |
|-------|-------|
| Version | v1.0 |
| Date | 2025-01-15 |
| Author | [CUSTOMIZE] |
| Change Summary | Initial version |

---

## Section 1: Why AI-Coded Apps Look Generic

Before defining what Beacon should look like, we must catalog what it should NOT look
like. These five anti-patterns appear in virtually every AI-coded application. Recognizing
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
without examples are useless. Show what the brand IS and what it IS NOT. -->

**Beacon's visual identity: clean productivity, not corporate enterprise.**

| Attribute | Beacon IS | Beacon IS NOT |
|-----------|-----------|---------------|
| Mood | Focused, calm, confident | Playful, whimsical, heavy |
| Density | Compact but breathable | Cramped or wasteful |
| Color | Cool neutrals with a sharp accent | Warm and cozy OR cold and sterile |
| Typography | Modern, clean, hierarchy through weight | Decorative, serif, or monospaced |
| Interactions | Responsive, quick, purposeful | Bouncy, slow, or theatrical |

**Design references:** Linear (density and keyboard focus), Vercel (typography and spacing),
Raycast (dark UI with clear hierarchy). NOT: Notion (too playful), Jira (too enterprise).

## Section 3: Color System

<!-- [CUSTOMIZE] Replace with your product's actual color tokens. Define the semantic
role of each color, not just its hex value. -->

### Core Palette

```css
/* Background hierarchy (darkest to lightest) */
--color-bg-base:      #0C0D11;    /* Page background */
--color-bg-elevated:  #14161E;    /* Cards, panels */
--color-bg-surface:   #1C1F2A;    /* Inputs, hover states */
--color-bg-overlay:   #252836;    /* Dropdowns, modals */

/* Text hierarchy */
--color-text-primary:   #E4E4E8;  /* Headings, important content */
--color-text-secondary: #8E8E9A;  /* Descriptions, metadata */
--color-text-tertiary:  #5C5C6A;  /* Placeholders, disabled */

/* Accent */
--color-accent:         #5B7FFF;  /* Primary actions, links, focus rings */
--color-accent-hover:   #7B9AFF;  /* Hover state for accent elements */
--color-accent-subtle:  #5B7FFF1A; /* Accent backgrounds (10% opacity) */

/* Semantic */
--color-success:  #34D399;
--color-warning:  #FBBF24;
--color-error:    #F87171;
--color-info:     #60A5FA;
```

### Banned Colors

Zero instances of these Tailwind defaults anywhere in the codebase:
`bg-gray-*`, `bg-zinc-*`, `bg-slate-*`, `bg-neutral-*`,
`text-gray-*`, `text-zinc-*`, `text-slate-*`, `text-neutral-*`,
`border-gray-*`, `border-zinc-*`, `border-slate-*`

Use `tokens.css` custom properties exclusively.

## Section 4: Typography

<!-- [CUSTOMIZE] Specify your actual font stack. Explain WHEN each typeface is used. -->

| Role | Typeface | Weights | Usage |
|------|----------|---------|-------|
| Display | Inter | 600, 700 | Page titles, section headers |
| Body | Inter | 400, 500 | Descriptions, content, labels |
| Mono | JetBrains Mono | 400 | Code, IDs, timestamps |

**[CUSTOMIZE]** If your product has a distinct typographic personality, use different
typefaces for display and body. Beacon uses Inter throughout because its brand is
utilitarian -- typography personality comes from weight and spacing variation, not
typeface contrast.

### Type Scale

| Token | Size | Line Height | Weight | Usage |
|-------|------|-------------|--------|-------|
| `--text-2xl` | 24px | 32px | 600 | Page titles |
| `--text-xl` | 20px | 28px | 600 | Section headers |
| `--text-lg` | 16px | 24px | 500 | Card titles, emphasis |
| `--text-base` | 14px | 20px | 400 | Body text, descriptions |
| `--text-sm` | 12px | 16px | 400 | Metadata, timestamps |
| `--text-xs` | 11px | 14px | 500 | Badges, labels |

Every page must use at least 3 different sizes from this scale.

## Section 5: Spacing and Layout

### Spacing Scale

```css
--space-0:  0px;
--space-1:  4px;
--space-2:  8px;
--space-3:  12px;
--space-4:  16px;
--space-5:  20px;
--space-6:  24px;
--space-8:  32px;
--space-10: 40px;
--space-12: 48px;
--space-16: 64px;
```

**Rule:** Every screen must use at least 3 different spacing values. Uniform `p-4 gap-4`
everywhere is a brand violation.

### Layout Principles
- Content areas use asymmetric spacing (more space above sections than below).
- Group related items with tight spacing; separate sections with generous spacing.
- Sidebar width: 240px (desktop), 56px (collapsed), 0 (mobile).
- Maximum content width: 1200px for list views, uncapped for board views.

## Section 6: Motion and Animation

- **Duration:** Fast (100ms) for hover states, medium (200ms) for panels and dropdowns,
  slow (300ms) for page transitions. Never exceed 400ms.
- **Easing:** `ease-out` for entrances, `ease-in` for exits, `ease-in-out` for transforms.
- **What animates:** opacity transitions, slide-ins (panels), scale (modals), height changes
  (expanding sections).
- **What does NOT animate:** color changes on text, layout reflows, scroll position.
- **Reduced motion:** Respect `prefers-reduced-motion`. Replace animations with instant
  state changes.

## Section 7: Voice and Tone

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

## Section 8: Anti-Generic Checklist

Run every item against each component or page. All Typography, Color, and Layout items
must pass. Interaction and Voice items should pass but can be deferred with justification.

### Typography (7 items)
1. [ ] At least 3 distinct font sizes are used on this screen.
2. [ ] At least 2 distinct font weights are visible.
3. [ ] Letter-spacing or tracking varies between headings and body.
4. [ ] Line-height differs between headings and body text.
5. [ ] No text uses Tailwind default `text-gray-*` colors.
6. [ ] Heading hierarchy is visually clear without relying on size alone.
7. [ ] Monospace font is used for code, IDs, or timestamps (where applicable).

### Color (5 items)
8. [ ] Zero instances of banned Tailwind default color utilities.
9. [ ] Accent color appears in 1-2 focal points per screen, not everywhere.
10. [ ] Body text contrast is 4.5:1 or higher (WCAG AA).
11. [ ] Surface colors create 3+ distinct elevation levels.
12. [ ] Interactive elements have visible hover, focus, and active states.

### Layout (5 items)
13. [ ] At least 3 different spacing values used on this screen.
14. [ ] Related items are visually grouped (tighter spacing within, more between).
15. [ ] Layout is NOT a centered column of uniform-width cards.
16. [ ] Mobile and desktop layouts differ meaningfully.
17. [ ] Intentional whitespace exists (some areas are dense, some breathe).

### Interaction (4 items)
18. [ ] Button labels are specific to their action.
19. [ ] At least one micro-interaction exists (hover, transition, animation).
20. [ ] Loading states match content shape (skeletons, not spinners).
21. [ ] Empty states include a suggested next action.

### Voice (3 items)
22. [ ] No user-facing text uses forbidden terms (AI, generate, model, prompt).
23. [ ] Error messages are specific and actionable.
24. [ ] Placeholder text is realistic and helpful.

### Visual Verification (3 items)
25. [ ] Page is visually distinguishable from a competitor's equivalent page.
26. [ ] Brand is evident even with the logo hidden.
27. [ ] No clipping, overflow, or collapse at 375px and 1280px viewports.

**Minimum passing score:** 22/27. All Typography, Color, and Layout items are mandatory.
