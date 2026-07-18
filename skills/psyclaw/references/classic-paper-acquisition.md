# Classic Psychology Paper Acquisition — What Works & What Doesn't

Date: 2026-07-02. Updated 2026-07-11 with Sci-Hub CDP batch results.

## Primary method (2026-07-11): Sci-Hub CDP batch

**This is now the canonical path for paywalled psychology papers.** Chrome CDP on port 9222 + `scihub_cdp_pdf.py` solves the Altcha PoW in-browser and downloads native PDFs.

```bash
# 1. Start Chrome with debug port (must use temp profile to avoid conflicts)
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="<chrome-debug-profile-dir>" \
  --no-first-run --no-default-browser-check "about:blank" &

# 2. Single paper (~5s first, ~3s subsequent)
python scihub_cdp_pdf.py "10.1037/h0054651" --output stroop_1935.pdf

# 3. Batch via Python subprocess loop (see references/category1-pdfs.md)
```

**Verified 2026-07-11**: 45/50 classic cognitive psychology papers downloaded from sci-hub.red.
Total 48 PDFs (47 unique), 56MB. All major publishers (APA/T&F/Elsevier/Springer/Science/OUP) work.

**Chrome CDP stability**: Chrome with `--remote-debugging-port=9222` exits after ~3-5 minutes of idle.
Restart before each batch run. Use `curl -s http://127.0.0.1:9222/json/version` to verify before running scripts.

## The core problem: APA (10.1037) is a hard paywall

Most classic experimental psychology papers (Stroop 1935, Simon 1969,
Kirchner 1958, MacLeod et al. 1986) were published in APA journals —
*Journal of Experimental Psychology*, *Journal of Abnormal Psychology*,
etc. APA does not provide open-access versions, and `academic-search`
explicitly cannot extract from `psycnet.apa.org` / `doi.apa.org` (server-side
paywall, 0 body returned).

## What was tried (2026-07-02 session)

| Source | Result | Notes |
|--------|--------|-------|
| **academic-search fetch doi:10.1037/...** | ❌ 0 body | APA paywall, documented limitation |
| **Sci-Hub (.se / .ee / .ru)** | ❌ DNS blocked | `getaddrinfo failed` for all domains; China GFW |
| **ResearchGate direct PDF** | ❌ 403 | Requires browser cookies + session |
| **Semantic Scholar API** | ❌ 404 | No pre-1990 papers indexed |
| **archive.org (wikipedia corpus)** | ❌ 404 | DOI-specific file removed |
| **psychclassics.yorku.ca** | ✅ HTML | Stroop 1935 full text (38KB) |
| **sas.upenn.edu/~saul** | ✅ HTML | Sternberg 1966 full text (17KB) — author's personal site |
| **hanover.edu direct PDF** | ✅ HTML (fake PDF) | Returns course page, not paper |
| **wexler.free.fr direct PDF** | ❌ 404 | All links dead as of 2026-07 |
| **link.springer.com `/content/pdf/`** | ✅ PDF | Eriksen & Eriksen 1974 (955KB) — direct publisher PDF, no auth needed for Psychonomic Society journals |
| **xlzhanglab.scnu.edu.cn** | ✅ PDF | Posner 1980 (671KB) — educational mirror |
| **facultypsy.hope.edu direct PDF** | ✅ PDF | Treisman & Gelade 1980 (2.8MB, genuine publisher PDF) |

## Successfully acquired (in <psyclaw-workspace>\papers\classics\)

| File | Format | Size | Quality | Source |
|------|--------|------|---------|--------|
| `Treisman_Gelade_1980.pdf` | PDF | 2.8MB | Genuine publisher PDF (10.1016, Elsevier) | facultypsy.hope.edu |
| `Eriksen_Flanker_1974.pdf` | PDF | 955KB | Genuine publisher PDF (10.3758, Springer) | link.springer.com `/content/pdf/` |
| `Posner_1980_Orienting_of_Attention.pdf` | PDF | 671KB | Genuine PDF | xlzhanglab.scnu.edu.cn |
| `Bechara_1994_IGT_review.pdf` | PDF | 118KB | Review article, not original | mdproblemgambling.com |
| `Roelofs_2018_Donders_review.pdf` | PDF | 682KB | Donders subtractive-method review | ardiroelofsscience.nl |
| `Stroop_1935.txt` | Plain text | 38KB | Full paper | psychclassics.yorku.ca |
| `Sternberg_1966.txt` | Plain text | 17KB | Full paper | sas.upenn.edu/~saul |

Full catalog: `<psyclaw-workspace>\papers\classics\CATALOG.md`

## Missing (paywall-blocked)

| Paper | DOI | Publisher | Why blocked |
|-------|-----|-----------|-------------|
| **Simon 1969** | 10.1037/h0027212 | APA | APA paywall |
| **Kirchner 1958** | 10.1037/h0043688 | APA | APA paywall |
| **MacLeod et al. 1986** | 10.1037/0021-843X.95.1.15 | APA | APA paywall |
| **Bechara et al. 1994** (original) | 10.1016/0010-0277(94)90018-3 | Elsevier | Not tried; review substitute acquired |

## The key insight: textbook > original paper for experiment extraction

For PsyClaw's goal (extracting experiment Method → generating runnable .psyexp),
**textbook descriptions are more useful than original papers** for classic
paradigms, for three reasons:

1. **OCR quality**: Pre-1980 papers are scanned bitmaps with terrible OCR.
   Text extraction from a Stroop 1935 PDF scan would produce garbage.
2. **Paywall**: Most are behind APA/Springer/T&F paywalls, and neither
   `academic-search` nor Sci-Hub bypasses them from this environment.
3. **Structure**: Textbook Method descriptions (e.g. Eysenck & Keane,
   Pashler, standard lab manuals) are already parameterized — trial counts,
   SOA ranges, condition layouts — whereas original papers often bury
   parameters in prose.

**Recommendation for the paper→experiment pipeline**: don't start with
original PDFs. Use curated Method descriptions from textbooks, lab manuals,
or PsyToolkit experiment library pages. These are:
- Already structured (conditions, timing, stimuli)
- Free of paywall
- Modern-text (clean extraction, no OCR)
- Validated by thousands of replications

## Publisher support matrix for `academic-search --pdf`

See the main academic-search SKILL.md for the full table. Relevant for
psychology:

| Publisher | DOI prefix | `--pdf` support | Psychology papers? |
|-----------|-----------|-----------------|-------------------|
| Elsevier | 10.1016 | ✅ publisher PDF | Yes (Cognition, Neuropsychologia, NeuroImage) |
| APA | 10.1037 | ❌ nothing | **Most classic experimental psych** |
| Springer | 10.1007/10.3758 | ✅ publisher PDF | Yes (Psychonomic Society) |
| T&F | 10.1080 | ❌ CF-blocked | Yes (Quarterly JEP) |
| Science | 10.1126 | ✅ publisher PDF | Rare (Sternberg 1966) |
| Frontiers | 10.3389 | ✅ gold-OA PDF | Yes (Frontiers in Psychology) |
| PLOS | 10.1371 | ✅ gold-OA PDF | Yes (PLOS ONE) |

## If you must get an APA paper

1. Check if the author has a personal-site PDF (Sternberg pattern)
2. Check psychclassics.yorku.ca for pre-1950 papers
3. Check ResearchGate — may require browser with cookies
4. Accept the review/substitute (Bechara → IGT review; Donders → Roelofs 2018)
