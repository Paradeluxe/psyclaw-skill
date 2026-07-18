# Publication framing (user 2026-07)

## What ships to labs

| Artifact | Role |
|----------|------|
| **psyclaw-webui** | Installable lab product: Builder → run → project `data/` CSV |
| **Hermes `psyclaw` skill** | Optional **AI-driven build** narrative (NL / paper → design). **Not** a runtime dependency. |

User agreed: skill is an attachment for the “AI 建实验” story; main choice for researchers is the webui.

## Do not public-ship

- `papers/**` PDFs (copyright) — DOI/metadata lists + designs only
- Hard lab-only PsychoPy path as the only install story
- Unsolicited git public / tag / visibility change

## Evidence (internal)

- Path C gates G0/G1/G2: **150/150** (2026-07-18) — `output/webui_batch_validate_150/FINAL_SUMMARY.json`
- WebUI packaging skeleton: webui `LICENSE`, `docs/INSTALL.md`, `docs/RELEASE_CHECKLIST.md`, `backend/psychopy_env.py`
- Detail: skill `psyclaw-webui` → `references/release-packaging.md`

## When user says “发布骨架 / 没准备好”

Prepare files only. No push/tag/public.
