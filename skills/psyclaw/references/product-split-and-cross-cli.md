# Product split + cross-CLI readiness (2026-07-18+)

## Two products (HARD)

| Product | Canonical location | Hermes | Audience |
|---------|-------------------|--------|----------|
| **Skill** | GitHub **`Paradeluxe/psyclaw-skill`**; local **`~/.hermes/skills/research/psyclaw`** (origin → that repo) | id + slash **`/psyclaw`** (`name: psyclaw` — **not** `/psyclaw-skill`) | Agents: intent → **`<folderName>.psyclaw`** |
| **WebUI** | `<psyclaw-webui-repo>` · `Paradeluxe/psyclaw-webui` | **`/psyclaw-webui`** | Humans: GUI → run → CSV |

### Path confusion (session 2026-07-18)

| Path | Role | Edit for `/psyclaw`? |
|------|------|----------------------|
| Hermes `skills/research/psyclaw` + GitHub `psyclaw-skill` | **Skill package** (SKILL.md, scripts, templates) | **YES** |
| `<psyclaw-workspace>` (papers / replications / builder) | **Research workspace** — name collision risk; often no skill remote | **NO** |
| Legacy `<psyclaw-workspace>` | Old workspace alias | NO |

User: product/repo name may be `psyclaw-skill`; **slash stays `/psyclaw`**.

- Do **not** merge trees or ship one public blob of skill+webui+PDFs.
- Skill = AI narrative attachment — not a required webui pip dep.
- **No tag/push** without explicit ok (skill GitHub may already be public).

## IR / deliverable

Canonical project marker (webui + skill output): **`<folderName>.psyclaw`** (JSON).  
Legacy webui `design.psyclaw` migrates on open/save. Not PsychoPy Builder XML.

## Skill pipeline (simple)

```
Input: (1) user NL  (2) PDF/HTML/material text  (3) existing folder.psyclaw
  → optional: browser-skill / academic-search to FETCH materials (related, not merged)
  → write/validate <folderName>.psyclaw
  → optional handoff webui for G1/G2 run+CSV
```

Default skill success = **G0** (valid design). G1/G2 = webui/runner when asked.

## Cross-CLI “is the repo enough?”

**As Hermes skill:** strong (paths A/B/C, pitfalls, 150/150 Path C evidence).

**As cross-CLI product (Codex / Claude Code / OpenCode / generic agents):** **not yet packaged.**

Portable surface that would qualify:

1. Stable **schema** (JSON Schema for design / YAML for Path B) as first-class artifact
2. Installable **CLI**: validate / compile / run (no `E:\` or `~/.hermes/skills/...` hardcodes)
3. Documented I/O + examples runnable without Hermes
4. Optional **MCP** adapter — not Hermes `SKILL.md` as the only interface
5. Clean package: LICENSE, pyproject, no scihub/lab scrapers on the public surface

Current gaps: three paths mixed in one narrative; workspace is research dump + agent runbook; `python -m psyclaw.runner` promised in LAYOUT but not a real installable package; no formal cross-agent schema publish.

When user asks “够格了吗 for cross-CLI skill”: answer with this split — evidence strong, packaging incomplete.

## Nature-style pattern (user asked)

Like `nature-figure`: **skills install = light cookbook**; large runtimes (Python/R or PsychoPy/webui) **external**; first use **detect missing → install/prompt**, do not silent-fail to a fake substitute.

## Routing

- UI / Pilot / CSV / :8876 → `psyclaw-webui`
- Replicate paper / builder.py / replications → `add-paradigm` + playground workspace
- Edit skill / market / `/psyclaw` behavior → Hermes skill dir + GitHub `psyclaw-skill`
- Fetch papers/pages → **`browser-skill`** (related), not baked into every step
- Install/market short-name → `references/install-orchestrator.md` + `references/product-pipeline-and-hermes-market.md`
