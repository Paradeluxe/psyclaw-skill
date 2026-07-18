# Builder design principles (v3.7, 2026-07-13)

The two overlap rules every `.psyexp` routine must satisfy, plus the
class-level architecture for the new paradigm builders. Read this
when adding a new paradigm builder, when designing a complex spec,
or when a validator trips with an error you don't recognize.

## The two overlap rules

The product rule design rule ("一个 routine 里只放同时重复出现的
component / 只要时间上有 overlap，才可以放入同一个 routine") is
**two rules**, not one — and the second one was missed in v3.6.

### Rule 1 — time-window overlap (rule #50)

A `<Routine>` may only contain components whose on-screen windows
overlap (in `[start_time, start_time + duration)`). Non-overlapping
components in the same routine cause the headless runner to hang:
PsychoPy's per-frame "every component finished?" loop only exits when
**all** components in the routine are FINISHED; a non-overlapping
component that finishes early sits FINISHED while others are still
STARTED but cannot set `continueRoutine = False`.

Formula (strict, touching at boundary counts as non-overlap):

```
A.start < B.end  AND  B.start < A.end
```

Components with no `duration` / `duration_ms` are treated as
**unbounded** (`end = +inf`) and overlap with everything else.

### Rule 2 — visual layout overlap (rule #53, added 2026-07-13 after
the user called out v3.6 as "不符合原著")

Two routine components at the same on-screen position render
illegible text-on-text. Builder enforces this with bbox estimation:

