# Flowchart Schema 设计思路

## 概述

本文档描述 `flowchart.schema.json` 的核心设计理念、数据结构和关键设计决策。

---

## 1. 核心设计哲学

### 1.1 统一数组结构 (Unified Array)

**设计**: 使用单一的 `flowchart` 数组包含所有实验元素（routines 和 loops）

```json
{
  "flowchart": [
    { "name": "instruction", "Point": 2, ... },  // Routine
    { "name": "trials", "list": [...], ... },     // Loop
    { "name": "end", "Point": 4, ... }            // Routine
  ]
}
```

**优势**:
- 保持实验的时间顺序
- 简化导入/导出逻辑
- 支持嵌套结构（loop 中包含 loop）

### 1.2 分离关注点 (Separation of Concerns)

| 层级 | 职责 | 示例 |
|------|------|------|
| Schema | 定义数据结构、验证规则 | `flowchart.schema.json` |
| 前端渲染 | 视觉布局、交互逻辑 | `psyclaw.html` |
| 数据转换 | 格式转换、代码生成 | `json2psyexp.js` |

**原则**: Schema 只定义实验逻辑，不定义视觉表现

---

## 2. Point 系统

### 2.1 设计原理

Point 是实验流程中的位置标记，采用**奇偶分离**设计：

```
Point 1    Point 2      Point 3      Point 4      Point 5
  |          |            |            |            |
  └──────────┴────────────┴────────────┴────────────┘
Loop边界   Routine 1    Loop边界    Routine 2    Loop边界
```

- **偶数点 (2, 4, 6...)**: Routine 的位置
- **奇数点 (1, 3, 5...)**: Loop 的连接点（边界）

### 2.2 Loop 边界计算

**核心规则**（v2.0 新设计）：

```
startPoint = first routine's Point - 1
endPoint = last routine's Point + 1
```

**示例**:
```
Routine Points: [2, 4, 6]  →  Loop: startPoint=1, endPoint=7
Routine Points: [4, 6]     →  Loop: startPoint=3, endPoint=7
```

**设计演进**:
- v1.0: Loop 显式存储 `startPoint` 和 `endPoint`
- v2.0: Loop 只存储 `list`，边界在渲染时动态计算

---

## 3. Routine 设计

### 3.1 最小完整单元

```json
{
  "name": "stroop_trial",
  "Point": 2,
  "components": [
    {
      "name": "fixation",
      "type": "text",
      "text": "+",
      "startTime": 0,
      "duration": 500
    },
    {
      "name": "response",
      "type": "keyboard",
      "keys": "f,j",
      "startTime": 500,
      "duration": 2000
    }
  ]
}
```

**必需字段**:
- `name`: 唯一标识符
- `Point`: 在流程中的位置（偶数）
- `components`: 刺激/响应组件数组（至少一个）

### 3.2 Component 类型系统

支持 5 种组件类型：

| 类型 | 用途 | 关键字段 |
|------|------|----------|
| `text` | 文本刺激 | `text`, `color`, `font` |
| `image` | 图片刺激 | `path`, `size`, `contrast` |
| `audio` | 音频刺激 | `path`, `volume`, `loop` |
| `video` | 视频刺激 | `path`, `volume`, `flip` |
| `keyboard` | 键盘响应 | `keys`, `forceEndRoutine` |

---

## 4. Loop 设计

### 4.1 嵌套结构

Loop 通过 `list` 字段实现嵌套：

```json
{
  "name": "blocks",
  "nRounds": 2,
  "type": "sequential",
  "list": [
    {
      "name": "trials",
      "nRounds": 10,
      "type": "random",
      "list": [
        { "name": "fixation", "Point": 2, ... },
        { "name": "stimulus", "Point": 4, ... }
      ]
    },
    { "name": "break", "Point": 6, ... }
  ]
}
```

**特点**:
- `list` 可以包含 Routine 和 Loop
- 支持任意深度的嵌套
- 每个 Loop 独立配置 `nRounds` 和 `type`

### 4.2 Condition 系统

用于定义 trial 级别的变量：

