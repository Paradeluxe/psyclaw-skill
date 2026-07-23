# Conservative workflow (product rule)

Default when the operator reports a specific bug or asks a narrow question:

## Scope = one surgical change

1. Reproduce the bug.
2. Smallest fix in **one** place.
3. Verify on one paradigm / one case.
4. Report. **Stop.**

Do **not** in the same turn:

- Add validators that were not requested
- Refactor unrelated paths
- Re-implement working components
- Add new component types “while here”
- Build extra debug tooling that was not asked for
- Edit files the operator did not name

When scope might expand, **ask once** (one question, plain language) before doing more.

## Why

Wide “fix everything nearby” turns break working code and bury the original ask. Overlap rules, emitters, and runners are easy to tangle; keep changes reviewable.

## Decision tree (symptom report)

```
Operator: "Why does X appear at the same time as Y?"

  1. Read source → exact cause
  2. Confirm on disk / minimal repro
  3. Smallest check or fix
  4. Verify that case
  5. Report → STOP
```

Separate turns for: new validators, new component types, runner rewrites, docs dumps.

## Clarify style (general)

- One question per turn when asking the operator
- Prefer short plain language over architecture walls
- Operator override (“就这样 / 按默认”) wins; log deviations
