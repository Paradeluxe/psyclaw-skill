# Norms appendix — marker field map (when writing)

Load at write time if unsure how norms land in JSON. Stub: `marker-stub.psyclaw`. Validate: `marker-validate.md`.

| Norm | Typical marker / design fields |
|------|--------------------------------|
| Design | `design_notes` / meta: factorial, assignment (within\|between\|mixed), factor list |
| IV | conditions columns; one per factor; rows = cells or continuum samples |
| DV | keyboard/slider/mouse store; **`corrAns`** if mapping known → `corr` + summary |
| Control | extra level or baseline routine |
| Random | loop `loopType` / nReps / nesting; between = group field outside within-loop |
| Practice | practice loop vs main; `pass_threshold` (default 0.60) + `max_redo` (default 1) |
| Script | instructions + thanks; optional `debrief_text` at run end only |
| Response | keyboard/slider; stopVal / force_end |
| Trial+Load | routine sequence; 24/cell default (practice 8–12); nReps×conditions; fix 500ms / ITI jitter; rest if long |
| Metrics | stimlist factors (`congruent`, `trialType`, …) + optional `metrics.group_by` (webui trial-metrics) |
| OutPath | project dir; marker `<folderName>.psyclaw` |
| **Seed** | optional root `seed` (int); absent → runner randomizes; set once for reproducibility |
| **Exclusion** | optional `exclusion_rules` (e.g. RT ±2.5 SD → flag; low accuracy → flag). Default **flag only**, drop in analysis not at run |

Compiler component types (typical): `text`, `keyboard`, `image`, `sound`/`audio`, `video`, `rect`, `slider`, `code`. Prefer types live webui accepts — see `webui-handoff.md`.
