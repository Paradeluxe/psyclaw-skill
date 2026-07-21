# Experiment design norms — core (clarify gate)

**Coach, then write.** One question or one **topic cluster** per turn. User override + logged deviation wins.  
Lit fetch / intent → `skill-pipeline.md`. Appendices (load only when needed):

| File | When |
|------|------|
| `norms-counterbalance.md` | item 5 detail / user asks 随机·拉丁方·分块 |
| `norms-trial-n.md` | item 9 detail / trial N · 时长 · 被试 N(G*Power) |
| `norms-marker-map.md` | writing marker fields / seed / exclusion |

```
[lit landed?] → Clarify + this checklist → Write (stub) → Validate → [ask run]
```

| Do | Don't |
|----|--------|
| Next missing gap, plain language | Dump all 10 items |
| Lock design structure early | Lead with paradigm brand names |
| Default when unsure; paper values if lit | Refuse nonstandard; ignore Method |

## Literature-anchored clarify

**After** Method on disk: paper-first.

1. **Extract** — design tag, IVs, DV, trial skeleton/timing, N/blocks, keys, practice, counterbalance, specials  
2. **Recap** — 「按 [作者/年份]，读到：… 默认按这个；要改再说。」  
3. **Gaps only** — paper-clear → skip; ambiguous → paper A / variant B; user change → log deviation  
4. **Shrug** → paper value; checklist default only if paper silent  
5. **Citation** in `design_notes` (+ path)  

Don't silently replace paper N/keys/timing; don't claim perfect replication if display/stimuli can't match. 改编 → one Q stays vs changes.

## Design structure first

**Not** paradigm brands. **Not** a fixed “N types.” Axes combine.

| Axis | Question | Common values |
|------|----------|----------------|
| **1. Factor structure** | What is crossed? | 1-way · *k*×*m* · continuous · continuous×continuous |
| **2. Assignment** | Who sees which cells? | within · between · mixed |
| **3. Causal strength** | Manipulate + randomize? | true experiment · quasi · correlational |

**Design tag** (recap + `design_notes`): `[axis1] + [axis2] + (optional axis3)`  
Examples: `2×2 within` · `2 between` · `2 within × 2 between mixed` · `1-way within, 3 levels` · `continuous × continuous`

| Kind | User language |
|------|----------------|
| Factorial | 「2×2」「一个因素三水平」 |
| Assignment | 「每个人都做全套」「一组只做一种」 |
| IV scale | 「一致/不一致」vs「难度 1–7」 |
| True/quasi/corr | 「我随机分组」vs「按原班级」vs「只测相关」 |

Continuous IVs need a **trial skeleton** + sampling (default fixed list). Do not silent median-split. Analysis model not required to write marker; log continuous columns.

## Checklist (10 — ask by priority gap)

Track coverage. Skip if NL/PDF/folder already answered.  
**Cluster OK:** items 1–3 as one design one-liner when user is fast (`2×2 within · IVs · DV`).

| # | Code | Pass means | Example one-Q (zh) | Safe default |
|---|------|------------|--------------------|--------------|
| 1 | **Design** | *k*×*m* or continuous; within/between/mixed | 「几乘几？每人全套还是分组？」 | One contrast → 1-way within; say once |
| 2 | **IV** | Factors + levels (or continuous range + sampling) | 「因素叫什么、几档？还有别的吗？」 | Infer labels from description |
| 3 | **DV** | Measure + how logged | 「看反应时、对错、还是评分？」 | RT+correct if keyboard; rating if slider |
| 4 | **Control** | Baseline cell or waived | 「有没有对照/基线？」 | Neutral if typical; else note waived |
| 5 | **Random** | Order + counterbalance scheme | 「随机 / 拉丁方 / 分块 / 固定？」 | Defaults → `norms-counterbalance.md` |
| 6 | **Practice** | Practice vs main; pass threshold | 「正式前练习几题？准确率门槛？」 | 8–12; pass 60% (one redo); high-load 70%+ |
| 7 | **Script** | Instructions + thanks; **session language** | 「开头怎么说？结束谢谢页？」 | Short instr+thanks; mask hypothesis if needed |
| 8 | **Response** | Device/keys, deadline, stored fields | 「哪些键？有无时限？」 | Task keys; store key+RT; `corrAns` if known |
| 9 | **Trial+Load** | Skeleton + **per-cell N** + duration | 「一题顺序？每条件多少题？」 | fix 500ms→stim→resp→ITI jitter; detail → `norms-trial-n.md` |
| 10 | **OutPath** | Project dir locked. Ask **last** | 「项目放哪？默认 `./experiments/<slug>/`」 | See Output location below |

### Output location (item 10)

**When:** after Design+IV+DV+response+trial clear (or 开始写). **Skip** if editing existing path.  
**Never:** Desktop; skill install tree.

| Operator gives | Write |
|----------------|--------|
| absolute path | that folder |
| slug only | `./experiments/<slug>/` (or session base) |
| 默认 / 回车 | `./experiments/<folderName>/` |
| existing project | edit in place |

On disk: `<projectDir>/<folderName>.psyclaw` with `folderName` = basename.  
Recap before write: `out: …` + design tag + DV + N.

### Design sub-rules

1. **几×几** = product of categorical level counts (or `2 × continuous`).  
2. **Within** → one loop, all cells; **Between** → group/arm, not every subject every arm; **Mixed** → state which is which.  
3. **Cell N** default 24/condition — detail in `norms-trial-n.md`.

### Pass / soft-fail

- **Pass:** answered, or defaulted once out loud.  
- **Soft-fail (still write):** 就这样 / 按默认 — log `norms_deviations`.  
- **Hard block:** almost never; only if no trial structure at all.

## Clarify behavior

1. Highest-priority unchecked gap (Design before cosmetics). Cluster 1–3 OK.  
2. Plain language unless user already uses jargon.  
3. **Stop:** 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 · or Design+IV+DV+response+trial clear.  
4. PDF/Method: extract first; gaps only.  
5. Edit existing: only norms touched by the edit.  
6. **Before write:** design tag + DV + N + response + OutPath + deviations.  
7. OutPath last among gaps.  
8. After write → `marker-validate.md` → ask-run.

## What this is not

- Not sample-size power (if user asks 被试 N → `norms-trial-n.md` G*Power blurb; never fake N).  
- Not full IRB / full stats plan / must-be-named paradigm.

## One-liner

几×几 + 全套/分组 + 量什么/按键/一题长什么样 → 再问文件夹。
