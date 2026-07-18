# Paper Library Classification (2026-07-11)

150 papers across 3 categories at `E:\hermes_playground\psyclaw\papers\`.

## Three-category system

| Category | Count | Dir | Criteria |
|----------|-------|-----|----------|
| 1 — Pure PsychoPy | 50 | `category1/` | No external materials needed. Text, shapes, colors, timing only. |
| 2 — Downloadable materials | 50 | `category2/` | PsychoPy + external stimuli (images/audio) available on OSF/open repos. |
| 3 — Manual materials | 50 | `category3/` | Experiment design implementable, but materials must be user-created/found. |

## Audit rules (applied 2026-07-11)

When vetting papers for the library, reject any of:

- **Animal experiments** (Thorndike cats, Gallup chimps, Pavlov dogs, etc.)
- **Clinical scales / test manuals** (BDI, STAI, MMPI, Raven's, PANAS, Hamilton)
- **Meta-analyses / reviews** (Psychol Bull, Annual Reviews, TICS)
- **Book chapters** (no experimental data)
- **Database introduction papers** (CFD, RaFD, OASIS, GAPED, NAPS, food-pics, FRIDa, BOSS, THINGS — these describe the dataset, not an experiment using it)
- **Norm / calibration papers** (ANEW, Warriner norms, Brysbaert concreteness)
- **Computer science papers** (CVPR, ACM MM — not psychology experiments)
- **Symposium summaries** (JOV symposium — no experiment)
- **Non-computer-based experiments** (Stanford Prison, Strange Situation, Marshmallow, Visual Cliff — can't run in PsychoPy)

## Download method

- **Primary**: sci-hub CDP batch via `scihub_cdp_pdf.py` (Chrome `--remote-debugging-port=9222`)
- **Secondary**: Google Scholar + bsk for DOI discovery/correction
- **Fallback**: Direct OA URLs (PLOS, eLife, Frontiers)

See `academic-pdf-fetch` skill for the full pipeline.

## Category 1 — Pure PsychoPy (50 papers)

Classic cognitive paradigms: Stroop, Posner cueing, Flanker, Simon, Visual Search,
Attentional Blink, Navon, Negative Priming, ANT, Dot Probe, Sternberg, N-back,
Brown-Peterson, Serial Position, DRM, Lexical Decision, Stop-Signal, Task Switching,
WCST, Iowa Gambling, Mental Rotation, Change Blindness, MOT, VWM Change Detection,
Corsi Block, Fitts' Law, SRT, Hick's Law, BART, Delay Discounting, Probability
Discounting, CGT, IAT, Trust Game, Ultimatum Game, Moral Dilemmas, Cyberball,
Semantic Priming, Wason Selection, Picture Naming, Dual N-back, AX-CPT, Trail
Making, Sperling Partial Report, Probabilistic Reversal, SNARC Effect, Part-Whole
Face Effect, Orthographic Neighbors, Negative Compatibility.

All use only text, shapes, colors, and keyboard responses. Fully generatable
from spec.yaml → builder.py → .psyexp.

## Category 2 — Downloadable materials (50 papers)

Experiments using open datasets: face perception (CFD, RaFD), emotion recognition,
scene perception (MIT Places), object recognition (BOSS), food images (food-pics),
body perception, voice/sound, word norms.

Key difference from Category 1: the .psyexp references external image/audio files
that exist in a known open repository. The user downloads the dataset once, then
the experiment runs.

## Category 3 — Manual materials (50 papers)

Experiments where the framework can be built but materials need manual work:
- Word list experiments (language-specific, need translation)
- Social psychology vignettes (scenario text must be authored)
- Gated-database experiments (KDEF, NimStim, IAPS need application)
- Judgment/decision problems (framing text, gamble descriptions)
- Conditioning paradigms (CS/UCS selection)
- Moral dilemmas (story text)
- Clinical tasks adapted for research

The .psyexp + conditions.xlsx provide the structure; the user fills in the stimuli.

## Path C validation link (2026-07-18)

Paper claims must use **run + data retention**, not PDF count alone.

- Specs present: cat1 **50** + cat2 **47** + cat3 **50** under `replications/`
- G0 design_compiler: **147/147** (`output/webui_batch_validate/summary.json`)
- G1+G2 stratified smoke: **15/15** finished with project-mirrored CSV
- Procedure: `references/path-c-webui-validation.md`
