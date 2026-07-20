# Experiment design norms (clarify gate, 2026-07-20)

Guide the user toward a **paper-defensible** design during the clarify loop.
Not a second product path. Not a rigid quiz. **Coach, then write.**

## Where it sits

```
Hear → Clarify (one Q/turn) + norms checklist → Write marker → Validate → [webui]
```

- Default success still = valid `<folderName>.psyclaw`.
- Norms live in **step 2** only. Do not block write forever; user override wins with a logged deviation.

## Role

| Do | Don't |
|----|--------|
| Ask the next missing norm item in plain language | Dump all items at once |
| Lock **design structure** early (× factors, within/between, continuous) | Lead with paradigm names (Stroop/…) |
| Suggest a standard default when user is unsure | Refuse nonstandard designs |
| Mark deliberate deviations before write | Domain menus ("注意/记忆/情绪…") |
| When user cites **prior literature** as reference → **anchor Qs + defaults on that paper** | Ignore the Method and fall back to generic coach defaults |

## Literature-anchored clarify (用户指定前人文献时)

**Trigger (any):** 按这篇 / 参考某某 / 复现 / 改编自 / Method PDF / 文献链接 / 「跟 paper 一样」/ replication / follow X et al.

**Goal:** clarify is **paper-first**, not generic-first. The checklist still applies, but **pass criteria and suggested defaults come from the reference Method** (and user-stated changes).

### Order

1. **Obtain text (proactive, must land)** — citation/URL/“搜一下”: **host web search first** → if fail **browser-skill** (offer install if missing) → **confirm article/Method file is saved** (path to user). Only then extract. Paste = last resort. Detail: `skill-pipeline.md` § Net fetch.
2. **Extract once (silent or short recap)** — design tag, IVs/levels, DV, trial skeleton + timing, trial N / blocks, response mapping, practice, counterbalance, special constraints (SOAs, masks, language of stimuli).
3. **Recap anchor** (brief, user language): 「按 [作者/年份] Method，我读到的是：… 默认按这个走；你要改的再说。」
4. **Clarify only gaps / conflicts**
   - Already clear in paper → **do not re-ask**; treat as answered.
   - Paper ambiguous → one Q, options framed as *paper says A / common variant B*.
   - User wants change → confirm delta; log in `design_notes` as deviation from reference.
5. **Defaults when user shrugs** → **paper value first**, then table “Safe default” only if paper silent.
6. **Citation** — put reference id (APA-ish or filename) in marker `design_notes` / session notes so the 说明书 records the anchor.

### What not to do

- Do not replace paper trial N / keys / timing with skill generic defaults without saying so.
- Do not quiz the user on items the Method already fixed.
- Do not claim perfect replication if stimuli/fonts/display cannot match — say what is matched vs approximate.
- Replication vs extension: if user says 改编, ask **one** Q on what stays vs what changes, then anchor the rest on paper.

## Design structure first (what “实验类型” means here)

**Not** paradigm brand names. **Not** a fixed deck of “N types.”  
Psychology designs are **axes combined** — that is why “总共几种” has no single integer answer.

### Three axes (teach this; lock early)

| Axis | Question | Common values |
|------|----------|----------------|
| **1. Factor structure** | What is crossed? | 1-way · *k*×*m* factorial · continuous IV(s) · continuous×continuous |
| **2. Assignment** | Who sees which cells? | within · between · mixed |
| **3. Causal strength** | Did you manipulate + randomize? | true experiment · quasi · correlational/observational |

Optional 4th (procedure, not a replace-for-design): cross-sectional vs longitudinal · blocked vs interleaved · multi-session.

**One-line design tag** (recap + `design_notes`):

```
[axis1] + [axis2] + (optional axis3)
```

Examples:

- `2×2 within` — congruency × color, everyone does all cells  
- `2 between` — train vs control groups  
- `2 within × 2 between mixed`  
- `1-way within, 3 levels`  
- `continuous × continuous` (regression-style sampling; not silent median-split)  
- `2×3 within, true experiment`

### Axis detail (agent cheat sheet)

| Kind | Meaning | Example user language |
|------|---------|------------------------|
| **Factorial levels** | How many factors × how many levels each | 「2×2」「3×2」「一个因素三水平」 |
| **Assignment** | Within / between / mixed | 「每个人都做所有条件」「一组只做一种」 |
| **IV scale** | Categorical levels vs continuous | 「一致/不一致」vs「难度 1–7」vs「两个连续变量」 |
| **Crossing** | Fully crossed vs partial cells | 「全面组合」vs「只有部分搭配」 |
| **True / quasi / corr** | Manipulate+randomize vs intact groups vs no manipulate | 「我随机分组」vs「按原班级」vs「只测相关」 |

