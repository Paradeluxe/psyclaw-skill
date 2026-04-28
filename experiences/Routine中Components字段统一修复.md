# Routine 中 Components 字段统一修复

## 问题描述
所有保存逻辑都丢失了 routine 里的 component 数据。

## 问题根源
项目中使用了两种不同的字段名来存储 routine 的组件数据：
- `avtpComponents` - psyclaw.html 内部历史使用的字段名
- `components` - flowchart.schema.json v2.0 标准定义的字段名

当从 chatbot 导入数据时，数据使用 `components` 字段，但部分代码只读取 `avtpComponents` 字段，导致组件数据丢失。

## 解决方案
**统一使用 `components` 字段**（schema v2.0 标准），完全移除 `avtpComponents` 的兼容代码。

## 修改的文件和位置

### psyclaw.html

#### 1. 保存逻辑
- **第 3028 行** - `updateCurrentTaskFlowchartAndNotify` 函数
- **第 3095 行** - `autoSaveProject` 函数  
- **第 7400 行** - 保存按钮处理
- **第 7623 行** - 另存为按钮处理

修改前：
```javascript
avtpComponents: rect.avtpComponents || []
```

修改后：
```javascript
components: rect.components || []
```

#### 2. 解析逻辑
- **第 7293、7311 行** - `parseProjectData` 函数

修改前：
```javascript
const rawComponents = r.avtpComponents || r.components || [];
// ...
avtpComponents: processedComponents,
```

修改后：
```javascript
const rawComponents = r.components || [];
// ...
components: processedComponents,
```

#### 3. 消息通信
- **第 8207 行** - `request-flowchart-state` 消息处理
- **第 8247、8265 行** - `restore-flowchart-state` 消息处理

#### 4. UI 渲染
- **第 4093 行** - `calculateRoutineHeight` 函数
- **第 5225 行** - 绘制 routine 的代码
- **第 6333-6341 行** - `renderAvtpComponentsList` 函数
- **第 6402 行** - 添加组件的代码

#### 5. 其他
- **第 4075 行** - 创建 routine 的初始数据
- **第 4183 行** - 诊断检查代码
- **第 6649-6651 行** - 变量检测代码
- **第 8073 行** - `flowchart-generated` 消息处理

### json2psyexp.js

#### 1. collectRandomPatterns 函数（第 51 行）
修改前：
```javascript
const components = routineRect.avtpComponents || routineRect.components;
```

修改后：
```javascript
const components = routineRect.components;
```

#### 2. collectRandomPatternsFromRoutine 函数（第 268 行）
修改前：
```javascript
const components = routine.components || routine.avtpComponents || [];
```

修改后：
```javascript
const components = routine.components || [];
```

#### 3. generateRoutine 函数（第 425 行）
修改前：
```javascript
const components = routine.components || routine.avtpComponents || [];
```

修改后：
```javascript
const components = routine.components || [];
```

#### 4. detectVariablesFromRoutines 函数（第 702 行）
修改前：
```javascript
const components = routine.avtpComponents || routine.components || [];
```

修改后：
```javascript
const components = routine.components || [];
```

## 验证方法
1. **保存时**：检查生成的 JSON 中 routines 包含 `components` 数组
2. **导入时**：检查 `parseProjectData` 正确读取 `components` 并赋值给 `routine.components`
3. **导出时**：检查 `json2psyexp.js` 正确读取 `routine.components`

## 经验教训
1. **字段名一致性至关重要** - 数据流的所有环节必须使用相同的字段名
2. **Schema 是单一真相源** - `flowchart.schema.json` 定义了标准格式，代码必须遵循
3. **避免兼容代码** - 同时支持多种字段名会导致混乱，应该统一使用标准格式
4. **全面搜索替换** - 修改时要搜索所有相关文件，确保没有遗漏

## 相关文件
- `psyclaw.html` - 主编辑器
- `json2psyexp.js` - PsychoPy XML 导出
- `flowchart.schema.json` - 数据格式标准
