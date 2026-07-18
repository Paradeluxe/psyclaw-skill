"""frames_viz.py -- replay frame JSON dumps as ASCII + matplotlib timeline.

Frames are written by ``run_psyexp.py`` when ``PSYCLAW_FRAME_LOG=1``.
Each frame is one JSON file with this shape:

    {
      "frame_id": 1700000000000,
      "routines": [
        {
          "name": "trial",
          "frame_index": 14,
          "forceEnded": false,
          "thisN": 3, "thisTrialN": 3, "thisRepN": 0,
          "components": [
            {"name": "trial_text_0", "type": "TextComponent",
             "status": "STARTED", "text": "RED",
             "pos": [0, 0], "size": null},
            {"name": "trial_keyboard_1", "type": "KeyboardComponent",
             "status": "STARTED"},
          ],
        },
      ],
    }

Usage:
    python scripts/frames_viz.py <frames_dir>          # ASCII timeline
    python scripts/frames_viz.py <frames_dir> --png out.png   # matplotlib
    python scripts/frames_viz.py <frames_dir> --frame 23      # single-frame dump
    python scripts/frames_viz.py <frames_dir> --list          # list frame indices

The ASCII timeline gives one column per frame, one row per routine,
with text characters used as a one-letter-per-status glyph. It's
density-tuned for a terminal so a 60-frame sequence fits on screen.

Companion reference: ``references/frame-recorder.md``.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def _load_frames(frames_dir: Path) -> list[tuple[int, dict]]:
    """Read every frame JSON in sort order.

    Returns list of (file_index, snapshot). file_index is the
    position in the directory (0-based) -- useful when multiple frames
    share the same ms frame_id (i.e. a fast headless loop).
    """
    if not frames_dir.is_dir():
        sys.exit(f"frames dir not found: {frames_dir}")
    files = sorted(p for p in frames_dir.glob("frame_*.json"))
    out = []
    for i, fp in enumerate(files):
        try:
            snap = json.loads(fp.read_text(encoding="utf-8"))
        except Exception as e:
            print(f"warn: failed to parse {fp}: {e}", file=sys.stderr)
            continue
        out.append((i, snap))
    return out


def _glyph_for(comp: dict) -> str:
    """One-letter status for the ASCII timeline."""
    s = str(comp.get("status", "?")).upper()
    if s in ("NOT_STARTED", "0", None):
        return "."
    if s in ("STARTED", "1", "START", "PLAYING"):
        return "#"
    if s in ("FINISHED", "2", "DONE"):
        return "x"
    return "?"


def _ascii_timeline(frames: list[tuple[int, dict]]) -> str:
    """Print a terminal-friendly frame timeline.

    Each row: <time_sec>   <frame_idx>  <routine>  <glyphs>
    """
    if not frames:
        return "(no frames)"
    out = []
    out.append(f"frames: {len(frames)}  first_ms={frames[0][1].get('frame_id')}  "
               f"last_ms={frames[-1][1].get('frame_id')}")
    out.append("")

    rows: dict[str, list[tuple[int, dict]]] = {}
    for fi, snap in frames:
        for r in snap.get("routines", []):
            rows.setdefault(r.get("name", "?"), []).append((fi, r))

    base_ms = frames[0][1].get("frame_id", 0)
    stride = max(1, len(frames) // 80)

    for rname, occurrences in rows.items():
        sample = occurrences[0][1]
        comp_names = [c.get("name", "?") for c in sample.get("components", [])]
        per_comp: list[dict[int, str]] = [{} for _ in comp_names]
        for fi, r in occurrences:
            comps = r.get("components", [])
            for ci, comp in enumerate(comps):
                if ci >= len(per_comp):
                    continue
                per_comp[ci][fi] = _glyph_for(comp)
        first_text: list[str] = [""] * len(comp_names)
        for fi, r in occurrences:
            comps = r.get("components", [])
            for ci, comp in enumerate(comps):
                if ci < len(first_text) and not first_text[ci] and comp.get("text"):
                    first_text[ci] = repr(comp.get("text", ""))[:20]
        row_label_w = max(len(n) for n in comp_names) if comp_names else 0
        out.append(f"  routine: {rname}")
        for ci, cname in enumerate(comp_names):
            label = f"    {cname:<{row_label_w}} "
            series = "".join(per_comp[ci].get(fi, " ")
                              for fi in range(0, len(frames), stride))
            t_info = f"  '{first_text[ci]}'" if first_text[ci] else ""
            out.append(f"{label}|{series}|{t_info}")
        out.append("")

    header = "  frame#  "
    for fi in range(0, len(frames), stride):
        header += f"{fi:<3d}"[1:]
    out.append("=" * 60)
    out.append(header)
    out.append("=" * 60)
    return "\n".join(out)


def _frame_dump(frames: list[tuple[int, dict]], idx: int) -> str:
    """Pretty-print a single frame's snapshot."""
    if idx < 0 or idx >= len(frames):
        return f"frame index out of range 0..{len(frames) - 1}"
    fi, snap = frames[idx]
    lines = [f"== frame #{fi} (file_idx={idx}) ==",
             f"frame_id (ms): {snap.get('frame_id')}",
             "routines:"]
    for r in snap.get("routines", []):
        lines.append(f"  - {r.get('name')!r} frame_index={r.get('frame_index')} "
                     f"forceEnded={r.get('forceEnded')} "
                     f"thisN={r.get('thisN')} thisTrialN={r.get('thisTrialN')} "
                     f"thisRepN={r.get('thisRepN')}")
        for c in r.get("components", []):
            txt = repr(c.get("text", "")).strip("'\"") if c.get("text") else ""
            rating = f" rating={c.get('rating')}" if "rating" in c else ""
            pos = f" pos={c.get('pos')}" if c.get("pos") else ""
            size = f" size={c.get('size')}" if c.get("size") else ""
            lines.append(f"      {c.get('name')!r} ({c.get('type')}) "
                         f"status={c.get('status')}{rating} "
                         f"text={txt!r}{pos}{size}")
    return "\n".join(lines)


