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
2. Repo layout: `skills/psyclaw/` (this repo — tap + skills.sh friendly)  
3. Public git push; bootstrap skills.sh: `npx skills add Paradeluxe/psyclaw-skill --skill psyclaw -y`  
4. Avoid multiple exact name collisions  

Full id (always): `Paradeluxe/psyclaw-skill/skills/psyclaw`  
Short: `hermes skills install psyclaw` after unique skills.sh/tap resolve.

Dev: edit `<psyclaw-skill-repo>\skills\psyclaw`; hub install is for clean machines.

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
