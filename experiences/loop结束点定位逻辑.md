# Loop 结束点定位逻辑

## 概述

本文档描述了 PsyClaw 项目中 Loop 连接点 label 与 routine 索引之间的映射关系，特别是 loop 结束点如何正确对应到 routine 的结束位置。

## 连接点 Label 系统

### Label 分配规则

在 `card.html` 中，每个 routine 有两个连接点（都是奇数 label）：

| Routine 索引 | 左侧连接点 Label | 右侧连接点 Label |
|-------------|-----------------|-----------------|
| routine_0   | 1               | 3               |
| routine_1   | 3               | 5               |
| routine_2   | 5               | 7               |
| routine_i   | 2*i + 1         | 2*i + 3         |

**关键观察：**
- label = 2*i + 1：routine i 的**左侧**连接点（也是 routine i-1 的右侧）
- label = 2*i + 3：routine i 的**右侧**连接点（也是 routine i+1 的左侧）

### 从 Label 计算 Routine 索引

```
routine 索引 = (label - 1) / 2
```

例如：
- label = 1: (1-1)/2 = 0 → routine_0 的左侧
- label = 3: (3-1)/2 = 1 → routine_0 的右侧 / routine_1 的左侧
- label = 5: (5-1)/2 = 2 → routine_1 的右侧 / routine_2 的左侧

## Loop 结束点定位问题

### 问题描述

当生成 PsychoPy XML 时，需要将 loop 的结束点 label 转换为 routine 索引，以确定：
1. Loop 在哪个 routine 结束
2. 在 Flow 中何时插入 `LoopTerminator`

### 原代码的问题

原代码计算 `endRoutineIndex`：

```javascript
endRoutineIndex = Math.floor((endLabel - 1) / 2);
```

**示例问题：**
- endLabel = 3（routine_0 的右侧）
- 计算结果：Math.floor((3-1)/2) = 1
- 错误：loop 被认为在 routine_1 结束
- 正确：loop 应该在 routine_0 结束

### 正确逻辑

当 endLabel 连接到某个 routine 的**右侧**时，表示 loop 在**该 routine** 结束。

当 endLabel 连接到某个 routine 的**左侧**时，表示 loop 在**前一个 routine** 结束。

由于所有 label 都是奇数，统一使用以下公式：

```javascript
const endConnIndex = Math.floor((endLabel - 1) / 2);
endRoutineIndex = endConnIndex - 1;
```

**验证：**
- endLabel = 3（routine_0 的右侧）：endConnIndex = 1, endRoutineIndex = 0 ✓
- endLabel = 5（routine_1 的右侧）：endConnIndex = 2, endRoutineIndex = 1 ✓
- endLabel = 1（routine_0 的左侧）：endConnIndex = 0, endRoutineIndex = -1（无效，但这种情况不应该发生）

## 实现代码

### 文件位置

`json2psyexp.js` - JSON 到 PsychoPy XML 转换器

### 核心代码

```javascript
loopConnections.forEach(conn => {
    const startLabel = parseInt(conn.start.label);
    const endLabel = parseInt(conn.end.label);
    
    // 连接点 label 为奇数：label = 2*i + 1 表示 routine i 的左侧连接点
    // 连接点 label 为奇数：label = 2*i + 3 表示 routine i 的右侧连接点
    // 因此：routine i 的左侧 label = 2*i + 1，右侧 label = 2*i + 3
    // 从 label 计算 routine 索引：i = (label - 1) / 2
    const startRoutineIndex = Math.floor((startLabel - 1) / 2);
    let endRoutineIndex;
    
    if (startLabel === endLabel) {
        // 起点和终点相同，loop 只包含一个 routine
        endRoutineIndex = startRoutineIndex;
    } else {
        // endLabel 是奇数，表示连接到某个 routine 的左侧或右侧
        // 当 endLabel = 2*i + 1（routine i 的左侧），表示 loop 在 routine i-1 结束
        // 当 endLabel = 2*i + 3（routine i 的右侧），表示 loop 在 routine i 结束
        // 统一使用 endConnIndex - 1 计算
        const endConnIndex = Math.floor((endLabel - 1) / 2);
        endRoutineIndex = endConnIndex - 1;
    }
    
    console.log(`Loop ${conn.loopName}: startLabel=${startLabel}, endLabel=${endLabel}, startRoutineIndex=${startRoutineIndex}, endRoutineIndex=${endRoutineIndex}`);
    
    loops.push({
        name: conn.loopName || 'trials',
        reps: conn.loopReps || 1,
        loopType: conn.loopType || 'sequential',
        conditions: conn.loopConditions || '',
        isTrials: conn.loopIsTrials !== false,
        startRoutineIndex: startRoutineIndex,
        endRoutineIndex: endRoutineIndex,
        depth: conn.depth || 0
    });
});
```

