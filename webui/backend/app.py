"""Flask app entrypoint for psyclaw-webui.

Responsibilities:
- Create the Flask app
- Register the /api blueprint (see backend/api/routes.py)
- Serve the SPA from / (frontend/index.html) and other frontend/* assets

Run from the repository root:

    python backend/app.py
"""
import os

from flask import Flask, jsonify, send_from_directory

from api import api_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder=None)

    # API routes first so /api/* always wins over the SPA catch-all.
    app.register_blueprint(api_bp)

    # Resolve frontend/ relative to this file (backend/app.py -> ../frontend).
    frontend_dir = os.path.normpath(
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "frontend")
    )

    @app.route("/")
    def index():  # type: ignore[no-redef]
        return send_from_directory(frontend_dir, "index.html")

    @app.route("/<path:filename>")
    def static_file(filename: str):  # type: ignore[no-redef]
        # Never let the static handler swallow /api/*.
        if filename.startswith("api/"):
            return jsonify({"error": "not found"}), 404
        return send_from_directory(frontend_dir, filename)

    return app


app = create_app()


if __name__ == "__main__":
    # Default 8876 — 8765 is Mentor. Override: PSYCLAW_PORT=xxxx
    port = int(os.environ.get("PSYCLAW_PORT", "8876"))
    # Disable reloader to keep background threads from being doubled.
    app.run(host="127.0.0.1", port=port, debug=False, use_reloader=False, threaded=True)
