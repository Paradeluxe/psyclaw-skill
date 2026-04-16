# Loop Conditions 表格解析与 _valueKeys 机制

## 概述

本文档描述了 PsyClaw 项目中 Loop Settings 面板的 Condition 表格数据解析流程，以及 `_valueKeys` 字段的作用和修复的相关 Bug。

## 问题描述

### 现象

从 Chatbot 通过 AI 生成 Flowchart JSON 后，导入到 PsyClaw 时，Condition 表格中的变量值（value）显示为空，但 `_valueKeys` 和 `values` 数据实际上已经正确存储。

### 调试过程

1. **检查原始数据**：`formLoopConditions.value` 中数据正确
   ```json
   [{"name":"Congruent Red","weight":1,"values":["RED","red"],"_valueKeys":["word","color"]},...]
   ```

2. **检查表头列变量**：按字母排序
   ```
   ["color", "word"]
   ```

3. **检查 getLoopConditions() 返回值**：`_valueKeys` 变成了 `undefined`

## 根本原因

### 数据格式转换链

1. **AI 返回的原始格式**（对象格式）：
   ```json
   {
     "values": {
       "$word$": ["RED"],
       "$ink_color$": ["red"]
     }
   }
   ```

2. **convertConditionsToInternalFormat 转换后**（数组格式）：
   ```json
   {
     "values": ["RED", "red"],
     "_valueKeys": ["word", "ink_color"]
   }
   ```

3. **存储在 connection.loopConditions**：
   ```json
   [{"name":"Congruent Red","values":["RED","red"],"_valueKeys":["word","color"]},...]
   ```

### Bug 位置

**文件**: `psyclaw.html`  
**函数**: `getLoopConditions()`  
**位置**: 第 5008-5014 行

**问题代码**:
```javascript
} else {
    return {
        name: c.name || `Condition ${i + 1}`,
        weight: c.weight !== undefined ? c.weight : 1,
        values: []  // ❌ 固定返回空数组，丢失原始 values
                 // ❌ 缺少 _valueKeys 字段
    };
}
```

### 问题分析

当 condition 的 `values` 已经是数组格式时（而非对象格式），代码进入了 `else` 分支。这个分支存在两个问题：

1. **`values: []` 固定返回空数组** - 没有使用原始的 `c.values`
2. **缺少 `_valueKeys` 字段** - 没有保留原始的 `c._valueKeys`

这导致后续渲染时无法获取正确的值。

## 修复方案

**修改后的代码**:
```javascript
} else {
    return {
        name: c.name || `Condition ${i + 1}`,
        weight: c.weight !== undefined ? c.weight : 1,
        values: Array.isArray(c.values) ? c.values : [],  // 使用原始 values
        _valueKeys: c._valueKeys || []                    // 保留 _valueKeys
    };
}
```

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

将对象格式转换为数组格式，同时保留映射关系：

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
    if (condition._valueKeys && condition._valueKeys.length > 0) {
        const keyIndex = condition._valueKeys.indexOf(varName);
        if (keyIndex !== -1 && condition.values[keyIndex] !== undefined) {
            value = condition.values[keyIndex];
        }
    }
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

## 完整数据流

```
AI 返回 JSON
    ↓
chatbot.html: extractJSON() + postMessage
    ↓
psyclaw.html: message event listener
    ↓
loopsToConnections() + convertConditionsToInternalFormat()
    ↓
connection.loopConditions (JSON string，_valueKeys 已转换)
    ↓
showLoopForm() → formLoopConditions.value
    ↓
getLoopConditions() → 解析 JSON（修复后的代码保留 _valueKeys）
    ↓
renderLoopConditions() → 渲染 HTML 表格
    ↓
用户编辑 → saveLoopConditions() → 保存回 formLoopConditions
    ↓
saveLoopFormChanges() → 更新 connection.loopConditions
```

## 相关函数

### 1. getLoopConditions() - 读取并解析

