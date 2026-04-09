# defaultFlowchartSchema 修复报告

## 修复时间
2026-04-09

## 修复文件
`d:\Project\PsyClaw\chatbot.html` (第1962-2027行)

## 主要问题

### 1. Connection结构过于严格
**原问题**：Connection的required字段包含`["start", "end", "depth", "loopIsTrials"]`，这意味着LLM必须生成depth和loopIsTrials字段，即使对于简单的顺序流程也需要这些字段。

**影响**：LLM可能因为不知道如何正确生成这些字段而跳过connections，或者生成错误的格式。

### 2. ConnectionEndpoint设计过于复杂
**原问题**：
- 使用x,y坐标定位连接点
- 使用奇数编号规则（odd numbers for left, odd+2 for right）
- 需要isSnapTarget布尔字段
- required字段：`["x", "y", "label", "isSnapTarget"]`

**影响**：过于技术性的细节增加了LLM生成正确格式的难度。

## 修复内容

### 1. 简化Connection.required
```diff
- "required": ["start", "end", "depth", "loopIsTrials"],
+ "required": ["start", "end"],
```

### 2. 优化ConnectionEndpoint结构
```diff
- "required": ["x", "y", "label", "isSnapTarget"],
+ "required": ["routineId", "position"],

- "properties": {
-   "x": { "type": "number" },
-   "y": { "type": "number" },
-   "label": { "type": "integer", "description": "Connection point label (odd numbers for left, odd+2 for right)" },
-   "isSnapTarget": { "type": "boolean", "default": false }
- }

+ "properties": {
+   "routineId": {
+     "type": "integer",
+     "description": "ID of the routine this endpoint connects to"
+   },
+   "position": {
+     "type": "string",
+     "enum": ["left", "right"],
+     "description": "Position of the connection point on the routine (left=exit, right=entry)"
+   },
+   "label": {
+     "type": "string",
+     "description": "Optional connection point label for visual identification"
+   }
+ }
```

### 3. 添加更清晰的描述
为每个可选字段添加了更清晰的说明：
- `depth`: "Nesting depth for loops (0 for normal flow, 1+ for loops)"
- `loopName`: "Name of the loop (only needed if this connection creates a trial loop)"
- `loopReps`: "Number of loop repetitions (only for trial loops)"
- `loopType`: "Loop type for trial loops"
- `loopIsTrials`: "Whether this loop is a trial handler"

### 4. 修改默认值
```diff
- "loopIsTrials": { "default": true }
+ "loopIsTrials": { "default": false }

+ "depth": { "default": 0 }
```

## 修复后的优点

1. **更符合实际使用场景**：简单实验只需要routine之间的顺序连接，不需要循环相关字段
2. **更易于LLM理解**：使用routineId和position替代坐标和复杂编号
3. **更简洁的required字段**：只要求必要字段，减少生成错误
4. **更好的description**：让LLM知道何时需要使用可选字段

## 示例输出

### 简单流程（无循环）
```json
{
  "version": "1.0.0",
  "timestamp": "2026-04-09T12:00:00Z",
  "routineRects": [
    {
      "id": 0,
      "name": "instructions",
      "x": 100,
      "y": 200,
      "width": 180,
      "height": 100
    },
    {
      "id": 1,
      "name": "trial",
      "x": 350,
      "y": 200,
      "width": 180,
      "height": 100
    },
    {
      "id": 2,
      "name": "end",
      "x": 600,
      "y": 200,
      "width": 180,
      "height": 100
    }
  ],
  "connections": [
    {
      "start": { "routineId": 0, "position": "right" },
      "end": { "routineId": 1, "position": "left" }
    },
    {
      "start": { "routineId": 1, "position": "right" },
      "end": { "routineId": 2, "position": "left" }
    }
  ]
}
```

### 带循环的流程
```json
{
  "connections": [
    {
      "start": { "routineId": 0, "position": "right" },
      "end": { "routineId": 1, "position": "left" },
      "depth": 1,
      "loopName": "trials",
      "loopReps": 10,
      "loopType": "sequential",
      "loopIsTrials": true
    },
    {
      "start": { "routineId": 1, "position": "right" },
      "end": { "routineId": 0, "position": "left" }
    },
    {
      "start": { "routineId": 0, "position": "right", "label": "exit" },
      "end": { "routineId": 2, "position": "left" }
    }
  ]
}
```

## 验证建议

1. **测试简单流程生成**：输入"生成一个简单的stroop任务"
2. **测试带循环的流程**：输入"生成一个stroop任务，包含10次试次循环"
3. **检查connections完整性**：确保每次生成的JSON都包含connections数组
4. **验证schema合规性**：使用JSON Schema验证工具检查生成的输出

## 相关文件

- Schema定义：`d:\Project\PsyClaw\chatbot.html` (第1175-2049行)
- System Prompt：`d:\Project\PsyClaw\chatbot.html` (第2935-2946行)
- Debug输出：`d:\Project\PsyClaw\debug\debug_2026-04-09T15-18-49-836Z.json`

## 下一步建议

1. **更新system prompt**：在Important Notes中添加更明确的connections生成示例
2. **添加示例JSON**：在prompt中包含一个完整的connections示例
3. **实现后处理验证**：在JavaScript中添加schema验证逻辑，自动补充缺失字段
4. **测试修复效果**：重新生成stroop任务，检查是否包含connections
