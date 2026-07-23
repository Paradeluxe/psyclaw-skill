"""Paradigm registry — re-exports the loader's public API.

Kept as a thin re-export so the rest of the backend can do
``from paradigms import list_paradigms, load_paradigm, validate_paradigm``
without reaching into ``paradigms.loader`` directly. Adding a new
paradigm is just dropping a new YAML into ``examples/`` — the registry
picks it up on next app start.
"""
from .loader import (
    ALLOWED_FIELD_TYPES,
    EXAMPLES_DIR,
    discover_all,
    list_paradigms,
    load_paradigm,
    validate_paradigm,
)

__all__ = [
    "ALLOWED_FIELD_TYPES",
    "EXAMPLES_DIR",
    "discover_all",
    "list_paradigms",
    "load_paradigm",
    "validate_paradigm",
]
