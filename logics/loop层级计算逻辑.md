# Loop 层级计算逻辑

## 概述

本文档描述了 PsyClaw 项目中 Loop 连线层级（高度）的计算逻辑。Loop 的层级决定了其在画布上的水平偏移量，包含一切的 Loop 拥有最高的高度（最大的 X 偏移量）。

## 核心概念

### 1. Loop 包含关系定义

Loop A 包含 Loop B 的条件：
- Loop A 的起始点 ≤ Loop B 的起始点
- Loop A 的终结点 ≥ Loop B 的终结点

数学表达式：
```
if (LoopA.start <= LoopB.start && LoopA.end >= LoopB.end) {
    // Loop A 包含 Loop B
}
```

**特殊情况 - 相同起点和终点：**
当两个 Loop 的起点和终点完全相同时，后加入的 Loop 会包含先加入的 Loop。这是因为在 connections 数组中，后加入的元素排在后面，通过比较数组索引可以判断加入的先后顺序。

```
Loop A (先加入): 起点 2，终点 5，索引 0
Loop B (后加入): 起点 2，终点 5，索引 1

判断：B 包含 A（因为 B 的索引 > A 的索引）
结果：
- Loop A: height = 0
- Loop B: height = 1
```

### 2. 高度（Height）概念

高度是一个 Loop 连线相对于其他 Loop 连线的层级：
- **高度 0**：不包含任何其他 Loop 的连接（最内层/被包含的）
- **高度 1**：包含高度 0 的 Loop 的连接
- **高度 N**：包含高度 N-1 的 Loop 的连接
- **包含一切的 Loop**：拥有最高的高度（最大 X 偏移量）

### 3. 计算公式

一个 Loop 连线的高度 = 它所包含的 Loop 连线中的**最大高度** + 1

```
height(conn) = max(height(contained_conn)) + 1
```

如果一个 Loop 不包含任何其他 Loop，则其高度为 0。

## 实现代码

### 文件位置
`card.html` - 主要包含逻辑的 HTML 文件

### 核心函数

#### 1. getNestingDepth(conn, allConnections)

用于计算单个连接的层级深度。

```javascript
function getNestingDepth(conn, allConnections) {
    const startLabel = parseInt(conn.start.label);
    const endLabel = parseInt(conn.end.label);
    const connMin = Math.min(startLabel, endLabel);
    const connMax = Math.max(startLabel, endLabel);
    
    let maxContainedDepth = -1;
    
    for (const other of allConnections) {
        if (other === conn) continue;
        const otherStartLabel = parseInt(other.start.label);
        const otherEndLabel = parseInt(other.end.label);
        const otherMin = Math.min(otherStartLabel, otherEndLabel);
        const otherMax = Math.max(otherStartLabel, otherEndLabel);
        
        // 检查当前连接是否包含其他连接
        if (connMin <= otherMin && connMax >= otherMax) {
            // 特殊情况：当起点和终点完全相同时，后加入的 Loop 包含先加入的
            if (connMin === otherMin && connMax === otherMax) {
                const connIndex = allConnections.indexOf(conn);
                const otherIndex = allConnections.indexOf(other);
                if (connIndex > otherIndex) {
                    maxContainedDepth = Math.max(maxContainedDepth, other.depth);
                }
            } else {
                maxContainedDepth = Math.max(maxContainedDepth, other.depth);
            }
        }
    }
    
    return maxContainedDepth + 1;
}
```

#### 2. getNestingDepthForPreview(conn, allConnections)

用于预览时计算层级深度，功能与 `getNestingDepth` 相同。

```javascript
function getNestingDepthForPreview(conn, allConnections) {
    const startLabel = parseInt(conn.start.label);
    const endLabel = parseInt(conn.end.label);
    const connMin = Math.min(startLabel, endLabel);
    const connMax = Math.max(startLabel, endLabel);
    
    let maxContainedDepth = -1;
    
    for (const other of allConnections) {
        if (other === conn) continue;
        const otherStartLabel = parseInt(other.start.label);
        const otherEndLabel = parseInt(other.end.label);
        const otherMin = Math.min(otherStartLabel, otherEndLabel);
        const otherMax = Math.max(otherStartLabel, otherEndLabel);
        
        if (connMin <= otherMin && connMax >= otherMax) {
            // 特殊情况：当起点和终点完全相同时，后加入的 Loop 包含先加入的
            if (connMin === otherMin && connMax === otherMax) {
                const connIndex = allConnections.indexOf(conn);
                const otherIndex = allConnections.indexOf(other);
                if (connIndex > otherIndex) {
                    maxContainedDepth = Math.max(maxContainedDepth, other.depth);
                }
            } else {
                maxContainedDepth = Math.max(maxContainedDepth, other.depth);
            }
        }
    }
    
    return maxContainedDepth + 1;
}
```

#### 3. rebuildAllConnectionDepths()

重建所有连接的层级，通过迭代计算直到收敛。

```javascript
function rebuildAllConnectionDepths() {
    if (connections.length === 0) return;
    
    let changed = true;
    let iterations = 0;
    const maxIterations = connections.length + 1;
    
    while (changed && iterations < maxIterations) {
        changed = false;
        iterations++;
        
        for (const conn of connections) {
            const oldDepth = conn.depth;
            const newDepth = getNestingDepth(conn, connections);
            
            if (newDepth !== oldDepth) {
                conn.depth = newDepth;
                changed = true;
            }
        }
    }
}
```

