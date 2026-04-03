# 无限 Canvas 实现逻辑

## 概述

本文档描述了 PsyClaw 项目中无限 Canvas（Infinite Canvas）的实现逻辑。无限 Canvas 允许用户自由缩放和平移 flowchart，以便更好地查看和编辑复杂的实验流程。

## 核心功能

### 1. 视口状态管理

**状态变量**：
```javascript
let viewportX = 0;        // 视口 X 偏移（世界坐标系）
let viewportY = 0;        // 视口 Y 偏移（世界坐标系）
let scale = 1;            // 缩放比例
const minScale = 0.25;    // 最小缩放 25%
const maxScale = 3;       // 最大缩放 300%
```

**视口变换原理**：
- 屏幕坐标 = (世界坐标 + viewport) × scale
- 世界坐标 = 屏幕坐标 / scale - viewport

### 2. 画布渲染变换

**Draw 函数中的变换**：
```javascript
function draw() {
    ctx.save();
    ctx.setTransform(1, 0, 0, 1, 0, 0);
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.restore();

    ctx.save();
    ctx.translate(viewportX * scale, viewportY * scale);
    ctx.scale(scale, scale);
    
    // 绘制 flowchart 内容...
    
    ctx.restore();
}
```

**关键点**：
- 先清空整个 canvas（使用 identity transform）
- 然后应用视口变换：先平移再缩放
- 所有绘制操作都在变换后的坐标系中进行

### 3. 鼠标位置转换

**getMousePos 函数**：
```javascript
function getMousePos(e) {
    const rect = canvas.getBoundingClientRect();
    const screenX = e.clientX - rect.left;
    const screenY = e.clientY - rect.top;
    return {
        x: (screenX / scale) - viewportX,
        y: (screenY / scale) - viewportY
    };
}
```

**转换逻辑**：
- 屏幕坐标 → 世界坐标
- 公式：世界坐标 = 屏幕坐标 / scale - viewport

### 4. 缩放功能

#### 4.1 滚轮缩放

**实现代码**：
```javascript
canvas.addEventListener('wheel', (e) => {
    e.preventDefault();

    // 计算排除 chatbot 后的画布中心
    const chatbotWidth = chatbotPanel.offsetWidth;
    const canvasCenterX = (window.innerWidth - chatbotWidth) / 2;
    const canvasCenterY = window.innerHeight / 2;

    const zoomFactor = e.deltaY > 0 ? 0.9 : 1.1;
    const newScale = Math.max(minScale, Math.min(maxScale, scale * zoomFactor));

    // 获取缩放中心（选中 routine 或第一个 routine）
    const flowchartCenter = getFlowchartCenter();
    
    // 将 flowchart 中心点置于画布中心（排除 chatbot）
    viewportX = canvasCenterX / newScale - flowchartCenter.x;
    viewportY = canvasCenterY / newScale - flowchartCenter.y;
    scale = newScale;

    draw();
    updateZoomLevelDisplay();
}, { passive: false });
```

**缩放中心计算**：
- 排除 chatbot 后的画布中心：`canvasCenterX = (window.innerWidth - chatbotWidth) / 2`
- 以选中或第一个 routine 的中心为缩放中心
- 公式：`viewport = 屏幕中心/scale - 世界中心`

#### 4.2 按钮缩放

**Zoom In**：
```javascript
function zoomIn() {
    const chatbotWidth = chatbotPanel.offsetWidth;
    const canvasCenterX = (window.innerWidth - chatbotWidth) / 2;
    const canvasCenterY = window.innerHeight / 2;
    
    const newScale = Math.min(maxScale, scale * 1.2);
    
    const flowchartCenter = getFlowchartCenter();
    
    viewportX = canvasCenterX / newScale - flowchartCenter.x;
    viewportY = canvasCenterY / newScale - flowchartCenter.y;
    scale = newScale;

    draw();
    updateZoomLevelDisplay();
}
```

**Zoom Out**：
```javascript
function zoomOut() {
    const chatbotWidth = chatbotPanel.offsetWidth;
    const canvasCenterX = (window.innerWidth - chatbotWidth) / 2;
    const canvasCenterY = window.innerHeight / 2;
    
    const newScale = Math.max(minScale, scale * 0.8);
    
    const flowchartCenter = getFlowchartCenter();
    
    viewportX = canvasCenterX / newScale - flowchartCenter.x;
    viewportY = canvasCenterY / newScale - flowchartCenter.y;
    scale = newScale;

    draw();
    updateZoomLevelDisplay();
}
```

**Reset View**：
```javascript
function resetView() {
    viewportX = 0;
    viewportY = 0;
    scale = 1;
    draw();
    updateZoomLevelDisplay();
}
```

### 5. 缩放中心计算

