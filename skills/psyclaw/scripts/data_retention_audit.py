"""Publication-grade data retention audit on headless sample CSVs."""
from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path

REPS = Path(r"<psyclaw-workspace>/replications")
OUT = Path(r"<psyclaw-workspace>/output/webui_batch_validate")
hs = json.loads((OUT / "headless_sample.json").read_text(encoding="utf-8"))

REQUIRED_SESSION = {
    "participant_id",
    "session",
    "participant_name",
    "notes",
    "session_date",
}
REQUIRED_TRIAL = {"trial", "routine", "response", "rt", "keys"}


def main() -> None:
    audit = []
    for r in hs["results"]:
        name = r["name"]
        item = {"name": name, "status": r.get("status"), "checks": {}}
        path = r.get("proj_csv_newest")
        if not path or not Path(path).exists():
            data = REPS / name / "data"
            files = (
                sorted(data.glob("*.csv"), key=lambda p: p.stat().st_mtime)
                if data.exists()
                else []
            )
            path = str(files[-1]) if files else None
        item["csv"] = path
        if not path:
            item["ok"] = False
            item["fail"] = ["no_csv"]
            audit.append(item)
            continue

        p = Path(path)
        text = p.read_text(encoding="utf-8", errors="replace")
        rows = list(csv.DictReader(text.splitlines()))
        cols = set(rows[0].keys()) if rows else set()
        item["n_rows"] = len(rows)
        item["n_cols"] = len(cols)
        item["bytes"] = p.stat().st_size
        checks = item["checks"]
        checks["file_exists"] = True
        checks["bytes_gt_200"] = p.stat().st_size > 200
        checks["has_session_cols"] = REQUIRED_SESSION.issubset(cols)
        checks["has_trial_cols"] = REQUIRED_TRIAL.issubset(cols)
        checks["under_project_data"] = p.parent.resolve() == (REPS / name / "data").resolve()

        pids = {row.get("participant_id") for row in rows}
        checks["pid_autopilot"] = "P_autopilot" in pids

        trial_rows = [
            row
            for row in rows
            if row.get("routine") and row.get("routine") not in ("instructions", "thanks")
        ]
        resp_rows = [row for row in trial_rows if (row.get("response") or "").strip()]
        item["n_trial_phase_rows"] = len(trial_rows)
        item["n_response_rows"] = len(resp_rows)
        checks["has_response_rows"] = len(resp_rows) >= 1

        design_path = REPS / name / "design.psyexp"
        if design_path.exists():
            design = json.loads(design_path.read_text(encoding="utf-8"))
            conds = []
            for node in design.get("flow") or []:
                if node.get("kind") == "loop":
                    conds = node.get("conditions") or []
                    break
            if conds:
                sample_keys = set(conds[0].keys())
                checks["cond_cols_present"] = bool(sample_keys.intersection(cols))
                item["cond_keys"] = sorted(sample_keys)
            else:
                checks["cond_cols_present"] = True
        else:
            checks["cond_cols_present"] = False

        rts_ok = True
        for row in resp_rows:
            try:
                float(row.get("rt") or "nan")
            except Exception:
                rts_ok = False
        checks["rt_numeric"] = rts_ok if resp_rows else False

        notes = {row.get("notes") for row in rows}
        checks["notes_preserved"] = any(
            "publication validation" in (n or "") for n in notes
        )

        routines = Counter(row.get("routine") for row in rows)
        item["routines"] = dict(routines)
        checks["has_instructions"] = "instructions" in routines
        checks["has_thanks"] = "thanks" in routines

        fails = [k for k, v in checks.items() if not v]
        item["ok"] = not fails
        item["fail"] = fails
        audit.append(item)

    ok_n = sum(1 for a in audit if a.get("ok"))
    summary = {"n": len(audit), "pass": ok_n, "fail": len(audit) - ok_n, "items": audit}
    (OUT / "data_retention_audit.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"DATA_RETENTION {ok_n}/{len(audit)}")
    for a in audit:
        mark = "OK" if a.get("ok") else "FAIL"
        print(
            f"  {mark} {a['name']}: rows={a.get('n_rows')} resp={a.get('n_response_rows')} fail={a.get('fail')}"
        )


if __name__ == "__main__":
    main()
