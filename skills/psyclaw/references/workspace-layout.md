# PsyClaw Workspace Layout

Date: 2026-07-02. The PsyClaw project uses a two-location split.

## Locations

| Purpose | Path | Git | Contents |
|---------|------|-----|----------|
| **Skill source** | `C:\Users\User\AppData\Local\hermes\skills\research\psyclaw\` | `origin`: `https://github.com/Paradeluxe/PsyClaw.git` (master) | `SKILL.md`, `scripts/`, `templates/`, `references/`, `examples/` |
| **Project workspace** | `E:\hermes_playground\psyclaw\` | Local only (`git init` 2026-07-02) | `papers/`, `specs/`, `output/`, `references/` |

## Why the split

- The skill source must live under `~/.hermes/skills/` for Hermes to load it.
  Moving it to E: breaks skill discovery.
- E: has more space and is the user's working drive (`hermes_playground` is
  the general sandbox).
- Workspace contains large files (PDFs, generated experiments) that don't
  belong in the skill repo (`.gitignore` in skill repo already excludes them).

## Workspace directory structure

```
E:\hermes_playground\psyclaw\
├── papers/            # Downloaded papers for reference
│   └── classics/      # Classic experiment papers (see references/classic-paper-acquisition.md)
├── specs/             # Experiment YAML specs
├── output/            # Generated .psyexp + xlsx + assets
├── references/        # Project-specific references
└── .gitignore         # Excludes output/ and *.pdf
```

## Skill source directory structure

See `SKILL.md` §Files for full tree. Key: `scripts/`, `templates/`, `references/`, `examples/`, `SKILL.md`.
