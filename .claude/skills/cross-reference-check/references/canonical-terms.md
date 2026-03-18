# Canonical Terms

Terms with authoritative definitions that must be used consistently across the repo.

## Registry

| Term                          | Authoritative Source               | Dependent Locations                                  |
|-------------------------------|------------------------------------|------------------------------------------------------|
| "five-tier context hierarchy" | `guide/04-context-architecture.md` | `CLAUDE.md`, `README.md`                             |
| "document cascade"            | `guide/03-specification-phase.md`  | `CLAUDE.md`, `README.md`, `templates/docs/README.md` |

## How to Update

If a canonical term changes in its authoritative source:

1. Search all `.md` files for the old term: `grep -rn "old term" .`
2. Update every occurrence to match the new wording exactly
3. Update this registry if the term itself changed
4. Update the Cross-Reference Registry table in `CLAUDE.md`
