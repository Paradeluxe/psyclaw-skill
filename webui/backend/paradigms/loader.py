"""Paradigm YAML loader + validator.

Paradigm-agnostic by design: we treat each ``examples/<name>.yaml`` file as
a pure data file describing fields, runtime hints and metadata. The platform
never hard-codes Stroop / GoNoGo / etc.; adding a new paradigm is just
dropping a new YAML.

Public API
----------
- ``list_paradigms()`` — returns ``[{id, label}]`` for every discovered YAML
- ``load_paradigm(name)`` — returns the parsed dict for one paradigm
- ``validate_paradigm(d)`` — returns ``{ok, errors}`` for a parsed dict
- ``discover_all()`` — called once at app startup; scans examples/ and
  caches parsed paradigms in a module-level dict. Validation errors are
  logged to stderr but never crash the app (we want the UI to keep working
  for the paradigms that DO validate).

Deviations from CONTRACT.md
---------------------------
- None on the contract surface. The CONTRACT.md schema permits ``fields``
  to be absent (a paradigm can be metadata-only). We allow that, but every
  paradigm with a UI form should declare at least one field.
"""
from __future__ import annotations

import os
import sys
from typing import Any, Dict, List, Optional

import yaml

# Allowed field types per CONTRACT.md. Mirrored here so we can fail fast on
# a typo in YAML (``type: nmber``) before the frontend ever sees it.
ALLOWED_FIELD_TYPES = {
    "text",
    "number",
    "checkbox",
    "textarea",
    "select",
    "multiselect",
    "color",
    "slider",
}

# Resolved at import time from this file's location. We expect:
#   backend/paradigms/loader.py   ->   backend/   ->   <repo root> / examples
_THIS_DIR = os.path.dirname(os.path.abspath(__file__))
_REPO_ROOT = os.path.normpath(os.path.join(_THIS_DIR, "..", ".."))
EXAMPLES_DIR = os.environ.get("PSYCLAW_EXAMPLES_DIR") or os.path.join(_REPO_ROOT, "examples")

# Module-level cache: paradigm_id -> parsed dict.
_CACHE: Dict[str, Dict[str, Any]] = {}


def _load_yaml_file(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def validate_paradigm(d: Dict[str, Any]) -> Dict[str, Any]:
    """Schema check a parsed paradigm dict.

    Returns ``{"ok": bool, "errors": [str, ...]}``. Never raises.
    """
    errors: List[str] = []

    if not isinstance(d, dict):
        return {"ok": False, "errors": [f"paradigm must be a mapping, got {type(d).__name__}"]}

    # id is required and must be a non-empty kebab-case-ish string.
    pid = d.get("id")
    if not isinstance(pid, str) or not pid.strip():
        errors.append("missing or empty required field: 'id'")
    else:
        if any(c.isspace() for c in pid):
            errors.append(f"'id' must not contain whitespace, got {pid!r}")

    # label is required (human-readable).
    label = d.get("label")
    if not isinstance(label, str) or not label.strip():
        errors.append("missing or empty required field: 'label'")

    # fields is optional (paradigm may be metadata-only), but if present
    # must be a list of valid field dicts.
    fields = d.get("fields")
    if fields is not None:
        if not isinstance(fields, list):
            errors.append("'fields' must be a list")
        else:
            seen_names: Dict[str, int] = {}
            for i, f in enumerate(fields):
                if not isinstance(f, dict):
                    errors.append(f"fields[{i}] must be a mapping")
                    continue

                fname = f.get("name")
                if not isinstance(fname, str) or not fname.strip():
                    errors.append(f"fields[{i}].name missing or empty")
                else:
                    if fname in seen_names:
                        errors.append(
                            f"duplicate field name {fname!r} (first at index {seen_names[fname]})"
                        )
                    else:
                        seen_names[fname] = i

                ftype = f.get("type")
                if ftype is None:
                    errors.append(f"fields[{i}] ({fname!r}).type is required")
                elif ftype not in ALLOWED_FIELD_TYPES:
                    errors.append(
                        f"fields[{i}] ({fname!r}).type={ftype!r} "
                        f"not in allowed types: {sorted(ALLOWED_FIELD_TYPES)}"
                    )

                # select/multiselect need an options list
                if ftype in ("select", "multiselect"):
                    opts = f.get("options")
                    if not isinstance(opts, list) or not opts:
                        errors.append(
                            f"fields[{i}] ({fname!r}) type={ftype!r} requires non-empty 'options' list"
                        )

                # number / slider may declare min/max
                if ftype in ("number", "slider"):
                    for k in ("min", "max"):
                        v = f.get(k)
                        if v is not None and not isinstance(v, (int, float)):
                            errors.append(
                                f"fields[{i}] ({fname!r}).{k} must be number, got {type(v).__name__}"
                            )

    # runtime is optional, but if present must be a mapping
    runtime = d.get("runtime")
    if runtime is not None and not isinstance(runtime, dict):
        errors.append("'runtime' must be a mapping")

    return {"ok": len(errors) == 0, "errors": errors}


def list_paradigms() -> List[Dict[str, str]]:
    """List all discovered paradigms as ``[{id, label}, ...]``.

    Sorted by (order, id) where order is the optional ``order`` field in yaml;
    paradigms without order come last.
    """
    def sort_key(item):
        pid, d = item
        return (d.get("order", 9999), pid)
    return [
        {"id": pid, "label": d.get("label", pid)}
        for pid, d in sorted(_CACHE.items(), key=sort_key)
    ]


def load_paradigm(name: str) -> Optional[Dict[str, Any]]:
    """Return the parsed YAML dict for paradigm ``name`` or None if missing."""
    return _CACHE.get(name)


def discover_all(examples_dir: Optional[str] = None) -> List[str]:
    """Scan ``examples/*.yaml``, load + validate each, populate cache.

    Idempotent: re-running replaces the cache. Returns the list of
    paradigm ids that loaded successfully. Failed paradigms are logged
    to stderr but do NOT raise (we want the rest of the app to keep
    working for the paradigms that did validate).
    """
    global _CACHE
    scan_dir = examples_dir or EXAMPLES_DIR
    _CACHE = {}

    if not os.path.isdir(scan_dir):
        print(f"[paradigms] examples dir not found: {scan_dir}", file=sys.stderr)
        return []

    loaded: List[str] = []
    for fname in sorted(os.listdir(scan_dir)):
        if not (fname.endswith(".yaml") or fname.endswith(".yml")):
            continue
        path = os.path.join(scan_dir, fname)
        try:
            data = _load_yaml_file(path)
        except yaml.YAMLError as e:
            print(f"[paradigms] {fname}: YAML parse error: {e}", file=sys.stderr)
            continue
        except OSError as e:
            print(f"[paradigms] {fname}: I/O error: {e}", file=sys.stderr)
            continue

        result = validate_paradigm(data)
        if not result["ok"]:
            for err in result["errors"]:
                print(f"[paradigms] {fname}: {err}", file=sys.stderr)
            continue

        pid = data["id"]
        _CACHE[pid] = data
        loaded.append(pid)
        print(f"[paradigms] loaded {fname} -> id={pid}", file=sys.stderr)

    return loaded


# Eagerly discover at import time so unit tests (and the Flask app) can
# rely on the cache being populated without needing a separate init step.
discover_all()
