---
name: psyclaw
version: 0.3.0
author: Paradeluxe
license: AGPL-3.0
platforms: [windows, macos, linux]
description: >
  PsyClaw skill — turn NL or paper Method into a project folder with
  <folderName>.psyclaw (design JSON). Clarify + experiment-design norms,
  then write marker. Optional handoff to psyclaw-webui for participant
  run + CSV. Not the lab GUI; not PsychoPy Builder XML.
tags: [psychology, psychopy, experiment-design, stimuli-generation, conversational]
related_skills: [browser-skill, psyclaw-webui]
---

# PsyClaw (`/psyclaw`)

Write the experiment **说明书** (marker file). Humans run subjects in **psyclaw-webui**.

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
- Skill success = project folder + valid marker (G0).
- Full lab success (finished run + `<project>/data/` CSV) needs webui (G1/G2).

## Pipeline (5 steps)

1. **Hear** — NL / PDF Method / existing project folder
2. **Clarify** — **one question per turn**. Coach with `references/experiment-design-norms.md`:
   - **Design first** (几×几 / within·between·mixed / continuous IVs) — not paradigm brand names
   - then IV → DV → control → random → practice → script → response → trial
   - **OutPath last** — default `./experiments/<slug>/`; never Desktop; never skill install tree
   - Stop: 满意 / 就这样 / 开始写 / 别问了按默认 / core items clear (rest defaulted)
3. **Write** — `<projectDir>/<folderName>.psyclaw` at agreed OutPath
4. **Validate** — schema / structure (G0)
5. **Optional handoff** — only if user asks 能跑吗 / 跑一下 → load `psyclaw-webui`

Edit path: open existing marker → change → rewrite → validate. Do not re-ask OutPath.

## Intent map

| User | Do |
|------|-----|
| 做一个… | steps 1→4 |
| 改… | edit marker → 3→4 |
| 能跑吗 / 跑一下 | handoff webui |
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

## References (load on demand)

| File | When |
|------|------|
| `references/skill-pipeline.md` | pipeline detail |
| `references/skill-pipeline-and-inputs.md` | inputs, marker, OutPath |
| `references/experiment-design-norms.md` | clarify checklist (Design first, OutPath last) |
| `references/install-orchestrator.md` | install / doctor / short name |
| `references/path-c-webui-validation.md` | G0/G1/G2 + webui handoff gates |
| `references/user-conservative-workflow-preference.md` | one surgical fix per bug report |

## Marker content (minimal)

Emit design JSON the webui runner accepts: routines, flow/loops, components (text/image/keyboard/slider/…), conditions columns, session metadata as required by webui schema. Prefer fields already used by psyclaw-webui `design_compiler`; do not invent a second parallel schema.

When unsure of a field: read webui schema / `path-c-webui-validation.md`, not legacy YAML→psyexp docs.

## Out of scope (this skill)

- PsychoPy Builder `.psyexp` generation pipelines
- Paper PDF batch libraries / replications workspace
- Bundling or installing PsychoPy itself
- Statistical analysis of subject data
