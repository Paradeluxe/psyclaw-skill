# Routine 块 AVTPK 信息显示逻辑

## 概述

本文档描述了 PsyClaw 项目中 Routine 块表面的信息显示逻辑。在 Canvas 上绘制的每个 Routine 块会显示其包含的 AVTPK 组件信息，包括键盘按键和各类组件的时间轴。

## 核心功能

### 1. Routine 名称显示

**位置**：每个 Routine 块的顶部左对齐显示

**样式**：
- 字体：600 12px (加粗)
- 颜色：选中状态为蓝色 (#0066cc)，未选中为黑色 (#000000)
- 对齐：左对齐
- Y 坐标：`dragRect.y + padding + 10`

### 2. 键盘按键信息显示

**功能**：显示 Routine 中所有 Keyboard 组件的按键信息

**数据获取**：
```javascript
const keyboardComponents = enabledComponents.filter(c => c.type === 'keyboard');
const allKeys = keyboardComponents
    .map(c => c.keys)
    .filter(keys => keys && keys.trim())
    .join(', ');
```

**显示逻辑**：
- 格式：`K: {按键列表}`
- 示例：`K: Space, F, J`
- 颜色：红色 (#e74c3c)
- 字体：10px
- 只显示有有效 keys 值的组件

**组件数据结构**：
```javascript
{
    type: 'keyboard',
    label: 'Keyboard',
    keys: 'Space, F, J',
    startTime: 0,
    duration: -1,
    forceEndRoutine: true,
    id: 'unique_id',
    enabled: true
}
```

### 3. 组件时间轴显示

**功能**：以时间轴形式显示 Audio、Video、Text、Picture 组件的时序信息

**数据获取**：
```javascript
const timelineComponents = enabledComponents.filter(
    c => ['audio', 'video', 'text', 'image'].includes(c.type)
);
```

**类型映射**：

| 组件类型 | 显示标签 | 颜色代码 | 含义 |
|---------|---------|---------|------|
| audio   | A       | #3498db  | 音频 |
| video   | V       | #9b59b6  | 视频 |
| text    | T       | #2ecc71  | 文本 |
| image   | P       | #f39c12  | 图片 |

**时间轴计算**：

1. **计算最大时长**：
```javascript
const maxDuration = Math.max(
    ...timelineComponents.map(c => {
        const startTime = c.startTime || 0;
        const duration = c.duration || 0;
        return startTime + (duration > 0 ? duration : 3);
    }),
    3  // 最小保证值
);
```

2. **时间条位置计算**：
```javascript
const startX = timelineStartX + (startTime / maxDuration) * timelineWidth;
const barWidth = (duration / maxDuration) * timelineWidth;
```

**绘制逻辑**：

1. **绘制时间轴背景**：
   - 位置：每个组件一行
   - 颜色：浅灰色 (#ecf0f1)
   - 尺寸：宽度为 timelineWidth，高度为 6px

2. **绘制组件时间条**：
   - 颜色：根据组件类型映射
   - 最小宽度：3px（确保即使很短也能看见）
   - Y 坐标：基于当前行号

3. **绘制类型标签**：
   - 位置：时间轴左侧
   - 对齐：右对齐
   - 颜色：深灰色 (#34495e)
   - 字体：9px

**布局参数**：

| 参数 | 值 | 说明 |
|------|-----|------|
| padding | 12 | 内边距 |
| lineHeight | 12 | 行高 |
| headerHeight | 35 | 标题区域高度（影响标题与第一个组件的间距）|
| letterWidth | 12 | 字母标签宽度 |
| letterGap | 2 | 字母与时间轴之间的间距 |
| timelineLineHeight | 18 | 时间轴组件行高 |
| timelineWidth | width - padding*2 - letterWidth - letterGap | 时间轴可用宽度 |

## 间距调整指南

Routine 块的布局由以下常量控制，它们位于 [`drawDragRect`](file:///d:/Project/PsyClaw/card.html#L2309-L2421) 函数中（约第 2328-2371 行）。

### 1. Routine 标题与第一个组件的间距

**调整方法**：修改 `headerHeight` 常量

```javascript
const headerHeight = 35;  // 当前值
```

- **增大间距**：增加 headerHeight 值（如 40、45）
- **减小间距**：减小 headerHeight 值（如 30、28）

### 2. Routine 块的整体内边距

**调整方法**：修改 `padding` 常量

```javascript
const padding = 12;  // 当前值
```

- **增大内边距**：增加 padding 值（如 15、20）
- **减小内边距**：减小 padding 值（如 10、8）

### 3. 字母标签与时间轴的间距

**调整方法**：修改 `letterGap` 常量

```javascript
const letterGap = 2;  // 当前值
```

- **增大间距**：增加 letterGap 值（如 5、8）
- **减小间距**：减小 letterGap 值（如 1、0）

### 4. 字母标签宽度

**调整方法**：修改 `letterWidth` 常量

```javascript
const letterWidth = 12;  // 当前值
```

- **增大宽度**：增加 letterWidth 值
- **减小宽度**：减小 letterWidth 值

### 5. 时间轴组件之间的行高

**调整方法**：修改 `timelineLineHeight` 常量

```javascript
const timelineLineHeight = 18;  // 当前值
```

- **增大行间距**：增加 timelineLineHeight 值（如 20、22）
- **减小行间距**：减小 timelineLineHeight 值（如 16、15）

### 6. 键盘组件的行高

**调整方法**：修改 `lineHeight` 常量

```javascript
const lineHeight = 12;  // 当前值
```

- **增大行高**：增加 lineHeight 值
- **减小行高**：减小 lineHeight 值

### 快速参考表

| 调整目标 | 修改常量 | 推荐范围 |
|---------|---------|---------|
| 标题与组件间距 | `headerHeight` | 25-45 |
| 块内边距 | `padding` | 8-20 |
| 字母与时间轴间距 | `letterGap` | 0-8 |
| 时间轴行高 | `timelineLineHeight` | 15-25 |
| 键盘组件行高 | `lineHeight` | 10-15 |

## 组件数据结构

### 扁平化结构

所有 AVTPK 组件都使用扁平的数据结构，而非嵌套结构：

**正确理解**：
```javascript
{
    type: 'keyboard',
    keys: 'Space',
    startTime: 0,
    duration: -1,
    // ...
}
```

**不是**：
```javascript
{
    k: {
        type: 'keyboard',
        keys: 'Space',
        // ...
    }
}
```

### 组件类型判断

使用 `c.type` 属性判断组件类型：

| 类型值 | 含义 | 显示 |
|--------|------|------|
| 'audio' | 音频组件 | A |
| 'video' | 视频组件 | V |
| 'text' | 文本组件 | T |
| 'image' | 图片组件 | P |
| 'keyboard' | 键盘组件 | K |

## 绘制流程

### drawDragRect 函数流程

```
1. 绘制 Routine 背景矩形
   └─ drawRoundedRect(dragRect.x, dragRect.y, width, height, borderRadius)

2. 获取组件数据
   ├─ avtpComponents = dragRect.avtpComponents || []
   └─ enabledComponents = avtpComponents.filter(c => c && c.enabled)

3. 绘制 Routine 名称
   └─ ctx.fillText(dragRect.name, x, y)

4. 绘制 Keyboard 信息
   ├─ 过滤 keyboard 组件
   ├─ 提取所有 keys
   ├─ 格式化为 "K: keys"
   └─ 绘制文本

5. 绘制 Timeline 信息
   ├─ 计算 maxDuration
   ├─ 计算 timelineWidth
   └─ 遍历每个组件：
       ├─ 绘制背景条
       ├─ 绘制彩色时间条
       └─ 绘制类型标签

6. 绘制边框
   └─ drawRoundedRect() + ctx.stroke()
```

## 与右侧编辑面板的关联

### 数据同步

Routine 块显示的信息与右侧编辑面板 (avtpForm) 完全同步：

1. **添加组件时**：
   - 用户点击 A/V/T/P/K 按钮
   - `createAvtpkComponent(type)` 创建新组件
   - 组件添加到 `activeDragRect.avtpComponents`
   - 调用 `renderAvtpComponentsList()` 更新面板
   - 调用 `draw()` 重绘 Canvas

2. **编辑组件时**：
   - 用户在面板中修改 keys 等属性
   - 直接修改 `activeDragRect.avtpComponents` 中的对象
   - 调用 `draw()` 重绘 Canvas

3. **删除组件时**：
   - 用户删除组件
   - 从 `avtpComponents` 数组中移除
   - 调用 `draw()` 重绘 Canvas

### 关键变量

| 变量 | 说明 |
|------|------|
| `routineRects` | 所有 Routine 块的数组 |
| `activeDragRect` | 当前选中的 Routine 块 |
| `selectedRoutineIndex` | 当前选中 Routine 的索引 |
| `avtpComponents` | Routine 块包含的组件数组 |

## 示例

### 示例 1：仅有 Keyboard

```
Routine: trial_1
K: Space, F, J
```

### 示例 2：Keyboard + Timeline

```
Routine: trial_2
K: space, f, j
A ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
V     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
T ▓▓▓▓▓▓▓▓▓▓▓
```

### 示例 3：复杂 Timeline

假设：
- Audio: startTime=0, duration=2
- Video: startTime=1, duration=3
- Text: startTime=0.5, duration=2.5
- Picture: startTime=2, duration=1

时间轴会显示：
```
A ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
V     ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
T   ▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓▓
P                 ▓▓▓▓▓▓▓▓
```

## 注意事项

1. **duration = -1**：Keyboard 组件的 duration 通常为 -1，表示持续到 Routine 结束，但在时间轴中会被忽略
2. **duration = 0**：如果 duration 为 0 或负数，使用默认值 3 秒
3. **最小时间条宽度**：即使组件时长很短，时间条最小也有 3px，确保可见
4. **选中和未选中状态**：Routine 名称的颜色会根据选中状态变化，但 timeline 颜色保持一致
5. **多 Keyboard 组件**：如果有多个 Keyboard 组件，所有 keys 会被合并显示

## 维护建议

1. **添加新组件类型**：在类型映射中添加新条目，并更新 `timelineComponents` 的过滤条件
2. **修改颜色**：直接修改 `typeColors` 对象中的颜色值
3. **调整布局**：修改 `padding`、`lineHeight`、`headerHeight`、`letterGap` 等参数，详见上方的 [间距调整指南](#间距调整指南)
4. **调试**：可以在关键位置添加 `console.log()` 观察数据流

---

## 动态高度调整功能

### 功能概述

Routine 块支持根据其包含的 AVTPK 组件数量**自动调整高度**，确保所有组件信息都能完整显示。同时，Canvas 的整体高度也会相应调整，以容纳所有 Routine 块。

### 高度计算逻辑

#### calculateRoutineHeight 函数

计算 Routine 块所需的最小高度：

```javascript
function calculateRoutineHeight(rect) {
    const avtpComponents = rect.avtpComponents || [];
    const enabledComponents = avtpComponents.filter(c => c && c.enabled);
    
    const padding = 8;        // 内边距
    const lineHeight = 12;   // 每行高度
    const headerHeight = 20;  // 标题区域
    const nameHeight = 20;    // 名称高度
    const minHeight = 100;    // 最小高度
    
    let height = padding + nameHeight + padding;
    
    // Keyboard 行（如果keys不为空）
    const keyboardComponents = enabledComponents.filter(c => c.type === 'keyboard');
    if (keyboardComponents.length > 0) {
        const allKeys = keyboardComponents
            .map(c => c.keys)
            .filter(keys => keys && keys.trim())
            .join(', ');
        if (allKeys) {
            height += lineHeight;
        }
    }
    
    // Timeline 组件行
    const timelineComponents = enabledComponents.filter(c => 
        ['audio', 'video', 'text', 'image'].includes(c.type)
    );
    height += timelineComponents.length * lineHeight;
    
    return Math.max(height, minHeight);
}
```

#### 高度计算公式

```
总高度 = padding + nameHeight + padding 
        + (keyboardKeys有效 ? lineHeight : 0)
        + timelineComponents数量 * lineHeight
        + padding
```

#### 示例

| 组件情况 | 计算过程 | 总高度 |
|---------|---------|-------|
| 仅名称 | 8 + 20 + 8 + 8 | 44 → 100 (最小值) |
| 名称 + 1个Timeline | 8 + 20 + 8 + 12 + 8 | 56 → 100 (最小值) |
| 名称 + Keyboard + 3个Timeline | 8 + 20 + 8 + 12 + 12*3 + 8 | 92 → 100 (最小值) |
| 名称 + Keyboard + 5个Timeline | 8 + 20 + 8 + 12 + 12*5 + 8 | 116 → 116 |

### 自动调整触发时机

高度调整会在以下情况下自动触发：

#### 1. 添加组件时

```javascript
btn.addEventListener('click', (e) => {
    const newComponent = createAvtpkComponent(type);
    activeDragRect.avtpComponents.push(newComponent);
    adjustRoutineHeight(activeDragRect);  // ✓ 调整 Routine 高度
    updateCanvasHeight();                   // ✓ 调整 Canvas 高度
    renderAvtpComponentsList(activeDragRect);
    draw();
});
```

#### 2. 删除组件时

```javascript
removeBtn.onclick = (e) => {
    component.enabled = false;
    adjustRoutineHeight(rect);  // ✓ 调整 Routine 高度
    updateCanvasHeight();       // ✓ 调整 Canvas 高度
    renderAvtpComponentsList(rect);
    draw();
};
```

#### 3. 创建新 Routine 时

```javascript
const newRect = createRoutineRect(newIndex);
routineRects[newIndex] = newRect;
selectedRoutineIndex = newIndex;
updateRoutineCount();
updateCanvasHeight();  // ✓ 调整 Canvas 高度
draw();
```

#### 4. 导入项目数据时

在以下三个导入位置都添加了高度调整：
- `loadProject()` - 从文件句柄导入
- `handleFileOpen()` - 从 FileReader 导入
- `loadProjectFromData()` - 从数据对象导入

#### 5. 撤销/重做操作时

```javascript
// undo() 中
updatePoints();
updateRoutineCount();
updateCanvasHeight();  // ✓ 调整 Canvas 高度
draw();

// redo() 中
updatePoints();
updateRoutineCount();
updateCanvasHeight();  // ✓ 调整 Canvas 高度
draw();
```

### Canvas 高度调整逻辑

#### updateCanvasHeight 函数

根据所有 Routine 块的底部位置自动扩展 Canvas 高度：

```javascript
function updateCanvasHeight() {
    let maxBottom = 0;
    routineRects.forEach(rect => {
        const bottom = rect.y + rect.height;
        if (bottom > maxBottom) {
            maxBottom = bottom;
        }
    });
    
    const requiredHeight = maxBottom + 100;  // 留出底部边距
    if (requiredHeight > canvasHeight) {
        canvasHeight = requiredHeight;
        canvas.height = canvasHeight * dpr;
        canvas.style.height = canvasHeight + 'px';
        ctx.scale(dpr, dpr);  // 重新缩放以适应新尺寸
    }
}
```

### 设计特点

#### 1. **最小高度保证**
   - Routine 块最小高度为 100px，即使没有任何组件
   - 确保即使信息很少，块也不会太小

#### 2. **只增不减**
   - Canvas 高度只会增大，不会自动缩小
   - 避免频繁调整导致的视觉抖动
   - 用户可以手动删除组件来减小高度

#### 3. **平滑扩展**
   - 当添加新组件时，高度立即更新
   - 用户可以看到高度变化，增加交互反馈

#### 4. **DPR 支持**
   - Canvas 尺寸使用设备像素比 (dpr) 进行缩放
   - 确保在高分辨率屏幕上的清晰显示

### 与连接线和点的关系

#### 自动适应机制

由于 `updateCanvasHeight()` 在 `updatePoints()` 之后调用：

1. `updatePoints()` 重新计算并分配所有 snapPoints 的位置
2. `updateCanvasHeight()` 确保 Canvas 足够容纳所有内容
3. 连接线会通过现有的 `drawConnectionLines()` 自动重绘
4. 所有点会自动调整到新位置

#### 性能优化

- **批量更新**：高度调整只在必要时触发
- **最小化重绘**：只在必要时调用 `draw()`
- **智能检测**：`updateCanvasHeight()` 只在需要时扩展

### 故障排查

#### 问题 1：Routine 块高度不变

**可能原因**：
- `adjustRoutineHeight()` 未被调用
- `calculateRoutineHeight()` 计算错误

**排查方法**：
```javascript
console.log('Current height:', rect.height);
console.log('Required height:', calculateRoutineHeight(rect));
```

#### 问题 2：Canvas 高度不变

**可能原因**：
- `updateCanvasHeight()` 未被调用
- `requiredHeight <= canvasHeight`

**排查方法**：
```javascript
console.log('Canvas height:', canvasHeight);
console.log('Required height:', requiredHeight);
```

#### 问题 3：内容被裁剪

**可能原因**：
- Canvas 高度不够
- Routine 块位置超出 Canvas 范围

**排查方法**：
- 检查是否有多个 Routine 块重叠
- 确认 `maxBottom` 计算正确
- 验证 `padding` 值是否足够

### 未来优化建议

1. **自动缩小功能**：考虑添加"优化布局"按钮，可以自动调整所有 Routine 块位置以减小 Canvas 尺寸

2. **高度缓存**：缓存每个 Routine 的高度，避免重复计算

3. **渐进式动画**：添加平滑的高度过渡动画，提升用户体验

4. **最大高度限制**：添加最大高度限制，当超过时显示滚动条或其他提示

5. **响应式调整**：根据屏幕大小自动调整 Routine 块的最大允许宽度

### 相关函数列表

| 函数名 | 功能 | 调用位置 |
|--------|------|---------|
| `calculateRoutineHeight()` | 计算单个 Routine 的最小高度 | `adjustRoutineHeight()` |
| `adjustRoutineHeight()` | 调整 Routine 块高度 | 添加/删除组件时 |
| `updateCanvasHeight()` | 调整 Canvas 整体高度 | 所有影响布局的操作后 |
| `updateConnectionPoints()` | 更新连接点位置以匹配 Routine 高度 | `updateCanvasHeight()` |
| `adjustPointsToRoutineHeights()` | 完整调整所有连接点（包含 reassignSnapPoints） | `updatePoints()` |
| `draw()` | 重绘 Canvas | 所有数据变更后 |

### 连接点动态调整

#### 问题背景

当 Routine 块的高度根据 AVTPK 组件数量自动增加时，连接点（snapPoints 和 linePoints）需要相应调整位置，以确保：

1. **连接点始终位于 Routine 块的中心**：snapPoint.y = Routine.y + Routine.height / 2
2. **连接线正确连接各个 Routine**：linePoint 位置跟随 Routine 位置
3. **视觉美观**：间距保持一致，不出现重叠或间隙

#### updateConnectionPoints 函数

在 Routine 高度变化时自动更新所有连接点的 Y 坐标：

```javascript
function updateConnectionPoints() {
    const baseY = baseStartY;
    let cumulativeY = baseY;
    
    routineRects.forEach((rect, index) => {
        // 计算 Routine 中心 Y 坐标
        const routineCenterY = cumulativeY + rect.height / 2;
        
        // 更新 snapPoint（位于 Routine 中心）
        const snapPoint = snapPoints.find(p => parseInt(p.label) === (index + 1) * 2);
        if (snapPoint) {
            snapPoint.y = routineCenterY;
        }
        
        // 更新 linePoint（位于 Routine 顶部和底部）
        // ...
        
        // 移动到下一个 Routine
        cumulativeY += spacing;
    });
}
```

#### 调用时机

`updateConnectionPoints()` 在以下情况自动调用：

1. **添加/删除 AVTPK 组件** → `adjustRoutineHeight()` → `updateCanvasHeight()` → `updateConnectionPoints()`
2. **导入项目数据** → `updatePoints()` → `adjustPointsToRoutineHeights()` → `reassignSnapPoints()`

#### 与 adjustPointsToRoutineHeights 的区别

| 函数 | 作用 | 位置 |
|------|------|------|
| `adjustPointsToRoutineHeights()` | 完整调整（包含 reassignSnapPoints） | `updatePoints()` |
| `updateConnectionPoints()` | 仅更新连接点位置 | `updateCanvasHeight()` |

### 总结

动态高度调整功能确保了：

✅ **内容完整性**：所有 AVTPK 组件信息都能完整显示
✅ **视觉美观**：Routine 块不会显得过于拥挤或空旷
✅ **自动适应**：用户添加/删除组件时无需手动调整
✅ **性能优化**：只在必要时触发重绘和尺寸调整
✅ **布局稳定**：连接线和点自动适应新的布局
✅ **精确连接**：连接点始终位于 Routine 中心，连接线正确连接
