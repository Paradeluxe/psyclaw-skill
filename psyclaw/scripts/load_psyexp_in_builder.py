#!/usr/bin/env python3
"""Launch PsychoPy Builder with hermes-agent site-packages stripped from sys.path.

Usage:
    load_psyexp_in_builder.py <path.psyexp>

Must be run with PsychoPy's python.exe (D:\\Software\\P\\python.exe).
"""
import sys, os

# Strip hermes-agent pollution from sys.path BEFORE importing psychopy
for p in (
    r"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Lib\site-packages",
    r"C:\Users\User\AppData\Local\hermes\hermes-agent\venv\Lib",
):
    while p in sys.path:
        sys.path.remove(p)

# Also strip from os.environ
for k in ("PYTHONPATH", "PYTHONHOME"):
    if k in os.environ:
        del os.environ[k]
os.environ["PYTHONNOUSERSITE"] = "1"

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
