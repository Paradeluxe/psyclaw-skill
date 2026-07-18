# PsychoPy platform — design defects (2026-07-13 audit)

Documented during psyclaw-webui session. All paths verified on `D:\Software\P\python.exe` (PsychoPy 2026.1.1) from WSL.

## Why this matters for any PsyClaw path

Every path through PsychoPy Builder hits these defects. The fixes PsyClaw adds
(overlap validators, runtime smoke tests, PATCH_BLOCK injectors in
`scripts/run_psyexp.py`) are workarounds for missing PsychoPy features.

## Path C bypass — psyclaw-webui

psyclaw-webui skips `.psyexp` XML entirely. Backend compiles spec.yaml
into a pure Python script using `psychopy.visual.Window / TextStim / core / event`
directly. Output runs without `psyexpCompile.generateScript()` and without
`loadFromXML()` validation. **None of the defects below affect Path C.**

If you choose to keep using `.psyexp` (Path A/B), every defect below applies.

## Defects (all confirmed on PsychoPy 2026.1.1)

### 1. `Experiment.loadFromXML()` is NOT a validation gate

15 classes of broken experiments load with zero warnings. Full catalog
in `add-paradigm/references/headless-runner-real-bugs.md`. Examples:

- Empty `<Param val="" name="stopVal"/>` → infinite loop, never FINISHED
- `$column` interpolation missing → bare-name `NameError` at runtime
- Empty `correctAns` → `if (key.keys == str())` syntax error in generated runner
- Component name collisions across routines → silently overwrites globals
- Slider `storeRating` typed as string instead of bool → data logging wrong
- BOM in generated runner → `runpy.run_path` SyntaxError

**Fix:** Always pair `loadFromXML` with `scripts/run_psyexp.py --timeout 30`.
Don't trust schema-valid as runnable.

### 2. `Experiment.writeScript()` produces broken Python

`exp.writeScript(target='PsychoPy')` emits scripts with syntax errors
(empty `if` bodies, BOM headers, undefined `none` reference). These are
known PsychoPy bugs that do NOT affect Builder GUI runtime.

**Counterpart that works:** `psychopy.scripts.psyexpCompile.generateScript(exp, outfile)`
— same goal (compile .psyexp → Python script) but module-level API.
Used by Builder's internal Runner and by psyclaw's `run_psyexp.py`.

**Rule:** Use `generateScript()` not `writeScript()`.

### 3. No CLI entry point for running `.psyexp`

`psychopy.exe my_experiment.psyexp` → returns `Preferences --help`.
`psychopy --help` → also Preferences parser.
`psychopy run` / `psychopy execute` → do not exist.
`psychopy.app.runner` → wxPython GUI module, crashes outside `wx.App` loop
(`TypeError: 'module' object is not callable`).

**Only CLI path:** `generateScript()` then `runpy.run_path(outfile)`.

### 4. wxPython modal trap (GUI verification)

`computer_use` PostMessage clicks on Builder window's:
- close (X) button
- File menu → Open...
- Ctrl+O accelerator

All silently swallowed when a wxPython modal is on top (the "Save before
quitting?" dialog or file picker). Symptom: capture shows the same window,
no new dialog, no AX nodes for the missing dialog.

**Fix:** `psychopy.scripts.psyexpCompile.generateScript()` + run headless.
Or use `scripts/load_psyexp_in_builder.py` to load directly in same process.

### 5. `Parameter` valType not in any schema docs

For each component, grep `D:\Software\P\lib\site-packages\psychopy\experiment\components\<type>\__init__.py`
for `self.params['<name>'] = Param(` to see actual supported params.

**Known mismatches (psychoPy source vs vendored generator):**
- `SoundComponent.loop` — emitted in older json2psyexp.js, NOT supported 2026.1.1
- `MovieComponent.flip` and `anchor` — removed in 2026.1.1
- `SliderComponent.storeRating` — bool, not string

### 6. DLL load failure when launching from MSYS bash

Hermes venv's site-packages leak into subprocess when `PYTHONPATH` is set.
Symptom: `ImportError: DLL load failed` on Windows when launching
`D:\Software\P\python.exe` from MSYS bash.

**Fix:** Clear env vars before launch:
```bash
cd /d/Software/P && PYTHONPATH= PYTHONHOME= ./pythonw.exe -m psychopy.app
```

### 7. `psychopy.exe` launcher itself is broken

Shebang points to a path that may not exist (e.g. `D:\Pythons\Python312\python.exe`).
Canonical Python is `D:\Software\P\python.exe` or `pythonw.exe`. Never use `psychopy.exe`.

## Validation hierarchy (least to most strict)

| Level | Tool | Catches |
|-------|------|---------|
| L1 | `lxml` parse | XML well-formed |
| L2 | `<Settings>/<Routines>/<Flow>` present | structural |
| L3 | `<Routine>` has components | empty routines |
| L4 | `<LoopInitiator>` = `<LoopTerminator>` | loop nesting |
| L5 | `<Param>` has val/valType/name | field shape |
| L6 | `psychopy.experiment.Experiment().loadFromXML()` | schema-version (passes 15 broken types!) |
| L7 | `scripts/run_psyexp.py --timeout 30` | runtime (catches the 15 silent bugs) |

**Use L7 as your real gate. L6 alone is insufficient.**

## Sources

- psyclaw/builder.py (overlap validators + headless runner, 1972 lines)
- psyclaw/scripts/run_psyexp.py (PATCH_BLOCK for 15 bug classes)
- psyclaw-webui (skips `.psyexp` entirely, pure Python output)
- D:\Software\P\lib\site-packages\psychopy\experiment\components\*\__init__.py
  (ground truth for supported params, must grep this every time)