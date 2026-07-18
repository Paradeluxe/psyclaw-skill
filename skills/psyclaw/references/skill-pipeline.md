# `/psyclaw` skill pipeline (product, 2026-07-18)

## Two products (do not merge)

| | `/psyclaw` | `/psyclaw-webui` |
|---|---|---|
| Role | Write experiment “说明书” for agents | Lab software: draw / run / CSV |
| Slash | **`/psyclaw`** (Hermes skill id; keep this name) | `/psyclaw-webui` |
| GitHub | `Paradeluxe/psyclaw-skill` (renamed from PsyClaw) | `Paradeluxe/psyclaw-webui` (private) |
| Disk | Hermes `skills/research/psyclaw` + workspace `psyclaw-skill` | `<psyclaw-webui-repo>` |

## Shared IR (single track)

On-disk project:

```
MyStroop/
  └── MyStroop.psyclaw    # folder name + .psyclaw (webui rule)
```

- Content = design JSON (routines + flow), **not** Builder XML.
- Skill goal: **produce / edit this file**.
- Do **not** lead with Path A/B/C jargon in operator-facing chat — use kitchen/recipe language if needed.

## Five steps

1. **Hear** intent (NL / PDF Method / existing folder)
2. **Clarify until satisfied + norms gate** — **one question per turn** (never stack Qs). Coach via **`experiment-design-norms.md`**: lock **Design** first (几×几 factorial, within/between/mixed, categorical vs continuous IVs), then IV levels, DV, control, randomize, practice, script, response, trial+load. Keep going until stop signals **or** critical items answered/defaulted. User override wins; log deviations. Not “one question then force-write.”
3. **Write** `<folderName>.psyclaw`
4. **Validate** schema / structure (G0)
5. **Optional handoff** to webui for real run + CSV (G1/G2)

Default skill success = through step **4** (folder + valid marker).  
Run/CSV only when user asks 「能跑吗 / 帮我跑」.

## Intent map

| User says | Do |
|-----------|-----|
| 做一个… | 1→4 package |
| 改… | open existing marker → edit → 3→4 |
| 能跑吗 / 跑一下 | handoff webui (load `psyclaw-webui`) |

## Explain preference

- Prefer short lists and concrete file names when the operator is confused
- No multi-path architecture dumps in chat; keep technical detail in `references/`
- Kitchen/recipe metaphors OK; Path A/B/C jargon only if asked

## Cross-CLI later

Enough product: **schema + CLI around same IR**. Hermes `SKILL.md` alone ≠ cross-CLI package.
