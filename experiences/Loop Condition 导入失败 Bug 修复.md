# Loop Condition 导入失败 Bug 修复

## 问题描述

### 现象

从 Chatbot 通过 AI 生成 Flowchart JSON 后，导入到 PsyClaw 时，Loop Settings 面板中 Condition 表格的变量值（value）显示为空，但数据实际上已经正确存储。

**用户界面表现**：
- Loop Settings 面板打开后，Condition 表格中的 `ink_color` 和 `word` 列显示为空
- 但 Flowchart JSON 中明确包含了这些值：
  ```json
  {
    "name": "Incongruent_Main",
    "weight": 1,
    "values": {
      "$condition_type$": ["incongruent"]
    }
  }
  ```

## 调试过程

### 1. 数据流分析

```
AI 生成 Flowchart JSON
    ↓
chatbot.html: extractJSON() 提取并验证 JSON
    ↓
postMessage 发送到 psyclaw.html
    ↓
psyclaw.html: message event listener 接收数据
    ↓
loopsToConnections() 转换 loops 为 connections 格式
    ↓
convertConditionsToInternalFormat() 转换 conditions 格式
    ↓
connection.loopConditions (存储为 JSON string)
    ↓
用户点击 Loop → showLoopForm()
    ↓
formLoopConditions.value = conn.loopConditions
    ↓
renderLoopConditions() 渲染 HTML 表格
    ↓
Condition 表格显示空值 ❌
```

### 2. 关键检查点

#### 检查点 1: 原始 Flowchart JSON
```json
{
  "conditions": [
    {
      "name": "Congruent_Main",
      "weight": 1,
      "values": {
        "$condition_type$": ["congruent"]
      }
    },
    {
      "name": "Incongruent_Main",
      "weight": 1,
      "values": {
        "$condition_type$": ["incongruent"]
      }
    }
  ]
}
```
✅ 数据正确

#### 检查点 2: convertConditionsToInternalFormat 输出
```javascript
// 期望输出
'[{"name":"Congruent_Main","weight":1,"values":["congruent"],"_valueKeys":["condition_type"]},...]'

// 实际输出（Bug）
'[{"name":"Congruent_Main","weight":1,"values":[],"_valueKeys":[]},...]'
```
❌ values 变成空数组，_valueKeys 丢失

#### 检查点 3: formLoopConditions.value
```javascript
// 存储的 JSON string
'[{"name":"Congruent_Main","weight":1,"values":[],"_valueKeys":[]},...]'
```
❌ 已经是错误的数据

#### 检查点 4: getLoopConditions() 返回值
```javascript
// 解析后的对象
[{name: "Congruent_Main", weight: 1, values: [], _valueKeys: []}]
```
❌ 从源头就是空的

### 3. 定位 Bug

**问题文件**: `psyclaw.html`  
**问题函数**: `convertConditionsToInternalFormat`  
**问题位置**: 第 5500-5505 行

**问题代码**:
```javascript
} else {
    return {
        name: c.name || `Condition ${i + 1}`,
        weight: c.weight !== undefined ? c.weight : 1,
        values: []  // ❌ 固定返回空数组
    };
}
```

## 根本原因

### 两种数据格式

AI 返回的 condition 有两种可能的格式：

#### 格式 1: 对象格式（AI 原始格式）
```json
{
  "values": {
    "$word$": ["RED"],
    "$ink_color$": ["red"]
  }
}
```

#### 格式 2: 数组格式（内部格式）
```json
{
  "values": ["RED", "red"],
  "_valueKeys": ["word", "ink_color"]
}
```

### Bug 触发条件

当 `convertConditionsToInternalFormat` 遇到**已经是数组格式**的 condition 时，代码进入了 `else` 分支，导致：

1. **`values: []` 固定返回空数组** - 没有使用原始的 `c.values`
2. **缺少 `_valueKeys` 字段** - 没有保留原始的 `c._valueKeys`

### 为什么会遇到数组格式？

