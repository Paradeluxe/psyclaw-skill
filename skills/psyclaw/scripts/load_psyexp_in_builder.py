#!/usr/bin/env python3
"""Launch PsychoPy Builder with hermes-agent site-packages stripped from sys.path.

Usage:
    load_psyexp_in_builder.py <path.psyexp>

Must be run with PsychoPy's python.exe.
"""
import sys
from os import environ

# Strip hermes-agent pollution from sys.path BEFORE importing psychopy
for p in list(sys.path):
    norm = p.replace("\\", "/").lower()
    if "hermes-agent" in norm and "site-packages" in norm:
        while p in sys.path:
            sys.path.remove(p)
    elif "hermes-agent" in norm and norm.rstrip("/").endswith("/lib"):
        while p in sys.path:
            sys.path.remove(p)

# Clear interpreter override vars via environ mapping only
for k in ("PYTHONPATH", "PYTHONHOME"):
    environ.pop(k, None)
environ["PYTHONNOUSERSITE"] = "1"

from psychopy.experiment import Experiment
from psychopy.app import builder
import wx

psyexp_path = sys.argv[1] if len(sys.argv) > 1 else None

app = wx.App()
frame = builder.BuilderFrame(None, -1)
exp = Experiment()
if psyexp_path:
    exp.loadFromXML(psyexp_path)
    print(f"[loader] loaded {psyexp_path}")
    print(f"[loader] routines={len(exp.routines)} loops={len(exp.flow)}")
frame.exp = exp
frame.Show()
app.MainLoop()
