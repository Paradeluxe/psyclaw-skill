# psyclaw（Hermes 技能）

[English](README.md) · [中文](README.zh-CN.md)

[![License: AGPL-3.0](https://img.shields.io/badge/License-AGPL--3.0-blue.svg)](LICENSE)
[![Hermes skill](https://img.shields.io/badge/Hermes-%2Fpsyclaw-8B5CF6)](https://github.com/Paradeluxe/psyclaw-skill)
[![Marker](https://img.shields.io/badge/marker-.psyclaw-0ea5e9)](https://github.com/Paradeluxe/psyclaw-skill)
[![Platform](https://img.shields.io/badge/platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)](https://github.com/Paradeluxe/psyclaw-skill)
[![Lab GUI](https://img.shields.io/badge/lab%20GUI-psyclaw--webui-22c55e)](https://github.com/Paradeluxe/psyclaw-webui)
[![GitHub stars](https://img.shields.io/github/stars/Paradeluxe/psyclaw-skill?style=social)](https://github.com/Paradeluxe/psyclaw-skill)

把自然语言描述（或论文 Method）变成项目文件夹里的 **`<folderName>.psyclaw`**。

**宗旨：拿起来就能用。** 论文/自然语言 → 可跑标记 → webui 跑被试 → `data/` 长表+汇总+指标长表。

- **斜杠命令：** `/psyclaw`
- **GitHub：** https://github.com/Paradeluxe/psyclaw-skill
- **不是**实验室 GUI——那是 **[psyclaw-webui](https://github.com/Paradeluxe/psyclaw-webui)**（跑被试 → CSV）。

## 用户使用管线

只有一条主线。安装见下文，与日常使用分开。本节是 **`/psyclaw` 日常怎么用**。

```text
输入
  ├─ 自然语言描述实验
  ├─ 论文 Method / PDF / HTML / 粘贴   （需要时用 browser-skill 拉取）
  └─ 已有项目文件夹 + 标记文件         （原地修改）

        ▼
澄清  （每轮只问一个问题 · 教练式）
  • 用户不确定时给出标准默认建议
  • 先定设计结构（几×几、被试内/间/混合、连续自变量）
  • 再 IV → DV → 对照 → 随机 → 练习 → 指导语 → 反应 → 单试次
  • 最后才定输出路径（默认 ./experiments/<slug>/）
  • 停止信号：满意 / 就这样 / 开始写 / 按默认 / 核心项已清

        ▼
写入 + 校验（G0）
  <projectDir>/<folderName>.psyclaw     # 设计 JSON，不是 Builder 的 .psyexp

        ▼
询问是否开跑  （由智能体主动问——不要干等用户自己发明「能跑吗」）
  「说明书写好了。要跑被试吗？」

        ├─ 否  → 结束（有标记文件即可）
        │
        └─ 是  → 交接 psyclaw-webui（G1 finished → G2 project/data/*.csv）
                   • 按顺序逐个跑被试
                   • 被试编号 / UID 自动分配
                   • P_pilot 不占用正式编号
                   • 正式跑完 → 下一号 + 新 UID
                   • 智能体驱动开跑时：session.experimenter = AI 身份
```

| 用户意图 | 行为 |
|----------|------|
| 做一个实验 | 澄清 → 写 G0 → **问是否开跑** |
| 改已有设计 | 改标记 → G0 → **问是否开跑** |
| 要跑 / 多人 | webui 顺序跑；自动编号；智能体开跑则 experimenter=AI |
| 不要跑 / 只要说明书 | G0 后停止 |
| 全装 / 首次部署 | doctor → 征得同意 → 只补缺项 |

**本技能不做：** 半跑 /「只预览几题」作为产品模式（webui 的 Builder 有组件 PREVIEW；实验室交付是完整 Start/Pilot + CSV）。不做 CSV 后的统计分析。不做 Builder `.psyexp`。

### 磁盘交付物

```text
MyExp/
  MyExp.psyclaw          # 必需标记（文件夹名 + .psyclaw）
  data/                  # 跑完后由 webui 镜像写出
  participants.json      # 名册（webui）
```

| 门禁 | 含义 |
|------|------|
| **G0** | 标记可编译（合法设计 JSON → PsychoPy 脚本形态） |
| **G1** | 运行状态为 `finished` |
| **G2** | CSV 落在 **`<project>/data/`** |

仅技能 = 到 G0 + 询问是否开跑。完整实验室成功需要 webui + PsychoPy。

## 安装（不是使用管线）

```bash
hermes skills install psyclaw -y
# 始终可用的完整 id：
hermes skills install Paradeluxe/psyclaw-skill/skills/psyclaw -y
```

然后在新会话里用 `/psyclaw`。

| | 会装 | 不会装 |
|--|------|--------|
| `hermes skills install …` | 本技能 → `/psyclaw` | webui、Flask 虚拟环境、PsychoPy、browser-skill |
| 实验室 GUI | 另行安装 [psyclaw-webui](https://github.com/Paradeluxe/psyclaw-webui) | Hermes 智能体 |
| 相关 | **browser-skill** 可选（第二类：拉 PDF/Method） | 不静默安装 |

首次使用 / 全装：doctor 查缺 → **征得同意** → 只装缺的。详见 `skills/psyclaw/references/install-orchestrator.md`。

## 仓库布局

```text
psyclaw-skill/
  README.md            # 英文（默认）
  README.zh-CN.md      # 中文
  LICENSE
  NOTICE
  skills.sh.json
  skills/
    psyclaw/
      SKILL.md
      scripts/doctor.py
      references/   # 管线、规范、webui 交接门禁
```

## 自检

```bash
python skills/psyclaw/scripts/doctor.py
```

## 许可证

**AGPL-3.0** — [LICENSE](LICENSE)。PsychoPy 另计 — [NOTICE](NOTICE)。
