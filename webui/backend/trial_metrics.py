"""Trial-level scoring + run summary metrics (stdlib only).

Used by design_compiler runner (source inlined into generated experiment.py)
and by unit tests. Platform-generic — no paradigm hardcoding.

Conventions (PsychoPy-aligned):
  corrAns  expected response key/label from stimlist
  corr     0/1 accuracy; "" if unscored (no answer key or non-response routine)
  rt       seconds (already on the row)

design.metrics (optional, data not compiler branches):
  {
    "group_by": ["congruent"],   # factor columns already on rows
    "aggregates": ["accuracy", "mean_rt", "mean_rt_correct", "mean_rt_error", "n", "n_correct"]
  }
  If group_by omitted, auto-detect first present of:
  congruent, congruency, cong, trialType, trial_type, condition, cond, stimType, stim_type

Go/NoGo (when trialType|stimType has go/nogo values):
  go   → score vs corrAns (miss = 0)
  nogo → withhold correct (1); any key = FA (0)
  summary adds hit_rate, fa_rate, miss_rate, cr_rate

Outputs (written by runner):
  *_summary.json       nested overall + by_group
  *_by_condition.csv   one row per overall/group cell (Excel-friendly)
  *_metrics_long.csv   tidy long: scope, group_*, metric, value (R/ggplot-ready)
"""
from __future__ import annotations

from statistics import mean, median
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


_ANSWER_KEY_NAMES = (
    "corrAns",
    "corr_ans",
    "correctAns",
    "correct_ans",
    "correctKey",
    "correct_key",
)

# Prefer these over bare correct/corr (those may be 0/1 already)
_ANSWER_KEY_FALLBACK = ("correct", "corr")

_AUTO_GROUP_COLS = (
    "congruent",
    "congruency",
    "cong",
    "trialType",
    "trial_type",
    "condition",
    "cond",
    "stimType",
    "stim_type",
    "blockType",
    "block_type",
)

_KIND_COLS = (
    "trialType",
    "trial_type",
    "stimType",
    "stim_type",
    "type",
    "condition",
    "cond",
)

_GO_TOKENS = frozenset({"go", "target", "hit"})
_NOGO_TOKENS = frozenset({"nogo", "nogo", "inhibit", "stop", "nogotrial"})

_DEFAULT_AGG = (
    "n",
    "n_scored",
    "n_correct",
    "accuracy",
    "mean_rt",
    "median_rt",
    "mean_rt_correct",
    "mean_rt_error",
)

_METRIC_ORDER = (
    "n",
    "n_scored",
    "n_correct",
    "accuracy",
    "mean_rt",
    "median_rt",
    "mean_rt_correct",
    "mean_rt_error",
    "hit_rate",
    "fa_rate",
    "miss_rate",
    "cr_rate",
    "n_go",
    "n_nogo",
    "n_hit",
    "n_fa",
    "n_miss",
    "n_cr",
)


def _norm_token(v: Any) -> str:
    s = str(v or "").strip().lower()
    for ch in (" ", "-", "_"):
        s = s.replace(ch, "")
    return s


def detect_trial_kind(*sources: Optional[Dict[str, Any]]) -> str:
    """Return 'go', 'nogo', or '' from stimlist-like dicts."""
    for src in sources:
        if not isinstance(src, dict):
            continue
        for k in _KIND_COLS:
            if k not in src:
                continue
            tok = _norm_token(src.get(k))
            if not tok:
                continue
            if tok in _GO_TOKENS:
                return "go"
            if tok in _NOGO_TOKENS or tok.startswith("nogo"):
                return "nogo"
    return ""


def pick_corr_ans(trial_vars: Optional[Dict[str, Any]]) -> str:
    """Return expected answer string, or \"\" if none."""
    tv = trial_vars or {}
    for k in _ANSWER_KEY_NAMES:
        if k in tv and str(tv[k]).strip() != "":
            return str(tv[k]).strip()
    for k in _ANSWER_KEY_FALLBACK:
        if k not in tv:
            continue
        v = str(tv[k]).strip()
        if not v:
            continue
        # skip if already a 0/1 accuracy flag
        if v in ("0", "1", "0.0", "1.0", "True", "False", "true", "false"):
            continue
        return v
    return ""


