# Local development layout

| Path | Role |
|------|------|
| `E:\hermes_playground\psyclaw-skill-src` | Git clone of `Paradeluxe/psyclaw-skill` (edit + push here) |
| `~\.hermes\skills\psyclaw-dev` | Local Hermes skill **`/psyclaw-dev`** (DEV checkout; not published name) |
| `~\.hermes\skills\psyclaw` | Hub install **`/psyclaw`** from GitHub |

Sync DEV after editing skill-src package:

```bash
# from git bash
rm -rf "$HOME/AppData/Local/hermes/skills/psyclaw-dev"
mkdir -p "$HOME/AppData/Local/hermes/skills/psyclaw-dev"
cp -a /e/hermes_playground/psyclaw-skill-src/psyclaw/. "$HOME/AppData/Local/hermes/skills/psyclaw-dev/"
# then set name: psyclaw-dev in SKILL.md frontmatter
```

Users:

```bash
hermes skills install Paradeluxe/psyclaw-skill/psyclaw -y
```
