# One install + first `/psyclaw` doctor (2026-07-18)

## Hard split

| Mechanism | Installs | Does **not** install |
|-----------|----------|----------------------|
| **`hermes skills install …`** | Skill under `~/.hermes/skills` → **`/psyclaw`** | webui app, Flask venv, PsychoPy |
| **Lab software install** | git/pip webui + deps + start | Hermes agent |
| **`psyclaw setup` / `install.py` (planned)** | Orchestrates both + doctor | Full PsychoPy binary (probe only) |

**Never claim** skills install alone deploys the GUI.

## First `/psyclaw` = doctor (user confirmed)

On first use (or when user says 全装 / 部署):

1. Check skill-side small deps / scripts runnable.
2. Check webui present (path or import) **if** lab software needed this turn.
3. Check PsychoPy python (`PSYCLAW_PSYCHOPY_PYTHON` / probe) **if** run needed.
4. Missing → report + **ask consent** (user policy) → install/deploy only what is missing.
5. Present → skip; do the task (write `<folderName>.psyclaw`).

Not every turn reinstalls. Updates: skill via `hermes skills check/update`; webui via git/pip; PsychoPy via its installer.

## `hermes skills install psyclaw` (short name)

Resolver: no `/` → search all sources → **exact** `name == psyclaw` → exactly one match installs.

To make short name work for others:

1. `name: psyclaw` in SKILL.md  
2. Publish where Hermes can search (tap / public GitHub / skills.sh / official)  
3. Prefer tap layout: `skills/psyclaw/SKILL.md` under the GitHub repo  
4. Avoid multiple exact name collisions  

Until then: full id e.g. `Paradeluxe/psyclaw-skill/skills/psyclaw` (after layout) or local copy already in Hermes skills.

Dev machine: skill already at `skills/research/psyclaw` — **edit in place**; install is for clean machines.

## Orchestrator steps (when script exists)

0. Install root  
1. `hermes skills install <psyclaw-id> -y` (+ optional browser-skill)  
2. Clone/pip webui  
3. venv + requirements  
4. PsychoPy probe — stop with link if missing  
5. Doctor (flask, psychopy import, :8876)  
6. Print slash, paths, start URL  

Agent on「帮我全装」: run orchestrator order; do not random soup. Network/clone: consent if user requires.

## Hermes market (brief)

- browse sources: official, skills-sh, github, clawhub, taps, URL  
- Team share: `hermes skills tap add owner/repo` then `install psyclaw`  
- `hermes bundles` = multi-skill slash load only — not webui install  
- `related_skills` recommends; does not auto-install  

Detail market checklist: `references/product-pipeline-and-hermes-market.md`.

## Layer roadmap

| Layer | Shape |
|-------|--------|
| A | git + venv + webui INSTALL.md |
| B | pip entry `setup|doctor|start` |
| C | zip / start.bat |

PsychoPy external every layer.
