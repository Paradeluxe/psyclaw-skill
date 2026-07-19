---
name: psyclaw
version: 0.3.1
author: Paradeluxe
license: AGPL-3.0
platforms: [windows, macos, linux]
description: >
  PsyClaw skill — turn NL or paper Method into a project folder with
  <folderName>.psyclaw (design JSON). Clarify + experiment-design norms,
  then write marker. After G0, ask the user whether to run subjects;
  handoff psyclaw-webui for sequential runs + CSV (experimenter=AI when
  agent-driven). Not the lab GUI; not PsychoPy Builder XML.
tags: [psychology, psychopy, experiment-design, stimuli-generation, conversational]
related_skills: [browser-skill, psyclaw-webui]
---

# PsyClaw (`/psyclaw`)

Write the experiment **说明书** (marker file). Run subjects in **psyclaw-webui**.

| | Skill | WebUI |
|---|--------|--------|
| Role | design → `<folderName>.psyclaw` | draw / run / CSV |
| GitHub | `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |
| Install | `hermes skills install Paradeluxe/psyclaw-skill/skills/psyclaw -y` | separate lab install |
| Slash | **`/psyclaw`** | `/psyclaw-webui` |

Never merge install narratives. Skill install ≠ GUI deploy.

## Shared IR

```text
MyStroop/
  └── MyStroop.psyclaw    # folder basename + .psyclaw
```

- Content = design JSON (routines + flow), **not** `.psyexp`.
- New work: **`<folderName>.psyclaw`** (not fixed `design.psyclaw`; webui migrates legacy).
- Skill write success = project folder + valid marker (G0).
- Full lab success (finished run + `<project>/data/` CSV) needs webui (G1/G2).

## User usage pipeline

```text
INPUT (NL | PDF/Method | existing folder)
  → Clarify (1 Q/turn, coach + defaults; Design first, OutPath last)
  → Write + Validate G0
  → Agent ASKS: 要跑被试吗？
       No  → stop
       Yes → webui sequential subjects
             auto ID/UID · P_pilot free · finished → next ID
             agent-driven run → session.experimenter = AI identity
```

No half-run product mode. Multi-subject = normal sequential runs, not a special batch UI.

## Pipeline (steps)

1. **Hear** — NL / PDF Method / existing project folder
2. **Clarify** — **one question per turn**. Coach with `references/experiment-design-norms.md`:
   - Give standard defaults when the user is unsure (coach, not pure quiz)
   - **Design first** (几×几 / within·between·mixed / continuous IVs) — not paradigm brand names
   - then IV → DV → control → random → practice → script → response → trial
   - **OutPath last** — default `./experiments/<slug>/`; never Desktop; never skill install tree
   - Stop: 满意 / 就这样 / 开始写 / 别问了按默认 / core items clear (rest defaulted)
3. **Write** — `<projectDir>/<folderName>.psyclaw` at agreed OutPath
4. **Validate** — schema / structure (G0)
5. **Ask run** — after G0, **agent asks** whether to run subjects (do not only wait for 能跑吗).  
   If yes → load `psyclaw-webui`, sequential runs, auto IDs, set `session.experimenter` to the AI identity when the agent drives the run.

Edit path: open existing marker → change → rewrite → validate → **ask run again**. Do not re-ask OutPath.

## Intent map

| User | Do |
|------|-----|
| 做一个… | steps 1→5 (ask run after G0) |
| 改… | edit marker → 3→5 |
| 要跑 / 跑一下 / 多人 | handoff webui; sequential; experimenter=AI if agent-run |
| 不要跑 / 只要说明书 | stop after G0 |
| 全装 / 首次 | doctor — `references/install-orchestrator.md` |

## Inputs

| Class | Source | Note |
|-------|--------|------|
| 1 | NL description | default |
| 2 | PDF / HTML / paste Method | fetch with **browser-skill** / academic tools if needed, then return here |
| 3 | Existing folder + marker | edit in place |

browser-skill = related only; do not silent-install or run browser every turn.

## Agent rules

- Plain language when operator is confused; no multi-path architecture dumps
- Platform > paradigm-specific hardcoding (Stroop/GoNoGo as data labels OK; do not hardcode paradigm compilers)
- User override wins; log design deviations in marker notes
- No public release / tag / push without explicit approval
- First `/psyclaw` or 全装: doctor gaps → consent → install only missing pieces
- After every successful G0 write/edit: **ask** 要跑被试吗 (unless user already said run/don't-run this turn)

## References (load on demand)

| File | When |
|------|------|
| `references/skill-pipeline.md` | pipeline detail |
| `references/skill-pipeline-and-inputs.md` | inputs, marker, OutPath |
| `references/experiment-design-norms.md` | clarify checklist (Design first, OutPath last) |
| `references/install-orchestrator.md` | install / doctor / short name |
| `references/webui-handoff.md` | G0/G1/G2 + webui handoff gates |
| `references/user-conservative-workflow-preference.md` | one surgical fix per bug report |

## Marker content (minimal)

Emit design JSON the webui runner accepts: routines, flow/loops, components (text/image/keyboard/slider/…), conditions columns, session metadata as required by webui schema. Prefer fields already used by psyclaw-webui `design_compiler`; do not invent a second parallel schema.

When unsure of a field: read webui schema / `webui-handoff.md`, not legacy YAML→psyexp docs.

## Out of scope (this skill)

- PsychoPy Builder `.psyexp` generation pipelines
- Paper PDF batch libraries / replications workspace
- Bundling or installing PsychoPy itself
- Statistical analysis of subject data
- Half-run / partial-trial lab modes (not a webui product surface)
