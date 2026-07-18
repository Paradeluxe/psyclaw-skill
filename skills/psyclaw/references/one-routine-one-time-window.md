# One-routine-one-time-window rule

## The rule

A `<Routine>` in a `.psyexp` must contain only components whose
on-screen windows overlap.

For two components A and B in the same routine, they **overlap** when:

```
A.start < B.end  AND  B.start < A.end
```

(`<` is strict — touching at the boundary is *not* overlap; put
back-to-back components in separate routines.)

A component with no explicit `duration` or `duration_ms` (or
`duration: null` in the spec) is treated as **unbounded**: its window
extends to `+inf`, so it overlaps with everything else in the routine.

## Why the rule exists

PsychoPy's per-frame `while continueRoutine` loop checks "every
component finished?" and only exits when **all** components in the
routine are FINISHED. A non-overlapping component that finishes early
sits FINISHED while the others are still STARTED, but the finished
one can never set `continueRoutine = False` — that only happens on a
key press / stimulus offset.

In the headless runner, this means a routine with a fixation (0–0.5s)
and a trial text (0.5s+, unbounded) in the *same* routine will hit the
60-frame watchdog cap (4s @ 30fps) and force-end. The end result
is the same as a hang, just with a hard timeout.

## Examples

| Routine  | Components                           | Valid? |
|----------|--------------------------------------|--------|
| `fix`    | `fix_text` 0–0.5s                   | yes |
| `stim`   | `cue_text` 0–0.2s                    | yes |
| `trial`  | `fix_text` 0–0.5s, `trial_text` 0.5s+, `key` 0.5s+ | no (fix and trial_text are back-to-back) |
| `trial`  | `trial_text` 0s+, `key` 0s+          | yes (both unbounded) |
| `iti`    | `blank_text` 0–0.5s                 | yes |

## Enforcement in `builder.py`

Three layers, in increasing specificity:

### 1. Spec-driven routines

`_build_spec_driven_routines` validates every `routines:` entry
in `spec.yaml` before emitting any XML. Collects all warnings, prints
them to stderr, and raises `ValueError` on any violation. The spec
author sees every problem at once rather than playing whack-a-mole.

```python
all_warnings = []
for r in routines_in:
    all_warnings.extend(_validate_routine_overlap(r, strict=True))
for w in all_warnings:
    print(f"  [builder] {w}", file=sys.stderr)
if all_warnings:
    bad = [r.get("name", "?") for r in routines_in
           if _validate_routine_overlap(r, strict=False)]
    raise ValueError(
        "spec.yaml violates the one-routine-one-time-window rule "
        f"(components with non-overlapping time windows in: {bad}). "
        "Move the offending components into their own routines."
    )
```

### 2. Paradigm-specific builders (Sternberg, Task Switching)

Each paradigm builder first runs `_validate_routines_against_overlap_rule`
against a description of its intended routine design, then emits the
XML. The description is a list of `{name, components: [...]}` dicts
in the same shape as a spec-driven entry.

```python
def _build_sternberg_routines(spec):
    _validate_routines_against_overlap_rule(
        spec, _build_sternberg_routines.__name__,
        _sternberg_routine_specs(spec),
    )
    # ... build routines ...
```

### 3. Standard 3-routine structure (fixation + trial + isi)

`_check_standard_routine_overlap` is a guard rail that converts the
builder-emitted `<Routine>` element back into a validator spec dict
and runs the check. The standard structure is overlap-clean by
construction (single component per routine, or unbounded stim +
keyboard with `1e-6` max_wait). If a future edit accidentally
introduces a non-overlapping pair, this fails fast.

### 4. Multi-block path

The multi-block path runs both `_check_standard_routine_overlap` (for
paradigms using the standard structure) and the spec-driven path
(for paradigms with `routines:` overrides per block).

## API

```python
from builder import (
    _compute_time_window,                         # (start, end) tuple
    _validate_routine_overlap,                  # list[str] warnings
    _validate_routines_against_overlap_rule,    # raises ValueError
)
```

## Sternberg and Task-Switching refactor

Both paradigm generators were refactored to comply with the rule:

- **Sternberg**: was 2 routines (`encode`, `probe`), now 5 (`encode_fix`,
  `encode_stim`, `probe_fix`, `probe_trial`, `iti`; 4 if `iti_ms=0`).
  The fixation+stim back-to-back and ISI-after-keyboard back-to-back
  were each split into their own routines.
- **Task Switching**: was 2 routines (`cue`, `trial`), now 5
  (`cue_fix`, `cue_disp`, `trial_fix`, `trial`, `iti`; 4 if `iti_ms=0`).
  Same fix pattern.

The old design had ISI as a `<StaticComponent>` inside the trial
routine with `start_time = trial_start + 3.0`. With the keyboard's
finite `max_wait`, the ISI's `[3, 3+iti)` window did not overlap the
keyboard's `[0, max_wait)` window — a violation. The refactor moves
ISI to its own routine back-to-back with the trial routine.

## Test coverage

`tests/test_builder_overlap.py` covers:

- `_compute_time_window` for `duration` in seconds, `duration_ms` in ms,
  unbounded (`None` or missing), and zero duration (treated as unbounded
  for safety).
- `_validate_routine_overlap` for back-to-back, touching-at-boundary,
  unbounded-overlapping-everything, key-ISI-don't-overlap, and
  single-component routines.
- `_validate_routines_against_overlap_rule` for both pass and raise
  paths.
- End-to-end `_build_sternberg_routines` (verifies routine count
  = 5 + instructions + thanks) and bad spec rejection (verifies
  `ValueError` on a deliberately violating spec).

18/18 tests passing as of 2026-07-12.

## When NOT to apply the rule

A few cases that look like violations but are not:

- **Unbounded components** (`duration: null`) overlap with everything
  because their end is `+inf`. A routine with two unbounded components
  is fine.
- **Touching at the boundary** (component A ends exactly when
  component B starts) is **not** overlap. This is a common mistake —
  people think "they share a moment in time" but they don't. Use
  separate routines for back-to-back components.
- **`1e-6` max_wait** on a KeyboardComponent is treated as a finite
  duration of 0.001 seconds. With an unbounded text stimulus, the
  keyboard's `[0, 0.001)` window is technically non-overlapping with
  the stim's `[0, +inf)` only if you read 0.001 strictly, but the
  actual overlap check uses `start < end` which evaluates to `0 < 0.001`
  and `0 < +inf`, both true. So this combination passes.
- **Routine-level stopVal** set via `_build_spec_driven_routines`'s
  `duration` field. This is the routine's own auto-exit, not a
  component window. It's not part of the per-component overlap
  check.

## Future work

Apply the same validation to stroop/simon/flanker/posner/nback when
their spec files are migrated to the `routines:` format. Currently
they use the legacy `timeline:` format and skip the validation.

The `_check_standard_routine_overlap` helper could be extended to
also check the loop structure: every `<LoopInitiator>` and
`<LoopTerminator>` must reference a real routine, and the loop's
`endPoints` must lie within the routines it wraps. This is currently
caught by `validate_psyexp.py` layer 4, but adding it as a builder-side
check would catch it earlier.
