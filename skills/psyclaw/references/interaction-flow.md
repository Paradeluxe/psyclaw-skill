# PsyClaw Interaction Flow — 2026-06-24 rewrite

> **产品定位**: 完全无 GUI, 用户跟 AI(我)对话, 我在后台跑 pipeline 出完整项目。
> 这份文件是"产品需求文档", 讲清楚用户说啥、AI 接啥、stage 边界在哪。

---

## 1. 用户意图分类 (intent classes)

用户对 PsyClaw 的需求只有 4 种本质意图:

| 意图 | 触发词 / 场景 | 典型输入 | 输出 |
|------|---------------|----------|------|
| **CREATE** | "做一个 Stroop 实验", "我需要 N-back", "想跑个 GoNoGo" | 自然语言 | 完整项目目录 |
| **MODIFY** | "把 trial 数改成 50", "feedback 改成红色", "加一个 break routine" | 局部修改描述 | 更新后的项目目录 + diff 说明 |
| **DIAGNOSE** | "为什么 .psyexp PsychoPy 打开报错", "这个 routine 是干嘛的", "我改错了" | 报错信息 / 反问 | 错误定位 + 修复建议 |
| **VERIFY** | "用真实 PsychoPy 验一下", "看 README", "跑一下试试" | "验一下" / "跑一下" | validate_psyexp 输出 + 真实 PsychoPy load 结果 |

**重要**: 4 种意图的 pipeline 路径不一样, 不能一锅炖。

| 意图 | 走的 stage |
|------|-----------|
| CREATE | 全部 8 个 stage |
| MODIFY | 只重跑受影响的 stage (YAML 没改 → 跳过 nl_intake) |
| DIAGNOSE | 大概率只走 stage 1-3 (看 spec / flowchart), 不 emit |
| VERIFY | stage 5 + 真实 PsychoPy loadFromXML |

---

## 2. Stage contract

每个 stage 是一个独立可调用的"工位", 有明确的输入/输出 contract。

### Stage 1 — `nl_intake.py`  →  **NL → ExperimentDesign YAML**
- **输入**: `--nl "做 Stroop 30 trials"` / `--paradigm stroop --n-trials 30` / `--spec foo.yaml`
- **输出**: ExperimentDesign YAML (kebab-case name, routines, loops, stimuli)
- **contract**:
  - 6 个 built-in paradigm 走模板 (Stroop/GoNoGo/Flanker/N-back/IAPS/Posner)
  - 其余 paradigm 或复杂需求 → AI 手写 YAML (绕过 nl_intake, 直接 stage 2)
  - 用户可以直接给 YAML, 完全跳过此 stage
- **失败模式**: paradigm 识别不出 → AI 启动 §6 intent discovery 引导, 不死循环

### Stage 2 — `spec_validator.py`  →  **YAML schema check**
- **输入**: YAML path
- **输出**: exit 0 (valid) / 2 (errors) / 10 (file missing) / 11 (no PyYAML)
- **contract**:
  - 校验结构 (name required, routines non-empty, loop refs valid)
  - 不校验语义 ("30 trials 是否合理" — 不管)
- **依赖**: PyYAML

### Stage 3 — `flow_gen_transform.py`  →  **YAML → flowchart JSON**
- **输入**: YAML path, output JSON path
- **输出**: `{routines: [...], loops: [...]}` consumed by json2psyexp.js
- **contract**:
  - key remap (snake_case → camelCase or json2psyexp convention)
  - Loop Point = `(routineIndex + 1) * 2` (json2psyexp.js line 754)
  - 内联 spreadsheet rows 直接写到 loop.list
- **失败模式**: 字段名映射错 (schema drift 4 种变体) — 见 pitfalls §1

### Stage 4 — `emit.js` + `json2psyexp.js`  →  **flowchart → .psyexp XML**
- **输入**: flowchart JSON path, output .psyexp path
- **输出**: PsychoPy 2026.1.1 兼容的 .psyexp 文件
- **contract**:
  - 接受 4 种 flowchart 形态 (root array / routines[] / routineRects[] + loops / avtpData obj)
  - emit.js 做 normalize → json2psyexp.js 做转换
  - 3 个已知 schema bug 已 patch (`anchor`/`stopWithRoutine`/`flip` — 见 SKILL.md pitfall §6)

### Stage 5 — `validate_psyexp.py`  →  **5-layer XML check**
- **输入**: .psyexp path
- **输出**: exit 0 (pass) / non-zero (fail)
- **contract**:
  - L1 XML parse (lxml recover mode)
  - L2 settings/routines/flow sections
  - L3 each routine has ≥1 component
  - L4 loop initiator == terminator count
  - L5 each Param has val + valType + name