def score_response(
    resp: Any,
    corr_ans: str,
    *,
    had_keyboard: bool = True,
    trial_kind: str = "",
) -> Tuple[str, Any]:
    """Return (corrAns, corr) where corr is 0, 1, or \"\".

    Miss (no response) with an answer key counts as incorrect (0) when the
    routine had a keyboard — standard forced-choice coding.

    nogo: withhold = 1, any key = 0 (false alarm).
    go without corrAns: any key = 1 (hit), miss = 0.
    """
    kind = str(trial_kind or "").strip().lower()
    ans = str(corr_ans or "").strip()
    if not had_keyboard:
        return ans, ""
    r = "" if resp is None else str(resp).strip()

    if kind == "nogo":
        # correct rejection vs false alarm
        return ans, (1 if r == "" else 0)

    if kind == "go":
        if ans:
            if r == "":
                return ans, 0
            return ans, int(r.lower() == ans.lower())
        # go without explicit key: any press = hit
        return "", (0 if r == "" else 1)

    # forced choice / generic
    if not ans:
        return "", ""
    if r == "":
        return ans, 0
    return ans, int(r.lower() == ans.lower())


def _as_float(v: Any) -> Optional[float]:
    if v is None or v == "":
        return None
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def _as_corr(v: Any) -> Optional[int]:
    if v is None or v == "":
        return None
    if v is True or v is False:
        return int(v)
    s = str(v).strip().lower()
    if s in ("1", "1.0", "true", "yes"):
        return 1
    if s in ("0", "0.0", "false", "no"):
        return 0
    try:
        n = float(s)
        if n == 1.0:
            return 1
        if n == 0.0:
            return 0
    except ValueError:
        pass
    return None


def _safe_mean(vals: Sequence[float]) -> Optional[float]:
    if not vals:
        return None
    return round(float(mean(vals)), 6)


def _safe_median(vals: Sequence[float]) -> Optional[float]:
    if not vals:
        return None
    return round(float(median(vals)), 6)