#### 4. rebuildAllConnectionDepthsForPreview(allConnections, previewConn)

用于预览时的层级重建。

```javascript
function rebuildAllConnectionDepthsForPreview(allConnections, previewConn) {
    if (allConnections.length === 0) return;
    
    let changed = true;
    let iterations = 0;
    const maxIterations = allConnections.length + 1;
    
    while (changed && iterations < maxIterations) {
        changed = false;
        iterations++;
        
        for (const conn of allConnections) {
            const oldDepth = conn.depth;
            const newDepth = getNestingDepthForPreview(conn, allConnections);
            
            if (newDepth !== oldDepth) {
                conn.depth = newDepth;
                changed = true;
            }
        }
    }
}
```

### X 偏移量计算

连接的水平偏移量由以下公式计算：

```javascript
function getConnectionOffsetX(conn, allConnections) {
    return baseOffsetX + conn.depth * offsetXStep;
}
```

其中：
- `baseOffsetX = 150`：基础偏移量
- `offsetXStep = 80`：每层级的偏移增量
- `conn.depth`：连接的高度

## 可视化示例

```
┌────────────────────────────────────────────────────────────┐
│                                                             │
│  Loop A (高度 3)                                            │
│  X偏移量 = 150 + 3 * 80 = 390                               │
│  包含: Loop B, Loop C, Loop D                               │
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │  Loop B (高度 2)                                      │  │
│  │  X偏移量 = 150 + 2 * 80 = 310                         │  │
│  │  包含: Loop C, Loop D                                 │  │
│  │                                                      │  │
│  │  ┌────────────────────────────────────────────────┐  │  │
│  │  │                                                │  │  │
│  │  │  Loop C (高度 1)                                │  │  │
│  │  │  X偏移量 = 150 + 1 * 80 = 230                   │  │  │
│  │  │  包含: Loop D                                   │  │  │
│  │  │                                                │  │  │
│  │  │  ┌──────────────────────────────────────────┐  │  │  │
│  │  │  │                                          │  │  │  │
│  │  │  │  Loop D (高度 0)                         │  │  │  │
│  │  │  │  X偏移量 = 150 + 0 * 80 = 150            │  │  │  │
│  │  │  │  不包含任何其他 Loop                      │  │  │  │
│  │  │  │                                          │  │  │  │
│  │  │  └──────────────────────────────────────────┘  │  │  │
│  │  │                                                │  │  │
│  │  └────────────────────────────────────────────────┘  │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└────────────────────────────────────────────────────────────┘
```

## 计算步骤

### 示例场景

假设有以下 Loop 连线：
- Loop A: 起点 0，终点 10
- Loop B: 起点 2，终点 8
- Loop C: 起点 4，终点 6
- Loop D: 起点 3，终点 7

### 计算过程

1. **Loop D (起点 3, 终点 7)**
   - 检查包含关系：
     - Loop A 包含 D？ 0 ≤ 3 且 10 ≥ 7 → **是**
     - Loop B 包含 D？ 2 ≤ 3 且 8 ≥ 7 → **是**
     - Loop C 包含 D？ 4 ≤ 3 且 6 ≥ 7 → **否**（4 > 3）
   - 不包含任何 Loop → height = -1 + 1 = **0**

2. **Loop C (起点 4, 终点 6)**
   - 检查包含关系：
     - Loop A 包含 C？ 0 ≤ 4 且 10 ≥ 6 → **是**
     - Loop B 包含 C？ 2 ≤ 4 且 8 ≥ 6 → **是**
   - 包含的最大高度 = max(?, ?) = 0
   - height = 0 + 1 = **1**

3. **Loop B (起点 2, 终点 8)**
   - 检查包含关系：
     - Loop A 包含 B？ 0 ≤ 2 且 10 ≥ 8 → **是**
   - 包含的最大高度 = 1
   - height = 1 + 1 = **2**

4. **Loop A (起点 0, 终点 10)**
   - 检查包含关系：
     - 不被任何 Loop 包含
   - 包含的最大高度 = max(2, 1, 0) = 2
   - height = 2 + 1 = **3**

### 最终结果

- Loop A: 高度 3，X偏移量 390
- Loop B: 高度 2，X偏移量 310
- Loop C: 高度 1，X偏移量 230
- Loop D: 高度 0，X偏移量 150

## 注意事项

1. **迭代收敛**：`rebuildAllConnectionDepths` 函数使用迭代直到收敛，确保所有连接的深度都正确计算。

2. **预览功能**：添加新连接前会使用 `rebuildAllConnectionDepthsForPreview` 进行预览计算。

3. **Label 解析**：使用 `parseInt()` 解析连接的 label，确保数值比较正确。

4. **双向连接**：包含关系的判断与连接的起点和终点方向无关，使用 `Math.min` 和 `Math.max` 确保无论连接方向如何都能正确判断。

## 更新历史

- **2026-04-02**: 修复相同起点终点 Bug
  - 当两个 Loop 的起点和终点完全相同时，后加入的 Loop 层级 +1
  - 通过比较 connections 数组中的索引来判断加入的先后顺序
  - 后加入的 Loop 包含先加入的 Loop

- **2026-04-02**: 初始版本
  - 定义了新的包含关系判断逻辑
  - 实现了基于"高度"而非"深度"的层级计算
  - 包含一切的 Loop 现在拥有最高的 X 偏移量
