# `psyclaw` skill pipeline + inputs (product, 2026-07-20)

User wants **simple** explanations first (plain language when stuck). One pipeline only.

## Two products (do not merge)

| | `psyclaw` | `psyclaw-webui` |
|---|---|---|
| Role | Write experiment “说明书” for agents | Lab software: draw / run / CSV |
| Skill id | **`psyclaw`** | `psyclaw-webui` |
| GitHub | `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |
| Disk | repo `skills/psyclaw/` · edit `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |

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
  → Write + Validate G0
  → Agent ASKS: 要跑被试吗？
       No  → stop at marker
       Yes → webui sequential subjects (G1/G2)
             auto ID/UID · P_pilot free · finished → next ID
             agent-driven → session.experimenter = AI identity
```

Clarify = user satisfaction **and** norms coach (see `experiment-design-norms.md`) — give defaults when unsure.  
Priority: **Design** first; **OutPath** last before write (skip if editing an existing folder).  
Stop signals: 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 / Design·IV·DV·response·trial clear with remaining norms defaulted or waived.

Write success = **valid marker + project folder at agreed path** (G0), then **ask run**.  
Full lab success (finished run + `<project>/data/` CSV) needs webui/runner.  
Multi-subject = sequential runs (not a special batch mode). No half-run product mode.

## Six steps

1. **Hear** intent (NL / PDF Method / existing folder)
2. **Clarify until satisfied + norms gate** — **one question per turn** (never stack Qs). Coach via **`experiment-design-norms.md`**: suggest defaults when unsure; lock **Design** first (几×几 / within·between·mixed / continuous IVs), then IV→…→trial; **OutPath last** (default `./experiments/<slug>/`, never Desktop / never skill install dir). Stop signals or critical items answered/defaulted. User override wins; log deviations.
3. **Write** project folder + `<folderName>.psyclaw` at the agreed **OutPath**
4. **Validate** schema / structure (G0)
5. **Ask run** — agent asks after G0 (do not only wait for the user to say 能跑吗). Skip ask only if this turn already answered run/don't-run.
6. **Handoff** (if yes) → load `psyclaw-webui` → G1 finished + G2 `<project>/data/*.csv`

Write success = through step **4**. Lab success = through step **6**.

## Intent map

| User says | Do |
|-----------|-----|
| 做一个… | 1→5 (ask run after G0) |
| 改… | open existing marker → edit → 3→5 |
| 要跑 / 跑一下 / 多人 | handoff webui; sequential; experimenter=AI if agent-run |
| 不要跑 / 只要说明书 | stop after G0 |
| 全装 / 首次 | doctor — `install-orchestrator.md` |

## Three input classes

| # | Input | Companion skill |
|---|--------|-----------------|
| 1 | User NL description of the experiment | none |
| 2 | Materials (PDF Method, HTML, pasted text) | **`browser-skill`** (and/or academic-search) to **fetch** — then return to `psyclaw` |
| 3 | Existing project folder with marker | edit in place |

### browser-skill = related, not core

- Put in `related_skills`; load when class-2 needs net download.
- **Do not** merge browser into psyclaw package or run browser on every `psyclaw` invoke.
- Installing browser skill is separate; skill may **recommend** related installs, never silent-install.

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
