# Component type coverage audit (PsychoPy 2026.1.1)

Generated 2026-07-01 by emitting a YAML containing one of every supported type, running `node scripts/emit.js`, and reading the resulting `.psyexp` against `D:\Software\P\lib\site-packages\psychopy\experiment\components\<type>\__init__.py`.

## Coverage matrix (PsychoPy 2026.1.1)

| Type      | Dispatcher branch | Generate func | LoadFromXML warnings | Status     |
|-----------|-------------------|---------------|----------------------|------------|
| `text`    | ✅                | ✅            | 0                    | OK         |
| `image`   | ✅                | ✅            | 0                    | OK         |
| `audio`   | ✅                | ✅            | 0                    | OK (deprecated `loop` Param removed) |
| `video`   | ✅                | ✅            | 0                    | OK (deprecated `flip`/`anchor` Params removed) |
| `keyboard`| ✅                | ✅            | 0                    | OK (`stopWithRoutine` Param removed) |
| `mouse`   | ✅                | ✅            | 0                    | OK         |
| `slider`  | ✅                | ✅            | 0                    | OK (`storeRating`/`forceEndRoutine` emit as `bool` not `str`) |
| `code`    | ✅                | ✅            | 0                    | OK (`extendedCode` valType + HTML escape) |

All 8 component types have working dispatch + emit. The dispatcher is in
`scripts/json2psyexp.js` `generateComponents()` (~L428-446). Param lists
were verified against
`D:\Software\P\lib\site-packages\psychopy\experiment\components\<type>\__init__.py`
on 2026-07-01; any time PsychoPy ships a new release, re-grep and
re-validate.

## Open emit-bug table (per component, against 2026.1.1 param source)

| Component        | Param in vendored emit | PsychoPy 2026.1.1 supports? | Fix                               |
|------------------|------------------------|------------------------------|-----------------------------------|
| SoundComponent   | `loop`                 | ❌                           | drop the Param line               |
| SoundComponent   | `hamming`              | ✅                           | keep                              |
| SoundComponent   | `stopWithRoutine`      | n/a (see below)              | n/a                               |
| MovieComponent   | `flip`                 | ❌                           | drop the Param line               |
| MovieComponent   | `anchor`               | ❌ (only Image keeps it)     | drop the Param line               |
| MovieComponent   | `loop`                 | ✅                           | keep                              |
| TextComponent    | `anchor`               | ❌                           | already removed (see bug catalog) |
| KeyboardComponent| `stopWithRoutine`      | ❌                           | already removed (see bug catalog) |

Verified by grepping `D:\Software\P\lib\site-packages\psychopy\experiment\components\<type>\__init__.py` for `self.params['<name>'] = Param(` — `name="loop"` does not appear in `sound/__init__.py`; `name="flip"` does not appear in `movie/__init__.py`.

## How to add a new component type

1. **Read the target type's `__init__.py` for the actual param list** — the vendored generator is the source of bugs; the PsychoPy source is the source of truth. Grep for `self.params['<name>'] = Param(` to enumerate every supported Param.
2. **Extract a golden XML reference first** — write a 3-line Python probe (see "Extracting golden XML reference" below) that constructs the component in-process, saves via `exp.saveToXML()`, then grep the resulting .psyexp for `<ComponentClass.*?</ComponentClass>` to get the **exact attribute set, param order, valType, updates, and HTML escape style** PsychoPy itself emits. Don't invent any of these — copy them verbatim from the golden file.
3. **Write `generate<Type>ComponentFromSchema(component, routineName)` in `scripts/json2psyexp.js`** — emit `<ComponentClass name="..." plugin="None">` followed by one `<Param val=... valType=... updates=... name=.../>` per supported param. Optional params default-construct from the input object (`component.<param> ?? defaultValue`). Match the param ORDER from the golden XML, not alphabetical.
4. **Add an `else if (component.type === '<type>')` branch in `generateComponents()` (~L428)**.
5. **Add `<type>` to `VALID_COMPONENT_TYPES` in `scripts/spec_validator.py`** (if not already there from a previous partial fix).
6. **Write a YAML test in `examples/<type>_test.yaml`** that exercises at least: name override, one or more body params, and any field-specific HTML escape cases (e.g. for CodeComponent: a Begin Routine containing `<b>"hi" & bye</b>` to verify roundtrip).
7. **Run `bash scripts/regression_suite.sh`** — exit 0 confirms all YAML specs (existing + new) load with zero warnings.