**getFlowchartCenter 函数**：
```javascript
function getFlowchartCenter() {
    if (routineRects.length === 0) {
        return { x: 400, y: 300 };
    }
    
    // 如果有选中的 routine，以选中的 routine 为中心
    if (selectedRoutineIndex >= 0 && selectedRoutineIndex < routineRects.length) {
        const selectedRect = routineRects[selectedRoutineIndex];
        return {
            x: selectedRect.x + selectedRect.width / 2,
            y: selectedRect.y + selectedRect.height / 2
        };
    }
    
    // 如果没有选中的 routine，以第一个 routine 为中心
    const firstRect = routineRects[0];
    return {
        x: firstRect.x + firstRect.width / 2,
        y: firstRect.y + firstRect.height / 2
    };
}
```

**优先级**：
1. 选中的 routine → 以其中心为缩放中心
2. 无选中 routine → 以第一个 routine 的中心为缩放中心
3. 无 routine → 默认中心 `(400, 300)`

### 6. 平移功能

#### 6.1 鼠标拖拽平移

**状态变量**：
```javascript
let isCanvasPanning = false;
let canvasPanStartX = 0;
let canvasPanStartY = 0;
let canvasPanStartViewportX = 0;
let canvasPanStartViewportY = 0;
```

**Mouse Down**：
```javascript
canvas.addEventListener('mousedown', (e) => {
    const pos = getMousePos(e);

    // 左键或中键开始平移
    if (e.button === 1 || e.button === 0) {
        const clickedRect = getDragRectAtPos(pos.x, pos.y);

        // 如果点击在 routine 上，则拖动 routine
        if (clickedRect) {
            // ... 拖动 routine 的逻辑
            return;
        }

        // 否则开始平移画布
        e.preventDefault();
        isCanvasPanning = true;
        canvasPanStartX = e.clientX;
        canvasPanStartY = e.clientY;
        canvasPanStartViewportX = viewportX;
        canvasPanStartViewportY = viewportY;
        canvas.style.cursor = 'grabbing';
        return;
    }
    // ...
});
```

**Mouse Move**：
```javascript
canvas.addEventListener('mousemove', (e) => {
    // ...

    if (isCanvasPanning) {
        const deltaX = (e.clientX - canvasPanStartX) / scale;
        const deltaY = (e.clientY - canvasPanStartY) / scale;
        viewportX = canvasPanStartViewportX + deltaX;
        viewportY = canvasPanStartViewportY + deltaY;
        draw();
        return;
    }
    // ...
});
```

**Mouse Up / Leave**：
```javascript
canvas.addEventListener('mouseup', (e) => {
    if (isCanvasPanning) {
        isCanvasPanning = false;
        canvas.style.cursor = 'grab';
        return;
    }
    // ...
});

canvas.addEventListener('mouseleave', () => {
    if (isCanvasPanning) {
        isCanvasPanning = false;
        canvas.style.cursor = 'grab';
    }
    // ...
});
```

**平移逻辑**：
- 计算鼠标移动距离（屏幕像素）
- 转换为世界坐标距离：`delta / scale`
- 更新视口偏移：`viewport = startViewport + delta`

### 7. UI 控件

#### 7.1 控件布局

**HTML 结构**：
```html
<div class="viewport-controls">
    <button class="action-button" id="zoomIn" title="Zoom In">
        <!-- 放大图标 -->
    </button>
    <button class="action-button" id="zoomOut" title="Zoom Out">
        <!-- 缩小图标 -->
    </button>
    <button class="action-button" id="resetView" title="Reset View">
        <!-- 重置图标 -->
    </button>
    <div class="zoom-level" id="zoomLevel">100%</div>
</div>
```

**CSS 样式**：
```css
.viewport-controls {
    position: fixed;
    bottom: 20px;
    left: 20px;
    display: flex;
    gap: 6px;
    z-index: 1000;
    width: auto;
    flex-shrink: 0;
}

.zoom-level {
    display: flex;
    align-items: center;
    padding: 0 8px;
    font-size: 14px;
    font-weight: 500;
    color: #333;
    min-width: 50px;
    text-align: center;
}
```

**设计特点**：
- 无背景、无边框、无阴影（与顶部按钮样式一致）
- 固定在左下角
- 显示当前缩放百分比

#### 7.2 事件绑定

```javascript
zoomInButton.addEventListener('click', zoomIn);
zoomOutButton.addEventListener('click', zoomOut);
resetViewButton.addEventListener('click', resetView);
```

### 8. 画布尺寸适配

**初始化**：
```javascript
canvas.width = window.innerWidth * dpr;
canvas.height = window.innerHeight * dpr;
canvas.style.width = '100vw';
canvas.style.height = '100vh';
ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
```

**窗口大小改变**：
```javascript
window.addEventListener('resize', () => {
    canvas.width = window.innerWidth * dpr;
    canvas.height = window.innerHeight * dpr;
    ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
    draw();
});
```

**关键点**：
- Canvas 填满整个视口
- 使用 devicePixelRatio (dpr) 确保高分辨率屏幕清晰
- 窗口大小改变时自动调整

## 坐标系说明

### 三种坐标系

