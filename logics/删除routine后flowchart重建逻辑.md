# 删除 Routine 后 Flowchart 重建逻辑

## 概述

本文档描述了 PsyClaw 项目中删除 Routine 后 Flowchart 的重建逻辑。当用户删除一个 Routine 时，系统需要：
1. 删除与该 Routine 相关的 Loop
2. 更新剩余 Loop 的 label
3. 重新分配连接点
4. 保持 Flowchart 的一致性

## 核心概念

### 1. 连接点 Label 系统

每个 Routine 有两个连接点（奇数 label）：
- Routine i 的左侧连接点 label = `i * 2 + 1`
- Routine i 的右侧连接点 label = `i * 2 + 3`

**示例（3 个 routines）：**
| Routine | 左侧 Label | 右侧 Label |
|---------|-----------|-----------|
| routine_0 (i=0) | 1 | 3 |
| routine_1 (i=1) | 3 | 5 |
| routine_2 (i=2) | 5 | 7 |

**注意：** 相邻 Routine 共享连接点（如 label 3 是 routine_0 的右侧，也是 routine_1 的左侧）

### 2. Loop 与 Routine 的关系

Loop 使用连接点 label 来定义其范围：
- Loop 的起点 label 和终点 label 定义了它跨越的 Routine 范围
- Loop 包含所有在其范围内的 Routine

**示例：**
- Loop `1→3`：只包含 routine_0（自循环）
- Loop `1→5`：包含 routine_0 和 routine_1
- Loop `3→7`：包含 routine_1 和 routine_2

## 删除 Routine 的流程

### 步骤 1：标记要删除的 Routine

```javascript
const routineMarks = routineRects.map((_, index) =>
    index === removedRoutineIndex ? 'delete' : 'keep'
);
```

### 步骤 2：标记要删除的 Loop

Loop 删除规则：**如果 Loop 范围内没有保留的 Routine，则删除该 Loop**

```javascript
const loopMarks = connections.map(conn => {
    const startLabel = parseInt(conn.start.label);
    const endLabel = parseInt(conn.end.label);
    const minLabel = Math.min(startLabel, endLabel);
    const maxLabel = Math.max(startLabel, endLabel);

    // 检查这个 loop 包含的所有 routine
    let hasKeepRoutine = false;
    for (let i = 0; i < routineRects.length; i++) {
        // routine i 占据的连接点范围：[i * 2 + 1, i * 2 + 3]
        const routineLeftLabel = i * 2 + 1;
        const routineRightLabel = i * 2 + 3;
        // 如果 routine 在 loop 范围内
        if (routineLeftLabel >= minLabel && routineRightLabel <= maxLabel) {
            // 如果这个 routine 不是被删除的
            if (i !== removedRoutineIndex) {
                hasKeepRoutine = true;
                break;
            }
        }
    }

    // 如果 loop 范围内没有保留的 routine，标记为删除
    return hasKeepRoutine ? 'keep' : 'delete';
});
```

### 步骤 3：重建 Flowchart

#### 3.1 删除标记的 Loop 和 Routine

```javascript
// 从后向前删除，避免索引变化影响
for (let i = loopMarks.length - 1; i >= 0; i--) {
    if (loopMarks[i] === 'delete') {
        connections.splice(i, 1);
    }
}

for (let i = routineMarks.length - 1; i >= 0; i--) {
    if (routineMarks[i] === 'delete') {
        routineRects.splice(i, 1);
    }
}
```

#### 3.2 重建 Label 映射

创建旧 label 到新 label 的映射：

```javascript
const oldLabelToNewLabel = {};
let newRoutineIndex = 0;
for (let i = 0; i < routineMarks.length; i++) {
    if (routineMarks[i] === 'keep') {
        // 旧 routine i 的连接点范围：[i * 2 + 1, i * 2 + 3]
        const oldLeftLabel = i * 2 + 1;
        const oldRightLabel = i * 2 + 3;
        // 新 routine newRoutineIndex 的连接点范围
        const newLeftLabel = newRoutineIndex * 2 + 1;
        const newRightLabel = newRoutineIndex * 2 + 3;
        oldLabelToNewLabel[oldLeftLabel] = newLeftLabel;
        oldLabelToNewLabel[oldRightLabel] = newRightLabel;
        newRoutineIndex++;
    }
}
```

#### 3.3 更新 Loop 的 Label

```javascript
for (const conn of connections) {
    const oldStartLabel = parseInt(conn.start.label);
    const oldEndLabel = parseInt(conn.end.label);

    // 使用映射更新 label
    if (oldLabelToNewLabel.hasOwnProperty(oldStartLabel)) {
        conn.start.label = oldLabelToNewLabel[oldStartLabel].toString();
    }
    if (oldLabelToNewLabel.hasOwnProperty(oldEndLabel)) {
        conn.end.label = oldLabelToNewLabel[oldEndLabel].toString();
    }
}
```

#### 3.4 重建 Loop 高度（Depth）

删除 routine 后，剩余 loop 的层级关系可能发生变化，需要重新计算高度：

```javascript
rebuildAllConnectionDepths();
```