虽然 AI 返回的是对象格式，但在以下场景中可能出现数组格式：
1. 用户手动编辑后保存的 condition
2. 从文件导入的 condition
3. 经过多次转换的 condition

## 修复方案

### 修改前（第 5500-5505 行）
```javascript
} else {
    return {
        name: c.name || `Condition ${i + 1}`,
        weight: c.weight !== undefined ? c.weight : 1,
        values: []  // ❌ 固定返回空数组
    };
}
```

### 修改后
```javascript
} else {
    return {
        name: c.name || `Condition ${i + 1}`,
        weight: c.weight !== undefined ? c.weight : 1,
        values: Array.isArray(c.values) ? c.values : [],  // ✓ 使用原始 values
        _valueKeys: c._valueKeys || []                    // ✓ 保留 _valueKeys
    };
}
```

### 修复逻辑

1. **检查 `c.values` 是否为数组**：`Array.isArray(c.values)`
2. **如果是数组**：直接使用 `c.values`
3. **如果不是数组**：返回空数组 `[]`（兼容其他格式）
4. **保留 `_valueKeys`**：`c._valueKeys || []`

## 对比：getLoopConditions 函数

`getLoopConditions` 函数（第 4991-5020 行）已经正确实现了这个逻辑：

```javascript
} else {
    return {
        name: c.name || `Condition ${i + 1}`,
        weight: c.weight !== undefined ? c.weight : 1,
        values: Array.isArray(c.values) ? c.values : [],  // ✓ 正确
        _valueKeys: c._valueKeys || []                    // ✓ 正确
    };
}
```

修复后的 `convertConditionsToInternalFormat` 与 `getLoopConditions` 保持一致。

## _valueKeys 的作用

### 为什么需要 _valueKeys

AI 返回的 `values` 是对象格式：
```json
{
  "values": {
    "$word$": ["RED"],
    "$ink_color$": ["red"]
  }
}
```

对象的 key 顺序在不同环境下可能不同，无法依赖顺序来获取值。

### 转换机制

`convertConditionsToInternalFormat` 将对象格式转换为数组格式：

```javascript
// 原始对象
{
  "values": {
    "$word$": ["RED"],
    "$ink_color$": ["red"]
  }
}

// 转换后
{
  "values": ["RED", "red"],           // 值的数组
  "_valueKeys": ["word", "ink_color"] // 变量名映射
}
```

### 渲染时的查找逻辑

在 `renderLoopConditions()` 中，通过 `_valueKeys.indexOf(varName)` 找到变量的值：

```javascript
variables.forEach((varName, varIndex) => {
    let value = '';
    if (condition._valueKeys && condition._valueKeys.length > 0) {
        const keyIndex = condition._valueKeys.indexOf(varName);
        if (keyIndex !== -1 && condition.values[keyIndex] !== undefined) {
            value = condition.values[keyIndex];
        }
    }
    // 渲染 input
});
```

### 示例

表头列：`["color", "word"]`（按字母排序）

查找 "color" 的值：
- `_valueKeys.indexOf("color")` = 1
- `values[1]` = "red" ✓

查找 "word" 的值：
- `_valueKeys.indexOf("word")` = 0
- `values[0]` = "RED" ✓

## 完整数据流（修复后）

```
AI 返回 JSON (对象格式 values)
    ↓
chatbot.html: extractJSON() + postMessage
    ↓
psyclaw.html: message event listener
    ↓
loopsToConnections() + convertConditionsToInternalFormat()
    ↓
    ├─ 对象格式 → 转换为数组格式 + _valueKeys ✓
    └─ 数组格式 → 直接使用 + 保留 _valueKeys ✓
    ↓
connection.loopConditions (JSON string，_valueKeys 已转换)
    ↓
showLoopForm() → formLoopConditions.value
    ↓
getLoopConditions() → 解析 JSON（保留 _valueKeys）
    ↓
renderLoopConditions() → 渲染 HTML 表格
    ↓
用户看到正确的值 ✓
```

## 相关函数

### 1. convertConditionsToInternalFormat (修复后)

