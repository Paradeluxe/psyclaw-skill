# Category 1 — 50 Classic Cognitive Experiments (Pure PsychoPy)

Date: 2026-07-11. 50 articles identified, 48 PDFs acquired, 2 problematic.

## Download method: Sci-Hub CDP batch (primary)

Used `scihub_cdp_pdf.py` (from academic-pdf-fetch skill) with Chrome CDP on port 9222.
Single-DOI CLI called from a Python subprocess loop.

```bash
python scihub_cdp_pdf.py "10.1037/h0054651" --output stroop_1935.pdf
```

First paper solves Altcha PoW (~5s), subsequent papers reuse the session cookie (~3s each).
45/50 succeeded on first pass; 3 failed (DOI issues), 2 of those recovered after DOI correction.

## Article list with download results

| # | Paradigm | Year | DOI | Size | Status |
|---|----------|------|-----|------|--------|
| 1 | Stroop | 1935 | 10.1037/h0054651 | 896KB | ✓ |
| 2 | Posner Cueing | 1980 | 10.1080/00335558008248231 | 1.6MB | ✓ |
| 3 | Flanker | 1974 | 10.3758/BF03203267 | 955KB | ✓ |
| 4 | Simon | 1969 | 10.1037/h0027448 | 248KB | ✓ (DOI fixed) |
| 5 | Visual Search | 1980 | 10.1016/0010-0285(80)90005-5 | 2.8MB | ✓ |
| 6 | Attentional Blink | 1992 | 10.1037/0096-1523.18.3.849 | 1.6MB | ✓ |
| 7 | Navon | 1977 | 10.1016/0010-0285(77)90012-3 | 1.9MB | ✓ |
| 8 | Negative Priming | 1985 | 10.1080/14640748508400920 | 1.2MB | ✓ |
| 9 | ANT | 2002 | 10.1162/089892902317361886 | 107KB | ✓ |
| 10 | Dot Probe | 1986 | 10.1037/0021-843X.95.1.15 | 625KB | ✓ |
| 11 | Sternberg | 1966 | 10.1126/science.153.3736.652 | 806KB | ✓ |
| 12 | N-back | 1958 | 10.1037/h0043688 | 433KB | ✓ |
| 13 | Brown-Peterson | 1958 | 10.1080/17470215808416249 | 778KB | ✓ |
| 14 | Serial Position | 1962 | 10.1037/h0045106 | 495KB | ✓ |
| 15 | Working Memory | 1974 | 10.1016/S0079-7421(08)60452-1 | 2.3MB | ✓ |
| 16 | DRM | 1995 | 10.1037/0278-7393.21.4.803 | 1.4MB | ✓ |
| 17 | Lexical Decision | 1971 | 10.1037/h0031564 | 715KB | ✓ |
| 18 | Go/No-Go | 1868/1969 | 10.1016/0001-6918(69)90065-1 | 3.0MB | ✓ |
| 19 | Stop-Signal | 1984 | 10.1037/0033-295X.91.3.295 | 2.7MB | ✓ |
| 20 | Task Switching | 1995 | 10.1037/0096-3445.124.2.207 | 3.0MB | ✓ |
| 21 | WCST | 1963 | 10.1001/archneur.1963.00460070100010 | 1.0MB | ✓ |
| 22 | Iowa Gambling | 1994 | 10.1016/0010-0277(94)90018-3 | 573KB | ✓ |
| 23 | Mental Rotation | 1971 | 10.1126/science.171.3972.701 | 875KB | ✓ |
| 24 | Change Blindness | 1997 | 10.1111/j.1467-9280.1997.tb00427.x | 477KB | ✓ |
| 25 | MOT | 1988 | 10.1163/156856888X00122 | 1.4MB | ✓ |
| 26 | VWM Change Detection | 1997 | 10.1038/36846 | 250KB | ✓ |
| 27 | Corsi Block | 2000 | 10.1207/S15324826AN0704_8 | 142KB | ✓ (DOI fixed) |
| 28 | Fitts' Law | 1954 | 10.1037/h0055392 | 866KB | ✓ |
| 29 | SRT | 1987 | 10.1016/0010-0285(87)90002-8 | 2.2MB | ✓ |
| 30 | Hick's Law | 1952 | 10.1080/17470215208416600 | 1.4MB | ✓ |
| 31 | BART | 2002 | 10.1037/1076-898X.8.2.75 | 335KB | ✓ |
| 32 | Delay Discounting | 1999 | 10.1037/0096-3445.128.1.78 | 1.6MB | ✓ |
| 33 | Probability Discounting | 1991 | 10.1901/jeab.1991.55-233 | 1.6MB | ✓ |
| 34 | CGT | 1999 | 10.1016/S0893-133X(98)00091-8 | 385KB | ✓ |
| 35 | IAT | 1998 | 10.1037/0022-3514.74.6.1464 | 2.4MB | ✓ |
| 36 | Trust Game | 1995 | 10.1006/game.1995.1027 | 1.0MB | ✓ |
| 37 | Ultimatum Game | 1982 | 10.1016/0167-2681(82)90011-7 | 3.0MB | ✓ |
| 38 | Moral Dilemmas | 2001 | 10.1126/science.1062872 | 234KB | ✓ |
| 39 | Emotional Stroop | 1996 | 10.1037/0033-2909.120.1.3 | 2.6MB | ✓ |
| 40 | Cyberball | 2006 | 10.3758/BF03192765 | 400KB | ✓ |
| 41 | Prisoner's Dilemma | 1981 | 10.1126/science.7466396 | 1.9MB | ✓ |
| 42 | Semantic Priming | 1977 | 10.1037/0096-3445.106.3.226 | 2.6MB | ✓ |
| 43 | Sentence Verification | 1972 | 10.1016/0010-0285(72)90017-X | — | ✗ MISSING |
| 44 | Picture Naming | 1965 | 10.1038/2071217a0 | 246KB | ✓ |
| 45 | Dual N-back | 2008 | 10.1073/pnas.0801268105 | 622KB | ✓ |
| 46 | AX-CPT | 2001 | 10.1093/cercor/11.9.825 | 769KB | ✓ |
| 47 | Trail Making | 1958 | 10.2466/pms.1958.8.3.271 | 232KB | ✓ |
| 48 | Line Bisection | 2000 | 10.1016/S0028-3932(99)00045-7 | 253KB | ✓ |
| 49 | Mental Imagery | 1978 | 10.1016/0010-0285(78)90010-5 | 27KB | ⚠ 1 page |
| 50 | Probabilistic Reversal | 2002 | 10.1523/JNEUROSCI.22-11-04563.2002 | 284KB | ✓ |

## DOI corrections (pitfalls)

| Paper | Wrong DOI | Correct DOI | Issue |
|-------|-----------|-------------|-------|
| Simon 1969 | 10.1037/h0027444 | 10.1037/h0027448 | Last digit wrong (h0027444 = auditory signal paper) |
| Corsi Block 2000 | 10.1076/1380-3395(200004)22:2;1-9;FT252 | 10.1207/S15324826AN0704_8 | Ugly DOI from index; real one found via Google Scholar |

## Problematic papers

- **Sentence Verification 1972 (Clark & Chase)**: sci-hub has no copy. Stanford faculty page hosts the PDF (`web.stanford.edu/~clark/1970s/...`) but unreachable from this network (curl timeout). Candidate for manual download.
- **Mental Imagery 1978 (Kosslyn)**: sci-hub only has page 1 (27KB). The full paper is 12 pages in Cognitive Psychology. sci-hub's copy is corrupt/incomplete.

## Full article list JSON

`<psyclaw-workspace>\papers\category1_articles.json` — machine-readable list with paradigm/author/year/doi.

## PDF storage

`<psyclaw-workspace>\papers\category1\` — 48 PDFs (47 unique papers, 1 duplicate cleaned), 56MB total.
