"""Tests for paradigm loader (yaml schema validation + listing)."""
import os
import sys
from pathlib import Path

# Allow running tests from repo root
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))

from paradigms.loader import (
    validate_paradigm,
    list_paradigms,
    load_paradigm,
    discover_all,
    EXAMPLES_DIR,
)


def test_validate_minimal_paradigm_ok():
    data = {
        "id": "test",
        "label": "Test",
        "fields": [{"name": "f1", "label": "Field 1", "type": "text"}],
    }
    result = validate_paradigm(data)
    assert result["ok"], result["errors"]
    assert result["errors"] == []


def test_validate_missing_id_fails():
    data = {"label": "X", "fields": [{"name": "f", "label": "F", "type": "text"}]}
    result = validate_paradigm(data)
    assert not result["ok"]
    assert any("id" in e for e in result["errors"])


def test_validate_invalid_field_type_fails():
    data = {
        "id": "x", "label": "X",
        "fields": [{"name": "f", "label": "F", "type": "bogus"}],
    }
    result = validate_paradigm(data)
    assert not result["ok"]
    assert any("invalid type" in e or "type" in e for e in result["errors"])


def test_validate_duplicate_field_names_fails():
    data = {
        "id": "x", "label": "X",
        "fields": [
            {"name": "f", "label": "F", "type": "text"},
            {"name": "f", "label": "F2", "type": "text"},
        ],
    }
    result = validate_paradigm(data)
    assert not result["ok"]
    assert any("duplicate" in e for e in result["errors"])


def test_validate_select_requires_options():
    data = {
        "id": "x", "label": "X",
        "fields": [{"name": "f", "label": "F", "type": "select"}],
    }
    result = validate_paradigm(data)
    assert not result["ok"]
    assert any("options" in e for e in result["errors"])


def test_list_paradigms_finds_stroop():
    discover_all()
    paradigms = list_paradigms()
    assert any(p["id"] == "stroop" for p in paradigms), paradigms


def test_list_paradigms_finds_gonogo():
    discover_all()
    paradigms = list_paradigms()
    assert any(p["id"] == "gonogo" for p in paradigms), paradigms


def test_list_paradigms_count_at_least_two():
    discover_all()
    paradigms = list_paradigms()
    assert len(paradigms) >= 2, paradigms


def test_get_paradigm_returns_full_schema():
    discover_all()
    p = load_paradigm("stroop")
    assert p is not None
    assert p["id"] == "stroop"
    assert isinstance(p["fields"], list)
    assert len(p["fields"]) > 0
    # Every field has name + type
    for f in p["fields"]:
        assert "name" in f
        assert "type" in f


def test_gonogo_fields_have_correct_types():
    discover_all()
    p = load_paradigm("gonogo")
    assert p is not None
    types = {f["name"]: f["type"] for f in p["fields"]}
    assert types["n_go"] == "number"
    assert types["fullscreen"] == "checkbox"
    assert types["instructions_text"] == "textarea"
    assert types["go_label"] == "text"


def test_get_unknown_paradigm_returns_none():
    discover_all()
    p = load_paradigm("nonexistent")
    assert p is None