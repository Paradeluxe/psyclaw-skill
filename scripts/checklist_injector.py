#!/usr/bin/env python3
"""checklist_injector.py — Inject pre-experiment hardware/environment checks into a PsyClaw YAML spec.

Scans spec for component types and inserts appropriate check routines
between the instructions routine and the first trial loop.

Mapping:
  audio component        → headphone_check (tone + Y/N confirmation)
  image / video          → screen_check (visual pattern + Y/N confirmation)
  keyboard with store    → latency_check (5-beep RT calibration)

Usage:
  python checklist_injector.py spec.yaml --output spec_checked.yaml
"""

import yaml
import copy
from pathlib import Path


# ── Check routine templates ───────────────────────────────────────────────

HEADPHONE_CHECK = {
    "name": "headphone_check",
    "duration": None,
    "components": [
        {
            "type": "text",
            "text": (
                "Headphone Check\n\n"
                "Please put on your headphones.\n"
                "You will hear a short tone.\n\n"
                "Press Y if you heard it clearly.\n"
                "Press N if you did not."
            ),
            "height": 0.04,
            "color": "white",
        },
        {
            "type": "audio",
            "path": "assets/check_tone.wav",
            "duration": 1.0,
            "volume": 1.0,
        },
        {
            "type": "keyboard",
            "keys": "y,n",
            "duration": None,
            "store": "headphone_ok",
        },
    ],
}

SCREEN_CHECK = {
    "name": "screen_check",
    "duration": None,
    "components": [
        {
            "type": "text",
            "text": (
                "Screen Check\n\n"
                "You should see a white cross on a dark background.\n"
                "Check that the screen is not cropped or flickering.\n\n"
                "Press Y if everything looks correct.\n"
                "Press N if something is wrong."
            ),
            "height": 0.035,
            "color": "white",
        },
        {
            "type": "text",
            "text": "+",
            "height": 0.1,
            "color": "white",
        },
        {
            "type": "keyboard",
            "keys": "y,n",
            "duration": None,
            "store": "screen_ok",
        },
    ],
}

LATENCY_CHECK = {
    "name": "latency_check",
    "duration": None,
    "components": [
        {
            "type": "text",
            "text": (
                "Response Time Calibration\n\n"
                "You will hear 5 beeps.\n"
                "Press SPACE as quickly as possible after EACH beep.\n\n"
                "Press SPACE to begin."
            ),
            "height": 0.035,
            "color": "white",
        },
        {
            "type": "keyboard",
            "keys": "space",
            "duration": None,
            "store": None,
        },
    ],
}

CHECK_TEMPLATES = {
    "headphone_check": HEADPHONE_CHECK,
    "screen_check": SCREEN_CHECK,
    "latency_check": LATENCY_CHECK,
}


# ── Detection ─────────────────────────────────────────────────────────────

def detect_required_checks(spec: dict) -> list[str]:
    """Scan all routine components; return ordered list of check names needed."""
    checks = []

    has_audio = False
    has_visual = False
    has_rt = False

    for routine in spec.get("routines", []):
        for comp in routine.get("components", []):
            ctype = comp.get("type", "")
            if ctype == "audio":
                has_audio = True
            if ctype in ("image", "video"):
                has_visual = True
            if ctype == "keyboard" and comp.get("store") and comp["store"] != "headphone_ok":
                has_rt = True

    # Text always counts as visual (every experiment has at least text)
    for routine in spec.get("routines", []):
        for comp in routine.get("components", []):
            if comp.get("type") in ("text", "image", "video", "slider"):
                has_visual = True
                break

    # Ordered: hardware checks first, then calibration
    if has_audio:
        checks.append("headphone_check")
    if has_visual:
        checks.append("screen_check")
    if has_rt:
        checks.append("latency_check")

    return checks


def get_check_routine(name: str) -> dict | None:
    template = CHECK_TEMPLATES.get(name)
    return copy.deepcopy(template) if template else None


def find_insertion_point(routines: list[dict]) -> int:
    """Find where to insert check routines: right after 'instructions' routine."""
    for i, r in enumerate(routines):
        name = r.get("name", "")
        if "instruction" in name.lower():
            return i + 1
    # Fallback: insert at position 0 (before everything)
    return 0


# ── Injection ─────────────────────────────────────────────────────────────

def inject_checks(spec: dict) -> dict:
    """Deep-copy spec, inject check routines, return modified spec."""
    spec = copy.deepcopy(spec)
    required = detect_required_checks(spec)

    if not required:
        return spec

    check_routines = []
    for name in required:
        r = get_check_routine(name)
        if r:
            check_routines.append(r)

    routines: list = spec.setdefault("routines", [])
    insert_at = find_insertion_point(routines)

    for i, check in enumerate(check_routines):
        routines.insert(insert_at + i, check)

    # Annotate description
    desc = spec.get("description", "")
    spec["description"] = f"{desc} [Pre-experiment checks: {', '.join(required)}]"

    return spec


# ── CLI ───────────────────────────────────────────────────────────────────

def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Inject hardware/environment checks into PsyClaw spec"
    )
    parser.add_argument("spec", help="Input YAML spec")
    parser.add_argument("--output", "-o", required=True, help="Output YAML path")
    args = parser.parse_args()

    with open(args.spec, encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    required = detect_required_checks(spec)
    print(f"Detected: {required if required else '(none)'}")

    checked = inject_checks(spec)

    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    with open(args.output, "w", encoding="utf-8") as f:
        yaml.dump(checked, f, default_flow_style=False, allow_unicode=True, sort_keys=False)

    n_routines = len(checked.get("routines", []))
    print(f"Saved: {args.output} ({n_routines} routines)")


if __name__ == "__main__":
    main()
