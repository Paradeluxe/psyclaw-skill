# One install + first-use doctor (2026-07-18)

## Hard split

| Mechanism | Installs | Does **not** install |
|-----------|----------|----------------------|
| **Skill install** | Skill files → `psyclaw` only | webui, Flask venv, PsychoPy |
| **Lab software install** | **psyclaw-webui** + its deps; **PsychoPy only when webui’s install/update docs say so** | AI agent / skill files |
| **`psyclaw setup` / `install.py` (planned)** | Orchestrates skill + webui doctor | Skill must **not** freestyle-upgrade PsychoPy |

**Never claim** skills install alone deploys the GUI.

**PsychoPy ownership:** belongs to **webui**, not the skill. Skill never `pip install -U psychopy` on its own. If webui release notes / INSTALL / optional requirements do not ask for a PsychoPy bump, leave PsychoPy alone (probe “present?” only when running subjects).

## First use = doctor (user confirmed)

On first use (or when user says 全装 / 部署):

1. Check skill-side small deps / scripts runnable.
2. Check webui present (path or import) **if** lab software needed this turn.
3. **If run needed:** only probe whether a PsychoPy interpreter resolves (env → library → standalone). Missing → point at **webui** `docs/INSTALL.md` (do not invent a skill-side PsychoPy upgrade path).
4. Missing skill/webui → report + **ask consent** → install only those gaps.
5. Present → skip; do the task (write `<folderName>.psyclaw`).

Not every turn reinstalls. See **Update stack** below when the user asks to update.

## Two update entry points (nested)

```text
更新 skill / 更新 psyclaw
  ├─ 1. psyclaw skill 本身（本 CLI）
  ├─ 2. related skills / companion software（如 browser-skill，在用才更）
  └─ 3. psyclaw-webui  ← 走下面「更新 webui」整段
           ├─ webui 代码
           ├─ Flask venv 依赖
           └─ PsychoPy 仅当 webui 本版要求

更新 webui
  ├─ webui 代码
  ├─ Flask venv 依赖
  └─ PsychoPy 仅当 webui 本版要求
  （不碰 skill）
```

**接上关系：** skill 更新 **包含** 执行 webui 更新；webui 更新 **包含** 它自己的库。不是“只提醒不管”。

### Triggers

| User says | Scope |
|-----------|--------|
| 更新 skill · 升级 psyclaw · update psyclaw | **Full skill entry**: skill + related + **webui 整段** |
| 更新 webui · 升级实验室软件 | **Webui entry only** (code + libs + conditional PsychoPy) |
| 全装 / 首次 | First-use doctor（另文） |

### A — 更新 skill（必须做完才算成功）

1. **Skill 本身** — 本 CLI 的 `psyclaw` 对齐上游（`Paradeluxe/psyclaw-skill` → `skills/psyclaw/`）。
2. **Related** — `related_skills`（如 browser-skill）已装或本轮需要 → 一并更新；不用则跳过并注明。
3. **Webui 整段** — 执行下面 **B**（同一轮，不是只甩一句提醒）。找不到 clone → 问路径或按 INSTALL 部署，不得静默跳过。
4. 汇报表：skill / related / webui（+ 若 B 动了 PsychoPy）— 已新 / 已更 / 失败 / 跳过原因。
5. 禁止在 webui 未处理时声称「psyclaw 已更新完成」（用户明确放弃 webui 除外）。

### B — 更新 webui（被 A 调用，或用户只说更新 webui）

Follow **psyclaw-webui `docs/INSTALL.md` § Update** (canonical):

1. `git pull` webui 仓库。
2. 其 venv：`pip install -r requirements.txt`（pull 后例行一次）。
3. **PsychoPy** — **仅当** 该节 / changelog / 可选 req 写明要升；否则 **不动**。
4. 若 Flask 在跑 → 重启。
5. **不**更新 skill。

### Rules

1. Skill 入口 **嵌套** webui 入口；webui 入口 **嵌套** 自身依赖（含条件 PsychoPy）。
2. Skill **不**自己发明 PsychoPy 升级；只通过 B、且听 webui 文档。
3. Skill 文件 = 本 CLI；webui = 本机一份（对所有 CLI 共用）。
4. 网络操作按用户政策要同意；可一批：「将更新 skill、related、webui」。
5. 普通 做一个… / 改… → 不走更新。

## Skill installation (short name)

Resolver: search all sources → **exact** `name == psyclaw` → exactly one match installs.

To make short name work for others:

1. `name: psyclaw` in SKILL.md  
2. Repo layout: `skills/psyclaw/` (this repo)  
3. Public git push; register in skill registry  
4. Avoid multiple exact name collisions  

Full id (always): `Paradeluxe/psyclaw-skill/skills/psyclaw`  
Short: `psyclaw` after unique registry resolve.

Maintainers edit `skills/psyclaw/` in this repository; end users install via their agent's skill installer.

## Orchestrator steps (when script exists)

0. Install root  
1. Install skill (`Paradeluxe/psyclaw-skill/skills/psyclaw`) (+ optional browser-skill)  
2. Clone webui  
3. webui venv + `requirements.txt`  
4. PsychoPy **only per webui INSTALL** (library preferred); else probe and stop with webui doc link if missing  
5. Doctor (flask, psychopy import, :8876)  
6. Print skill name, paths, start URL  

Agent on「帮我全装」: run orchestrator order; do not random soup. Network/clone: consent if user requires.

## Skill registry (brief)

- Browse sources: official registries, GitHub, skill directories  
- Team share: add repo source then install `psyclaw`  
- `related_skills` recommends; does not auto-install  

Registry/short-name notes: this file.

## Layer roadmap

| Layer | Shape |
|-------|--------|
| A | git + venv + webui INSTALL.md |
| B | pip entry `setup|doctor|start` |
| C | zip / start.bat |

PsychoPy external every layer.
