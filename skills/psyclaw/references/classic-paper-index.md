# Classic Paper Index — 29 canonical cognitive psychology experiments

Full index: `<psyclaw-workspace>\papers\classics\index.json`

## Source tiers (empirical distribution from 2026-07-04 crawl)

| Tier | Count | % |
|------|-------|---|
| L1 — Direct PDF | 2 | 7% |
| L2 — Substitute full-text | 0 | 0% |
| L3 — PsyToolkit/Wikipedia/Scholarpedia | 27 | 93% |

## L1 PDFs (2)

| Paper | Size | Source |
|-------|------|--------|
| Stroop 1935 | 2.1 MB | csusm.diehr.com course page |
| Greenwald et al. 1998 IAT | 513 KB | faculty.washington.edu |

## L3 sources by paradigm

### Attention (10 papers)
| Paradigm | Paper | Year | DOI | PsyToolkit | Wikipedia |
|----------|-------|------|-----|-----------|-----------|
| Stroop | Stroop | 1935 | 10.1037/h0054651 | stroop.html | — |
| Posner cueing | Posner | 1980 | 10.1080/00335558008248231 | posner.html | — |
| Flanker | Eriksen & Eriksen | 1974 | 10.3758/BF03203267 | flanker.html | ✓ |
| Simon | Simon | 1969 | 10.1037/h0027444 | simon.html | — |
| Visual Search | Treisman & Gelade | 1980 | 10.1016/0010-0285(80)90005-5 | visualsearch.html | — |
| Attentional Blink | Raymond et al. | 1992 | 10.1037/0096-1523.18.3.849 | — | Scholarpedia |
| Navon | Navon | 1977 | 10.1016/0010-0285(77)90012-3 | — | — |
| Negative Priming | Tipper | 1985 | 10.1080/14640748508400920 | — | — |
| Attention Networks | Petersen & Posner | 1990 | 10.1146/annurev.ne.13.030190.000325 | — | — |
| Dot Probe | MacLeod et al. | 1986 | 10.1037/0021-843X.95.1.15 | dotprobe.html | — |

### Memory (7 papers)
| Paradigm | Paper | Year | DOI | PsyToolkit | Wikipedia |
|----------|-------|------|-----|-----------|-----------|
| Sternberg | Sternberg | 1966 | 10.1126/science.153.3736.652 | — | Scholarpedia |
| N-back | Kirchner | 1958 | 10.1037/h0043688 | nback.html | ✓ |
| Brown-Peterson | Brown, J. | 1958 | 10.1080/17470215808416249 | — | ✓ |
| Serial Position | Murdock | 1962 | 10.1037/h0045106 | — | ✓ |
| Working Memory | Baddeley & Hitch | 1974 | 10.1016/S0079-7421(08)60452-1 | — | ✓ |
| DRM | Roediger & McDermott | 1995 | 10.1037/0278-7393.21.4.803 | — | — |
| Lexical Decision | Meyer & Schvaneveldt | 1971 | 10.1037/h0031564 | — | ✓ |

### Executive Function (5 papers)
| Paradigm | Paper | Year | DOI | PsyToolkit | Wikipedia |
|----------|-------|------|-----|-----------|-----------|
| Go/No-Go | Donders | 1868 | — | gonogo.html | — |
| Stop-Signal | Logan & Cowan | 1984 | 10.1037/0033-295X.91.3.295 | stopsignal.html | ✓ |
| Task Switching | Rogers & Monsell | 1995 | 10.1037/0096-3445.124.2.207 | — | ✓ |
| WCST | Milner | 1963 | 10.1001/archneur.1963.00460070100010 | — | ✓ |
| Iowa Gambling | Bechara et al. | 1994 | 10.1016/0010-0277(94)90018-3 | — | ✓ |

### Perception (1 paper)
| Paradigm | Paper | Year | DOI | Wikipedia |
|----------|-------|------|-----|-----------|
| Mental Rotation | Shepard & Metzler | 1971 | 10.1126/science.171.3972.701 | ✓ |

### Social & Emotion (6 papers)
| Paradigm | Paper | Year | DOI | PsyToolkit | Wikipedia |
|----------|-------|------|-----|-----------|-----------|
| IAT | Greenwald et al. | 1998 | 10.1037/0022-3514.74.6.1464 | iat.html | ✓ |
| Trust Game | Berg et al. | 1995 | 10.1006/game.1995.1027 | — | ✓ |
| Ultimatum Game | Güth et al. | 1982 | 10.1016/0167-2681(82)90011-7 | — | ✓ |
| Moral Dilemmas | Greene et al. | 2001 | 10.1126/science.1062872 | — | ✓ |
| Emotional Stroop | Williams et al. | 1996 | 10.1037/0033-2909.120.1.3 | — | ✓ |
| IAPS | Lang et al. | 2008 | — | — | — |

## Directory layout

```
<psyclaw-workspace>\papers\classics\
├── index.json                 # Full machine-readable index (29 entries)
├── psytoolkit/               # 10 HTML pages from psytoolkit.org
├── scholarpedia/             # 3 Scholarpedia + 15 Wikipedia HTML pages
├── stroop_1935/
│   ├── paper.pdf             # 2.1 MB
│   └── paper.json
├── greenwald_1998/
│   ├── paper.pdf             # 513 KB
│   └── paper.json
└── ... (remaining 27 paper directories with paper.json only)
```

## Usage in PsyClaw pipeline

1. Look up the paradigm in this index → get PsyToolkit URL if available
2. Download PsyToolkit page → extract parameters (trial count, SOA, conditions, response mapping)
3. Generate YAML spec from extracted parameters
4. Run normal pipeline: spec → flowchart → .psyexp → validate

**Always prefer PsyToolkit over the original paper.** The PsyToolkit page is parameterized and validated by thousands of replications. The original paper is prose and usually paywalled.
