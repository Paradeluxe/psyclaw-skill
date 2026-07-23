"""Flask Blueprint registry for /api/* routes.

A single ``api_bp`` Blueprint with ``url_prefix="/api"`` is registered by
``backend/app.py``. All route modules attach handlers to this blueprint.

The contract in ``docs/CONTRACT.md`` defines the full surface area; see
``routes.py`` for the handlers.
"""
from flask import Blueprint

api_bp = Blueprint("api", __name__, url_prefix="/api")

# Importing the module registers its @api_bp.route handlers.
# (Side effect is what matters; the import is not "unused".)
from . import routes  # noqa: E402,F401
