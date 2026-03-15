# Chapter 6: Design Intent Preservation — The Anti-Slop System

> **Part 3: HARNESS** | Maps to templates: `templates/.claude/skills/design-enforcement/SKILL.md`, `templates/docs/brand-identity-template.md`

This is the most important chapter in the HARNESS section. It addresses the single largest quality risk in agent-generated frontend code: generic output.

Claude — like all language models — has strong priors. It has seen millions of Tailwind utility classes, and it defaults to the most common ones. It gravitates toward Inter, uniform spacing, card grids, `rounded-lg`, `bg-gray-800`, `p-4 gap-4`. Left unchecked, the output looks like every other AI-built app. This is the "vibe-coded" aesthetic, and it is the death of brand identity.

This chapter presents a five-layer defense system that makes the agent's path of least resistance the same as your brand's requirements.

---

## Principles

**Generic is the default failure mode.** You do not need to instruct Claude to produce generic output — it will do so without intervention. Every layer of defense you add pushes the output toward specificity. The question is not "will it be generic?" but "how many layers of defense prevent that?"

**Negative examples outperform positive rules.** Telling the agent "use the brand color palette" is less effective than telling it "NEVER use `bg-gray-800`, `text-gray-500`, or any Tailwind default color." Agents course-correct more reliably when they know what to avoid than when they know what to aspire to.

**Enforcement at the moment of work beats enforcement after the fact.** Loading design constraints right before the agent writes a component is more effective than reviewing the output after it is written. Prevention beats remediation.

---

## The Problem in Detail

Here is what unguided Claude Code produces for a typical component:

```tsx
// The generic result — recognizable as AI-generated
export function FeatureCard({ title, description, icon }: FeatureCardProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 hover:bg-gray-700 transition-colors">
      <div className="flex items-center gap-3 mb-2">
        {icon}
        <h3 className="text-lg font-semibold text-white">{title}</h3>
      </div>
      <p className="text-gray-400 text-sm">{description}</p>
    </div>
  );
}
```

Every element of this is a Tailwind default. `bg-gray-800`. `rounded-lg`. `p-4`. `gap-3`. `text-gray-400`. `text-lg font-semibold`. `hover:bg-gray-700`. The result is technically correct and visually indistinguishable from a thousand other apps.

The five-layer defense transforms this into output that reflects a specific brand identity — not because the agent is more creative, but because the generic patterns are systematically blocked.

---

## Layer 1: The Anti-Pattern Catalog

Name the failure modes explicitly. Give them memorable labels. Define them with concrete code examples. This layer goes in your design-enforcement skill so it loads when the agent is about to do frontend work.

**Tailwind Default Syndrome**

The agent reaches for Tailwind's built-in color palette and spacing scale because those are the tokens it has seen most often in training data.

```
BANNED:
- bg-gray-* , bg-zinc-* , bg-slate-* , bg-neutral-*
- text-gray-* , text-zinc-* , text-slate-*
- Any Tailwind default color used directly

REQUIRED:
- All colors from CSS custom properties defined in your design tokens
- Example: bg-[var(--color-surface-primary)] instead of bg-gray-900
```

**Typography Flatness**

The agent defaults to the system font stack or Inter for everything. Headings look like body text with a larger font size. There is no typographic hierarchy.

```
BANNED:
- font-sans applied to headings (unless your heading font IS sans-serif)
- Same font family for headings and body (unless that is the intentional brand choice)
- Only one font weight used across the entire component

REQUIRED:
- Heading font: [your display typeface] via CSS custom property
- Body font: [your body typeface] via CSS custom property
- At least 2 distinct weights in any component with both headings and body text
```

**Layout Monotony**

Everything is a card grid. Everything is centered. Spacing is uniform. The layout has no rhythm.

```
BANNED:
- Every section using the same grid column count
- Uniform gap-4 or gap-6 across all layout contexts
- All content centered with no left-aligned or asymmetric layouts

REQUIRED:
- Spacing values from your design token scale (not arbitrary Tailwind values)
- At least two different layout approaches on any page with 3+ sections
- Intentional spacing hierarchy (tight within groups, generous between sections)
```

