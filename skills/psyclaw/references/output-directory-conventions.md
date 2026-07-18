# Per-paradigm output directory (2026-07-05)

User asked "测试数据和脚本单独放一个子文件夹？" — answer: yes,
`output/` subfolder per paradigm. Don't dump CSVs to a flat
`<psyclaw-workspace>\output\<paradigm>\` tree.

## Per-paradigm layout

```
replications/<paradigm_slug>/
├── <name>_runner.py
├── spec.yaml              # if using YAML-driven flow
├── README.md
└── output/                # gitignored, per-subject CSVs
    ├── subj_ID01_trials.csv
    ├── subj_ID02_trials.csv
    └── ...
```

Why inside-paradigm, not a global `<psyclaw-workspace>\output\`
tree:

1. **git checkout portability.** Each paradigm dir is self-contained.
   You can `zip -r replications/<slug>` and ship to a colleague; the
   data travels with it.
2. **No name clashes.** Two paradigms can't shadow each other's
   `summary.csv` because each owns its own dir.
3. **`.gitignore` one-liner.** Add `**/output/` once at repo root.
4. **Mass-factory cleanup.** The old `mass_factory*.py` scripts wrote
   to `<psyclaw-workspace>\replications/<slug>/data/`
   already, so this isn't actually new — we just unified on
   `output/` (not `data/`) and dropped stub data.

## gitignore snippet

```gitignore
# Trial-level data (per paradigm)
**/output/

# PsychoPy temp
*.pyc
__pycache__/
*.log
```

## Backwards compat

If mass-factory scripts (which are still on disk 2026-07-05) wrote
CSVs to `replications/<slug>/data/`, those files are stale and can be
deleted. New runner.py output goes to `output/` exclusively.

Old path that's now obsolete:
```bash
<psyclaw-workspace>/output/stroop_1935_exp2/   # moved/removed
```

New path:
```bash
<psyclaw-workspace>/replications/stroop_1935_exp2/output/
```
