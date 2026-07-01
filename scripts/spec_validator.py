#!/usr/bin/env python3
"""spec_validator.py — Validate an ExperimentDesign YAML file."""
import argparse, json, sys
from pathlib import Path
from collections import Counter

VALID_COMPONENT_TYPES = {"text", "image", "audio", "video", "keyboard", "mouse", "slider", "code"}
VALID_STIMULUS_KINDS = {"text", "image", "audio", "video"}
VALID_LOOP_ORDERS = {"sequential", "random", "fullRandom"}

class ValidationError:
    def __init__(self, path, message, severity="error"):
        self.path = path; self.message = message; self.severity = severity
    def __str__(self):
        marker = "ERROR" if self.severity == "error" else "WARN"
        return f"[{marker}] {self.path}: {self.message}" if self.path else f"[{marker}] {self.message}"

def validate_spec(spec):
    errors = []; warnings = []
    if not isinstance(spec, dict):
        errors.append(ValidationError("", "spec must be a YAML mapping")); return errors, warnings
    if "name" not in spec:
        errors.append(ValidationError("name", "required field missing"))
    elif not isinstance(spec["name"], str):
        errors.append(ValidationError("name", f"must be string, got {type(spec['name']).__name__}"))
    if "routines" not in spec:
        errors.append(ValidationError("routines", "required field missing"))
    elif not isinstance(spec["routines"], list):
        errors.append(ValidationError("routines", "must be list"))
    elif len(spec["routines"]) == 0:
        errors.append(ValidationError("routines", "must have at least 1 routine"))
    if isinstance(spec.get("routines"), list):
        routine_names = []
        for i, r in enumerate(spec["routines"]):
            rpath = f"routines[{i}]"
            if not isinstance(r, dict):
                errors.append(ValidationError(rpath, "must be mapping")); continue
            rname = r.get("name")
            if not rname: errors.append(ValidationError(f"{rpath}.name", "required"))
            elif rname in routine_names: errors.append(ValidationError(f"{rpath}.name", f"duplicate '{rname}'"))
            else: routine_names.append(rname)
            comps = r.get("components", [])
            if not isinstance(comps, list):
                errors.append(ValidationError(f"{rpath}.components", "must be a list"))
            elif len(comps) == 0:
                warnings.append(ValidationError(f"{rpath}.components", "empty component list", "warning"))
            else:
                for j, c in enumerate(comps):
                    cpath = f"{rpath}.components[{j}]"
                    if not isinstance(c, dict):
                        errors.append(ValidationError(cpath, "must be mapping")); continue
                    ctype = c.get("type")
                    if not ctype: errors.append(ValidationError(f"{cpath}.type", "required"))
                    elif ctype not in VALID_COMPONENT_TYPES:
                        errors.append(ValidationError(f"{cpath}.type", f"unknown type '{ctype}'. Valid: {sorted(VALID_COMPONENT_TYPES)}"))
                    elif ctype == "text" and "text" not in c: errors.append(ValidationError(cpath, "type='text' requires 'text'"))
                    elif ctype == "image" and "path" not in c: errors.append(ValidationError(cpath, "type='image' requires 'path'"))
                    elif ctype in ("audio", "video") and "path" not in c: errors.append(ValidationError(cpath, f"type='{ctype}' requires 'path'"))
                    elif ctype == "keyboard" and "keys" not in c: errors.append(ValidationError(cpath, "type='keyboard' requires 'keys'"))
    if isinstance(spec.get("loops"), list):
        for i, lp in enumerate(spec["loops"]):
            lpath = f"loops[{i}]"
            if not isinstance(lp, dict): errors.append(ValidationError(lpath, "must be mapping")); continue
            if "name" not in lp: errors.append(ValidationError(f"{lpath}.name", "required"))
            if "start_routine" not in lp: errors.append(ValidationError(f"{lpath}.start_routine", "required"))
            if "end_routine" not in lp: errors.append(ValidationError(f"{lpath}.end_routine", "required"))
            if "start_routine" in lp and "end_routine" in lp:
                start = lp["start_routine"]; end = lp["end_routine"]
                if isinstance(spec.get("routines"), list):
                    rnames = [r.get("name") for r in spec["routines"] if isinstance(r, dict)]
                    if start not in rnames: errors.append(ValidationError(f"{lpath}.start_routine", f"'{start}' not in routines"))
                    if end not in rnames: errors.append(ValidationError(f"{lpath}.end_routine", f"'{end}' not in routines"))
                    if start in rnames and end in rnames and rnames.index(end) < rnames.index(start):
                        errors.append(ValidationError(f"{lpath}.end_routine", f"end_routine '{end}' must come after start_routine '{start}'"))
            if "n_rounds" in lp and not isinstance(lp["n_rounds"], int):
                errors.append(ValidationError(f"{lpath}.n_rounds", f"must be int"))
            elif "n_rounds" in lp and lp["n_rounds"] < 1:
                errors.append(ValidationError(f"{lpath}.n_rounds", "must be >= 1"))
            if "order" in lp and lp["order"] not in VALID_LOOP_ORDERS:
                errors.append(ValidationError(f"{lpath}.order", f"must be one of {sorted(VALID_LOOP_ORDERS)}"))
    if isinstance(spec.get("stimuli"), list):
        stim_ids = []
        for i, s in enumerate(spec["stimuli"]):
            spath = f"stimuli[{i}]"
            if not isinstance(s, dict): errors.append(ValidationError(spath, "must be mapping")); continue
            sid = s.get("id")
            if not sid: errors.append(ValidationError(f"{spath}.id", "required"))
            elif sid in stim_ids: errors.append(ValidationError(f"{spath}.id", f"duplicate id '{sid}'"))
            else: stim_ids.append(sid)
            kind = s.get("kind")
            if not kind: errors.append(ValidationError(f"{spath}.kind", "required"))
            elif kind not in VALID_STIMULUS_KINDS:
                errors.append(ValidationError(f"{spath}.kind", f"must be one of {sorted(VALID_STIMULUS_KINDS)}"))
    return errors, warnings

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec"); ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"[FATAL] file not found: {spec_path}", file=sys.stderr); return 10
    try: import yaml
    except ImportError:
        print("[FATAL] PyYAML required", file=sys.stderr); return 11
    try:
        with open(spec_path) as f: spec = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"[FATAL] YAML parse error: {e}", file=sys.stderr); return 1
    errors, warnings = validate_spec(spec)
    print(f"=== Validating {spec_path} ===")
    if args.verbose:
        print(f"  name: {spec.get('name', '<missing>')}")
        print(f"  routines: {len(spec.get('routines', []))}")
        print(f"  loops: {len(spec.get('loops', []))}")
        print(f"  stimuli: {len(spec.get('stimuli', []))}")
    for w in warnings: print(f"  {w}")
    if errors:
        for e in errors: print(f"  {e}", file=sys.stderr)
        print(f"=== VALIDATION FAILED ({len(errors)} error(s), {len(warnings)} warning(s)) ===", file=sys.stderr)
        return 2
    print("=== VALID ==="); return 0

if __name__ == "__main__":
    sys.exit(main())
