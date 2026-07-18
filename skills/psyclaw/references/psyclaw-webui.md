# psyclaw-webui — Path C architecture (2026-07-13)

Web-based experiment builder. Skips `.psyexp` XML entirely. Flask SPA +
paradigm-agnostic backend. Lives at `E:\hermes_playground\psyclaw-webui\`,
git `https://github.com/Paradeluxe/psyclaw-webui` (private).

## Why this exists

PsychoPy Builder's GUI is a mess (see `psychopy-platform-pitfalls.md`).
psyclaw-webui is the alternative: a web UI that takes a paradigm spec and
generates a pure Python PsychoPy script. No `.psyexp` roundtrip, no
`loadFromXML()` silent bugs, no missing CLI entry.

## Three-layer model

```
Browser (HTML/JS form)
        |
        v
Flask backend (paradigm loader + run state machine + CSV download)
        |
        v
Pure Python script using psychopy.visual / core / event
```

A paradigm is **a yaml file**, not Python code. Adding a paradigm =
dropping a yaml in `examples/`. Platform never references paradigm names.

## Layout

```
E:\hermes_playground\psyclaw-webui\
├── docs/CONTRACT.md            # contract for subagent fan-outs (READ FIRST)
├── backend/
│   ├── app.py                  # factory + /api/health + serves frontend/
│   ├── api/routes.py           # all /api/* endpoints (CONTRACT surface)
│   ├── paradigms/loader.py     # yaml schema validate + discover_all() cache
│   └── runner/                 # state.py + process.py (MockProcess for now)
├── frontend/
│   ├── index.html              # 3 tabs (Experiment / Flow / Run)
│   ├── app.js                  # paradigm load + form bind + Run tab wiring
│   ├── forms.js                # window.PsyClawForms (bindForm/readForm/validate)
│   └── style.css               # dark theme, palette per CONTRACT
├── examples/
│   ├── stroop.yaml             # 13 fields
│   └── gonogo.yaml             # 12 fields
├── tests/test_loader.py        # 11 tests, schema + multi-paradigm
└── requirements.txt            # flask, pyyaml, pytest, lxml
```

## API surface (CONTRACT.md)

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/health` | liveness probe |
| GET | `/api/paradigms` | `[{id, label, order?}]` |
| GET | `/api/paradigm/<id>/form` | `{html, schema}` (server-rendered form) |
| POST | `/api/paradigm/<id>/submit` | echo spec + validation errors |
| POST | `/api/runs` | body `{paradigm_id, spec}` → `{run_id, status}` |
| GET | `/api/runs` | list all runs (in-memory + rehydrated from disk) |
| GET | `/api/runs/<id>` | `{status, progress, log_tail, data_files}` |
| POST | `/api/runs/<id>/stop` | request stop |
| GET | `/api/runs/<id>/data/<file>` | CSV stream |

## Run lifecycle (state machine)

```
created → compiling → compiled → running → (finished | failed | stopped)
```

Each transition appended to `runs/<id>/events.jsonl`. Current state in
`runs/<id>/state.json`. Process writes CSV to `runs/<id>/data/`.

`MockProcess` in `runner/process.py` simulates the lifecycle in ~3 seconds.
Replace with real `subprocess.Popen([D:\Software\P\python.exe, ...])` to
launch actual PsychoPy experiments — interface is already drop-in.

## Paradigm yaml schema

```yaml
id: unique-id                 # required
label: "Human Label"          # required
description: "..."            # optional
version: "1.0"                # required
order: 1                      # optional, controls dropdown default order

fields:                       # required, non-empty
  - name: field_name          # required, unique within paradigm
    label: "Field Label"      # required
    type: text | number | checkbox | textarea | select | multiselect | color | slider
    default: ...              # type-appropriate default
    required: true | false    # optional, default false
    min: 0                    # number only
    max: 100                  # number only
    options: [a, b, c]        # select/multiselect only

runtime:                      # optional
  script_template: name.py.j2 # informational only
  timing: { fixation_ms: 500 }
  loop: { type: random }
```

Adding a paradigm: drop a yaml in `examples/`. No platform code change.
Discoverer auto-loads on next server start.

## Verified end-to-end

2026-07-13, after commit `fbcb910`:
- 11/11 pytest pass
- `/api/health`, `/api/paradigms`, `/api/paradigm/<id>/form` all 200
- POST /api/runs with valid spec → run created, lifecycle to finished in ~3s
- GET /api/runs/<id>/data/trials.csv returns valid CSV
- Browser: paradigm dropdown loads stroop (default) + gonogo
- Browser: switching paradigm re-renders form fields, spec preview updates
- Browser: Run tab Start button → polling → finished → Download CSV enabled

## Critical pitfalls (learned)

1. **`send_from_directory` needs Windows path** — `os.path.normpath()` over
   `os.path.dirname(__file__)`; MSYS `/e/...` strings fail.
2. **Subagent fan-outs over bsk hang** — bsk daemon becomes unresponsive
   in subagent contexts; tasks time out at 600s even though their code is
   written. Tell subagents: curl/pytest only, parent runs bsk.
3. **forms.js `$$(selector, form)` argument order** — `$$(form, sel)`
   is the right call. Reversed call silently breaks at first paradigm load
   with `form.querySelectorAll is not a function`.
4. **Multi-subagent file ownership violations** — subagent 2 (forms.js)
   overwrote subagent 3 (backend) and vice versa. Always re-read files
   before patching if any sibling subagent may have touched them.

## How to extend

**Add a paradigm:** write `examples/<name>.yaml`. Done.

**Add a new Component type:** patch `routes.py` form renderer (currently
text/number/checkbox/textarea/select — handle the others if you need them).

**Replace MockProcess with real PsychoPy:** edit `runner/process.py`. The
interface (`start()`, `join()`, `returncode`) is stable; just Popen a
subprocess running a compiled Python script with `D:\Software\P\python.exe`.

**Connect to dFC paper data:** the CSV format (`runs/<id>/data/trials.csv`)
matches what your existing analysis scripts expect. Add a "Upload to
project" button that copies the file to your Telegram-bot or paper folder.

## Status

MVP+ committed. Next: real PsychoPy subprocess (replace MockProcess),
then real experiment data flows to dFC paper pipeline.