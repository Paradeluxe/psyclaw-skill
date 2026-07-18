# Legacy GUI history — preserved for context, NOT active

PsyClaw **had** a browser-based GUI (`psyclaw.html`, ~450KB) on a `with-chatbot` branch through May 2026. The GUI hosted an inline flowchart editor + AI chatbot (multiple providers via dropdown) + `FileSystemDirectoryHandle` project folder selection.

**As of 2026-06-24 the GUI is deprecated and the product is conversational only** — users talk to Hermes, Hermes runs the pipeline. The `psyclaw-setup` skill (which held all GUI-specific content) has been folded into this skill and is now empty/redundant; deleted via `hermes curator delete psyclaw-setup`.

## Why the GUI was abandoned (lessons worth keeping)

### Cross-script-block `const`/`let`/`class` redeclaration silently kills an entire `<script>` block
Two separate `<script>` blocks in the same HTML both declared `const ALLOWED_ORIGIN` → browser threw `SyntaxError` and discarded the whole second block. Every function inside (`checkAvailableModels`, `sendMessage`, `selectProvider`, …) appeared `undefined` at runtime. `node --check` on extracted script shows "PARSE OK" because it parses in isolation. Diagnostic: `browser_console typeof functionName` — all expected functions undefined → grep for duplicate top-level `const`/`let`/`class` across script blocks.

### `showDirectoryPicker()` is a native OS dialog
Playwright / CDP / Selenium cannot click it. The only agent-automatable workaround was a text input + "Use Path" button (`setProjectFolderByPath()`). Even that required the user to have selected the folder manually at least once (so the `FileSystemDirectoryHandle` existed in IndexedDB — text-input path doesn't grant permissions).

### Chatbot iframe → inlined chat caused merge hell
The `with-chatbot` branch tried to keep chatbot.html separate and postMessage into an iframe. May 2026 attempt to inline it produced two ~4500-line script blocks with duplicate top-level identifiers. Inlining worked after the `ALLOWED_ORIGIN` fix but the codebase was already brittle.

### GUI version drift between PsychoPy releases
`json2psyexp.js` upstream still emits 3 params PsychoPy 2026.1.1 doesn't recognise (`anchor` on Text/Movie components, `stopWithRoutine` on Keyboard, plus a `flip` false positive). Vendored copy in this skill patched; do not blindly upgrade.

### "Open a file" exposed every GUI bug at once
That flow (load psclaw.html → show modal → IndexedDB handle → showOpenFilePicker → render flowchart) touches `localStorage` persistence, OS dialog handling, IndexedDB retrieval, and postMessage/file-handle plumbing all at once. Useful as an integration smoke test if you ever resurrect the GUI.

## Legacy artefacts (do not use, preserved for archaeology)

- `psyclaw.html` (449KB, 2026-05-27 master) — flowchart editor only, chatbot code stripped (commit `ff386cd`)
- `psyclaw_patched.html` (702KB, 2026-05-18) — `with-chatbot` branch snapshot
- `DESIGN.md`, `deeppsych_project_1.psyexp`, `flowchart.schema.json` — original 2026-Q2 design artifacts
- Local server for legacy GUI testing (archived): `cd /mnt/e/ProjLegacy/DeepPsych && python3 -m http.server 8080`

These all live under `/mnt/e/ProjLegacy/DeepPsych/`. `git checkout with-chatbot` on the upstream repo will restore the GUI; this skill will not.