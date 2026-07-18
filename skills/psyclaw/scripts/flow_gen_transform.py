#!/usr/bin/env python3
"""
flow_gen_transform.py — Convert ExperimentDesign YAML → flowchart JSON.

Output: {routines, loops}, consumed by json2psyexp.js.

Loop Point convention (verified from json2psyexp.js line 754):
  Point = (routineIndex + 1) * 2
  → routine 0 → Point 2, routine 1 → Point 4, ...
  json2psyexp.js computes:
    startRoutineIndex = floor(firstPoint / 2) - 1
    endRoutineIndex   = floor(lastPoint  / 2) - 1
"""
import argparse, json, sys
from pathlib import Path

COMPONENT_KEY_MAP = {
    "type": "type", "name": "name", "text": "text",
    "color": "color", "font": "font",
    "height": "letterHeight", "letterHeight": "letterHeight",
    "pos": "pos", "size": "size", "ori": "ori", "opacity": "opacity",
    "path": "path", "volume": "volume", "loop": "loop",
    "keys": "keys",
    "force_end": "forceEndRoutine", "forceEndRoutine": "forceEndRoutine",
    "duration": "duration", "store": "store",
    "correct_ans": "correctAns", "correctAns": "correctAns",
    "register_on": "registerOn", "registerOn": "registerOn",
    "discard_previous": "discard previous",
    "units": "units",
    "wrap_width": "wrapWidth", "wrapWidth": "wrapWidth",
    "languageStyle": "languageStyle",
    "italic": "italic", "bold": "bold",
    "flip": "flip", "flipVert": "flipVert", "flipHoriz": "flipHoriz",
    "anchor": "anchor", "contrast": "contrast", "interpolate": "interpolate",
    "no_audio": "No audio", "backend": "backend",
    "deviceLabel": "deviceLabel", "syncScreenRefresh": "syncScreenRefresh",
    "forceEndOnClick": "forceEndOnClick", "forceEndOnTimeout": "forceEndOnTimeout",
}
LOOP_KEY_MAP = {
    "name": "name", "n_rounds": "nRounds", "nRounds": "nRounds",
    "order": "type", "type": "type", "is_trials": "isTrials", "isTrials": "isTrials",
    "conditions": "conditions",
}
ORDER_TO_LOOPTYPE = {"sequential": "sequential", "random": "random", "fullRandom": "fullRandom"}

def remap_keys(d, key_map):
    if not isinstance(d, dict): return d
    out = {}
    for k, v in d.items():
        new_k = key_map.get(k, k)
        out[new_k] = remap_keys(v, key_map) if isinstance(v, (dict, list)) else v
    return out

def routine_to_point(routine_index):
    return (routine_index + 1) * 2

def transform_component(c, default_name=None):
    if not isinstance(c, dict): return c
    out = remap_keys(c, COMPONENT_KEY_MAP)
    if "name" not in out and "type" in out:
        out["name"] = f"{out['type']}_{default_name or 'comp'}"
    return out

def transform_routine(r):
    name = r.get("name", "routine")
    out = {"name": name, "components": [transform_component(c, default_name=name) for c in r.get("components", [])]}
    if "duration" in r: out["duration"] = r["duration"]
    return out

def transform_loop(loop, routine_index_by_name):
    start_name = loop.get("start_routine"); end_name = loop.get("end_routine")
    if start_name not in routine_index_by_name:
        raise ValueError(f"loop '{loop.get('name')}': start_routine '{start_name}' not in routines")
    if end_name not in routine_index_by_name:
        raise ValueError(f"loop '{loop.get('name')}': end_routine '{end_name}' not in routines")
    start_idx = routine_index_by_name[start_name]; end_idx = routine_index_by_name[end_name]
    if end_idx < start_idx:
        raise ValueError(f"loop '{loop.get('name')}': end '{end_name}' before start '{start_name}'")
    body_indices = list(range(start_idx, end_idx + 1))
    body_points = [routine_to_point(i) for i in body_indices]
    out = {
        "name": loop.get("name", "loop"),
        "nRounds": loop.get("n_rounds", 1),
        "type": ORDER_TO_LOOPTYPE.get(loop.get("order", "sequential"), "sequential"),
        "isTrials": bool(loop.get("is_trials", False)),
        "conditions": "",
        "list": [{"Point": p} for p in body_points],
    }
    if "spreadsheet" in loop:
        ss = loop["spreadsheet"]
        if "file" in ss: out["conditionsFile"] = ss["file"]
        if "rows" in ss and ss["rows"]:
            rows = ss["rows"]; cols = [c["name"] for c in ss.get("columns", [])] if "columns" in ss else []
            new_list = []
            for i, p in enumerate(body_points):
                row_idx = i % len(rows) if len(rows) > 0 else 0
                row = rows[row_idx] if rows else {}
                item = {"Point": p}
                if cols:
                    for c in cols: item[c] = row.get(c, "")
                else:
                    item.update(row)
                new_list.append(item)
            out["list"] = new_list
    return out

def transform_spec(spec):
    routines_in = spec.get("routines", []); loops_in = spec.get("loops", [])
    routine_index_by_name = {r["name"]: i for i, r in enumerate(routines_in) if "name" in r}
    routines_out = [transform_routine(r) for r in routines_in]
    loops_out = []
    for lp in loops_in:
        loops_out.append(transform_loop(lp, routine_index_by_name))
    return {"routines": routines_out, "loops": loops_out}

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec"); ap.add_argument("output", nargs="?")
    ap.add_argument("--verbose", "-v", action="store_true")
    args = ap.parse_args()
    spec_path = Path(args.spec)
    if not spec_path.exists():
        print(f"[FATAL] not found: {spec_path}", file=sys.stderr); return 1
    try: import yaml
    except ImportError:
        print("[FATAL] PyYAML required", file=sys.stderr); return 1
    with open(spec_path) as f: spec = yaml.safe_load(f)
    try: flowchart = transform_spec(spec)
    except ValueError as e:
        print(f"[FATAL] transform failed: {e}", file=sys.stderr); return 2
    out_path = Path(args.output) if args.output else Path(spec.get("name", "output") + ".flowchart.json")
    with open(out_path, "w") as f: json.dump(flowchart, f, indent=2, ensure_ascii=False)
    if args.verbose:
        print(f"input routines: {len(spec.get('routines', []))}, loops: {len(spec.get('loops', []))}")
        for r in flowchart["routines"]:
            print(f"  routine {r['name']}: {len(r['components'])} components")
        for lp in flowchart["loops"]:
            pts = [it['Point'] for it in lp.get('list', [])]
            print(f"  loop {lp['name']}: nRounds={lp['nRounds']}, Points {pts}, isTrials={lp['isTrials']}")
    print(f"OK  {spec_path} -> {out_path}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
