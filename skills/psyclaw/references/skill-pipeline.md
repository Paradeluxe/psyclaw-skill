# `psyclaw` skill pipeline + inputs (product, 2026-07-20)

User wants **simple** explanations first (plain language when stuck). One pipeline only.

## Two products (do not merge)

| | `psyclaw` (skill) | `psyclaw-webui` (lab app, **not** a skill) |
|---|---|---|
| Role | Write experiment “说明书” for agents | Lab software: draw / run / CSV |
| Id | skill id **`psyclaw`** | product name `psyclaw-webui` |
| GitHub | `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |
| Disk | repo `skills/psyclaw/` | clone + venv; `docs/INSTALL.md` |

## Shared IR (single track)

```text
MyStroop/
  └── MyStroop.psyclaw    # folder basename + .psyclaw
```

- Content = design JSON (routines + flow), **not** Builder XML / `.psyexp`.
- Canonical: **`<folderName>.psyclaw`** (not fixed `design.psyclaw`; webui migrates legacy).
- Skill goal: **produce / edit this file**, then **ask** whether to run.
- Single track only: marker → ask run → optional webui. No alternate “paths.”

## User usage pipeline (canonical)

```text
INPUT (NL | PDF/Method | existing folder)
  → Clarify (1 Q/turn · coach + defaults · Design first · OutPath last)
  → Write + validate marker
  → Agent ASKS: 要跑被试吗？
       No  → stop at marker
       Yes → webui sequential subjects (run finished + data on disk)
             auto ID/UID · P_pilot free · finished → next ID
             agent-driven → session.experimenter = AI identity
