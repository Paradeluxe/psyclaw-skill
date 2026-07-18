#!/usr/bin/env python3
"""validate_psyexp.py — 5-layer lxml validator for .psyexp files."""
import os, sys
from pathlib import Path
from lxml import etree
if not hasattr(os, "add_dll_directory"): os.add_dll_directory = lambda x: None
REQUIRED = ["Settings", "Routines", "Flow"]
EXPECTED = ["KeyboardComponent","TextComponent","ImageComponent","AudioComponent","VideoComponent","CodeComponent","MouseComponent","SliderComponent"]
def main():
    p = Path(sys.argv[1])
    if not p.exists(): print(f"FATAL: {p} not found", file=sys.stderr); return 10
    print(f"=== Validating {p} ===")
    print(f"    size: {p.stat().st_size} bytes")
    try: tree = etree.parse(str(p))
    except etree.XMLSyntaxError as e: print(f"[L1] FAIL: {e}", file=sys.stderr); return 1
    # Also try with recover mode for forgiving parse (PsychoPy itself is more lenient)
    try: tree_recover = etree.parse(str(p), etree.XMLParser(recover=True))
    except Exception: tree_recover = tree
    root = tree.getroot()
    tag = root.tag.split("}",1)[-1] if "}" in root.tag else root.tag
    if tag != "PsychoPy2experiment": print(f"[L1] FAIL: root <{tag}>", file=sys.stderr); return 1
    print("[L1] OK")
    sections = {c.tag: c for c in root if c.tag in REQUIRED}
    miss = [s for s in REQUIRED if s not in sections]
    if miss: print(f"[L2] FAIL: missing {miss}", file=sys.stderr); return 2
    routines = list(sections["Routines"].findall("Routine"))
    flow = sections["Flow"]
    flow_children = [c for c in flow if c.tag != "Refresh"]
    if not routines: print("[L2] FAIL: 0 routines", file=sys.stderr); return 2
    if not flow_children: print("[L2] FAIL: empty flow", file=sys.stderr); return 2
    print(f"[L2] OK  Routines({len(routines)})/Flow({len(flow_children)})")
    bad = []
    for r in routines:
        n = r.get("name","?")
        cs = [c for c in r if c.tag in EXPECTED]
        if not cs: bad.append(n)
        else: print(f"    [routine] {n}: {len(cs)} ({[c.tag for c in cs]})")
    if bad: print(f"[L3] FAIL: empty {bad}", file=sys.stderr); return 3
    print(f"[L3] OK  all {len(routines)} routines have components")
    inits = flow.findall("LoopInitiator")
    terms = flow.findall("LoopTerminator")
    if len(inits) != len(terms): print(f"[L4] FAIL: loop init/term mismatch", file=sys.stderr); return 4
    rnames = {r.get("name") for r in routines}
    for li in inits:
        ln = li.get("name","?")
        for ref in [r.get("name") for r in li.findall("Routine")]:
            if ref not in rnames:
                print(f"[L4] FAIL: loop '{ln}' refs unknown '{ref}'", file=sys.stderr); return 4
    print(f"[L4] OK  {len(inits)} loops")
    n = 0; bad2 = []
    for r in routines:
        for c in r:
            if c.tag not in EXPECTED: continue
            for prm in c.findall("Param"):
                n += 1
                for k in ("val","valType","name"):
                    if k not in prm.attrib: bad2.append(f"{r.get('name')}/{c.tag}/{k}")
    if bad2: print(f"[L5] FAIL: param {bad2[:3]}", file=sys.stderr); return 5
    print(f"[L5] OK  {n} params valid")
    print("=== ALL PASS ===")
    return 0
main()