## Flow 生成逻辑

### Loop 在 Flow 中的位置

```javascript
for (let i = 0; i < routineRects.length; i++) {
    // 1. 找出在这个 routine 处开始的循环（深度小的先开始）
    const loopsStartingHere = loops.filter(l => 
        l.startRoutineIndex === i && !activeLoops.has(l.name)
    ).sort((a, b) => a.depth - b.depth);
    loopsStartingHere.forEach(loop => {
        xml += generateLoopInitiator(loop);
        activeLoops.add(loop.name);
    });
    
    // 2. 插入 routine
    xml += `    <Routine name="${routineNames[i]}"/>\n`;
    
    // 3. 找出在这个 routine 处结束的循环（深度大的先结束）
    const loopsEndingHere = loops.filter(l => 
        l.endRoutineIndex === i && activeLoops.has(l.name)
    ).sort((a, b) => b.depth - a.depth);
    loopsEndingHere.forEach(loop => {
        xml += generateLoopTerminator(loop);
        activeLoops.delete(loop.name);
    });
}
```

### 示例

**场景：**
- routine_0: routine_1
- routine_1: routine_2
- Loop trials_1: 从 label=1 到 label=3（包围 routine_0）
- Loop trials: 从 label=1 到 label=5（包围 routine_0 和 routine_1）

**计算：**
- trials_1: startLabel=1, endLabel=3
  - startRoutineIndex = (1-1)/2 = 0
  - endConnIndex = (3-1)/2 = 1
  - endRoutineIndex = 1 - 1 = 0
  - 结果：在 routine_0 开始，在 routine_0 结束 ✓

- trials: startLabel=1, endLabel=5
  - startRoutineIndex = (1-1)/2 = 0
  - endConnIndex = (5-1)/2 = 2
  - endRoutineIndex = 2 - 1 = 1
  - 结果：在 routine_0 开始，在 routine_1 结束 ✓

**生成的 Flow XML：**
```xml
<Flow>
  <LoopInitiator loopType="TrialHandler" name="trials">
    <LoopInitiator loopType="TrialHandler" name="trials_1">
      <Routine name="routine_1"/>
    <LoopTerminator name="trials_1"/>
    <Routine name="routine_2"/>
  <LoopTerminator name="trials"/>
</Flow>
```

## 可视化对比

### 修复前（错误）

```
connections: label 1 → label 3 (trials_1)
             label 1 → label 5 (trials)

错误计算：
- trials_1: endLabel=3 → endRoutineIndex = 1 (错误！应该在 routine_0 结束)
- trials: endLabel=5 → endRoutineIndex = 2 (错误！应该在 routine_1 结束)
```

### 修复后（正确）

```
connections: label 1 → label 3 (trials_1)
             label 1 → label 5 (trials)

正确计算：
- trials_1: endLabel=3 → endConnIndex=1 → endRoutineIndex = 0 ✓
- trials: endLabel=5 → endConnIndex=2 → endRoutineIndex = 1 ✓
```

## 注意事项

1. **Label 必须是奇数**：当前系统只使用奇数 label 作为连接点

2. **endLabel 不能等于 1**：label=1 是 routine_0 的左侧，如果 endLabel=1，则 endRoutineIndex=-1，这是无效情况

3. **startLabel 和 endLabel 相同**：表示 loop 只包含一个 routine，此时 endRoutineIndex = startRoutineIndex

4. **Flow 顺序**：
   - LoopInitiator 在 routine 之前插入
   - LoopTerminator 在 routine 之后插入
   - 多个 loop 在同一位置开始时，深度小的先开始
   - 多个 loop 在同一位置结束时，深度大的先结束

## 更新历史

- **2026-04-09**: 修复 endRoutineIndex 计算逻辑
  - 问题：endLabel 转换为 routine 索引时结果偏移 1
  - 修复：统一使用 `endConnIndex - 1` 计算 endRoutineIndex
  - 影响：`json2psyexp.js` 中的 `generateFlow` 函数