```

Clarify = user satisfaction **and** norms coach (see `experiment-design-norms.md`) — give defaults when unsure.  
Priority: **Design** first; **OutPath** last before write (skip if editing an existing folder).  
Stop signals: 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 / Design·IV·DV·response·trial clear with remaining norms defaulted or waived.

Write success = **valid marker + project folder at agreed path** (**marker ready**), then **ask run**.  
Full lab success (run finished + `<project>/data/` CSV) needs webui/runner.  
Multi-subject = sequential runs (not a special batch mode). No half-run product mode.

## Six steps

1. **Hear** intent (NL / PDF Method / existing folder)
2. **Clarify until satisfied + norms gate** — **one question per turn** (never stack Qs). Coach via **`experiment-design-norms.md`**: suggest defaults when unsure; lock **Design** first (几×几 / within·between·mixed / continuous IVs), then IV→…→trial; **OutPath last** (default `./experiments/<slug>/`, never Desktop / never skill install dir). Stop signals or critical items answered/defaulted. User override wins; log deviations.
3. **Write** project folder + `<folderName>.psyclaw` at the agreed **OutPath**
4. **Validate** schema / structure (**marker ready**)
5. **Ask run** — agent asks once the marker is ready (do not only wait for the user to say 能跑吗). Skip ask only if this turn already answered run/don't-run.
6. **Handoff** (if yes) → **run prep checklist** (project · webui · which PsychoPy path/source · System gate; same facts as webui System) → start/use **psyclaw-webui** → `finished` + CSV under `<project>/data/`

Write success = through step **4**. Lab success = through step **6**.

## Intent map

| User says | Do |
|-----------|-----|
| 做一个… | 1→5 (ask run after marker ready) |
| 改… | open existing marker → edit → 3→5 |
| 要跑 / 跑一下 / 多人 | handoff webui; sequential; experimenter=AI if agent-run |
| 不要跑 / 只要说明书 | stop once marker is ready |
| 全装 / 首次 | doctor — `install-orchestrator.md` |
| 更新 skill / 升级 psyclaw | skill + related + **webui 整段** — `install-orchestrator.md` |
| 更新 webui | webui + 其依赖（条件 PsychoPy）；不动 skill |

## Three input classes

| # | Input | Companion skill |
|---|--------|-----------------|
| 1 | User NL description of the experiment | none |
| 2 | Materials (PDF Method, HTML, pasted text) **or user says follow/replicate a paper** | **`browser-skill`** (and/or academic-search) to **fetch** — then return to `psyclaw` |
| 3 | Existing project folder with marker | edit in place |

### Class-2 / literature mode

When the user **names prior literature as the reference** (复现、参考、按 Method、跟某文一样) **or** asks to search online:

1. **Acquire Method / paper (proactive net path)** — see below; do not stall on “请自己粘贴” as the only option.
2. Recap what the paper fixes (design, IV/DV, trial N, keys, timing…).
3. **Clarify only what the paper leaves open or what the user wants to change.**
4. Shrug defaults → **paper values first** (see `experiment-design-norms.md` § Literature-anchored).
5. Write marker; note citation + any deviations.

Do **not** run a generic 10-question interview that ignores the Method.

### Net fetch — search first, then browser-skill; article must land

**Triggers:** 参考/复现某文 · DOI/URL/标题要全文或 Method · 「搜一下」「联网查」· 只有引用没有正文.

**Strict order (same session):**

| Step | Action |
|------|--------|
| 1 | Detect need for literature / network |
| 2 | **First: host联网搜索 / fetch** — use this CLI’s built-in web search, URL fetch, academic search, etc. Prefer open PDF/HTML; **save file** when possible (e.g. `experiments/<slug>/refs/` or user-agreed path). |
| 3 | **If step 2 fails** (no hit, abstract-only, paywall, broken link) → **browser-skill**: |
| 3a | Already installed → drive browser to publisher / OS / Sci-Hub-policy-compliant sources the user allows → download PDF or copy Method |
| 3b | Not installed → **ask once** to install `browser-skill` (why: 抓全文). Yes → install then fetch. No → paste / local file only |
| 4 | **Success gate:** agent can point to a **local path** (PDF/HTML/txt extract) **or** an explicitly saved Method excerpt file. “I looked online” without content **does not count**. |
| 5 | Tell user the path + one-line source. Then paper-anchored clarify. |
| 6 | Still fail → honest reason + paste fallback; **do not invent Method details** |

**Landing rules:**

- Prefer: `<project>/refs/<slug>.pdf` (or `.html` / `method-extract.md`) once OutPath known; if project not chosen yet → `./refs/` under cwd or temp then move into project on write.
- Record citation + file path in marker `design_notes`.
- Paywall: try legal OA (author manuscript, OSF, PubMed Central) before giving up; never claim you have the PDF if you do not.

**Rules:**

- Host search **before** browser-skill; browser-skill is the **escalation**, not the first toy.
- `related_skills: [browser-skill]` — offer when step 3 needs it; **never silent-install**.
- Do not merge browser into psyclaw package.
- Do not net-browse pure NL designs with no lit/search ask.

## OutPath defaults

- New: `./experiments/<folderName>/` under session cwd (or operator-given base)
- Marker: `<projectDir>/<folderName>.psyclaw` (`folderName` = basename)
- Never default to Desktop; never write into the agent skill install tree
- Edit existing project → path already known, do not re-ask

## First use = doctor

Detect missing small deps / webui / PsychoPy when needed → report → consent → install only gaps. Not every turn. See `install-orchestrator.md`.

## Naming / slash / GitHub

| Name | Meaning |
|------|---------|
| Skill id | **`psyclaw`** |
| GitHub skill repo | **`Paradeluxe/psyclaw-skill`** (edit this package) |
| Agent local | skill directory (e.g. `~/.agents/skills/psyclaw`) |
| Papers vault (optional) | separate data folder — **not** the skill package |

Do **not** rename the skill id to `psyclaw-skill` unless user asks.

Installing `psyclaw` works when searchable sources have exactly one skill named `psyclaw`. Repo layout is `skills/psyclaw/`. Full fallback: `Paradeluxe/psyclaw-skill/skills/psyclaw`. See `install-orchestrator.md`.

## Language

Match the **user's first substantive message** for chat + on-screen experiment text (instructions / thanks / prompts). Override if they ask to switch. No agent-default language. Detail: `SKILL.md` Agent rules.

## Explain preference

- Prefer short lists and concrete file names when the operator is confused
- No multi-path architecture dumps in chat; keep technical detail in `references/`
- Prefer concrete file names over architecture lectures

## Nature-style pattern

Like `nature-figure`: skills install = light cookbook; large runtime external; missing → stop + install commands, no fake substitute backend.

## Cross-CLI later

Enough product: **schema + CLI around same IR**. `SKILL.md` alone ≠ cross-CLI package.
