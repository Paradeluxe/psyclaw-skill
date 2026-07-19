# `/psyclaw` skill pipeline (product, 2026-07-19)

## Two products (do not merge)

| | `/psyclaw` | `/psyclaw-webui` |
|---|---|---|
| Role | Write experiment “说明书” for agents | Lab software: draw / run / CSV |
| Slash | **`/psyclaw`** (Hermes skill id; keep this name) | `/psyclaw-webui` |
| GitHub | `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |
| Disk | Hermes `skills/psyclaw` · edit `Paradeluxe/psyclaw-skill` | `Paradeluxe/psyclaw-webui` |

## Shared IR (single track)

On-disk project:

```text
MyStroop/
  └── MyStroop.psyclaw    # folder name + .psyclaw (webui rule)
```

- Content = design JSON (routines + flow), **not** Builder XML.
- Skill goal: **produce / edit this file**, then **ask** whether to run.
- Single track only: marker → ask run → optional webui. No alternate “paths.”

## User usage pipeline (canonical)

```text
INPUT (NL | PDF/Method | existing folder)
  → Clarify (1 Q/turn · coach + defaults · Design first · OutPath last)
  → Write + Validate G0
  → Agent ASKS: 要跑被试吗？
       No  → stop at marker
       Yes → webui sequential subjects
             auto ID/UID · P_pilot free · finished → next ID
             agent-driven → session.experimenter = AI identity
```

No half-run product mode. Multi-subject = sequential Starts, not a special batch product.

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

## Explain preference

- Prefer short lists and concrete file names when the operator is confused
- No multi-path architecture dumps in chat; keep technical detail in `references/`
- Prefer concrete file names over architecture lectures

## Cross-CLI later

Enough product: **schema + CLI around same IR**. Hermes `SKILL.md` alone ≠ cross-CLI package.
