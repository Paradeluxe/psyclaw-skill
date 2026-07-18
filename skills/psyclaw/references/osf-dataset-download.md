# OSF / open dataset acquisition for paper-replication stimuli

When a paper's stimulus set is on **OSF** (Open Science Framework) — free, no application — the standard recipe works. This doc captures the worked example from 2026-07-02 where we replicated **Thieleking et al. (2020) art.pics** in Frontiers in Psychology.

## The recipe (3 steps, ~5 min for 30 images)

### 1. Extract the OSF URL from the PDF

```
from pymupdf import open as pdfopen
import re
doc = pdfopen('paper.pdf')
text = ''.join(p.get_text() for p in doc)
urls = re.findall(r'https?://[^\s<>"]+', text)
# Look for: osf.io/<NODE_ID>/  (usually 5-char alphanumeric)
```

OSF node IDs look like `BTWNQ`. The Frontiers papers typically link with text like *"data stored at OSF (https://osf.io/BTWNQ/)"*.

### 2. List subfolders and find the stimuli folder

```python
import urllib.request, json, ssl
ssl_ctx = ssl.create_default_context()
ssl_ctx.check_hostname = False
ssl_ctx.verify_mode = ssl.CERT_NONE

# List root
url = "https://api.osf.io/v2/nodes/<NODE_ID>/files/osfstorage/?page[size]=100"
req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
data = json.loads(urllib.request.urlopen(req, context=ssl_ctx, timeout=20).read())

# Find a subfolder with "stim" in its name
for f in data['data']:
    if 'stimul' in f['attributes']['name'].lower():
        stimuli_folder_id = f['attributes']['path'].strip('/')
```

### 3. List files in that folder, then download per-file (not the zip)

```python
# List files
url = f"https://api.osf.io/v2/nodes/<NODE_ID>/files/osfstorage/{stimuli_folder_id}/?page[size]=100"
data = json.loads(urllib.request.urlopen(req, context=ssl_ctx, timeout=30).read())

# Download each file via its individual download link
for f in data['data']:
    name = f['attributes']['name']
    dl = f['links']['download']
    outpath = os.path.join(outdir, name)
    req2 = urllib.request.Request(dl, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req2, context=ssl_ctx, timeout=30) as resp:
        with open(outpath, 'wb') as fp:
            fp.write(resp.read())
    time.sleep(0.3)  # politeness — OSF rate limits
```

**Critical**: download per-file, NOT via `?zip=` on the whole node.

## The slow-zip trap (DON'T do this)

`https://files.osf.io/v1/resources/<NODE_ID>/providers/osfstorage/?zip=` returns the WHOLE NODE as a zip:
- For 2,332-image datasets, the stream is **~50 KB/s** (server-side zipping)
- 50MB+ zip downloaded 5 minutes, never completes reliably
- **Kill it the moment you see < 100 KB/s throughput**, switch to per-file API downloads

```bash
# If you accidentally started one:
process(action='kill', session_id=<id>)
```

## Pagination

OSF API returns paginated results. `data['links']['next']` has the URL for page 2. For the art.pics replication we only needed page 1 (100 files); for larger datasets, loop.

OSF rate-limits aggressively. If you get HTTP 502/503 on the second page, sleep and retry — or just take page 1's 100 files.

## Worked example: art.pics (art stimuli)

**Paper**: Thieleking et al. (2020) "art.pics Database: An Open Access Database for the Perception of Art" — Frontiers in Psychology 11:576580. DOI: 10.3389/fpsyg.2020.576580.

| Step | Result |
|------|--------|
| Fetch paper PDF | 5.7MB, 6 pages, https://www.frontiersin.org/journals/psychology/articles/10.3389/fpsyg.2020.576580/pdf |
| Extract OSF URL | `osf.io/BTWNQ/` from "Data Availability Statement" |
| List root folders | 3 folders: `art.pics stimuli`, `art.pics license agreement`, `art.pics meta-data` |
| List stimuli folder | 100+ files, naming pattern `{id}_{style}.jpg` (e.g. `2542_dali.jpg`, `1017_azulejos.jpg`) |
| Download 32 images (4 per art style × 8 styles) | 138 seconds (~4 sec/image, 50-200KB each) |
| Spec from PDF Method | 5 Likert ratings per image (liking, wanting, recognizability, arousal, valence), 1-9 scale, 12 picture sets randomly assigned |
| Generated `.psyexp` | 70KB, 9 routines, 1 loop, 642 params, 0 loadFromXML warnings |
| Runtime validated | 32/32 trials, 8 styles × 4 images, 5 ratings per trial, CSV logged |

The 8 art styles in art.pics: Azulejos, Dalí, Hundertwasser, Klimt, Munch, Picasso, Pointillism, Popart.

