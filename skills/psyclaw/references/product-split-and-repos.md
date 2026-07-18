# PsyClaw product split & repo map (2026-07-18)

## Two products

| Product | User | Deliverable | Must not |
|---------|------|-------------|---------|
| **psyclaw-webui** | Lab human | Install → window → run → CSV under `<project>/data/` | Bundle Hermes skill as install dep; force public without auth |
| **psyclaw** (agent skill) | Agents (Hermes / future CLIs) | Schema + scripts + SKILL narrative | Own the webui install surface |

## Identifiers

| What | Value |
|------|--------|
| Hermes skill id / slash | `psyclaw` → **`/psyclaw`** |
| WebUI skill / slash | `psyclaw-webui` → **`/psyclaw-webui`** |
| Path B helper | `/add-paradigm` |
| GitHub skill repo | `https://github.com/Paradeluxe/psyclaw-skill` (renamed from `PsyClaw`; redirect keeps old links) |
| GitHub webui (local origin) | `https://github.com/Paradeluxe/psyclaw-webui.git` (may be private; not in public list) |
| Hermes skill checkout | `~/.hermes/skills/research/psyclaw` · `origin` → `…/psyclaw-skill.git` |
| WebUI tree | `E:\hermes_playground\psyclaw-webui` |
| Papers / replications workspace | under `E:\hermes_playground\` (names `psyclaw` / `psyclaw-skill` may both appear after local copy); **not** the published skill contents |

## Path C success gate (unchanged)

G0 compile · G1 run finished · G2 CSV under **`<project>/data/`**.  
Full 150 benchmark: `output/webui_batch_validate_150/FINAL_SUMMARY.json` (pass_both=150).

## Cross-CLI readiness (honest)

**Enough for Hermes skill.** **Not enough** as a portable multi-CLI product:

- Need: stable design/spec schema (JSON Schema), installable CLI (`validate` / `compile` / `run`), zero hardcoded `E:\` / `~/.hermes` paths, examples that run without an agent.
- Optional: MCP adapter.
- SKILL.md is Hermes runbook (pitfalls, user prefs) — keep it; do not ship it as the only API.

## GitHub rename SOP (already done once)

1. Auth: Windows Credential Manager target `git:https://github.com` (user `Paradeluxe`) works with `git credential fill` → API Bearer token. Prefer not printing the token.
2. `PATCH /repos/Paradeluxe/PsyClaw` body `{"name":"psyclaw-skill"}`.
3. Update local skill `git remote set-url origin https://github.com/Paradeluxe/psyclaw-skill.git`.
4. **Do not** attach playground papers tree as that remote — different content.
5. Visibility stays as-is unless user explicitly asks to change public/private.
6. Push/tag/Release still need explicit user auth per standing rules.

## Local folder rename pitfall (Windows)

- Directory lock → `rename` / `mv` fails with “in use”.
- Robocopy copy to new name works; **deleting** the old tree is destructive — require user consent (“删旧 …”) after they close Explorer/IDE handles.
- Prefer fixing GitHub name first when user says “repo 上”; local playground is secondary.

## Handoff note (CLI ↔ QQ)

CLI and QQ are different chat pipes. `/resume <session_id>` if supported; else paste handoff summary. `hermes send` to qqbot: text OK, MEDIA attachments may fail — send body as message text.

## Slash vs repo name

| User says | Means |
|-----------|--------|
| `/psyclaw` | Load skill `psyclaw` |
| `psyclaw-skill` | GitHub repo name for the skill package |
| `psyclaw-webui` | Lab software product + `/psyclaw-webui` skill |
