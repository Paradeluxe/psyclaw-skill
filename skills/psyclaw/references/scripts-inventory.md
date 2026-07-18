# Scripts inventory — 2026-06-24 audit

10 个脚本盘点, 标定决策:

## 表格

| # | 脚本 | 行数 | 用途 | 决策 | 理由 |
|---|------|------|------|------|------|
| 1 | `nl_intake.py` | 122 | NL → YAML (6 paradigm 模板) | **保留** | CREATE 意图的入口, 6 个 built-in paradigm 走它 |
| 2 | `spec_validator.py` | 125 | YAML schema 校验 | **保留** | 所有 stage 之前的 gate, 必须有 |
| 3 | `flow_gen_transform.py` | 144 | YAML → flowchart JSON (key remap, loop Point) | **保留** | json2psyexp.js 的契约翻译层, 不可少 |
| 4 | `emit.js` | 17 | Node CLI wrapper | **保留** | thin wrapper, 但 normalize 4 种 flowchart 形态的逻辑在这里, 不能丢 |
| 5 | `json2psyexp.js` | 1059 | upstream emitter (vendored) | **保留 + patch** | 核心 emit 库, 已 patch 3 个 schema bug, 不要盲升 upstream |
| 6 | `validate_psyexp.py` | 62 | 5-layer lxml check | **保留** | 不止生成要验, 修改也要验 |
| 7 | `xlsx_generator.py` | 62 | conditions xlsx | **保留** | 没有 .xlsx PsychoPy 跑不起来 |
| 8 | `stimulus_generator.py` | 184 | PIL/wave/edge-tts/ffmpeg | **保留** | 4 种 stimulus generator 是 PsyClaw 比手写 Builder 强的关键 |
| 9 | `project_scaffolder.py` | 112 | assemble runnable folder | **保留** | README + run scripts 必须有, 不然用户拿到 .psyexp 不知道跑啥 |
| 10 | `harness_main.py` | 97 | end-to-end orchestrator | **保留** | 单文件调全部 8 stage, 比手敲 8 个命令强 |
| 11 | `harness_cli.py` | 69 | CLI entry (--nl / --spec / --paradigm) | **保留** | 是给 AI 用的入口, 也是给 power user 的入口 |

## 合并/拆分建议

**没有合并/拆分的需要**。原因:
- 10 个文件职责清晰, 单文件都不超过 200 行 (json2psyexp.js 是上游 vendored 不动)
- `harness_main.py` 已经是 orchestrator, 调用其它 9 个, 没有重复逻辑
- `harness_cli.py` 是 CLI 入口, 跟 main 是分工 (cli 解析参数 → main 跑 pipeline)

## drop 候选 (但保留)

- 无。10 个脚本都有实际用途, 没有 dead code。

## 已知改造点

- `emit.js` 的 normalize 逻辑可以挪到 `flow_gen_transform.py` 末尾 (Python 实现), 减少 Node 依赖。但目前能跑, 不紧急。
- `nl_intake.py` 的 paradigm keyword 列表 (9 个) 可以拆出来到 YAML config, 方便加 paradigm。但目前 9 个够用, 不紧急。
- `validate_psyexp.py` L6 (真实 PsychoPy load) 跳过了, 是 verify 意图时手动跑 (`<psychopy-python>`)。可以让 harness_main 加一个 `--verify` flag 自动跑 L6。