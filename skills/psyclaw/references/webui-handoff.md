# WebUI handoff — compile / run / CSV (canonical)

Skill writes **`<folderName>.psyclaw`**. Once the marker is ready the agent **asks** 要跑被试吗 (do not only wait for 能跑吗). If yes, lab software **psyclaw-webui** opens the project, runs subjects **in order**, mirrors CSV.

**Multi-subject:** sequential Start runs; auto participant ID + UID; formal finished → next ID. No separate batch product.

**Agent-driven session:** set `session.experimenter` to the AI agent identity (e.g. `PsyClaw-AI`). Pilot = `P_pilot` (does not consume production IDs).

**Out of scope:** half-run / play-only-N-trials lab mode (Builder component PREVIEW ≠ participant run).

## Architecture

```
<folderName>.psyclaw  (design JSON; same schema as design object)
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

- Repo: `Paradeluxe/psyclaw-webui` · port **8876** only
- SPA skill: **`psyclaw-webui`**
- Open duration canonical: **`-1`**
- Platform > named paradigms (no Stroop-hardcoded SPA fields)
- Marker name: **`<folderName>.psyclaw`** (not fixed `design.psyclaw`; webui migrates legacy)

## Success checks

| Check | Pass means |
|-------|------------|
| **Marker ready** | `design_compiler` emits parseable Python with `Window` |
| **Run finished** | `/api/runs` → status `finished` |
| **Data on disk** | CSV under **`<project_path>/data/`** |

Skill alone → marker ready. Run finished + data on disk need webui + PsychoPy.

### CSV minimum columns

- Session: `participant_id`, `session`, `participant_name`, `notes`, `session_date`, `uid`
- Trial: `trial`, `routine`, `response`, `corrAns`, `corr` (0/1/""), `rt`, `keys` + stimlist cols
- Pack: `{stem}.csv` (long trials) + `_summary.json` + `_by_condition.csv` + `_metrics_long.csv`
- Instrument: accuracy / mean RT / hit·FA when Go-NoGo
- Detail (webui repo): `references/trial-metrics.md`

Compile-only ≠ success. Finished without project-mirrored CSV ≠ desktop-parity success.

### Classic metrics (when Method has precedent)

When writing from classic literature, put **paper factors on the stimlist** and optional:

```json
"metrics": { "group_by": ["congruent"] }
```

| Example | Stimlist | metrics.group_by |
|---------|----------|------------------|
| Stroop | `congruent` yes/no + `corrAns` | `["congruent"]` |
| Flanker | `congruency` + `corrAns` | `["congruency"]` |
| Go/NoGo | `trialType` go/nogo (+ go has `corrAns`) | `["trialType"]` |

Generic scoring only — no paradigm-named compiler branches.

## design object (agent-generatable)

```json
{
  "name": "example_flanker",
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

Compiler component types (typical): `text`, `keyboard`, `image`, `sound`/`audio`, `video`, `rect`, `slider`, `code`. Prefer types the live webui compiler accepts — check webui if unsure.

## Run API (minimal)

```json
{
  "design": { "...": "same object as marker JSON" },
  "headless": true,
  "project_path": "C:\\\\path\\\\to\\\\MyExp",
  "session": {
    "participant_id": "P_autopilot",
    "session": "1",
    "participant_name": "batch",
    "notes": ""
  }
}
```

- Pilot: `participant_id: "P_pilot"` (does not consume production IDs)
- Formal: sequential IDs from project `participants.json`
- Omit `project_path` → only internal `runs/` CSV (fails **data on disk**)

## Pitfalls

1. Marker ready ≠ full lab delivery — need **run finished** + **data on disk**.
2. Missing `project_path` — Open folder looks empty.
3. Port **8876** only (not Mentor 8787).
4. Do not emit Builder `.psyexp` as the skill deliverable.

## Related

- Skill: `psyclaw-webui` — SPA IA, System/Run layout
- Skill pipeline: `skill-pipeline.md`
