"""Headless runtime sample validation via psyclaw-webui /api/runs."""
from __future__ import annotations

import json
import time
import urllib.error
import urllib.request
from pathlib import Path

BASE = "http://127.0.0.1:8876"
OUT = Path(r"E:/hermes_playground/psyclaw/output/webui_batch_validate")
REPS = Path(r"E:/hermes_playground/psyclaw/replications")
OUT.mkdir(parents=True, exist_ok=True)

# Stratified sample: classic cat1 + materials cat2 + manual cat3
SAMPLES = [
    "cat1_flanker",
    "cat1_simon",
    "cat1_posner_cueing",
    "cat1_n-back",
    "cat1_go-no-go",
    "cat1_stroop" if (REPS / "cat1_stroop").exists() else "cat1_emotional_stroop",
    "cat1_lexical_decision",
    "cat1_serial_position",
    "cat1_dot_probe",
    "cat1_ax-cpt",
    "cat2_boundary_extension",
    "cat2_change_detection_real_scenes",
    "cat3_anchoring_effect",
    "cat3_availability_heuristic",
    "cat3_base_rate_neglect",
]


def req(method: str, path: str, body=None, timeout: int = 60):
    data = None
    headers = {}
    if body is not None:
        data = json.dumps(body).encode("utf-8")
        headers["Content-Type"] = "application/json"
    r = urllib.request.Request(BASE + path, data=data, headers=headers, method=method)
    with urllib.request.urlopen(r, timeout=timeout) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
        return json.loads(raw) if raw else {}


def cap_design(design: dict) -> dict:
    d = json.loads(json.dumps(design))  # deep copy
    for node in d.get("flow") or []:
        if node.get("kind") == "loop":
            node["nReps"] = 1
            conds = node.get("conditions") or []
            if len(conds) > 2:
                node["conditions"] = conds[:2]
    return d


def main() -> None:
    health = req("GET", "/api/health")
    print("health", health)

    results = []
    for name in SAMPLES:
        des = REPS / name / "design.psyexp"
        item = {"name": name}
        if not des.exists():
            item["status"] = "no_design"
            results.append(item)
            print("skip", name, "no_design")
            continue
        design = cap_design(json.loads(des.read_text(encoding="utf-8")))
        t0 = time.time()
        try:
            r = req(
                "POST",
                "/api/runs",
                {
                    "design": design,
                    "headless": True,
                    "project_path": str((REPS / name).resolve()),
                    "session": {
                        "participant_id": "P_autopilot",
                        "session": "1",
                        "participant_name": "batch_validate",
                        "notes": "publication validation sample",
                    },
                },
            )
        except urllib.error.HTTPError as e:
            body = e.read().decode("utf-8", errors="replace")[:500]
            item.update({"status": "post_fail", "detail": f"{e.code} {body}"})
            results.append(item)
            print("post_fail", name, e.code, body[:120])
            continue
        except Exception as e:
            item.update({"status": "post_fail", "detail": str(e)})
            results.append(item)
            print("post_fail", name, e)
            continue

        run_id = r.get("run_id") or r.get("id")
        item["run_id"] = run_id
        item["post"] = {k: r.get(k) for k in ("status", "source", "mode") if k in r}
        print("started", name, run_id)

        final = None
        for _ in range(120):
            time.sleep(1)
            try:
                st = req("GET", f"/api/runs/{run_id}")
            except Exception as e:
                final = {"status": "poll_fail", "detail": str(e)}
                break
            status = st.get("status")
            if status in ("finished", "failed", "stopped", "error"):
                final = st
                break
        if final is None:
            final = {"status": "timeout"}

        elapsed = round(time.time() - t0, 2)
        data_files = final.get("data_files") or []
        proj_data = []
        pdata = REPS / name / "data"
        if pdata.exists():
            proj_data = sorted(pdata.glob("*.csv"), key=lambda p: p.stat().st_mtime)
        # count rows in newest csv if any
        rows = None
        newest = None
        if proj_data:
            newest = str(proj_data[-1])
            try:
                text = Path(newest).read_text(encoding="utf-8", errors="replace")
                lines = [ln for ln in text.splitlines() if ln.strip()]
                rows = max(0, len(lines) - 1)
            except Exception:
                rows = None

        item.update(
            {
                "status": final.get("status"),
                "elapsed_s": elapsed,
                "data_files": data_files,
                "proj_csv_count": len(proj_data),
                "proj_csv_newest": newest,
                "csv_data_rows": rows,
                "error": final.get("error") or final.get("message"),
                "log_tail": str(final.get("log_tail") or "")[-400:],
            }
        )
        results.append(item)
        print(
            " ",
            name,
            item["status"],
            f"{elapsed}s",
            "rows",
            rows,
            "csv",
            len(data_files),
        )

    ok = sum(1 for r in results if r.get("status") == "finished")
    summary = {
        "n": len(results),
        "finished": ok,
        "failed": [r for r in results if r.get("status") != "finished"],
        "results": results,
    }
    (OUT / "headless_sample.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(f"HEADLESS {ok}/{len(results)}")
    for r in results:
        print(
            f"  {r.get('name')}: {r.get('status')} rows={r.get('csv_data_rows')} t={r.get('elapsed_s')}"
        )


if __name__ == "__main__":
    main()
