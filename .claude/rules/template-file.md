---
paths:
  - "templates/**"
---

# Template File Editing Rules

## Example Project

Templates use the fictional **Beacon** task management SaaS as the example project. Never use "RecipeVault" in
templates — that is for guide chapters only.

## CUSTOMIZE Markers

Every template must have at least one `**[CUSTOMIZE]**` marker indicating where users replace example content with their
own. If you remove the last marker, add a new one or restore it.

## No Outbound Links

Templates should not link to guide chapters (e.g., `[Chapter 04](../../guide/04-context-architecture.md)`). Users copy
templates out of this repo into their own projects, where those links would break.

## Rename Protocol

After renaming a template file:

1. Grep `guide/` for the old filename — chapters reference templates by path
2. Update any matches to use the new filename
3. Check `templates/docs/README.md` and `templates/contracts/README.md` for the old name

## Init Script Sync

After adding, renaming, or removing any file under `templates/`:

1. Open `scripts/init-project.py` and update the `TEMPLATE_FILES` list to match the current set of files
2. Verify every file listed in `TEMPLATE_FILES` exists, and every file under `templates/` is listed
