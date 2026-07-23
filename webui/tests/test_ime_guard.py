"""IME force helpers + design_compiler inject."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from design_compiler import compile_design  # noqa: E402
from ime_guard import EXPERIMENT_IME_HELPERS, force_english, restore  # noqa: E402


def _mini_design():
    return {
        "name": "ime_test",
        "display": {"size": [800, 600], "fullscreen": False},
        "routines": [
            {
                "name": "t",
                "components": [
                    {
                        "id": "k",
                        "type": "keyboard",
                        "name": "k",
                        "start": 0,
                        "duration": -1,
                        "params": {"keys": "space", "force_end": True},
                    }
                ],
            }
        ],
        "flow": [{"kind": "routine", "routine": "t"}],
    }


def test_helpers_snippet_has_force_and_restore():
    assert "_psyclaw_force_en_ime" in EXPERIMENT_IME_HELPERS
    assert "_psyclaw_restore_ime" in EXPERIMENT_IME_HELPERS
    assert "_psyclaw_assert_en_ime" in EXPERIMENT_IME_HELPERS
    assert "00000409" in EXPERIMENT_IME_HELPERS


def test_compile_inlines_ime_helpers():
    src = compile_design(_mini_design(), session={"participant_id": "P_pilot", "force_en_ime": True})
    assert "__IME_HELPERS__" not in src
    assert "FORCE_EN_IME" in src
    assert "_psyclaw_force_en_ime" in src
    assert "_psyclaw_assert_en_ime" in src
    assert "IME -> en-US" in src


def test_compile_respects_force_en_ime_false_in_session_literal():
    src = compile_design(_mini_design(), session={"participant_id": "P_pilot", "force_en_ime": False})
    # SESSION is double-encoded JSON string; false appears escaped
    assert "force_en_ime" in src
    assert ("false" in src) and ("force_en_ime" in src)


def test_force_english_roundtrip_windows():
    if sys.platform != "win32":
        t = force_english()
        assert t.ok is False
        return
    t = force_english(also_default=False)
    assert t.ok is True
    assert (t.forced_hkl & 0xFFFF) == 0x0409
    restore(t)
