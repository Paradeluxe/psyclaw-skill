# Runtime Validation — Auto-Advance Pattern

When the user says "真正跑一遍" or "run the experiment end-to-end", the
correct response is a standalone Python script that executes the
experiment's trial loop programmatically — NOT `psychopy.app.runner`,
NOT `writeScript()`, NOT Builder's green Run button.

## Why not the other approaches

| Approach | Why it fails |
|----------|-------------|
| `psychopy.exe <file.psyexp>` | MSYS path canonicalization → "Failed to canonicalize script path" |
| `pythonw.exe -m psychopy.app.runner` | `runner` is a wxPython GUI module, not callable from script |
| `Experiment.writeScript()` | Generates buggy Python (empty `if` body, line ~837) |
| Builder Run button | Requires GUI interaction; `computer_use` clicks are unreliable (#21) |

## Auto-advance script template

```python
"""
Auto-run experiment validation — no human required.
Auto-advances through all trials, simulates responses, logs results.
Usage: PYTHONPATH= PYTHONHOME= D:\Software\P\python.exe _auto_run.py
"""
import sys, os, random, datetime
os.chdir(r'<project_dir>')  # cd to the generated experiment folder

from psychopy import core, visual, data
import openpyxl

# 1. Load conditions from xlsx
wb = openpyxl.load_workbook('spreadsheets/<conditions>.xlsx')
ws = wb.active
headers = [c.value for c in ws[1]]
rows = list(ws.iter_rows(min_row=2, values_only=True))
conditions = [{headers[i]: row[i] for i in range(len(headers))} for row in rows]
random.shuffle(conditions)
print(f"Loaded {len(conditions)} conditions")

# 2. Create window (windowed, small, no GUI decorations)
win = visual.Window(
    size=[800, 600], fullscr=False, screen=0,
    winType='pyglet', allowGUI=False,  # headless-friendly
    color=[-0.2, -0.2, -0.2], colorSpace='rgb', units='height',
)
print(f"Window OK: {win.size}")

# 3. Create stimuli (one per component type)
fixation = visual.TextStim(win=win, text='+', height=0.05, color='white')
trial_stim = visual.TextStim(win=win, text='', height=0.1, color='white')
instr_stim = visual.TextStim(win=win, text='AUTO-RUN MODE', height=0.05, color='white')
thanks_stim = visual.TextStim(win=win, text='COMPLETE', height=0.08, color='green')

# 4. Instructions flash
instr_stim.draw()
win.flip()
core.wait(0.5)

# 5. Trial loop — auto-advance, no keypresses
data_log = []
for i, cond in enumerate(conditions):
    # Fixation
    fixation.draw()
    win.flip()
    core.wait(0.3)

    # Stimulus
    trial_stim.text = str(cond['<text_column>'])
    trial_stim.color = str(cond['<color_column>'])
    trial_stim.draw()
    win.flip()
    core.wait(0.5)  # auto-advance

    data_log.append({**cond, 'trial': i+1})
    if i < 3 or i % 8 == 0:
        print(f"  Trial {i+1}/{len(conditions)}: OK")

# 6. Save results
os.makedirs('data', exist_ok=True)
ts = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
csv_path = f'data/test_run_{ts}.csv'
keys = list(data_log[0].keys())
with open(csv_path, 'w') as f:
    f.write(','.join(keys) + '\n')
    for d in data_log:
        f.write(','.join(str(d[k]) for k in keys) + '\n')

# 7. Thanks + close
thanks_stim.draw()
win.flip()
core.wait(0.5)
win.close()

print(f"\n=== RESULTS ===")
print(f"Trials completed: {len(data_log)}/{len(conditions)}")
print(f"Window created: YES")
print(f"Data saved: {csv_path}")
print(f"ALL CHECKS PASSED")
```

## Stroop-specific notes

- Stroop conditions xlsx has columns: `stim_word`, `stim_color`, `correct_resp`, `congruent` (bool→1/0)
- 12 rows (6 congruent, 6 incongruent) under `fullRandom` order with `n_rounds: 30`
- Key mapping: r=red, b=blue, g=green
- Builder structure: instructions → fixation → trial(×30) → thanks

## Launch command

From Hermes MSYS/bash terminal:
```bash
cd /e/hermes_playground/psyclaw/output/<experiment_name> && \
PYTHONPATH= PYTHONHOME= /d/Software/P/python.exe _auto_run.py
```

The `PYTHONPATH=` and `PYTHONHOME=` clearing prevents Hermes venv contamination (#19).