**Missing Personality**

Buttons say "Submit." Headers say "Welcome." Empty states say "No items found." The copy is functional but has zero brand voice.

```
BANNED:
- Generic button labels: "Submit", "Cancel", "OK", "Click Here"
- Generic headings: "Welcome", "Dashboard", "Settings"
- Generic empty states: "No items found", "Nothing here yet"

REQUIRED:
- Button labels that reflect the action in domain terms
- Headings that reflect the brand voice
- Empty states with personality and guidance
```

**Interaction Poverty**

No hover states. No transitions. No micro-interactions. The interface feels static.

```
BANNED:
- Interactive elements with no hover/focus state
- Transitions that use only transition-colors (the lowest-effort default)

REQUIRED:
- Every clickable element has a distinct hover state
- Transitions use your brand's easing curve (e.g., cubic-bezier from tokens)
- Focus states meet WCAG 2.1 AA requirements
```

---

## Layer 2: Design Tokens as the Only Option

The most effective enforcement is mechanical. If `bg-gray-800` is not available as a class, the agent cannot use it.

**How to implement this with Tailwind v4:**

Define your entire color palette, type scale, spacing scale, and effects as CSS custom properties in a tokens file:

```css
/* tokens.css */
:root {
  /* Colors — these are the ONLY colors available */
  --color-surface-primary: #0D0A0F;
  --color-surface-secondary: #171318;
  --color-surface-elevated: #1E1921;
  --color-accent: #C4536A;
  --color-accent-hover: #D4637A;
  --color-text-primary: #F0ECE6;
  --color-text-secondary: #A8A0B0;
  --color-text-muted: #706878;

  /* Typography */
  --font-display: 'Cormorant Garamond', serif;
  --font-body: 'Source Serif 4', serif;
  --font-ui: 'Inter', sans-serif;

  /* Spacing scale */
  --space-1: 0.25rem;
  --space-2: 0.5rem;
  --space-3: 0.75rem;
  --space-4: 1rem;
  --space-6: 1.5rem;
  --space-8: 2rem;
  --space-12: 3rem;
  --space-16: 4rem;

  /* Effects */
  --radius-sm: 4px;
  --radius-md: 8px;
  --radius-lg: 12px;
  --ease-standard: cubic-bezier(0.2, 0.0, 0.0, 1.0);
  --duration-fast: 150ms;
  --duration-normal: 250ms;
}
```

Then configure Tailwind's theme to use these tokens, replacing defaults:

```css
/* In your Tailwind v4 CSS */
@theme {
  --color-surface-primary: var(--color-surface-primary);
  --color-surface-secondary: var(--color-surface-secondary);
  --color-surface-elevated: var(--color-surface-elevated);
  --color-accent: var(--color-accent);
  /* ... map all tokens ... */
}
```

**The effect:** When the agent tries to use `bg-gray-800`, it gets a build error or no style applied. The only colors that work are your brand colors. The path of least resistance is the correct path.

**For spacing and typography:** The same principle applies. If your spacing scale is defined via custom properties and Tailwind is configured to use them, the agent cannot reach for arbitrary `p-4` or `gap-6` — it must use your scale.

---

## Layer 3: Mandatory Skill Invocation

Create a design-enforcement skill that loads the anti-pattern catalog, token reference, and checklist into the agent's context at the moment it begins frontend work.

**In CLAUDE.md (Tier 1):**

```markdown
## Mandatory Skills
- `/design-check` — REQUIRED before creating or modifying any component,
  page, or layout. Do NOT skip this because you "already know" the brand.
```

**In `.claude/skills/design-enforcement/SKILL.md` (Tier 3):**

