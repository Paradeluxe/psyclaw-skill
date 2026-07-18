# json2psyexp.js — known emit bugs and their fixes

This is a class-level bug catalog: every entry here is a `let X = ''` or `val="True"` hardcode in `scripts/json2psyexp.js` that silently swallows data from the flowchart JSON. The bugs share three properties:

1. **No warning, no error** — `lxml` validator passes, real PsychoPy `loadFromXML()` may pass too (the bug only shows when the data is read at runtime)
2. **Single-loop Stroop doesn't trigger them** — need nested loops, non-trial loops, or non-default paradigm values to surface
3. **Fix is always the same shape** — read the field from the input object instead of hardcoding the default

## Catalog (2026-07-01)

### Bug 1 — `conditionsFile` hardcoded empty (lines 755, 845)

**Symptom**: YAML has `loops[0].spreadsheet.file: "stroop_conditions.xlsx"`. Flowchart JSON has `loops[0].conditionsFile: "stroop_conditions.xlsx"`. The `.psyexp` `<LoopInitiator>` has `<Param name="conditionsFile" val=""/>` empty.

**Root cause** (two places must both be fixed):
- L755: `processedLoops` return object in `generateFlow()` did not include `conditionsFile` — the field is silently dropped during the L750-759 loop transform.
- L845: `generateLoopInitiator()` had `let conditionsFileVal = '';` — hardcoded default, never read from `loop.conditionsFile`.

**Fix**:
```js
// L755 area — add to return object:
conditionsFile: loop.conditionsFile || '',

// L845:
let conditionsFileVal = loop.conditionsFile || '';
```

**Runtime impact when broken**: PsychoPy Builder renders the loop visually. `$column` interpolation (e.g. `$stim_word`, `$correct_resp`) resolves to empty strings at runtime because no conditions data reaches the loop. Trial counts look right; every trial is blank.

---

### Bug 2 — `correctAns` hardcoded empty (line 662)

**Symptom**: Keyboard component in trial routine has `correctAns=""` even when YAML specifies `correct_ans: $correct_resp`. Stroop runs but accuracy is always 0/1 because no correct answer is registered.

**Root cause** (line 662):
```js
<Param val="" valType="str" updates="constant" name="correctAns"/>
```

**Fix**:
```js
<Param val="${component.correctAns || ''}" valType="str" updates="constant" name="correctAns"/>
```

**Note**: `flow_gen_transform.py` L26 already maps `correct_ans → correctAns` correctly. The data IS in the flowchart JSON; the emit layer just doesn't read it.

---

### Bug 3 — `isTrials` hardcoded True (lines 753, 865)

**Symptom**: Block-level outer loops (e.g. outer=3 blocks, inner=10 trials) all show `isTrials=True` in the .psyexp. PsychoPy data logging counts block-level iterations as trials. Single-loop designs (Stroop) work fine because there's nothing to compare against.

**Root cause** (two places):
- L753: `processedLoops` return object did not include `isTrials` field. Field silently dropped.
- L865: `generateLoopInitiator()` had `<Param name="isTrials" val="True" valType="bool"/>` — hardcoded.

**Fix**:
```js
// L753 area — add to return object:
isTrials: !!loop.isTrials,

// L865:
<Param name="isTrials" updates="None" val="${loop.isTrials ? 'True' : 'False'}" valType="bool"/>
```

**Verification recipe**: build a nested-loop YAML (see `templates/nested-loops-test.yaml` for a working example). Inner loop should be `is_trials: true`, outer should be `is_trials: false`. Emit, then grep for `name="isTrials"` near each `LoopInitiator` — values must differ.

---

### Bug 4 — stale `anchor` / `stopWithRoutine` params (text/movie/keyboard components)

**Symptom**: PsychoPy 2026.1.1 `loadFromXML` warns:
```
Parameters not known to this version of PsychoPy: anchor, stopWithRoutine, anchor, anchor, stopWithRoutine, anchor
```

**Root cause** (3 places):
- `generateTextComponentFromSchema` and `generateMovieComponentFromSchema` emit `<Param name="anchor" val="center">` even though PsychoPy 2026 dropped `anchor` from these (only `ImageComponent` keeps it via `BaseVisualComponent`).
- `generateKeyboardComponentFromSchema` emits `<Param name="stopWithRoutine" val="True">` even though this was renamed/moved in 2026.

**Fix**: delete the `<Param val="..." name="anchor"/>` line from the text and movie generators; delete the `<Param val="..." name="stopWithRoutine"/>` line from the keyboard generator.

**Status**: **Fixed in current code** (the generators no longer emit these). The old `examples/stroop/stroop_experiment.psyexp` (generated before the fix) still had them and produced 6 warnings. **Always regenerate examples after patching json2psyexp.js.**

---

## Detection recipe

To check whether any of the above are present in a generated `.psyexp`:

```bash
# Bug 1: conditionsFile empty
grep -n 'name="conditionsFile"' <file>.psyexp | grep 'val=""'

# Bug 2: correctAns empty in a non-instructions trial
grep -n 'name="correctAns"' <file>.psyexp | grep 'val=""'

# Bug 3: isTrials hardcoded — build nested loop and check both values
grep -B1 -A1 'name="isTrials"' <file>.psyexp

# Bug 4: stale params
grep -n 'name="anchor"\|name="stopWithRoutine"' <file>.psyexp
```

If any match, the emit is broken. Re-run `node scripts/emit.js <flowchart>.json <out>.psyexp` after applying the corresponding fix.

## Why these bugs were missed in the original validation

The skill's "Verified samples" section (SKILL.md) lists 5 paradigms (Stroop/GoNoGo/Flanker/N-back/IAPS) all passing `loadFromXML` with zero warnings. But all 5 are single-loop designs. The 5-paradigm sample does not exercise:

- A non-trial loop (`is_trials: false`)
- A nested loop (one loop wrapping another)
- A keyboard component whose `correctAns` is non-empty in the YAML (most templates leave it empty for the input routine, the wrong default matches)

To restore confidence after each json2psyexp.js patch, regenerate at minimum one **nested-loop YAML** (use `templates/nested-loops-test.yaml`) and verify:
1. Outer `isTrials=False`, inner `isTrials=True` (different values)
2. Inner loop's `conditionsFile` is non-empty
3. `loadFromXML` reports zero warnings
4. Flow element order: `[outer_init, inner_init, ..., inner_term, ..., outer_term]`

The single-loop Stroop regression is a necessary-but-not-sufficient check.