- **NOTE**: L6 (real PsychoPy load) 是 verify 意图的事, 不在这里跑

### Stage 6 — `xlsx_generator.py`  →  **conditions.xlsx per loop**
- **输入**: YAML, output dir
- **输出**: openpyxl xlsx, 每个 loop 一个 spreadsheet
- **依赖**: openpyxl

### Stage 7 — `stimulus_generator.py`  →  **PIL/ffmpeg/edge-tts assets**
- **输入**: YAML, output dir
- **输出**: image (PIL) / tone (wave) / TTS (edge-tts) / video (ffmpeg H.264)
- **依赖**: pillow, edge-tts, ffmpeg

### Stage 8 — `project_scaffolder.py`  →  **assemble runnable folder**
- **输入**: psyexp, xlsx dir, assets dir, out dir
- **输出**: `experiments/<name>/` 含 README/run.sh/run.bat/requirements.txt

---

## 3. 操作语义 (operation semantics)

用户消息怎么映射到 stage 调用:

| 用户说 | AI 行为 | 走哪个 stage |
|--------|---------|-------------|
| "做 Stroop 30 trials" | nl_intake → 全部 8 stage | 1-8 |
| "把 trial 数改成 50" | edit YAML → 从 stage 2 重跑 | 2-8 (跳过 1) |
| "feedback 加个红色" | edit YAML (color: red) → 从 stage 2 重跑 | 2-8 |
| "在 trial 前加 fixation" | edit YAML (routine reorder) → 从 stage 2 重跑 | 2-8 |
| "为什么 PsychoPy 报错" | 读 .psyexp → 跑 stage 5 + 真实 load | 5 + L6 |
| "用真实 PsychoPy 验" | 调 D:\Software\P\python.exe 跑 loadFromXML | L6 |
| "看 README" | cat experiments/<name>/README.md | 无 stage |
| "做 N-back 但 paradigm 词是 working memory" | AI 手写 YAML (不走模板) → 跳过 1 | 2-8 |

---

## 4. 交互模式分层

按复杂度分 3 档, 每档有不同的"AI 自动度":

### Level 1 — Chat-only (默认, 最快)
- 用户一句话, AI 直接跑全部 stage, 出项目目录
- 适用: 标准 paradigm, 用户已信任 AI
- 不展示中间产物

### Level 2 — Show spec first (重要实验)
- 用户一句话, AI 先跑 stage 1 出 YAML → 把 YAML 路径和摘要贴给用户看
- 用户点头 → 跑 stage 2-8
- 适用: 不熟 paradigm, 或想看 AI 的理解对不对

### Level 3 — Iterate on YAML (深度参与)
- 用户一句话 → AI 跑 stage 1 出 YAML → 用户改 YAML → AI 从 stage 2 重跑
- 适用: 用户知道实验设计但想自己调 timing/keys/text

**默认 Level 1**, 用户主动说"先给我看看"才升 Level 2, "我自己改改"才升 Level 3.

---

## 5. 错误处理哲学

| 失败 stage | AI 行为 |
|-----------|---------|
| 1 (nl_intake) | paradigm 识别不出 → 启动 §6 intent discovery 引导; YAML schema 错 → 给错+建议修法 |
| 2 (validator) | 列错, 让用户/AI 修 YAML, 不绕过 |
| 3 (transform) | 大概率 schema drift → 重新跑 emit 看具体错 |
| 4 (emit) | 真实 PsychoPy load 验, 把 warning 列给用户 |
| 5 (validate) | 列 layer 错, 提示回 stage 1-4 哪里出问题了 |
| 6/7/8 | 资源/依赖错 (ffmpeg 不在 PATH / edge-tts 没装), 提示安装 |

**核心原则**: 不静默 retry, 不"猜"用户意图, 出错就把错摊开给用户看。

---

## 6. Intent discovery (引导式) — 设计草稿 2026-06-24

> **关键教训 (2026-06-24)**: 用户明确否决了"按领域分类 (注意/记忆/情绪/社会...)"的引导思路。原话 "我不喜欢领域分类, 主要是变量类型和数量要先确定"。**任何想做引导分类的人, 第一反应应该是按变量 (IV/DV/水平) 拆, 不要按心理学子领域拆。** 领域分类对用户的认知负担没降低——他们本来就懂自己想研究什么, 只是缺术语翻译。
>
> **第二教训 (同日)**: 用户的整体设计意图是"先和用户讨论清楚实验设计类型 (如果用户不知道的话, 你要引导用户做)"——所以 §6 是必须的, 不能因为 §4 默认 Level 1 就跳过。但 §6 的入口和形态不能按领域分类。