### CodeComponent-specific gotchas (added 2026-07-01)

- **`valType="extendedCode"`**, NOT `str` — `extendedCode` is PsychoPy's special code-typed string param that allows `$variable` interpolation and supports multi-line bodies via `val=`.
- **HTML escape required on every body field** — at minimum `"` → `&quot;` (or `&apos;`), `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;`, `'` → `&apos;`. The golden XML shows PsychoPy uses `&quot;` for `"` and `&apos;` for `'` interchangeably; either works. **Without escape, `Begin Routine: "x = 'hello'"` becomes `<Param val="x = 'hello'"/>` which lxml strict-mode rejects on the unescaped `'`.** Roundtrip verification: load the .psyexp via PsychoPy and read `exp.routines['<r>'].children[-1].params['<phase>'].val` — should equal the original user string byte-for-byte.
- **Two parallel param sets** — 6 Py phases (Before Experiment, Begin Experiment, Begin Routine, Each Frame, End Routine, End Experiment) + 6 JS mirrors (Before JS Experiment, etc.). User YAML keys follow `code_test.yaml` convention: snake_case with `_js_` infix for JS phases.
- **`Code Type` is a `str` choice** with `allowedVals=['Py', 'JS', 'Both', 'Auto->JS']`. Default `'Py'` matches what most users want.
- **`name` is BOTH a component attribute** (`<CodeComponent name="my_code" plugin="None">`) **AND a Param** (`<Param val="my_code" valType="code" updates="None" name="name"/>`). Both must agree. Easy to forget the attribute; the Param alone makes PsychoPy raise "Component name mismatch".

### Extracting golden XML reference (recipe)

```python
# D:/Software/P/python.exe -c "..." (strip hermes-agent sys.path first)
from psychopy.experiment import Experiment
from psychopy.experiment.routines import Routine
from psychopy.experiment.components.code import CodeComponent  # or any type

exp = Experiment()
r = Routine(name='probe', exp=exp)
cc = CodeComponent(exp=exp, parentName='probe', name='my_code',
                   codeType='Py',
                   beginRoutine='msg = "hello"',
                   endRoutine='print(msg)',
                   eachFrame='pass')
r.append(cc)
exp.routines['probe'] = r
exp.flow.addRoutine(r, 0)
exp.saveToXML('examples/code_probe_REF.psyexp')
```

Then `grep -A 20 '<CodeComponent' examples/code_probe_REF.psyexp` to see the verbatim golden XML.

## Regression test recipe (post-fix)

```bash
cd ~/.hermes/skills/research/psyclaw
.venv/Scripts/python scripts/flow_gen_transform.py \
  templates/component-coverage-test.yaml \
  /tmp/component_flowchart.json --verbose
node scripts/emit.js /tmp/component_flowchart.json /tmp/component_test.psyexp

# 1. Dispatcher coverage — every type should have ≥1 component
for t in TextComponent ImageComponent SoundComponent MovieComponent \
         KeyboardComponent MouseComponent SliderComponent CodeComponent; do
  count=$(grep -c "<$t " /tmp/component_test.psyexp)
  echo "$t: $count"
done

# 2. loadFromXML zero warnings
D:/Software/P/python.exe -c "
import logging
logging.basicConfig(level=logging.WARNING)
from psychopy.experiment import Experiment
exp = Experiment()
exp.loadFromXML(r'C:\Users\User\AppData\Local\Temp\component_test.psyexp')
print('OK')
" 2>&1 | grep -iE 'warning|error|OK'

# 3. Optional: scan with scripts/check_emit_bugs.py
.venv/Scripts/python scripts/check_emit_bugs.py /tmp/component_test.psyexp
```

Expected output after all bugs are fixed: every component type has `count ≥ 1`, `OK` with zero warnings, `PASS` from check_emit_bugs.py.

## Why this audit was needed

The "5/5 PASS" validation in SKILL.md uses paradigms (Stroop/GoNoGo/Flanker/N-back/IAPS) that all use the same 5 component types (text, image, audio, video, keyboard). None of them exercise `mouse`, `slider`, or `code` — and none of the in-use types stress-test edge cases (multi-loop, non-trial loop, real condition file). The 5-paradigm test is **necessary but not sufficient**. A YAML that uses a type that has no dispatcher branch will emit silently, and a YAML that uses a single trial loop will not catch the `isTrials` hardcode bug. See `references/json2psyexp-emit-bugs.md` for the full bug catalog.
