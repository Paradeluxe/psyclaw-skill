# paper-to-experiment — Faithful paper→PsyClaw workflow

**When to use this**: User has given a paper (PDF/HTML/DOI) and wants to reproduce the experiment as a runnable PsychoPy project. The default `harness_cli.py --paradigm <name>` does **NOT** do this — it loads a modern cognitive-psychology convention template, not the paper's actual design.

**Workflow** (see pitfall #31 in SKILL.md):

## 1. Fetch + extract paper Method

```bash
# Get PDF via curl (10.3389 Frontiers are open-access)
curl -sL -o paper.pdf -H "User-Agent: Mozilla/5.0" \
  "https://www.frontiersin.org/journals/psychology/articles/<DOI>/pdf"

# Extract Method section (pymupdf is in D:\Software\P python, NOT hermes venv)
/d/Software/P/python.exe -c "
import pymupdf
doc = pymupdf.open('paper.pdf')
text = ''.join(p.get_text() for p in doc)
# Locate MATERIALS AND METHODS / Participants / Stimuli / Procedure
# (heuristic: search for these markers in the text)
import re
markers = ['MATERIALS AND METHODS', 'Participants', 'Stimuli',
           'Procedure', 'RESULTS', 'Discussion']
# Print the section blocks
"

# APA (10.1037) paywall, OSF preprints, ResearchGate direct PDFs all fail in this env
# → use Frontiers in Psychology (gold-OA) or preprint servers
```

## 2. Hand-extract the design parameters

Build a 2-column table: **Paper design | PsyClaw mapping**. Common fields:

| Paper element | What to extract | Spec YAML field |
|---|---|---|
| Stimulus set | Number of identities, emotions, views, conditions | `rows:` count |
| Trial structure | Fixation → blank → stimulus → response → ITI timings | `duration:` per routine |
| Condition distribution | e.g. 70% AX, 10% AY, 10% BX, 10% BY | `n_rounds` × row weighting |
| Response mapping | e.g. F=positive, J=negative; counterbalanced | `keys:` + `correct_ans:` |
| Inter-trial interval | e.g. 1000 ms blank screen | separate routine w/ blank text |
| Number of blocks | e.g. 3 blocks × 240 trials | multiple loops or comment |

## 3. Hand-write the YAML (do NOT use `--paradigm`)

Save as `specs/<paper_shortname>_exp<n>.yaml`. See worked examples below for template structure.

## 4. Generate + verify + run

```bash
# Generate
/c/Users/User/AppData/Local/hermes/skills/research/psyclaw/.venv/Scripts/python.exe \
  /c/Users/User/AppData/Local/hermes/skills/research/psyclaw/scripts/harness_cli.py \
  --spec specs/<name>.yaml --out-dir output/

# Load validation (psychoPy 2026.1.1)
/d/Software/P/python.exe \
  /c/Users/User/AppData/Local/hermes/skills/research/psyclaw/scripts/validate_load_from_xml.py \
  output/<name>/<name>.psyexp

# Runtime validation (auto-advance script — see runtime-validation.md)
PYTHONPATH= PYTHONHOME= /d/Software/P/python.exe _auto_run.py
```

## 5. Report side-by-side comparison

Always produce a table showing which paper parameters are faithfully reproduced and which are approximated (PsychoPy-only, sequential trials vs page-grid, etc.).

---

## Worked example 1: Stroop (1935) Experiment 2

**Source**: Stroop, J.R. (1935). "Studies of interference in serial verbal reactions." J. Exp. Psychology, 18, 643-662. Available at https://psychclassics.yorku.ca/Stroop/ (full text — this is one of the few classic papers with public full text).

**Paper design (Exp 2)**:
- 5 colors: red, blue, green, **brown**, **purple** (not yellow — yellow was substituted out)
- Two conditions:
  - **NC** — neutral colored squares (subject names the ink color)
  - **NCWd** — color word printed in conflicting ink (subject names the **ink**, not the word)
- **NO congruent condition** in the original
- Each word appears in each of the other 4 colors equally
- Original presentation: 10×10 grid on a single sheet, oral response timed with stopwatch to 1/5 second
- ~200 reactions per condition per subject

**PsyClaw approximation** (sequential, keyboard, not page-grid):

| Paper | PsyClaw | Match? |
|---|---|---|
| 5 colors (R, B, G, brown, purple) | 5 colors in spreadsheets | ✓ |
| Two conditions: NC vs NCWd | Two loops (neutral_loop, incongruent_loop) | ✓ |
| No congruent | 0 congruent trials | ✓ |
| Each word × each other color equally | 5 words × 4 colors = 20 incongruent rows | ✓ |
| Sheet-grids × 100 items | 30 sequential trials | ≈ approximation (PsychoPy limit) |
| Oral RT timed by experimenter | Keyboard response | ≈ approximation |

See `E:\hermes_playground\psyclaw\specs\stroop_1935_exp2.yaml` for the YAML.

**Runtime test** (auto-advance):
```
Conditions: 30 + 20 = 50
Window: [800 600]
Neutral trials: 30 (5 colors)
Incongruent trials: 20 (5 words × 4 colors)
Congruent trials: 0 (matches original)
ALL CHECKS PASSED ✓
```

## Worked example 2: AX-CPT

**Source**: Servan-Schreiber, Cohen & Steingard (1996); Braver, Barch & Cohen (1999). Canonical cognitive control paradigm.

**Paper design**:
- Cue (A or B) → delay (blank screen) → probe (X or Y) → response
- Four trial types with canonical distribution: AX 70%, AY 10%, BX 10%, BY 10%
- Target: AX only (press one key, e.g. LEFT)
- All other 3 types: press the other key (RIGHT)
- ~120 trials
- Tests: cue-driven proactive control vs reactive control

**PsyClaw spec**: `specs/axcpt.yaml`

**Runtime test**:
```
AX: 84/84 (100%)
AY: 12/12 (100%)
BX: 12/12 (100%)
BY: 12/12 (100%)
Trial distribution: AX=84 AY=12 BX=12 BY=12
(target ~70% AX, ~10% each non-target — MATCHES canonical AX-CPT)
ALL CHECKS PASSED ✓
```

## Worked example 3: Burra & Kerzel (2019) face stimuli

**Source**: Burra & Kerzel (2019). "Task Demands Modulate Effects of Threatening Faces on Early Visual Processing." Frontiers in Psychology, 10:2400. DOI: 10.3389/fpsyg.2019.02400.

**Paper design**:
- Stimuli: 60 face images (20 identities × 3 emotions: neutral, angry, happy) from KDEF + NimStim + 10 house images
- Trial: bilateral array (face left + face right or face + house), 200 ms presentation
- Tasks: gender discrimination (block A) vs pixel discrimination on fixation (block B), counterbalanced
- 3 blocks of each task × 240 trials = 720 trials per subject (paper says 240 trials/block, 3 blocks = 720)
- Wait — paper actually says 240 trials per block × 6 blocks = 1440 (3 each task). Verify before replicating.

**Bottleneck**: KDEF requires application; NimStim requires application; the paper itself used these via controlled access. See "Academic stimulus databases" section below.

---

## Academic stimulus databases — practical reality (2026-07-02)

Confirmed by direct testing — most are application-gated, not direct-download:

| Dataset | Direct download? | What it offers | Gate |
|---|---|---|---|
| KDEF (kdef.se) | ✗ needs form | 70 identities × 7 emotions × 5 views = 2450 JPGs | Email application |
| NimStim (Columbia) | ✗ needs form | ~672 face images (multiple identities × emotions × race × sex) | Email application |
| NIMH-ChEFS (Duke) | ✗ needs form | Child emotional faces | Email application |
| RaFD (Radboud) | ✗ needs form | 8 females + 12 males (modelling set) | Email application |
| FERG-DB (UW) | ✗ needs form | 55,767 stylized character face images | Form submission |
| `nnataliecc/kdef-images` (GitHub) | partial | 9 images, 1 identity (AF01 only) | None |
| IAPS | ✗ needs form | 956 normative emotional images | Email application + payment |
| OASIS | ✓ | Open Affective Standardized Image Set, 900 images, no auth | Direct download |

**Workflow when dataset is gated**:
1. Surface the bottleneck to the user on the FIRST attempt — don't loop through pages hoping to find a direct link
2. Offer three alternatives:
   - (a) User has access — they provide file paths, we point YAML at `assets/...`
   - (b) PIL-generated geometric placeholders (colored circles, arrows, simple letter stimuli) for pipelines that need stimulus structure but not visual semantics
   - (c) Swap to a paradigm that needs no external assets: Flanker (arrows), Go/No-Go (letters), IAT (words), N-back (digits/letters), Stroop (color words)

**Realistic ceiling for paper→experiment with custom assets**:
~15% of papers can be replicated end-to-end without user-supplied assets. The other 85% require either user access to the gated dataset or substitution.

---

## When to use this reference vs. the templates

Use a template (`--paradigm stroop`) when:
- User says "做一个 2-back 实验" with no specific paper
- Generic cognitive-psychology replication is fine (e.g. teaching demos)
- User says "按 PsychoPy 的标准 Stroop"

Use this reference (hand-written YAML from paper) when:
- User provides a PDF/DOI/HTML and says "做这个"
- User says "复现 Stroop 1935" with a specific year
- User asks for non-standard paradigm variations not in the 6 templates
- Pipeline result must be defensible as "faithful replication" in a methods section

When in doubt, ASK. Offer both options: "I can use the standard 3-color Stroop template, or hand-write from the 1935 paper. Which?" Always explicitly state that the templates are modern, not historical.