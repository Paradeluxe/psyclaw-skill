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
  → [LIT INTENT?] ──yes──► FIND literature FIRST (search → browser → file on disk)
  │                         then paper-anchored clarify
  └──no───────────────────► Clarify (1 Q/turn · Design first · OutPath last)
  → Write + validate marker
  → Agent ASKS: 要跑被试吗？
```

### Lit-first gate (do not skip)

If **literature intent** is detected in the user need, the agent’s **first real work** is retrieval — **not** the design checklist.

#### Intent recognition (必做，读用户原话)

Scan the **first substantive message** and later turns. Hit **any** row → lit-first **on**.

| Signal class | Examples (zh / en, not exhaustive) |
|--------------|-------------------------------------|
| **Explicit ref** | 参考、依据、按照、基于、改编自、复现、复制、跟…一样、照着…做 |
| **Paper words** | 文献、论文、研究、Method、方法部分、前人、经典实验、发表、期刊 |
| **Citation shape** | 作者+年份、et al.、DOI、PMID、arxiv、URL 到 publisher/PDF |
| **Named paradigm + source** | 「经典 Stroop」「Eriksen 侧翼」「按 Posner 线索」且带出处/文献意味 |
| **Search ask** | 搜一下、找一篇、帮我查、有没有现成 paradigm 论文 |
| **File already there** | 用户给了 PDF/路径/粘贴 Method → lit on, **read file** (search optional) |

| **Not** lit intent (stay on normal clarify) | Examples |
|-----------------------------------------------|----------|
| Pure task ask | 「做一个红绿字色 Stroop」「2×2 按键实验」且无参考/文献/复现 |
| Only tool/run | 「更新 webui」「跑被试」 |
| Vague “专业一点” | 无具体文献指向 → 用 norms 默认，**不**乱搜论文 |

**Ambiguous:** e.g. 「做一个专业的 Stroop」→ **one short Q**: 要不要按某篇经典文献做，还是按通用默认？  
- 要文献 → lit-first immediately  
- 通用 → normal clarify  

**Do not** wait for the user to say the magic word `搜一下` if they already said 参考/复现/文献.

| Detect | First actions | Do **not** yet |
|--------|---------------|----------------|
| Lit intent on | Web search → save under `refs/` → short recap | Ask 几×几 / IV / trial N |
| User gave PDF/path/paste | Read → recap | Ignore file; generic defaults |
| Lit intent off | Normal clarify | Random paper search |

**Pass lit-first when:** local path under `./refs/` or `<project>/refs/` (PDF/HTML/`method-extract.md`) **or** user waived net and pasted Method.  
**Fail:** claimed “按文献” but no search/read and no file — **invalid**; search/read **now**.

**Where files go:** before OutPath → `./refs/` (or `~/psyclaw/refs/` if you already use that home); after project chosen → `<project>/refs/` and note path in marker.

Clarify = user satisfaction **and** norms coach (see `experiment-design-norms.md`) — give defaults when unsure.  
Priority after lit gate: **Design** first; **OutPath** last before write (skip if editing an existing folder).  
Stop signals: 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 / Design·IV·DV·response·trial clear with remaining norms defaulted or waived.

Write success = **valid marker + project folder at agreed path** (**marker ready**), then **ask run**.  
Full lab success (run finished + `<project>/data/` CSV) needs webui/runner.  
Multi-subject = sequential runs (not a special batch mode). No half-run product mode.

## Steps

1. **Hear** intent (NL / PDF Method / existing folder)
2. **Lit-first (conditional but hard)** — if lit intent in user need → **search/fetch until article or Method extract is landed** (or user waived). **No design Qs before this passes.** See § Lit-first + § Net fetch.
3. **Clarify until satisfied + norms gate** — **one question per turn**. If lit landed → **paper-anchored** (`experiment-design-norms.md`). Else coach generics. Design first; OutPath last.
4. **Write** project folder + `<folderName>.psyclaw` at the agreed **OutPath**
5. **Validate** schema / structure (**marker ready**)
6. **Ask run** — once marker ready (unless user already said run/don't-run).
7. **Handoff** (if yes) → run prep checklist → **psyclaw-webui** → `finished` + CSV under `<project>/data/`

Write success = through step **5**. Lab success = through step **7**.

## Intent map

| User says | Do |
|-----------|-----|
| 做一个…（无文献） | 1→3→…→6 |
| 做一个…且要文献/复现/参考 | **2 first (find lit)** → 3 paper-anchored → …→6 |
| 改… | open existing marker → edit → 4→6 |
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

When the user **names prior literature** (复现、参考、按 Method、跟某文一样) **or** asks to search online — **including when buried inside “帮我做一个…参考经典…”**:

0. **Immediate lit-first** (same turn as detection): run § Net fetch until file lands.  
1. Recap what the paper fixes (design, IV/DV, trial N, keys, timing…).  
2. **Clarify only gaps / user changes** (paper-anchored).  
3. Shrug → **paper values first**.  
4. Write marker; citation + file path + deviations in notes.

Do **not** start the generic interview before step 0 completes.

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
