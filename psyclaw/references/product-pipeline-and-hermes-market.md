# Pipeline + Hermes market + explain style (2026-07-18)

## User communication

When user is non-expert or says 没理解 / 幼儿园: **short sentences, almost no jargon tables overload**.  
Product talk = 菜谱(skill) vs 厨房(webui); 装全部 = 总开关.

## Pipeline (skill)

```
/psyclaw
  S0 clarify if vague (one question)
  S1 intake: NL | PDF/HTML text | existing <folder>.psyclaw
  S2 IR: <folderName>.psyclaw
  S3 validate
  S4 package folder
  S5 optional → webui G1/G2
```

**browser-skill:** related companion for fetching type-(2) materials. Load when needed; **not** merged into skill core; **not** every `/psyclaw` opens browser.

**Inputs (user-confirmed three):**

1. Spoken/typed experiment description  
2. PDF / HTML / pasted method materials  
3. Existing project to modify  

## Hermes market adapt checklist

1. Standard skill tree + valid frontmatter (`name`, `description`, version, license, tags, related_skills)  
2. Prefer repo layout `skills/psyclaw/` for taps  
3. Publish GitHub public (or private + token)  
4. Pass skills_guard (no secrets, no destructive defaults)  
5. README one-liner install: tap and/or full identifier and/or short name when unique  
6. Self-test: install on clean profile → `/psyclaw`  
7. Optional later: skills.sh / clawhub / official optional PR  

Official optional = Hermes core PR. Tap = easiest for lab share.

## Related skills (expected)

- `browser-skill` — fetch pages/PDFs  
- `psyclaw-webui` — SPA / run / marker rules  
- `add-paradigm` — Path B replication  

## Do not

- Equate `hermes skills install` with lab software install  
- Put paper PDF corpora in the skill release surface  
- Rename slash to `/psyclaw-skill` unless user explicitly changes `name:`  
