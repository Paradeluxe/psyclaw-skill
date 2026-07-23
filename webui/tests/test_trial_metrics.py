"""Unit tests for trial_metrics (scoring + summary + long tables)."""
from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "backend"))

from trial_metrics import (  # noqa: E402
    apply_trial_scores,
    by_condition_rows,
    detect_trial_kind,
    metrics_long_rows,
    pick_corr_ans,
    score_response,
    summarize_rows,
)


def test_pick_corr_ans_prefers_corrAns():
    assert pick_corr_ans({"corrAns": "r", "correct": "g"}) == "r"
    assert pick_corr_ans({"correct": "space"}) == "space"
    assert pick_corr_ans({"corr": "1"}) == ""  # accuracy flag, not key
    assert pick_corr_ans({}) == ""


def test_score_response_match_miss_case():
    assert score_response("r", "r") == ("r", 1)
    assert score_response("R", "r") == ("r", 1)
    assert score_response("g", "r") == ("r", 0)
    assert score_response(None, "r") == ("r", 0)  # miss = wrong
    assert score_response("", "r") == ("r", 0)
    assert score_response("r", "") == ("", "")
    assert score_response("r", "r", had_keyboard=False) == ("r", "")


def test_nogo_scoring():
    assert score_response(None, "", trial_kind="nogo") == ("", 1)
    assert score_response("space", "", trial_kind="nogo") == ("", 0)
    assert score_response("r", "r", trial_kind="go") == ("r", 1)
    assert score_response(None, "r", trial_kind="go") == ("r", 0)


def test_detect_trial_kind():
    assert detect_trial_kind({"trialType": "go"}) == "go"
    assert detect_trial_kind({"trialType": "no-go"}) == "nogo"
    assert detect_trial_kind({"stimType": "NoGo"}) == "nogo"
    assert detect_trial_kind({"congruent": "yes"}) == ""


def test_apply_trial_scores_on_row():
    row = {"response": "r", "word": "RED"}
    apply_trial_scores(
        row, resp="r", trial_vars={"corrAns": "r", "word": "RED"}, had_keyboard=True
    )
    assert row["corrAns"] == "r"
    assert row["corr"] == 1
    apply_trial_scores(
        row, resp="g", trial_vars={"corrAns": "r"}, had_keyboard=True
    )
    assert row["corr"] == 0


def test_apply_nogo_row():
    row = {}
    apply_trial_scores(
        row, resp=None, trial_vars={"trialType": "nogo"}, had_keyboard=True
    )
    assert row["corr"] == 1
    apply_trial_scores(
        row, resp="space", trial_vars={"trialType": "nogo"}, had_keyboard=True
    )
    assert row["corr"] == 0


def test_summarize_overall_and_group():
    rows = [
        {"corr": 1, "rt": 0.4, "congruent": "yes"},
        {"corr": 1, "rt": 0.5, "congruent": "yes"},
        {"corr": 0, "rt": 0.8, "congruent": "no"},
        {"corr": 1, "rt": 0.6, "congruent": "no"},
        {"corr": "", "rt": "", "routine": "instructions"},  # unscored
    ]
    s = summarize_rows(rows, {"group_by": ["congruent"]})
    ov = s["overall"]
    assert ov["n"] == 5
    assert ov["n_scored"] == 4
    assert ov["n_correct"] == 3
    assert ov["accuracy"] == 0.75
    # mean_rt only over scored trials (instructions excluded)
    assert ov["mean_rt"] == 0.575  # (0.4+0.5+0.8+0.6)/4
    assert "yes" in s["by_group"]
    assert "no" in s["by_group"]
    assert s["by_group"]["yes"]["accuracy"] == 1.0
    assert s["by_group"]["no"]["n_scored"] == 2
    assert s["by_group"]["no"]["accuracy"] == 0.5


def test_mean_rt_ignores_unscored_instruction_rt():
    rows = [
        {"corr": "", "rt": 0.2, "routine": "instructions"},
        {"corr": 1, "rt": 0.5, "congruent": "yes"},
        {"corr": 1, "rt": 0.7, "congruent": "yes"},
    ]
    ov = summarize_rows(rows, {})["overall"]
    assert ov["mean_rt"] == 0.6
    assert ov["n_scored"] == 2


def test_summarize_auto_group_congruent():
    rows = [
        {"corr": 1, "rt": 0.3, "congruent": "cong"},
        {"corr": 0, "rt": 0.5, "congruent": "incong"},
    ]
    s = summarize_rows(rows, {})  # auto-detect
    assert s["group_by"] == ["congruent"]
    assert set(s["by_group"].keys()) == {"cong", "incong"}


def test_gonogo_rates():
    rows = [
        {"corr": 1, "rt": 0.4, "trialType": "go"},
        {"corr": 0, "rt": "", "trialType": "go"},  # miss
        {"corr": 1, "rt": "", "trialType": "nogo"},  # CR
        {"corr": 0, "rt": 0.2, "trialType": "nogo"},  # FA
    ]
    ov = summarize_rows(rows, {"group_by": ["trialType"]})["overall"]
    assert ov["n_go"] == 2
    assert ov["n_nogo"] == 2
    assert ov["hit_rate"] == 0.5
    assert ov["miss_rate"] == 0.5
    assert ov["fa_rate"] == 0.5
    assert ov["cr_rate"] == 0.5


def test_long_and_by_condition_tables():
    rows = [
        {"corr": 1, "rt": 0.4, "congruent": "yes"},
        {"corr": 0, "rt": 0.8, "congruent": "no"},
    ]
    s = summarize_rows(rows, {"group_by": ["congruent"]})
    s["participant_id"] = "P01"
    flat = by_condition_rows(s, participant_id="P01", session="1")
    assert any(r["scope"] == "overall" for r in flat)
    assert any(r.get("congruent") == "yes" for r in flat)
    long = metrics_long_rows(s, participant_id="P01", session="1")
    metrics = {r["metric"] for r in long if r["scope"] == "overall"}
    assert "accuracy" in metrics
    assert "mean_rt" in metrics
    assert all("value" in r for r in long)
