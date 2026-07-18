# psyclaw (Hermes skill)

AI / agent skill for psychology experiments: turn a description (or paper Method text) into a project folder with **`<folderName>.psyclaw`**.

- **Slash command:** `/psyclaw`
- **GitHub:** https://github.com/Paradeluxe/psyclaw-skill
- **Not** the lab GUI — that is **[psyclaw-webui](https://github.com/Paradeluxe/psyclaw-webui)** (run participants → CSV).

## Install (Hermes)

```bash
hermes skills install Paradeluxe/psyclaw-skill
```

Then start a **new** chat session (or reload skills) and run:

```text
/psyclaw
```

Inspect without installing:

```bash
hermes skills inspect Paradeluxe/psyclaw-skill
```

## What you get

| | |
|---|---|
| Skill package | `SKILL.md` + `scripts/` + `references/` + `templates/` + `examples/` |
| Agent entry | `/psyclaw` |
| Design handoff | **`<folderName>.psyclaw`** (JSON) for webui |

## Optional lab software

To run subjects on a PC, install **psyclaw-webui** separately (Flask + local PsychoPy). The skill can guide setup; it does not bundle PsychoPy.

## Doctor

```bash
python scripts/doctor.py
```

Checks that core script files exist and prints install identity. Does not require network.

## License

See repository / skill metadata (MIT intended for the skill package; third-party PsychoPy is separate).
