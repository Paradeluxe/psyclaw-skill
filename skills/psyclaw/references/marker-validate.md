# Marker validate (after every write/edit)

Run **in order**. Soft checks may warn; hard fails block “marker ready”.

## Hard fail (must pass)

| # | Check | Pass means |
|---|--------|------------|
| 1 | **File** | `<projectDir>/<folderName>.psyclaw` exists; `folderName` = basename of `projectDir` |
| 2 | **JSON** | File parses as a single JSON object (UTF-8) |
| 3 | **Shape** | Top-level has non-empty `routines` (array) and `flow` (array) |
| 4 | **Routine refs** | Every `flow` node with `"kind":"routine"` names a routine that exists in `routines[].name` |
| 5 | **Loop kids** | Every `"kind":"loop"` has non-empty `children` and `nReps` ≥ 1 |
| 6 | **Trial skeleton** | At least one routine used in a loop has a stimulus-like component (`text`/`image`/…) **and** a response component (`keyboard`/`slider`/…), unless user waived response |
| 7 | **No parallel schema** | No Builder `.psyexp` as deliverable; no invented top-level keys that replace `routines`/`flow` |

## Soft warn (fix once, still may ask-run)

| # | Check | If missing |
|---|--------|------------|
| A | `name` | Set to `folderName` |
| B | `display` | Default window ok for lab; webui may fill |
| C | `devices` | Prefer explicit keyboard/mouse if used |
| D | conditions / stim columns | Factors + `corrAns` when scoring expected |
| E | practice vs main | Separate loops if practice was agreed |
| F | `design_notes` | design tag + path + lit citation + deviations |

## Optional deep gate (when webui is up)

| # | Check | Pass means |
|---|--------|------------|
| C1 | **Compile** | webui `design_compiler` (or equivalent) emits parseable Python containing `Window` |
| C2 | | Fail → fix marker; do not claim marker ready |

Skill-alone success = hard checks 1–7. Lab success still needs run `finished` + `<project>/data/` CSV (`webui-handoff.md`).

## Agent procedure

1. Write/edit marker (start from `marker-stub.psyclaw` if new).  
2. Run hard checks 1–7 (read file; do not skip).  
3. If webui available and user will run soon → try C1.  
4. On hard fail → fix, re-validate.  
5. On all hard pass → **marker ready** → ask 要跑被试吗 (unless already answered).

## Recap line (before ask-run)

```text
ready: <path>/<folderName>.psyclaw · <design tag> · DV=… · N=… · validate OK
```
