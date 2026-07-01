---

name: psyclaw
description: 'PsyClaw experiment builder — turn natural-language experiment descriptions into complete PsychoPy .psyexp projects with spreadsheets, stimuli, and run scripts. No GUI: user talks to Hermes, Hermes runs the pipeline. Core job is GENERATING experiment flow scripts from intent, NOT picking from a paradigm library. The 6 built-in templates (Stroop/GoNo-Go/Flanker/N-back/IAPS/Posner) are convenience starting points for common cases; the real power is hand-written ExperimentDesign YAML for anything else. Schema design is in flux — see `references/experiment-schema.md` for the proposed Design/Procedure/Stimuli/Response block split.'
tags: [psychology, psychopy, experiment-design, stimuli-generation, conversational]
related_skills: [academic-paper-editing]
merged_skills: [psyclaw-setup]
---

# PsyClaw — Natural Language → PsychoPy Experiment (no GUI)

**You describe the experiment in chat; I run the pipeline and hand back a runnable project folder.** There is no GUI, no flowchart editor, no buttons. The whole product is a conversation.

> **Product framing (2026-06-24 user pivot)**: PsyClaw's value is **generating experiment flow scripts from intent**, not **matching against a library of named paradigms**. When users describe what they want to study, the right output is a runnable flow (routines/loops/components) — *with* paradigm recommendations when asked, but never as the starting point of every interaction. This reframing affects how intent discovery and NL intake should behave — see `references/interaction-flow.md` §6.

## Architecture: 4-layer model

`json2psyexp.js` is **the emitter (L3)**, NOT the harness or the interface.
When someone asks "is X the harness?", they're locating a layer — use this
canonical 4-layer vocabulary so future sessions don't have to re-derive it.
Full breakdown in `references/pipeline-architecture.md`.

| Layer | Role | In PsyClaw |
|-------|------|------------|
| L1 Interface | User-facing entry (chat, CLI, bot, GUI) | Telegram/CLI → you (The Machine) |
| L2 Harness | Orchestration, glue, state machine | `harness_cli.py` / `harness_main.py` |
| L3 Emitter | Pure translation, no IO/UI | `json2psyexp.js` |
| L4 Schema | Data contract, validation | `spec_validator.py` + YAML/JSON/XML specs |

**Implication for "where do I add feature Y?":** L1 = new chat platform,
L2 = new pipeline stage, L3 = new component type / PsychoPy version bump,
L4 = new YAML field. Most patching happens at L3 — see pitfall #17a.

## When to use this skill

Trigger when the user wants to:
- Build a new PsychoPy experiment (any paradigm)
- Generate trial conditions + stimulus files together
- Convert their research description into a runnable project
- Modify an existing experiment (edit the YAML, re-run pipeline)
- Diagnose a .psyexp that PsychoPy won't open

**Don't trigger** for: analyzing existing data, writing papers about experiments, or non-PsychoPy tools (e.g. E-Prime, OpenSesame).

## Interaction model

3 levels, default Level 1. See `references/interaction-flow.md` for the full product spec.

| Level | When | What you see |
|-------|------|--------------|
| **1 — Chat-only** (default) | Standard paradigm, you trust me | One message in, project folder out |
| **2 — Show spec first** | "先给我看看" / important experiment | I render YAML first, you nod, then I emit |
| **3 — Iterate on YAML** | "我自己改改" / you know the design | I emit YAML, you edit it directly, I re-run from stage 2 |

4 intent classes map to 4 different pipeline paths:

| Intent | Trigger words | Pipeline path |
|--------|---------------|---------------|
| **CREATE** | "做一个 X 实验" | Stages 1-8 |
| **MODIFY** | "把 X 改成 Y" | Stages 2-8 (skip 1, re-emit) |
| **DIAGNOSE** | "为什么 .psyexp 报错" | Stages 5 + real PsychoPy load |
| **VERIFY** | "用 PsychoPy 验一下" | Real PsychoPy `loadFromXML()` |

**CREATE intent with vague description (no paradigm / no key params)** → **launch intent discovery (`references/interaction-flow.md` §6) before any stage**. Don't dump a 6-paradigm menu on the user; the discovery flow is variable-driven (IV count → IV type → IV levels → DV → paradigm match → trial structure → confirm). **User explicitly rejected domain-based categorization** — see §6 for the lesson and the full 7-step script.

### Asking the user: one question at a time, plain language (2026-06-24 user prefs)

Two user preferences that must be honored whenever you ask anything in PsyClaw:

1. **"一个一个问呢"** — when you need user input, ask **one** question per turn. Don't stack 2-3 questions in one message. If the topic has multiple sub-decisions (e.g. IV count, IV type, IV levels), treat each as its own turn with a clear next step. The user can always say "我都知道" / "按 X 做" to skip ahead.
2. **"简单易懂的语言"** — avoid jargon when explaining design choices. Default to plain Chinese (since this user is Chinese-speaking). Use technical terms only when they are exactly the PsychoPy / psychology term (e.g. "DV", "IV", "Likert"). When the user themselves used a jargon term, mirror it; when introducing a concept, explain it in one short sentence first.

Both preferences are also captured in `references/interaction-flow.md` §10.

### Other user prefs (2026-07-01)

3. **"你自己验证吧"** — when the user delegates verification, **do it end-to-end** and report a real result (process PID, `loadFromXML` 0-warnings, screenshot path). Don't ask "do you want me to verify?" or list verification steps — that's dodging the delegation. If a verification step fails, report the failure concretely and pivot to the next approach; don't punt back to the user with a question.
4. **"不要对比。我想你继续使用它这个名字"** — there is a separate `Paradeluxe/PsyClaw` repo on GitHub that is a *web app / chatbot* version of PsyClaw (HTML + JS, different scope). Do NOT cross-reference, contrast, or compare this skill with that repo. They share the name only. When asked about "psyclaw" or "the psyclaw project", assume the local skill (this directory). If the user explicitly says "对比一下 GitHub 那只", then do the cross-comparison; otherwise stay local.

