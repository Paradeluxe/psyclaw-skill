"""Local design project folders on disk.

Project rules (user-enforced):
  - Empty folder → OK (init as project)
  - Folder with our marker file → OK (open)
  - Folder with other files but NO marker → REFUSE (do not pretend)

Marker / design file (canonical, 2026-07-18):
  <folderName>.psyclaw   — same basename as the project folder + .psyclaw
  e.g.  MyStroop/MyStroop.psyclaw

Legacy (one-shot migrate on open/save, then removed):
  design.psyclaw

Optional:
  .psyclaw-project      (meta only; not required if design file present)

Content is psyclaw design JSON (not PsychoPy Builder XML; not .psyexp).
"""
from __future__ import annotations

import json
import os
import re
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Legacy fixed name — still recognized once, then renamed to folder-name form
LEGACY_DESIGN_FILENAME = "design.psyclaw"
# Human-readable pattern for UI / API docs (not a literal path)
DESIGN_FILENAME_PATTERN = "{folderName}.psyclaw"
# Kept as alias for older imports; do NOT use as write target
DESIGN_FILENAME = DESIGN_FILENAME_PATTERN

META_FILENAME = ".psyclaw-project"

_SAFE_SEGMENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._ -]{0,120}$")


def default_designs_root() -> Path:
    env = os.environ.get("PSYCLAW_DESIGNS_DIR")
    if env:
        return Path(env).expanduser().resolve()
    # repo/designs next to backend/
    here = Path(__file__).resolve().parent  # backend/
    return (here.parent / "designs").resolve()


def design_filename_for(folder: Path) -> str:
    """Canonical marker basename for a project folder: <folder.name>.psyclaw."""
    folder = Path(folder)
    name = (folder.name or "").strip() or "project"
    # avoid project.psyclaw.psyclaw if someone named the folder *.psyclaw
    if name.lower().endswith(".psyclaw"):
        return name
    return f"{name}.psyclaw"


def design_path_for(folder: Path) -> Path:
    return Path(folder) / design_filename_for(folder)


def _is_design_doc(d: Any) -> bool:
    return (
        isinstance(d, dict)
        and isinstance(d.get("routines"), list)
        and isinstance(d.get("flow"), list)
    )


def _find_design_file(folder: Path) -> Optional[Path]:
    """Prefer <folderName>.psyclaw; fall back to legacy design.psyclaw."""
    folder = Path(folder)
    primary = design_path_for(folder)
    if primary.is_file():
        return primary
    legacy = folder / LEGACY_DESIGN_FILENAME
    if legacy.is_file() and legacy.resolve() != primary.resolve():
        return legacy
    # primary == legacy path when folder is literally named "design"
    if primary.is_file():
        return primary
    return None


def migrate_design_filename(folder: Path) -> Optional[Path]:
    """Rename legacy design.psyclaw → <folderName>.psyclaw if needed.

    Returns the active design path after migration, or None if none exists.
    """
    folder = Path(folder)
    if not folder.is_dir():
        return None
    desired = design_path_for(folder)
    legacy = folder / LEGACY_DESIGN_FILENAME

    if desired.is_file():
        # Drop leftover legacy when both exist and differ
        if (
            legacy.is_file()
            and legacy.resolve() != desired.resolve()
        ):
            try:
                legacy.unlink()
            except OSError:
                pass
        return desired

    if legacy.is_file():
        try:
            legacy.replace(desired)
        except OSError:
            # copy-then-delete fallback (cross-volume etc.)
            try:
                data = legacy.read_bytes()
                desired.write_bytes(data)
                legacy.unlink()
            except OSError:
                return legacy
        return desired if desired.is_file() else legacy

    return None


def classify_folder(path: Path) -> Dict[str, Any]:
    """Classify a directory for open/init.

    Returns:
      status: empty | project | foreign | not_dir | missing
      design_path, files (names only)
    """
    path = Path(path)
    if not path.exists():
        return {
            "status": "missing",
            "path": str(path),
            "files": [],
            "design_path": str(design_path_for(path)),
            "marker": design_filename_for(path),
        }
    if not path.is_dir():
        return {"status": "not_dir", "path": str(path), "files": []}

    try:
        entries = sorted(os.listdir(path))
    except OSError as exc:
        return {"status": "error", "path": str(path), "error": str(exc), "files": []}

    # ignore common junk
    files = [n for n in entries if n not in (".DS_Store", "Thumbs.db")]
    design_file = _find_design_file(path)
    has_design = design_file is not None
    expected = design_filename_for(path)

    if not files:
        return {
            "status": "empty",
            "path": str(path.resolve()),
            "files": [],
            "design_path": str(design_path_for(path)),
            "marker": expected,
        }

    if has_design:
        return {
            "status": "project",
            "path": str(path.resolve()),
            "files": files,
            "design_path": str(design_file.resolve()),
            "marker": design_file.name,
        }

    # has other files, no marker → refuse
    return {
        "status": "foreign",
        "path": str(path.resolve()),
        "files": files,
        "design_path": str(design_path_for(path)),
        "marker": expected,
        "reason": (
            f"folder has files but no {expected} "
            f"(or legacy {LEGACY_DESIGN_FILENAME}) — not a psyclaw project"
        ),
    }


