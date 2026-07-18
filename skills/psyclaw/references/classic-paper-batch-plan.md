# Classic Paper Batch Download Plan

## Strategy: 4-tier acquisition

Most classic cognitive psychology papers are behind APA/T&F/Springer paywalls (pitfall #26).
Use a tiered approach to maximize what we can get locally.

| Tier | Source | Success rate | Content |
|------|--------|-------------|---------|
| L1 — Direct PDF | PubMed Central, OSF, PsyArXiv, author lab, Semantic Scholar open links | ~30% | Full original paper |
| L2 — Substitute full-text | Author replication papers, reviews, OA versions, dissertations | ~25% | Method section complete, not original but parameters intact |
| L3 — Textbook/experiment library | PsyToolkit, Eysenck & Keane, Pashler, lab manuals | ~35% | Parameterized description, validated by thousands of replications |
| L4 — Metadata only | DOI + title + abstract + known parameters | ~10% | Placeholder, fill when access available |

## Target: 30 classic cognitive experiments

### Attention
- Stroop (1935) — 5 colors, NC vs NCWd, no congruent condition
- Posner (1980) — cueing spatial attention
- Flanker / Eriksen & Eriksen (1974) — response competition
- Visual Search / Treisman & Gelade (1980) — feature integration theory
- Attentional Blink / Raymond, Shapiro & Arnell (1992)
- Simon (1969) — spatial S-R compatibility
- Navon (1977) — global vs local precedence
- Negative Priming / Tipper (1985)

### Memory
- Sternberg (1966) — memory scanning
- N-back / Kirchner (1958)
- Brown-Peterson (1958) — short-term memory decay
- DRM / Roediger & McDermott (1995) — false memory
- Working Memory / Baddeley & Hitch (1974)
- Serial Position / Murdock (1962)

### Executive Function
- Go/No-Go / Donders (1969)
- Stop-Signal / Logan & Cowan (1984)
- Wisconsin Card Sort / Grant & Berg (1948)
- Task Switching / Rogers & Monsell (1995)
- Iowa Gambling / Bechara et al. (1994)

### Perception & Judgment
- Mental Rotation / Shepard & Metzler (1971)
- IAPS / Lang, Bradley & Cuthbert (2008)
- Dot Probe / MacLeod, Mathews & Tata (1986)
- Lexical Decision / Meyer & Schvaneveldt (1971)

### Social & Emotion
- IAT / Greenwald, McGhee & Schwartz (1998)
- Trust Game / Berg, Dickhaut & McCabe (1995)
- Ultimatum Game / Güth, Schmittberger & Schwarze (1982)
- Moral Dilemmas / Greene et al. (2001)
- Emotional Stroop / Williams, Mathews & MacLeod (1996)

## Directory layout

```
<psyclaw-workspace>\papers\classics\
├── stroop\
│   ├── paper.pdf           # L1 full text / L2 substitute
│   ├── paper.json          # {doi, title, authors, year, journal, tier, pdf_path, key_params}
│   └── parameters.yaml     # L3: textbook-extracted parameters when no paper source
├── stroop_emotional\
│   └── ...
├── posner\
│   └── ...
... (30 directories)
```

## Execution

1. **Batch search** — Semantic Scholar API + web_search × 30 papers → DOI, OA PDF URL, paywall status
2. **Tiered download** — L1 first (direct PDF), fall to L2 (substitute), then L3 (textbook params)
3. **Metadata records** — `paper.json` per paper: DOI, title, authors, year, journal, tier, pdf_path, key_design_params
4. **L3 fallback** — For papers behind paywalls: extract experiment parameters from PsyToolkit / textbooks → `parameters.yaml`

## Known pitfalls

- APA (psycnet.apa.org) returns 0 body on web_extract — hard paywall
- ResearchGate PDF links 403 without session cookies
- Sci-Hub DNS blocked in this environment
- Pre-1980 papers are scanned bitmaps with terrible OCR
- Classic papers often describe multiple experiments — need to pick the canonical one (usually Exp 1 or Exp 2)

## Actual results (2026-07-04 batch crawl)

Ran full 4-tier strategy across 29 classic cognitive psychology papers.
Results confirmed pitfall #26 — the paywall is real, but L3 sources are superior.

### By the numbers

| Tier | Count | % |
|------|-------|---|
| L1 — Direct PDF | 2 | 7% |
| L2 — Substitute | 0 | 0% |
| L3 — PsyToolkit/Wikipedia/Scholarpedia | 27 | 93% |

**L1 PDFs obtained:**
- Stroop 1935 (2.1 MB) — from csusm.diehr.com course page
- Greenwald et al. 1998 IAT (513 KB) — from faculty.washington.edu

**L3 sources collected:**

| Source | Count | Usefulness |
|--------|-------|-----------|
| PsyToolkit experiment pages | 10 | Clean parameter tables, trial structure, timing |
| Wikipedia articles | 15 | Historical context, stimulus lists, variations |
| Scholarpedia articles | 3 | Expert-written, parameterized but shorter |

**PsyToolkit pages (most valuable):** stroop, simon, flanker, posner, gonogo,
stopsignal, nback, dotprobe, visualsearch, iat.

### Key finding: L3 > L1 for PsyClaw

The PsyToolkit experiment library pages are **superior to original papers**
for PsyClaw's purpose. Each page contains:
- Standardized parameter tables (trial count, SOA, condition distribution)
- Response mappings with key bindings
- Trial structure timing (fixation → stimulus → response → ITI)
- Known replication parameters validated by thousands of users

By contrast, original papers:
- Are scanned bitmaps for pre-1980 publications (bad OCR)
- Often describe multiple experiments without clean isolation
- Use prose descriptions that require manual parameter extraction
- Are 90% behind paywalls

**Conclusion**: For paper→experiment pipeline, search PsyToolkit first.
Only fall back to the original paper when PsyToolkit doesn't cover the paradigm.
See pitfall #35.
