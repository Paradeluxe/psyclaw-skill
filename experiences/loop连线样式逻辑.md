# Loop 连线样式逻辑

## 概述

本文档描述了 PsyClaw 项目中 Loop 连线的样式设置，包括颜色、线宽、选中状态等视觉表现。

## 样式定义

### 1. 颜色定义

| 元素 | 未选中状态 | 选中状态 |
|------|-----------|----------|
| 连线颜色 | `#808080` (灰色) | `#0066cc` (蓝色) |
| 方块边框 | `#808080` (灰色) | `#0066cc` (蓝色) |
| 方块填充 | `#ffffff` (白色) | `#e6f2ff` (浅蓝色) |
| 文字颜色 | `#808080` (灰色) | `#0066cc` (蓝色) |

### 2. 线宽定义

| 状态 | 线宽 |
|------|------|
| 默认/未选中 | 1.5px |
| 选中状态 | 2px |

## 实现代码

### 文件位置
`card.html` - `drawConnectionLines()` 函数

### 核心样式代码

```javascript
function drawConnectionLines() {
    // ... 其他代码 ...
    
    sortedConnections.forEach(conn => {
        const isSelected = activeConnection === conn;
        const isPreview = conn.loopName === 'preview';

        // 1. 连线样式
        if (isSelected && !isPreview) {
            ctx.strokeStyle = '#0066cc';  // 选中：蓝色
            ctx.lineWidth = 1.5;
        } else {
            ctx.strokeStyle = '#808080';  // 未选中：灰色
            ctx.lineWidth = 1.5;
        }
        ctx.lineCap = 'round';
        ctx.lineJoin = 'round';
        ctx.setLineDash([]);

        // 绘制连线路径...
        ctx.beginPath();
        ctx.moveTo(conn.start.x, conn.start.y);
        ctx.lineTo(conn.start.x, conn.start.y + offsetY);
        ctx.lineTo(conn.end.x, conn.start.y + offsetY);
        ctx.lineTo(conn.end.x, conn.end.y);
        ctx.stroke();

        // 2. 中间方块样式（显示重复次数）
        if (isSelected && !isPreview) {
            ctx.fillStyle = '#e6f2ff';    // 选中：浅蓝填充
            ctx.strokeStyle = '#0066cc';  // 选中：蓝色边框
            ctx.lineWidth = 2;
        } else {
            ctx.fillStyle = '#ffffff';    // 未选中：白色填充
            ctx.strokeStyle = '#808080';  // 未选中：灰色边框
            ctx.lineWidth = 1.5;
        }
        
        // 绘制圆角矩形...
        drawRoundedRect(middleX - followRectWidth / 2, cornerY - followRectHeight / 2, 
                        followRectWidth, followRectHeight, followRectRadius);
        ctx.fill();
        ctx.stroke();

        // 3. 文字样式（重复次数数字）
        ctx.fillStyle = isSelected && !isPreview ? '#0066cc' : '#808080';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.font = 'bold 16px -apple-system, BlinkMacSystemFont, SF Pro Text, sans-serif';
        ctx.fillText(loopReps, middleX, cornerY);
    });
}
```

## 视觉元素说明

### Loop 连线结构

```
    ┌─────────────────────────────┐
    │                             │
    │         ┌─────┐             │  ← 中间方块（显示重复次数）
    │         │  3  │             │
    │         └─────┘             │
    │                             │
    └─────────────────────────────┘
    ↑                           ↑
  起点                        终点
```

### 样式特点

1. **连线**：从起点垂直向上，水平连接到终点上方，再垂直向下到终点，形成「门」字形
2. **中间方块**：位于连线顶部水平段中央，显示循环重复次数
3. **圆角设计**：方块使用圆角矩形，视觉更柔和
4. **选中高亮**：选中时使用蓝色系，与未选中的灰色形成对比

## 更新历史

- **2026-04-04**: 修改未选中状态颜色
  - 连线颜色从 `#000000` (黑色) 改为 `#808080` (灰色)
  - 方块边框从 `#000000` (黑色) 改为 `#808080` (灰色)
  - 文字颜色从 `#000000` (黑色) 改为 `#808080` (灰色)
  - 选中状态保持蓝色不变
