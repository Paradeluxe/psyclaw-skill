"""Debug entrypoint for psyclaw-webui (completely separate from production).

Runs on port 8877 by default (PSYCLAW_DEBUG_PORT). Uses Flask debug server with
auto-reload, optional flask-debugtoolbar, and PSYCLAW_FORCE_MOCK=1 by default
so no real PsychoPy subprocess is spawned.

This module NEVER imports from production code paths beyond app.create_app,
and production code never imports this module. Launch via:

    python backend/debug_app.py
    python start_debug.py
    start_debug.bat

Environment:
    PSYCLAW_DEBUG_PORT  override port (default 8877)
    PSYCLAW_PORT        fallback port if DEBUG_PORT unset (still defaults to 8877)
    PSYCLAW_FORCE_MOCK  set to "0" to allow real PsychoPy in debug
    PSYCLAW_DEBUG       always "1" when this module runs
"""
from __future__ import annotations

import os
import sys

# Mark debug mode before any imports that might check it.
os.environ.setdefault("PSYCLAW_DEBUG", "1")
os.environ.setdefault("PSYCLAW_FORCE_MOCK", "1")

# Ensure backend/ is on sys.path so `from app import create_app` resolves
# regardless of cwd (matches start.py's PYTHONPATH injection).
_HERE = os.path.dirname(os.path.abspath(__file__))
if _HERE not in sys.path:
    sys.path.insert(0, _HERE)

from app import create_app  # noqa: E402

app = create_app()
app.config["DEBUG"] = True
app.config["SECRET_KEY"] = os.environ.get("PSYCLAW_DEBUG_SECRET", "psyclaw-debug-dev-only")

# Flask-debugtoolbar (optional — only if installed in .venv-debug).
try:
    from flask_debugtoolbar import DebugToolbarExtension  # type: ignore

    toolbar = DebugToolbarExtension()
    toolbar.init_app(app)
    _HAS_TOOLBAR = True
except ImportError:
    _HAS_TOOLBAR = False


def _debug_banner(port: int) -> None:
    sep = "=" * 56
    print(sep)
    print("  psyclaw-webui · DEBUG MODE (isolated from production)")
    print(f"  port      : 127.0.0.1:{port}")
    print(f"  mock      : {os.environ.get('PSYCLAW_FORCE_MOCK', '1')}")
    print(f"  toolbar   : {'on' if _HAS_TOOLBAR else 'off (pip install flask-debugtoolbar)'}")
    print(f"  reloader  : on")
    print(f"  venv      : .venv-debug (separate from .venv)")
    print(sep)


if __name__ == "__main__":
    port = int(
        os.environ.get("PSYCLAW_DEBUG_PORT")
        or os.environ.get("PSYCLAW_PORT", "8877")
    )
    _debug_banner(port)
    app.run(
        host="127.0.0.1",
        port=port,
        debug=True,
        use_reloader=True,
        threaded=True,
    )