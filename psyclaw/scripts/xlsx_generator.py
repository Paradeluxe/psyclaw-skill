#!/usr/bin/env python3
"""xlsx_generator.py — Generate Excel conditions files for loops."""
import argparse, sys
from pathlib import Path
try:
    import openpyxl
except ImportError:
    print("[FATAL] openpyxl required", file=sys.stderr); sys.exit(1)
try:
    import yaml
except ImportError:
    print("[FATAL] PyYAML required", file=sys.stderr); sys.exit(1)

def _coerce_value(val, col_type):
    if val is None or val == "": return ""
    if col_type in ("int",):
        try: return int(val)
        except: return val
    if col_type in ("float", "num"):
        try: return float(val)
        except: return val
    if col_type in ("bool",):
        if isinstance(val, bool): return 1 if val else 0
        if isinstance(val, str): return 1 if val.lower() in ("true","1","yes") else 0
        return 1 if val else 0
    return str(val)

def generate_xlsx_for_loop(loop_spec, out_path, verbose=False):
    ss = loop_spec.get("spreadsheet")
    if not ss: return None
    columns = ss.get("columns", []); rows = ss.get("rows", [])
    if not columns: return None
    fname = ss.get("file") or (loop_spec.get("name","loop") + "_conditions.xlsx")
    out_path = Path(out_path) / fname
    out_path.parent.mkdir(parents=True, exist_ok=True)
    wb = openpyxl.Workbook(); ws = wb.active; ws.title = "conditions"
    ws.append([c["name"] for c in columns])
    for row in rows:
        ws.append([_coerce_value(row.get(c["name"], ""), c.get("type","str")) for c in columns])
    wb.save(str(out_path))
    if verbose: print(f"  [xlsx] {loop_spec.get('name')}: {out_path} ({len(rows)} rows, {len(columns)} cols)")
    return out_path

def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--spec", required=True); ap.add_argument("--out-dir", default="spreadsheets")
    ap.add_argument("--loop"); ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    with open(args.spec) as f: spec = yaml.safe_load(f)
    loops = spec.get("loops", [])
    if args.loop:
        loops = [lp for lp in loops if lp.get("name") == args.loop]
        if not loops:
            print(f"[FATAL] no loop named '{args.loop}'", file=sys.stderr); return 2
    out_dir = Path(args.out_dir); n = 0
    for lp in loops:
        if generate_xlsx_for_loop(lp, out_dir, verbose=args.verbose): n += 1
    print(f"[xlsxgen] generated {n}/{len(loops)} xlsx files in {out_dir}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
