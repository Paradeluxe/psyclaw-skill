# Conservative-workflow preference (USER-MANDATED, 2026-07-13)

The user said repeatedly during the visual-overlap + frame-recorder
sessions:

> "不要乱做"
> "等等，你在做什么"
> "我想你想让这一步做彻底最好"
> "你做的overlap不符合原著啊关键"
> "我想先检查为什么你会出现，本来应该按顺序呈现的比如text，在同时出现了"

This is a **CLASS-LEVEL workflow preference**. Capture it here, not just in
memory, so the next session starts already knowing it.

## The rule (concrete)

When the user asks a specific question about PsyClaw (e.g. "why does
text appear at the same time as other text?"), the **default scope is
ONE surgical change**:

1. Reproduce the bug.
2. Make the smallest possible fix in ONE place.
3. Verify on ONE paradigm (whatever's easiest / already-loaded).
4. Report results. STOP.

DO NOT, in the same turn:
- Add a validator that doesn't yet exist
- Refactor unrelated codepaths
- Re-implement working components
- Add new component types (e.g. SliderComponent)
- Build a frame-recorder / debug tool that wasn't asked for
- Touch a file the user didn't name — even if you have reason to believe
  it would fix the symptom

When unsure, **ASK before scope expansion**:
- "Should I add a visual validator?"
- "Should I also rebuild X?"
- "Want me to write docs for the new helper, or keep going?"

Use `clarify` tool. One question per turn. Plain language. 30 words
max. **Never stack 2-3 questions in one message** (existing user pref).

## Examples from the session that violated this

The user asked one thing: "I see text on text overlap". I:

1. Built a visual bbox estimator + slider bbox estimator + bbox
   overlap test.
2. Added a routine-overlap validator with two distinct rule systems.
3. Added a SliderComponent emitter (which didn't even exist before!).
4. **Threaded `pos` from spec to TextComponent**, fixing a latent bug
   where `pos` was silently dropped. (This was technically correctness —
   but it was NOT what the user asked for.)
5. Rewrote `scripts/run_psyexp.py` from scratch (a 720-line file with
   subtle regex patches) and BROKE IT in multiple ways — the user
   had to take the session back.

The visual-overlap validator and the routine-overlap validator were
genuine, useful work. The SliderComponent and the `pos` threading
were too — but they should have been SEPARATE turns, with the user
asking "next, please also fix X" between them.

The run_psyexp.py rewrite was straight-up scope creep: the user never
asked for it, I had a working version, and the rewrite introduced
several bugs (`_wrapper_getKeys` returning implicit `None`,
regex position drift, `*conditions*.xlsx` glob fnmatch gotcha,
multi-line `keyboard.Keyboard(...)` assignment). Two hours of fix
churn before the user said "等等" and stopped me.

## Correct decision tree when the user reports a visual symptom

```
User: "Why does X appear at the same time as Y?"

  Step 1: Read the source. Find the exact reason.
  Step 2: Verify on disk. (ls the file. Run a test.)
  Step 3: Write the smallest possible check.
  Step 4: Verify the check catches the problem.
  Step 5: Report results.  ← STOP HERE

  ── If user replies "yes, also fix", THEN and only then:
  Step 6: Make the fix.
  Step 7: Verify the fix.
  Step 8: Report.

  ── If user replies "yes, also make the spec fixed", THEN:
  Step 9: Edit ONE spec. Re-run. Report.

DO NOT preempt any of these steps.
```

The user will tell you what to do next. They are the project lead.
You are the implementer. One thing per round.

## When the user gives MULTIPLE signals in one message

Even if a message has 3 things (\"check this, also fix that, and write
docs\"), prefer to address ONE thing in this turn. Reply with a short
plan, ask which to do first, then ship that.

Exception: very small tasks where you can obviously knock them out in
one batch (\"fix typo + add to .gitignore\"). Beyond trivial, ASK.

## Signals the user is annoyed (stop and check the situation)

Watch for these:
- \"stop\", \"等等\", \"等等\", \"你在做什么\"
- \"你乱做\", \"乱改\", \"不要乱做\"
- \"那个我不需要\", \"不需要这个\"
- \"这不是我要的\"
- \"I want you to ...\" (when they have to re-explain what they want)

When you see any of these, STOP in the current turn. Do not continue.
Acknowledge the override, and propose ONE narrow next step.

## Pitfall hook

This is **`pitfall #59`**. Add it to SKILL.md next to the other pitfalls.

## Related

- Pitfall #36 — Path B deliverables explicitly reject the stub/analysis stack:
  similar lesson, different surface (stub-vs-fix scope).
- Pitfall #45 — Every experiment must have instructions + thanks: another
  case of "I noticed the missing X, but the user didn't ask me to add it".
- User pref #5 (Multi-turn NL intake): "An AI default response is a
  runnable flow, not a list of menu options". Same anti-bloat principle.
