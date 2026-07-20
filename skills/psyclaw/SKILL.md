---
name: psyclaw
version: 0.3.4
author: Paradeluxe
license: AGPL-3.0
platforms: [windows, macos, linux]
description: >
  PsyClaw skill — turn NL or paper Method into a project folder with
  <folderName>.psyclaw (design JSON). Clarify + experiment-design norms,
  then write marker. After the marker is ready, ask whether to run subjects;
  handoff psyclaw-webui for sequential runs + CSV (experimenter=AI when
  agent-driven). Not the lab GUI; not PsychoPy Builder XML.
tags: [psychology, psychopy, experiment-design, stimuli-generation, conversational]
related_skills: [browser-skill, psyclaw-webui]
---

# PsyClaw (`psyclaw`)

Write the experiment **说明书** (marker file). Run subjects in **psyclaw-webui**.

| | Skill | WebUI |
|---|--------|--------|
| Role | design → `<folderName>.psyclaw` | draw / run / CSV |
| GitHub | `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |
| Install | skill installer (`Paradeluxe/psyclaw-skill/skills/psyclaw`) | separate lab install |
| Names | **`psyclaw`** | `psyclaw-webui` |

Never merge install narratives. Skill install ≠ GUI deploy.

## Shared IR

```text
MyStroop/
  └── MyStroop.psyclaw    # folder basename + .psyclaw
```

- Content = design JSON (routines + flow), **not** `.psyexp`.
- New work: **`<folderName>.psyclaw`** (webui migrates legacy `design.psyclaw`).
- Skill write success = project folder + valid marker (**marker ready**).
- Full lab success = run finished + CSV under `<project>/data/` (needs webui).

## Pipeline (summary)

```text
INPUT (NL | PDF/Method | existing folder)
  → Clarify (1 Q/turn, coach + defaults; Design first, OutPath last)
  → Write + validate marker
  → Agent ASKS: 要跑被试吗？
       No  → stop
       Yes → webui sequential subjects
             auto ID/UID · P_pilot free · finished → next ID
             agent-driven → session.experimenter = AI identity
```

Detail: `references/skill-pipeline.md`. Norms: `references/experiment-design-norms.md`.

No half-run product mode. Multi-subject = normal sequential runs, not a special batch UI.

## Intent map

| User | Do |
|------|-----|
| 做一个… | clarify → write marker → **ask run** |
| 改… | edit marker → validate → **ask run** |
| 要跑 / 跑一下 / 多人 | handoff webui; sequential; experimenter=AI if agent-run |
| 不要跑 / 只要说明书 | stop once marker is ready |
| 全装 / 首次 | doctor — `references/install-orchestrator.md` |

Edit path: open existing marker → change → rewrite → validate → **ask run again**. Do not re-ask OutPath.

## Agent rules

- **Language = user's language.** Match the language of the user's **first substantive message** for all chat (clarify, recap, ask-run) **and** marker-facing text (instructions, thanks, on-screen prompts, `design_notes` if prose). Mixed code-switch → follow the language used for the task description. Explicit override («用中文 / in English») wins for the rest of the session. Do not default to Chinese or English by agent habit.
- **One question per turn.** Coach with defaults; Design first, OutPath last (`./experiments/<slug>/`; never Desktop; never skill install tree).
- Stop clarify: 满意 / 就这样 / 开始写 / 别问了按默认 / OK go ahead / defaults please / core items clear (rest defaulted).
- Plain language when operator is confused; no multi-path architecture dumps.
- Platform > paradigm-specific hardcoding (Stroop/GoNoGo as data labels OK; do not hardcode paradigm compilers).
- User override wins; log design deviations in marker notes.
- No public release / tag / push without explicit approval.
- First use or 全装: doctor gaps → consent → install only missing pieces.
- After every successful marker write/edit: **ask** 要跑被试吗 (unless user already said run/don't-run this turn).
- browser-skill = related only (class-2 PDF fetch); do not silent-install or run browser every turn.

## Marker content (minimal)

Emit design JSON the webui runner accepts: routines, flow/loops, components (text/image/keyboard/slider/…), conditions columns, session metadata as required by webui schema. Prefer fields already used by psyclaw-webui `design_compiler`; do not invent a second parallel schema.

Optional reproducibility / analysis fields (write only when the user opts in or asks):

- `seed` (int, optional) — randomize trial/order generation. Absent → runner randomizes every run. Present → reproducible order.
- `exclusion_rules` (object, optional) — pre-registered exclusion plan, default flag-only (runner does not drop rows):
  ```json
  "exclusion_rules": {
    "trial_level": {"rt_outlier_sd": 2.5, "rt_min_ms": 100, "rt_max_ms": 3000, "action": "flag"},
    "participant_level": {"overall_accuracy_min": 0.60, "action": "exclude_after_run"}
  }
  ```

When unsure of a field: read webui schema / `webui-handoff.md`, not legacy YAML→psyexp docs.

## References (load on demand)

| File | When |
|------|------|
| `references/skill-pipeline.md` | pipeline detail, inputs, OutPath, naming |
| `references/experiment-design-norms.md` | clarify checklist (Design first, OutPath last) |
| `references/install-orchestrator.md` | install / doctor / short name |
| `references/webui-handoff.md` | compile / run finished / data on disk + webui handoff |
| `references/user-conservative-workflow-preference.md` | one surgical fix per bug report |

## Out of scope (this skill)

- PsychoPy Builder `.psyexp` generation pipelines
- Paper PDF batch libraries / replications workspace
- Bundling or installing PsychoPy itself
- Statistical analysis of subject data
- Half-run / partial-trial lab modes (not a webui product surface)