## File naming conventions in OSF for image/audio datasets

These conventions let you build a `conditions.xlsx` file directly from filenames (saving a separate metadata lookup):

| Dataset | Pattern | Example | Parsed fields |
|---------|---------|---------|---------------|
| art.pics | `{id}_{style}.jpg` | `2542_dali.jpg` | style=dali, id=2542 |
| NimStim | `{face}_{emotion}_{view}.JPG` | `AF01ANFL.JPG` | sex=AF, identity=01, emotion=AN, view=FL |
| KDEF | similar NimStim-style | | |

For OSF repos without structured filenames, fetch the metadata subfolder (`art.pics meta-data` in the example above) for normative ratings — that spreadsheet IS your conditions file source.

## When OSF works vs doesn't

| Database type | OSF access | License | Direct download? |
|---------------|-----------|---------|------------------|
| art.pics (Frontiers 2020) | Public | CC with PI agreement | ✓ via API |
| KFS (Kitchen & Food Sounds, 2024) | Public | Springer OA | ✓ via API |
| Many Frontiers/PLOS supplementary data | Public | varies | ✓ via API |
| OSF-registered preregistrations + data | Public | varies | ✓ if no embargo |
| Embargoed data | Requires request | — | ✗ |
| License-gated (e.g. RaFD, NimStim) | Not OSF-hosted | Lab-specific | ✗ → see pitfall #32 |

## Audio dataset: MP4 container → WAV conversion pattern

Many OSF-hosted audio databases use **MP4 containers** (AAC audio in an MP4 wrapper), but PsychoPy's Sound component only supports `.wav`, `.mp3`, `.ogg`. Recipe:

```bash
# 1. Download MP4 files from OSF API (same pattern as images)
curl -sL -o "S1.mp4" "https://osf.io/download/<guid>/"

# 2. Convert to WAV with ffmpeg
ffmpeg -y -i S1.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 S1.wav

# 3. Remove the MP4 source
rm S1.mp4
```

Key flags: `-vn` drops video track, `-acodec pcm_s16le` produces uncompressed 16-bit WAV, `-ar 44100` sets sample rate PsychoPy handles reliably, `-ac 1` downmixes to mono (stereo works but mono halves file size with no perceptual loss for most kitchen/voice sounds).

### Worked example: KFS (kitchen/food sounds)

**Paper**: Saraiva, Guedes, Garrido & Prada (2024) "Normative ratings for the Kitchen and Food Sounds (KFS) database" — Behavior Research Methods 56:6967–6980. DOI: 10.3758/s13428-024-02402-7.

| Step | Result |
|------|--------|
| Fetch paper PDF | 840KB, 20 pages, https://link.springer.com/content/pdf/10.3758/s13428-024-02402-7.pdf |
| Find OSF URL | `osf.io/8jygx/` from paper's "Open Practices Statement" |
| List root | Folder `Stimuli set - 180 sounds/`, `Appendix 1.xlsx`, `Appendix 2.xlsx` |
| List stimuli folder | 26 MP4 files (S1-S27, gaps), ~160KB each, AAC audio |
| Convert to WAV | `ffmpeg -i S{n}.mp4 -vn -acodec pcm_s16le -ar 44100 -ac 1 S{n}.wav` → ~870KB each, ~14MB total |
| Spec from PDF Method | 9 rating dimensions (Valence, Familiarity, Intensity, Healthfulness, Appetizingness, Arousal, Sweet, Savory, Confidence), 7-point Likert, 30 sounds/subject (random subset of 180) |
| Generated `.psyexp` | 110KB, 13 routines, 1 loop, 1062 params, 0 loadFromXML errors |
| Runtime validated | 26/26 trials, ~10s audio each, simulated ratings, CSV logged |

Note: The OSF repo had 26 files (not the full 180 claimed in the paper). The paper states each participant rated only 30 randomly selected sounds, so a 26-sound subset is sufficient for replication.

## PyMuPDF / pdfplumber for PDF extraction

`<psychopy-install>\python\Lib\site-packages\pymupdf` is already installed with PsychoPy. Use:

```python
from pymupdf import open as pdfopen   # PsychoPy 2026.1.1 uses 'pymupdf' not 'fitz'
doc = pdfopen('paper.pdf')
text = ''.join(p.get_text() for p in doc)
```

If running from hermes venv, `pip install pymupdf` first or use `<psychopy-python>` directly which already has it.

## See also

- `references/paper-to-experiment.md` — the full hand-spec writing workflow
- `references/runtime-validation.md` — how to run an OSF-stimuli experiment end-to-end
- SKILL.md pitfall #32 — when the dataset is application-gated, not OSF-hosted
