# psyclaw (Hermes skill)

[English](README.md) · [中文](README.zh-CN.md)

Turn a description (or paper Method) into a project folder with **`<folderName>.psyclaw`**.

- **Slash:** `/psyclaw`
- **GitHub:** https://github.com/Paradeluxe/psyclaw-skill
- **Not** the lab GUI — that is **[psyclaw-webui](https://github.com/Paradeluxe/psyclaw-webui)** (run subjects → CSV).

## User usage pipeline

One track. Install is separate (see below). This is **how people use** `/psyclaw` day to day.

```text
INPUT
  ├─ Natural-language description of the experiment
  ├─ Paper Method / PDF / HTML / paste   (fetch via browser-skill if needed)
  └─ Existing project folder + marker   (edit in place)

        ▼
CLARIFY  (one question per turn · coach)
  • Suggest standard defaults when the user is unsure
  • Design first (k×m, within/between/mixed, continuous IVs)
  • then IV → DV → control → random → practice → script → response → trial
  • OutPath last  (default ./experiments/<slug>/)
  • Stop when the user is satisfied, says write/defaults, or core items are clear

        ▼
WRITE + VALIDATE (G0)
  <projectDir>/<folderName>.psyclaw     # design JSON, not Builder .psyexp

        ▼
ASK RUN  (agent asks — do not wait for the user to invent the run request)
  "The design marker is ready. Run participants?"

        ├─ No  → stop (marker is enough)
        │
        └─ Yes → handoff psyclaw-webui (G1 finished → G2 project/data/*.csv)
                   • Run subjects in order (one after another)
                   • Participant ID / UID auto-assigned
                   • P_pilot does not consume production IDs
                   • Finished formal run → next ID + new UID
                   • When the agent drives the run: session.experimenter = AI identity
```

| User intent | What happens |
|-------------|--------------|
| Create an experiment | clarify → write G0 → **ask run** |
| Edit an existing design | edit marker → G0 → **ask run** |
| Run / multi-subject | sequential webui runs; auto ID; experimenter=AI if agent-run |
| Design only / do not run | stop after G0 |
| First-time full setup | doctor → consent → install gaps only |

**Not in scope for this skill:** half-run / “preview only a few trials” as a product mode (webui has Builder PREVIEW for components; lab success is full Start/Pilot + CSV). Statistics after CSV. Builder `.psyexp`.

### Deliverable on disk

```text
MyExp/
  MyExp.psyclaw          # required marker (folder basename + .psyclaw)
  data/                  # appears after runs (webui mirror)
  participants.json      # roster (webui)
```

| Gate | Meaning |
|------|---------|
| **G0** | Marker compiles (valid design JSON → PsychoPy script shape) |
| **G1** | Run status `finished` |
| **G2** | CSV under **`<project>/data/`** |

Skill alone = through G0 + the run question. Full lab success needs webui + PsychoPy.

## Install (not the usage pipeline)

```bash
hermes skills install psyclaw -y
# always-safe full id:
hermes skills install Paradeluxe/psyclaw-skill/skills/psyclaw -y
```

Then `/psyclaw` in a new session.

| | Installs | Does not install |
|--|----------|------------------|
| `hermes skills install …` | this skill → `/psyclaw` | webui, Flask venv, PsychoPy, browser-skill |
| Lab GUI | [psyclaw-webui](https://github.com/Paradeluxe/psyclaw-webui) separately | Hermes agent |
| Related | **browser-skill** optional (class-2 PDF/Method fetch) | not silent-installed |

First use / full lab setup: doctor gaps → **ask consent** → install only missing pieces. See `skills/psyclaw/references/install-orchestrator.md`.

## Repo layout

```text
psyclaw-skill/
  README.md            # English (default)
  README.zh-CN.md      # Chinese
  LICENSE
  NOTICE
  skills.sh.json
  skills/
    psyclaw/
      SKILL.md
      scripts/doctor.py
      references/   # pipeline, norms, webui handoff gates
```

## Doctor

```bash
python skills/psyclaw/scripts/doctor.py
```

## License

**AGPL-3.0** — [LICENSE](LICENSE). PsychoPy is separate — [NOTICE](NOTICE).