| Component | Bbox (x_min, x_max, y_min, y_max) |
|-----------|-----------------------------------|
| text      | `(text_width/2, h, 0, 0) + pos`, where `text_width = len(text) × 0.5 × height` |
| slider    | `(pos_x - w/2, pos_y - h/2 - 0.025)` to `(pos_x + w/2, pos_y + h/2 + 0.025)` (default `pos=(0, -0.1)`, `size=(1.0, 0.1)`) |
| rect      | `(pos_x - w/2, pos_y - h/2)` to `(pos_x + w/2, pos_y + h/2)` |
| image     | not yet estimated (specs typically don't set `size`) |

Tick labels above and below the slider are projected by `0.025 +
h/2` so that text labels at `y=0` are flagged when the slider is at
`(0, -0.1)` — this was the exact kfs/artpics spec bug.

**When designing rating-scale specs**: the slider bar should be at a
y that does NOT intersect text labels at the same x. The
slider-tick-label projection is roughly `±(h/2 + 0.025)` vertically.
Move text labels either above (y > 0.10) or well below (y < -0.15),
never at the same y as the slider.

## Validator API (`builder.py`)

| Helper | Purpose |
|--------|---------|
| `_compute_time_window(comp)` / `_component_time_window` | alias: `(start, end)` seconds per spec |
| `_validate_routine_time_overlap(routine)` | list of warnings; rules out back-to-back windows |
| `_validate_routine_visual_overlap(routine)` | list of warnings; rules out screen-space overlap |
| `_validate_routines_against_overlap_rule(spec, name, routines)` | raises ValueError on any violation |
| `_estimate_text_bbox(comp)` | text bbox |
| `_slider_bbox(comp)` / `_rect_bbox(comp)` | non-text component bboxes |
| `_bbox_overlap(a, b)` | standard 2D closed-interval box test |
| `_normalize_pos(pos)` | coerce spec `pos` (list/tuple/str) to PsychoPy `"(x, y)"` form |

Naming back-compat: `_compute_time_window`, `_validate_routine_overlap`
(routes to time-overlap only).

## How `builder.py` enforces both rules

Three enforcement layers:

1. **Spec-driven routines** (`routines:` list in spec.yaml) — every
   entry's components are validated for BOTH time-window and
   visual-layout overlap before XML is emitted. Violations raise
   `ValueError` naming the bad routine(s) and rule.

2. **Sternberg / task-switching paradigm builders** — emits 5 routines
   (`encode_fix`, `encode_stim`, `probe_fix`, `probe_trial`, `iti`;
   4 if `iti_ms=0`). Validated via `_sternberg_routine_specs` /
   `_taskswitch_routine_specs` + `_validate_routines_against_overlap_rule`.

3. **Standard three-routine fallback**
   (`fixation`/`trial`/`isi`) — guard-rail via
   `_check_standard_routine_overlap`. Single-component routines
   skip this check.

## Example: the kfs/artpics fix (2026-07-13)

Before:
```yaml
- type: text
  text: "1 = Not pleasant"
  pos: [-0.15, 0.0]   # y=0
- type: slider
  ticks: [1..7]
  # no pos/size set  → defaults to pos=(0, -0.1), size=(1.0, 0.1)
```
Validator output: `routine 'rate_valence': components 'text_1' and
'slider_3' have overlapping on-screen bboxes (text_1=(-0.25..-0.05,
-0.025..0.0); slider_3=(-0.52..0.52, -0.175..-0.025))` — moves slider
below labels.

After:
```yaml
- type: slider
  pos: [0, -0.3]      # clear of text at y=0
  size: [0.7, 0.05]   # smaller, doesn't run to full screen edges
```
`6/6` build OK. Validator silent (no overlap).

## Validation failure examples

| Bad design | Detector output |
|------------|------------------|
| `fix: 0-0.5s` + `stim: 0.5s+` in same routine | `_validate_routine_time_overlap`: "components 'fix' [0.000-0.500s] and 'stim' [0.500-2.000s] have non-overlapping windows" |
| 2× text at same `pos: [-0.2, 0.0]` | `_validate_routine_visual_overlap`: "components 'text_0' and 'text_1' have overlapping on-screen bboxes" |
| Text at `y=0` + slider default `pos=(0,-0.1)` | `_validate_routine_visual_overlap`: "components 'X' (y=-0.025..0.000) and 'slider_Y' (y=-0.175..-0.025) have overlapping" (when bbox projection matches) |

## Helper additions that landed with rule 2

Adding rule 2 required three new helpers in `builder.py`:

1. `_estimate_text_bbox(comp)` — `[x_min, x_max, y_min, y_max]`
   from `pos` + `height` + `len(text) × 0.5 × height`
2. `_slider_bbox(comp)` — same, with tick-label projection
3. `_rect_bbox(comp)` — same, for `type: rect`
4. `_bbox_overlap(a, b)` — standard 2D closed-interval box test
5. `_normalize_pos(pos)` — coerce spec `pos` (list/tuple/str) into
   PsychoPy-native `"(x, y)"` form. Without this, the spec_driven
   text emit path was silently dropping `pos`, which is why the
   first validator run looked bizarre — every text was rendering at
   `(0, 0)` regardless of spec.

Plus a new `_slider_component(name, ticks, ...)` in the emit layer
(previously rating-scale paradigms emitted nothing for sliders).

## Test catalog (`tests/test_builder_overlap.py`, 27/27)

| Test | Asserts |
|------|---------|
| `test_window_with_duration` | `(start, duration)` → `(s, s + duration)` |
| `test_window_with_duration_ms` | `start_time` + `duration_ms` |
| `test_window_unbounded` | no duration → `+inf` end |
| `test_window_no_duration_field` | same |
| `test_window_zero_duration_treated_as_unbounded` | `duration=0` → `+inf` (safer failure mode) |
| `test_overlap_no_warnings_for_overlapping_comps` | strict overlap, both bounded |
| `test_overlap_warning_for_back_to_back` | back-to-back triggers warning |
| `test_overlap_unbounded_overlaps_everything` | unbounded component overlaps with anything |
| `test_overlap_key_and_isi_dont_overlap` | ISI after max_wait fires |
| `test_overlap_single_component` | no check for 1-comp routines |
| `test_overlap_touching_at_boundary_is_violation` | touching = violation |
| `test_rule_passes_for_overlapping_routines` | top-level happy path |
| `test_rule_raises_for_violating_routines` | raises ValueError |
| `test_sternberg_routine_specs_overlap_clean` | refactored 5 routines pass |
| `test_sternberg_no_iti_overlap_clean` | iti_ms=0 case: 4 routines |
| `test_taskswitch_routine_specs_overlap_clean` | refactored 5 routines |
| `test_build_sternberg_yields_routine_count` | end-to-end XML has 7 routines |
| `test_build_rejects_spec_with_violating_routines` | end-to-end ValueError |
| `test_select_routine_chain_*` (3 tests) | `_select_routine_chain` helper |
| `test_build_loop_from_spec_basic` | `_build_loop_from_spec` helper |
| `test_build_preserves_conditions_xlsx_when_spec_names_it_so` | pitfall #56 stale-cleanup guard |
| `test_build_spec_driven_multi_loop` | end-to-end 2-loop spec |
| `test_visual_overlap_two_texts_in_same_place` | rule 2 fires |
| `test_visual_overlap_text_and_slider_at_default` | rule 2 catches kfs bug |
| `test_visual_passes_when_texts_dont_overlap` | rule 2 negative case |

## Adding a new paradigm builder (checklist)

1. Define a `<paradigm>_routine_specs(spec) -> list[dict]` that returns
   the in-memory routine design in the same shape as a spec-driven
   `routines:` entry (each dict has `name`, `components: [{name, ...}]`).
2. Add `_validate_routines_against_overlap_rule(spec, builder_name,
   _routine_specs(spec))` at the top of the new `_build_*_routines`.
   This runs **both** time-window AND visual-layout checks.
3. Make sure back-to-back time windows land in different routine dicts.
4. If the routine contains visual components, design the layout so
   `pos` + `height` give non-overlapping bboxes (validator will catch
   any violation at build time).
5. Add the spec to `tests/test_builder_overlap.py`.

## Multi-loop specs (`Stroop` style)

A spec may declare multiple `loops:` entries (e.g. Stroop neutral +
incongruent). The builder honours them by emitting one
`<LoopInitiator>` per entry, each with its own `nReps`, `order`,
`spreadsheet.file`, and `start_routine`/`end_routine` chain. Helpers:

- `_select_routine_chain(routines, start_name, end_name)` — slices
  the routine list by start/end name (inclusive).
- `_build_loop_from_spec(name, lp, chain)` — builds the
  `<LoopInitiator>` element.
- `_write_loop_xlsx(out_dir, lp)` — writes the per-loop rows to
  the loop's named xlsx (e.g. `neutral_conditions.xlsx`).

When `loops[].spreadsheet.rows` is set, that loop's trial data is
written to its own `*_conditions.xlsx` (file name from
`spreadsheet.file`). The paradigm-specific `_gen_*_conditions` is
**skipped** for that loop — the trial list is fully specified in YAML.

Validation applies the overlap rule **per loop, not globally**: a
routine in loop A can share a time window with components in loop B
because each loop is a separate, sequential flow step.

## Why these rules matter in practice

- **Time-window rule** (R1): prevents the headless runner from
  hanging at a routine with non-overlapping component windows. The
  watchdog force-ends at 120 frames (4s @ 30fps), which is what
  caused the original IAT pilot to repeatedly hit the watchdog cap.
- **Visual layout rule** (R2): prevents generating `.psyexp` files
  where texts render on top of each other (illegible), sliders
  overlap text labels (visual mess), or ratings-scale specs look
  broken because the prompt and the rating widget are at the same
  coordinates. Caught the kfs/artpics stale-spec bugs.

Together they produce a `.psyexp` that:
- Has well-separated routines (per R1)
- Renders legibly inside each routine (per R2)
- Loads with 0 warnings in PsychoPy (per the loadFromXML gate)
- Runs end-to-end without hanging (per the runtime smoke test)