```markdown
# Design Enforcement — Mandatory Pre-Flight

You MUST complete this checklist before writing any frontend component,
page, or layout code. This is not optional.

## Step 1: Load Context
Read the following files before proceeding:
- docs/brand-identity.md (full design system)
- tokens.css or your project's token file (available values)

## Step 2: Anti-Pattern Review
Before writing any code, confirm you will NOT use:
- [ ] Any Tailwind default gray/zinc/slate/neutral color
- [ ] font-sans on headings (use the display typeface)
- [ ] Uniform spacing (same gap/padding everywhere)
- [ ] Generic copy ("Submit", "Welcome", "No items found")
- [ ] Interactive elements without hover/focus states

## Step 3: Build the Component

## Step 4: Post-Build Checklist
After writing the code, verify every item:

### Typography
- [ ] Headings use the display font (--font-display)
- [ ] Body text uses the body font (--font-body)
- [ ] UI elements use the UI font (--font-ui)
- [ ] At least 2 font weights visible in the component

### Colors
- [ ] All colors reference CSS custom properties, not Tailwind defaults
- [ ] Background colors are from the surface palette
- [ ] Text colors are from the text palette
- [ ] Accent color used intentionally (not as default for everything)

### Layout
- [ ] Spacing values from the design token scale
- [ ] No uniform gap-4/gap-6 applied to everything
- [ ] Intentional spacing hierarchy (tight within, generous between)

### Interaction
- [ ] All clickable elements have hover states
- [ ] Focus states are visible and meet WCAG AA
- [ ] Transitions use the brand easing curve
- [ ] No bare transition-colors without specifying duration

### Voice
- [ ] No "AI" / "model" / "generate" / "prompt" in user-facing text
- [ ] Button labels are domain-specific, not generic
- [ ] Empty states have personality

### Threshold
If more than 2 items fail, revise before proceeding.
```

**Why this works better than putting it all in CLAUDE.md:** CLAUDE.md loads at session start. By the time the agent begins writing a component, it has read dozens of files and the design rules are buried deep in context. The skill reloads everything at the moment of maximum relevance — right before the work happens.

---

## Layer 4: Concrete, Measurable Checklist

The checklist in Layer 3 must be specific and binary. Not "is the design good?" but "does the heading use `--font-display`?" Each item has a yes/no answer. The threshold (more than 2 failures = revise) creates a mechanical gate.

**Why measurability matters:** Subjective criteria ("ensure the design feels premium") are unenforceable by an agent. The agent will always judge its own output as meeting subjective criteria. Objective criteria ("all colors reference CSS custom properties") can be verified by searching the code.

**Evolving the checklist:** Start with the items above. After each phase of frontend work, review the output. If you see a new failure pattern, add it to the checklist. The checklist is a living document — it grows as you discover new ways the agent drifts from the brand.

**Example of checklist evolution:**

```
Version 1 (initial):
- [ ] No Tailwind default colors
- [ ] Correct font families

Version 2 (after noticing inline style drift):
- [ ] No inline styles for token references (use Tailwind arbitrary values)
  BAD:  style={{ padding: "var(--space-4)" }}
  GOOD: className="p-[var(--space-4)]"

Version 3 (after noticing missing dark mode consideration):
- [ ] All surfaces have sufficient contrast with parent background
- [ ] Text meets 4.5:1 contrast ratio against its background
```

---

## Layer 5: CSS-Layer Enforcement

This is the strongest layer — mechanical enforcement at the build level.

When your Tailwind theme is configured to use only your design tokens, references to non-brand values produce warnings or failures. The agent cannot produce code that compiles with wrong colors because the wrong colors do not exist in the theme.

**Reinforcing with linting:**

Add lint rules (ESLint, Stylelint, or custom) that flag:
- Inline `style={{}}` attributes that reference CSS custom properties (should use Tailwind arbitrary values)
- Direct hex/rgb color values in component files (should use tokens)
- Font-family declarations outside the token set

**Example ESLint rule concept:**

```javascript
// Conceptual — detect inline styles that should be Tailwind classes
{
  "rules": {
    "no-inline-token-styles": {
      "message": "Use Tailwind arbitrary values instead of inline styles for tokens. Example: p-[var(--space-4)]",
      "pattern": "style=\\{\\{.*var\\(--"
    }
  }
}
```