Continuous × continuous (or continuous × categorical) still needs a **task skeleton** (what one trial shows) plus how the continuum is sampled (fixed list, random draw, adaptive — default fixed list from spreadsheet). Analysis model (ANOVA vs regression) is **not** required to write the marker; logging columns should preserve the continuous values.

## The checklist (10 items — ask by priority gap)

Agent tracks coverage mentally (or in chat). Order = **default ask priority**. Skip if NL/PDF/folder already answered.

| # | Code | Pass means | Example one-Q (zh) | Safe default if user shrugs |
|---|------|------------|--------------------|-----------------------------|
| 1 | **Design** | Factor structure clear: *k*-way factorial (e.g. 2×3), or continuous IV(s); **and** within / between / mixed | 「这是几乘几？比如 2×2。每个人做全部条件，还是分组只做一种？」 | If only one contrast named → treat as 1-way within with those levels; say so once |
| 2 | **IV** | Each factor named + levels (or continuous range + how sampled) | 「第一个因素叫什么、有几档？还有别的因素吗？」 | Infer labels from description; continuous → spreadsheet column of values |
| 3 | **DV** | Dependent measure + how logged (RT, accuracy, rating, choice, …) | 「你主要看什么结果？反应时、对错、还是评分？」 | RT + correct if keyboard; rating if slider |
| 4 | **Control** | Baseline / control cell exists, or user waives | 「有没有对照/基线条件？」 | Add control/neutral if typical; else `no control — user OK` |
| 5 | **Random** | Order rule + counterbalance scheme chosen | 「试次顺序怎么排？随机 / 拉丁方 / 分块 / 固定？要不要抵消平衡？」 | See **Counterbalance schemes** below |
| 6 | **Practice** | Practice vs main separated, and pass threshold | 「正式前要不要几题练习？准确率要多少才进正式？」 | 8–12 practice; pass threshold 60% (allow one redo, else exclude); n-back 3-back 等 high-load → 70%+ |
| 7 | **Script** | Instructions + thanks (light ethics); **same language as user session** | 「开头说明怎么做？结束要谢谢页吗？要不要藏设计委婉版？」 | Short instructions + thanks **in the user's language** (see SKILL language rule); 若有 filler/掩蔽设计 → 指导语委婉版，不告诉被试真实假设留余地 |
| 8 | **Response** | Device/keys, deadline or until-response, stored fields | 「哪些键？有无时限？」 | Task-appropriate keys; store key+RT; correct if mapping known |
| 9 | **Trial+Load** | One-trial skeleton + timing; **per-condition trial N**; session length; blocks if long | 「一题顺序？每个条件大概多少题？整段大概多久？」 | See **Trial N** below; fixation 500ms → stim → response → ITI 600~1500ms 抖动; >~30–40 min → blocks + rest. 帧取整提示仅 fMRI/ERP/眼动/TMS 触发 |
| 10 | **OutPath** | Project directory locked (absolute or agreed relative). Ask **late** — after design core, right before write | 「项目放哪？默认 `./experiments/<slug>/`，直接回车就用默认」 | See **Output location** below |

### Counterbalance schemes (item 5 — pick one)

Item 5 over random / Latin square / blocked / fixed, agent should also tell user which fits:

| Scheme | When it fits | When it doesn't |
|--------|--------------|-----------------|
| **random / fullRandom** | Within-subject, 大量 trial（>40），单次顺序扰动可接受；ERP 也常用于 jittered ITI | 短 block；少量条件（≤3）→ 顺序效应没洗掉 |
| **Latin square** | Within-subject，条件数 2~5，每被试看不同顺序抵消顺序效应；study-test / memory / 序列学习必选 | 完全随机已够；条件之间相互独立、无顺序依赖 |
| **blocked** | 练习 vs 正式分块；homogeneous block 减少切换成本；between 设计分组施测 | 想要"每一试次随机抽条件"，block 会变成连续同类 |
| **fixed / sequential** | 教学演示；demo；渐进难度/Stroop 检查 | 真正数据收集——固定顺序=无法控制顺序效应 |

**一对多（between 因素）**：分组层用 randomize 分组（被试随机分到 arm），arm 内 trial 顺序再选 random / Latin square / blocked 之一。