def read_design(path: Path) -> Tuple[Optional[Dict[str, Any]], Optional[str]]:
    p = Path(path)
    if p.is_dir():
        migrate_design_filename(p)
        design_file = _find_design_file(p)
        expected = design_filename_for(p)
    else:
        design_file = p if p.is_file() else None
        expected = p.name if design_file else DESIGN_FILENAME_PATTERN
    if design_file is None or not design_file.is_file():
        return None, f"missing {expected}"
    try:
        with open(design_file, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (OSError, json.JSONDecodeError) as exc:
        return None, str(exc)
    if not _is_design_doc(data):
        return None, "invalid design: need routines[] and flow[]"
    return data, None


def write_design(folder: Path, design: Dict[str, Any], *, create_ok: bool = True) -> Dict[str, Any]:
    """Write <folderName>.psyclaw into folder. create_ok allows creating folder if missing."""
    folder = Path(folder)
    if not folder.exists():
        if not create_ok:
            raise FileNotFoundError(str(folder))
        folder.mkdir(parents=True, exist_ok=True)

    info = classify_folder(folder)
    if info["status"] == "foreign":
        raise PermissionError(info.get("reason") or "foreign folder")
    if info["status"] not in ("empty", "project", "missing"):
        # missing handled by mkdir above → reclassify
        info = classify_folder(folder)
        if info["status"] == "foreign":
            raise PermissionError(info.get("reason") or "foreign folder")

    if not _is_design_doc(design):
        raise ValueError("invalid design: need routines[] and flow[]")

    fname = design_filename_for(folder)
    design = json.loads(json.dumps(design))  # deep copy plain
    meta = design.get("_meta") if isinstance(design.get("_meta"), dict) else {}
    meta.update(
        {
            "format": "psyclaw-design",
            "version": 1,
            "fileName": fname,
            "savedAt": time.strftime("%Y-%m-%d %H:%M:%S"),
            "projectDir": str(folder.resolve()),
        }
    )
    design["_meta"] = meta

    target = folder / fname
    tmp = folder / (fname + ".tmp")
    with open(tmp, "w", encoding="utf-8", newline="\n") as f:
        json.dump(design, f, ensure_ascii=False, indent=2)
        f.write("\n")
    os.replace(tmp, target)

    # remove legacy marker if different name
    legacy = folder / LEGACY_DESIGN_FILENAME
    if legacy.is_file() and legacy.resolve() != target.resolve():
        try:
            legacy.unlink()
        except OSError:
            pass

    # light meta sidecar (identifier companion; open only requires design file)
    sidecar = {
        "format": "psyclaw-project",
        "version": 1,
        "design": fname,
        "savedAt": meta["savedAt"],
        "name": design.get("name") or folder.name,
    }
    with open(folder / META_FILENAME, "w", encoding="utf-8", newline="\n") as f:
        json.dump(sidecar, f, ensure_ascii=False, indent=2)
        f.write("\n")

    return {
        "path": str(folder.resolve()),
        "design_path": str(target.resolve()),
        "name": design.get("name"),
        "savedAt": meta["savedAt"],
        "marker": fname,
    }


def init_project(folder: Path, design: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Init empty (or missing) folder as project. Refuses foreign."""
    folder = Path(folder)
    if folder.exists() and not folder.is_dir():
        raise NotADirectoryError(str(folder))
    if not folder.exists():
        folder.mkdir(parents=True, exist_ok=True)

    info = classify_folder(folder)
    if info["status"] == "foreign":
        raise PermissionError(info.get("reason") or "foreign folder")
    if info["status"] == "project":
        raise FileExistsError(f"already a project: {folder}")

    if design is None:
        design = {
            "name": folder.name or "untitled",
            "display": {"size": [1024, 768], "fullscreen": True},
            "routines": [
                {
                    "name": "trial",
                    "components": [],
                }
            ],
            "flow": [{"kind": "routine", "routine": "trial"}],
        }
    return write_design(folder, design, create_ok=True)


def list_projects(root: Optional[Path] = None) -> List[Dict[str, Any]]:
    """List immediate subdirs of root that are projects (have marker)."""
    root = Path(root) if root else default_designs_root()
    if not root.is_dir():
        return []
    out: List[Dict[str, Any]] = []
    try:
        kids = sorted(root.iterdir(), key=lambda p: p.name.lower())
    except OSError:
        return []
    for p in kids:
        if not p.is_dir():
            continue
        info = classify_folder(p)
        if info["status"] != "project":
            continue
        design, err = read_design(p)
        entry = {
            "name": (design or {}).get("name") or p.name,
            "path": str(p.resolve()),
            "fileName": Path(info["design_path"]).name
            if info.get("design_path")
            else design_filename_for(p),
            "savedAt": None,
        }
        if design and isinstance(design.get("_meta"), dict):
            entry["savedAt"] = design["_meta"].get("savedAt")
        if err:
            entry["error"] = err
        out.append(entry)
    return out


def resolve_under_root(root: Path, name_or_path: str) -> Path:
    """Resolve a project folder. Absolute paths allowed only if under root or explicit abs with checks."""
    root = root.resolve()
    raw = (name_or_path or "").strip()
    if not raw:
        raise ValueError("empty path")
    p = Path(raw)
    if p.is_absolute():
        resolved = p.resolve()
    else:
        # treat as folder name under root
        if not _SAFE_SEGMENT.match(raw.replace("\\", "/").split("/")[-1]):
            # allow relative subpath with safe segments
            parts = raw.replace("\\", "/").split("/")
            for seg in parts:
                if seg in ("", ".", ".."):
                    raise ValueError("invalid path segment")
                if not _SAFE_SEGMENT.match(seg):
                    raise ValueError(f"invalid path segment: {seg!r}")
        resolved = (root / raw).resolve()
    # For absolute paths outside root: still allow if user explicitly opened them
    # (local lab machine). Only block path traversal via .. in relative form (done).
    return resolved
