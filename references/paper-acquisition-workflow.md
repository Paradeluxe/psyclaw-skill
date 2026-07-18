# Paper Acquisition Workflow — three-category classification + batch PDF download

## Three-category classification (2026-07-11)

PsyClaw实验文章分三类：

| 类 | 描述 | 示例 | 材料来源 |
|---|------|------|---------|
| 1 | 纯PsychoPy生成 | Stroop, Flanker, N-back, Simon, Posner | 无需外部材料 |
| 2 | PsychoPy + 可下载材料 | 情绪面孔识别(CFD/RaFD), OASIS图片评分, food-pics | OSF/开放数据库 |
| 3 | 能做框架，材料用户自备 | 道德判断(vignettes), 词表记忆(语言特定), KDEF(需申请) | 用户手动制作/查找 |

## Category 3 selection rules

必须满足全部条件：
- **人类实验**（非动物：Thorndike猫、Gallup猩猩、Pavlov狗 ❌）
- **可计算机化**（非物理道具：Marshmallow棉花糖、Visual Cliff视觉悬崖 ❌）
- **实验而非量表**（BDI、STAI、MMPI、PANAS是临床量表 ❌）
- **实验而非综述/理论**（Öhman & Mineka 2001综述、Zajonc 1965理论 ❌）
- **实验而非演示**（Müller-Lyer错觉无标准实验论文 ❌）

## Batch PDF download: sci-hub CDP primary, Scholar+bsk fallback

### Prerequisites
- Chrome with `--remote-debugging-port=9222`
- `websockets` Python package
- `scihub_cdp_pdf.py` from academic-pdf-fetch skill

### Workflow

1. **Start Chrome CDP** (background):
```bash
"/c/Program Files/Google/Chrome/Application/chrome.exe" \
  --remote-debugging-port=9222 \
  --user-data-dir="C:/Users/User/AppData/Local/chrome-debug-profile" \
  --no-first-run --no-default-browser-check "about:blank"
```
Verify: `curl -s http://127.0.0.1:9222/json/version`

2. **Single paper**:
```bash
python scihub_cdp_pdf.py "10.1037/h0054651" --output stroop_1935.pdf
```
First paper ~8s (Altcha solve), subsequent ~3s (cookie reuse).

3. **Batch papers** (loop via subprocess):
```python
for doi, out in papers:
    subprocess.run([sys.executable, SCRIPT, doi, '--output', out], timeout=60)
```

4. **Scholar+bsk fallback** (only for sci-hub failures):
- Navigate: `bsk navigate "https://scholar.google.com/scholar?q=<DOI>"`
- Snapshot: find `[PDF]` link ref
- Click: `bsk click @eN`
- Get URL: `bsk evaluate "JSON.stringify({url: location.href})"`
- Download: `curl -sL -o out.pdf <url>`

**Reality**: most Scholar `[PDF]` links point to publisher paywalls. Real OA PDFs are rare for pre-2010 papers. Scholar is useful for DOI discovery (search by title → find correct DOI), not for direct PDF access.

### Direct OA publishers (skip sci-hub)

| Publisher | URL pattern | Time |
|-----------|------------|------|
| PLOS ONE | `journals.plos.org/plosone/article/file?id=<DOI>&type=printable` | ~3s |
| eLife | `elifesciences.org/articles/<id>.pdf` | ~3s |
| Frontiers | `frontiersin.org/articles/<DOI>/pdf` | ~3s |

### Pitfalls

1. **MSYS path mangling**: On Windows git-bash, `/e/path/file.py` becomes `E:\e\path\file.py`. Always use `E:/path/file.py` or `"E:\path\file.py"` in terminal commands.

2. **Chrome CDP exits**: Chrome started with `--remote-debugging-port` may exit after a few minutes if no tabs are kept open. Always open `about:blank` and verify CDP is alive before batch operations. Restart if needed.

3. **Wrong DOIs**: The classic paper index has incorrect DOIs:
   - Simon 1969: `10.1037/h0027444` → `10.1037/h0027448` (h0027444 is auditory signal paper)
   - Corsi Block: ugly DOI → `10.1207/S15324826AN0704_8` (found via Scholar title search)
   Always verify via Scholar search if sci-hub fails on a DOI.

4. **Sci-hub Altcha solve**: The `scihub_cdp_pdf.py` script handles this automatically in the browser. First paper in a batch takes ~8s (PoW solve), rest reuse the session cookie (~3s each). If Chrome dies mid-batch, restart Chrome and resume — the script creates a new tab and re-solves Altcha.

5. **Batch durability**: ~50 papers take ~4-5 minutes via sci-hub CDP. Run with `background=true` + `notify_on_complete=true`. The batch is resumable — already-downloaded files are skipped.

6. **Small PDFs**: Some sci-hub PDFs are incomplete (1 page only, e.g. Kosslyn 1978 at 27KB). Check page count with `fitz.open(path).page_count`. Replace papers with <2 pages.
