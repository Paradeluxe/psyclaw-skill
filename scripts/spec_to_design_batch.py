"""spec.yaml (cat1/2/3 replications) → design.json → design_compiler syntax check."""
from __future__ import annotations

import ast
import json
import re
import sys
import traceback
from collections import Counter
from pathlib import Path

try:
    import yaml
except ImportError:
    import subprocess

    subprocess.check_call([sys.executable, "-m", "pip", "install", "pyyaml", "-q"])
    import yaml

PSYCLAW = Path(r"E:/hermes_playground/psyclaw")
REPS = PSYCLAW / "replications"
OUT = PSYCLAW / "output" / "webui_batch_validate"
OUT.mkdir(parents=True, exist_ok=True)
WEBUI = Path(r"E:/hermes_playground/psyclaw-webui")
sys.path.insert(0, str(WEBUI / "backend"))
from design_compiler import compile_design  # noqa: E402


def safe_name(s: str) -> str:
    s = re.sub(r"[^A-Za-z0-9_]+", "_", str(s or "x")).strip("_")
    return s or "x"


def keys_str(keys) -> str:
    if keys is None:
        return "space"
    if isinstance(keys, dict):
        keys = list(keys.keys())
    if isinstance(keys, (list, tuple)):
        return ",".join(str(k) for k in keys) if keys else "space"
    return str(keys)


def cond_rows(spec: dict) -> list:
    c = spec.get("conditions") or {}
    if isinstance(c, dict) and "rows" in c:
        rows = c.get("rows") or []
        out = []
        for r in rows:
            if not isinstance(r, dict):
                continue
            row = dict(r)
            if "correct_resp" in row and "corrAns" not in row:
                row["corrAns"] = row["correct_resp"]
            if "correct_key" in row and "corrAns" not in row:
                row["corrAns"] = row["correct_key"]
            out.append(row)
        return out
    if isinstance(c, dict) and c and "columns" not in c:
        rows = []
        for name, params in c.items():
            if isinstance(params, dict):
                row = {"condition": name, **params}
            else:
                row = {"condition": name, "value": params}
            rows.append(row)
        return rows
    return [{"_dummy": 1}]


def map_comp(raw: dict, idx: int, start: float, dur) -> dict:
    typ = str(raw.get("type") or "text").lower()
    name = safe_name(raw.get("name") or f"{typ}_{idx}")
    c_dur = raw.get("duration", dur)
    if c_dur is None or c_dur == "" or c_dur == "inf":
        c_dur = -1
    try:
        c_dur = float(c_dur)
    except Exception:
        c_dur = -1
    params = {}
    if typ in ("text", "textbox"):
        typ = "text"
        params["text"] = raw.get("text", "+")
        if "height" in raw:
            params["height"] = raw["height"]
        if "color" in raw:
            params["color"] = raw["color"]
        if "pos" in raw:
            params["pos"] = raw["pos"]
    elif typ in ("keyboard", "key", "keys"):
        typ = "keyboard"
        params["keys"] = keys_str(raw.get("keys") or raw.get("allowed") or "space")
        params["force_end"] = bool(raw.get("force_end", True))
        if raw.get("correct_ans") is not None:
            params["correct_ans"] = raw.get("correct_ans")
        if raw.get("store") or raw.get("until_response"):
            if c_dur is None or c_dur == 0:
                c_dur = -1
    elif typ in ("image", "img"):
        typ = "image"
        params["path"] = raw.get("path") or raw.get("image") or raw.get("file") or ""
        if "size" in raw:
            params["size"] = raw["size"]
    elif typ in ("sound", "audio"):
        typ = "sound"
        params["path"] = raw.get("path") or raw.get("file") or ""
    elif typ in ("video", "movie"):
        typ = "video"
        params["path"] = raw.get("path") or raw.get("file") or ""
    elif typ in ("rect", "polygon", "shape"):
        typ = "rect"
        params["size"] = raw.get("size", [0.2, 0.2])
        if "color" in raw or "fillColor" in raw:
            params["color"] = raw.get("color") or raw.get("fillColor")
    elif typ == "code":
        params["code"] = raw.get("code") or raw.get("text") or ""
    else:
        params["text"] = f"[{typ}]"
        typ = "text"
    return {
        "id": f"c_{name}_{idx}",
        "type": typ,
        "name": name,
        "start": float(raw.get("start") or start or 0),
        "duration": c_dur if c_dur is not None else -1,
        "params": params,
    }


