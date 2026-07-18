# PsyClaw — Real PsychoPy GUI verification (2026-06-24)

## What this doc captures

`psyclaw` skill produces `.psyexp` files that are structurally valid
(lxml 5-layer check passes) but lxml is **not enough** — PsychoPy
Builder itself does a second semantic check when loading. This file
records the bugs that were invisible to lxml but caught by real
PsychoPy `Experiment.loadFromXML()`, the fix in `scripts/json2psyexp.js`,
and the workflow for running this same test from WSL.

## The "real PsychoPy" test

`lxml` validates XML well-formedness and structural sanity. PsychoPy
Builder additionally checks that every `<Param val="..." name="..."/>` is
a known parameter of the parent component. Unknown params produce:

```
WARNING  Parameters not known to this version of PsychoPy have come
         from your experiment file: anchor, stopWithRoutine, ...
         This experiment may not run correctly in the current version.
```

The validate_psyexp.py (lxml) cannot see this — but the warning is real
and means the .psyexp will fail at runtime when PsychoPy reads the param.

## The script

Run from Windows `D:\Software\P\python.exe` (PsychoPy's own Python):

```python
# C:\Users\<user>\Desktop\check_psyexp.py
import sys
sys.path.insert(0, r"D:\Software\P\Lib\site-packages")
# Do NOT set os.add_dll_directory — see "os.add_dll_directory trap" below
from psychopy.experiment import Experiment
import warnings
warnings.filterwarnings("error", message=".*not known.*")
for fn in ["test_stroop.psyexp", "test_go-no-go.psyexp", "test_n-back.psyexp",
           "test_iaps.psyexp", "test_flanker.psyexp"]:
    p = r"C:\Users\<user>\Desktop\\" + fn
    try:
        exp = Experiment()
        exp.loadFromXML(p)
        n_routines = len(exp.routines)
        n_components = sum(len(r) for r in exp.routines.values())
        print(f"  [OK]   {fn}: {n_routines} routines, {n_components} components - CLEAN")
    except Warning as w:
        print(f"  [WARN] {fn}: {str(w)[:120]}")
    except Exception as e:
        print(f"  [FAIL] {fn}: {e}")
```

Expected output for 5/5 PASS:
```
  [OK]   test_stroop.psyexp: 4 routines, 10 components - CLEAN
  [OK]   test_go-no-go.psyexp: 4 routines, 10 components - CLEAN
  [OK]   test_n-back.psyexp: 4 routines, 10 components - CLEAN
  [OK]   test_iaps.psyexp: 5 routines, 12 components - CLEAN
  [OK]   test_flanker.psyexp: 4 routines, 10 components - CLEAN
```

## The 3 bugs the lxml validator missed

### Bug 1: `anchor` on TextComponent (⚠️ NOT YET FIXED — 2026-07-01 verified)

**What PsychoPy did:** Loaded TextComponent and warned
`anchor, anchor, anchor, anchor` (4 instances — 4 TextComponents).

**Why lxml didn't see it:** `anchor` IS a valid XML attribute on
`<Param>`. lxml checks XML well-formedness, not schema validity.

**Why it was wrong:** TextComponent in PsychoPy 2026.1.1 does **NOT**
have an `anchor` param (it has `flip`, `letterHeight`, `wrapWidth`,
`languageStyle` but no `anchor`). `anchor` is on `ImageComponent` (via
`BaseVisualComponent`).

**Status (2026-07-01):** `scripts/json2psyexp.js` L503 still emits
`const anchor = component.anchor || 'center';` — NOT removed. The
`examples/stroop/stroop_experiment.psyexp` still produces `anchor`
warnings. Fix: delete the anchor param from TextComponent and
MovieComponent generators; keep only on ImageComponent.

### Bug 2: `stopWithRoutine` on KeyboardComponent (⚠️ NOT YET FIXED — 2026-07-01 verified)

**What PsychoPy did:** Warned `stopWithRoutine` per KeyboardComponent.

**Why wrong:** KeyboardComponent in 2026.1.1 has no `stopWithRoutine` param.
The valid param for "end on key press" is `forceEndRoutine`.

**Status (2026-07-01):** Still emitted in current vendored
`scripts/json2psyexp.js`. Fix: delete the `stopWithRoutine` param
from generateKeyboardComponent.

### Bug 3: `flip` on TextComponent — this one is ACTUALLY VALID (false alarm)

Initially the validator reported `flip` as bad on TextComponent. On
inspection, `TextComponent` in 2026.1.1 DOES have `flip` (it inherits
from `BaseVisualComponent` along with `pos`, `size`, `ori`, `opacity`,
`color`, `colorSpace`, `flip`, `flipHoriz`, `flipVert`, etc.).

**Lesson:** don't trust warning messages without reading them — "not
known" is the trigger, but a component may legitimately inherit params
from `BaseVisualComponent`. Always check the component's actual
`self.params` dict before deciding a warning indicates a real bug.

### Bug 4: `conditionsFile` empty — loop has no trial data (2026-07-01)

**What PsychoPy did:** Builder opens the .psyexp and shows the flow
diagram correctly (loop wraps fixation→trial→thanks), but the
`<LoopInitiator>` has `<Param name="conditionsFile" ... val=""/>` —
empty string. At runtime, `$stim_word`, `$correct_resp` etc. resolve
to empty strings because no conditions data reaches the trial loop.

**Why:** `flow_gen_transform.py` L90-91 correctly populates
`conditionsFile` in the flowchart JSON, but `json2psyexp.js` L845
hardcodes `let conditionsFileVal = '';` and never reads
`loop.conditionsFile`. The data is present at the flowchart stage but
dropped silently during emit.

**Fix:** In `json2psyexp.js` `generateLoopInitiator()`, change L845:
`let conditionsFileVal = loop.conditionsFile || '';`

### Bug 5: `PYTHONPATH` contamination when launching PsychoPy from hermes git-bash (2026-07-01)

**Symptom:** Running `D:\Software\P\python.exe -m psychopy.app` from
hermes git-bash produces:
```
ImportError: DLL load failed while importing _rust: 找不到指定的程序。
```
Traceback shows `cryptography` imported from
`C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages`
— the hermes venv, not PsychoPy's site-packages.

**Why:** Python's `sys.path[0:2]` get hermes-agent's launch directory
and venv site-packages prepended before PsychoPy's own paths. The
hermes venv contains a Linux wheel of `cryptography` whose `_rust.pyd`
fails on Windows.

**Fix:** Launch with environment cleared:
```
cd /d/Software/P && PYTHONPATH= PYTHONHOME= ./pythonw.exe -m psychopy.app <file.psyexp>
```
For `loadFromXML()` validation only (CLI, no GUI), the import path
doesn't conflict — plain `D:\Software\P\python.exe -c "..."` works fine.
Only the GUI launch (which imports `psychopy.projects.sshkeys` →
`cryptography`) is affected.

## Validation: which Python to use?

There are at least 3 Python candidates for loading a .psyexp:

1. **`D:\Software\P\python.exe`** ✅ — PsychoPy's own Python (3.10.11).
   Has the full site-packages, no venv shebang issues. **Use this.**
2. **`E:\ProjLegacy\DeepPsych\.venv\Scripts\python.exe`** ❌ — Venv launcher.
   Shebang points to `D:\Pythons\Python312\python.exe` (doesn't exist).
   Error: `No Python at '"D:\Pythons\Python312\python.exe"'`
3. **`D:\Software\Miniconda\pkgs\python-3.13...\python.exe`** ❌ — conda
   env, may not have psychopy.

**Detection heuristic:** check `D:\Software\P\Lib\site-packages\psychopy`
exists, then use `D:\Software\P\python.exe`. Alternative: invoke via
`py.exe -3.10` only if the user has set up the Windows Python launcher
to point to that version.

## The `os.add_dll_directory` trap

If you set `os.add_dll_directory = lambda x: None` in your test script
**before** numpy is imported, numpy will fail with:

```
ImportError: DLL load failed while importing _multiarray_umath
```

This is because numpy's import-time check uses `os.add_dll_directory`
internally, and overriding it with a no-op lambda breaks the lookup.

**Workaround:** if you really need to set it (e.g. for some other
DLL), do it AFTER numpy is imported:

```python
import numpy  # import first
import os
os.add_dll_directory = lambda x: None  # then override
from psychopy.experiment import Experiment
```

But in practice, you don't need `os.add_dll_directory` at all when
calling `D:\Software\P\python.exe` from WSL — the env is set up correctly.

## The `psychopy.exe` launcher trap

`E:\ProjLegacy\DeepPsych\.venv\Scripts\psychopy.exe` is a **42KB launcher
stub** that reads a shebang and tries to invoke another Python. The
shebang points to `D:\Pythons\Python312\python.exe` which **does not
exist** on most systems. Symptom:

```
No Python at '"D:\Pythons\Python312\python.exe"'
```

**Workaround:** use `D:\Software\P\python.exe` (PsychoPy's own Python) and
invoke the module directly:

```bash
D:\Software\P\python.exe -m psychopy.app.psychopyApp --builder C:\path\file.psyexp
```

## The WMI Win32_Process.Create trick for Session 1 GUI

When you launch a Windows process from WSL via `Start-Process`, the
child inherits WSL's session (Session 0, invisible to the user). To
spawn in the **user's interactive desktop session** (Session 1), use
WMI:

```powershell
$arg = '"D:\Software\P\python.exe" "-m" "psychopy.app.psychopyApp" "--builder" "C:\Users\User\Desktop\test_flanker.psyexp"'
$pid = (Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList $arg).ProcessId
Start-Sleep -Seconds 35  # wxPython init time
Get-Process -Id $pid | Select-Object Id, SessionId, MainWindowTitle, Responding
# SessionId=1, MainWindowTitle="test_flanker.psyexp - PsychoPy Builder (v2026.1.1)"
```

Full details: see `~/.hermes/skills/devops/wsl-windows-interop/references/wsl-launch-windows-gui.md`

## Repro: end-to-end

```bash
# 1. From WSL: generate a .psyexp
python3 ~/.hermes/skills/research/psyclaw/scripts/harness_cli.py \
    --nl "做一个 Flanker 任务, 60 trials" \
    --out-dir /tmp/test_flanker/
ls /tmp/test_flanker/_work/out/flanker_task/flanker_task.psyexp

# 2. Copy to Windows desktop (WMI will need an absolute path)
cp /tmp/test_flanker/_work/out/flanker_task/flanker_task.psyexp \
   /mnt/c/Users/User/Desktop/test_flanker.psyexp

# 3. Validate with real PsychoPy (lxml + loadFromXML)
powershell.exe -Command "& 'D:\\Software\\P\\python.exe' 'C:\\Users\\User\\Desktop\\check_psyexp.py'"

# 4. Open in real PsychoPy Builder GUI (for visual verification)
powershell.exe -Command "Invoke-WmiMethod -Class Win32_Process -Name Create -ArgumentList '\"D:\\Software\\P\\python.exe\" \"-m\" \"psychopy.app.psychopyApp\" \"--builder\" \"C:\\Users\\User\\Desktop\\test_flanker.psyexp\"' | Select-Object -ExpandProperty ProcessId"
# wait 35s, then verify
powershell.exe -Command "Get-Process python -ErrorAction SilentlyContinue | Select-Object Id, SessionId, MainWindowTitle, Responding | Format-Table"

# 5. Screenshot the desktop to send back to the user
powershell.exe -Command "Add-Type -AssemblyName System.Windows.Forms; Add-Type -AssemblyName System.Drawing; \$bmp = New-Object Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width, [System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height); \$g = [Drawing.Graphics]::FromImage(\$bmp); \$g.CopyFromScreen(0, 0, 0, 0, \$bmp.Size); \$bmp.Save('C:\\Users\\User\\Desktop\\psychoPy_real.png')"
# Then: MEDIA:/mnt/c/Users/User/Desktop/psychoPy_real.png
```

## When you should rerun this

- After any change to `scripts/json2psyexp.js` (different PsychoPy
  version may add/remove params)
- After upgrading PsychoPy (`D:\\Software\\P`)
- After adding a new paradigm template that exercises new component types
- After changing the WMI launch script (verify GUI actually shows in
  the user's session)

## Computer-use GUI verification (2026-07-01)

When `computer_use` is available (cua-driver running on Windows),
this is the preferred workflow for visually confirming a .psyexp
opens correctly in Builder:

```bash
# 1. Launch PsychoPy Builder directly with the .psyexp
cd /d/Software/P && PYTHONPATH= PYTHONHOME= ./pythonw.exe -m psychopy.app \
  "C:\Users\User\AppData\Local\hermes\skills\research\psyclaw\examples\stroop\stroop_experiment.psyexp"

# 2. Wait for process to appear (~10-15s, PsychoPy splash + wxPython init)
sleep 10
tasklist //FI "IMAGENAME eq pythonw.exe"  # expect 300-400MB PID

# 3. computer_use list_apps → confirm pythonw.exe is in the list

# 4. Capture with SOM overlay
computer_use(action='capture', app='pythonw.exe', mode='som')
# Check TitleBar label: "<filename>.psyexp - PsychoPy Builder (v2026.1.1)"
# Count routine tabs (should match routines in YAML spec)
# Inspect Flow diagram for loop wrap correctness
# Verify Components panel renders Image/Keyboard/Mouse/Slider/Sound/Text

# 5. Also run loadFromXML for warnings that visual capture can't see
"D:/Software/P/python.exe" -c "
from psychopy.experiment import Experiment
exp = Experiment()
exp.loadFromXML(r'<path>.psyexp')
# watch for 'Parameters not known' in stdout
"
```

Key checks from the capture:
| Element | What to verify |
|---------|---------------|
| TitleBar | `<name>.psyexp - PsychoPy Builder (v2026.1.1)` |
| Routine tabs | Correct count, correct names |
| Flow diagram | Loop wraps correct routines, arrows connected |
| Components | 6 preference icons visible (Image/Keyboard/Mouse/Slider/Sound/Text) |
| Timeline | Components rendered as bars with correct duration |
