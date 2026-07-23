# psyclaw-webui — Design system (canonical)

Governing visual + UI rules for this repo. Prefer this over inventing new chrome.
Product scope: `PRODUCT.md`. API/forms: `CONTRACT.md`.

---

## 1. Product posture

- **Mission-control / SpaceX density**, not “PsychoPy but dark,” not academic gray.
- Local harness: configure → probe host → run PsychoPy on this machine.
- **Builder is primary**; System / Run / Settings / Guide are peers with the same language.

| Surface | Role |
|---------|------|
| **Builder** | Palette, timeline, flow, inspector |
| **System** | Host profile, Display / Mic / Speaker, live probes |
| **Run** | Session, pilot / start, CSV |
| **Settings / Guide** | Prefs and docs |

Port **8876** (8765 = Mentor — never reuse).

---

## 2. Tokens (`frontend/style.css` `:root`)

Use CSS variables. Do not hardcode one-off sizes for text or spacing on new UI.

### Color

| Token | Role |
|-------|------|
| `--void` / `--bg` | Page black |
| `--surface` / `--surface-2` / `--surface-3` | Cards / elevated |
| `--line` / `--line-2` | Hairlines only |
| `--text` / `--text-dim` / `--text-ghost` | Primary / secondary / tertiary |
| `--red` / `--red-soft` / `--red-glow` | **Single accent** (actions, active, eyebrows) |
| `--ok` / `--warn` | Status only |

No extra brand colors (no cyan/blue rails for “flavor”) unless telemetry status needs it.

### Type scale

| Token | Size | Typical use |
|-------|------|-------------|
| `--fs-2xs` | 11px | Mono meta, status chips, host hint |
| `--fs-xs` | 12px | Eyebrow, field labels, small mono |
| `--fs-sm` | 13px | Card `h3` titles, body secondary, selects |
| `--fs` | 15px | Page body default |
| `--fs-md` | 16px | Emphasized body |
| `--fs-lg` / `--fs-xl` | 18 / 24 | Page titles (`h2`) |

Fonts: `--font` (UI), `--mono` (telemetry, eyebrows, numbers).

### Space & radius

| Token | Value |
|-------|-------|
| `--space-1` … `--space-5` | 6 / 10 / 14 / 18 / 24 |
| `--radius` | **3px** (sharp mission chrome; avoid large soft radii on cards) |

---

## 3. Card language (all tabs)

### Structure

```
┌─ surface + 1px --line + --radius ─────────────┐
│ panel-heading  (one hairline under title)     │
│ body inset = --space-3                        │
│ rows / content                                │
└───────────────────────────────────────────────┘
```

### `.panel-heading` (canonical)

- **One line**: red **eyebrow** (small) + **h3** title (large white) (+ optional trailing meta).
- Eyebrow: mono, uppercase, `--fs-2xs` (~10), letter-spacing ~0.18em, `--red`.
- `h3`: `--font`, `--fs-lg` (~16–18), weight **600**, letter-spacing **~-0.02em**, **no** uppercase, color **`--text` (white)**.
- Page `h2` in `.panel-heading-row`: same white-large idea (`--fs-xl` ~20, weight 600).
- **Single** `border-bottom: 1px solid var(--line)` under the heading.
- Do **not** shrink card titles back to uppercase micro/dim telemetry — that killed the e675eba “红小字 + 白大字” read.

### Separators (no double lines)

- **One** hairline per logical boundary.
- Prefer either row `border-bottom` **or** a following block `border-top`, **never both** on the same edge.
- `:last-of-type` is unsafe when a non-row sibling (e.g. host hint) follows — use `:last-child` or `:has(+ .next)`.
- Card outer border is enough; do not add a second full-card outline.

### Fields

- Row: `label | control` grid; labels `--fs-xs` / `--text-dim`.
- Controls: void fill, `--line-2` border, `--radius`, height ~34px, text `--fs-sm`.
- Focus: red border + soft red ring (existing pattern).

---

## 4. System tab — Display / Mic / Speaker

### Layout

- Grid: **Display** dominant + **audio column** (Mic over Speaker).
- Adaptive columns (wide → split; ~920px → stack). Do not invent a third design language for this block.
- Mic/Speaker share column height when side-by-side; content height when stacked.

### Display preview

- Nested: **host chassis** (monitor aspect) + **design window** (letterboxed).
- Size chassis from **stage client box** (fill stage; no toy 188×108 pin).
- Hover zoom is optional; veil must not capture pointer (existing rule).

### Heading + status

- Mic/Speaker: `eyebrow + h3 + .sys-io-status` on one row.
- Status is mono meta (`--fs-2xs`), ellipsis; full string in `title`.
- Title and status must both `min-width: 0` + ellipsis so they **never paint over each other**.

---

## 5. Motion & density

- Ease: `--ease` (0.2, 0.8, 0.2, 1).
- Short transitions (~0.12–0.2s); no decorative bounce.
- Prefer telemetry density over empty “marketing” padding; still keep readable hit targets (~34px controls).

---

## 6. i18n

- All user-visible strings via `data-i18n` / `i18n.js` (`en` + `zh`).
- Layout must survive longer Chinese/English labels (ellipsis, flexible grids) — do not assume EN width.

---

## 7. Implementation checklist (before shipping UI)

1. Used **tokens** for type, space, radius, color?
2. Card head matches **global** `.panel-heading` type (not a one-off)?
3. **One** separator per edge (no border-bottom + border-top pair)?
4. Flex/grid children that share a row have `min-width: 0` and ellipsis where needed?
5. Adaptive at ~920 / ~1180 without a third layout language?
6. Cache-bust `?v=` on `style.css` / JS after CSS or script changes?

---

## 8. Anti-patterns

- New accent colors / icon-glyph systems for “polish.”
- Restyling System cards into a different product look than Builder/Run.
- Fixed pixel toy sizes for the display preview.
- Double hairlines, stacked card shells, or status pills that fight mono meta.
- Overriding global title type without updating **this** doc.

---

*Last aligned with System I/O card work. Update this file when the design language actually changes.*
