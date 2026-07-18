# /psyclaw pipeline + inputs (2026-07-18+)

User wants **simple** explanations first (幼儿园 when stuck); A/B/C paths are implementation detail.

## Two products (one line each)

- **`/psyclaw`** = write the experiment “说明书” (marker file).
- **`/psyclaw-webui`** = lab software that opens that file, runs subjects, writes CSV.

## Marker (shared contract)

```
MyStroop/
  └── MyStroop.psyclaw
```

- Canonical: **`<folderName>.psyclaw`** (JSON design schema).
- Not fixed `design.psyclaw` for new work (webui migrates legacy on open/save).
- Not PsychoPy Builder XML.

## Default agent pipeline

```
INPUT → clarify loop (one Q per turn) until user satisfied / ready
     → write/update <folderName>.psyclaw
     → validate → deliver project folder
     → optional handoff to webui (G1/G2)
```

Clarify stop signals: 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 / enough detail that IV·DV·response·trial structure are clear.

Default success for skill alone = **valid marker + project folder**.  
Full lab success (finished run + `<project>/data/` CSV) needs webui/runner.

## Three input classes

| # | Input | Companion skill |
|---|--------|-----------------|
| 1 | User NL description of the experiment | none |
| 2 | Materials (PDF Method, HTML, pasted text) | **`browser-skill`** (and/or academic-search) to **fetch** — then return to `/psyclaw` |
| 3 | Existing project folder with marker | edit in place |

## browser-skill = related, not core

- Put in `related_skills`; tell agent: load when class-2 needs net download.
- **Do not** merge browser into psyclaw package or run browser on every `/psyclaw`.
- `hermes skills install` of browser is separate from installing this skill.
- Skill may **recommend** related installs; does not silent-install them.

## First `/psyclaw` = doctor (user confirmed)

Detect missing small deps / webui / PsychoPy when needed → report → consent → install only gaps. Not every turn. See `install-orchestrator.md`.

## Nature-style pattern

Like `nature-figure`: skills install = light cookbook; large runtime external; missing → stop + install commands, no fake substitute backend.

## Slash vs GitHub vs playground

| Name | Meaning |
|------|---------|
| Slash / skill id | **`/psyclaw`** / `psyclaw` |
| GitHub skill repo | **`Paradeluxe/psyclaw-skill`** (edit this package) |
| Hermes local | `~/.hermes/skills/research/psyclaw` |
| `E:\hermes_playground\psyclaw-skill` | **Papers/replications workspace** — NOT skill package |

Do **not** rename slash to `/psyclaw-skill` unless user asks.

## Market / short name

`hermes skills install psyclaw` works when searchable sources have exactly one skill named `psyclaw`. Prefer tap layout `skills/psyclaw/`. See `product-pipeline-and-hermes-market.md` + `install-orchestrator.md`.
