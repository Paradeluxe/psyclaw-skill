# WebUI handoff (index)

Skill writes **`<folderName>.psyclaw`**. After marker ready, ask 要跑被试吗 if session `ask_run` is still `null`. Yes → lab app **psyclaw-webui** (sequential subjects → CSV).

| Load | When |
|------|------|
| [`run-prep.md`](run-prep.md) | ask-run yes — **user-facing** 4-line checklist + done ticks |
| [`api-notes.md`](api-notes.md) | calling webui / compile / CSV / API |
| [`failure-playbooks.md`](failure-playbooks.md) | paywall, webui down, compile fail, missing CSV, lost session |
| [`marker-validate.md`](marker-validate.md) | after write/edit |
| [`marker-stub.psyclaw`](marker-stub.psyclaw) | new marker shape |

**Out of scope:** half-run lab mode (Builder PREVIEW ≠ participant run).

**Related:** `Paradeluxe/psyclaw-webui` · pipeline `skill-pipeline.md` · state `session-state.md`
