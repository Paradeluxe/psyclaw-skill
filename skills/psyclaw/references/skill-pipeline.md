# `psyclaw` skill pipeline (2026-07-21)

One pipeline. Plain language first. Detail lives here; `SKILL.md` is the thin entry.

## Two products

| | `psyclaw` (skill) | `psyclaw-webui` (lab app) |
|---|---|---|
| Role | Write 说明书 | draw / run / CSV |
| GitHub | `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |
| Disk | skill dir | clone + venv — webui `docs/INSTALL.md` |

## Shared IR

```text
MyStroop/
  └── MyStroop.psyclaw    # folder basename + .psyclaw
```

- Design JSON (routines + flow), **not** `.psyexp`.
- Skill goal: produce/edit marker → **ask run**. Lab success needs webui.

## Canonical flow

```text
INPUT (NL | PDF/Method | existing folder)
  → [LIT INTENT?] ──yes──► FIND literature FIRST → paper-anchored clarify
  └──no───────────────────► Clarify (1 Q/turn · Design first · OutPath last)
  → Write + validate marker
  → ASK: 要跑被试吗？
       No  → stop
       Yes → webui sequential subjects
```

### Steps

1. **Hear** intent  
2. **Lit-first** (if lit intent) — land article/Method before design Qs  
3. **Clarify** — norms coach; paper-anchored if lit landed  
4. **Write** folder + `<folderName>.psyclaw` at OutPath  
5. **Validate** → marker ready  
6. **Ask run** (unless user already said run/don't-run)  
7. **Handoff** if yes → prep checklist → webui → `finished` + CSV  

Write success = step 5. Lab success = step 7. Multi-subject = sequential runs. No half-run mode.

## Lit-first gate

If literature intent → **first real work is retrieval**, not the design checklist.

### Intent recognition

Scan first substantive message + later turns. **Any** hit → lit-first **on**.

| Class | Examples |
|-------|----------|
| Explicit ref | 参考、依据、按照、基于、改编自、复现、复制、跟…一样、照着…做 |
| Paper words | 文献、论文、研究、Method、方法部分、前人、经典实验、发表、期刊 |
| Citation | 作者+年份、et al.、DOI、PMID、arxiv、publisher/PDF URL |
| Named + source | 「经典 Stroop」「按 Posner」且带出处意味 |
| Search ask | 搜一下、找一篇、帮我查 |
| File given | PDF/路径/粘贴 Method → lit on, **read file** |

| Not lit | Examples |
|---------|----------|
| Pure task | 「做一个红绿 Stroop」无参考/文献 |
| Tool/run only | 「更新 webui」「跑被试」 |
| Vague「专业」 | no paper → norms defaults, **don't** random-search |

**Ambiguous**（「做一个专业的 Stroop」）→ one Q: 文献 or 通用默认？  
**Do not** wait for magic word `搜一下` if 参考/复现/文献 already said.

| Detect | First actions | Do not yet |
|--------|---------------|------------|
| Lit on | search → save `refs/` → short recap | Ask 几×几 / IV / N |
| PDF/path/paste | Read → recap | Ignore file; generic defaults |
| Lit off | Normal clarify | Random paper search |

**Pass:** path under `./refs/` or `<project>/refs/` (PDF/HTML/`method-extract.md`) **or** user waived + pasted Method.  
**Fail:** claimed 按文献 but no search/read — **invalid**; do it now.

**Where:** before OutPath → `./refs/` (or `~/psyclaw/refs/`); after project → `<project>/refs/` + note in marker.

## Net fetch order

**Triggers:** 参考/复现 · DOI/URL/标题要全文 · 搜一下 · 只有引用没有正文.

| Step | Action |
|------|--------|
| 1 | Host web search / fetch first; save file when possible |
| 2 | Fail (no hit / abstract-only / paywall) → **browser-skill** |
| 2a | Installed → open publisher/OS/user-allowed source → PDF or Method |
| 2b | Missing → **ask once** to install; never silent-install |
| 3 | **Success gate:** local path or saved Method extract. “I looked” without content = fail |
| 4 | Tell user path + one-line source → paper-anchored clarify |
| 5 | Still fail → reason + paste fallback; **do not invent Method** |

Prefer OA (author MS, OSF, PMC) before giving up. Host search before browser. No net on pure-NL no-lit.

### Class-2 after land

1. Recap what paper fixes  
2. Clarify **only gaps / user changes**  
3. Shrug → **paper values first**  
4. Write; citation + path + deviations in notes  

## Intent map

| User | Flow |
|------|------|
| 做一个…（无文献） | 1→3→…→6 |
| 做一个…+文献/复现 | **2 first** → 3 paper-anchored → …→6 |
| 改… | open marker → edit → 4→6 |
| 要跑 / 多人 | handoff webui; experimenter=AI if agent-run |
| 不要跑 / 只要说明书 | stop at marker ready |
| 全装 / 首次 | `install-orchestrator.md` |
| 更新 skill / psyclaw | skill + related + webui 整段 |
| 更新 webui | webui only |

## Clarify stop / priority

- Priority: **Design** first; **OutPath** last (skip if editing existing).  
- Stop: 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 / core items clear.  
- Norms: `experiment-design-norms.md`.

## OutPath

- New: `./experiments/<folderName>/` under session cwd  
- Marker: `<projectDir>/<folderName>.psyclaw`  
- Never Desktop; never skill install tree  
- Edit existing → path known, do not re-ask  

## Naming

| Name | Meaning |
|------|---------|
| Skill id | **`psyclaw`** (do not rename to `psyclaw-skill` unless asked) |
| GitHub | `Paradeluxe/psyclaw-skill` · layout `skills/psyclaw/` |
| Agent local | e.g. `~/.config/opencode/skills/psyclaw` |

## Language / explain

- Match user's first substantive message (chat + marker-facing text).  
- Short lists + concrete paths when stuck; no multi-path architecture dumps in chat.
