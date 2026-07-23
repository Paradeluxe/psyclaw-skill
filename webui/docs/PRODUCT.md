# Product boundary

## What this is

**PsyClaw WebUI** — local **mission-control** UI for psychology experiments on a lab PC.

Pipeline:

```
Builder design (`<folderName>.psyclaw` JSON)
  → design_compiler (pure Python using PsychoPy APIs)
  → PsychoPy library via configured Python subprocess
  → CSV under <project>/data/  (+ runs/<id>/ mirror)
```

Not a PsychoPy Builder clone. Marker **`<folderName>.psyclaw` is JSON**, not Builder XML — opening it in desktop Builder will fail by design.

## Tabs

| # | Tab | Role |
|---|-----|------|
| 1 | **Builder** (default) | Design: parts → sequence timeline → mission flow + stimlist + inspector |
| 2 | **System** | Host profile, Display / Mic / Speaker, hardware preflight |
| 3 | **Run** | Session form, roster, Start / Pilot / Autopilot, Instrument, live log |
| 4 | **Settings** | Timeline snap, visual onset click, language, file prefs |
| 5 | **Guide** | Keyboard / ops help (not inlined into Builder) |

Port **8876** (do not reuse 8765). Override: `PSYCLAW_PORT`.

## Goals

- Design multi-routine experiments with loops and condition tables (`$col` params).
- Run **Pilot** (manual), **Start** (formal IDs), **Autopilot** (headless smoke keys).
- Keep behavioral data on the project folder like desktop lab software.
- en/zh UI; readable mission-control chrome (black/red).

## Non-goals (v0.1)

- Remote / browser multi-participant hosting
- Full PsychoPy component surface (sound, mouse, slider, eye-tracker, serial triggers — out of scope until listed)
- Round-trip edit of official `.psyexp` XML
- Bundling PsychoPy or paper PDF corpora
- Requiring Hermes Agent / AI skill to run experiments

## Components (current palette)

text · keyboard · image · video · fixation · code

## Success criteria for a run

1. Process reaches **finished**
2. CSV retained under **`<project_path>/data/`** with session columns and trial rows

Autopilot validates the pipeline; it does not validate psychological effects.