## Quickstart

### One-shot (Level 1, recommended)

```bash
# From natural language
python ~/.hermes/skills/research/psyclaw/scripts/harness_cli.py \
    --nl "做一个 Stroop 实验, 30 trials" \
    --out-dir ./experiments/

# From built-in template
python ~/.hermes/skills/research/psyclaw/scripts/harness_cli.py \
    --paradigm go-no-go --n-trials 50 \
    --out-dir ./experiments/

# From a custom YAML spec (Level 3 entry point)
python ~/.hermes/skills/research/psyclaw/scripts/harness_cli.py \
    --spec ./my_experiment.yaml \
    --out-dir ./experiments/
```

### Run the full regression suite (after any json2psyexp.js change)

```bash
# Uses D:\Software\P\python.exe, strips hermes sys.path, runs all examples/*.yaml
# Exit 0 iff all produced .psyexp load with zero warnings
bash ~/.hermes/skills/research/psyclaw/scripts/regression_suite.sh
```

### One-shot (Level 1, recommended)

```bash
# 1. NL → YAML
python scripts/nl_intake.py --input "Stroop 30 trials" --output spec.yaml

# 2. Validate YAML
python scripts/spec_validator.py spec.yaml

# 3. Convert YAML → flowchart JSON
python scripts/flow_gen_transform.py spec.yaml flowchart.json

# 4. Emit .psyexp
node scripts/emit.js flowchart.json experiment.psyexp

# 5. Validate .psyexp (5-layer lxml check)
python scripts/validate_psyexp.py experiment.psyexp

# 6. Generate conditions xlsx
python scripts/xlsx_generator.py --spec spec.yaml --out-dir spreadsheets/

# 7. Generate stimuli
python scripts/stimulus_generator.py --spec spec.yaml --out-dir assets/

# 8. Assemble runnable project folder
python scripts/project_scaffolder.py \
    --spec spec.yaml \
    --psyexp experiment.psyexp \
    --xlsx-dir spreadsheets/ \
    --assets-dir assets/ \
    --out-dir ./my_project/
```

## Pipeline stages

Full contract for each stage is in `references/interaction-flow.md` §2. Inventory & decision (keep/merge/drop) is in `references/scripts-inventory.md`.

| # | Stage | Tool | What it does | Failure mode |
|---|-------|------|--------------|--------------|
| 1 | NL → spec | `nl_intake.py` | Detect paradigm (9 built-in keywords), render template or generic spec | Unknown paradigm → launch intent discovery §6 |
| 2 | Spec validate | `spec_validator.py` | YAML schema, types, cross-refs | Exit 2 with error list |
| 3 | Spec → flowchart | `flow_gen_transform.py` | Key remap, Loop Point = `(idx+1)*2`, inline spreadsheet | Schema drift — see pitfalls §1 |
| 4 | Flowchart → .psyexp | `emit.js` + `json2psyexp.js` | Pure transform, handles 4 flowchart shapes | Schema bug — patched, see §6 |
| 5 | .psyexp validate | `validate_psyexp.py` | 5-layer lxml check | Layer 6 (real PsychoPy) is separate |
| 6 | Conditions xlsx | `xlsx_generator.py` | Per-loop spreadsheet (openpyxl) | openpyxl missing |
| 7 | Stimuli gen | `stimulus_generator.py` | PIL text/shape, wave tone, edge-tts TTS, ffmpeg video | ffmpeg / edge-tts missing |
| 8 | Project scaffold | `project_scaffolder.py` | README + run.sh/run.bat + requirements.txt | None |

## Supported paradigms (built-in)

| Paradigm | Keywords (zh/en) | Template | Trials |
|----------|------------------|----------|--------|
| Stroop | stroop, 色词, 颜色冲突 | `templates/stroop.yaml.tmpl` | 30+ |
| Go/No-Go | gonogo, gng, 抑制任务, 反应抑制 | `templates/go-no-go.yaml.tmpl` | 50+ |
| Flanker | flanker, 侧抑制, 箭头干扰, eriksen | `templates/flanker.yaml.tmpl` | 50+ |
| N-back | n-back, nback, 工作记忆 | `templates/n-back.yaml.tmpl` | 50+ |
| IAPS | iaps, 情绪图片, 情绪调节 | `templates/iaps.yaml.tmpl` | 20+ |
| Posner cueing | posner, cueing, 空间注意 | `templates/posner.yaml.tmpl` | 60+ |

For anything else, use `--spec your_experiment.yaml` with the schema below, or describe it in chat and I'll hand-write the YAML.

## ExperimentDesign YAML schema (abbreviated)

```yaml
name: my_experiment           # required, kebab-case
version: "1.0"
description: "..."

display:
  fullscreen: true
  size: [1024, 768]
  background_color: [0, 0, 0]
  units: height              # height | pix | cm | deg

routines:                    # required, list
  - name: trial              # unique
    duration: 2.0            # seconds; null = wait for response
    components:
      - type: text
        text: "Hello"
        height: 0.05
        color: white
        pos: [0, 0]
      - type: image
        path: "assets/foo.png"
        size: [0.5, 0.5]
      - type: keyboard
        keys: "space, r, b"
        duration: 2.0
        correct_ans: $correct_resp   # $col references loop spreadsheet
        store: response
      - type: audio
        path: "assets/beep.wav"
        volume: 1.0
      - type: video
        path: "assets/anim.mp4"
        no_audio: false

loops:                       # optional
  - name: main_loop
    start_routine: trial
    end_routine: trial       # inclusive
    n_rounds: 30
    order: fullRandom        # sequential | random | fullRandom
    is_trials: true
    spreadsheet:
      file: conditions.xlsx
      columns:
        - name: stim_word
          type: str
        - name: correct_resp
          type: str
      rows:
        - stim_word: RED
          correct_resp: r
        - stim_word: BLUE
          correct_resp: b

stimuli:                     # asset generation requests
  - id: fixation_cross
    kind: image
    format: png
    size: [100, 100]
    background: [0, 0, 0]
    foreground: [1, 1, 1]
    generator: text          # text | shape | tone | tts | animated_shape
    text: "+"
    output: assets/fixation_cross.png
  - id: correct_tone
    kind: audio
    format: wav
    duration: 0.3
    generator: tone
    frequency: 880
    output: assets/correct.wav
  - id: welcome_voice
    kind: audio
    generator: tts
    text: "Welcome to the experiment."
    voice: en-US-AriaNeural
    output: assets/welcome.wav
  - id: expanding_circle
    kind: video
    duration: 2.0
    fps: 30
    size: [400, 400]
    generator: animated_shape
    shape: circle
    start_radius: 10
    end_radius: 100
    color: [1, 0, 0]
    output: assets/anim.mp4
  - id: iaps_image_001
    kind: image
    external: assets/iaps/001.jpg   # user supplies
```

