# Design & API conventions

Contributor rules for PsyClaw WebUI. Breaking these is a product bug.

## Principles

1. **Paradigm-agnostic platform** — core code must not hardcode Stroop / GoNoGo / etc. as special compilers. Paradigm flavor is data (marker JSON, stimlists, examples).
2. **CSS variables only** — no ad-hoc inline hex colors in new UI; use tokens from `frontend/style.css` / `docs/design.md`.
3. **Tabs** — Builder designs; System preflights host + PsychoPy; Run executes sessions; Settings / Guide support ops.
4. **Marker** — product handoff is `<folderName>.psyclaw` (JSON). Not PsychoPy Builder `.psyexp` XML.
5. **Local only** — default bind `127.0.0.1`; data under the project folder.

## Success checks (run)

| Check | Pass |
|-------|------|
| Marker ready | design compiles |
| Run finished | run status `finished` |
| Data on disk | CSV under `<project_path>/data/` |

## PsychoPy boundary

- Flask process does **not** need to import PsychoPy.
- Runs use `PSYCLAW_PSYCHOPY_PYTHON`, else PATH library (`import psychopy`), else probed Standalone paths.
- Session fields come from the Run form — not PsychoPy `gui.Dlg` / expInfo dialogs.

## Public HTTP surface (high level)

- SPA: `/` and static `frontend/*`
- Health: `GET /api/health`
- Designs / projects: open folder, read/write marker via designs store APIs
- Runs: `POST /api/runs` (and status / stop / artifacts as implemented)
- System: host + PsychoPy probe endpoints

Exact request/response fields live next to route handlers in `backend/api/`. Prefer extending existing routes over parallel schemas.

## Examples

- Sample stimlists: `examples/`
- Fixture project: `tests/example_experiment/`
- Tiny sample folders: `designs/`
