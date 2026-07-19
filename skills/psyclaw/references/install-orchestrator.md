# One install + first-use doctor (2026-07-18)

## Hard split

| Mechanism | Installs | Does **not** install |
|-----------|----------|----------------------|
| **Skill install** | Skill files → `psyclaw` | webui app, Flask venv, PsychoPy |
| **Lab software install** | git/pip webui + deps + start | AI agent |
| **`psyclaw setup` / `install.py` (planned)** | Orchestrates both + doctor | Full PsychoPy binary (probe only) |

**Never claim** skills install alone deploys the GUI.

## First use = doctor (user confirmed)

On first use (or when user says 全装 / 部署):

1. Check skill-side small deps / scripts runnable.
2. Check webui present (path or import) **if** lab software needed this turn.
3. Check PsychoPy python (`PSYCLAW_PSYCHOPY_PYTHON` / probe) **if** run needed.
4. Missing → report + **ask consent** (user policy) → install/deploy only what is missing.
5. Present → skip; do the task (write `<folderName>.psyclaw`).

Not every turn reinstalls. Updates: skill via git pull; webui via git/pip; PsychoPy via its installer.

## Skill installation (short name)

Resolver: search all sources → **exact** `name == psyclaw` → exactly one match installs.

To make short name work for others:

1. `name: psyclaw` in SKILL.md  
2. Repo layout: `skills/psyclaw/` (this repo)  
3. Public git push; register in skill registry  
4. Avoid multiple exact name collisions  

Full id (always): `Paradeluxe/psyclaw-skill/skills/psyclaw`  
Short: `psyclaw` after unique registry resolve.

Maintainers edit `skills/psyclaw/` in this repository; end users install via their agent's skill installer.

## Orchestrator steps (when script exists)

0. Install root  
1. Install psipec skill (`Paradeluxe/psyclaw-skill/skills/psyclaw`) (+ optional browser-skill)  
2. Clone/pip webui  
3. venv + requirements  
4. PsychoPy probe — stop with link if missing  
5. Doctor (flask, psychopy import, :8876)  
6. Print skill name, paths, start URL  

Agent on「帮我全装」: run orchestrator order; do not random soup. Network/clone: consent if user requires.

## Skill registry (brief)

- Browse sources: official registries, GitHub, skill directories  
- Team share: add repo source then install `psyclaw`  
- `related_skills` recommends; does not auto-install  

Registry/short-name notes: this file.

## Layer roadmap

| Layer | Shape |
|-------|--------|
| A | git + venv + webui INSTALL.md |
| B | pip entry `setup|doctor|start` |
| C | zip / start.bat |

PsychoPy external every layer.
