# Frame recorder — per-frame state dump for runner debugging (2026-07-13)

When the user asks "我想要知道每一帧发生了什么" / "这一帧里发生了
什么" — they want to **see what's actually on screen** during a headless
run. This is a debugging/inspection tool that watches what the
participant saw, frame by frame.

The visible behaviour: text content, component status (NOT_STARTED /
STARTED / FINISHED), screen position, what loop iteration is active,
all saved as one JSON file per visual flip under `data/frames/`. The
companion viewer (`scripts/frames_viz.py`) renders an ASCII timeline
or a matplotlib PNG so you can see the experiment at a glance.

## How to use

### Step 1 — Run with the recorder on

```bash
PYTHONPATH= PYTHONHOME= <psychopy-python> \
    <psyclaw-workspace>/scripts/run_psyexp.py \
    <psyclaw-workspace>/replications/my_paradigm/my_paradigm.psyexp \
    --timeout 60
PSYCLAW_FRAME_LOG=1 \
PSYCLAW_FRAME_DIR=<psyclaw-workspace>/replications/my_paradigm/data/frames \
PSYCLAW_FRAME_KEEP=500 \
```

Three env vars control the recorder:

| Var | Default | Purpose |
|-----|---------|---------|
| `PSYCLAW_FRAME_LOG` | `0` | `1` to enable (no effect if unset) |
| `PSYCLAW_FRAME_DIR` | `<cwd>/data/frames` | Output directory |
| `PSYCLAW_FRAME_KEEP` | `200` | cull oldest frames beyond this; `0` to disable culling |

Files are ~1 KB each and named `frame_<ms_timestamp:013d>.json`. The 13-digit
zero-pad timestamp keeps lexicographic order matching write order.

### Step 2 — View the timeline

ASCII (terminal-friendly, default):

```bash
python <psyclaw-workspace>/scripts/frames_viz.py \
    <psyclaw-workspace>/replications/my_paradigm/data/frames
```

Output looks like:

```
frames: 47  first_ms=1700000123456  last_ms=1700000167890

  routine: trial
    trial_text_0  |   .   .   .   .   .   .   # # # # # # # # # # x x x x x x x|  '$stim_text: pure'
    trial_keyboard_1  |   .   .   .   .   .   .   . . . . . . . . . . . . . .|  '$correct_key'
```

`#` = STARTED, `x` = FINISHED, `.` = NOT_STARTED, ` ` = component not in
that routine's view (or the routine's frame interval was zero).

PNG (matplotlib, color-coded):

```bash
python <psyclaw-workspace>/scripts/frames_viz.py \
    <psyclaw-workspace>/replications/my_paradigm/data/frames \
    --png out.png
```

Inspect a single frame's full JSON (useful when a specific frame looks
suspicious in the ASCII timeline):

```bash
python <psyclaw-workspace>/scripts/frames_viz.py \
    <psyclaw-workspace>/replications/my_paradigm/data/frames \
    --frame 23
```

## How it works (implementation recipe)

The recorder monkey-patches `psychopy.visual.Window.flip()`. On every
visual refresh (Pyglet's flip), a hook executes that:

1. Walks `gc.get_objects()` to find every active `Routine`.
2. Per routine, dumps each component's status, name, type, text,
   rating, pos, size.
3. Per routine, dumps the trial-loop pointers (`thisN` /
   `thisTrialN` / `thisRepN`) if present.
4. Serializes to JSON, writes to disk, culls oldest frames.

```python
def _record_frame(self, *a, **kw):
    active_routines = []
    for obj in gc.get_objects():
        if type(obj).__name__ == "Routine":   # avoid isinstance lazy-import
            try:
                if obj.status not in (None, "FINISHED"):
                    active_routines.append(obj)
            except Exception:
                continue
    # ... build snapshot, write to disk ...
    return _orig_flip(self, *a, **kw)
_visual.Window.flip = _record_frame
```

### Two important details

**Use `type(obj).__name__ == "Routine"` instead of `isinstance(obj, Routine)`**.
`isinstance()` triggers `psychopy.data.Routine` to be loaded into
the module's namespace, which can pull in `psychopy.app` (a wxPython
module). That's catastrophic in a headless runner — wxPython init
tries to attach to the Windows GUI and either segfaults or refuses
to load. `type(obj).__name__` is a string check, no import.

**The recorder lives in the patch block, not at module scope.** If
the recorder function is defined at module scope of `run_psyexp.py`
but the runner is exec'd via `runpy.run_path`, the recorder
function is NOT in the runner's namespace — the runner has its
own fresh module globals, and the call never fires. Put the
recorder function **definition and call** both inside the
`_PATCH_BLOCK` triple-quoted string, which gets injected verbatim
into the runner file.

## What good looks like for a routine

A routine's frames should look like:

| Frame | text_0 | key_1 |
|-------|--------|-------|
| 0     | .      | .     |
| 1     | #      | #     |
| 2     | #      | #     |
| ...   | #      | #     |
| 30    | x      | x     |   <-- routine ended, force-ended or keypress

If you see `.` (NOT_STARTED) for many frames in a row, the component
isn't getting `setAutoDraw(True)` — likely a bad `startType`/`startVal`
configuration. If you see `#` (STARTED) forever and the watchdog
force-ends the routine, see pitfall #49 in `add-paradigm/SKILL.md`.

## Status code reference

PsychoPy 2026.1.1 routine.status values:
- `None` -- never started (a routine not yet entered)
- `NOT_STARTED` -- entered but `tStart` is in the future
- `STARTED` / `PLAYING` -- actively running
- `FINISHED` -- exited cleanly
- `STOPPED` / `STOPPING` / `PAUSED` -- explicit pause
- `FORCED` -- watchdog force-end

The recorder treats `None` and `FINISHED` as "not currently on screen"
and silently skips them in the per-frame snapshot.

## Pseudocode shape

For each JSON file:

```json
{
  "frame_id": 1700000123456,
  "routines": [
    {
      "name": "trial",
      "frame_index": 23,
      "forceEnded": false,
      "thisN": 5,
      "thisTrialN": 5,
      "thisRepN": 0,
      "components": [
        {"name": "trial_text_0", "type": "TextComponent",
         "status": "STARTED", "text": "RED",
         "pos": [0, 0], "size": null},
        {"name": "trial_keyboard_1", "type": "KeyboardComponent",
         "status": "STARTED"}
      ]
    }
  ]
}
```

For multi-routine frames (e.g. instructions + trial nested), `routines`
is a list, not a dict. Check `len(routines)` first.

## Limitations

- **Slider bboxes not in the JSON.** Only the slider's `pos`, `size`,
  and current `rating` are captured. Use `frames_viz --frame N` to
  see what's in the frame, but the slider's internal tick geometry
  is not reconstructable from this alone.
- **Image stimuli don't carry full filepath.** Image components
  have a `path` attribute but the recorder skips it to keep files
  small. If you need to debug image stimuli, grep the spec or look
  at the .psyexp XML directly.
- **No component-level screenshots.** The recorder sees the
  *renderer state* but doesn't write a screenshot -- `Window
  .getMovieFrame()` is the right tool for that (slow).
- **Culled frames are gone.** `PSYCLAW_FRAME_KEEP=200` is the safety
  budget. Raise it for long runs.
