#!/usr/bin/env python3
"""nl_intake.py — Natural language → ExperimentDesign YAML (template-based)."""
import argparse
import re
import sys
from pathlib import Path

PARADIGM_KEYWORDS = {
    "stroop": ["stroop", "斯特鲁普", "色词", "颜色冲突", "color word"],
    "go-no-go": ["go-no-go", "gonogo", "go/nogo", "go no go", "抑制任务", "反应抑制", "gng"],
    "flanker": ["flanker", "侧抑制", "箭头干扰", "eriksen"],
    "n-back": ["n-back", "nback", "n back", "工作记忆", "working memory"],
    "iaps": ["iaps", "情绪图片", "情绪评估", "emotion", "情绪调节"],
    "posner": ["posner", "cueing", "提示线索", "空间注意", "spatial attention"],
    "oddball": ["oddball", "odd ball", "odd-ball", "odd球", "新异刺激"],
    "dot-probe": ["dot-probe", "dot probe", "点探测", "注意偏向", "attentional bias"],
    "antisaccade": ["antisaccade", "anti-saccade", "反向眼跳", "anti saccade"],
}

def detect_paradigm(text):
    text_lower = text.lower()
    normalized = re.sub(r"[/\-]+", " ", text_lower)
    normalized = re.sub(r"\s+", " ", normalized)
    for paradigm, keywords in PARADIGM_KEYWORDS.items():
        for kw in keywords:
            if kw.lower() in normalized: return paradigm
    return None

def extract_n(text, default=30):
    m = re.search(r"(\d+)\s*(?:trials?|个\s*trial|次|轮|个刺激|个试次)", text, re.IGNORECASE)
    return int(m.group(1)) if m else default

def extract_n_back(text, default=2):
    m = re.search(r"(\d+)[\-\s]?back", text, re.IGNORECASE)
    return int(m.group(1)) if m else default

def get_template_dir():
    return Path(__file__).parent.parent / "templates"

def render_template(paradigm, **kwargs):
    template_path = get_template_dir() / f"{paradigm}.yaml.tmpl"
    if not template_path.exists(): return None
    template = template_path.read_text()
    for k, v in kwargs.items():
        template = template.replace("{" + k + "}", str(v))
    return template

def generic_spec(text):
    name = re.sub(r"[^a-z0-9]+", "_", text.lower())[:40].strip("_") or "experiment"
    return f"""name: {name}
version: "1.0"
description: |
  {text}

routines:
  - name: instructions
    duration: null
    components:
      - type: text
        text: "{text}"
        height: 0.05
      - type: keyboard
        keys: space
        duration: -1
        force_end: true
  - name: trial
    duration: 2.0
    components:
      - type: text
        text: "Trial"
        height: 0.08
      - type: keyboard
        keys: space
        duration: 2.0
  - name: thanks
    duration: 3.0
    components:
      - type: text
        text: "Thanks!"
        height: 0.05

loops: []
"""

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--input", "-i"); ap.add_argument("--output", "-o", default="experiment_spec.yaml")
    ap.add_argument("--n-trials", type=int); ap.add_argument("--n-back", type=int)
    ap.add_argument("--paradigm"); ap.add_argument("--list-paradigms", action="store_true")
    args = ap.parse_args()
    if args.list_paradigms:
        print("Known paradigms:")
        for p in sorted(set(PARADIGM_KEYWORDS.keys())):
            kws = ", ".join(PARADIGM_KEYWORDS[p])
            print(f"  {p:10} — keywords: {kws}")
        return 0
    if not args.input:
        print("[FATAL] provide --input", file=sys.stderr); return 1
    text = args.input
    paradigm = detect_paradigm(text)
    n_trials = args.n_trials or extract_n(text, default=30)
    if paradigm:
        print(f"[intake] paradigm: {paradigm}, n_trials: {n_trials}")
        if paradigm == "n-back":
            n_back = args.n_back if args.n_back is not None else extract_n_back(text, default=2)
            rendered = render_template("n-back", n_trials=n_trials, n_back=n_back)
        elif paradigm == "go-no-go":
            rendered = render_template("go-no-go", n_trials=n_trials, go_pct=80)
        else:
            rendered = render_template(paradigm, n_trials=n_trials)
        if rendered is None:
            print(f"[intake] no template for {paradigm}, using generic", file=sys.stderr)
            rendered = generic_spec(text)
    else:
        print(f"[intake] no paradigm detected, using generic spec", file=sys.stderr)
        rendered = generic_spec(text)
    Path(args.output).write_text(rendered)
    print(f"[intake] wrote {args.output} ({len(rendered)} bytes)")
    return 0

if __name__ == "__main__":
    sys.exit(main())
