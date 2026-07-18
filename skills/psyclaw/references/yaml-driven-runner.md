# YAML-driven generic runner (2026-07-05)

> Status: **experimental**. Workspace at `<psyclaw-workspace>\`
> started migrating from per-paradigm hand-written runner.py files to a
> YAML-driven generic runner on 2026-07-05. Canonical 2-file path
> (runner.py + README.md, no YAML) is still the default for new
> paradigms — see `add-paradigm` skill. Use this YAML flow only when you
> expect ≥4 paradigms sharing identical boilerplate.

## Why YAML

User asked "我们的新流程有更好吗？还是说yaml更好" mid-session after the
mass-factory scripts accumulated 6 stubbed paradigms that all shared
identical `make_trial_list` + `run_stub` + `run_stub_batch` + analyze
plumbing. The cost of "copy-paste one more runner" had become higher
than the cost of "spec out the schema once". Two reasons drove the
pivot from the default 2-file model:

1. **Per-paradigm runner drift**. Half the runners had
   `--skip-window` argparse without main() dispatch (would crash if
   invoked without checking the parser). Another quarter had
   indentation/quote-escaping bugs from a half-finished regex rewrite.
   Every new paradigm required touching the same boilerplate (`if
   __name__ == "__main__":`, `argparse`, `csv.DictWriter` plumbing).
2. **Method/parameter duplication**. spec.yaml and methods.md both
   listed conditions, trial count, response mapping — and *drifted*
   from each other. User saw this and asked why both files exist.

## Resulting layout

```
psyclaw/                                # workspace root on E:
├── runner.py                           # generic runner, reads spec.yaml
├── SCHEMA.md                           # YAML contract (Design/Stimuli/Timeline/Response/Output)
├── LAYOUT.md                           # paradigm-dir convention
└── replications/<paradigm>/
    ├── spec.yaml                       # machine-readable parameters
    ├── README.md                       # human description + Running section
    └── output/                         # per-subject CSVs (gitignore)
```

`runner.py` invocation:
```bash
python runner.py replications/stroop_1935_exp2/spec.yaml --skip-window --sub ID01
python runner.py replications/<paradigm>/spec.yaml --sub ID02  # real PsychoPy window
```

## Schema sketch (proposed)

```yaml
paradigm: stroop_1935_exp2
citation: "Stroop, J. R. (1935)…"
doi: 10.1037/h0054651

trials_per_condition: 30
conditions:           # key → human description
  NC: {description: "Neutral — colored square, name the color"}
  NCWd: {description: "Incongruent word — color word in different ink, name the ink"}

stimuli:              # name → {type, properties}
  fixation: {type: text, text: "+", height: 0.06, color: white}
  square:   {type: text, text: "■", height: 0.12}
  word:     {type: text, height: 0.12}

color_pool:           # name → [r, g, b] in -1..1
  red:    [ 1.0, -1.0, -1.0]
  ...
word_pool: [RED, BLUE, GREEN, BROWN, PURPLE]

timeline:             # ordered list of events
  - fixation: 500
  - stimuli: [square, word]
    until_response: true
  - blank: 300

response:
  keys: {r: red, b: blue, g: green, n: brown, p: purple}
  timeout_ms: 3000

output:
  fields: [sub, trial, condition, stim_word, ink_color,
           resp_key, resp_color, correct, rt_ms]

apparatus:
  window: [1024, 768]
  background: [-0.5, -0.5, -0.5]
  units: height
```

Per-trial stimulus selection is condition-driven via a small Python
function (`fill_trial_stimuli`) that maps conditions to specific
stimulus properties. This is the place where paradigm-specific logic
lives — it's the only hand-written Python per paradigm.

## Verified

Stroop spec works end-to-end (2026-07-05): 60 trials written to
`replications/stroop_1935_exp2/output/subj_ID01_trials.csv`, header
matches `output.fields`, condition labels (NC vs NCWd) appear in the
expected ratio, NCWd `stim_word` and `ink_color` are guaranteed
non-matching.

## Not yet supported (gaps in current generic runner.py)

- Multi-factor designs (only single-factor = "condition")
- Block structure (practice vs test; switch vs repeat; etc.)
- Counterbalancing / latin-square assignments
- Stimulus images / audio (text/rect only)
- Within-run randomization control beyond `random.shuffle`
- Save-state mid-trial (escape-key recovery)
- Output schema per condition

Each new paradigm needing one of these will tip the cost-benefit back
toward hand-written runner.py + README.md. Default to that path until
generic runner.py supports your paradigm without per-paradigm code.

## Decision rule

| If… | Then… |
|---|---|
| 1-3 paradigms total | Hand-written runner.py + README.md (no YAML) |
| ≥4 paradigms sharing identical timeline skeleton | YAML + generic runner.py |
| New paradigm needs blocks / images / multi-factor | Hand-written runner.py + YAML can come later |
| User explicitly asks "yaml" | Switch to YAML flow and port forward |

## Pitfalls

### YAML list-as-key trap

PyYAML rejects list keys at parse time (`found unhashable key`). Write
`- stimuli: [square, word]\n  until_response: true` not
`- [square, word]: until_response`. The schema guide at `SCHEMA.md`
documents both forms and how to pick.

### `random` not `import` in smoke mode

The generic runner imports `random` at module top. Smoke-run is
fine. Real-run also fine. The instinct to lazy-import random inside
`smoke_run` breaks headless reuse; don't.

### `--output-dir` default

The runner defaults `output_dir` to `<spec_dir>/output`, NOT to the
E: drive. Means git checkouts are self-contained — running the runner
from any clone produces local CSV files. Override with `--output-dir`
if you want centralized collection.
