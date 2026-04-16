# Loop 内容检测逻辑

## 概述

本文档描述了 PsyClaw 项目中 Loop Settings 面板中 "Contains" 和 "Contained In" 两个部分的检测逻辑。这些逻辑用于显示当前 Loop 包含的内容以及它被哪些父级 Loop 包含。

## 核心概念

### 1. Label 系统

每个 Routine 和连接点都有对应的 Label：
- Routine `i` 的左边界 Label = `i * 2 + 1`
- Routine `i` 的右边界 Label = `i * 2 + 3`
- 连接点的 Label 对应于 Routine 的边界

### 2. 包含关系判断

Loop A 包含 Loop B 的条件：
- Loop A 的最小 Label ≤ Loop B 的最小 Label
- Loop A 的最大 Label ≥ Loop B 的最大 Label

### 3. Depth 层级

- **Depth 越大** = 越外层（包含更多内容）
- **Depth 越小** = 越内层（被更多内容包含）
- 直接子级的 Depth = 父级 Depth - 1

## 检测逻辑

### 1. 获取 Loop 直接包含的内容 (getLoopContents)

**文件位置**: `psyclaw.html`

**函数签名**:
```javascript
function getLoopContents(conn, allConnections)
```

**返回值**:
```javascript
{
    routines: [{ name, type: 'routine', index }],
    loops: [{ name, type: 'loop', index }]
}
```

**实现逻辑**:

1. **获取当前 Loop 的边界**:
```javascript
const startLabel = parseInt(conn.start.label);
const endLabel = parseInt(conn.end.label);
const minLabel = Math.min(startLabel, endLabel);
const maxLabel = Math.max(startLabel, endLabel);
const connDepth = conn.depth || 0;
```

2. **首先获取直接嵌套的子 Loops**:
```javascript
const childLoops = [];
for (let i = 0; i < allConnections.length; i++) {
    const otherConn = allConnections[i];
    if (otherConn === conn) continue;
    
    const otherStartLabel = parseInt(otherConn.start.label);
    const otherEndLabel = parseInt(otherConn.end.label);
    const otherMinLabel = Math.min(otherStartLabel, otherEndLabel);
    const otherMaxLabel = Math.max(otherStartLabel, otherEndLabel);
    const otherDepth = otherConn.depth || 0;
    
    // 检查是否是直接子级（在范围内且 depth = connDepth - 1）
    if (otherMinLabel >= minLabel && otherMaxLabel <= maxLabel && otherDepth === connDepth - 1) {
        loops.push({ name: otherConn.loopName || `Loop ${i + 1}`, type: 'loop', index: i });
        childLoops.push({ minLabel: otherMinLabel, maxLabel: otherMaxLabel });
    }
}
```

3. **然后获取直接包含的 Routines（排除被子 Loop 包含的）**:
```javascript
for (let i = 0; i < routineRects.length; i++) {
    const rect = routineRects[i];
    if (!rect) continue;
    const routineLeftLabel = i * 2 + 1;
    const routineRightLabel = i * 2 + 3;
    
    // 检查 Routine 是否在当前 Loop 范围内
    if (routineLeftLabel >= minLabel && routineRightLabel <= maxLabel) {
        // 检查 Routine 是否被任何子 Loop 包含
        let isInChildLoop = false;
        for (const childLoop of childLoops) {
            if (routineLeftLabel >= childLoop.minLabel && routineRightLabel <= childLoop.maxLabel) {
                isInChildLoop = true;
                break;
            }
        }
        
        // 只添加不被子 Loop 包含的 Routines
        if (!isInChildLoop) {
            routines.push({ name: rect.name || `Routine ${i + 1}`, type: 'routine', index: i });
        }
    }
}
```

**关键逻辑**:
- 先获取子 Loops，记录它们的边界
- 再检测 Routines，排除被任何子 Loop 包含的 Routine
- 这样确保只显示直接包含在当前 Loop 内的内容

### 2. 获取包含当前 Loop 的父级 Loops (getParentLoops)

**文件位置**: `psyclaw.html`

**函数签名**:
```javascript
function getParentLoops(conn, allConnections)
```

