# Multi-Routine Architecture (2026-07-12)

User explicitly rejected cram-everything-into-one-timeline pattern. Standard PsychoPy Builder design: each phase gets its own routine.

## Correct Flow

```
instructions → [ fixation → trial → isi ] × N → thanks
```

## Routine Functions

- `_build_fixation_routine(spec)` — crosshair, auto-advance after ~500ms
- `_build_trial_routine(spec, conditions)` — stimulus + keyboard, no fixation/ISI inside
- `_build_isi_routine(spec)` — blank StaticComponent, auto-advance after ~300ms
- `_build_instructions_routine(spec)` — welcome text + SPACE to start
- `_build_thanks_routine(spec)` — thank you + any key to exit

## Anti-Patterns

- DO NOT cram fixation, stim, keyboard, ISI in one routine with overlapping timeline bars
- DO NOT hardcode ISI start at `stim_start + 3.0` — makes no sense for response-terminated trials
- DO NOT use StaticComponent as timeline overlay — ISI = its own routine
- DO NOT add features absent from the original paper (default timeout, etc.)