def timeline_to_routines(spec: dict):
    routines = []
    trial_names = []
    instr = spec.get("instructions") or "Press SPACE to start."
    routines.append(
        {
            "name": "instructions",
            "components": [
                {
                    "id": "c_instr_text",
                    "type": "text",
                    "name": "instr_text",
                    "start": 0,
                    "duration": -1,
                    "params": {"text": str(instr), "height": 0.04, "color": "white"},
                },
                {
                    "id": "c_instr_kb",
                    "type": "keyboard",
                    "name": "instr_kb",
                    "start": 0,
                    "duration": -1,
                    "params": {"keys": "space", "force_end": True},
                },
            ],
        }
    )
    tl = spec.get("timeline") or []
    if not tl and spec.get("routines"):
        for r in spec["routines"]:
            rname = safe_name(r.get("name") or "routine")
            comps = []
            for i, c in enumerate(r.get("components") or []):
                comps.append(
                    map_comp(c, i, c.get("start") or 0, c.get("duration", r.get("duration")))
                )
            if not comps:
                comps = [
                    {
                        "id": f"c_{rname}_t",
                        "type": "text",
                        "name": f"{rname}_t",
                        "start": 0,
                        "duration": float(r.get("duration") or 1),
                        "params": {"text": rname, "color": "white"},
                    }
                ]
            routines.append({"name": rname, "components": comps})
            if rname not in ("instructions", "thanks"):
                trial_names.append(rname)
    else:
        for i, phase in enumerate(tl):
            if not isinstance(phase, dict):
                continue
            rname = safe_name(phase.get("name") or f"phase_{i}")
            dur = phase.get("duration")
            if dur is None:
                dur = -1
            try:
                dur = float(dur)
            except Exception:
                dur = -1
            comps_raw = phase.get("components") or []
            comps = []
            for j, c in enumerate(comps_raw):
                comps.append(map_comp(c, j, 0, dur if dur != -1 else -1))
            if not comps:
                comps = [
                    {
                        "id": f"c_{rname}_t",
                        "type": "text",
                        "name": f"{rname}_t",
                        "start": 0,
                        "duration": dur if dur != -1 else 1.0,
                        "params": {"text": rname, "color": "white"},
                    }
                ]
            base = rname
            n = 2
            existing = {r["name"] for r in routines}
            while rname in existing:
                rname = f"{base}_{n}"
                n += 1
            routines.append({"name": rname, "components": comps})
            trial_names.append(rname)

    thanks = spec.get("thanks") or "Thank you.\n\nPress any key to exit."
    routines.append(
        {
            "name": "thanks",
            "components": [
                {
                    "id": "c_thanks_text",
                    "type": "text",
                    "name": "thanks_text",
                    "start": 0,
                    "duration": -1,
                    "params": {"text": str(thanks), "height": 0.04, "color": "white"},
                },
                {
                    "id": "c_thanks_kb",
                    "type": "keyboard",
                    "name": "thanks_kb",
                    "start": 0,
                    "duration": -1,
                    "params": {"keys": "space", "force_end": True},
                },
            ],
        }
    )
    return routines, trial_names


