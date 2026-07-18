# PsychoPy Component Reference

This is the complete parameter set for each component type, verified from
PsychoPy 2026.1.1 source at `psychopy/experiment/components/<name>/__init__.py`.

The psyclaw skill auto-fills sensible defaults; you only need to specify
required fields + the params you care about.

---

## text — Text stimulus

**Required:** `text` (string), `startTime` (auto), `duration` (auto)

**Common params:**
- `text` (str): the text to display
- `height` (float, 0.05): text size in 'units'
- `color` (str, 'white'): 'white'/'red'/etc, or [r,g,b] 0..1
- `font` (str, 'Arial'): font family
- `pos` ([x,y], [0,0]): position in 'units'
- `italic` (bool, false), `bold` (bool, false)
- `units` (str, 'from exp settings')

## image — Image stimulus

**Required:** `path` (relative to project root, e.g. `assets/foo.png`)

**Common params:**
- `path` (str): image file path
- `size` ([w,h] or null): image size in 'units'; null = native pixels
- `pos` ([x,y], [0,0]): position
- `ori` (float, 0): rotation in degrees
- `opacity` (float, 1.0)
- `flipVert` (bool), `flipHoriz` (bool)

## audio — Sound playback

**Required:** `path`

**Common params:**
- `path` (str): sound file (wav/mp3)
- `volume` (float, 1.0)
- `loop` (bool, false)

## video — Movie playback

**Required:** `path`

**Common params:**
- `path` (str)
- `size` ([w,h])
- `pos` ([x,y])
- `ori`, `opacity`
- `loop` (bool)
- `no_audio` (bool, false)
- `backend` ('moviepy' default)

## keyboard — Keyboard response

**Required:** `keys` (comma-separated key names)

**Common params:**
- `keys` (str): 'space, r, b' or 'left, right'
- `duration` (float, -1): response window; -1 = infinite
- `force_end` (bool, false): end routine on first response
- `correct_ans` (str or `$column`): for accuracy tracking
- `store` (str, 'response'): column name in output data
- `registerOn` ('press' default)

## mouse — Mouse response

**Required:** none

**Common params:**
- `duration` (float, -1)
- `force_end` (bool)
- `newClicksOnly` (bool, true)

## code — Custom Python code

**Required:** `code` (str), `phase` ('begin'/'each'/'end' default 'each')

The `code` is inserted into the generated .py script. Use sparingly —
PsychoPy components cover 95% of needs.

---

## Units of measurement

- `height` (default): relative to screen height; 0.5 = center, 1.0 = top
- `pix`: pixels
- `cm`: centimeters (requires monitor calibration)
- `deg`: degrees of visual angle (requires monitor calibration)

## Colors

Named colors work in strings: 'white', 'red', 'blue', 'green', 'black',
'yellow', 'cyan', 'magenta', 'gray'.

RGB tuples can be:
- 0..1 floats: `[1, 0, 0]` = red
- 0..255 ints: `[255, 0, 0]` = red

## Positions

`pos: [x, y]` is in the units above. y is positive UP.

## Tips for using `$column` references

In any text field, prefix with `$` to interpolate from the active loop's spreadsheet:
- `text: $stim_word` → shows the value of column `stim_word` for the current trial
- `correct_ans: $correct_resp` → uses column `correct_resp`
- `text: "Press $key_to_press"` → mixed literal + interpolation
