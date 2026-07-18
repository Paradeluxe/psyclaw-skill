# Paradigm Recipes

Notes on each built-in paradigm — typical parameters, common variants, and pitfalls.

---

## Stroop (Color-Word Interference)

**Standard**: Stroop (1935). 30-100 trials. Incongruent trials slower than congruent.

**Variants**:
- 2-color (red/blue): simplest
- 3-color (red/blue/green): more sensitive
- 4-color: max sensitivity, more errors
- Emotional Stroop: color words replaced by emotion words

**Typical timing**:
- Fixation: 500ms
- Stimulus: 2000ms (response window)
- ITI: 500-1000ms
- Total per trial: ~3-4s

**Pitfalls**:
- Make sure text is large enough to read clearly (height: 0.1)
- Color-blind participants: use shapes + colors or only B/W stimuli
- Practice: 5-10 trials before main block

## Go/No-Go (Response Inhibition)

**Standard**: Most go (80%), some no-go (20%). Measures false alarms (responding on no-go).

**Variants**:
- Equal go/no-go (50/50): different task demands
- 2-choice go/no-go: two Go stimuli, one NoGo
- Stop-signal: dynamic stop after Go

**Typical timing**:
- Fixation: 500ms
- Stimulus: 1000-1500ms (must respond before)
- ITI: 1500-2500ms (jittered helps)
- Total per trial: ~3s

**Pitfalls**:
- Go stimuli shouldn't be too rare (< 60%): participants develop strategy
- NoGo stimulus must be visually distinct (different color, shape, or category)
- Practice: ensure participants understand "DO NOT press on NoGo"

## Flanker (Eriksen)

**Standard**: Eriksen & Eriksen (1974). 5 arrows, target is middle. 50-100 trials.

**Variants**:
- 3-letter (XX>XX): simpler
- 5-arrow (>>>>): standard
- Spatial vs letter: spatial flanker with arrows
- Spatial arrow task: full arrows, not just symbols

**Typical timing**:
- Fixation: 500ms
- Stimulus: until response (max 2000ms)
- ITI: 500-1000ms
- Total per trial: ~2.5s

**Pitfalls**:
- Display MUST be 5 elements; in psyclaw this is encoded in `flanker_display` column
- Avoid literal `<` characters in instructions (XML escaping issue)
- Center target can be hidden by flanking — make sure spacing is good

## N-back (Working Memory)

**Standard**: Kirchner (1958). Letter/digit presented; press if matches N trials back.

**Variants**:
- 1-back: easy, good for children
- 2-back: standard, sensitive to WM
- 3-back: hard, ceiling effects
- Dual n-back: location + sound
- Spatial: position-based not identity

**Typical timing**:
- Stimulus: 500ms
- ISI: 2500ms (response window)
- Total per trial: 3s
- Block: 60+ trials, with breaks

**Pitfalls**:
- 3-back is very hard; consider practice
- Need ~50+ trials for stable signal
- Use distinct stimuli (letters or digits, not random shapes)

## IAPS (Affective Picture Rating)

**Standard**: Lang, Bradley & Cuthbert (1997). International Affective Picture System.

**Variants**:
- Passive viewing: just look, then rate
- Ratings: valence (1-9), arousal (1-9), dominance (1-9)
- Free viewing with eye-tracking
- Memory task: remember which images seen

**Required assets**: IAPS images (must be obtained from CSEA, not included)

**Typical timing**:
- Fixation: 1000ms
- Image: 6000ms (or until response)
- Rating: 5000ms
- ITI: 1000-2000ms
- Total per trial: ~10-15s

**Pitfalls**:
- IAPS images have copyright; obtain through proper channels
- Need diverse valence × arousal combinations
- Counterbalance order across participants
- Some images are intense; IRB approval required

## Posner Cueing (Spatial Attention)

**Standard**: Posner (1980). Cue predicts (or doesn't) target location.

**Variants**:
- Valid cue (80%), invalid (20%): standard
- Neutral cue (e.g. cross at center)
- Peripheral vs central cues
- Auditory cues

**Typical timing**:
- Fixation: 1000ms
- Cue: 300ms
- ISI: 500ms
- Target: 2000ms (response window)
- ITI: 1000-2000ms
- Total per trial: ~4-5s

**Pitfalls**:
- Cue-target SOA is critical; too short = no effect
- Need enough invalid trials (~20%) to see the validity effect
- Make sure target doesn't appear at fixation (cue would be useless)

---

## Adding new paradigms

To add a new paradigm template:

1. Write `templates/my_paradigm.yaml.tmpl` with `{n_trials}` placeholder
2. Add keywords to `scripts/nl_intake.py` PARADIGM_KEYWORDS dict
3. Test: `python nl_intake.py --input "做 my_paradigm 20 trials" --output /tmp/test.yaml`
4. Verify spec is valid: `python spec_validator.py /tmp/test.yaml`
5. Run pipeline: `python harness_cli.py --spec /tmp/test.yaml --out-dir /tmp/test_out/`

For complex multi-routine paradigms (e.g. with breaks, instructions, multiple loops),
write the YAML directly rather than trying to template everything.