```json
{
  "conditions": [
    {
      "name": "congruent",
      "weight": 1,
      "values": { "$color$": ["red", "blue"] }
    }
  ]
}
```

**设计要点**:
- `weight`: 条件在随机化中的权重
- `values`: 单变量字典（key 是变量名，value 是可能值数组）
- 变量名格式: `$variableName$`

---

## 5. 验证规则

### 5.1 Loop 有效性规则

```
VALID:
  - Loop A (routines 2-8) 包含 Loop B (routines 4-6)     [嵌套]
  - Loop A (routines 2-4) 和 Loop B (routines 6-8)         [顺序]

INVALID:
  - Loop A (routines 2-6) 和 Loop B (routines 4-8)         [交叉]
  - Loop A (routines 2-4) 和 Loop B (routines 4-6)         [共享边界]
```

### 5.2 Schema 验证

```json
{
  "required": ["name", "Point", "components"],  // Routine
  "required": ["name", "nRounds", "type", "list"]  // Loop (v2.0)
}
```

---

## 6. 版本演进

### v1.0 → v2.0 关键变更

| 方面 | v1.0 | v2.0 |
|------|------|------|
| Loop 边界 | 显式存储 `startPoint`/`endPoint` | 从 `list` 动态计算 |
| Loop 识别 | 检查 `startPoint` 字段 | 检查 `list` 字段 |
| 数据结构 | 扁平结构 | 嵌套结构 |
| 兼容性 | - | 向后兼容 v1.0 |

**迁移策略**:
- 导入时优先使用 `list` 计算边界
- 如果 `list` 不存在，回退到 `startPoint`/`endPoint`

---

## 7. 渲染时计算逻辑

### 7.1 从 list 计算边界

```javascript
// 伪代码
function calculateLoopBounds(loop) {
  const routinePoints = loop.list
    .filter(item => item.Point !== undefined)
    .map(item => item.Point)
    .sort((a, b) => a - b);
  
  const firstPoint = routinePoints[0];
  const lastPoint = routinePoints[routinePoints.length - 1];
  
  return {
    startPoint: firstPoint - 1,  // 奇数
    endPoint: lastPoint + 1      // 奇数
  };
}
```

### 7.2 从 Point 计算 Routine 索引

```javascript
// Routine Index (0-based) → Point (偶数)
point = (index + 1) * 2

// Point (偶数) → Routine Index
index = point / 2 - 1
```

---

## 8. 设计决策记录

### 8.1 为什么移除显式的 startPoint/endPoint？

**问题**:
- 数据冗余：`list` 已经包含 routines 的信息
- 容易不一致：手动设置可能出错
- 维护困难：移动 routine 需要更新 loop

**解决方案**:
- 只保留 `list`，边界自动计算
- 单一数据源（Single Source of Truth）

### 8.2 为什么使用 Point 而不是 Index？

**优势**:
- 直观表示流程位置
- 支持奇偶分离（routines vs loops）
- 便于可视化渲染

### 8.3 为什么 Condition 使用 weight 而不是 nReps？

**设计**:
- `nRounds`: Loop 级别的重复次数
- `weight`: Condition 级别的权重

**示例**:
```
nRounds: 2
conditions: [
  { name: "A", weight: 2 },  // 出现 2 * 2 = 4 次
  { name: "B", weight: 1 }   // 出现 2 * 1 = 2 次
]
```

---

## 9. 相关文件

| 文件 | 职责 |
|------|------|
| `flowchart.schema.json` | 数据结构和验证规则 |
| `psyclaw.html` | 前端渲染和交互 |
| `json2psyexp.js` | 转换为 PsychoPy XML |
| `chatbot.html` | AI 生成 flowchart |

---

## 10. 更新历史

- **2026-04-15**: v2.0 发布
  - 移除 Loop 的显式 `startPoint`/`endPoint`
  - 添加 `list` 作为必需字段
  - 边界在渲染时从 `list` 计算

- **2026-04-12**: v1.0 稳定版
  - 基础 Routine 和 Loop 支持
  - 5 种 Component 类型
  - Condition 系统
