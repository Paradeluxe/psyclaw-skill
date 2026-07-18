# GUI verification pitfalls (2026-07-01)

## Why this doc exists

Earlier SKILL.md described a canonical "use computer_use to open the .psyexp
in PsychoPy Builder and visually verify" workflow. **That workflow is
unreliable in practice** because wxPython's modal lifecycle blocks
PostMessage clicks. This doc records what was tried, what failed, and
what works instead.

## The reliable open path: `pythonw.exe -m psychopy.app <path>` (2026-07-01)

`scripts/load_psyexp_in_builder.py` was originally listed as the
"programmatic load + show" recommended path. **It is NOT reliable** when a
Builder instance is already running in the same desktop session:

```
File "<psychopy-site-packages>\psychopy\app\builder\builder.py", line 124, in __init__
    self.dpi = self.app.dpi
AttributeError: 'NoneType' object has no attribute 'dpi'
```

Cause: `BuilderFrame.__init__` calls `self.app.dpi` but does NOT initialize
`self.app = wx.GetApp()` first when a second instance is launched. wxPython's
wx.App singleton already belongs to the first Builder; the second Builder
gets `self.app = None`. Workaround (close the first Builder via GUI) is
itself blocked by the wxPython Save? modal — see SKILL pitfall #21.

**The path that actually works end-to-end**: pass the .psyexp as a positional
argument to `pythonw.exe -m psychopy.app`. PsychoPy's `app/__main__.py`
calls `Experiment.loadFromXML(path)` before showing the frame, so no
file-picker dialog ever opens.

```bash
# Step 1: close any stale Builder (reliable, see SKILL pitfall #23)
powershell -ExecutionPolicy Bypass -File scripts/close_psychopy.ps1

# Step 2: open the target file directly
 PYTHONPATH= PYTHONHOME= PYTHONNOUSERSITE=1 ./pythonw.exe \
    -m psychopy.app "<absolute/path/to/file.psyexp>"

# Step 3: poll for the title bar to confirm load
powershell -Command "Get-Process pythonw | Where-Object { \$_.MainWindowTitle -like '*PsychoPy*' }"

# Step 4: visual sanity check (capture mode=som is reliable AFTER load)
computer_use(action='capture', app='pythonw', mode='som')

# Step 5: close when done
powershell -ExecutionPolicy Bypass -File scripts/close_psychopy.ps1
```

`scripts/load_psyexp_in_builder.py` is still useful for one case:
constructing an `Experiment` from scratch programmatically (golden sample
generation for audit purposes). For "verify this .psyexp opens in
Builder", use the `pythonw.exe -m psychopy.app <path>` form above.

## What was tried (and failed) on 2026-07-01

Setup:
- PsychoPy 2026.1.1 in `<psychopy-install>\`
- Builder already running (`pythonw.exe` PID 9428), window `untitled.psyexp - PsychoPy Builder (v2026.1.1)`
- Target: load `examples/parallel_loops_out/_work/parallel_loops.psyexp`
- Tool: `computer_use(action='click', element=N)` with ref IDs from SOM capture

Attempts:
1. `computer_use(action='click', element=45)` on the 文件 (File) MenuItem
   → no menu appeared, capture unchanged.
2. `computer_use(action='click', coordinate=[800, 300])` on Builder canvas
   + `computer_use(action='key', keys='ctrl+o')`
   → no Open dialog appeared.
3. `computer_use(action='focus_app', app='pythonw', raise_window=True)`
   → raise_window=True silently dropped (interface only supports `false`).
4. `computer_use(action='click', element=44)` on the `关闭` (X) window button
   → Builder stayed open, capture unchanged. The "Save before quitting?"
   modal was likely blocking but invisible in the AX tree (no nodes surfaced
   for it).
5. Direct `<psychopy-python> -c "from psychopy.app import builder; ..."`
   → `ImportError: cannot import name '_imaging' from 'PIL'` because Hermes's
   venv site-packages (containing a Linux PIL wheel) was prepended to sys.path
   via PYTHONPATH or sys.path[0] pollution.

The correct action: **don't fight the GUI.** Trust `loadFromXML` 0 warnings
as ground truth. Use GUI capture ONLY for the post-load visual sanity check
(title bar, routine tab count, Flow diagram), not for click-driven actions.

## What works

### Headless validation (canonical, use this for CI/regression)

```bash
<psychopy-python> scripts/validate_load_from_xml.py <file.psyexp
```

Returns 0 on zero warnings, 1 on warnings, 2 on exceptions. No GUI needed.
This is what `regression_suite.sh` runs.

### Programmatic load + show (only for constructing Experiment from scratch)

```bash
# From any clean environment (no hermes venv on sys.path):
<psychopy-python> scripts/load_psyexp_in_builder.py <file.psyexp
```

Use this ONLY when you need to construct an `Experiment` in-process and
manipulate it (e.g. golden sample generation for audit purposes). For
"verify this .psyexp opens in Builder", use the
`pythonw.exe -m psychopy.app <path>` form in the section above — it
does NOT have the second-instance wx.App singleton conflict.

### Headless validation (canonical, use this for CI/regression)

```bash
<psychopy-python> scripts/validate_load_from_xml.py <file.psyexp
```

Returns 0 on zero warnings, 1 on warnings, 2 on exceptions. No GUI needed.
This is what `regression_suite.sh` runs.

## When GUI capture IS useful

- Confirming the .psyexp opens in the right Builder version (title bar check)
- Counting routine tabs to confirm Flow count matches YAML
- Inspecting Flow diagram for visual block style (red = nested initiator,
  blue = routine, white = outside-loop)
- Screenshotting the experiment for documentation

Don't use it for: opening files, dismissing dialogs, clicking through
menus, driving any wxPython modal interaction.

## Anti-patterns

- ❌ `taskkill /F /IM pythonw.exe` — kills Hermes's own pythonw workers
- ❌ `taskkill /F /PID <pid>` without cross-checking the session ID
- ❌ `computer_use` click on wxPython `关闭 (X)` button when a modal is open
- ❌ `computer_use` Ctrl+O when the Builder window is not foreground
- ❌ Running `from psychopy.app import builder` from a Hermes-spawned Python
  (sys.path pollution from hermes-agent venv → PIL/cryptography DLL load fails)

## Mental model

- **Generation** = json2psyexp.js emit, no GUI needed
- **Validation** = `loadFromXML` 0 warnings = "would PsychoPy accept this?"
- **Visual sanity** = GUI capture of an already-loaded file, no clicking
- **Clicking** = avoid, use programmatic load via `load_psyexp_in_builder.py`