**默认推荐**：
- >3 因素 levels 或 trial 数 ≥40 → `random`
- 2~3 levels 且想发表 → `Latin square`
- 含 practice/main 或 high-load 任务 → `blocked`（practice/main block 分开）

### Trial N (item 9 — per condition, not participant N)

**Trial N** = how many formal trials **each condition/cell** gets.  
**Participant N** = how many people — separate; do not fake power (see below).

#### Defaults when user shrugs (behavioral RT / accuracy)

| Layer | Default | Notes |
|-------|---------|--------|
| **Practice** | 8–12 trials | High-load (n-back…) → 12–20; pass ≥60% (one redo) |
| **Per condition (cell)** | **24** | Lab norm for stable mean RT after light exclusions |
| **Demo / classroom only** | 8–12 per cell | Say once this is not publishable density |
| **Individual-diff / heavy exclusion** | 30–40 per cell | Optional upgrade if user asks reliability |
| **Exclusion buffer** | design × **1.15** | Plan extra so post-reject cells still ≈ target |

**Total formal trials** (within, fully crossed):

```text
total = (product of level counts) × trials_per_cell
# e.g. 2×2 × 24 = 96 formal
```

- User gives **total only** → split equal across cells (round; say the per-cell number).
- User gives **per-cell** → compute total; recap both.
- **Many cells** (≥6): still default 24 unless duration blows past ~35–40 min — then offer 16–20 per cell or blocks+rest, don’t silently starve cells.
- Continuous IV: “per cell” = per sampled value bin / row in the conditions list; same 24 default per row unless list is long (then shorten list or lower reps).
- Marker: conditions rows × loop `nReps` should realize the agreed total (prefer explicit rows for each cell × reps, or rows=cells and `nReps` = trials_per_cell).

#### Duration estimate (recap before write)

Rough task-core minutes (no instructions/breaks):

```text
minutes ≈ total_formal_trials × seconds_per_trial / 60
```

Default skeleton ≈ **2.5–3.5 s/trial** (fix 0.5 + stim/RT ~1–2 + ITI ~1) → **~20–25 trials/min**.

| Total formal | ≈ task core | Session note |
|--------------|-------------|--------------|
| 48 (e.g. 2×2×12 demo) | ~2–3 min | classroom OK |
| **96 (2×2×24)** | **~4–6 min** | common lab core |
| 192 (2×4×24 or 2×2×48) | ~8–12 min | still light |
| 300–400 | ~15–20 min | add mid rest if fragile pop |
| ≥600 or **>~35 min wall** | — | **blocks + rest**; reconsider per-cell or factors |

Always recap: `per-cell N · total formal · ≈ minutes · practice n`.  
Wall time includes instructions, practice, breaks — add ~5–10 min overhead in the spoken estimate.

#### Not this

- Not participant sample-size power (G*Power only if user asks **被试 N**).
- Not ERP/fMRI trial minima (those need modality-specific floors; if user says ERP, prefer ≥40 presented/cell before reject, else stay behavioral defaults).

### Output location (item 10 — late, short, defaulted)

**When to ask:** after Design + IV + DV + response + trial skeleton are clear (or operator says 开始写), **not** as Q1.

**When to skip:** input class 3 (existing project folder) → edit in place; operator already gave a path in the first message.

**One-Q template (zh):**  
「说明书要写到哪个文件夹？默认：`./experiments/<folderName>/`（里面是 `<folderName>.psyclaw`）。回车用默认，或丢一个路径/名字。」

**Resolution rules:**

| Operator gives | Agent writes |
|----------------|--------------|
| absolute path | that folder; create if missing |
| folder name / slug only | `<base>/experiments/<slug>/` |
| “默认 / 就这样 / 回车” | default below |
| existing project path | use as-is (edit mode) |

**Default base** (first that applies):

1. Explicit workspace from operator / session (`--out-dir`, “放到 X”)
2. Else current working directory of the session: `./experiments/<folderName>/`
3. Never default to Desktop
4. Never write into the agent skill install tree

**On disk:**

```
<projectDir>/
  <folderName>.psyclaw    # required marker (folderName = project folder basename)
  data/                   # created on run (webui), not required at write time
```

`folderName` = basename of `<projectDir>` (filesystem-safe: alnum + `_` + `-`).  
If operator picks a path whose basename is awkward, propose a safe slug once.

**Recap line before write must include path**, e.g.  
`out: E:/lab/experiments/my-stroop/` + design tag + DV + N.

