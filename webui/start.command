#!/bin/bash
# macOS: double-click in Finder
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  exec python3 ./start.py "$@"
elif command -v python >/dev/null 2>&1; then
  exec python ./start.py "$@"
else
  echo "psyclaw-webui: need python3 on PATH. See docs/INSTALL.md"
  read -r -p "Press Enter to close…"
  exit 1
fi
