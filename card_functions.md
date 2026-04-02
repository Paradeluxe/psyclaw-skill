# card.html 函数索引

## UI/布局控制

- [updateRoutineControlsPosition](#updateroutinecontrolsposition) - 更新 routine 控件位置
- [calculateCanvasHeight](#calculatecanvasheight) - 计算画布高度
- [showNotification](#shownotification) - 显示通知消息

## 状态管理/撤销重做

- [deepCopyState](#deepcopystate) - 深拷贝状态对象
- [saveState](#savestate) - 保存当前状态到历史栈
- [undo](#undo) - 撤销上一步操作
- [redo](#redo) - 重做已撤销的操作
- [updateUndoButtons](#updateundobuttons) - 更新撤销/重做按钮状态

## 节点和矩形生成

- [generatePoints](#generatepoints) - 生成时间线上的连接点
- [createRoutineRect](#createroutinerect) - 创建新的 routine 矩形

## AVTPK 组件管理

- [createAvtpkComponent](#createavtpkcomponent) - 创建新的 AVTPK 组件
- [createDefaultAvtpkData](#createdefaultavtpkdata) - 创建默认的 AVTPK 数据
- [renderAvtpComponentsList](#renderavtpcomponentslist) - 渲染 AVTPK 组件列表

## 连接线/嵌套管理

- [getMaxDepthForSameEndpoints](#getmaxdepthforsameendpoints) - 获取相同端点连接的最大深度
- [getNestingDepth](#getnestingdepth) - 获取连接的嵌套深度
- [getConnectionOffsetX](#getconnectionoffsetx) - 获取连接线的 X 轴偏移量
- [getFollowRectPosition](#getfollowrectposition) - 获取循环跟随矩形的位置
- [getAllFollowRectPositions](#getallfollowrectpositions) - 获取所有跟随矩形位置
- [isOverlapping](#isoverlapping) - 检查连接线是否重叠

## 绘制函数

- [drawRoundedRect](#drawroundedrect) - 绘制圆角矩形
- [drawPreviewLine](#drawpreviewline) - 绘制预览连接线
- [drawConnectionLines](#drawconnectionlines) - 绘制所有连接线
- [draw](#draw) - 主绘制函数，渲染整个画布
- [drawDragRect](#drawdragrect) - 绘制可拖拽的 routine 矩形及其 AVTPK 信息

## 拖拽和吸附

- [snapToPoint](#snaptopoint) - 将矩形吸附到最近的点
- [findNearestSnapPoint](#findnearsestsnappoint) - 找到最近的吸附点
- [hasDragRectAtPoint](#hasdragrectatpoint) - 检查指定点是否有矩形
- [hasDragRectInLoopRange](#hasdragrectinlooprange) - 检查循环范围内是否有矩形
- [findNearestValidPoint](#findnearestvalidpoint) - 找到最近的有效连接点

## 鼠标和坐标

- [getMousePos](#getmousepos) - 获取鼠标在画布上的位置
- [isInsideRect](#isinsiderect) - 检查点是否在矩形内

---

## 详细信息

### AVTPK 组件显示逻辑

Routine 块的 Canvas 绘制逻辑负责在每个 routine 块上显示：

1. **Routine 名称**：顶部左对齐显示
2. **Keyboard 按键信息**：显示所有键盘组件的 keys（红色字体）
3. **组件时间轴**：A/V/T/P 组件以时间条形式显示

**组件数据结构**：所有组件使用扁平化结构，包含 `type`、`keys`、`startTime`、`duration` 等字段。

详见：[Routine 块 AVTPK 信息显示逻辑](../logics/Routine块AVTPK信息显示逻辑.md)

## 碰撞检测

- [getDragRectAtPos](#getdragrectatpos) - 获取指定位置的 routine 矩形
- [isInsidePoint](#isinsidepoint) - 检查点是否在目标点内
- [isInsideAvtpArea](#isinsideavtparea) - 检查点是否在 AVTP 区域
- [isInsideConnection](#isinsideconnection) - 检查点是否在连接线上
- [isNearSegment](#isnearsegment) - 检查点是否在线段附近
- [isInsideLoopBlock](#isinsideloopblock) - 检查点是否在循环块内
- [isInsideAvtp](#isinsideavtp) - 检查点是否在 AVTP 组件内
- [isInsideKeyArea](#isinsidekeyarea) - 检查点是否在按键区域

## 表单和模态框

- [getClickableAvtp](#getclickableavtp) - 获取可点击的 AVTP 元素
- [showAvtpForm](#showavtpform) - 显示 AVTP 编辑表单
- [hideAvtpForm](#hideavtpform) - 隐藏 AVTP 表单
- [showLoopForm](#showloopform) - 显示循环编辑表单
- [hideLoopForm](#hideloopform) - 隐藏循环表单
- [saveFormChanges](#saveformchanges) - 保存 AVTP 表单的更改
- [saveLoopFormChanges](#saveloopformchanges) - 保存循环表单的更改

## 变量和条件

- [collectAutoDetectedVariables](#collectautodetectedvariables) - 收集自动检测的变量
- [parseConditionsJSON](#parseconditionsjson) - 解析条件 JSON 字符串
- [conditionsToJSON](#conditionstojson) - 将条件转换为 JSON 字符串

## 条件表格

- [updateHeaderRow](#updateheaderrow) - 更新表格表头行
- [updateConditionsTableBody](#updateconditionstablebody) - 更新条件表格主体
- [updateCellClasses](#updatecellclasses) - 更新表格单元格样式
- [updateTargetFormsWithVariables](#updatetargetformswithvariables) - 用变量更新目标表单
- [updateConditionsTableState](#updateconditionstablestate) - 更新条件表格状态
- [switchToTableView](#switchtotableview) - 切换到表格视图模式
- [updateRoutineCount](#updateroutinecount) - 更新 routine 数量显示
- [updatePoints](#updatepoints) - 更新连接点数据
- [reassignSnapPoints](#reassignsnappoints) - 重新分配吸附点

## 键盘模态框

- [initKeyboard](#initkeyboard) - 初始化键盘事件
- [updateSelectedKeysDisplay](#updateselectedkeysdisplay) - 更新选中的按键显示
- [openKeyboardModal](#openkeyboardmodal) - 打开键盘选择模态框
- [closeKeyboardModal](#closekeyboardmodal) - 关闭键盘模态框

---

# 函数详细说明

## UI/布局控制

### updateRoutineControlsPosition
[card.html#L1343](file:///e:/ProjLegacy/DeepPsych/card.html#L1343)
根据窗口宽度和聊天面板宽度计算并更新 routine 控件的位置，使其居中显示。

### calculateCanvasHeight
[card.html#L1413](file:///e:/ProjLegacy/DeepPsych/card.html#L1413)
根据 routine 数量计算画布的最小高度，确保所有内容都能正确显示。

### showNotification
[card.html#L1421](file:///e:/ProjLegacy/DeepPsych/card.html#L1421)
在屏幕右上角显示通知消息，支持自动消失动画。

---

## 状态管理/撤销重做

### deepCopyState
[card.html#L1457](file:///e:/ProjLegacy/DeepPsych/card.html#L1457)
使用 JSON 序列化和反序列化实现深拷贝，用于保存状态快照。

### saveState
[card.html#L1461](file:///e:/ProjLegacy/DeepPsych/card.html#L1461)
将当前状态保存到历史栈，支持撤销/重做功能。

### undo
[card.html#L1476](file:///e:/ProjLegacy/DeepPsych/card.html#L1476)
撤销上一步操作，恢复之前保存的状态。

### redo
[card.html#L1500](file:///e:/ProjLegacy/DeepPsych/card.html#L1500)
重做已撤销的操作，恢复到较新的状态。

### updateUndoButtons
[card.html#L1524](file:///e:/ProjLegacy/DeepPsych/card.html#L1524)
根据历史栈和重做栈的状态更新撤销/重做按钮的可用性。

---

## 节点和矩形生成

### generatePoints
[card.html#L1540](file:///e:/ProjLegacy/DeepPsych/card.html#L1540)
在时间线上生成连接点，每隔一个点标记为可吸附目标。

### createRoutineRect
[card.html#L1587](file:///e:/ProjLegacy/DeepPsych/card.html#L1587)
创建一个新的 routine 矩形对象，包含默认的 AVTP 配置。

---

## 连接线/嵌套管理

### getMaxDepthForSameEndpoints
[card.html#L1691](file:///e:/ProjLegacy/DeepPsych/card.html#L1691)
获取与当前连接有相同端点的其他连接的最大深度。

### getNestingDepth
[card.html#L1708](file:///e:/ProjLegacy/DeepPsych/card.html#L1708)
计算连接的嵌套深度，用于确定连接线的显示层次。

### getConnectionOffsetX
[card.html#L1731](file:///e:/ProjLegacy/DeepPsych/card.html#L1731)
根据连接深度计算 X 轴偏移量，使嵌套连接线错开显示。

### getFollowRectPosition
[card.html#L1736](file:///e:/ProjLegacy/DeepPsych/card.html#L1736)
获取循环跟随矩形的坐标和尺寸信息。

### getAllFollowRectPositions
[card.html#L1752](file:///e:/ProjLegacy/DeepPsych/card.html#L1752)
获取所有连接的跟随矩形位置数组。

### isOverlapping
[card.html#L1756](file:///e:/ProjLegacy/DeepPsych/card.html#L1756)
检测两个连接线是否在视觉上重叠。

---

## 绘制函数

### drawRoundedRect
[card.html#L1780](file:///e:/ProjLegacy/DeepPsych/card.html#L1780)
使用 canvas 绘制带圆角的矩形路径。

### drawPreviewLine
[card.html#L1795](file:///e:/ProjLegacy/DeepPsych/card.html#L1795)
绘制拖拽过程中的预览连接线。

### drawConnectionLines
[card.html#L1864](file:///e:/ProjLegacy/DeepPsych/card.html#L1864)
绘制所有连接线，包括循环跟随矩形。

### draw
[card.html#L1933](file:///e:/ProjLegacy/DeepPsych/card.html#L1933)
主绘制函数，清空画布并按顺序绘制所有元素。

### drawDragRect
[card.html#L1996](file:///e:/ProjLegacy/DeepPsych/card.html#L1996)
绘制 routine 矩形，支持选中状态的高亮显示。

---

## 拖拽和吸附

### snapToPoint
[card.html#L2064](file:///e:/ProjLegacy/DeepPsych/card.html#L2064)
将矩形吸附到最近的 snap point。

### findNearestSnapPoint
[card.html#L2087](file:///e:/ProjLegacy/DeepPsych/card.html#L2087)
在所有 snap points 中找到距离最近的点。

### hasDragRectAtPoint
[column.html#L2107](file:///e:/ProjLegacy/DeepPsych/card.html#L2107)
检查指定位置是否已有 routine 矩形。

### hasDragRectInLoopRange
[card.html#L2122](file:///e:/ProjLegacy/DeepPsych/card.html#L2122)
检查循环起点和终点之间是否已有矩形。

### findNearestValidPoint
[card.html#L2139](file:///e:/ProjLegacy/DeepPsych/card.html#L2139)
找到距离最近的有效连接点（不能是自己）。

---

## 鼠标和坐标

### getMousePos
[card.html#L2156](file:///e:/ProjLegacy/DeepPsych/card.html#L2156)
获取鼠标相对于 canvas 的坐标位置。

### isInsideRect
[card.html#L2164](file:///e:/ProjLegacy/DeepPsych/card.html#L2164)
判断点坐标是否在矩形范围内。

---

## 碰撞检测

### getDragRectAtPos
[card.html#L2169](file:///e:/ProjLegacy/DeepPsych/card.html#L2169)
获取指定坐标处的 routine 矩形。

### isInsidePoint
[card.html#L2176](file:///e:/ProjLegacy/DeepPsych/card.html#L2176)
检查坐标是否在目标点区域内。

### isInsideAvtpArea
[card.html#L2183](file:///e:/ProjLegacy/DeepPsych/card.html#L2183)
检查坐标是否在 AVTP 区域（音频/视频/文本/图片/按键）内。

### isInsideConnection
[card.html#L2394](file:///e:/ProjLegacy/DeepPsych/card.html#L2394)
检查坐标是否在连接线附近。

### isNearSegment
[card.html#L2412](file:///e:/ProjLegacy/DeepPsych/card.html#L2412)
检查坐标是否在给定线段的容差范围内。

### isInsideLoopBlock
[card.html#L2425](file:///e:/ProjLegacy/DeepPsych/card.html#L2425)
检查坐标是否在循环块区域内。

### isInsideAvtp
[card.html#L2549](file:///e:/ProjLegacy/DeepPsych/card.html#L2549)
检查坐标是否在某个 AVTP 类型区域内。

### isInsideKeyArea
[card.html#L2564](file:///e:/ProjLegacy/DeepPsych/card.html#L2564)
检查坐标是否在按键区域（键盘图标）内。

---

## 表单和模态框

### getClickableAvtp
[card.html#L2577](file:///e:/ProjLegacy/DeepPsych/card.html#L2577)
获取点击位置对应的可编辑 AVTP 元素。

### showAvtpForm
[card.html#L2593](file:///e:/ProjLegacy/DeepPsych/card.html#L2593)
显示 AVTP 编辑表单模态框。

### hideAvtpForm
[card.html#L2742](file:///e:/ProjLegacy/DeepPsych/card.html#L2742)
隐藏 AVTP 编辑表单。

### showLoopForm
[card.html#L2747](file:///e:/ProjLegacy/DeepPsych/card.html#L2747)
显示循环编辑表单。

### hideLoopForm
[card.html#L2779](file:///e:/ProjLegacy/DeepPsych/card.html#L2779)
隐藏循环编辑表单。

### saveFormChanges
[card.html#L2801](file:///e:/ProjLegacy/DeepPsych/card.html#L2801)
保存 AVTP 表单中的修改到对应矩形。

### saveLoopFormChanges
[card.html#L2870](file:///e:/ProjLegacy/DeepPsych/card.html#L2870)
保存循环表单中的修改到对应连接。

---

## 变量和条件

### collectAutoDetectedVariables
[card.html#L2925](file:///e:/ProjLegacy/DeepPsych/card.html#L2925)
从所有 routine 中自动收集变量名。

### parseConditionsJSON
[card.html#L2968](file:///e:/ProjLegacy/DeepPsych/card.html#L2968)
解析条件 JSON 字符串为对象。

### conditionsToJSON
[card.html#L3006](file:///e:/ProjLegacy/DeepPsych/card.html#L3006)
将条件对象序列化为 JSON 字符串。

---

## 条件表格

### updateHeaderRow
[card.html#L3038](file:///e:/ProjLegacy/DeepPsych/card.html#L3038)
更新条件表格的表头行。

### updateConditionsTableBody
[card.html#L3061](file:///e:/ProjLegacy/DeepPsych/card.html#L3061)
更新条件表格的主体内容。

### updateCellClasses
[card.html#L3112](file:///e:/ProjLegacy/DeepPsych/card.html#L3112)
根据条件值更新表格单元格的 CSS 类。

### updateTargetFormsWithVariables
[card.html#L3125](file:///e:/ProjLegacy/DeepPsych/card.html#L3125)
用收集到的变量更新目标表单的下拉选项。

### updateConditionsTableState
[card.html#L3175](file:///e:/ProjLegacy/DeepPsych/card.html#L3175)
更新条件表格的整体状态。

### switchToTableView
[card.html#L3224](file:///e:/ProjLegacy/DeepPsych/card.html#L3224)
从编辑视图切换到表格视图。

### updateRoutineCount
[card.html#L3303](file:///e:/ProjLegacy/DeepPsych/card.html#L3303)
更新显示的 routine 数量。

### updatePoints
[card.html#L3325](file:///e:/ProjLegacy/DeepPsych/card.html#L3325)
根据当前 routine 数量更新连接点。

### reassignSnapPoints
[card.html#L3377](file:///e:/ProjLegacy/DeepPsych/card.html#L3377)
重新分配 snap points 的位置。

---

## 键盘模态框

### initKeyboard
[card.html#L3869](file:///e:/ProjLegacy/DeepPsych/card.html#L3869)
初始化键盘相关的事件监听。

### updateSelectedKeysDisplay
[card.html#L3904](file:///e:/ProjLegacy/DeepPsych/card.html#L3904)
更新已选按键的显示文本。

### openKeyboardModal
[card.html#L3922](file:///e:/ProjLegacy/DeepPsych/card.html#L3922)
打开键盘选择模态框。

### closeKeyboardModal
[card.html#L3929](file:///e:/ProjLegacy/DeepPsych/card.html#L3929)
关闭键盘选择模态框。