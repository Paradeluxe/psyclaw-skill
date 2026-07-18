# Builder fixes — 2026-07-12

Four critical bugs discovered and fixed during batch testing of 147 experiments across three categories.

## 1. `_gen_generic_conditions` misreads new-style specs

**Symptom**: conditions.xlsx contained garbage rows — `condition="columns"`, `condition="rows"`, `stim_text="?"`.

**Root cause**: The fallback generator called `spec.get("conditions", {}).keys()` which returns the top-level YAML dict keys (`['columns', 'rows']`) instead of parsing the `rows` list inside.

**Fix** (builder.py ~line 828):
```python
def _gen_generic_conditions(spec: dict) -> list[dict]:
    conds_block = spec.get("conditions", {})
    
    # New format: conditions.columns + conditions.rows
    if "rows" in conds_block and isinstance(conds_block.get("rows"), list):
        rows = conds_block["rows"]
        trials = []
        for row in rows:
            trial = {"condition": "default", "stim_text": "?", "stim_color": "white", "correct_key": "space"}
            if isinstance(row, dict):
                trial["stim_text"] = str(row.get("stimulus", row.get("stim_text", "?")))
                trial["correct_key"] = str(row.get("correct_resp", row.get("correct_key", "space")))
                trial["stim_color"] = str(row.get("color", "white"))
                trial["condition"] = str(row.get("condition", "default"))
            trials.append(trial)
        return trials
    
    # Old format: conditions keys are condition names
    n = spec.get("trials_per_condition", 30)
    conds = list(conds_block.keys()) if isinstance(conds_block, dict) else []
    ...
```

**Key mapping**: `correct_resp` (from spec template) → `correct_key` (xlsx column referenced by `$correct_key` in .psyexp).

## 2. Empty `correctAns` causes PsychoPy code-gen syntax error

**Symptom**: `Experiment.writeScript()` produces broken Python at line ~534:
```python
if (instr_key.keys == str()) or (instr_key.keys == ):
```
The empty comparison after `==` is a syntax error.

**Root cause**: `_keyboard_component` emitted `correctAns=""` for instructions and thanks routines (which don't have correct answers). PsychoPy 2026.1.1's code generator can't handle empty `correctAns`.

**Fix** (builder.py line 139):
```python
("correctAns", correct_key_col if correct_key_col else "none", "code", ...),
```
Default to `"none"` instead of empty string. Instructions and thanks routines get `"none"` as a dummy correct answer, which is harmless (they don't check correctness anyway).

## 3. ISI placement hardcoded at stim_start + 3.0

**Symptom**: Pink shaded "isi" region visible at a fixed 3s mark in Builder timeline, regardless of whether the trial is response-terminated or fixed-duration.

**Root cause**: `_build_generic_routine` always used `start_time=str(stim_start + 3.0)` for the StaticComponent.

**Fix** (builder.py ~line 641):
```python
if isi_ms:
    if until_response:
        isi_start = stim_start  # Short blank after response ends routine
    else:
        max_wait_s = float(max_wait) if max_wait else 2.0
        isi_start = stim_start + max_wait_s  # After response window
    rt.append(_static_component("isi", isi_ms / 1000.0, start_time=str(isi_start)))
```

For response-terminated trials, ISI starts with the stimulus — the routine ends when the response comes, so the visible ISI is the brief blank at end-of-routine. For fixed-duration trials, ISI starts after the response window.

## 4. Missing instructions and thanks routines

**Symptom**: Flow panel showed only `trial` routine with a loop. No welcome screen, no debriefing.

**Fix**: Added two new routine builders:
- `_build_instructions_routine(spec)` — TextComponent + KeyboardComponent (SPACE to advance). Reads `spec.instructions` or shows default.
- `_build_thanks_routine(spec)` — TextComponent + KeyboardComponent (any key to exit). Reads `spec.thanks` or shows default.

New Flow order: `instructions → [trials loop] → thanks`

Instructions text is paradigm-aware:
- Stroop: color-key mapping (R=Red, B=Blue, G=Green, N=Brown, P=Purple)
- Flanker: arrow directions (LEFT for ←, RIGHT for →)
- Simon: "respond based on COLOR, not position"
- etc.
- Unknown paradigms: generic "Press LEFT for one response, RIGHT for the other"

## 7. Single-routine → three-routine refactor (v3.2)

**Symptom**: User rejected having all components (fixation, stimulus, keyboard, ISI) crammed into one routine. "为什么你所有的component都挤在一个routine里，而且我从来没看到过isi这样的写法，我一般都是单独写一个routine"

**Fix**: Replaced `_build_generic_routine()` with three separate functions:
- `_build_fixation_routine(spec)` → "fixation" routine: TextComponent "+" for ~500ms
- `_build_trial_routine(spec, conditions)` → "trial" routine: TextComponent + KeyboardComponent
- `_build_isi_routine(spec)` → "isi" routine: StaticComponent blank for ~300ms

New Flow: `instructions → [ fixation → trial → isi ] × N → thanks`

Each routine has ONE job. This matches standard PsychoPy Builder practice.

## 8. timeout_ms: no default unless paper specifies

**Symptom**: Initially defaulted to 0 (no timeout), briefly changed to 3000ms during fix session.

**User feedback**: "如果文章没有说timeout，那我们也可以不做呀"

**Fix**: Reverted to 0 default. Only set timeout if original paper explicitly specifies a response deadline.

**Fix** (builder.py line 591):
```python
resp_keys = spec.get("response", {}).get("keys", ["space"])
if isinstance(resp_keys, dict):
    keys = list(resp_keys.keys()) or ["space"]
elif isinstance(resp_keys, list):
    keys = resp_keys or ["space"]
else:
    keys = ["space"]
```

## 6. Paradigm naming rules

- No `/` in paradigm names (creates phantom subdirectory)
- No `'` in paradigm names (breaks Python `-c` verification strings)
- Safe pattern: `[a-z0-9_]+`