**触发条件**: 用户消息没指定 paradigm / 关键参数 (trials/blocks/IV 数), AI 启动引导而非直接跑 pipeline。

**核心思想**: **变量驱动, 不是领域驱动**。心理学实验设计 = IV × DV × 试次结构, paradigm 由变量组合反推。

```
Step 1: IV 数 (1 / 2 / 3 / 混合)
   ↓
Step 2: 每个 IV 的变量类型 (categorical / continuous / 不知道)
   ↓
Step 3: 每个 IV 的水平数 (2 / 3 / 4 / 其它)
   ↓
Step 4: DV 类型 (RT / accuracy / 两者 / RT+confidence / 眼动 / Likert)
   ↓
Step 5: 候选 paradigm 匹配 (Step 1-4 → 2-4 candidates, 用户选 1)
   ↓
Step 6: 试次结构 + 时长预算 (N trials × blocks × 时长)
   ↓
Step 7: 确认 → 跑 stage 1-8
```

**规则**:
- 最多 7 轮, 超了直接问 "你最关心哪个参数?其它我默认"
- 用户说 "我都知道, 按 X 做" → 立即升 Level 1, 跳过引导
- DV=眼动/生理 → 诚实说做不了, 引导到 e-prime / eyelink 自带工具
- 每步多选 + 填空混合, 不强制必选
- Step 5 的 paradigm 候选从现有模板 + 复杂 YAML 库里匹配

**形式**: 用户消息里有以下任一, 触发引导而非 Level 1 pipeline:
- 没指定 paradigm / 范式: "做个心理学实验" / "我想研究注意力" / "做个认知实验"
- paradigm 词含糊: "做个跟记忆有关的" / "关于情绪的实验"
- 没说关键参数 (trials / blocks / IV 数)

**不触发引导**: paradigm 明确 + 关键参数齐全 → 直接走 Level 1 pipeline.

---

## 7. 暂不实现的功能 (out of scope)

- 实验**运行** (PsychoPy 实验运行时) — 只生成 .psyexp, 用户在 PsychoPy 跑
- 实验**数据分析** — 出 CSV 后用户自己处理
- 实验**迭代版本管理** — 改了就改覆盖, 不存 history
- 多用户协作 — 单用户对话, 无 session 共享

---

## 8. 跟旧 GUI 的差异

| 维度 | 旧 GUI (psyclaw.html) | 新交互 |
|------|----------------------|--------|
| 输入 | 表单 + flowchart 拖拽 | 自然语言对话 |
| 中间产物 | flowchart JSON (可视化) | YAML (文本) |
| 错误处理 | console.log + 模态框 | AI 把错摊开给用户 |
| 自动化 | 受 showDirectoryPicker 限制 | 我全权跑 |
| 多 paradigm | 模板切换 | 一句话识别 |
| 文件系统 | FileSystemDirectoryHandle (浏览器权限) | 我用普通 fs (无沙盒限制) |

---

## 9. 工作流偏好 (2026-06-24 用户原话)

用户原话: "要不我们从零开始规划一下交互方式, 然后看看从目前的代码里有需要的就拿"

**含义**: 任何产品形态的重新设计, 工作流是
1. **先规划交互模式** (意图分类 / 引导流程 / Level 分层)
2. **再盘点现有代码资产** (keep / merge / split / drop)
3. **最后才动代码**

**不要反过来**——不要先看现有代码能做什么, 再倒推交互模式 (那会被现有代码绑架, 做不出"本来应该是什么形态"的判断)。

---

## 10. 询问风格 (2026-06-24 用户原话)

用户对 AI 在 PsyClaw 流程中**主动发问**时的两个偏好:

### 10.1 "一个一个问呢"

> 用户原话: "一个一个问呢"

**规则**: AI 需要用户输入时, **每个 turn 只问一个问题**。如果一个 topic 有多个子决定 (例如 IV 数 / IV 类型 / IV 水平数), 拆成多轮, 一次只走一步。**一直问到用户满意/可以开写为止**（满意 / 就这样 / 开始写 / 可以了 / 别问了按默认），不要问完一句就强行开写。例外:
- 多选题可以一次列多个选项 (用户从 4 个选项里挑 1, 算"一个问题")
- 用户主动说 "我都知道, 按 X 做" / "下一步" → 立即跳到下个 topic, 不再细问

**反面例子**: "你想研究什么?有 3 个 IV 吗?每个 IV 是 categorical 还是 continuous?有 blocks 吗?" — 4 个问题一锅
**正面例子**: "你想研究什么? [6 选 1 候选 paradigm]" — 1 个问题 + 选项

