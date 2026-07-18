# Paper Categories for PsyClaw Experiment Replication

Three-category classification system (2026-07-11) for academic papers
targeted for PsychoPy experiment replication.

## Category 1: Pure PsychoPy (text/shapes/colors only)

No external materials needed. The entire experiment (stimuli, conditions,
timeline) is generated from spec.yaml alone.

**Examples**: Stroop, Flanker, Simon, Posner Cueing, N-back, Go/No-Go,
Sternberg, Dot Probe, Hick's Law, Mental Rotation, IAT, Stop-Signal,
Task Switching, WCST, Iowa Gambling, DRM, Lexical Decision, BART,
Delay Discounting, etc.

**Data**: 50 papers, 58MB PDFs at `papers/category1/`.
Article list at `papers/category1_articles.json`.

**Download method**: Sci-Hub CDP batch (45/50) + Google Scholar curl (3/50)
+ DOI corrections (2/50). ~5 min for full batch.

## Category 2: PsychoPy + Downloadable Materials

Experiment needs image/audio/video stimuli, but materials are openly
available on OSF or equivalent open repositories.

**Datasets used**: Chicago Face Database, RaFD, OASIS, GAPED, NAPS,
food-pics, FRIDa, MIT Places, BOSS, THINGS, ESC-50, ANEW, Warriner norms,
Concreteness norms, etc.

**Data**: 50 papers, 58MB PDFs at `papers/category2/`.
Article list at `papers/category2_articles.json`.

**Download method**: Sci-Hub CDP batch (42/47) + direct OA (2/47) +
replacement papers (6/47). ~8 min for full batch.

**Note**: Not all listed datasets are fully verified as downloadable.
Each dataset needs manual verification before experiment generation.

## Category 3: Partial — Materials User-Supplied

Experiment framework can be built (routines, loops, components) but
specific stimuli, word lists, or materials must be created/located by
the user. This is the largest category by volume.

**Not yet collected** (as of 2026-07-11). Estimated 50 papers.

## Download Workflow (reusable)

1. Build article list as JSON with DOIs
2. Start Chrome: `chrome.exe --remote-debugging-port=9222 --user-data-dir=<temp>`
3. Verify: `curl http://127.0.0.1:9222/json/version`
4. Run batch script calling `scihub_cdp_pdf.py` single-DOI CLI in a loop
5. For failures: try Google Scholar for DOI correction, then retry
6. Replace unrescuable papers (book chapters, symposium summaries) with alternatives

Full recipe in `academic-pdf-fetch` skill → `references/batch-download-recipe.md`.

## Pitfalls

- Google Scholar `[PDF]` links mostly point to publisher paywalls, not real OA PDFs
- Sci-Hub CDP is the reliable primary path for ALL psychology publishers
- Chrome CDP exits after 3-5 min idle — verify before each batch
- MSYS path translation mangles `/e/...` → `E:\e\...` — use Windows paths
- DOI typos are common: always verify with Scholar or Crossref before batch
- Book chapters and symposium summaries aren't on sci-hub — replace with real papers
