#!/usr/bin/env python3
"""
validate_load_from_xml.py — verify a .psyexp with real PsychoPy (Layer 6).

Use this when validate_psyexp.py (lxml) passes but you suspect the
emitted XML has params PsychoPy doesn't recognize, or when you want
the gold-standard "would PsychoPy actually load this?" answer.

Usage:
    D:\\Software\\P\\python.exe scripts/validate_load_from_xml.py <file.psyexp>
    D:\\Software\\P\\python.exe scripts/validate_load_from_xml.py <file.psyexp> --strict
    D:\\Software\\P\\python.exe scripts/validate_load_from_xml.py <file1> <file2> ...

Exit codes:
    0  — all files loaded clean (zero "Parameters not known" warnings)
    1  — at least one file produced warnings
    2  — at least one file failed to load (exception, not warning)

This is what should run after every change to json2psyexp.js.
"""
import argparse
import logging
import sys
from pathlib import Path

# Capture PsychoPy's WARNING-level "Parameters not known" messages
# by promoting them to errors temporarily, then re-running.
def verify_one(path: Path, strict: bool = False) -> tuple[str, list[str]]:
    """Returns ('OK'|'WARN'|'FAIL', list_of_messages)."""
    from psychopy.experiment import Experiment  # noqa: F401  (import side-effect)
    msgs: list[str] = []
    warnings_list: list[str] = []

    # Hook 1: capture the standard logger warnings
    handler = _ListHandler(warnings_list)
    handler.setLevel(logging.WARNING)
    psy_log = logging.getLogger()
    psy_log.addHandler(handler)

    try:
        exp = Experiment()
        exp.loadFromXML(str(path))
    except Exception as e:  # loadFromXML may also raise Warning-as-exception
        msgs.append(f"  EXCEPTION: {type(e).__name__}: {e}")
        return ("FAIL", warnings_list + msgs)
    finally:
        psy_log.removeHandler(handler)

    if warnings_list:
        for w in warnings_list:
            msgs.append(f"  WARN: {w}")
        if strict:
            return ("WARN", warnings_list + msgs)
        return ("WARN", warnings_list + msgs)

    return ("OK", [])


class _ListHandler(logging.Handler):
    def __init__(self, sink: list[str]) -> None:
        super().__init__()
        self.sink = sink

    def emit(self, record: logging.LogRecord) -> None:
        try:
            msg = self.format(record)
        except Exception:
            msg = record.getMessage()
        self.sink.append(msg)


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("files", nargs="+", help="one or more .psyexp files to verify")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failure")
    args = ap.parse_args()

    overall = 0
    for fp in args.files:
        path = Path(fp).resolve()
        if not path.exists():
            print(f"[SKIP] {path} (not found)")
            continue
        status, msgs = verify_one(path, strict=args.strict)
        n = len(paths := [m for m in msgs if m.strip().startswith("WARN:")])
        print(f"[{status:4}] {path.name}  ({n} warning(s))")
        for m in msgs:
            print(m)
        if status == "WARN":
            overall = overall or 1
        elif status == "FAIL":
            overall = 2
    return overall


if __name__ == "__main__":
    sys.exit(main())
