---
name: psyclaw
version: 0.3.11
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
**psyclaw-webui** draws / runs / CSV — lives in the same repo under `webui/`.

| | Skill | Lab app |
|---|--------|--------|
| Path | `skills/psyclaw/` | `webui/` subdir |
| GitHub | `Paradeluxe/psyclaw` | `Paradeluxe/psyclaw` |
| Success | project + valid marker | run `finished` + `<project>/data/` CSV |

```text
MyStroop/
  ├── MyStroop.psyclaw
  └── .psyclaw-session.json   # pipeline state (file wins over chat)
```

## Pre-flight (every load)

Before the pipeline, a quick dep check (≤5s). Skip if already done this session.

1. **Skill-side deps**: check Python, scripts runnable.
2. **WebUI present?** Fast path: first try `~/.psyclaw/config.json` → `webui_root` (cached by `start.py` / `user_config.py remember`). If valid → instant hit. Else fall back to full resolution (`install-orchestrator.md` § Webui location policy).
3. **Missing?** Ask **one** question: "PsyClaw webui 还没装，现在装吗？" — yes → `install-orchestrator.md` § First use doctor. no → continue with skill-only mode.
4. **All OK** → silent, proceed to pipeline.

## Pipeline

```text
[pre-flight OK?] → INPUT → [lit intent?] FIND lit first → Clarify (1 Q/turn) → Write+validate → ASK 要跑被试吗？
         yes: search→browser-skill→file on disk → paper-anchored clarify
         run yes → webui sequential (experimenter=AI if agent-driven)
```

**State file:** read/write `.psyclaw-session.json` each step — `session-state.md`. No half-run mode. Multi-subject = sequential runs.

## Intent → load (flow detail: `skill-pipeline.md` only)

| User | Load first |
|------|------------|
| 做一个…（无文献） | `norms-core.md` (+ `session-state.md`) |
| 参考/复现/文献/Method/DOI/搜… | `skill-pipeline.md` → lit gate → `norms-core.md` |
| 改… | marker + `norms-core.md` (touched) + `marker-validate.md` |
| 要跑 / 多人 | `run-prep.md`（+ `api-notes.md` if calling webui） |
| 不要跑 / 只要说明书 | — (stop; session `ask_run=no`) |
| 全装 / 首次 / 更新 skill·webui | `install-orchestrator.md` |

## Hard rules

1. **Language** = user's first substantive message (chat + on-screen text). Override if they switch.
2. **Session state file** — on start, read `.psyclaw-session.json` (project dir if known, else cwd). After every step, update it. Never under skill install tree. Schema/transitions: `session-state.md`. File wins over chat memory.
3. **One question per turn** after lit gate (topic cluster OK). Design first, OutPath last (`./experiments/<slug>/`; never Desktop; never skill tree).
4. **Lit gate** — only real lit intent (出处/Method/DOI/复现/搜全文) → fetch until `refs/` before Design Q. **Not lit:** pure task、可行性聊聊、工具/开跑、空「专业」— 见 pipeline 负面样例. Ambiguous → one Q; no quick answer → **norms defaults** (don't stall).
5. **Stop clarify** on 满意/就这样/开始写/按默认, or core Design·IV·DV·response·trial clear (rest defaulted/paper-filled).
6. **User override wins**; log deviations in marker notes. Plain language; no architecture dumps.
7. **After every marker write/edit** → validate (`marker-validate.md`) → ask 要跑被试吗 only if `ask_run` still `null`.
8. **Before run** → user checklist only — `run-prep.md`. API/compile → `api-notes.md`. Failures → `failure-playbooks.md`.
9. **browser-skill** = related; offer install if missing; never silent-install; no browse on pure-NL no-lit.
10. **Platform > paradigm hardcoding.** No release/tag/push without approval.
11. **Bug / narrow ask** → one surgical fix — `user-conservative-workflow-preference.md`.
12. **Install/update** → `install-orchestrator.md` only. Skill never freestyle-upgrades PsychoPy.

## Marker (minimal)

Design JSON webui `design_compiler` accepts: `routines`, `flow`/loops, components, conditions, session fields. Do not invent a parallel schema.

- **New marker:** copy/adapt `references/marker-stub.psyclaw` (do not freestyle empty JSON).
- **After every write/edit:** run `references/marker-validate.md` hard checks → then ask-run.
- Unsure of component types → `webui-handoff.md` / live webui schema.

Optional (only if user asks): `seed`, `exclusion_rules` (flag-only default).

## Load on demand

| File | When |
|------|------|
| `references/skill-pipeline.md` | lit-first, net fetch, OutPath, naming, full steps |
| `references/session-state.md` | start/resume + every step (state file) |
| `references/session-stub.json` | first create of `.psyclaw-session.json` |
| `references/norms-core.md` | every clarify / write (default norms) |
| `references/norms-counterbalance.md` | item 5 / 随机·拉丁方·分块 |
| `references/norms-trial-n.md` | item 9 / trial N · 时长 · 被试 N |
| `references/norms-marker-map.md` | write-time field mapping |
| `references/experiment-design-norms.md` | index only (points at norms-*) |
| `references/marker-stub.psyclaw` | starting a new marker |
| `references/marker-validate.md` | after every write/edit |
| `references/webui-handoff.md` | handoff index |
| `references/run-prep.md` | ask-run yes — user checklist |
| `references/api-notes.md` | webui API / compile / CSV |
| `references/failure-playbooks.md` | paywall / webui down / compile / CSV / session |
| `references/install-orchestrator.md` | 全装 / 更新 / doctor |
| `references/user-conservative-workflow-preference.md` | bug / narrow fix |

## Out of scope

`.psyexp` pipelines · paper batch libraries · bundling PsychoPy · stats analysis · half-run lab modes
