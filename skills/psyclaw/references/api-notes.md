# WebUI API notes (agent)

Load only when calling webui, compiling, or debugging runs. User-facing prep → `run-prep.md`.

## Architecture

```text
<folderName>.psyclaw  (design JSON)
        │
        ▼
Flask 127.0.0.1:8876
  POST /api/runs { design, session, headless, project_path }
        │
        ▼
design_compiler → pure PsychoPy .py
        │
        ▼
PsychoPyProcess
  • runs/<id>/data/*.csv                 (internal)
  • <project_path>/data/{id}_s{sess}_{ts}.csv   (REQUIRED mirror)
```

- Repo: `Paradeluxe/psyclaw-webui` · port **8876** only (not 8787)
- Lab app is **not** a skill; companion skill is only `psyclaw`
- Open duration canonical: **`-1`**
- Platform > named paradigms
- Marker: **`<folderName>.psyclaw`** (webui migrates legacy `design.psyclaw`)

## Success checks

| Check | Pass means |
|-------|------------|
| **Marker ready** | compiler emits parseable Python with `Window` |
| **Run finished** | `/api/runs` → `finished` |
| **Data on disk** | CSV under **`<project_path>/data/`** |

## Run API (minimal)

```json
{
  "design": { },
  "headless": true,
  "project_path": "C:\\\\path\\\\to\\\\MyExp",
  "session": {
    "participant_id": "P_autopilot",
    "session": "1",
    "participant_name": "batch",
    "notes": "",
    "experimenter": "PsyClaw-AI"
  }
}
```

- Pilot: `participant_id: "P_pilot"` (no production ID burn)
- Formal: sequential IDs from `participants.json`
- Omit `project_path` → internal `runs/` only → **fails data-on-disk**

## CSV minimum

- Session: `participant_id`, `session`, `participant_name`, `notes`, `session_date`, `uid`
- Trial: `trial`, `routine`, `response`, `corrAns`, `corr`, `rt`, `keys` + stimlist cols
- Pack: `{stem}.csv` + `_summary.json` + `_by_condition.csv` + `_metrics_long.csv`
- Detail (webui): `trial-metrics.md`

## Design object

Prefer `marker-stub.psyclaw` as start. Shape: `name`, `display`, `devices`, `routines[]`, `flow[]` (routine | loop + conditions + children).

Types (typical): `text`, `keyboard`, `image`, `sound`/`audio`, `video`, `rect`, `slider`, `code`. Prefer live compiler accepts.

### Classic metrics (optional)

```json
"metrics": { "group_by": ["congruent"] }
```

Stimlist carries factors (`congruent`, `trialType`, …) + `corrAns` when scoring. No paradigm-named compiler forks.

## Pitfalls

1. Marker ready ≠ lab delivery  
2. Missing `project_path` → empty project data folder  
3. Port **8876** only  
4. Do not emit `.psyexp` as skill deliverable  
5. Skill never freestyle-upgrades PsychoPy
