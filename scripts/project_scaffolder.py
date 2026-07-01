#!/usr/bin/env python3
"""project_scaffolder.py — Build a complete PsyClaw experiment folder."""
import argparse, shutil, sys
from pathlib import Path

README_TEMPLATE = """# {name}

{description}

## Overview

PsyClaw-generated PsychoPy experiment.

- `{psyexp_file}` — main PsychoPy Builder file
- `spreadsheets/` — conditions Excel files
- `assets/` — image/audio/video stimuli
- `run.sh` / `run.bat` — launch scripts

## How to run

1. Open PsychoPy (2023.2+)
2. File → Open → `{psyexp_file}`
3. Click green Run button

## Conditions

{n_trials} trials, randomized.

## Files

- `spreadsheets/{xlsx_files}` — per-loop conditions
- `assets/{asset_files}` — stimuli
"""

RUN_SH = """#!/bin/bash
set -e
cd "$( dirname "${{BASH_SOURCE[0]}}" )"
if command -v psychopy &> /dev/null; then
    psychopy "{psyexp_file}"
else
    echo "PsychoPy not found. Install from https://www.psychopy.org/"
fi
"""

RUN_BAT = """@echo off
cd /d "%~dp0"
where psychopy >nul 2>&1 && psychopy "%cd%\{psyexp_file}" || echo Install PsychoPy from https://www.psychopy.org/
pause
"""

REQUIREMENTS_TXT = "psychopy>=2023.2\n"

def scaffold(spec_path, out_dir, psyexp_path=None, xlsx_dir=None, assets_dir=None,
             skip_psyexp=False, skip_xlsx=False, skip_assets=False, verbose=False):
    import yaml
    with open(spec_path) as f: spec = yaml.safe_load(f)
    name = spec.get("name", "experiment")
    out = Path(out_dir) / name
    out.mkdir(parents=True, exist_ok=True)
    (out / "spreadsheets").mkdir(exist_ok=True)
    (out / "assets").mkdir(exist_ok=True)
    (out / "data").mkdir(exist_ok=True)
    if verbose: print(f"[scaffold] project dir: {out}")
    psyexp_file = None
    if not skip_psyexp and psyexp_path and Path(psyexp_path).exists():
        psyexp_file = f"{name}.psyexp"
        dest = out / psyexp_file
        shutil.copy(psyexp_path, dest)
        if verbose: print(f"  [psyexp] {psyexp_path} -> {dest}")
    xlsx_files = []
    if not skip_xlsx and xlsx_dir and Path(xlsx_dir).exists():
        for f in Path(xlsx_dir).glob("*.xlsx"):
            shutil.copy(f, out / "spreadsheets" / f.name)
            xlsx_files.append(f.name)
            if verbose: print(f"  [xlsx] {f.name}")
    asset_files = []
    if not skip_assets and assets_dir and Path(assets_dir).exists():
        for f in Path(assets_dir).iterdir():
            if f.is_file():
                shutil.copy(f, out / "assets" / f.name)
                asset_files.append(f.name)
                if verbose: print(f"  [asset] {f.name}")
    n_trials = spec.get("loops", [{}])[0].get("n_rounds", 0) if spec.get("loops") else 0
    (out / "README.md").write_text(README_TEMPLATE.format(
        name=name, description=spec.get("description","(no description)").strip(),
        psyexp_file=psyexp_file or f"{name}.psyexp", n_trials=n_trials,
        xlsx_files=", ".join(xlsx_files) or "(none)",
        asset_files=", ".join(asset_files) or "(none)"))
    if psyexp_file:
        (out / "run.sh").write_text(RUN_SH.format(psyexp_file=psyexp_file))
        (out / "run.sh").chmod(0o755)
        (out / "run.bat").write_text(RUN_BAT.format(psyexp_file=psyexp_file))
    (out / "requirements.txt").write_text(REQUIREMENTS_TXT)
    shutil.copy(spec_path, out / "experiment_spec.yaml")
    print(f"[scaffold] complete: {out}")
    return out

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True); ap.add_argument("--out-dir", default="experiments")
    ap.add_argument("--psyexp"); ap.add_argument("--xlsx-dir"); ap.add_argument("--assets-dir")
    ap.add_argument("--skip-psyexp", action="store_true")
    ap.add_argument("--skip-xlsx", action="store_true")
    ap.add_argument("--skip-assets", action="store_true")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    scaffold(args.spec, args.out_dir, args.psyexp, args.xlsx_dir, args.assets_dir,
             args.skip_psyexp, args.skip_xlsx, args.skip_assets, args.verbose)
    return 0

if __name__ == "__main__":
    sys.exit(main())
