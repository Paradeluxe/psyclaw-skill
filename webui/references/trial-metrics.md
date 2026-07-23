# Trial metrics (participant CSV + summary)

## Ethos

**Pick up and use:** every finished run writes analysis-ready files under `data/` — no extra export step.

## What ships after every run

Next to the trial CSV under `data/`:

| File | Content |
|------|---------|
| `{id}_s{sess}_{ts}.csv` | **Long trial table** (default analysis table) |
| `{id}_s{sess}_{ts}_summary.json` | overall + optional by-group aggregates |
| `{id}_s{sess}_{ts}_by_condition.csv` | one row per overall/group cell (Excel) |
| `{id}_s{sess}_{ts}_metrics_long.csv` | tidy long: scope · group · metric · value (R/ggplot) |
| `instrument.json` | includes `metrics` blob (same summary) |

Mirrored to `<project>/data/` when `project_path` is set.

## Trial columns (always preferred order)

`trial, routine, loop, thisN, nReps, response, corrAns, corr, rt, keys, …session…, …stimlist…`

| Col | Meaning |
|-----|---------|
| `response` | key pressed (or blank) |
| `corrAns` | expected answer from stimlist (`corrAns` / `correctAns` / non-0-1 `correct`/`corr`) |
| `corr` | `1` correct · `0` incorrect/miss · `""` unscored |
| `rt` | seconds from keyboard onset |

Miss with an answer key → `corr=0` (forced-choice coding).

### Go / NoGo

When stimlist has `trialType` / `stimType` = `go` | `nogo` (aliases: target, no-go, inhibit, stop):

| Kind | Scoring |
|------|---------|
| go | match `corrAns` (or any key if no corrAns); miss = 0 |
| nogo | withhold = 1; any key = FA (0) |

Summary adds: `hit_rate`, `fa_rate`, `miss_rate`, `cr_rate`, `n_go`, `n_nogo`, …

Headless/Autopilot **does not** inject keys on nogo trials.

## `design.metrics` (optional, data not paradigm hardcode)

```json
"metrics": {
  "group_by": ["congruent"],
  "aggregates": ["accuracy", "mean_rt", "mean_rt_correct", "mean_rt_error", "n_scored", "n_correct"],
  "note": "optional free text"
}
```

- If `group_by` omitted, auto-detect first present of:
  `congruent`, `congruency`, `cong`, `trialType`, `trial_type`, `condition`, `cond`, `stimType`, `stim_type`, `blockType`, `block_type`
- `mean_rt` / medians use **scored** trials only (instructions with Space do not dilute RT).

## Classic literature (skill side)

When writing a marker from a classic Method / paper PDF:

1. Stimlist columns the paper uses (e.g. Stroop `congruent`; Go/NoGo `trialType`)
2. `corrAns` on every scored trial row
3. `metrics.group_by` matching those factors
4. Deliverable = runnable `<folder>.psyclaw` → user runs subjects → data pack above

| Paradigm | Stimlist factors | metrics.group_by |
|----------|------------------|------------------|
| Stroop | `congruent` yes/no | `["congruent"]` |
| Flanker | `congruency` | `["congruency"]` |
| Go/NoGo | `trialType` go/nogo | `["trialType"]` |
| N-back | `load`, `target` | `["load"]` |

Do **not** hardcode paradigm compilers in the SPA — factors are data; scoring is generic.

## Instrument panel

Shows **Accuracy**, **Mean RT**, and when present **Hit rate** / **FA rate** from `instrument.metrics.overall`.

## Code

- `backend/trial_metrics.py` — pure helpers (unit tested)
- `backend/design_compiler.py` — inlines helpers into generated `experiment.py`