## Component types reference

| Type | Required fields | Optional |
|------|-----------------|----------|
| `text` | `text` | `color`, `height` (0.05), `font`, `pos`, `italic`, `bold`, `letter_spacing` |
| `image` | `path` | `size`, `pos` |
| `audio` | `path` | `volume` (1.0) — note: `loop` is NOT supported in 2026.1.1 |
| `video` | `path` | `size`, `pos`, `no_audio` — note: `flip`/`anchor` not supported in 2026.1.1 |
| `keyboard` | `keys` | `duration` (-1=infinite), `force_end`, `correct_ans`, `store` |
| `mouse` | — | `duration`, `save_mouse_state` (`final`/`on click`/`never`), `force_end_on_press` (`never`/`any click`/`correct click`), `clickable`, `new_clicks_only`, `time_relative_to` |
| `slider` | — | `ticks`, `labels`, `init_val`, `granularity`, `force_end_routine`, `store_rating`, `read_only`, `size`, `pos`, `color`, `styles` |
| `code` | (at least one of the body fields) | `name`, `code_type` (`Py`/`JS`/`Both`/`Auto->JS`), `before_experiment`, `begin_experiment`, `begin_routine`, `each_frame`, `end_routine`, `end_experiment`, plus `*_js_*` mirrors (e.g. `begin_js_routine`). Body text is HTML-escaped (`<>&"'`) so user Python strings survive XML roundtrip — see pitfall #17a. |

See `references/psychopy-components.md` for the full per-component param
list with valTypes.

## Loop spreadsheet: `$column` interpolation

Inside a component, prefix any string with `$` to interpolate from the loop's spreadsheet column of the same name:
- `$stim_word` → column "stim_word" from current row
- `$stim_color` → column "stim_color"
- `$correct_resp` → column "correct_resp"

## Multi-turn NL intake

If user input is vague (no paradigm detected, no trial count), AI should launch the **intent discovery flow** in `references/interaction-flow.md` §6 — it's variable-driven (IV/DV/levels), not domain-driven. Don't fall back to the old 6-domain menu.

For complex multi-paradigm experiments, build the YAML directly rather than going through templates.

## Stimulus generation

`stimulus_generator.py` handles 4 kinds:
- **text image** (`generator: text`): rendered via PIL. Special chars (+/-) drawn as rectangles (predictable line width for fixation crosses).
- **shape image** (`generator: shape`): circle/rect/polygon via PIL.
- **tone audio** (`generator: tone`): sine wave with fade-in/out, any frequency.
- **TTS audio** (`generator: tts`): Microsoft Edge TTS (en-US-AriaNeural default).
- **animated video** (`generator: animated_shape`): PIL frames → ffmpeg → H.264 mp4.

For external assets (e.g. IAPS images, lab-recorded audio), use `external:` and ensure file exists.

## Validation

`validate_psyexp.py` checks (5 layers, all must pass):
- **L1** XML parses (lxml, with recover mode for forgiving parse)
- **L2** `<Settings>`, `<Routines>`, `<Flow>` all present
- **L3** Every `<Routine>` has at least one component
- **L4** `<LoopInitiator>` count = `<LoopTerminator>` count; loop refs real routines
- **L5** Every `<Param>` has val + valType + name

Layer 6 (real PsychoPy `Experiment.loadFromXML`) is a **separate VERIFY intent**, not part of the CREATE pipeline. See `interaction-flow.md` §3.

## Verified samples (5/5 PASS in lxml + real PsychoPy)

```
stroop    30 trials, 4 routines, 1 loop,  140 params, 23KB .psyexp
go-no-go  50 trials, 4 routines, 1 loop,  140 params, 23KB .psyexp
flanker   80 trials, 4 routines, 1 loop,  140 params, 23KB .psyexp
n-back   100 trials, 4 routines, 1 loop,  140 params, 23KB .psyexp
iaps      20 trials, 5 routines, 1 loop,  166 params, 30KB .psyexp
```

Plus custom complex test (8 routines + 2 loops + image+audio+video, 332 params, 46KB).

**Real PsychoPy 2026.1.1 verification (2026-07-01, all post-fix):** the five
paradigm samples (Stroop/GoNoGo/Flanker/N-back/IAPS) plus three custom
golden samples load via `psychopy.experiment.Experiment().loadFromXML()`
in `D:\Software\P\python.exe` on Windows with **zero "Parameters not
known" warnings**:

| sample | size | components exercised | result |
|--------|------|----------------------|--------|
| `examples/stroop/stroop_experiment.psyexp` | 22,852 bytes | text + keyboard, single loop with conditionsFile | 0 warnings |
| `examples/rich_components.psyexp` | 25,178 bytes | audio + video + text + mouse + slider | 0 warnings |
| `templates/nested-loops-test.yaml` → .psyexp | 23,514 bytes | outer (isTrials=false) + inner (isTrials=true) | 0 warnings |
| `examples/parallel_loops.yaml` → .psyexp | 26,575 bytes | 2 disjoint loops (parallel, not nested) + outside-loop routine | 0 warnings |
| `examples/stimgen_test.yaml` → .psyexp | varies | all 4 stimulus generators (text/shape/tone/tts/animated) | 0 warnings + assets generated |
| `examples/code_test.yaml` → .psyexp | 8,724 bytes | CodeComponent (begin/each/end Routine + JS phases + HTML escape roundtrip) | 0 warnings |

