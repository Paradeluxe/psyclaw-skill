# psyclaw (Hermes skill)

AI / agent skill for psychology experiments: turn a description (or paper Method text) into a project folder with **`<folderName>.psyclaw`**.

- **Slash command:** `/psyclaw`
- **GitHub:** https://github.com/Paradeluxe/psyclaw-skill
- **Not** the lab GUI — that is **[psyclaw-webui](https://github.com/Paradeluxe/psyclaw-webui)** (run participants → CSV).

## Repo layout

```text
psyclaw-skill/              # GitHub repo root
  README.md
  LICENSE
  skills.sh.json            # skills.sh category sidecar
  skills/
    psyclaw/                # installable skill directory
      SKILL.md
      scripts/
      references/
      templates/
      examples/
```

Tap-compatible (`skills/` parent). Hermes needs `owner/repo/<skill-dir>` (≥3 path segments).

## Install (Hermes)

```bash
# preferred — after skills.sh indexes unique name: psyclaw
hermes skills install psyclaw -y

# always works after git push (no tap)
hermes skills install Paradeluxe/psyclaw-skill/skills/psyclaw -y
```

New chat session (or reload skills), then:

```text
/psyclaw
```

Inspect without installing:

```bash
hermes skills inspect Paradeluxe/psyclaw-skill/skills/psyclaw
# or, after short-name resolve:
hermes skills inspect psyclaw
```

Optional lab share (per machine):

```bash
hermes skills tap add Paradeluxe/psyclaw-skill
hermes skills install psyclaw -y
```

## Bootstrap short-name index (authors / first installs)

skills.sh lists skills from install telemetry — no separate submit form:

```bash
npx skills add Paradeluxe/psyclaw-skill --skill psyclaw -y
hermes skills search psyclaw --json
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
python skills/psyclaw/scripts/doctor.py
```

Checks that core script files exist and prints install identity. Does not require network.

## License

**AGPL-3.0** — see [LICENSE](LICENSE). Same family as Praasper. PsychoPy is separate third-party software (see [NOTICE](NOTICE)).
