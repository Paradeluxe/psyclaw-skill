---
name: psyclaw
version: 0.3.5
author: Paradeluxe
license: AGPL-3.0
platforms: [windows, macos, linux]
description: >
  PsyClaw skill — turn NL or paper Method into a project folder with
  <folderName>.psyclaw (design JSON). Clarify + experiment-design norms,
  then write marker. After the marker is ready, ask whether to run subjects;
  handoff lab app psyclaw-webui for sequential runs + CSV (experimenter=AI when
  agent-driven). Not the lab GUI; not PsychoPy Builder XML.
tags: [psychology, psychopy, experiment-design, stimuli-generation, conversational]
related_skills: [browser-skill]
---

# PsyClaw (`psyclaw`)

Write the experiment **说明书** (marker file). Run subjects in the lab app **psyclaw-webui** (not a skill).

| | This skill | Lab software |
|---|--------|--------|
| Role | design → `<folderName>.psyclaw` | draw / run / CSV |
| Name | **`psyclaw`** | **psyclaw-webui** (Flask GUI) |
| GitHub | `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |
| Install | agent skill installer | git/venv — see webui `docs/INSTALL.md` |

Never merge install narratives. Skill install ≠ GUI deploy. Do not list webui under `related_skills`.

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
  → Clarify (1 Q/turn; Design first, OutPath last; lit → paper-anchored)
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
| 按这篇/参考/复现/Method/搜一下… | **host search first** → else browser-skill → **article on disk** → paper-anchored clarify → write → **ask run** |
| 改… | edit marker → validate → **ask run** |
| 要跑 / 跑一下 / 多人 | handoff lab app webui; sequential; experimenter=AI if agent-run |
| 不要跑 / 只要说明书 | stop once marker is ready |
| 全装 / 首次 | doctor — `references/install-orchestrator.md` |
| 更新 skill / 升级 psyclaw | **Skill 入口**: skill 本身 + related + **整段 webui 更新** — `references/install-orchestrator.md` |
| 更新 webui | **Webui 入口**: webui 代码 + 其依赖（PsychoPy 仅当 webui 要求）；不动 skill |

Edit path: open existing marker → change → rewrite → validate → **ask run again**. Do not re-ask OutPath.

## Agent rules

- **Language = user's language.** Match the language of the user's **first substantive message** for all chat (clarify, recap, ask-run) **and** marker-facing text (instructions, thanks, on-screen prompts, `design_notes` if prose). Mixed code-switch → follow the language used for the task description. Explicit override («用中文 / in English») wins for the rest of the session. Do not default to Chinese or English by agent habit.
- **One question per turn.** Coach with defaults; Design first, OutPath last (`./experiments/<slug>/`; never Desktop; never skill install tree).
- **Literature anchor:** if user points at prior work (paper/Method/复现/参考X), extract Method first; **ask only gaps**; **defaults = paper**, not generic table, unless paper silent or user overrides. Log reference + deviations in marker notes. Detail: `references/experiment-design-norms.md` § Literature-anchored.
- **Net / literature fetch (ordered, must land a file):** when user needs a paper / Method / DOI / “搜一下…”, **do not** only ask paste. Same session order:
  1. **Host web search / fetch first** (this CLI’s built-in search, WebFetch, academic search — whatever is already available). Aim to **download or save** PDF/HTML/Method text under the project or a clear temp path.
  2. If search finds nothing useful, paywall, or no full text → **browser-skill** next (if missing → **ask once** to install; never silent-install). Use it to open publisher/OS page and **get the article down**.
  3. **Done only when the article (or Method extract) is on disk or fully in context from a saved file** — path told to user. If still fail → say why + paste fallback.
  Detail: `references/skill-pipeline.md` § Net fetch.
- Stop clarify: 满意 / 就这样 / 开始写 / 别问了按默认 / OK go ahead / defaults please / core items clear (rest defaulted / paper-filled).
- Plain language when operator is confused; no multi-path architecture dumps.
- Platform > paradigm-specific hardcoding (Stroop/GoNoGo as data labels OK; do not hardcode paradigm compilers).
- User override wins; log design deviations in marker notes.
- No public release / tag / push without explicit approval.
- First use or 全装: doctor gaps → consent → install only missing pieces. Webui path order: `PSYCLAW_WEBUI_ROOT` → `~/.psyclaw/config.json` (`webui_root`) → `~/psyclaw/psyclaw-webui` → ask. After install/update **always** remember (`python scripts/user_config.py remember` or start.py).
- **更新两入口（嵌套）**:「更新 skill/psyclaw」= skill 本身 + related + **执行 webui 更新全段**。「更新 webui」= webui 代码 + 其库（PsychoPy 仅 webui 要求时）。Skill 禁止自行升 PsychoPy。Detail: `references/install-orchestrator.md`.
- After every successful marker write/edit: **ask** 要跑被试吗 (unless user already said run/don't-run this turn).
- Before run handoff: short **run prep checklist** (project, webui URL, **which PsychoPy python + source**, System gate) — same facts as webui System tab. Detail: `references/webui-handoff.md`.
- browser-skill = **related**, not core — load on class-2 / 联网需要; **offer install when missing**; do not silent-install; do not run browser on pure NL designs with no lit/net need.

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