**How to re-verify after any change to json2psyexp.js**:
`D:\Software\P\python.exe scripts/validate_load_from_xml.py <file.psyexp>`
(see `scripts/validate_load_from_xml.py`). Captures the "Parameters not
known to this version" warning via logging handler and exits non-zero on
any warning.

**4-layer GUI verification workflow (2026-07-01):** when a new component
type is added, don't trust a single check — run all 4:

1. **XML text check** — `grep <ComponentName out.psyexp` confirms the emit
   function emitted tags in the right place.
2. **loadFromXML** — `D:\Software\P\python.exe -c "from psychopy.experiment import Experiment; Experiment().loadFromXML(path)"` — exits 0 iff PsychoPy accepts the file.
3. **API roundtrip** — open the file with `Experiment().loadFromXML()`, then
   read `exp.routines['<r>'].children[i].params['<field>'].val` — verify
   the Python-side parse matches what we emitted (HTML-escape roundtrip
   test especially for CodeComponent's `extendedCode` fields).
4. **Builder GUI screenshot** — open `pythonw.exe -m psychopy.app <file>`
   (or use `load_psyexp_in_builder.py`), then `screenshot_window.ps1 -TitlePattern "*<file>*"` → `vision_analyze` the PNG. Confirms visual rendering (icon, tab placement, Flow loop wrap).

Layers 1-3 are required; layer 4 is gold-standard visual confirmation.

**Computer-use GUI verification (2026-07-01):** the canonical workflow for visually
confirming a .psyexp opens in Builder:
1. Launch PsychoPy: `cd /d/Software/P && PYTHONPATH= PYTHONHOME= ./pythonw.exe -m psychopy.app <path.psyexp>`
2. Poll `tasklist //FI "IMAGENAME eq pythonw.exe"` until ~300MB+ PID appears
3. `computer_use(action='capture', app='pythonw.exe', mode='som')` — check TitleBar label for
   `.psyexp - PsychoPy Builder (v2026.1.1)`, count Routine tabs, inspect Flow diagram.
   **If capture returns 0x0** (cua-driver can't see the window — usually because
   another app like Telegram holds foreground focus), fall back to
   `powershell -ExecutionPolicy Bypass -File scripts/screenshot_window.ps1 -TitlePattern "*<file>*"`
   to PrintWindow the Builder hwnd directly. See pitfall #24.
4. For full verification, also run `D:\Software\P\python.exe -c "from psychopy.experiment import Experiment; ..."` 
   to catch `loadFromXML` warnings the visual capture can't see.
5. When done, `powershell -ExecutionPolicy Bypass -File scripts/close_psychopy.ps1` — sends
   WM_CLOSE to Builder (reliable, doesn't kill Hermes). See pitfall #23.

From WSL: use `Invoke-WmiMethod Win32_Process.Create` to spawn the GUI process in the
user's interactive desktop session (Session 1) — see `wsl-windows-interop` skill.

**End-to-end smoke test (2026-06-24):** ran `.venv/bin/python scripts/harness_cli.py --nl "做一个 Stroop 实验 30 trials" --out-dir /tmp/psyclaw-smoke/` and produced a clean `stroop_experiment/` folder with all 7 expected files (.psyexp 22.8KB, xlsx 5.1KB, README.md, run.sh executable, run.bat, requirements.txt, experiment_spec.yaml source backup). `harness_main.py` step() was refactored so the project lands at `out_dir/<name>/` directly (no nested `_work/out/` indirection that trapped the user previously) and `_work/` is cleaned up after scaffold. Before this fix, the .psyexp landed in `_work/` and the user never saw the runnable folder.

## Dependencies

**Python**: 系统 `/usr/bin/python3` 没装 pip, 也没装 lxml/openpyxl/PIL/yaml/edge-tts。**必须用 PsyClaw 自带 venv**:
```bash
cd ~/.hermes/skills/research/psyclaw
uv venv --python 3.11 .venv
.venv/bin/python -m pip install lxml openpyxl pillow pyyaml edge-tts
.venv/bin/python scripts/harness_cli.py --nl "..." --out-dir ./experiments/
```

**System**:
- `node` 18+ (for json2psyexp.js emit)
- `ffmpeg` (for animated video stimuli)
- `psychopy` 2023.2+ (only required to RUN the generated .psyexp, not to generate it)

**Python packages**: `pyyaml`, `openpyxl`, `pillow`, `lxml`, `edge-tts`

**Critical pitfall**: 不要在 harness_main.py / harness_cli.py 里硬编码 `python3`——会用系统 python 跑 subprocess,找不到 venv 的 site-packages。已经修过:用 `sys.executable` 而不是 `"python3"`。以后加新 orchestrator 也遵守。这个坑通用,适用于任何含 subprocess.Popen 的 Python 工具链。

## Files

```
~/.hermes/skills/research/psyclaw/
├── SKILL.md                          # this file
├── scripts/
│   ├── nl_intake.py                  # stage 1: NL → YAML
│   ├── spec_validator.py             # stage 2: YAML validate
│   ├── flow_gen_transform.py         # stage 3: YAML → flowchart JSON
│   ├── emit.js                       # stage 4a: Node CLI wrapper + normalize
│   ├── json2psyexp.js                # stage 4b: upstream emitter (vendored, patched)
│   ├── validate_psyexp.py            # stage 5: 5-layer lxml check
│   ├── xlsx_generator.py             # stage 6: conditions xlsx
│   ├── stimulus_generator.py         # stage 7: PIL + TTS + tone + video
│   ├── project_scaffolder.py         # stage 8: build complete folder
│   ├── harness_main.py               # orchestrator: runs all 8 stages
│   ├── harness_cli.py                # CLI entry: --nl / --spec / --paradigm
│   ├── validate_load_from_xml.py     # real PsychoPy loadFromXML verifier (gold standard, L6)
│   ├── check_emit_bugs.py            # detect the 4 known emit-layer bugs in any .psyexp
│   ├── load_psyexp_in_builder.py     # launch Builder with hermes sys.path stripped + auto-load .psyexp (does NOT work for a second concurrent Builder instance — see pitfall #21)
│   ├── regression_suite.sh           # one-shot: all examples/*.yaml → harness_cli → loadFromXML 0-warn check
│   ├── close_psychopy.ps1            # PowerShell WM_CLOSE helper, reliable Builder shutdown (see pitfall #23)
│   └── screenshot_window.ps1         # PowerShell PrintWindow helper, works when cua-driver can't see foreground (see pitfall #24)
├── templates/
│   ├── stroop.yaml.tmpl
│   ├── go-no-go.yaml.tmpl
│   ├── flanker.yaml.tmpl
│   ├── n-back.yaml.tmpl
│   ├── iaps.yaml.tmpl
│   ├── posner.yaml.tmpl
│   └── nested-loops-test.yaml        # regression: outer isTrials=False + inner isTrials=True
├── examples/
│   ├── stroop/                       # complete generated project
│   ├── parallel_loops.yaml           # regression: 2 disjoint loops in same Flow
│   ├── rich_components.yaml          # regression: mouse + slider + audio + video
│   ├── stimgen_test.yaml             # regression: all 4 stimulus generators
│   ├── code_test.yaml                # regression: CodeComponent (begin/each/end Routine + JS phases + HTML escape)
│   ├── code_probe.yaml               # regression: minimal CodeComponent smoke test
│   ├── complex_task.yaml
│   └── asset_heavy_task.yaml
├── references/
│   ├── interaction-flow.md           # product spec: intents, stages, ops, intent discovery, working prefs
│   ├── pipeline-architecture.md      # 4-layer model: interface/harness/emitter/schema (NEW 2026-07-01)
│   ├── scripts-inventory.md          # 10-script audit: keep/merge/drop
│   ├── experiment-schema.md          # proposed Design/Procedure/Stimuli/Response block split (in flux, not binding)
│   ├── legacy-gui-history.md         # GUI archive (read-only context)
│   ├── psychopy-components.md        # full param list per component type
│   ├── paradigm-recipes.md           # paradigm-specific notes
│   ├── real-psychopy-validation.md   # bugs lxml missed + WSL→Session 1 GUI launch
│   ├── gui-verification-pitfalls.md  # what `computer_use` clicks can and can't do in PsychoPy Builder
│   ├── component-type-audit.md       # coverage matrix per PsychoPy 2026.1.1 component type
│   ├── json2psyexp-emit-bugs.md      # 4 known emit-layer hardcode bugs + fix recipes
│   └── xlsx-bool-and-weighting.md    # bool→int coercion + equal cell-weighting recipe (Stroop case study)
└── .venv/                            # uv venv (system Python lacks pip/lxml/etc.)
```

## Pitfalls (lessons learned)

1. **Schema drift** — flowchart JSON has 4 field-name variants (`components[]`, `avtpComponents[]`, `avtpData{}`, flowchart array). `emit.js` normalizes all 4 to internal format.
2. **Loop Point convention** — `Point = (routineIndex + 1) * 2`, must be in `loop.list[i].Point`. See json2psyexp.js line 754.
3. **YAML in templates** — use block-style (one key per line) NOT inline `{name: x, type: y}`. PyYAML chokes on double braces.
4. **Unescaped `<` in text** — PsychoPy itself is lenient but lxml strict mode rejects. Validator uses recover=True; templates avoid literal `<` characters.
5. **WSL CAN validate with real PsychoPy** — use `D:\Software\P\python.exe` (PsychoPy's own Python, NOT the `psychopy.exe` launcher in any venv). The venv launcher reads a shebang that points to a Python path that may not exist (e.g. `D:\Pythons\Python312\python.exe`). The `D:\Software\P` install has the full site-packages and works directly. `python -c "from psychopy.experiment import Experiment; exp = Experiment(); exp.loadFromXML('file.psyexp')"` is a complete load-test that catches schema mismatches the lxml validator misses.
6. **Three PsychoPy 2026.1.1 params that json2psyexp.js once emitted but should not** — `anchor` on TextComponent/MovieComponent, `stopWithRoutine` on KeyboardComponent. **FIXED in current code** — `generateTextComponentFromSchema` (L553), `generateImageComponentFromSchema` (L585), and `generateKeyboardComponentFromSchema` (L660) no longer emit these. The old `examples/stroop/stroop_experiment.psyexp` (generated before the fix) still had them and produced 6 `loadFromXML` warnings. Regenerated 2026-07-01 with fixed emit: **zero warnings**. Always regenerate examples after patching json2psyexp.js.
7. **Fixation cross** — never use PIL default font for `+`; it renders as a thick block. Use two thin rectangles.
8. **Complex multi-routine paradigms** — build YAML directly, don't try to template everything.
9. **YAML `JS reserved word` trap in JS** — never name a destructured variable `in` (it's a reserved word in JavaScript). In `emit.js` use `inp`/`outp` not `in`/`out`. Symptom: `SyntaxError: Unexpected token 'in'` at runtime.
10. **OS.add_dll_directory breaks numpy on Linux** — when calling Windows `D:\Software\P\python.exe` from WSL Python, do NOT do `import os; os.add_dll_directory = lambda x: None` before numpy import. This attribute addition corrupts numpy's `os` module lookup. Clean env works fine without it.
11. **Use the real PsychoPy to validate .psyexp, not just lxml** — `lxml` strict-parse passes files that PsychoPy 2026.1.1 still rejects. The `validate_psyexp.py` here uses lxml in `recover=True` mode (forgiving) but the gold standard is `psychopy.experiment.Experiment().loadFromXML(path)`. Five paradigms (Stroop/GoNoGo/Flanker/N-back/IAPS) all pass with **zero "not known" warnings** on the vendored json2psyexp.js after the schema fix.
12. **No GUI = no FileSystemDirectoryHandle hell** — the old GUI was crippled by `showDirectoryPicker()` being a native OS dialog that no automation can click. Dropping GUI means we use plain fs paths and don't need IndexedDB or permission handles. See `references/legacy-gui-history.md`.
13. **Intent discovery is variable-driven, not domain-driven** — user explicitly rejected the "按领域分类 (注意/记忆/情绪/社会...)" approach. Default to IV/DV/levels decomposition. See `references/interaction-flow.md` §6 for the 7-step script.
14. **Don't hardcode `python3` in subprocess orchestrators when the skill ships its own venv** — use `sys.executable` so the subprocess inherits the venv's site-packages. Symptom: `ModuleNotFoundError: No module named 'lxml'` even though `pip show lxml` says it's installed. The pip-installed location and the `python3` PATH location are different on this machine (pip → ~/.local/lib/python3.11, `python3` → /usr/bin/python3 with no site-packages).
15. **PsyClaw = generate flow scripts, not match paradigms** — when the user describes an experiment, the default response is a runnable flow, not a list of "would you like Stroop, GoNoGo, Flanker, N-back, IAPS, Posner?" Asking this question treats the 6 templates as the product. They aren't — they're convenience starting points for the 20% of cases where the user genuinely wants a stock paradigm. For the other 80%, build a flow from the variables in their description. (See `references/experiment-schema.md` for the Design/Procedure/Stimuli/Response block split that backs this.)
16. **`harness_main.step()` output path bug** — old signature was `step(spec_path, work, verbose)` and wrote the project under `work/out/<name>/` while also leaving `_work/` artifacts at the user's out_dir. User-visible symptom: ran `harness_cli.py --out-dir ./experiments/` and saw a stray `_work/` folder, with the actual project buried at `./experiments/_work/out/<name>/`. Fixed by changing step() to `step(spec_path, out_dir, verbose)`, writing directly to `out_dir/<name>/`, and `shutil.rmtree(work)` after scaffold succeeds.
17. **json2psyexp.js emit-layer hardcode bugs (2026-07-01)** — Four bugs in the flowchart-JSON → .psyexp emit layer: empty `conditionsFile` (L755/L845), empty `correctAns` (L662), hardcoded `isTrials="True"` + missing field on processedLoops (L753/L865), and stale `anchor`/`stopWithRoutine` params. Single-loop Stroop test does not catch the `isTrials` bug. **All bugs and fixes are catalogued in `references/json2psyexp-emit-bugs.md`.** Use `scripts/check_emit_bugs.py <file.psyexp>` to detect any of them, and `templates/nested-loops-test.yaml` as the regression test (nested outer=False + inner=True loop).
17c. **Multiple independent loops (not nested) — also handled by the same depth algorithm (2026-07-01)** — Two non-overlapping loops in the same Flow (e.g. loop_a wraps routines 0-1, loop_b wraps routines 2-3) both compute `depth=0` in `generateFlow()`'s containment iteration (neither contains the other), then sort stably and emit in order. Verified via `examples/parallel_loops.yaml` (5 routines, 2 disjoint loops + 1 outside-loop routine) — `loadFromXML` 0 warnings, Flow renders as `[loop_a] [loop_b] [end]`, each loop's `conditionsFile` and `isTrials` are correct. **Don't write a new algorithm for this case** — the existing containment-based depth computation already does the right thing. Add a new example whenever a third loop topology is tested.
17d. **`generateLoopTerminator` loop.name off-by-one (2026-07-01)** — When two parallel loops share an `endRoutineIndex`, the second loop's `LoopTerminator` MUST be emitted **before** the first loop's. Otherwise Builder GUI shows the wrong `name=` on the wrong terminator. Algorithm: sort `loopsEndingHere` by `b.depth - a.depth` (descending). Already correct in current code; this is just a tripwire if someone refactors that sort.
17e. **`storeRating` on SliderComponent is `bool`, not `str` (2026-07-01)** — PsychoPy 2026.1.1 SliderComponent `storeRating` is `valType="bool"` with `val="True"`. json2psyexp.js once emitted `val="last rating"` (string) — `loadFromXML` accepted but the resulting .psyexp's data logging is wrong. **Fix**: emit as `val="${storeRating ? 'True' : 'False'}"` with `valType="bool"`. Same rule for `forceEndRoutine`, `forceEndRoutineOnPress` (all bool). Check the actual `__init__.py` of each component for `valType="bool"` attrs before writing the emit.

**Data-drop diagnostic recipe** (2026-07-01): when a field X is correct at stage 3 (flowchart JSON) but wrong in stage 4 output (.psyexp), suspect BOTH the data carrier (the map that rebuilds the loop object in `generateFlow()` at L750-760) AND the reader (the body of `generateLoopInitiator()`). These are TWO separate silent drops in the same field path, and a single bug fix at one site will NOT fix the data loss. Recipe:
1. `flow_gen_transform.py` writes the field → verify with `python flow_gen_transform.py spec.yaml chart.json --verbose && grep <field> chart.json` (should be present)
2. `emit.js` normalize → if missing here, it's a normalize bug (rare)
3. `json2psyexp.js generateFlow()` rebuilt processedLoops → grep `<field>` in the JS source's processedLoops return object (L750-760); if absent, **add it**
4. `json2psyexp.js generateLoopInitiator()` reads the field → grep `<field>` in the function body; if hardcoded `''` or `True`, **change to read `loop.<field>`**

For component-level fields (e.g. `correctAns` on KeyboardComponent), the recipe collapses to: check the generate function's local `const` initializers — hardcoded defaults like `''` and `True` and `'center'` are the prime suspects.
17a. **Component type dispatcher coverage (2026-07-01)** — All 8 component types now have working dispatch + emit in `generateComponents()` (~L428-446): audio / video / text / image / keyboard / **mouse / slider / code**. Param lists verified against `D:\Software\P\lib\site-packages\psychopy\experiment\components\<type>\__init__.py` for PsychoPy 2026.1.1. Recipe for adding a new type: 1) look up param list from PsychoPy's own `__init__.py`; 2) write `generate<Type>ComponentFromSchema(component, routineName)` matching those params + valType + updates; 3) add `else if (component.type === '<type>')` branch to the dispatcher; 4) add `<type>` to `VALID_COMPONENT_TYPES` in `spec_validator.py` (often already there if it was in the validator's allowed set ahead of the dispatcher); 5) write a YAML with one of the new type and add to regression suite. **Gotcha: CodeComponent uses `extendedCode` valType, NOT `str` — body text must be HTML-escaped (e.g. `"` → `&quot;` or `&apos;`, `<` → `&lt;`, `>` → `&gt;`, `&` → `&amp;`) so user Python strings survive XML roundtrip. **See `references/component-type-audit.md` for the coverage matrix.**
17b. **SoundComponent.loop and MovieComponent.flip/anchor are 2026.1.1-incompatible (2026-07-01)** — Even with dispatcher working, the audio and video generators emit params that PsychoPy 2026.1.1 does not understand: `name="loop"` on `<SoundComponent>` (psychoPy source has no such param on Sound — only `hamming` and `stopWithRoutine`), and `name="flip"` / `name="anchor"` on `<MovieComponent>` (MovieComponent's BaseVisualComponent in 2026.1.1 only inherits `anchor` from text/image, NOT video; `flip` was removed). `loadFromXML` warns: "Parameters not known to this version: loop, flip". **Fix to implement**: in `generateAudioComponentFromSchema`, drop the `loop` const and the `<Param val="${loop}" name="loop"/>` line. In `generateVideoComponentFromSchema`, drop the `flip` const and the `<Param val="${flip}" name="flip"/>` line, and drop the `anchor` const. **General rule** when adding or fixing a component generator: grep `D:\Software\P\lib\site-packages\psychopy\experiment\components\<type>\__init__.py` for `self.params['<name>'] = Param(` to see the actual supported param list — don't trust the vendored generator to be in sync. See `references/component-type-audit.md`.
18. **NEVER use `taskkill /F /IM pythonw.exe` to kill PsychoPy** — kills ALL pythonw processes including Hermes's own gateway/worker, causing a silent disconnect. Use `process.kill(session_id)` for background processes, or `computer_use` close button for GUI apps. `taskkill /F /PID <pid>` also risky — the PID may belong to Hermes. Cross-check the PID against the known background session ID. This rule applies to ANY process name Hermes itself uses (pythonw, python3, etc.) — when in doubt, use `process.kill(session_id)`.
19. **Launching PsychoPy from Hermes terminal: PYTHONPATH pollution** — Hermes sets `sys.path[0]` to its own venv, and PsychoPy picks up `hermes-agent/venv/Lib/site-packages/cryptography` which is a Linux wheel (.so) → `ImportError: DLL load failed` on Windows. Fix: `cd /d/Software/P && PYTHONPATH= PYTHONHOME= ./pythonw.exe -m psychopy.app` (clears both variables). Do NOT use `psychopy.exe` launcher — its shebang may point to a non-existent Python. Use `pythonw.exe` directly. **First sign of "DLL load failed" when launching any Windows-installed Python from a Hermes terminal: clear PYTHONPATH and PYTHONHOME before re-running.**
20. **xlsx `bool` column type bug (Stroop)** — old `xlsx_generator.py` wrote Python `bool` (`True`/`False`) into `type: bool` spreadsheet columns. Pavlovia + some PsychoPy versions reject `bool` cells in CSV-converted data files (codec error on upload). **Fix**: coerce `bool` columns to `1`/`0` int. Verified with `openpyxl`: `ws.cell(2,3).value` is `<class 'int'>`, not `bool`. Also fixed a Stroop-specific equal-weighting bug — original template listed 6 congruent rows duplicated (RED/red×2, BLUE/blue×2, GREEN/green×2) and 6 incongruent rows once, giving a 2:1 congruent:incongruent ratio instead of 1:1. Now both conditions get 6 rows each for equal sampling probability under `fullRandom` loop. When writing new paradigm templates, always sanity-check that row counts reflect the design's intended cell weighting — a 6:6 factorial with `n_rounds: 30` will produce ~15 trials per cell, but a 6:12 split will produce ~10 vs ~20. See `references/xlsx-bool-and-weighting.md` for the full recipe.
21. **`computer_use` PostMessage click is UNRELIABLE on wxPython modals (2026-07-01)** — Earlier docs claimed the canonical GUI verification workflow is `computer_use(action='capture', app='pythonw.exe', mode='som')` after launching PsychoPy with `pythonw.exe -m psychopy.app`. **This is NOT reliable for the wxPython modal lifecycle**: PostMessage clicks on the `关闭 (X)` button, `Open...` menu item, and `Ctrl+O` accelerator all silently fail to dismiss the modal "Save before quitting?" dialog (or the file-picker dialog). Symptoms: capture still shows the same Builder window, no new dialog, no AX nodes surfaced for the missing dialog. **Trust `loadFromXML()` 0 warnings as the ground truth for "would PsychoPy accept this file"** — the GUI capture is fine for title-bar / routine-tab / Flow visual sanity checks AFTER load, but don't rely on it for click-driven interactions. If you must drive wxPython, use `scripts/load_psyexp_in_builder.py` (loads + shows the Builder programmatically in the same Python process — no separate file-picker step needed). **Caveat: load_psyexp_in_builder.py fails when a second Builder instance is started — the first instance owns wx.App.dpi, and the second fails with `'NoneType' object has no attribute 'dpi'`. Close any existing Builder first with `close_psychopy.ps1`, then start a new one.**
22. **One regression suite per project (2026-07-01)** — `scripts/regression_suite.sh` runs every `examples/*.yaml` (and `examples/*/*.yaml`) through `harness_cli.py` + `validate_load_from_xml.py` and asserts all pass with 0 warnings. After ANY change to `json2psyexp.js`, `flow_gen_transform.py`, `spec_validator.py`, or `xlsx_generator.py`: run the suite first, before the next feature. Currently 8/8 pass (asset_heavy_task, code_probe, code_test, complex_task, parallel_loops, rich_components, stimgen_test, stroop_experiment_spec). Exit code 0 iff all pass.
23. **Closing PsychoPy Builder reliably: PowerShell `SendMessage WM_CLOSE` (2026-07-01)** — `taskkill` kills Hermes; `computer_use` PostMessage on the X button is silently swallowed by wxPython modals (see #21). The reliable path is a small PowerShell snippet that grabs the builder's hwnd via `Get-Process` and sends `WM_CLOSE` (0x0010) to the main window AND to every child window first (in case a modal dialog is sitting on top — the modal owns the focus, sending WM_CLOSE to its own hwnd will dismiss it cleanly, often selecting "Don't Save" by default in PsychoPy):

```powershell
Add-Type 'using System; using System.Runtime.InteropServices; public class W { [DllImport("user32.dll")] public static extern IntPtr SendMessage(IntPtr h, uint m, IntPtr w, IntPtr l); [DllImport("user32.dll")] public static extern bool EnumChildWindows(IntPtr p, EnumProc cb, IntPtr l); public delegate bool EnumProc(IntPtr h, IntPtr l); }'
$proc = Get-Process pythonw | Where-Object { $_.MainWindowTitle -like '*PsychoPy*' }
$h = $proc.MainWindowHandle
[W]::EnumChildWindows($h, { param($c, $l) [W]::SendMessage($c, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null; return $true }, [IntPtr]::Zero) | Out-Null
Start-Sleep -Milliseconds 300
[W]::SendMessage($h, 0x0010, [IntPtr]::Zero, [IntPtr]::Zero) | Out-Null
```

Verified: builder (PID 9428) cleanly exited without any "Save?" dialog hanging. `Get-Process pythonw` shows only the child worker (no MainWindowTitle) after the script. **Add this as a `close_psychopy.ps1` helper if doing more than one round of GUI verification.**

24. **`computer_use` screen capture fails when cua-driver can't see the foreground window (2026-07-01)** — When a foreground user-facing app (e.g. Telegram desktop, chat client) owns the desktop focus, Windows 11 focus-stealing prevention will reject `SetForegroundWindow(PsychoPy)`, and cua-driver's `capture` will return `0x0` for any app. `list_apps` returns `[]`. The Builder process IS alive (PID + hwnd via `Get-Process` works) but cua-driver can't enumerate or capture it. **Workaround**: don't try to bring Builder to foreground — instead use Win32 `PrintWindow` against its known hwnd to capture its contents without going through the compositor. Requires System.Drawing assembly. Example:

```powershell
Add-Type -AssemblyName System.Drawing
Add-Type 'using System; using System.Runtime.InteropServices; public class W { [DllImport("user32.dll")] public static extern bool GetWindowRect(IntPtr h, out RECT r); [DllImport("user32.dll")] public static extern bool PrintWindow(IntPtr h, IntPtr hdc, uint flags); [StructLayout(LayoutKind.Sequential)] public struct RECT { public int L, T, R, B; } }'
$proc = Get-Process pythonw | Where-Object { $_.MainWindowTitle -like '*code_test*' }
$h = $proc.MainWindowHandle; $r = New-Object 'W+RECT'
[W]::GetWindowRect($h, [ref]$r) | Out-Null
$w = $r.R - $r.L; $ht = $r.B - $r.T
$bmp = New-Object System.Drawing.Bitmap $w, $ht
$g = [System.Drawing.Graphics]::FromImage($bmp)
$hdc = $g.GetHdc()
[W]::PrintWindow($h, $hdc, 2) | Out-Null   # PW_RENDERFULLCONTENT for DX-accelerated apps
$g.ReleaseHdc($hdc); $g.Dispose()
$bmp.Save('out.png', [System.Drawing.Imaging.ImageFormat]::Png)
```

Verified: captures PsychoPy Builder (wxPython + DWM composition) correctly even when Telegram is the foreground app. Use `vision_analyze(image_url=...)` on the saved PNG to inspect Builder contents. Add as `scripts/screenshot_window.ps1` if used more than once.

## References

- `references/interaction-flow.md` — product spec (intents, stages, ops, levels, intent discovery, working prefs)
- `references/pipeline-architecture.md` — 4-layer model: interface/harness/emitter/schema
- `references/scripts-inventory.md` — 10-script audit, keep/merge/drop decisions
- `references/xlsx-bool-and-weighting.md` — bool→int coercion + equal cell-weighting recipe (Stroop case study)
- `references/json2psyexp-emit-bugs.md` — four known hardcode bugs in `json2psyexp.js` (conditionsFile, correctAns, isTrials, stale anchor/stopWithRoutine), with line numbers, fix recipes, and a detection script pointer
- `references/component-type-audit.md` — coverage matrix for every supported `type:` value (which work today, which are silently dropped, which 2026.1.1 incompatibilities exist) plus the recipe for adding a new component type end-to-end
- `references/experiment-schema.md` — proposed Design/Procedure/Stimuli/Response block split (in flux, consult before extending the schema)
- `references/legacy-gui-history.md` — why GUI was abandoned (read-only)
- `references/psychopy-components.md` — full param list per component type
- `references/paradigm-recipes.md` — paradigm-specific notes (timing, common pitfalls)
- `references/real-psychopy-validation.md` — bugs the lxml validator missed, real PsychoPy `loadFromXML()` test
- `references/gui-verification-pitfalls.md` — what `computer_use` clicks can and can't do in PsychoPy Builder; the wxPython modal trap; how to use `load_psyexp_in_builder.py` instead
- [json2psyexp.js source](https://github.com/Paradeluxe/PsyClaw/blob/master/json2psyexp.js) — the emit logic
- [PsychoPy Builder docs](https://www.psychopy.org/builder/builder.html) — what we're emitting