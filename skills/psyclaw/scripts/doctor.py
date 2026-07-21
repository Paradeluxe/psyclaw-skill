#!/usr/bin/env python3
"""psyclaw skill doctor — local package health (no network)."""
from __future__ import annotations

import json
import sys
from pathlib import Path
from shutil import which

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "scripts/doctor.py",
    "references/skill-pipeline.md",
    "references/experiment-design-norms.md",
    "references/norms-core.md",
    "references/norms-counterbalance.md",
    "references/norms-trial-n.md",
    "references/norms-marker-map.md",
    "references/marker-stub.psyclaw",
    "references/marker-validate.md",
    "references/session-state.md",
    "references/session-stub.json",
    "references/install-orchestrator.md",
    "references/webui-handoff.md",
    "references/user-conservative-workflow-preference.md",
]


def main() -> int:
    print("psyclaw doctor")
    print(f"  root: {ROOT}")
    ok = True
    for rel in REQUIRED:
        p = ROOT / rel
        status = "OK" if p.is_file() else "MISSING"
        if status != "OK":
            ok = False
        print(f"  [{status}] {rel}")

    skill = ROOT / "SKILL.md"
    name = desc = None
    if skill.is_file():
        text = skill.read_text(encoding="utf-8", errors="replace")
        if text.startswith("---"):
            parts = text.split("---", 2)
            if len(parts) >= 3:
                for line in parts[1].splitlines():
                    if line.startswith("name:"):
                        name = line.split(":", 1)[1].strip()
                    if line.startswith("description:"):
                        desc = line.split(":", 1)[1].strip()
        print(f"  name: {name or '?'}")
        if desc:
            print(f"  description: {desc[:80]}{'…' if len(desc) > 80 else ''}")

    for cmd, label in (("python", "python"),):
        path = which(cmd)
        print(f"  [{'OK' if path else '—'}] {label}: {path or 'not on PATH'}")

    report = {
        "ok": ok,
        "root": str(ROOT),
        "name": name,
        "slash": f"/{name}" if name else None,
        "deliverable": "<folderName>.psyclaw",
    }
    print("  json:", json.dumps(report, ensure_ascii=False))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
