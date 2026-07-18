#!/usr/bin/env python3
"""Re-run the 4 emit-bug detection checks against a .psyexp file.

Usage:
    python scripts/check_emit_bugs.py <file.psyexp>

Exits 0 if all checks pass, 1 if any bug is detected. Prints a
per-check report with the line numbers where the issue was found.
"""
import re
import sys
from pathlib import Path

CHECKS = [
    {
        "id": "conditionsFile-empty",
        "description": "LoopInitiator has empty conditionsFile (Bug 1)",
        "pattern": re.compile(
            r'<Param name="conditionsFile"[^/]*val=""', re.MULTILINE
        ),
    },
    {
        "id": "correctAns-empty",
        "description": "Keyboard component has empty correctAns (Bug 2)",
        "pattern": re.compile(
            r'<Param name="correctAns"[^/]*val=""', re.MULTILINE
        ),
    },
    {
        "id": "stale-anchor",
        "description": "Stale `anchor` param (Bug 4 — only allowed on ImageComponent)",
        "pattern": re.compile(r'<Param[^/]*name="anchor"', re.MULTILINE),
    },
    {
        "id": "stale-stopWithRoutine",
        "description": "Stale `stopWithRoutine` param (Bug 4)",
        "pattern": re.compile(r'<Param[^/]*name="stopWithRoutine"', re.MULTILINE),
    },
]

# isTrials check is special: if a single loop is present, we can't tell
# from one value alone whether it's correct — the test is to build a
# nested-loop YAML and confirm the two values differ. This script just
# reports whatever it sees.
IS_TRIALS = re.compile(r'<LoopInitiator[^>]*name="([^"]+)"', re.MULTILINE)
IS_TRIALS_VAL = re.compile(
    r'<Param name="isTrials"[^/]*val="(True|False)"', re.MULTILINE
)


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2

    path = Path(sys.argv[1])
    if not path.exists():
        print(f"file not found: {path}", file=sys.stderr)
        return 2

    text = path.read_text(encoding="utf-8")
    failures = 0

    print(f"=== {path} ===\n")

    for check in CHECKS:
        matches = list(check["pattern"].finditer(text))
        if matches:
            failures += 1
            print(f"[FAIL] {check['id']}: {check['description']}")
            for m in matches:
                line_no = text[: m.start()].count("\n") + 1
                print(f"        line {line_no}")
        else:
            print(f"[ ok ] {check['id']}")

    # isTrials report (informational — true bug only visible with nested loops)
    loops = IS_TRIALS.findall(text)
    is_trials_vals = IS_TRIALS_VAL.findall(text)
    print()
    if len(loops) > 1 and len(set(is_trials_vals)) == 1:
        print(
            f"[WARN] {len(loops)} loops present but all have the same isTrials "
            f"value: {is_trials_vals}. If this is a nested-loop test with "
            f"is_trials:true and is_trials:false, that is Bug 3."
        )
        failures += 1
    elif loops:
        print(
            f"[info] isTrials values: {list(zip(loops, is_trials_vals))}"
        )

    print()
    if failures:
        print(f"FAIL ({failures} bug(s) detected)")
        return 1
    print("PASS (no emit-bug patterns found)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