def spec_to_design(spec: dict, name: str, project_dir: str) -> dict:
    routines, trial_names = timeline_to_routines(spec)
    rows = cond_rows(spec)
    n_reps = 1
    loops = spec.get("loops") or []
    if loops and isinstance(loops[0], dict):
        n_reps = int(loops[0].get("n_rounds") or loops[0].get("nReps") or 1)
    children = [{"kind": "routine", "routine": n} for n in trial_names] or [
        {"kind": "routine", "routine": "trial"}
    ]
    flow = [
        {"kind": "routine", "routine": "instructions"},
        {
            "kind": "loop",
            "name": "trials",
            "nReps": n_reps,
            "loopType": "random",
            "conditions": rows,
            "conditionsFile": "",
            "children": children,
        },
        {"kind": "routine", "routine": "thanks"},
    ]
    return {
        "_meta": {
            "format": "psyclaw-design",
            "version": 1,
            "fileName": "design.psyexp",
            "projectDir": project_dir,
            "source": "spec.yaml->webui design",
            "paradigm": spec.get("paradigm") or name,
        },
        "name": name,
        "display": {
            "size": [1024, 768],
            "fullscreen": False,
            "screen": 0,
            "bgcolor": "#000000",
        },
        "devices": {"keyboard": True, "microphone": False, "speaker": False},
        "routines": routines,
        "flow": flow,
    }


def check_compile(design: dict) -> tuple[bool, str]:
    try:
        src = compile_design(
            design, session={"participant_id": "P_pilot", "session": "1"}
        )
        ast.parse(src)
        if "visual.Window" not in src and "Window(" not in src:
            return False, "no Window in script"
        if len(src) < 500:
            return False, f"script too short ({len(src)})"
        return True, f"ok bytes={len(src)}"
    except SyntaxError as e:
        return False, f"SyntaxError: {e}"
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def main() -> None:
    results = []
    for cat in ("cat1", "cat2", "cat3"):
        dirs = sorted(REPS.glob(f"{cat}_*"))
        for d in dirs:
            spec_path = d / "spec.yaml"
            item = {"dir": d.name, "cat": cat, "status": "?", "detail": ""}
            if not spec_path.exists():
                item["status"] = "no_spec"
                results.append(item)
                continue
            try:
                spec = yaml.safe_load(spec_path.read_text(encoding="utf-8")) or {}
            except Exception as e:
                item["status"] = "yaml_fail"
                item["detail"] = str(e)
                results.append(item)
                continue
            name = d.name
            try:
                design = spec_to_design(spec, name, str(d.resolve()))
                des_path = d / "design.psyexp"
                des_path.write_text(
                    json.dumps(design, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                (OUT / f"{name}.design.json").write_text(
                    json.dumps(design, ensure_ascii=False, indent=2), encoding="utf-8"
                )
                ok, detail = check_compile(design)
                item["status"] = "ok" if ok else "compile_fail"
                item["detail"] = detail
                item["n_routines"] = len(design["routines"])
                item["n_cond"] = len(design["flow"][1].get("conditions") or [])
                item["types"] = sorted(
                    {c["type"] for r in design["routines"] for c in r["components"]}
                )
            except Exception as e:
                item["status"] = "convert_fail"
                item["detail"] = f"{type(e).__name__}: {e}"
                item["trace"] = traceback.format_exc()[-400:]
            results.append(item)

    ctr = Counter(r["status"] for r in results)
    by_cat = {}
    for r in results:
        by_cat.setdefault(r["cat"], Counter())[r["status"]] += 1

    summary = {
        "total": len(results),
        "status_counts": dict(ctr),
        "by_cat": {k: dict(v) for k, v in by_cat.items()},
        "fails": [r for r in results if r["status"] != "ok"][:40],
    }
    (OUT / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (OUT / "results.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print("TOTAL", len(results))
    print("STATUS", dict(ctr))
    for cat, c in by_cat.items():
        print(cat, dict(c), "ok", c.get("ok", 0), "/", sum(c.values()))
    if summary["fails"]:
        print("FAILS sample:")
        for f in summary["fails"][:15]:
            print(" ", f["dir"], f["status"], str(f.get("detail", ""))[:120])
    print("OUT", OUT)


if __name__ == "__main__":
    main()
