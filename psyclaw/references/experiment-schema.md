# PsyClaw Experiment Schema (设计稿) — 2026-06-24

> **核心思想**: 心理学实验 = 4 个必须块 (Design / Procedure / Stimuli / Response) + 2 个可选块 (Metadata / Display)。
> 各块**只管自己抽象层的事**,不互相重复。冲突在 schema 层面解决,不在运行时靠 AI 猜。

> **状态 (2026-06-24)**: **设计稿阶段, 未落地代码**。用户原话 "我们不用 gui 了, 直接通过跟你的交互来做" + "我觉得我们应该不应该匹配任何 paradigm...这个流程本质上是为了创造实验流程脚本的"——所以**这个 schema 不是落到磁盘的 schema, 只作为 AI 引导时的中间表示**, 实际写到磁盘的还是老的 `ExperimentDesign YAML` (routines/loops/components)。本文件保留是为了将来真要重写时有个起点。已定决策在 `references/interaction-flow.md` §11。

## 块结构总览

| 块 | 必须? | 抽象层 | 主管什么 |
|----|-------|--------|---------|
| 1. Metadata | 可选 | 文档 | 谁做的、IRB、招募信息 |
| 2. Display | 可选 | 硬件 | 屏幕参数 |
| 3. **Design** | **必须** | **逻辑** | **变量定义** |
| 4. **Procedure** | **必须** | **流程** | **时序阶段、试次结构** |
| 5. **Stimuli** | **必须** | **内容** | **刺激素材** |
| 6. **Response** | **必须** | **采集** | **反应设备、按键** |

---

## 3. Design 块(必须)

**只描述变量, 不说"试次怎么排"**。试次结构归 Procedure。

```yaml
design:
  # ── 自变量列表 (IV) ──
  # 一组 IV 是同一个 factor 的多个水平, IV 间是 factorial 关系
  independent_variables:
    - name: congruency                # 字符串, kebab-case 或 snake_case
      type: categorical               # categorical | continuous | ordinal
      levels:                         # categorical/ordinal: 列标签
        - congruent
        - incongruent
    # 多个 IV = factorial 设计
    # - name: word_meaning
    #   type: categorical
    #   levels: [literal, metaphorical]
    # continuous IV 用 range:
    # - name: stimulus_duration
    #   type: continuous
    #   range: [100, 1000]
    #   unit: ms

  # ── 因变量 (DV) ──
  # DV 是用户测什么, 怎么采集归 Response 块
  # 决策 (2026-06-24): 不合并 confidence 和 rating, 各自一个
  dependent_variables:
    - rt                              # 反应时
    - accuracy                        # 正确率
    # - confidence                   # 对自己答题的把握 (Likert)
    # - rating                       # 对刺激本身的主观打分 (Likert)

  # ── 随机化 ──
  # 决策 (2026-06-24): 全局一份, 不做 per-phase 覆盖
  randomization: fullRandom           # sequential | random | fullRandom
```

**字段规则**:
- `independent_variables`: 至少 1 个 IV, 可有任意多个
- `dependent_variables`: 至少 1 个 DV, 可多个;当前支持枚举: `rt`, `accuracy`, `confidence`, `rating`
- `randomization`: 默认 `fullRandom`
- **冲突规则**: 这里**不写试次数**, 试次归 Procedure 块。试次和 factorial 设计的乘法关系在 Procedure 阶段。

### DV 决策细节

**confidence vs rating (2026-06-24)**:
- `confidence` = 对自己答题的把握 ("我答得准不准", 1=瞎猜, 7=很确定)
- `rating` = 对刺激本身的主观打分 ("我喜不喜欢这个图", 1=非常不喜欢, 7=非常喜欢)
- 两者都是 1-7 Likert 但语义不同 → **不合并**, 各占一个枚举值
- 合并带来的"长尾分析混淆"代价 > 多记一个枚举名的成本

---

## 4. Procedure 块(必须,且能覆盖 Design)

**描述时序、阶段、试次结构**。每个 phase 是一个完整时段(instruction / practice / main / break / debrief)。

**核心冲突解决 (2026-06-24)**: Design 块的 IV × 水平数 vs "30 trials" 数字会冲突 (eg 2×2 设计下 60 trials 每 cell 15 次)。**Solution**: 试次结构归 Procedure, 用 `repeats_per_cell` 而非 `total_trials`, 让 factorial 关系在 Procedure 阶段算出来。

