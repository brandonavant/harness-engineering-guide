# Documentation Structure

<!-- WHY THIS EXISTS:
Claude Code agents implement against documentation, not verbal instructions. The quality
of the documentation directly determines the quality of the implementation. This file
explains the document cascade -- the order in which documents are created and the
dependency relationships between them. -->

## The Document Cascade

Documents are created in dependency order. Each document builds on the ones above it.

```
PRD (what to build and why)
  --> Architecture (how to build it, what tech, what constraints)
    --> UX Spec (screen-by-screen behavior)
    --> API Contract (endpoint-by-endpoint interface)
  --> Brand Identity (how it should look and feel)
```

## Document List

| Document | Purpose | Template |
|----------|---------|----------|
| `PRD.md` | Product requirements, features, personas, constraints | `prd-template.md` |
| `architecture.md` | Tech stack, system design, data models, deployment | `architecture-template.md` |
| `ux-spec.md` | Screen specs, interactions, accessibility, responsive behavior | `ux-spec-template.md` |
| `brand-identity.md` | Design system, colors, typography, anti-generic checklist | `brand-identity-template.md` |

The API contract lives in `contracts/openapi.yaml`, not in `docs/`.

## Version Tracking

Every document includes a header with:
- **Version:** Semantic version (v1.0, v1.1, v2.0)
- **Date:** Last updated
- **Author:** Who wrote or revised it
- **Change summary:** What changed in this version

## Read-Only Enforcement

During implementation, design documents are **read-only**. Agents implement against
what the documents specify -- they do not modify documents to match what they built.

If an agent discovers an ambiguity, contradiction, or gap in a document:
1. Record it in their `.agent-state/*.md` file.
2. Notify the team lead.
3. The team lead (or document owner) resolves it and updates the document.
4. The agent then implements against the updated document.

This prevents the failure mode where agents silently edit specs to justify implementation
shortcuts.
