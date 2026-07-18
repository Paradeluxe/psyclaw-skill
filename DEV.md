# Local development layout

| Path | Role |
|------|------|
| `E:\hermes_playground\psyclaw-skill-src` | Git clone of `Paradeluxe/psyclaw-skill` (edit + push here) |
| `skills/psyclaw/` | Published skill package (this repo) |
| `~\.hermes\skills\psyclaw-dev` | Local Hermes skill **`/psyclaw-dev`** (DEV checkout; not published name) |
| `~\.hermes\skills\psyclaw` | Hub install **`/psyclaw`** from GitHub |

## Daily publish

```bash
cd /e/hermes_playground/psyclaw-skill-src
# edit skills/psyclaw/
git add skills/psyclaw
git commit -m "..."
git push origin master
```

Full-path install works immediately after push:

```bash
hermes skills install Paradeluxe/psyclaw-skill/skills/psyclaw -y
```

Short name (`hermes skills install psyclaw`) needs skills.sh unique index — see README.

## Sync DEV after editing package

```bash
# from git bash
rm -rf "$HOME/AppData/Local/hermes/skills/psyclaw-dev"
mkdir -p "$HOME/AppData/Local/hermes/skills/psyclaw-dev"
cp -a /e/hermes_playground/psyclaw-skill-src/skills/psyclaw/. "$HOME/AppData/Local/hermes/skills/psyclaw-dev/"
# then set name: psyclaw-dev in SKILL.md frontmatter
```

## Users

```bash
hermes skills install psyclaw -y
# fallback:
hermes skills install Paradeluxe/psyclaw-skill/skills/psyclaw -y
```
