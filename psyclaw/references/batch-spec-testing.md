# Batch testing: Path B (historical) + Path C webui (current paper gate)

## Path B era (2026-07-11) — loadFromXML only

Verified: **50/50 Category 1** specs pass `builder.py` + `loadFromXML` on PsychoPy 2026.1.1.

```python
"""Test all specs through builder.py + loadFromXML."""
import subprocess, sys
from pathlib import Path

PSYCLAW = Path(r"E:\hermes_playground\psyclaw")
REPLICATIONS = PSYCLAW / "replications"
BUILDER = PSYCLAW / "builder.py"
PSYCHOPY = r"D:\Software\P\python.exe"

results = []
for d in sorted(REPLICATIONS.glob("cat1_*")):
    spec = d / "spec.yaml"
    r = subprocess.run([sys.executable, str(BUILDER), str(spec)],
                      capture_output=True, text=True, timeout=30, cwd=str(PSYCLAW))
    if r.returncode != 0:
        results.append({"dir": d.name, "status": "build_fail"})
        continue
    psyexps = list(d.glob("*.psyexp"))
    if not psyexps:
        results.append({"dir": d.name, "status": "no_psyexp"})
        continue
    vfy = subprocess.run(
        [PSYCHOPY, "-c",
         f"from psychopy.experiment import Experiment; e=Experiment(); e.loadFromXML(r'{psyexps[0]}'); print('OK')"],
        capture_output=True, text=True, timeout=30,
    )
    status = "ok" if "OK" in vfy.stdout else "verify_fail"
    results.append({"dir": d.name, "status": status})

ok = sum(1 for r in results if r["status"] == "ok")
print(f"{ok}/{len(results)} OK")
```

**Caveat (pitfall #49):** `loadFromXML` 0 warnings ≠ runnable. Path B still needs `run_psyexp.py` smoke for ship.

## Path C era (2026-07-18) — RUN + data retention (paper gate)

Success = **G0 compile + G1 finished + G2 project CSV correct**.

```bash
cd /e/hermes_playground/psyclaw
# ensure webui up: curl -s http://127.0.0.1:8876/api/health
python scripts/spec_to_design_batch.py      # G0 all cat1/2/3
python scripts/headless_webui_sample.py     # G1 stratified sample
python scripts/data_retention_audit.py      # G2
```

| Gate | N | Result (2026-07-18) |
|------|---|---------------------|
| G0 design_compiler | 147 (50+47+50) | 147/147 |
| G1 headless | 15 stratified | 15/15 finished |
| G2 data retention | 15 | 15/15 project `data/` CSV with session+response+rt |

Evidence: `output/webui_batch_validate/{summary,headless_sample,data_retention_audit}.json`

G2 checks (each sample):
1. CSV path = `replications/<slug>/data/*.csv` (not only internal `runs/`)
2. Columns include `participant_id`, `session`, `session_date`, `trial`, `routine`, `response`, `rt`, `keys`
3. Condition keys from design stimlist appear in CSV
4. ≥1 trial-phase row with non-empty `response` and numeric `rt`
5. Session notes / participant_id preserved

## Common failures

| Failure | Cause | Fix |
|---------|-------|-----|
| `'list' object has no attribute 'keys'` | `response.keys` list vs dict | builder.py isinstance check (Path B) |
| `FileNotFoundError` subdirectory | paradigm name contains `/` | use `gonogo` not `go/no-go` |
| G1 finished but G2 fail | missing `project_path` on `/api/runs` | always pass absolute project folder |
| Empty response column | keyboard not in trial routine / force_end wrong | check design components |
| cat2 claimed 50 builds | only 47 replications present | report 47 honestly |

## Result summary

- Path B cat1 (2026-07-11): 50/50 loadFromXML
- Path C all cats (2026-07-18): 147/147 compile; 15/15 run+data on stratified sample
- Full 147 headless battery: not yet claimed (sample is stratified publication smoke)
