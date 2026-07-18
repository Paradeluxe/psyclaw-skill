# Experiment design norms (clarify gate, 2026-07-18)

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

## Design structure first (what “实验类型” means here)

**Not** paradigm brand names. **Yes** the statistical / assignment skeleton:

| Kind | Meaning | Example user language |
|------|---------|------------------------|
| **Factorial levels** | How many factors × how many levels each | 「2×2」「3×2」「一个因素三水平」 |
| **Assignment** | Within-subjects / between-subjects / mixed | 「每个人都做所有条件」「一组只做 A」 |
| **IV scale** | Categorical levels vs continuous predictors | 「一致/不一致」vs「难度 1–7」vs「两个连续变量」 |
| **Crossing** | Fully crossed vs nested / only some cells | 「全面组合」vs「只有部分搭配」 |

Continuous × continuous (or continuous × categorical) still needs a **task skeleton** (what one trial shows) plus how the continuum is sampled (fixed list, random draw, adaptive — default fixed list from spreadsheet).

Agent goal: before deep trial cosmetics, get a one-line design tag, e.g.

- `2×2 within (congruency × color)`  
- `2 between (group: control/train)`  
- `mixed: 2 within × 2 between`  
- `continuous rating ~ continuous intensity` (regression-style; trials sample the continuum)

## The checklist (9 items — ask by priority gap)

Agent tracks coverage mentally (or in chat). Order = **default ask priority**. Skip if NL/PDF/folder already answered.

| # | Code | Pass means | Example one-Q (zh) | Safe default if user shrugs |
|---|------|------------|--------------------|-----------------------------|
| 1 | **Design** | Factor structure clear: *k*-way factorial (e.g. 2×3), or continuous IV(s); **and** within / between / mixed | 「这是几乘几？比如 2×2。每个人做全部条件，还是分组只做一种？」 | If only one contrast named → treat as 1-way within with those levels; say so once |
| 2 | **IV** | Each factor named + levels (or continuous range + how sampled) | 「第一个因素叫什么、有几档？还有别的因素吗？」 | Infer labels from description; continuous → spreadsheet column of values |
| 3 | **DV** | Dependent measure + how logged (RT, accuracy, rating, choice, …) | 「你主要看什么结果？反应时、对错、还是评分？」 | RT + correct if keyboard; rating if slider |
| 4 | **Control** | Baseline / control cell exists, or user waives | 「有没有对照/基线条件？」 | Add control/neutral if typical; else `no control — user OK` |
| 5 | **Random** | Order rule: random / fullRandom / blocked / counterbalance / fixed | 「试次顺序打乱吗？要不要抵消平衡？」 | Within: `fullRandom` in block; between: randomize trial order inside arm; counterbalance condition order if few blocks |
| 6 | **Practice** | Practice vs main separated, or waived | 「正式前要不要几题练习？」 | 8–12 practice; main N from user or cell-count rule of thumb |
| 7 | **Script** | Instructions + thanks (light ethics) | 「开头说明怎么做？结束要谢谢页吗？」 | Short instructions + thanks |
| 8 | **Response** | Device/keys, deadline or until-response, stored fields | 「哪些键？有无时限？」 | Task-appropriate keys; store key+RT; correct if mapping known |
| 9 | **Trial+Load** | One-trial skeleton; blocks/breaks if long | 「一题顺序？大概做多久？」 | fixation → stim → response → ITI; >~30–40 min → blocks + rest |

### Design sub-rules (agent)

1. **几×几** = product of level counts for categorical factors (ignore continuous axes in the “×” slogan, or say `2 × continuous`).
2. **Within** → same participant sees all cells (usually one loop, conditions in spreadsheet).
3. **Between** → factor is group/arm; often separate conditions file or group column; do not pretend every subject sees every arm.
4. **Mixed** → state which factors are within vs between in the recap line.
5. **Continuous IV** → not fake-forced into 2-level unless user wants median-split (discourage silent median-split; prefer keep continuous or explicit bins).
6. **Continuous × continuous** → still emit trials that present pairs (or one axis manipulated per trial); log both values as columns. Analysis can be regression later — skill does not run stats.
7. **Cell N** — if user gives total trials only, offer split equal across cells; if they give per-cell N, compute total.

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
6. **Before write**: short recap must include **design tag** (e.g. `2×2 within`) + DV + N + response + deviations.

## What this is not

- Not sample-size power analysis (only if user asks).
- Not full IRB.
- Not statistical analysis plan (ANOVA vs LMM vs regression — mention only if useful for logging columns).
- Not “must be a named classic paradigm.”

## Mapping into marker content (when writing)

| Norm | Typical marker / design fields |
|------|--------------------------------|
| Design | `design_notes` / meta: `factorial`, `assignment` (within\|between\|mixed), factor list |
| IV | conditions spreadsheet columns; one column per factor; rows = cells or sampled continuum |
| DV | keyboard/slider/mouse store; correct_ans if any |
| Control | extra level or baseline routine |
| Random | loop `order` / nReps / nesting; between = group field not in within-loop |
| Practice | practice loop vs main loop |
| Script | instructions + thanks |
| Response | keyboard/slider; stopVal / forceEnd |
| Trial+Load | routine sequence; rest between blocks |

## Kindergarten one-liner

「先说清这盘棋怎么摆：几乘几、每人做全套还是分组、因素是分档还是连续分数；再说量什么、怎么按键、一题长什么样。一次问一样，你点头我就写说明书。」