**返回值**:
```javascript
[{ name, type: 'loop', index }]
```

**实现逻辑**:

1. **获取当前 Loop 的边界**:
```javascript
const connStartLabel = parseInt(conn.start.label);
const connEndLabel = parseInt(conn.end.label);
const connMinLabel = Math.min(connStartLabel, connEndLabel);
const connMaxLabel = Math.max(connStartLabel, connEndLabel);
const connDepth = conn.depth || 0;
```

2. **查找父级 Loops**:
```javascript
for (let i = 0; i < allConnections.length; i++) {
    const otherConn = allConnections[i];
    if (otherConn === conn) continue;
    
    const otherStartLabel = parseInt(otherConn.start.label);
    const otherEndLabel = parseInt(otherConn.end.label);
    const otherMinLabel = Math.min(otherStartLabel, otherEndLabel);
    const otherMaxLabel = Math.max(otherStartLabel, otherEndLabel);
    const otherDepth = otherConn.depth || 0;
    
    // 父级 Loop 必须完全包含当前 Loop，且 depth 更大（更外层）
    if (otherMinLabel <= connMinLabel && otherMaxLabel >= connMaxLabel && otherDepth === connDepth + 1) {
        parents.push({ name: otherConn.loopName || `Loop ${i + 1}`, type: 'loop', index: i });
    }
}
```

**关键逻辑**:
- 父级 Loop 的边界必须完全包含当前 Loop
- 父级 Loop 的 depth = 当前 Loop 的 depth + 1（更外层）
- 只返回直接父级（不是祖父级等）

## 可视化示例

```
┌────────────────────────────────────────────────────────────┐
│  trials_3 (Depth 3)                                        │
│  ┌──────────────────────────────────────────────────────┐  │
│  │  trials_2 (Depth 2)                                   │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │  trials_1 (Depth 1)                             │  │  │
│  │  │  ┌──────────────────────────────────────────┐  │  │  │
│  │  │  │  routine_1                                │  │  │  │
│  │  │  └──────────────────────────────────────────┘  │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
└────────────────────────────────────────────────────────────┘

Loop: trials_3
├── Contains: trials_2
└── Contained In: (none)

Loop: trials_2
├── Contains: trials_1
└── Contained In: trials_3

Loop: trials_1
├── Contains: routine_1
└── Contained In: trials_2
```

## UI 显示逻辑

### 1. Contains 部分

**函数**: `updateLoopContentsDisplay(conn)`

- 调用 `getLoopContents(conn, connections)` 获取内容
- 渲染 Routine 标签（蓝色）和 Loop 标签（粉色）
- 点击 Routine 标签 → 打开 Routine Form
- 点击 Loop 标签 → 打开对应 Loop 的 Form

### 2. Contained In 部分

**函数**: `updateLoopContainedInDisplay(conn)`

- 调用 `getParentLoops(conn, connections)` 获取父级
- 渲染父级 Loop 标签（粉色）
- 点击标签 → 打开父级 Loop 的 Form

## 注意事项

1. **直接内容**: Contains 只显示直接包含的内容，不显示嵌套多层的内容
   - trials_2 的 Contains 只显示 trials_1，不显示 routine_1

2. **直接父级**: Contained In 只显示直接父级，不显示祖父级
   - trials_1 的 Contained In 只显示 trials_2，不显示 trials_3

3. **边界判断**: 使用 Label 范围判断包含关系，而不是视觉位置

4. **Depth 方向**: Depth 越大表示越外层，与直觉相反
   - 最内层 Loop: Depth 0
   - 最外层 Loop: 最大 Depth

## 变量检测逻辑

### 检测 Loop 包含的 Routines 中的变量

**函数**: `detectVariablesFromRoutines(routineIndices = null)`

**文件位置**: `psyclaw.html`

**函数签名**:
```javascript
function detectVariablesFromRoutines(routineIndices = null)
```

**参数**:
- `routineIndices`: 可选，指定要检测的 routine 索引数组。如果为 null，则检测所有 routines。

**返回值**:
```javascript
['varName1', 'varName2', ...]  // 排序后的变量名数组
```

**实现逻辑**:

