---
name: psyclaw
version: 0.3.6
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

**This skill** writes the experiment 说明书 (`<folderName>.psyclaw`).  
**psyclaw-webui** draws / runs / CSV — not a skill. Do not merge install stories.

| | Skill | Lab app |
|---|--------|--------|
| GitHub | `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |
| Success | project + valid marker | run `finished` + `<project>/data/` CSV |

```text
MyStroop/
  └── MyStroop.psyclaw
```

## Pipeline

```text
INPUT → [lit intent?] FIND lit first → Clarify (1 Q/turn) → Write+validate → ASK 要跑被试吗？
         yes: search→browser-skill→file on disk → paper-anchored clarify
         run yes → webui sequential (experimenter=AI if agent-driven)
```

No half-run mode. Multi-subject = sequential runs.

## Intent → action

| User | Do | Load first |
|------|-----|------------|
| 做一个…（无文献） | clarify → write → ask run | `experiment-design-norms.md` |
| 参考/复现/文献/Method/DOI/搜… | **lit first** → paper clarify → write → ask run | `skill-pipeline.md` then norms |
| 改… | edit marker → validate → ask run | marker + norms (touched only) |
| 要跑 / 多人 | handoff webui | `webui-handoff.md` |
| 不要跑 / 只要说明书 | stop at marker ready | — |
| 全装 / 首次 | doctor | `install-orchestrator.md` |
| 更新 skill / psyclaw | skill + related + **webui 整段** | `install-orchestrator.md` |
| 更新 webui | webui only（PsychoPy 仅 webui 要求时） | same |

## Hard rules

1. **Language** = user's first substantive message (chat + on-screen text). Override if they switch.
2. **One question per turn** after lit gate. Design first, OutPath last (`./experiments/<slug>/`; never Desktop; never skill tree).
3. **Lit gate** — 参考/复现/文献/论文/Method/DOI/按某文/作者年份… → **search/fetch until file in `refs/`** before any Design Q. Pure task ask → no forced search. Ambiguous「专业」→ one Q: 文献 or 默认. Detail: `skill-pipeline.md`.
4. **Stop clarify** on 满意/就这样/开始写/按默认, or core Design·IV·DV·response·trial clear (rest defaulted/paper-filled).
5. **User override wins**; log deviations in marker notes. Plain language; no architecture dumps.
6. **After every marker write/edit** → ask 要跑被试吗 (unless already said run/don't-run).
7. **Before run** → short prep checklist (project, webui URL, PsychoPy python+source, System gate) — `webui-handoff.md`.
8. **browser-skill** = related; offer install if missing; never silent-install; no browse on pure-NL no-lit.
9. **Platform > paradigm hardcoding.** No release/tag/push without approval.
10. **Bug / narrow ask** → one surgical fix — `user-conservative-workflow-preference.md`.
11. **Install/update** → `install-orchestrator.md` only. Skill never freestyle-upgrades PsychoPy.

## Marker (minimal)

Design JSON webui `design_compiler` accepts: routines, flow/loops, components, conditions, session fields. Do not invent a parallel schema. Unsure → read webui schema / `webui-handoff.md`.

Optional (only if user asks): `seed`, `exclusion_rules` (flag-only default).

## Load on demand

| File | When |
|------|------|
| `references/skill-pipeline.md` | lit-first, net fetch, OutPath, naming, full steps |
| `references/experiment-design-norms.md` | every clarify / write |
| `references/webui-handoff.md` | ask-run yes / handoff |
| `references/install-orchestrator.md` | 全装 / 更新 / doctor |
| `references/user-conservative-workflow-preference.md` | bug / narrow fix |

## Out of scope

`.psyexp` pipelines · paper batch libraries · bundling PsychoPy · stats analysis · half-run lab modes