### 10.2 "简单易懂的语言"

> 用户原话: "一个一个问呢, 简单易懂的语言"

**规则**:
- 默认中文 (用户是中文母语)
- 避免设计类 jargon ("响应抑制范式"、"被试内设计" 之类)。改用大白话 + 一句话解释 ("被试内设计 = 同一个被试经历所有条件")
- 心理学/PsychoPy 术语本身 (IV / DV / Likert / RT) 可以用, 因为用户群就熟
- 用户自己用了 jargon → 跟着用; 用户用大白话 → 解释术语再追问

### 10.3 适用范围

只在 **CREATE intent + 需要 intent discovery 引导** 时, 这两条规则生效:
- MODIFY (改 X 成 Y) — AI 不问, 直接改
- DIAGNOSE (为什么报错) — AI 不问, 直接 debug
- VERIFY (跑一下) — AI 不问, 直接跑
- CREATE 但参数齐全 (eg "Stroop 30 trials") — AI 不问, 直接走 Level 1

### 10.4 与 §6 的关系

§6 是 intent discovery 的 **流程骨架** (Step 1-7)。§10 是**提问风格**, 是骨架上套的语气壳子。两件事正交——可以拆开用。

---

## 11. 已定决策 (跨轮对话累积, 备忘用)

下列决策在 2026-06-24 多轮对话中通过 best-judgement 落定 (用户多次 timeout 未反驳), 后续 intent discovery / schema 实现默认遵守:

| 决策 | 结论 | 触发场景 |
|------|------|---------|
| DV 枚举 `confidence` 与 `rating` 合并? | **不合并** | 用户两次 timeout |
| `randomization` 全局 vs per-phase? | **全局一份** | 用户两次 timeout |
| 新 schema (Design/Procedure/...) vs 老 YAML (routines/loops)? | **就用老 YAML, 新 schema 不落盘, 仅作引导中间表示** | 用户明确说 "流程本质上是为了创造实验流程脚本的" |
| Stimulus 单个 vs 复合结构? | **单个** | 用户 timeout 后我定为单个 (Stroop 的颜色词在 routine 层拆 component 已够用) |
| 自变量 vs total_trials 冲突? | **默认走 factorial, 用 `repeats_per_cell` 而非 `total_trials`; Procedure 块的 `trials` 字段是 mixed/nested 逃生口** | 用户 timeout 后我定为方案 B |
| 用户超时未答怎么办? | **best judgement, 列在 §11 备忘, 用户随时可推翻** | 元规则 |
| 用户说 "你定一套能跑的框架" → 我自己定 | **整段 scaffold 跑通 + 把所有 best-judgement 决策落进 §11** | 用户原话 |

---

## 12. 当前能力范围 (2026-06-24 验证过)

| 能力 | 状态 | 验证 |
|------|------|------|
| NL → 完整项目目录 | **OK** | smoke test: `--nl "做一个 Stroop 实验 30 trials"` → `/tmp/psyclaw-smoke/stroop_experiment/` 含 7 文件 |
| 6 paradigm 模板 → .psyexp | **OK** (Stroop/GoNoGo/Flanker/N-back/IAPS/Posner) | 实测 5/5 PASS in lxml + real PsychoPy loadFromXML |
| 复杂自定义 YAML | **OK** (8 routines + 2 loops) | 实测 .psyexp 46KB, 332 params |
| 真实 PsychoPy 加载验证 | **OK** | D:\Software\P\python.exe loadFromXML, 0 warnings |
| Project scaffold (README/run.sh/run.bat) | **OK** | smoke test 验过 |
| 中文 NL 输入 | **OK** | "色词" / "go-nogo" / "n-back" 都识别 |
| Mixed/nested 设计 (eg N-back 的 probe + filler) | **未直接验证** | 代码层支持 (Procedure.trials 字段), 但 end-to-end smoke test 没跑过 |
| Schema 升级 (Design/Procedure/Stimuli/Response) | **未实现** | 只有 `references/experiment-schema.md` 设计稿, 没有代码落地 |
| Intent discovery 7-step 引导 (产品需求 §6) | **未实现** | 设计稿有, 没代码 |
| Level 2 / Level 3 升降级 (产品需求 §4) | **未实现** | harness_cli 始终 Level 1, 升降级靠对话触发 |
| Real PsychoPy 2026.1.1 loadFromXML (Windows D:\Software\P\python.exe) | **OK for Stroop 30-trial** | `routines=4, flow=6, stderr=空 (0 warnings)`. 其他 5 paradigm 端到端 Windows 验没跑过, 但 emit 层 lxml validator 都过 |