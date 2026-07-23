#!/bin/bash
# Psyclaw monorepo installer: clone + skill install + webui setup
# Works on any CLI that supports skills/<name>/SKILL.md

echo "=== PsyClaw monorepo install ==="

# 1. Clone monorepo
MONOREPO_DIR="${1:-$HOME/psyclaw}"

if [ -d "$MONOREPO_DIR/.git" ]; then
  echo "Monorepo already exists at $MONOREPO_DIR — updating..."
  git -C "$MONOREPO_DIR" pull
else
  echo "Cloning Paradeluxe/psyclaw to $MONOREPO_DIR..."
  git clone https://github.com/Paradeluxe/psyclaw.git "$MONOREPO_DIR"
fi

# 2. Install skill (CLI-specific — print instructions for common CLIs)
echo ""
echo "=== Skill install ==="
echo "Skill source: $MONOREPO_DIR/skills/psyclaw/"
echo ""
echo "Install command depends on your AI CLI:"
echo "  Hermes:    cd $MONOREPO_DIR && hermes install Paradeluxe/psyclaw/skills/psyclaw"
echo "  Claude Code: cp -r $MONOREPO_DIR/skills/psyclaw ~/.claude/skills/"
echo "  Codex:     cp -r $MONOREPO_DIR/skills/psyclaw <your-agent-skill-dir>/"
echo "  Generic:   Point your agent at $MONOREPO_DIR/skills/psyclaw/"
echo ""

# 3. WebUI setup
echo "=== WebUI setup ==="
WEBUI_DIR="$MONOREPO_DIR/webui"
cd "$WEBUI_DIR"

# Create venv if not present
if [ ! -d ".venv" ]; then
  echo "Creating Python venv..."
  python3 -m venv .venv 2>/dev/null || python -m venv .venv
fi

# Install deps
echo "Installing Flask dependencies..."
if [ -f ".venv/bin/pip" ]; then
  .venv/bin/pip install -r requirements.txt
else
  .venv/Scripts/pip install -r requirements.txt
fi

# Remember webui path
echo "Remembering webui path..."
python3 scripts/user_config.py remember 2>/dev/null || python scripts/user_config.py remember

echo ""
echo "=== Install complete ==="
echo "Monorepo:  $MONOREPO_DIR"
echo "WebUI:     $WEBUI_DIR"
echo "Start:     cd $WEBUI_DIR && python start.py"
echo "URL:       http://127.0.0.1:8876"