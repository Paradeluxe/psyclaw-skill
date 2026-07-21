# Norms appendix — counterbalance (checklist item 5)

Load when choosing order / 随机 / 拉丁方 / 分块, or user asks. Core checklist: `norms-core.md`.

| Scheme | When it fits | When it doesn't |
|--------|--------------|-----------------|
| **random / fullRandom** | Within-subject, many trials (>40); jittered ITI (ERP-friendly) | Short blocks; ≤3 conditions → order effects remain |
| **Latin square** | Within, 2–5 conditions; memory / study-test / sequence learning | Full random already enough; conditions independent, no order concern |
| **blocked** | Practice vs main; homogeneous blocks; between arms run as groups | Want every-trial random condition draws |
| **fixed / sequential** | Demo / teaching / progressive difficulty check | Real data collection (order confounded) |

**Between factor:** randomize assignment to arm; inside arm pick random / Latin / blocked for trials.

**Defaults:**

- >3 factor levels or trials ≥40 → `random`  
- 2–3 levels and publication-oriented → `Latin square`  
- practice/main or high-load → `blocked` (separate practice/main)

Marker: loop `loopType` / order / nesting; between = group field not inside within-loop. See `norms-marker-map.md`.