def _gonogo_block(rows: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Hit / FA / miss / CR rates when go+nogo trials present."""
    n_go = n_nogo = n_hit = n_fa = n_miss = n_cr = 0
    for r in rows:
        kind = detect_trial_kind(r)
        if kind not in ("go", "nogo"):
            continue
        c = _as_corr(r.get("corr"))
        if c is None:
            continue
        if kind == "go":
            n_go += 1
            if c == 1:
                n_hit += 1
            else:
                n_miss += 1
        else:
            n_nogo += 1
            if c == 1:
                n_cr += 1
            else:
                n_fa += 1
    if n_go == 0 and n_nogo == 0:
        return {}
    out: Dict[str, Any] = {
        "n_go": n_go,
        "n_nogo": n_nogo,
        "n_hit": n_hit,
        "n_fa": n_fa,
        "n_miss": n_miss,
        "n_cr": n_cr,
    }
    if n_go:
        out["hit_rate"] = round(n_hit / n_go, 6)
        out["miss_rate"] = round(n_miss / n_go, 6)
    if n_nogo:
        out["fa_rate"] = round(n_fa / n_nogo, 6)
        out["cr_rate"] = round(n_cr / n_nogo, 6)
    return out


def _agg_block(rows: List[Dict[str, Any]], aggregates: Optional[Iterable[str]] = None) -> Dict[str, Any]:
    wanted = list(aggregates) if aggregates else list(_DEFAULT_AGG)
    scored = []
    rts_all: List[float] = []
    rts_ok: List[float] = []
    rts_err: List[float] = []
    n_correct = 0
    for r in rows:
        c = _as_corr(r.get("corr"))
        rt = _as_float(r.get("rt"))
        if c is None:
            # skip instructions / unscored presses — do not pollute mean_rt
            continue
        scored.append(r)
        if rt is not None:
            rts_all.append(rt)
        if c == 1:
            n_correct += 1
            if rt is not None:
                rts_ok.append(rt)
        else:
            if rt is not None:
                rts_err.append(rt)

    n_scored = len(scored)
    out: Dict[str, Any] = {}
    table = {
        "n": len(rows),
        "n_scored": n_scored,
        "n_correct": n_correct,
        "accuracy": round(n_correct / n_scored, 6) if n_scored else None,
        "mean_rt": _safe_mean(rts_all),
        "median_rt": _safe_median(rts_all),
        "mean_rt_correct": _safe_mean(rts_ok),
        "mean_rt_error": _safe_mean(rts_err),
    }
    table.update(_gonogo_block(rows))
    for k in wanted:
        if k in table:
            out[k] = table[k]
    # always include core set even if custom aggregates miss them
    for k in ("n", "n_scored", "n_correct", "accuracy", "mean_rt"):
        if k not in out and k in table:
            out[k] = table[k]
    # always attach go/nogo rates when present
    for k, v in table.items():
        if k.startswith("n_go") or k.startswith("n_no") or k.endswith("_rate") or k in (
            "n_hit", "n_fa", "n_miss", "n_cr", "n_nogo",
        ):
            out[k] = v
    return out


def resolve_group_by(
    rows: List[Dict[str, Any]],
    metrics_cfg: Optional[Dict[str, Any]] = None,
) -> List[str]:
    cfg = metrics_cfg or {}
    raw = cfg.get("group_by") or cfg.get("groupby") or cfg.get("groupBy")
    if isinstance(raw, str) and raw.strip():
        cols = [raw.strip()]
    elif isinstance(raw, (list, tuple)):
        cols = [str(x).strip() for x in raw if str(x).strip()]
    else:
        cols = []
    if cols:
        return [c for c in cols if any(c in r for r in rows)]
    # auto-detect first common factor present on any row
    for c in _AUTO_GROUP_COLS:
        if any(c in r and str(r.get(c, "")).strip() != "" for r in rows):
            return [c]
    return []


def summarize_rows(
    rows: List[Dict[str, Any]],
    metrics_cfg: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Build a run-level metrics summary dict."""
    cfg = dict(metrics_cfg or {})
    aggs = cfg.get("aggregates") or cfg.get("stats")
    if isinstance(aggs, str):
        aggs = [a.strip() for a in aggs.split(",") if a.strip()]
    overall = _agg_block(rows, aggs)
    group_cols = resolve_group_by(rows, cfg)
    by_group: Dict[str, Any] = {}
    if group_cols:
        # single-factor grouping first (multi-factor key joined by |)
        buckets: Dict[str, List[Dict[str, Any]]] = {}
        for r in rows:
            key_parts = []
            skip = False
            for c in group_cols:
                v = r.get(c, "")
                if v is None or str(v).strip() == "":
                    skip = True
                    break
                key_parts.append(str(v).strip())
            if skip:
                continue
            key = "|".join(key_parts)
            buckets.setdefault(key, []).append(r)
        for key, brow in sorted(buckets.items(), key=lambda kv: kv[0]):
            block = _agg_block(brow, aggs)
            if len(group_cols) == 1:
                block[group_cols[0]] = key
            else:
                for i, c in enumerate(group_cols):
                    block[c] = key.split("|")[i] if i < len(key.split("|")) else ""
            by_group[key] = block

    return {
        "overall": overall,
        "group_by": group_cols,
        "by_group": by_group,
        "schema": {
            "corrAns": "expected response from stimlist",
            "corr": "1=correct 0=incorrect \"\"=unscored",
            "rt": "response time seconds",
            "accuracy": "n_correct / n_scored",
            "hit_rate": "go correct / n_go (when go/nogo present)",
            "fa_rate": "nogo incorrect / n_nogo",
            "trials_csv": "long trial data (one row per trial)",
            "by_condition_csv": "one row per overall/group cell",
            "metrics_long_csv": "tidy long metric table for analysis",
        },
    }


def apply_trial_scores(
    row: Dict[str, Any],
    *,
    resp: Any,
    trial_vars: Optional[Dict[str, Any]],
    had_keyboard: bool,
) -> Dict[str, Any]:
    """Mutate/return row with corrAns + corr filled."""
    kind = detect_trial_kind(trial_vars, row)
    ans = pick_corr_ans(trial_vars)
    # also allow corrAns already on row from stimlist merge
    if not ans:
        ans = pick_corr_ans(row)
    corr_ans, corr = score_response(
        resp, ans, had_keyboard=had_keyboard, trial_kind=kind
    )
    if corr_ans:
        row["corrAns"] = corr_ans
    row["corr"] = corr
    if kind:
        row.setdefault("trial_kind", kind)
    return row


def _metric_items(block: Dict[str, Any], skip_keys: Optional[Iterable[str]] = None) -> List[Tuple[str, Any]]:
    skip = set(skip_keys or ())
    items: List[Tuple[str, Any]] = []
    seen = set()
    for k in _METRIC_ORDER:
        if k in skip or k not in block:
            continue
        items.append((k, block[k]))
        seen.add(k)
    for k, v in block.items():
        if k in seen or k in skip:
            continue
        if isinstance(v, (dict, list)):
            continue
        items.append((k, v))
    return items


def by_condition_rows(
    summary: Dict[str, Any],
    *,
    participant_id: str = "",
    session: str = "",
    uid: str = "",
    design: str = "",
) -> List[Dict[str, Any]]:
    """One flat row per overall + each group cell (Excel-friendly)."""
    rows_out: List[Dict[str, Any]] = []
    base = {
        "participant_id": participant_id,
        "session": session,
        "uid": uid,
        "design": design,
    }
    group_cols = list(summary.get("group_by") or [])
    ov = dict(summary.get("overall") or {})
    r0 = dict(base)
    r0["scope"] = "overall"
    r0["group_key"] = ""
    for c in group_cols:
        r0[c] = ""
    for k, v in _metric_items(ov):
        r0[k] = v
    rows_out.append(r0)

    by_g = summary.get("by_group") or {}
    for key, block in sorted(by_g.items(), key=lambda kv: kv[0]):
        b = dict(block or {})
        rr = dict(base)
        rr["scope"] = "group"
        rr["group_key"] = key
        for c in group_cols:
            rr[c] = b.get(c, "")
        for k, v in _metric_items(b, skip_keys=group_cols):
            rr[k] = v
        rows_out.append(rr)
    return rows_out


def metrics_long_rows(
    summary: Dict[str, Any],
    *,
    participant_id: str = "",
    session: str = "",
    uid: str = "",
    design: str = "",
) -> List[Dict[str, Any]]:
    """Tidy long table: one row per metric value (R/ggplot-ready)."""
    out: List[Dict[str, Any]] = []
    group_cols = list(summary.get("group_by") or [])
    base = {
        "participant_id": participant_id,
        "session": session,
        "uid": uid,
        "design": design,
    }

    def emit(scope: str, group_key: str, group_vals: Dict[str, Any], block: Dict[str, Any]) -> None:
        for metric, value in _metric_items(block, skip_keys=group_cols):
            row = dict(base)
            row["scope"] = scope
            row["group_key"] = group_key
            for c in group_cols:
                row[c] = group_vals.get(c, "")
            row["metric"] = metric
            row["value"] = value
            out.append(row)

    ov = dict(summary.get("overall") or {})
    emit("overall", "", {}, ov)
    by_g = summary.get("by_group") or {}
    for key, block in sorted(by_g.items(), key=lambda kv: kv[0]):
        b = dict(block or {})
        gvals = {c: b.get(c, "") for c in group_cols}
        emit("group", key, gvals, b)
    return out
