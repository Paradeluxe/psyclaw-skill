# Path C — psyclaw-webui (canonical GUI + pure-Python runner)

**Status (2026-07-18, publication-facing):** product path, not scaffold.

## Architecture

```
Builder SPA (design.json / design.psyexp marker file)
        │
        ▼
Flask 127.0.0.1:8876
  POST /api/runs { design, session, headless, project_path }
        │
        ▼
design_compiler.compile_any → pure PsychoPy .py
        │
        ▼
PsychoPyProcess (D:\Software\P\python.exe)
  • runs/<id>/data/*.csv                 (internal harvest)
  • <project_path>/data/{id}_s{sess}_{ts}.csv   (REQUIRED mirror)
```

- Repo: `E:\hermes_playground\psyclaw-webui` · GitHub `Paradeluxe/psyclaw-webui`
- Port **8876** only (never 8765 / Mentor)
- SPA contract skill: **`psyclaw-webui`** (Builder / System / Run / Settings / Guide)
- Open duration canonical value: **`-1`**
- Platform > named paradigms: no hardcoding Stroop field sets in the SPA

## Success criteria (paper gate)

| Gate | Pass means |
|------|------------|
| G0 Compile | `design_compiler.compile_design` emits parseable Python with `Window` |
| G1 Run | `/api/runs` → status `finished` (headless/autopilot or participant) |
| G2 Data retention | CSV under **`<project_path>/data/`** with: |

Required CSV columns (minimum):
- Session: `participant_id`, `session`, `participant_name`, `notes`, `session_date`
- Trial: `trial`, `routine`, `response`, `rt`, `keys`
- Condition columns from stimlist (e.g. `word`, `color`, `corrAns`, or paradigm-specific)

**Compile-only is not success.** "Run finished" without project-mirrored CSV is not success.

## design.json (agent-generatable)

```json
{
  "name": "cat1_flanker",
  "display": { "size": [1024, 768], "fullscreen": false, "screen": 0, "bgcolor": "#000000" },
  "devices": { "keyboard": true },
  "routines": [
    {
      "name": "instructions",
      "components": [
        { "id": "c1", "type": "text", "name": "instr", "start": 0, "duration": -1,
          "params": { "text": "Press SPACE", "color": "white" } },
        { "id": "c2", "type": "keyboard", "name": "kb", "start": 0, "duration": -1,
          "params": { "keys": "space", "force_end": true } }
      ]
    },
    {
      "name": "trial",
      "components": [
        { "id": "c3", "type": "text", "name": "stim", "start": 0, "duration": 2.0,
          "params": { "text": "$target", "color": "white" } },
        { "id": "c4", "type": "keyboard", "name": "resp", "start": 0, "duration": 2.0,
          "params": { "keys": "left,right", "force_end": true } }
      ]
    },
    {
      "name": "thanks",
      "components": [
        { "id": "c5", "type": "text", "name": "bye", "start": 0, "duration": -1,
          "params": { "text": "Thanks", "color": "white" } },
        { "id": "c6", "type": "keyboard", "name": "end", "start": 0, "duration": -1,
          "params": { "keys": "space", "force_end": true } }
      ]
    }
  ],
  "flow": [
    { "kind": "routine", "routine": "instructions" },
    {
      "kind": "loop", "name": "trials", "nReps": 1, "loopType": "random",
      "conditions": [{ "target": "<<", "corrAns": "left" }],
      "children": [{ "kind": "routine", "routine": "trial" }]
    },
    { "kind": "routine", "routine": "thanks" }
  ]
}
```

Component types used in compiler path: `text`, `keyboard`, `image`, `sound`/`audio`, `video`, `rect`, `code`.

## Paper library bridge (50+50+50)

| Category | Papers on disk | Built replications (`spec.yaml`) | Notes |
|----------|----------------|----------------------------------|-------|
| 1 Pure PsychoPy | 50 | **50** (`cat1_*`) | text/shapes/keys only |
| 2 Downloadable materials | 50 | **50** (`cat2_*`) | +3 scaffolded 2026-07-18 for pipeline completeness |
| 3 Manual materials | 50 | **50** (`cat3_*`) | framework OK; stimuli user-supplied |

PDFs: `E:\hermes_playground\psyclaw\papers\category{1,2,3}\`
Replications: `E:\hermes_playground\psyclaw\replications\cat{1,2,3}_*`

### Conversion + batch scripts

| Script | Role |
|--------|------|
| `scripts/spec_to_design_batch.py` | `spec.yaml` → `design.psyexp` + compile G0 for all cat* |
| `scripts/headless_webui_sample.py` | stratified POST /api/runs headless G1 |
| `scripts/data_retention_audit.py` | G2 project CSV column/path audit |

Skill copy of converter: `~/.hermes/skills/research/psyclaw/scripts/spec_to_design_batch.py`
Workspace copies: `E:\hermes_playground\psyclaw\scripts\`

### Benchmark results (2026-07-18)

**Full battery (paper gate):** evidence `E:\hermes_playground\psyclaw\output\webui_batch_validate_150\`

| Gate | N | Result | Artifact |
|------|---|--------|----------|
| G0 design_compiler | **150** | **150/150 ok** | run log + per-folder `design.psyexp` |
| G1 headless full | **150** | **150/150 finished** | `g1g2_state.json` |
| G2 data retention full | **150** | **150/150 pass** | project `data/*.csv` + `FINAL_SUMMARY.json` |

Pass-by-cat: cat1 **50/50**, cat2 **50/50**, cat3 **50/50**. `fail_n: 0`.

Script: `scripts/full150_webui_validate.py` (resumable).

Each pass = run `finished` **and** CSV under `replications/<slug>/data/` with session cols + `response`/`rt` + condition cols.

Earlier stratified smoke (15/15) remains under `output/webui_batch_validate/` as warm-up.

## Run API (minimal)

```json
{
  "design": { "...": "design.json object" },
  "headless": true,
  "project_path": "E:\\\\hermes_playground\\\\psyclaw\\\\replications\\\\cat1_flanker",
  "session": {
    "participant_id": "P_autopilot",
    "session": "1",
    "participant_name": "batch_validate",
    "notes": "publication validation sample"
  }
}
```

- Pilot live keys: `participant_id: "P_pilot"` (does not consume production IDs)
- Formal: sequential IDs from project `participants.json`
- `project_path` omitted → only internal `runs/` CSV (fails G2 for desktop-parity claims)

## Pitfalls specific to Path C paper claims

1. **G0 ≠ shippable** — always G1+G2.
2. **Missing `project_path`** — Instrument may show internal path; Open folder looks empty.
3. **Legacy yaml-form docs** — `/api/paradigms` form SPA is superseded; design.json is primary.
4. **cat2 count honesty** — 47 replications built as of 2026-07-18.
5. **Headless caps** — sample scripts slice conditions ≤2 and nReps=1 for speed; full nReps is separate full-battery work.
6. **Port collision** — 8876 only.

## Related skill files

- `psyclaw-webui` skill — full SPA IA, pitfalls, System/Run layout
- `references/paper-library-classification.md` — 50+50+50 definition
- `references/batch-spec-testing.md` — Path B loadFromXML era (historical 50/50 cat1)
- `references/psychopy-platform-pitfalls.md` — why Path C skips .psyexp runtime
