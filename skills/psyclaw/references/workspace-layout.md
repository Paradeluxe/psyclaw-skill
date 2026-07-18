# Workspace layout (generic)

Skill package and experiment workspace are **separate**.

| Role | Typical location | Contents |
|------|------------------|----------|
| **Skill package** | Hermes skills dir after install (`~/.hermes/skills/.../psyclaw` or profile equivalent) | `SKILL.md`, `scripts/`, `references/`, `templates/` |
| **GitHub skill source** | Clone of `Paradeluxe/psyclaw-skill` (path `skills/psyclaw/`) | Same tree; edit here to publish |
| **Experiment workspace** | Any project folder you choose | Papers, `replications/`, generated `.psyclaw` / `.psyexp`, data |
| **WebUI product** | Separate repo `psyclaw-webui` (not bundled in this skill) | GUI + runner |

## Rules

1. Do **not** put large PDFs or participant data inside the skill package.
2. Do **not** hardcode one lab's absolute drive letters in docs or scripts — use env vars / discovery:
   - `PSYCLAW_PSYCHOPY_PYTHON` → PsychoPy's Python
   - project path from user / CLI `--out-dir`
3. Marker handoff: `<projectFolder>/<folderName>.psyclaw` next to the experiment, not under the skill tree.

## PsychoPy binary

```bash
export PSYCLAW_PSYCHOPY_PYTHON=/path/to/psychopy/python
"$PSYCLAW_PSYCHOPY_PYTHON" -c "from psychopy.experiment import Experiment; print('ok')"
```

Or discover a local PsychoPy install; never assume a single machine path.
