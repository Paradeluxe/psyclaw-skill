# psyclaw (Hermes skill)

Turn a description (or paper Method) into a project folder with **`<folderName>.psyclaw`**.

- **Slash:** `/psyclaw`
- **GitHub:** https://github.com/Paradeluxe/psyclaw-skill
- **Not** the lab GUI — that is **[psyclaw-webui](https://github.com/Paradeluxe/psyclaw-webui)** (run → CSV).

## Repo layout

```text
psyclaw-skill/
  README.md
  LICENSE
  NOTICE
  skills.sh.json
  skills/
    psyclaw/
      SKILL.md
      scripts/doctor.py
      references/   # pipeline, norms, webui handoff gates
```

## Install

```bash
hermes skills install psyclaw -y
# always:
hermes skills install Paradeluxe/psyclaw-skill/skills/psyclaw -y
```

Then `/psyclaw` in a new session.

## Deliverable

| | |
|---|---|
| Output | `MyExp/MyExp.psyclaw` (design JSON) |
| Run subjects | install **psyclaw-webui** separately |

## Doctor

```bash
python skills/psyclaw/scripts/doctor.py
```

## License

**AGPL-3.0** — [LICENSE](LICENSE). PsychoPy is separate — [NOTICE](NOTICE).