1. **确定要检测的 routines**:
```javascript
const routinesToCheck = routineIndices !== null 
    ? routineIndices.map(i => routineRects[i]).filter(r => r)
    : routineRects;
```

2. **遍历每个 routine 的 avtpComponents**:
```javascript
routinesToCheck.forEach(rect => {
    if (!rect || !rect.avtpComponents) return;
    
    rect.avtpComponents.forEach(component => {
        if (!component || typeof component !== 'object') return;
        
        Object.values(component).forEach(value => {
            if (typeof value === 'string') {
                // 匹配 $variableName$ 格式（变量被$包裹）
                const matches = value.match(/\$([a-zA-Z_][a-zA-Z0-9_]*)\$/g);
                if (matches) {
                    matches.forEach(match => {
                        // 提取变量名（去掉首尾$）
                        const varName = match.replace(/^\$/, '').replace(/\$$/, '');
                        if (varName) variables.add(varName);
                    });
                }
            }
        });
    });
});
```

### 在 renderLoopConditions 中使用

**关键逻辑**:
```javascript
function renderLoopConditions() {
    // 获取当前 loop 包含的 routines，只检测这些 routines 中的变量
    let variables = [];
    if (activeConnection) {
        const contents = getLoopContents(activeConnection, connections);
        const routineIndices = contents.routines.map(r => r.index);
        variables = detectVariablesFromRoutines(routineIndices);
    }
    
    // 根据是否检测到变量来启用/禁用 Add Condition 按钮
    if (addLoopConditionBtn) {
        if (variables.length === 0) {
            addLoopConditionBtn.disabled = true;
            addLoopConditionBtn.style.opacity = '0.5';
            addLoopConditionBtn.style.cursor = 'not-allowed';
        } else {
            addLoopConditionBtn.disabled = false;
            addLoopConditionBtn.style.opacity = '1';
            addLoopConditionBtn.style.cursor = 'pointer';
        }
    }
    
    // ... 渲染表格
}
```

**关键逻辑**:
- 只检测当前 Loop **直接包含**的 routines 中的变量
- 不检测被嵌套子 Loop 包含的 routines 中的变量
- 如果没有检测到变量，禁用 "Add Condition" 按钮

## UI 样式相关

### Loop Settings 表单布局

**文件位置**: `psyclaw.html`

**nRounds 和 Loop Type 并排显示**:

使用 `avtp-form-row` 类实现两列布局：
```css
.avtp-form-row {
    display: flex;
    flex-direction: row;
    gap: 16px;
    margin-bottom: 16px;
}

.avtp-form-row > div {
    flex: 1;
    min-width: 0;
}
```

**HTML 结构**:
```html
<div class="avtp-form-row">
    <div>
        <label class="avtp-form-label">nRounds</label>
        <input type="text" class="avtp-form-input" id="formLoopReps" step="1" min="1" placeholder="1">
    </div>
    <div>
        <label class="avtp-form-label">Loop Type</label>
        <select class="avtp-form-select" id="formLoopType">
            <option value="random">random</option>
            <option value="sequential">sequential</option>
            <option value="fullRandom">fullRandom</option>
        </select>
    </div>
</div>
```

**更新历史**:
- **2026-04-12**: 将 `avtp-form-row` 从 grid 改为 flexbox 布局
  - 原因：确保 nRounds 和 Loop Type 在同一行显示
  - 使用 `flex: 1` 让两个子元素平均分配宽度

### 3. 获取包含 Routine 的 Loops (getLoopsContainingRoutine)

**文件位置**: `psyclaw.html`

**函数签名**:
```javascript
function getLoopsContainingRoutine(routineIndex)
```

**返回值**:
```javascript
[{ name, type: 'loop', index, depth }]
```

**实现逻辑**:

1. **计算 Routine 的边界 Label**:
```javascript
const routineLeftLabel = routineIndex * 2 + 1;
const routineRightLabel = routineIndex * 2 + 3;
```

