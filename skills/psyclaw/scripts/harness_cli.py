#!/usr/bin/env python3
"""harness_cli.py — Single-entry CLI for PsyClaw pipeline.

Input modes:
  --nl "natural language"          generate spec from NL
  --spec path/to/experiment.yaml   use existing spec
  --paradigm stroop --n-trials 30  use built-in template
"""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent

def run(cmd, check=True, capture=True):
    r = subprocess.run(cmd, capture_output=capture, text=True)
    if check and r.returncode != 0:
        print(f"[FAIL] {' '.join(map(str, cmd))}", file=sys.stderr)
        if r.stdout: print(r.stdout, file=sys.stderr)
        if r.stderr: print(r.stderr, file=sys.stderr)
    return r

PY = sys.executable

def nl_to_spec(nl_text, out_yaml, n_trials=None, n_back=None, paradigm=None):
    cmd = [PY, str(SCRIPT_DIR / "nl_intake.py"), "--input", nl_text, "--output", str(out_yaml)]
    if n_trials: cmd += ["--n-trials", str(n_trials)]
    if n_back is not None: cmd += ["--n-back", str(n_back)]
    if paradigm: cmd += ["--paradigm", paradigm]
    r = run(cmd)
    if r.returncode != 0:
        print(f"[cli] nl_intake.py failed: {r.returncode}", file=sys.stderr)
        if r.stdout: print(r.stdout, file=sys.stderr)
        if r.stderr: print(r.stderr, file=sys.stderr)
    return r.returncode == 0

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    inp = ap.add_mutually_exclusive_group(required=True)
    inp.add_argument("--nl"); inp.add_argument("--spec"); inp.add_argument("--paradigm")
    ap.add_argument("--n-trials", type=int); ap.add_argument("--n-back", type=int)
    ap.add_argument("--out-dir", default="experiments")
    ap.add_argument("--validate-only", action="store_true")
    ap.add_argument("--keep-spec", action="store_true")
    args = ap.parse_args()
    out_dir = Path(args.out_dir).resolve(); out_dir.mkdir(parents=True, exist_ok=True)
    if args.spec:
        spec_path = Path(args.spec).resolve()
        if not spec_path.exists():
            print(f"[FATAL] spec not found: {spec_path}", file=sys.stderr); return 1
    elif args.nl or args.paradigm:
        work = Path(tempfile.mkdtemp(prefix="psyclaw_cli_"))
        spec_path = work / "spec.yaml"
        if args.paradigm:
            text = f"做一个 {args.paradigm} 实验"
            if args.n_trials: text += f", {args.n_trials} trials"
            ok = nl_to_spec(text, spec_path, args.n_trials, args.n_back, args.paradigm)
        else:
            ok = nl_to_spec(args.nl, spec_path, args.n_trials, args.n_back)
        if not ok:
            print("[FATAL] failed to generate spec", file=sys.stderr); return 2
        if args.keep_spec:
            shutil.copy(spec_path, out_dir / "spec.yaml")
    if args.validate_only:
        r = run([PY, str(SCRIPT_DIR / "spec_validator.py"), str(spec_path), "-v"], check=False)
        return r.returncode
    r = run([PY, str(SCRIPT_DIR / "harness_main.py"), "--spec", str(spec_path),
             "--out-dir", str(out_dir)], check=False)
    return r.returncode

if __name__ == "__main__":
    sys.exit(main())