```javascript
function getLoopConditions() {
    const jsonValue = formLoopConditions.value.trim();
    if (!jsonValue) return [];
    try {
        const parsed = JSON.parse(jsonValue);
        if (Array.isArray(parsed)) {
            return parsed.filter(c => c._meta !== true).map((c, i) => {
                if (typeof c.values === 'object' && c.values !== null && !Array.isArray(c.values)) {
                    // 对象格式：需要转换
                    const origKeys = Object.keys(c.values);
                    const valueKeys = origKeys.map(k => k.replace(/^\$/, '').replace(/\$$/, ''));
                    const values = origKeys.flatMap(k =>
                        Array.isArray(c.values[k]) ? c.values[k] : [c.values[k]]
                    );
                    return { name: c.name, weight: c.weight, values, _valueKeys: valueKeys };
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
        }
    } catch (e) {}
    return [];
}
```

### 2. renderLoopConditions() - 渲染表格

```javascript
function renderLoopConditions() {
    const conditions = getLoopConditions();
    const variables = detectVariablesFromRoutines(routineIndices);

    // 更新表头
    headerRow.innerHTML = `
        <th>Condition Name</th>
        ${variables.map(v => `<th class="cond-col-var">${v}</th>`).join('')}
        <th>Weight</th>
        <th></th>
    `;

    // 渲染每一行
    conditions.forEach((condition, index) => {
        let rowHtml = `<td><input class="loop-cond-name-input" value="${condition.name}"></td>`;

        variables.forEach((varName, varIndex) => {
            let value = '';
            if (condition.values && condition.values.length > 0) {
                if (condition._valueKeys && condition._valueKeys.length > 0) {
                    const keyIndex = condition._valueKeys.indexOf(varName);
                    if (keyIndex !== -1 && condition.values[keyIndex] !== undefined) {
                        value = condition.values[keyIndex];
                    }
                }
            }
            rowHtml += `<td><input class="loop-cond-var-input" data-var="${varName}" value="${value}"></td>`;
        });

        rowHtml += `<td><input class="loop-cond-weight-input" value="${condition.weight}"></td>`;
        rowHtml += `<td><button class="loop-cond-remove-btn">×</button></td>`;
        // 插入到表格
    });
}
```

### 3. saveLoopConditions() - 保存修改

```javascript
function saveLoopConditions() {
    const conditions = [];
    const rows = loopConditionsBody.querySelectorAll('tr');

    rows.forEach(row => {
        const nameInput = row.querySelector('.loop-cond-name-input');
        const weightInput = row.querySelector('.loop-cond-weight-input');

        if (nameInput && nameInput.value.trim()) {
            const condition = {
                name: nameInput.value.trim(),
                weight: parseInt(weightInput?.value) || 1,
                values: []
            };

            const varInputs = row.querySelectorAll('.loop-cond-var-input');
            varInputs.forEach(input => {
                const varIndex = parseInt(input.dataset.varindex);
                condition.values[varIndex] = input.value || '';
            });

            conditions.push(condition);
        }
    });

    formLoopConditions.value = conditions.length > 0 ? JSON.stringify(conditions) : '';
}
```

## 注意事项

1. **_valueKeys 的顺序问题**：表头列按字母排序变量名，但 `_valueKeys` 是按原始顺序，两者顺序可能不同，需要通过 `indexOf` 查找

2. **两种数据格式兼容**：
   - 对象格式：`{values: {"$word$": ["RED"]}}`
   - 数组格式：`{values: ["RED"], _valueKeys: ["word"]}`

3. **getLoopConditions 同时处理两种格式**：根据 `values` 的类型判断使用哪种处理逻辑

## 更新历史

- **2026-04-15**: 修复 getLoopConditions 中 else 分支丢失 _valueKeys 的问题
  - 问题：values 已是数组格式时，else 分支固定返回空数组且缺少 _valueKeys
  - 修复：else 分支改为 `values: Array.isArray(c.values) ? c.values : []` 并添加 `_valueKeys: c._valueKeys || []`
  - 影响：修复后 Condition 表格能正确显示变量值