2. **查找所有包含该 Routine 的 Loops**:
```javascript
for (let i = 0; i < connections.length; i++) {
    const conn = connections[i];
    const connStartLabel = parseInt(conn.start.label);
    const connEndLabel = parseInt(conn.end.label);
    const connMinLabel = Math.min(connStartLabel, connEndLabel);
    const connMaxLabel = Math.max(connStartLabel, connEndLabel);
    const connDepth = conn.depth || 0;
    
    // 检查 routine 是否在这个 loop 的范围内
    if (routineLeftLabel >= connMinLabel && routineRightLabel <= connMaxLabel) {
        containingLoops.push({ 
            name: conn.loopName || `Loop ${i + 1}`, 
            type: 'loop', 
            index: i, 
            depth: connDepth 
        });
    }
}
```

3. **只返回直接包含的 Loop（最内层）**:
```javascript
// 找到最小的 depth（最内层）
const minDepth = Math.min(...containingLoops.map(l => l.depth));
// 只返回 depth 等于最小 depth 的 loops（直接包含的 loop）
return containingLoops.filter(l => l.depth === minDepth);
```

**关键逻辑**:
- 只返回**直接包含**该 Routine 的 Loop（depth 最小的，即最内层的）
- 不返回外层嵌套的 Loops

## Loop 标签点击处理

### 问题与修复

**问题**: 点击 Loop 标签时，使用 `loopName` 查找 Connection 可能导致错误
```javascript
// 错误的方式
const connection = connections.find(c => c.loopName === loopName);
// 如果有多个 Loop 同名，会返回第一个匹配的，可能不是想要的那个
```

**修复**: 使用 `data-loop-index` 直接访问 Connection
```javascript
// 正确的方式
const loopIndex = parseInt(tag.dataset.loopIndex);
const connection = connections[loopIndex];
```

**涉及位置**:
1. `updateLoopContentsDisplay` - Contains 部分的 Loop 标签点击
2. `updateLoopContainedInDisplay` - Loop 的 Contained In 部分标签点击
3. `updateRoutineContainedInDisplay` - Routine 的 Contained In 部分标签点击

## 更新历史

- **2026-04-12**: 修复 Routine Contained In 只显示直接包含的 Loop
  - 问题：Routine 的 Contained In 显示所有包含它的 Loops（包括外层嵌套的）
  - 规则：只显示**直接包含**该 Routine 的 Loop（最内层的一个）
  - 修复：`getLoopsContainingRoutine` 函数只返回 depth 最小的 Loop

- **2026-04-12**: 修复 Loop 标签点击可能打开错误 Loop 的问题
  - 问题：点击 Loop 标签时使用 `loopName` 查找，如果有同名 Loop 会打开错误的那个
  - 修复：改用 `data-loop-index` 直接通过索引访问 Connection
  - 涉及：`updateLoopContentsDisplay`、`updateLoopContainedInDisplay`、`updateRoutineContainedInDisplay`

- **2026-04-12**: 修复变量检测范围问题
  - 问题：`trials_1` 检测到了 `routine_1` 中的 `$test` 变量，但 `routine_1` 并不在 `trials_1` 中
  - 原因：`detectVariablesFromRoutines` 检测了所有 routines，而不是只检测当前 loop 包含的
  - 修复：添加 `routineIndices` 参数，只检测 `getLoopContents` 返回的 routines

- **2026-04-12**: 添加 Add Condition 按钮禁用逻辑
  - 当没有检测到 `$` 变量时，禁用 "Add Condition" 按钮
  - 提示用户先在 routines 中添加以 `$` 开头的变量

- **2026-04-12**: 修复第二层以上 Loop 检测 Routine 的问题
  - 问题：第二层 Loop 会检测到第零层的 Routine
  - 原因：检测 Routines 时没有排除被子 Loop 包含的
  - 修复：先获取子 Loops，再排除被它们包含的 Routines

- **2026-04-12**: 添加 Contained In 部分
  - 新增 `getParentLoops` 函数
  - 新增 `updateLoopContainedInDisplay` 函数
  - 显示当前 Loop 被哪些父级 Loop 包含

- **2026-04-12**: 初始版本
  - 实现 `getLoopContents` 函数
  - 实现 `updateLoopContentsDisplay` 函数
  - 显示 Loop 包含的 Routines 和子 Loops
