#!/usr/bin/env python3
"""harness_main.py — End-to-end orchestrator for PsyClaw pipeline."""
import argparse, shutil, subprocess, sys, tempfile
from pathlib import Path

SCRIPT_DIR = Path(__file__).parent
PEERS = {
    "spec_validator": SCRIPT_DIR / "spec_validator.py",
    "transform": SCRIPT_DIR / "flow_gen_transform.py",
    "emit_js": SCRIPT_DIR / "emit.js",
    "json2psyexp": SCRIPT_DIR / "json2psyexp.js",
    "validate_psyexp": SCRIPT_DIR / "validate_psyexp.py",
    "xlsx_gen": SCRIPT_DIR / "xlsx_generator.py",
    "stim_gen": SCRIPT_DIR / "stimulus_generator.py",
    "scaffold": SCRIPT_DIR / "project_scaffolder.py",
}

def run(cmd, cwd=None, check=True, capture=True):
    r = subprocess.run(cmd, cwd=cwd, capture_output=capture, text=True)
    if check and r.returncode != 0:
        print(f"[FAIL] {' '.join(map(str, cmd))}", file=sys.stderr)
        if r.stdout: print("stdout:", r.stdout, file=sys.stderr)
        if r.stderr: print("stderr:", r.stderr, file=sys.stderr)
    return r

PY = sys.executable

def step(spec_path, out_dir, verbose):
    """Run stages 1-7. Stage 8 (scaffold) is done by caller using the returned project_dir."""
    out_dir = Path(out_dir).resolve()
    work = out_dir / "_work"
    work.mkdir(parents=True, exist_ok=True)
    json_path = work / "flowchart.json"
    psyexp_path = work / f"{spec_path.stem}.psyexp"
    xlsx_dir = work / "spreadsheets"
    assets_dir = work / "assets"
    xlsx_dir.mkdir(exist_ok=True); assets_dir.mkdir(exist_ok=True)
    # 1. validate
    if verbose: print("[1/8] spec_validator...")
    r = run([PY, str(PEERS["spec_validator"]), str(spec_path), "-v"])
    if r.returncode != 0: return None, r.stdout + r.stderr
    # 2. transform
    if verbose: print("[2/8] transform...")
    r = run([PY, str(PEERS["transform"]), str(spec_path), str(json_path), "-v"])
    if r.returncode != 0: return None, r.stdout + r.stderr
    # 3. emit (needs emit.js + json2psyexp.js together)
    if verbose: print("[3/8] emit (Node)...")
    emit_dir = work / "emit_workdir"
    emit_dir.mkdir(exist_ok=True)
    shutil.copy(PEERS["emit_js"], emit_dir / "emit.js")
    shutil.copy(PEERS["json2psyexp"], emit_dir / "json2psyexp.js")
    r = run(["node", "emit.js", str(json_path), str(psyexp_path)], cwd=emit_dir)
    if r.returncode != 0: return None, r.stdout + r.stderr
    # 4. validate psyexp
    if verbose: print("[4/8] validate_psyexp...")
    r = run([PY, str(PEERS["validate_psyexp"]), str(psyexp_path)])
    if r.returncode != 0:
        print(r.stdout); return None, "psyexp validation failed"
    # 5. xlsx
    if verbose: print("[5/8] xlsx_generator...")
    r = run([PY, str(PEERS["xlsx_gen"]), "--spec", str(spec_path), "--out-dir", str(xlsx_dir), "-v"])
    if r.returncode != 0: return None, r.stdout + r.stderr
    # 6. stimuli
    if verbose: print("[6/8] stimulus_generator...")
    r = run([PY, str(PEERS["stim_gen"]), "--spec", str(spec_path), "--out-dir", str(assets_dir), "-v"])
    if r.returncode != 0: return None, r.stdout + r.stderr
    # 7. scaffold (项目目录 = out_dir / name)
    if verbose: print("[7/8] project_scaffolder...")
    import yaml
    with open(spec_path) as f: spec = yaml.safe_load(f)
    name = spec.get("name", spec_path.stem)
    # 让 project_scaffolder 直接写到 out_dir (它会建 out_dir/name/)
    r = run([PY, str(PEERS["scaffold"]), "--spec", str(spec_path), "--out-dir", str(out_dir),
             "--psyexp", str(psyexp_path), "--xlsx-dir", str(xlsx_dir), "--assets-dir", str(assets_dir), "-v"])
    if r.returncode != 0: return None, r.stdout + r.stderr
    project_dir = out_dir / name
    # 清理 _work/ (scaffold 已把所有需要的文件拷过去了)
    shutil.rmtree(work, ignore_errors=True)
    return project_dir, None

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True); ap.add_argument("--out-dir", help="output base directory")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args()
    spec_path = Path(args.spec).resolve()
    if not spec_path.exists():
        print(f"[FATAL] not found: {spec_path}", file=sys.stderr); return 1
    if not args.out_dir:
        args.out_dir = str(spec_path.parent / "_build")
    out_dir = Path(args.out_dir).resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    project_dir, err = step(spec_path, out_dir, verbose=not args.quiet)
    if project_dir:
        print(f"\n=== SUCCESS: {project_dir} ===")
        return 0
    else:
        print(f"\n=== FAILED: {err} ===", file=sys.stderr)
        return 2

if __name__ == "__main__":
    sys.exit(main())
