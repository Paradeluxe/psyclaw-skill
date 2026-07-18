# PsychoPy GUI + CLI reality (2026-07-13)

The facts that justify PsyClaw existing as a separate project, and that drive
the architecture decision for `target='python'` output mode and the
`psyclaw-webui` Flask frontend.

## 1. `psychopy.exe` is NOT a CLI runner

| Command | Actual behavior |
|---------|-----------------|
| `psychopy.exe experiment.psyexp` | Runs `psychopy.tools.preferences` CLI, prints `PsychoPy Preferences --help` |
| `psychopy --help` | Same Preferences parser |
| `psychopy run experiment.psyexp` | Does not exist |
| `psychopy launch experiment.psyexp` | Does not exist |
| `psychopy execute experiment.psyexp` | Does not exist |
| `from psychopy.app.runner import Runner; Runner().run(...)` | `TypeError: 'module' object is not callable` outside `wx.App` loop |

**Correct paths to run a .psyexp headless:**

```python
# Path A: generate runner script + runpy (used by scripts/run_psyexp.py)
from psychopy.experiment import Experiment
from psychopy.scripts import psyexpCompile
import runpy
exp = Experiment.fromFile("experiment.psyexp")
psyexpCompile.generateScript(exp, "_runner.py", target="PsychoPy")
runpy.run_path("_runner.py")

# Path B: in-process Experiment.run()
exp = Experiment.fromFile("experiment.psyexp")
exp.run()
```

`Experiment.writeScript()` (the method, not the module function) is **broken**
— emits Python with syntax errors (empty `if` bodies, BOM header, undefined
`none`). Don't use it. Use `psyexpCompile.generateScript()` (the module
function).

## 2. `loadFromXML` is a forgiving parser, not a validator

`psychopy.experiment.Experiment().loadFromXML(path)` accepts 15+ classes of
broken experiments with **zero warnings**. Full catalog in
`add-paradigm/references/headless-runner-real-bugs.md`:

- Empty `stopVal` -> routine hangs forever
- `$column` interpolation missing -> `NameError` at trial time
- `correctAns=""` -> `if (key.keys == str())` (syntax-broken code-gen)
- Component name collisions across routines -> `WARNING duplicate variable name(s)`
- UTF-8 BOM in generated runner -> `runpy.run_path` fails
- `globals()[name] = ...` doesn't reach function-local lookups -> bare-name references unresolved

**Always pair loadFromXML with `scripts/run_psyexp.py --timeout 30`** before
declaring a paradigm shippable.

## 3. .psyexp XML is internal representation, not a public API

There is no XSD, no schema doc, no public CI gate. The "spec" lives in
`D:\Software\P\Lib\site-packages\psychopy\experiment\components\<type>\
__init__.py` — each Component's `self.params['<name>'] = Param(...)` lines are
the only authoritative source. To know what params a `<TextComponent>` supports
in 2026.1.1, grep that file. Vendored generators drift.

## 4. The 15 bug classes are all downstream of the XML format

| Bug class | Root cause | Disappears with target='python'? |
|-----------|-----------|----------------------------------|
| `loadFromXML` silent accept | Parser designed for max compat | YES — no XML |
| `writeScript()` syntax errors | XML-to-Python emit bugs | YES — we write Python directly |
| `correctAns=""` empty if | Schema accepts empty string | YES — we emit `if key == "none"` |
| Component name collisions | XML doesn't enforce uniqueness | YES — we namespace |
| BOM in runner | psyexpCompile writes UTF-8 BOM | YES — `open(path, "w", encoding="utf-8")` |
| `none` undefined | Schema references undefined name | YES — we inject `none = None` ourselves |
| Component type param drift | Vendored generators lag real params | YES — we use real PsychoPy Python API |
| wxPython modal trap | GUI uses wxWidgets | N/A — we're CLI/web |
| `psychopy.exe` no CLI | PsychoPy doesn't ship one | YES — we just `python experiment.py` |
| `Component.x += y` typo | No schema validation | YES — Python parser catches |
| `_keyboard_component` correctAns default | XML schema allows "" | YES — we default `correct_key="none"` |
| ... | ... |