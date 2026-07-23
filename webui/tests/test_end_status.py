# -*- coding: utf-8 -*-
"""ESC abort → end_status manual (not finished/normal)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from api.routes import _read_end_status  # noqa: E402
import participants_registry as preg  # noqa: E402


def test_read_end_status_from_end_reason_json(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "end_reason.json").write_text(
        json.dumps({"end_status": "manual", "reason": "escape", "n_rows": 3}),
        encoding="utf-8",
    )
    assert _read_end_status(str(tmp_path)) == "manual"


def test_read_end_status_from_instrument_reason(tmp_path: Path) -> None:
    data = tmp_path / "data"
    data.mkdir()
    (data / "instrument.json").write_text(
        json.dumps({"end_status": "normal", "end_reason": ""}),
        encoding="utf-8",
    )
    assert _read_end_status(str(tmp_path)) == "normal"
    (data / "instrument.json").write_text(
        json.dumps({"end_status": "manual", "end_reason": "escape"}),
        encoding="utf-8",
    )
    assert _read_end_status(str(tmp_path)) == "manual"


def test_read_end_status_default_normal(tmp_path: Path) -> None:
    (tmp_path / "data").mkdir()
    assert _read_end_status(str(tmp_path)) == "normal"


def test_escape_register_not_duplicate(tmp_path: Path) -> None:
    proj = str(tmp_path / "exp")
    Path(proj).mkdir()
    preg.register_run(
        proj, participant_id="P01", session="1", run_id="r1", end_status="escape"
    )
    ents = preg.list_entries(proj)
    assert ents[0]["end_status"] == "manual"
    assert preg.is_duplicate(proj, "P01", "1") is False
