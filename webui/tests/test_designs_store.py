"""Project folder rules: empty OK, marked OK, foreign REFUSE.
Marker = <folderName>.psyclaw (legacy design.psyclaw migrates).
"""
from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from designs_store import (  # noqa: E402
    LEGACY_DESIGN_FILENAME,
    classify_folder,
    design_filename_for,
    design_path_for,
    init_project,
    list_projects,
    migrate_design_filename,
    read_design,
    write_design,
)


def _minimal_design(name="t"):
    return {
        "name": name,
        "display": {"size": [800, 600], "fullscreen": False},
        "routines": [{"name": "trial", "components": []}],
        "flow": [{"kind": "routine", "routine": "trial"}],
    }


def test_empty_folder_is_empty(tmp_path):
    d = tmp_path / "e"
    d.mkdir()
    info = classify_folder(d)
    assert info["status"] == "empty"
    assert info["marker"] == "e.psyclaw"
    assert info["design_path"].endswith("e.psyclaw")


def test_foreign_folder_refused(tmp_path):
    d = tmp_path / "junk"
    d.mkdir()
    (d / "notes.txt").write_text("hi", encoding="utf-8")
    info = classify_folder(d)
    assert info["status"] == "foreign"
    with pytest.raises(PermissionError):
        write_design(d, _minimal_design())


def test_init_empty_then_project(tmp_path):
    d = tmp_path / "p1"
    d.mkdir()
    meta = init_project(d, _minimal_design("p1"))
    assert design_path_for(d).is_file()
    assert not (d / LEGACY_DESIGN_FILENAME).exists() or design_filename_for(d) == LEGACY_DESIGN_FILENAME
    info = classify_folder(d)
    assert info["status"] == "project"
    assert Path(info["design_path"]).name == "p1.psyclaw"
    design, err = read_design(d)
    assert err is None
    assert design["name"] == "p1"
    assert design["_meta"]["fileName"] == "p1.psyclaw"
    assert meta["path"]


def test_write_overwrite_project(tmp_path):
    d = tmp_path / "p2"
    d.mkdir()
    init_project(d, _minimal_design("p2"))
    design, _ = read_design(d)
    design["name"] = "p2b"
    write_design(d, design)
    design2, err = read_design(d)
    assert err is None
    assert design2["name"] == "p2b"
    assert design_path_for(d).is_file()


def test_legacy_design_psyclaw_open_and_migrate(tmp_path):
    d = tmp_path / "oldproj"
    d.mkdir()
    legacy = d / LEGACY_DESIGN_FILENAME
    import json

    legacy.write_text(
        json.dumps(_minimal_design("oldproj"), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    info = classify_folder(d)
    assert info["status"] == "project"
    assert Path(info["design_path"]).name == LEGACY_DESIGN_FILENAME

    design, err = read_design(d)
    assert err is None
    assert design["name"] == "oldproj"
    # read migrates to folder-name form
    assert design_path_for(d).is_file()
    assert not legacy.exists()


def test_migrate_function(tmp_path):
    d = tmp_path / "mig"
    d.mkdir()
    import json

    (d / LEGACY_DESIGN_FILENAME).write_text(
        json.dumps(_minimal_design("mig")), encoding="utf-8"
    )
    path = migrate_design_filename(d)
    assert path is not None
    assert path.name == "mig.psyclaw"
    assert path.is_file()
    assert not (d / LEGACY_DESIGN_FILENAME).exists()


def test_list_projects_only_marked(tmp_path, monkeypatch):
    root = tmp_path / "designs"
    root.mkdir()
    (root / "empty").mkdir()
    foreign = root / "foreign"
    foreign.mkdir()
    (foreign / "x.txt").write_text("x", encoding="utf-8")
    good = root / "good"
    good.mkdir()
    init_project(good, _minimal_design("good"))
    items = list_projects(root)
    names = {Path(p["path"]).name for p in items}
    assert names == {"good"}
    assert items[0]["fileName"] == "good.psyclaw"


def test_init_refuses_foreign(tmp_path):
    d = tmp_path / "f"
    d.mkdir()
    (d / "a.bin").write_bytes(b"\x00")
    with pytest.raises(PermissionError):
        init_project(d)
