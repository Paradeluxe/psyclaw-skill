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
| Ask the next missing norm item in plain language | Dump all 8 items at once |
| Suggest a standard default when user is unsure | Force a named paradigm (Stroop/…) as the product |
| Mark deliberate deviations in a short note before write | Refuse to write because design is "nonstandard" |
| Prefer IV/DV/trial structure language | Domain menus ("注意/记忆/情绪…") |

## The 8-item checklist

Agent tracks coverage mentally (or in chat). Order is **priority for asking**, not sacred ritual. Skip items already answered by NL/PDF/folder.

| # | Code | Pass means | Example one-Q (zh) | Safe default if user shrugs |
|---|------|------------|--------------------|-----------------------------|
| 1 | **IV** | At least one independent variable is operationalized (what changes across conditions) | 「这次你想比较的两边/几边是什么？比如一致 vs 不一致」 | Infer from description; state assumption once |
| 2 | **DV** | Dependent measure named (RT, accuracy, rating, choice, …) and how it is logged | 「你主要看什么结果？反应时、对错、还是评分？」 | RT + correct if keyboard task; rating if slider |
| 3 | **Control** | Baseline / control / comparison structure exists, or user explicitly waives | 「有没有对照条件？还是只要一种情况？」 | Add neutral/control if paradigm usually has one; else note "no control — user OK" |
| 4 | **Random** | Trial/condition order rule (random / fullRandom / blocked / counterbalance) | 「试次顺序要打乱吗？还是按固定顺序？」 | `fullRandom` within block for factorial; sequential only if paper says so |
| 5 | **Practice** | Practice vs main trials distinguished (or user waives practice) | 「正式开始前要不要几题练习？」 | 8–12 practice, no analysis flag; main N from user or paradigm norm |
| 6 | **Script** | Instructions + end/thanks (light ethics: what to do, how to stop if needed) | 「开头要不要一段说明怎么按键？结束要不要谢谢页？」 | Short instructions + thanks; optional "可随时退出" line if human-run |
| 7 | **Response** | Keys / device, timeout or until-response, what is stored (key, RT, correct) | 「用哪些键？有没有时间限制？」 | Task-appropriate keys; store key+RT; correct if mapping known |
| 8 | **Trial+Load** | One trial skeleton complete enough to emit; long sessions get blocks/breaks | 「一题里面先出现什么、再出现什么？大概做多久？」 | fixation → stim → response → ITI; if >~30–40 min suggest blocks + rest |

### Pass / soft-fail

- **Pass**: item answered, or safely defaulted with user hearing the default once.
- **Soft-fail (still write)**: user says 就这样 / 别问了 / 按默认 / 不要对照 — record one line under `design_notes` or chat summary: `norms_deviations: […]`.
- **Hard block**: almost never. Only if marker would be empty of any trial structure (no routine/flow at all).

## Clarify behavior (agent rules)

1. **One question per turn** — pick the highest-priority unchecked item.
2. **Plain language** — no "operationalization" jargon unless user used it first.
3. **Stop signals** (same as pipeline): 满意 / 就这样 / 开始写 / 可以了 / 别问了按默认 · or IV+DV+response+trial skeleton already clear **and** remaining items defaulted.
4. **PDF / Method input**: extract norms from Method first; only ask gaps.
5. **Edit existing project**: re-check only norms touched by the edit request.
6. **Before write**: optional 3–6 line recap (IV, DV, N trials, response, order, deviations). Not a wall of text.

## What this is not

- Not sample-size power analysis (mention only if user asks).
- Not full IRB packet (consent forms, multi-site ethics).
- Not statistical analysis plan.
- Not "must match a classic paradigm name."

## Mapping into marker content (when writing)

| Norm | Typical marker / design fields |
|------|--------------------------------|
| IV | conditions / loop spreadsheet columns, condition labels |
| DV | keyboard/slider/mouse store fields; correct_ans if any |
| Control | extra condition level or baseline routine |
| Random | loop `order` / nReps / nesting |
| Practice | separate practice loop or leading routine; `is_trials` as appropriate |
| Script | instructions + thanks routines |
| Response | keyboard/slider components; stopVal / forceEnd |
| Trial+Load | routine sequence; optional rest routine between blocks |

## Kindergarten one-liner (if user is lost)

「做实验就像做菜：要说清楚比什么、量什么、有没有对照、顺序乱不乱、先练不练、怎么说明、怎么按键、一题长什么样。缺哪样我问哪样，你点头我就写说明书。」