1. **屏幕坐标系**（Screen Coordinates）
   - 单位：像素
   - 范围：`(0, 0)` 到 `(canvas.width, canvas.height)`
   - 用途：鼠标事件、UI 定位

2. **世界坐标系**（World Coordinates）
   - 单位：逻辑单位
   - 范围：无限
   - 用途：flowchart 元素位置、routine 坐标

3. **视口坐标系**（Viewport Coordinates）
   - 定义：视口在世界坐标系中的偏移
   - 用途：确定显示区域

### 坐标转换公式

**屏幕 → 世界**：
```javascript
worldX = (screenX / scale) - viewportX;
worldY = (screenY / scale) - viewportY;
```

**世界 → 屏幕**：
```javascript
screenX = (worldX + viewportX) * scale;
screenY = (worldY + viewportY) * scale;
```

## 交互设计

### 缩放行为

| 操作 | 效果 | 中心点 |
|------|------|--------|
| 滚轮向上 | 放大 | 选中/第一个 routine |
| 滚轮向下 | 缩小 | 选中/第一个 routine |
| 点击 + 按钮 | 放大 20% | 选中/第一个 routine |
| 点击 - 按钮 | 缩小 20% | 选中/第一个 routine |
| 点击重置 | 恢复 100% | 无 |

### 平移行为

| 操作 | 效果 |
|------|------|
| 左键拖拽空白处 | 平移画布 |
| 左键拖拽 routine | 移动 routine |
| 中键拖拽 | 平移画布 |

### 光标状态

| 状态 | 光标 |
|------|------|
| 默认 | `grab` |
| 拖拽画布中 | `grabbing` |
| 拖拽 routine 中 | `grabbing` |
| 悬停在 routine 上 | `pointer` |
| 悬停在连接点上 | `pointer` |

## 性能优化

### 1. 减少重绘

- 只在必要时调用 `draw()`
- 避免在 `mousemove` 中频繁重绘（如果需要，使用节流）

### 2. 使用 requestAnimationFrame

```javascript
let animationId;
function scheduleDraw() {
    if (animationId) return;
    animationId = requestAnimationFrame(() => {
        draw();
        animationId = null;
    });
}
```

### 3. 分层渲染（可选）

- 背景层（网格、辅助线）
- 内容层（flowchart）
- 交互层（拖拽预览、高亮）

## 故障排查

### 问题 1：缩放时内容跳动

**原因**：视口偏移计算错误

**排查**：
```javascript
console.log('Scale:', scale);
console.log('Viewport:', viewportX, viewportY);
console.log('Canvas Center:', canvasCenterX, canvasCenterY);
console.log('Flowchart Center:', flowchartCenter);
```

### 问题 2：鼠标位置不准确

**原因**：`getMousePos` 转换错误

**排查**：
```javascript
// 在点击时打印坐标
console.log('Screen:', e.clientX, e.clientY);
console.log('World:', pos.x, pos.y);
```

### 问题 3：拖拽时卡顿

**原因**：频繁重绘

**解决**：使用 `requestAnimationFrame` 节流

### 问题 4：高分辨率屏幕模糊

**原因**：未使用 dpr

**解决**：确保 `ctx.setTransform(dpr, 0, 0, dpr, 0, 0)`

## 扩展建议

### 1. 最小地图（Minimap）

显示整个 flowchart 的缩略图，支持点击跳转。

### 2. 缩放范围限制

根据 flowchart 大小动态调整最小/最大缩放。

### 3. 惯性滚动

拖拽结束后继续滑动一段距离。

### 4. 键盘快捷键

- `Ctrl + +` / `Ctrl + -`：缩放
- `Ctrl + 0`：重置
- `Space + 拖拽`：平移（已实现）

### 5. 触摸支持

- 双指缩放
- 单指平移

## 相关函数列表

| 函数名 | 功能 | 调用位置 |
|--------|------|---------|
| `getFlowchartCenter()` | 计算缩放中心 | 所有缩放操作 |
| `zoomIn()` | 放大 | 点击 + 按钮 |
| `zoomOut()` | 缩小 | 点击 - 按钮 |
| `resetView()` | 重置视图 | 点击重置按钮 |
| `getMousePos()` | 屏幕坐标转世界坐标 | 鼠标事件处理 |
| `draw()` | 重绘 Canvas | 所有变换后 |
| `updateZoomLevelDisplay()` | 更新缩放百分比显示 | 缩放后 |

## 总结

无限 Canvas 实现的核心要点：

✅ **视口管理**：使用 viewportX/Y 和 scale 控制显示区域
✅ **坐标转换**：正确实现屏幕坐标与世界坐标的双向转换
✅ **缩放中心**：以选中/第一个 routine 为中心，排除 chatbot 区域
✅ **平移交互**：支持鼠标左键/中键拖拽平移
✅ **UI 控件**：简洁的放大镜控件，显示当前缩放比例
✅ **性能优化**：合理使用重绘，支持高分辨率屏幕

---

**文件位置**：[`card.html`](file:///d:/Project/PsyClaw/card.html)
