# Run prep (tell the user)

Load when `ask_run=yes` / handoff starts. **Operator-facing only** — no API dumps.  
Agent/API detail → `api-notes.md`. Failures → `failure-playbooks.md`.

## Before subjects

State this short checklist (same facts as webui **System** tab when available). Do not guess PsychoPy paths.

| # | Item | Say plainly |
|---|------|-------------|
| 1 | **Project** | folder path + marker name |
| 2 | **WebUI** | `http://127.0.0.1:8876` up, or starting it |
| 3 | **PsychoPy** | python path + source (`env` / `library` / `standalone`) from System / resolve — not invented |
| 4 | **Gate** | System pass/warn/fail; **fail → fix before formal run** |

Example:

```text
准备跑被试：
- 项目：E:\labs\MyStroop\（MyStroop.psyclaw）
- 实验室软件：http://127.0.0.1:8876
- 实验引擎：C:\...\python.exe（library）
- System 预检：通过
```

## Multi-subject (one line)

按顺序逐个开跑；正式跑完自动下一号；`P_pilot` 不占正式号。智能体开跑时 `session.experimenter` = AI 身份。

## Success (lab)

| Check | Pass |
|-------|------|
| Run finished | status `finished` |
| Data on disk | CSV under **`<project>/data/`** |

Marker ready alone ≠ lab success.

## Done checklist (agent, before close)

- [ ] path + marker name correct  
- [ ] design tag + deviations noted  
- [ ] validate OK (or compile OK if webui up)  
- [ ] `ask_run` recorded in session file  
- [ ] if ran: CSV under `data/` or user stopped cleanly → `state=done`