```yaml
procedure:
  phases:
    - name: instruction
      duration: until_response        # until_response | <N>s | infinite
      # 不在 loop 里, 只跑 1 次

    - name: practice
      duration: until_response
      trials: 10                      # 显式试次数, 不走 factorial
      # 适用于: 练习阶段 (通常 IV 组合不全)

    - name: main                      # 主试次, factorial 设计
      duration: until_response
      loop: true                      # 进入 loop
      repeats_per_cell: 30            # 每个 IV 组合重复 30 次
      # 算出来: 30 × (2 IV1 levels) = 60 trials total
      # 若是 2 IV 各 2 水平: 30 × 2 × 2 = 120 trials

    - name: break
      duration: 30s

    - name: test                      # 可有第二个 main 阶段, repeats_per_cell 可不同
      duration: until_response
      loop: true
      repeats_per_cell: 40
      # 算出来: 40 × 2 = 80 trials
```

**冲突解决规则**:
- 同一 phase, `loop: true` 时 `repeats_per_cell` 必填
- `trials` 和 `repeats_per_cell` 互斥: 不在 loop 里用 `trials`, 在 loop 里用 `repeats_per_cell`
- factorial 试次数 = `repeats_per_cell × ∏(IV levels)`; validate 阶段检查合理性(每 cell ≥5)
- mixed/nested 设计 (eg N-back 的 probe + filler): 在 procedure 里用显式 `trials` 而非 `repeats_per_cell`, 跳过 factorial

### 为什么不支持 per-phase randomization (决策细节)

- 6 个现有 paradigm 模板都是单 randomization (Stroop/Flanker 全 fullRandom, Posner 全 sequential), 从没出现过"练习 sequential + 测试 fullRandom"的需求
- 全局一份 → schema 简单, AI 不用每个 phase 处理"用全局还是自己定"
- 真要支持 per-phase 时, 加 `phase.randomization` 字段即可, 默认 fallback 到全局; 反过来从 per-phase 砍成全局是破坏性变更

---

## 5. Stimuli 块(必须)

**刺激素材清单 + 生成方式**。跟 Design 的 IV 水平一一对应。

[待设计]

### 决策 (2026-06-24): 单个 stimulus, 不是复合结构

- 单个 stimulus = 一块内容 (一个图、一个词、一个声音), 不管实际呈现多复杂 (Stroop 的颜色词需要颜色 + 词两个子刺激), 都被试看成"一个东西"
- 复合 stimuli (背景+前景) 在 routine 里加多个 component 自然处理
- 不要在 stimulus 层引入"主体 + 修饰 + 上下文"三层结构, 太复杂

---

## 6. Response 块(必须)

**反应采集方式**。跟 Design 的 DV 一一对应。

[待设计]

---

## 落盘策略 (2026-06-24 决策)

**本 schema 不落到磁盘, 仅作 AI 引导时的中间表示**。理由:

- 用户原话: "我觉得我们应该不应该匹配任何 paradigm...这个流程本质上是为了创造实验流程脚本的"
- 老 `ExperimentDesign YAML` (routines/loops/components) 是 PsychoPy Builder 的事实标准, 用户学会能直接用 Builder 打开 .psyexp 调
- AI 翻译新 schema → 老 YAML 是 N→M 映射, 每个 paradigm 都不一样, 维护成本高且易错
- 通过对话引导 (本 schema) 把老 YAML 翻译成自然语言给用户看, 而不是改 schema

---

## 已完成决策汇总 (来自 `references/interaction-flow.md` §11)

| 决策 | 结论 |
|------|------|
| DV `confidence` 与 `rating` 合并? | **不合并**, 各自一个枚举 |
| `randomization` 全局 vs per-phase? | **全局一份** |
| 新 schema vs 老 YAML? | **新 schema 不落盘, 老 YAML 是事实标准** |
| Stimulus 单个 vs 复合? | **单个** (复合在 routine 层处理) |
| IV vs total_trials 冲突? | **用 `repeats_per_cell` 而非 `total_trials`**, Procedure 块解决 |
| 用户超时未答? | **best judgement, 列备忘, 用户随时可推翻** |

---

## 待办

- [ ] Stimuli 块字段设计 (asset / external / generator / size / duration / position)
- [ ] Response 块字段设计 (device / keys / window / feedback)
- [ ] Metadata 块哪些字段真要哪些不要
- [ ] Display 块哪些字段真要哪些不要
- [ ] 如果未来真要落地, YAML schema 验证规则(lint 脚本怎么写)