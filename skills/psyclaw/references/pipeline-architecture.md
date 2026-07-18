# Pipeline architecture — 4-layer model (2026-07-01)

When someone asks "is json2psyexp.js the interface?", or "what's the harness?",
they're trying to locate a layer in the pipeline. The 4 layers below are the
canonical answer. Use this terminology in conversation — don't substitute
"translator" / "renderer" / "compiler" ad hoc, the words don't matter as
much as the boundaries.

```
┌─────────────────────────────────────────────────────────────────┐
│  L1  Interface  (人接触的层)                                       │
│      ├── Claude/Web chat, CLI, Slack/Telegram bot, GUI           │
│      ├── 你现在用的 Telegram DM (The Machine)                    │
│      └── 在 PsyClaw 语境里: nl_intake.py + 你的自然语言描述        │
├─────────────────────────────────────────────────────────────────┤
│  L2  Harness    (orchestration, glue)                            │
│      ├── "把 spec 喂进 emit，捕 warning，调度 stimulus 生成"       │
│      ├── 在 PsyClaw 语境里: harness_cli.py / harness_main.py      │
│      └── 跨阶段的状态机 + IO + 错误处理                          │
├─────────────────────────────────────────────────────────────────┤
│  L3  Emitter    (业务核心 — 单向翻译)                              │
│      ├── "把一个中间表示变成另一个"                                │
│      ├── 在 PsyClaw 语境里: json2psyexp.js                        │
│      └── 同 role 在不同系统里叫:                                  │
│            - compiler (LLVM IR → machine code)                   │
│            - transpiler (Babel TS → JS)                          │
│            - renderer (React VDOM → DOM)                         │
│            - serializer (Pydantic → JSON)                        │
│            - emitter (json2psyexp.js 就是这个)                   │
├─────────────────────────────────────────────────────────────────┤
│  L4  Schema     (数据契约)                                          │
│      ├── flowchart.json v2.0 / 你的 YAML spec / .psyexp XML       │
│      └── 在 PsyClaw 语境里: spec_validator.py + references/...     │
└─────────────────────────────────────────────────────────────────┘
```

## Why these layers matter

| Layer | When it changes | Who owns it | How to test it |
|-------|-----------------|-------------|----------------|
| **L1 Interface** | User adds a new chat platform / CLI flag | AI / UX | smoke test: input → expected output |
| **L2 Harness** | New pipeline stage added (e.g. add L7 analysis report) | Pipeline engineer | `regression_suite.sh` exits 0 |
| **L3 Emitter** | PsychoPy version bumps, new component type added | PsychoPy vendor / us (patches) | `validate_load_from_xml.py` exits 0 |
| **L4 Schema** | YAML format evolution, new paradigm field | Schema designer | `spec_validator.py` exits 0 |

**Why L3 (Emitter) is the layer that gets the most patches:** PsychoPy
releases change component param lists and valTypes, and json2psyexp.js is a
vendored upstream we don't fully control. Every PsychoPy version bump
risks 1-2 `loadFromXML` warnings. See pitfall #17a / #17b / #17e for the
"how to patch a new component type" recipe.

## Common confusion — "is X the harness?"

- `json2psyexp.js` is **the emitter** (L3), NOT the harness. It has zero
  IO, zero scheduling, zero UI.
- `harness_cli.py` / `harness_main.py` are **the harness** (L2). They
  call into the emitter and other stages.
- The Telegram bot you're typing into right now is **the interface** (L1).

If someone says "the harness is broken", they probably mean the harness
failed to detect that json2psyexp.js emitted warnings. The emitter is
rarely the failure point itself — it just emits whatever its inputs say.

## "Where do I add feature Y?"

| Feature type | Add in |
|--------------|--------|
| New chat platform / new NL parsing rule | L1 Interface |
| New pipeline stage, new CLI flag, new output format | L2 Harness |
| New PsychoPy component type, new param, new loop topology | L3 Emitter |
| New YAML field, new spreadsheet column type | L4 Schema |

## "Where was bug X fixed?"

The data-drop diagnostic recipe (SKILL.md pitfall #17) traces the field
through L4 → L3 → L2 → L4 output. The fix is always in L3 (the
processedLoops carrier OR the function body that reads from it). L2 and
L4 are not usually where the bug lives — they're the relay points.