**位置**: `psyclaw.html` 第 5474-5512 行

**职责**: 将 AI 返回的 conditions 转换为内部格式，用于存储到 connection.loopConditions

```javascript
function convertConditionsToInternalFormat(conditions) {
    if (!conditions) return '';

    let parsed;
    try {
        if (typeof conditions === 'string') {
            parsed = JSON.parse(conditions);
        } else if (Array.isArray(conditions)) {
            parsed = conditions;
        } else {
            return '';
        }

        if (!Array.isArray(parsed)) return '';

        const converted = parsed.map((c, i) => {
            if (typeof c.values === 'object' && c.values !== null && !Array.isArray(c.values)) {
                // 对象格式：转换为数组格式
                const origKeys = Object.keys(c.values);
                const valueKeys = origKeys.map(k => k.replace(/^\$/, '').replace(/\$$/, ''));
                const values = origKeys.flatMap(k =>
                    Array.isArray(c.values[k]) ? c.values[k] : [c.values[k]]
                );
                return {
                    name: c.name || `Condition ${i + 1}`,
                    weight: c.weight !== undefined ? c.weight : 1,
                    values: values,
                    _valueKeys: valueKeys
                };
            } else {
                // 数组格式：直接使用（修复后保留 _valueKeys）
                return {
                    name: c.name || `Condition ${i + 1}`,
                    weight: c.weight !== undefined ? c.weight : 1,
                    values: Array.isArray(c.values) ? c.values : [],
                    _valueKeys: c._valueKeys || []
                };
            }
        });
        return JSON.stringify(converted);
    } catch (e) {
        return '';
    }
}
```

### 2. getLoopConditions

**位置**: `psyclaw.html` 第 4991-5020 行

**职责**: 读取并解析 formLoopConditions.value，用于渲染 Loop Conditions 表格

### 3. renderLoopConditions

**位置**: `psyclaw.html` 第 5022-5145 行

**职责**: 根据 getLoopConditions() 返回的数据渲染 HTML 表格

## 注意事项

1. **两种格式兼容**：代码必须同时支持对象格式和数组格式
2. **_valueKeys 的顺序**：表头列按字母排序，但 _valueKeys 按原始顺序，需要通过 `indexOf` 查找
3. **数据一致性**：`convertConditionsToInternalFormat` 和 `getLoopConditions` 必须使用相同的处理逻辑

## 修复验证

### 测试场景 1: AI 生成 Flowchart（对象格式）
```json
{
  "conditions": [
    {
      "name": "Congruent_Main",
      "values": {
        "$condition_type$": ["congruent"]
      }
    }
  ]
}
```
**预期**: Condition 表格显示 "congruent"  
**结果**: ✓ 正确

### 测试场景 2: 手动编辑后保存（数组格式）
```json
[
  {
    "name": "Congruent_Main",
    "values": ["congruent"],
    "_valueKeys": ["condition_type"]
  }
]
```
**预期**: Condition 表格显示 "congruent"  
**结果**: ✓ 正确

### 测试场景 3: 从文件导入
```json
[
  {
    "name": "Trial1",
    "values": ["RED", "red"],
    "_valueKeys": ["ink_color", "word"]
  }
]
```
**预期**: Condition 表格显示 "RED" 和 "red"  
**结果**: ✓ 正确

## 总结

### Bug 本质
- `convertConditionsToInternalFormat` 的 else 分支固定返回空数组，丢失了数组格式的 values 和 _valueKeys

### 修复关键
- else 分支改为使用原始的 `c.values` 和 `c._valueKeys`
- 与 `getLoopConditions` 保持一致的处理逻辑

### 影响范围
- 修复后，所有 condition 导入场景（AI 生成、文件导入、手动编辑）都能正确显示变量值

## 相关文档

- [LoopConditions 表格解析与 valueKeys 机制.md](./LoopConditions 表格解析与 valueKeys 机制.md)
- [flowchart.schema.json 设计思路.md](./flowchart.schema.json 设计思路.md)

## 更新日期

2026-04-16