### Design sub-rules (agent)

1. **几×几** = product of level counts for categorical factors (ignore continuous axes in the “×” slogan, or say `2 × continuous`).
2. **Within** → same participant sees all cells (usually one loop, conditions in spreadsheet).
3. **Between** → factor is group/arm; often separate conditions file or group column; do not pretend every subject sees every arm.
4. **Mixed** → state which factors are within vs between in the recap line.
5. **Continuous IV** → not fake-forced into 2-level unless user wants median-split (discourage silent median-split; prefer keep continuous or explicit bins).
6. **Continuous × continuous** → still emit trials that present pairs (or one axis manipulated per trial); log both values as columns. Analysis can be regression later — skill does not run stats.
7. **Cell N** — default **24 formal trials per condition**; if user gives total only, split equal across cells; if per-cell, compute total; always recap per-cell + total + ≈minutes (see **Trial N**).

### Pass / soft-fail

- **Pass**: answered, or defaulted with user hearing the default once.
- **Soft-fail (still write)**: 就这样 / 别问了 / 按默认 — log `norms_deviations: […]`.
- **Hard block**: almost never; only if no trial structure at all.

## Clarify behavior (agent rules)

1. **One question per turn** — highest-priority unchecked item (usually **Design** before cosmetics).
2. **Plain language** — 「几乘几、每个人做全套还是分组」not「正交因子被试内设计」unless user already speaks that way.
3. **Stop signals**: 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 · or Design+IV+DV+response+trial clear and rest defaulted.
4. **PDF / Method**: extract design line from Method first; only ask gaps.
5. **Edit existing**: re-check only norms touched by the edit.
6. **Before write**: short recap must include **design tag** (e.g. `2×2 within`) + DV + N + response + **OutPath** + deviations.
7. **OutPath last among gaps** — do not open with “where to save”; lock design first, then path, then write.

## What this is not

- Not sample-size power analysis. **But if user asks N**: give G*Power reference + recommended parameters (paired-t: dz=0.5 medium, α=0.05, power 0.80; repeated-measures ANOVA: f=0.25 medium, ε=1, α=0.05, power 0.80) without self-computing. Tell user: 「装 G*Power，tabs选 t-test / F-test → Means: Within/Repeated measures → 打这几个默认参数，G*Power 会给你最小 N」。Never fake a sample-size calc.
- Not full IRB.
- Not statistical analysis plan (ANOVA vs LMM vs regression — mention only if useful for logging columns).
- Not “must be a named classic paradigm.”

## Mapping into marker content (when writing)

| Norm | Typical marker / design fields |
|------|--------------------------------|
| Design | `design_notes` / meta: `factorial`, `assignment` (within\|between\|mixed), factor list |
| IV | conditions spreadsheet columns; one column per factor; rows = cells or sampled continuum |
| DV | keyboard/slider/mouse store; **`corrAns`** if mapping known → runner writes `corr` + summary accuracy/RT |
| Control | extra level or baseline routine |
| Random | loop `order` / nReps / nesting; between = group field not in within-loop |
| Practice | practice loop vs main loop; `pass_threshold` (default 0.60) + `max_redo` (default 1) |
| Script | instructions + thanks; `debrief_text` optional — present real hypothesis only at run end |
| Response | keyboard/slider; stopVal / forceEnd |
| Trial+Load | routine sequence; **24/cell default** (practice 8–12); nReps×conditions = total; fixation 500ms / ITI 600~1500ms jitter; rest if long |
| Metrics | classic factors on stimlist (`congruent`, `trialType`, …) + optional `metrics.group_by`; see webui `trial-metrics.md` |
| OutPath | project directory on disk; marker `<folderName>.psyclaw` inside it |
| **Seed** | optional `seed` (int) at design root; if absent → runner randomizes. Write once in marker, reuse across reruns for reproducibility |
| **Exclusion rules** | optional `exclusion_rules` block (trial-level: RT outside ±2.5 SD → `rt_outlier: true` flag; participant-level: overall accuracy < threshold). Default: flag only, do not drop. Logged but applied in analysis, not at run time |

## Kindergarten one-liner

「实验类型不是背名单，是三句话：①比的是几乘几（或连续分数）②每人做全套还是分组③你有没有真的操控/随机。然后再说量什么、怎么按键、一题长什么样。设计差不多定了再问放哪个文件夹（有默认路径）。一次问一样，你点头我就写说明书。」