The point is not the specific linting tool. The point is that mechanical enforcement catches drift that skill invocation misses. Skills rely on the agent following instructions. Linting relies on the build pipeline rejecting bad output.

---

## For Projects Without a Frontend

The five-layer pattern applies wherever taste and consistency matter, not only to visual design.

**API Design Conventions:**
- Anti-pattern catalog: inconsistent casing, mixed plural/singular endpoints, non-standard error shapes
- Token equivalent: a response schema template that defines the standard envelope
- Skill: loads API design guidelines before implementing endpoints
- Checklist: consistent naming, standard error format, pagination pattern, correct HTTP verbs
- Enforcement: OpenAPI spec validation (automated contract check)

**Documentation Tone:**
- Anti-pattern catalog: passive voice, filler words, marketing language in technical docs
- Token equivalent: a writing style guide (word list, banned phrases)
- Skill: loads writing guidelines before generating docs
- Checklist: active voice, specific examples, no banned phrases, correct heading hierarchy
- Enforcement: prose linting tools (Vale, write-good)

**Error Message Quality:**
- Anti-pattern catalog: "Something went wrong", "Error occurred", stack traces shown to users
- Token equivalent: error message templates with required fields (what happened, what to do, error code)
- Skill: loads error conventions before implementing error handling
- Checklist: user-friendly message, actionable guidance, error code for support, no internal details leaked
- Enforcement: test assertions that verify error response shape

**CLI User Experience:**
- Anti-pattern catalog: walls of text, no color coding, inconsistent flag naming, missing help text
- Token equivalent: CLI style guide (output format, color usage, verbosity levels)
- Skill: loads CLI conventions before implementing commands
- Checklist: help text for all commands, consistent flag naming, colored output, progress indicators
- Enforcement: CLI integration tests that verify output format

---

## What the Human Should Do

1. **Define your brand identity before implementation begins.** Write the design tokens, choose the typefaces, establish the color palette, define the voice. This is a human decision — the agent implements it, not invents it.

2. **Write the anti-pattern catalog from real failures.** Build the first few components without the defense system. Observe what the agent produces. The failure patterns you see become the catalog. This is more effective than guessing in advance.

3. **Create the design tokens file.** Define every color, font, spacing value, radius, easing curve, and duration as CSS custom properties. Configure Tailwind to use these tokens as its theme. Verify that default Tailwind colors are not available.

4. **Build the skill.** Assemble the anti-pattern catalog, token reference, and checklist into a skill file. Make it mandatory in CLAUDE.md.

5. **Review the output visually.** Checklists catch mechanical failures (wrong font, wrong color). They do not catch aesthetic failures (the layout "feels" off, the spacing rhythm is wrong). Visual review by a human remains essential.

6. **Evolve the checklist.** After each phase, add new items for any failure patterns you observed. The checklist should grow over the first few phases, then stabilize.

---

## What the Agent Should Do

1. **Invoke the design skill before every frontend task.** Not just the first time. Every time. Design rules load fresh context that prevents drift that accumulates across a long session.

2. **Read the token file.** Know what values are available before writing any component. If you need a color that does not exist in the tokens, flag it for the human — do not invent one.

3. **Run the checklist after writing each component.** Not at the end of the phase — after each component. Catching a violation early is cheaper than rewriting three components that all share the same mistake.

4. **When in doubt, choose the specific option over the generic one.** If you are deciding between `rounded-lg` (a Tailwind default) and `rounded-[var(--radius-md)]` (a design token), always choose the token. If you are deciding between "Submit" and a domain-specific label, always choose the domain-specific label.

5. **Do not mix concerns in the skill invocation.** If the design skill says to read `docs/brand-identity.md`, read it. Do not also read the architecture doc, the API spec, and the CI config "just in case." Load what the skill tells you to load and nothing more.

6. **Treat checklist failures as blocking.** If more than 2 items fail, revise. Do not proceed to the next component hoping to fix it later. Fix it now, while the context for this component is fresh.
