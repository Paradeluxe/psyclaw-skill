#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
if command -v python3 >/dev/null 2>&1; then
  exec python3 ./start.py "$@"
elif command -v python >/dev/null 2>&1; then
  exec python ./start.py "$@"
else
  echo "psyclaw-webui: need python3 on PATH. See docs/INSTALL.md" >&2
  exit 1
fi
