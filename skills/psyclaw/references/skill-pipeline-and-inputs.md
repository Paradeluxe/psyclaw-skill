# /psyclaw pipeline + inputs (2026-07-18+)

User wants **simple** explanations first (plain language when stuck). One pipeline only.

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

## Default agent pipeline (user usage)

```text
INPUT → clarify loop (one Q per turn) + experiment-design-norms checklist
     → lock OutPath (late; default ./experiments/<slug>/)
     → write/update <projectDir>/<folderName>.psyclaw
     → validate G0 → deliver project folder
     → agent ASKS: 要跑被试吗？
          No  → stop
          Yes → webui sequential subjects (G1/G2)
                auto ID/UID · P_pilot free · finished → next ID
                agent-driven → session.experimenter = AI identity
```

Clarify = user satisfaction **and** norms coach (see `experiment-design-norms.md`) — give defaults when unsure.  
Priority: **Design** first; **OutPath** last before write (skip if editing an existing folder).  
Stop signals: 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 / Design·IV·DV·response·trial clear with remaining norms defaulted or waived (OutPath may still use default).

Write success = **valid marker + project folder at agreed path** (G0), then **ask run**.  
Full lab success (finished run + `<project>/data/` CSV) needs webui/runner.  
Multi-subject = sequential runs (not a special batch mode). No half-run product mode.

### OutPath defaults (summary)

- New: `./experiments/<folderName>/` under session cwd (or operator-given base)
- Marker: `<projectDir>/<folderName>.psyclaw` (`folderName` = basename)
- Never default to Desktop; never write into `~/.hermes/skills/.../psyclaw`
- Edit existing project → path already known, do not re-ask

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
| Hermes local | `~/.hermes/skills/psyclaw` (or profile skills dir) |
| Papers vault (optional) | separate data folder — **not** the skill package |

Do **not** rename slash to `/psyclaw-skill` unless user asks.

## Market / short name

`hermes skills install psyclaw` works when searchable sources have exactly one skill named `psyclaw`. Repo layout is `skills/psyclaw/`. Full fallback: `Paradeluxe/psyclaw-skill/skills/psyclaw`. See `install-orchestrator.md`.
