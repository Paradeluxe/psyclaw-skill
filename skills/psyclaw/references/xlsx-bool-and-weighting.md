# xlsx bool coercion + cell-weighting recipe (Stroop case study)

## Problem

Two bugs surfaced when a real user reviewed the generated Stroop
conditions.xlsx (after `.venv/bin/python scripts/harness_cli.py --nl "做一个 Stroop 实验 30 trials"`):

1. **`type: bool` columns wrote Python `True`/`False`** — Pavlovia (PsychoPy
   online) and some offline PsychoPy builds reject bool cells in the
   data file after CSV conversion. Symptom: codec error on data upload.
2. **Stroop conditions were weighted 2:1 (congruent:incongruent)** — the
   template listed 6 congruent rows duplicated (RED/red×2, BLUE/blue×2,
   GREEN/green×2) plus 6 incongruent rows once. Under `fullRandom` with
   `n_rounds: 30`, that produces ~20 congruent and ~10 incongruent
   trials instead of the textbook 1:1.

## Fix 1 — bool → int (in `scripts/xlsx_generator.py`)

```python
# Before (buggy)
if col_type in ("bool",):
    if isinstance(val, bool): return val
    if isinstance(val, str): return val.lower() in ("true","1","yes")
    return bool(val)

# After (correct)
if col_type in ("bool",):
    if isinstance(val, bool): return 1 if val else 0
    if isinstance(val, str): return 1 if val.lower() in ("true","1","yes") else 0
    return 1 if val else 0
```

Verified: `ws.cell(2,3).value` is `<class 'int'>` after the fix.

## Fix 2 — equal cell weighting (in `templates/stroop.yaml.tmpl`)

Row counts must match the design's intended cell weighting. For Stroop:

| Design | Congruent rows | Incongruent rows | Ratio |
|--------|---------------:|-----------------:|------:|
| Buggy (original) | 6 (duplicated 2×) | 6 | **2:1** ❌ |
| First attempt | 3 (one of each) | 6 | **1:2** ❌ |
| Correct (current) | 6 (each cell ×1) | 6 (each cell ×1) | **1:1** ✅ |

When you write a new paradigm template, always do this checklist:

```python
from openpyxl import load_workbook
wb = load_workbook("spreadsheets/conditions.xlsx")
ws = wb.active
# 1. bool columns are int, not bool
for row in ws.iter_rows(min_row=2, values_only=False):
    for cell in row:
        if cell.data_type == "b":  # openpyxl bool
            raise SystemExit(f"row {cell.row} col {cell.column_letter} is bool, must be int")
# 2. row counts match intended weighting
from collections import Counter
condition_col = ws.max_column  # adjust
counts = Counter(r[condition_col - 1] for r in ws.iter_rows(min_row=2, values_only=True))
print(counts)  # should be balanced across design cells
```

## How this maps to PsyClaw's design philosophy

**The fact that the user caught both bugs by looking at one xlsx file proves
the smoke-test loop is worth the 5 seconds.** Don't skip the "show user the
artifact and let them inspect" step just because the pipeline returned 0.

The two fixes also reflect a deeper principle: **the generated spreadsheet
is the experiment's ground truth for design intent**. If you claim a 2×2
factorial but the spreadsheet has 3 rows of condition A and 12 of condition B,
the experiment will produce skewed data and the user will find out 3 months
later during analysis. The xlsx is the contract.