def _png_timeline(frames: list[tuple[int, dict]], outpath: Path) -> None:
    """Render an annotated strip per component showing when it was
    STARTED (#) / FINISHED (x) / inert (.).

    Each routine gets its own row band; each component is a sub-row
    showing its status glyph per frame. Color-coded: green=STARTED,
    gray=FINISHED, white=NOT_STARTED.
    """
    import matplotlib
    matplotlib.use("Agg")  # non-interactive backend
    import matplotlib.pyplot as plt

    if not frames:
        sys.exit("no frames to plot")

    flat: list[tuple[str, list[tuple[int, str]]]] = []
    for fi, snap in frames:
        for r in snap.get("routines", []):
            for ci, comp in enumerate(r.get("components", [])):
                cn = comp.get("name", "?")
                flat.append((f"{r.get('name', '?')}.{cn}",
                             [(fi, _glyph_for(comp))]))

    fig, ax = plt.subplots(figsize=(max(8, len(frames) / 5),
                                    max(4, len(flat) * 0.3)))
    ax.set_xlim(0, max(len(frames), 1))
    ax.set_ylim(-0.5, len(flat) - 0.5)
    ax.set_yticks(range(len(flat)))
    ax.set_yticklabels([n for n, _ in flat], fontsize=7)
    ax.set_xlabel("frame index")
    ax.set_title("PsychoPy routine state timeline "
                 "(. NOT_STARTED, # STARTED, x FINISHED)")
    cmap = {".": "#ffffff", "#": "#33aa33", "x": "#666666", "?": "#cc0000"}
    for ri, (_, series) in enumerate(flat):
        for fi, g in series:
            ax.add_patch(plt.Rectangle((fi - 0.5, ri - 0.5), 1, 1,
                                       color=cmap.get(g, "#ffffff"),
                                       ec="none"))
            ax.text(fi, ri, g, ha="center", va="center", fontsize=5)
    plt.tight_layout()
    plt.savefig(outpath, dpi=120)
    print(f"wrote {outpath}", file=sys.stderr)


def main() -> int:
    p = argparse.ArgumentParser(description="Replay frame JSON dumps.")
    p.add_argument("frames_dir", type=Path,
                   help="Directory containing frame_*.json files.")
    p.add_argument("--png", type=Path, default=None,
                   help="Render a matplotlib PNG instead of ASCII.")
    p.add_argument("--frame", type=int, default=-1,
                   help="Show a single frame's full JSON (instead of "
                        "the timeline).")
    p.add_argument("--list", action="store_true",
                   help="List frame indices and frame_id only.")
    args = p.parse_args()

    frames = _load_frames(args.frames_dir)
    if not frames:
        print("no frames found", file=sys.stderr)
        return 1

    if args.list:
        for fi, snap in frames:
            print(f"{fi:5d}  {snap.get('frame_id')}")
        return 0

    if args.frame >= 0:
        print(_frame_dump(frames, args.frame))
        return 0

    if args.png:
        _png_timeline(frames, args.png)
        return 0

    print(_ascii_timeline(frames))
    return 0


if __name__ == "__main__":
    sys.exit(main())