**说明：**
- Loop 的高度（depth）决定了其在画布上的水平偏移量
- 删除 routine 后，loop 的包含关系可能改变，需要重新计算
- 例如：原本包含两个 routine 的外部循环，删除一个后可能变成自循环，高度应变为 0
- 详见：[Loop 层级计算逻辑](./loop层级计算逻辑.md)

### 步骤 4：更新连接点（updatePoints）

#### 4.1 生成新的连接点

根据剩余的 Routine 数量生成新的连接点：

```javascript
const displayCount = Math.max(routineRects.length, minDisplayRoutines);
pointsData = generatePoints(displayCount);
snapPoints = pointsData.snap;
linePoints = pointsData.line;
```

#### 4.2 验证 Loop 的有效性

**关键逻辑：** 检查 Loop 的起点和终点 label 是否都对应实际存在的 Routine

```javascript
function isLabelValid(label) {
    const i = (parseInt(label) - 1) / 2;
    // label 2i+1 对应左侧 routine i 和右侧 routine i-1
    const leftRoutineValid = i >= 0 && i < routineRects.length;
    const rightRoutineValid = i > 0 && (i - 1) >= 0 && (i - 1) < routineRects.length;
    return leftRoutineValid || rightRoutineValid;
}

const isStartValid = isLabelValid(labels.startLabel);
const isEndValid = isLabelValid(labels.endLabel);
```

**重要说明：**
- Label `2i+1` 是 routine `i` 的左侧连接点
- Label `2i+1` 也是 routine `i-1` 的右侧连接点（当 i > 0）
- 因此，label 3 对应 routine 0 的右侧和 routine 1 的左侧
- 验证时需要检查两侧是否至少有一侧存在

#### 4.3 更新 Loop 的连接点引用

```javascript
if (newStartPoint && newEndPoint && isStartValid && isEndValid) {
    connections[i].start = newStartPoint;
    connections[i].end = newEndPoint;
} else {
    // 删除无效的 Loop
    connections.splice(i, 1);
}
```

## 示例场景

### 场景：删除 routine_1（2 个 routines 的情况）

**初始状态：**
- routine_1 (i=0)：label 1（左），label 3（右）
- routine_2 (i=1)：label 3（左），label 5（右）
- Loop A（内部）：1→3（routine_1 的自循环）
- Loop B（外部）：1→5（跨越两个 routines）

**删除 routine_1 后：**

1. **标记阶段：**
   - routine_1 标记为 'delete'
   - routine_2 标记为 'keep'
   - Loop A 标记为 'delete'（只包含 routine_1）
   - Loop B 标记为 'keep'（还包含 routine_2）

2. **删除阶段：**
   - 删除 routine_1
   - 删除 Loop A
   - 剩余：routine_2（变成新的 routine_1），Loop B

3. **Label 映射：**
   - 旧 routine_2 (i=1) → 新 routine_1 (i=0)
   - 旧 label 3 → 新 label 1
   - 旧 label 5 → 新 label 3

4. **Loop B 更新：**
   - 旧 label：1→5
   - 新 label：1→3（变成 routine_2 的自循环）

5. **验证阶段：**
   - Label 1：i=0，左侧 routine 0 存在 ✓
   - Label 3：i=1，左侧 routine 1 不存在，但右侧 routine 0 存在 ✓
   - Loop B 有效，保留

**最终结果：**
- 1 个 routine（routine_2，显示为 routine_1）
- 1 个 loop（1→3，routine_2 的自循环）

## 关键函数

| 函数名 | 功能 | 位置 |
|--------|------|------|
| `rebuildFlowchartAfterRemove()` | 删除 routine 后重建 flowchart | card.html |
| `rebuildFlowchart()` | 核心重建函数 | card.html |
| `rebuildAllConnectionDepths()` | 重建所有 loop 的高度（depth） | card.html |
| `updatePoints()` | 更新连接点和验证 loop | card.html |
| `isLabelValid()` | 验证 label 是否对应存在的 routine | card.html（内嵌函数） |
| `calculateDeletionPreview()` | 计算删除预览（不修改数据） | card.html |

## 相关文档

- [Loop 层级计算逻辑](./loop层级计算逻辑.md) - 详细的 Loop 层级计算逻辑

## 注意事项

1. **共享连接点：** 相邻 routines 共享连接点，验证时需要考虑两侧
2. **从后向前删除：** 删除数组元素时从后向前遍历，避免索引变化
3. **Label 映射：** 只更新存在的 label，flowchart 起点(1)和终点保持不变
4. **迭代收敛：** `updatePoints` 中的验证可能需要在 `rebuildFlowchart` 之后再次检查

## 更新历史

- **2026-04-05**: 移除重复的层级计算内容
  - 将 `rebuildAllConnectionDepths()` 的详细说明移至 [Loop 层级计算逻辑](./loop层级计算逻辑.md)
  - 添加相关文档引用

- **2026-04-05**: 添加 loop 高度重建说明
  - 补充了 `rebuildAllConnectionDepths()` 的调用说明
  - 解释了删除 routine 后需要重新计算 loop 高度的原因

- **2026-04-05**: 初始版本
  - 定义了删除 routine 后的完整重建流程
  - 说明了 label 验证逻辑的重要性
  - 添加了详细的示例场景
