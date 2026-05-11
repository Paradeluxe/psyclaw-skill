# Chatbot 按钮设计逻辑

## 概述

本文档描述了 PsyClaw 项目中 chatbot 界面（`chatbot.html`）的消息操作按钮设计逻辑，包括用户消息和 AI 回复的消息操作按钮。

## 按钮类型

### 1. 用户消息按钮

**位置**：每个用户消息的右下角

**按钮列表**：

| 按钮 | 图标 | 功能 | 样式 |
|------|------|------|------|
| Copy | 复制图标 | 复制消息内容到剪贴板 | 默认样式 |
| Redo | 刷新/重试图标 | 重新发送当前消息 | 默认样式 |
| Delete | 删除图标 | 删除当前消息 | danger 样式（红色） |

**代码位置**：`addMessage` 函数中创建（约第 2929-2950 行）

```javascript
// 创建消息操作按钮栏（用户消息有复制、重做和删除按钮）
const messageActions = document.createElement('div');
messageActions.className = 'message-actions';
messageActions.innerHTML = `
    <button class="message-action-btn" data-tooltip="Copy" onclick="copyMessage(this)">
        <svg viewBox="0 0 24 24">
            <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
        </svg>
    </button>
    <button class="message-action-btn" data-tooltip="Redo" onclick="redoMessage(this)">
        <svg viewBox="0 0 24 24">
            <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
        </svg>
    </button>
    <button class="message-action-btn danger" data-tooltip="Delete" onclick="deleteMessage(this)">
        <svg viewBox="0 0 24 24">
            <path d="M6 19c0 1.1.9 2 2 2h8c1.1 0 2-.9 2-2V7H6v12zM19 4h-3.5l-1-1h-5l-1 1H5v2h14V4z"/>
        </svg>
    </button>
`;
```

### 2. AI 消息按钮

**位置**：每个 AI 回复消息的右下角

**按钮列表**：

| 按钮 | 图标 | 功能 | 样式 |
|------|------|------|------|
| Copy | 复制图标 | 复制 AI 回复内容到剪贴板 | 默认样式 |
| Redo | 刷新/重试图标 | 重新生成当前回复 | 默认样式 |

**特殊说明**：
- 第一个 AI 回复（outline 生成阶段）不显示按钮
- Turn 1 和 Turn 2 算作一个完整回复，按钮统一显示在 Turn 2 完成后

**代码位置**：`addAssistantMessageWithThink` 函数中创建（约第 3018-3035 行）

```javascript
// 创建消息操作按钮栏（第一个AI回复不显示）
const messageActions = document.createElement('div');
messageActions.className = 'message-actions';
if (isFirstAssistantMessage) {
    messageActions.style.display = 'none'; // 第一个AI回复隐藏按钮
}
messageActions.innerHTML = `
    <button class="message-action-btn" data-tooltip="Copy" onclick="copyMessage(this)">
        <svg viewBox="0 0 24 24">
            <path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/>
        </svg>
    </button>
    <button class="message-action-btn" data-tooltip="Redo" onclick="redoAssistantMessage(this)">
        <svg viewBox="0 0 24 24">
            <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
        </svg>
    </button>
`;
```

### 3. Flowchart 完成后的按钮

**位置**：Flowchart JSON 生成完成后，显示在消息容器底部

**按钮列表**：

| 按钮 | 图标 | 功能 |
|------|------|------|
| Copy | 复制图标 | 复制完整的 flowchart JSON |
| Redo | 刷新/重试图标 | 重新生成整个回复（outline + flowchart） |

**代码位置**：`finalizeMessage` 函数中创建（约第 3111-3162 行）

```javascript
// 创建 flowchart 操作按钮栏（Copy、Redo）
const actionsDiv = document.createElement('div');
actionsDiv.className = 'inline-description-actions';
actionsDiv.style.cssText = 'display: flex; align-items: center; margin-top: 8px; width: 100%;';

const leftActionsDiv = document.createElement('div');
leftActionsDiv.style.cssText = 'display: flex; gap: 0px;';

// Copy 按钮
const copyBtn = document.createElement('button');
copyBtn.className = 'message-action-btn';
copyBtn.setAttribute('data-tooltip', 'Copy');
copyBtn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M16 1H4c-1.1 0-2 .9-2 2v14h2V3h12V1zm3 4H8c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h11c1.1 0 2-.9 2-2V7c0-1.1-.9-2-2-2zm0 16H8V7h11v14z"/></svg>`;
copyBtn.onclick = () => { /* 复制逻辑 */ };
leftActionsDiv.appendChild(copyBtn);

// Redo 按钮
const redoBtn = document.createElement('button');
redoBtn.className = 'message-action-btn';
redoBtn.setAttribute('data-tooltip', 'Redo');
redoBtn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/></svg>`;
redoBtn.onclick = () => { /* 重做逻辑 */ };
leftActionsDiv.appendChild(redoBtn);

actionsDiv.appendChild(leftActionsDiv);
wrapper.appendChild(actionsDiv);
```

## 按钮样式

### CSS 类

| 类名 | 说明 |
|------|------|
| `message-actions` | 按钮栏容器 |
| `message-action-btn` | 单个按钮 |
| `danger` | 危险操作样式（删除按钮） |
| `success` | 成功状态样式（复制成功时临时添加） |
| `inline-description-actions` | Flowchart 完成后的按钮栏 |

### 样式定义

```css
.message-actions {
    display: flex;
    gap: 4px;
    margin-top: 4px;
    opacity: 0;
    transition: opacity 0.2s ease;
}

.message-wrapper:hover .message-actions {
    opacity: 1;
}

.message-action-btn {
    background: transparent;
    border: none;
    padding: 4px;
    cursor: pointer;
    border-radius: 4px;
    display: flex;
    align-items: center;
    justify-content: center;
    color: var(--text-gray);
    transition: all 0.2s ease;
}

.message-action-btn:hover {
    background: var(--hover-bg);
    color: var(--text-primary);
}

.message-action-btn.danger:hover {
    background: #fee2e2;
    color: #dc2626;
}

.message-action-btn.success {
    color: #16a34a;
}

.message-action-btn svg {
    width: 16px;
    height: 16px;
    fill: currentColor;
}
```

## 功能实现

### 1. Copy 功能

**函数**：`copyMessage(btn)`

**位置**：约第 3837-3870 行

**逻辑**：
1. 找到最近的 `.message-wrapper`
2. 获取 `.chat-message` 的文本内容
3. 使用 `navigator.clipboard.writeText` 复制到剪贴板
4. 临时改变按钮图标为勾选状态，1.5秒后恢复

```javascript
window.copyMessage = function(btn) {
    const wrapper = btn.closest('.message-wrapper');
    if (!wrapper) return;

    const msgDiv = wrapper.querySelector('.chat-message');
    if (msgDiv && msgDiv.textContent) {
        navigator.clipboard.writeText(msgDiv.textContent).then(() => {
            btn.classList.add('success');
            const originalSvg = btn.innerHTML;
            btn.innerHTML = `<svg viewBox="0 0 24 24"><path d="M9 16.17L4.83 12l-1.42 1.41L9 19 21 7l-1.41-1.41z"/></svg>`;
            showToast('Copied to clipboard', 'success', 1500);
            setTimeout(() => {
                btn.innerHTML = originalSvg;
                btn.classList.remove('success');
            }, 1500);
        });
    }
};
```

### 2. Redo 功能（用户消息）

**函数**：`redoMessage(btn)`

**位置**：约第 4099-4180 行

**逻辑**：
1. 获取存储在 `dataset.originalPrompt` 中的原始 prompt
2. 终止当前正在进行的请求（如果有）
3. 删除当前消息及其之后的所有消息（包括 AI 回复）
4. 重置对话状态
5. 将原始 prompt 填入输入框并重新发送

```javascript
window.redoMessage = async function(btn) {
    const wrapper = btn.closest('.message-wrapper');
    if (!wrapper) return;

    const originalPrompt = wrapper.dataset.originalPrompt;
    if (!originalPrompt) {
        showToast('No original prompt found', 'error', 2000);
        return;
    }

    // 1. 终止当前正在进行的请求
    if (currentAbortController) {
        currentAbortController.abort();
        currentAbortController = null;
    }

    // 2. 找到当前用户消息及其之后的所有消息并删除
    const allWrappers = Array.from(chatMessagesDiv.querySelectorAll('.message-wrapper, .assistant-message-wrapper'));
    const currentIndex = allWrappers.findIndex(w => w === wrapper || w.contains(wrapper));
    
    if (currentIndex === -1) return;

    // 删除当前消息及之后的所有消息
    const wrappersToRemove = allWrappers.slice(currentIndex);
    wrappersToRemove.forEach(w => {
        w.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
        w.style.opacity = '0';
        w.style.transform = 'translateX(20px)';
    });

    await new Promise(resolve => setTimeout(resolve, 300));
    wrappersToRemove.forEach(w => w.remove());

    // 3. 重置对话状态到适当阶段
    // ... 状态重置逻辑

    // 4. 将原始 prompt 填入输入框并发送
    chatInput.value = originalPrompt;
    await sendMessage(false);
};
```

### 3. Redo 功能（AI 消息）

**函数**：`redoAssistantMessage(btn)`

**位置**：约第 4183-4265 行

**逻辑**：
1. 找到当前 AI 消息对应的用户消息（向前查找最近的用户消息）
2. 获取该用户消息的原始 prompt
3. 终止当前正在进行的请求
4. 删除该用户消息及其之后的所有消息
5. 重置对话状态
6. 使用原始 prompt 重新发送请求

```javascript
window.redoAssistantMessage = async function(btn) {
    const assistantWrapper = btn.closest('.assistant-message-wrapper');
    if (!assistantWrapper) return;

    // 找到当前AI消息在聊天历史中的位置
    const allWrappers = Array.from(chatMessagesDiv.querySelectorAll('.message-wrapper, .assistant-message-wrapper'));
    const currentIndex = allWrappers.findIndex(w => w === assistantWrapper);
    
    if (currentIndex === -1) return;

    // 向前查找对应的用户消息
    let userWrapper = null;
    for (let i = currentIndex - 1; i >= 0; i--) {
        const wrapper = allWrappers[i];
        if (wrapper.classList.contains('user-wrapper')) {
            userWrapper = wrapper;
            break;
        }
    }

    if (!userWrapper) {
        showToast('No corresponding user message found', 'error', 2000);
        return;
    }

    const originalPrompt = userWrapper.dataset.originalPrompt;
    // ... 后续逻辑与 redoMessage 类似
};
```

### 4. Delete 功能

**函数**：`deleteMessage(btn)`

**位置**：约第 4068-4096 行

**逻辑**：
1. 找到消息容器
2. 添加淡出动画
3. 300ms 后从 DOM 中移除
4. 如果没有剩余消息，显示欢迎语

```javascript
window.deleteMessage = function(btn) {
    const wrapper = btn.closest('.message-wrapper');
    if (!wrapper) return;

    const assistantWrapper = wrapper.closest('.assistant-message-wrapper');
    const messageContainer = assistantWrapper || wrapper;

    // 添加淡出动画
    messageContainer.style.transition = 'all 0.3s cubic-bezier(0.4, 0, 0.2, 1)';
    messageContainer.style.opacity = '0';
    messageContainer.style.transform = 'translateX(20px)';

    setTimeout(() => {
        messageContainer.remove();
        // 检查是否还有消息
        const remainingMessages = chatMessagesDiv.querySelectorAll('.message-wrapper, .assistant-message-wrapper');
        if (remainingMessages.length === 0) {
            const welcomeMsg = chatMessagesDiv.querySelector('.chat-message.welcome');
            if (welcomeMsg) {
                welcomeMsg.style.display = 'flex';
            }
        }
        showToast('Message deleted', 'success', 1500);
    }, 300);
};
```

## 数据存储

### 原始 Prompt 存储

在用户消息创建时，将原始 prompt 存储在 DOM 元素的 dataset 中：

```javascript
function addMessage(content, role) {
    // ...
    if (role === 'user') {
        const wrapper = document.createElement('div');
        wrapper.className = 'message-wrapper user-wrapper';
        wrapper.dataset.originalPrompt = content; // 存储原始 prompt 用于重做
        // ...
    }
}
```

## 交互流程

### 用户点击 Redo 按钮后的完整流程：

```
1. 用户点击 Redo 按钮
   ↓
2. 获取原始 prompt
   ↓
3. 终止当前请求（如果有）
   ↓
4. 删除当前消息及之后的所有消息（带动画）
   ↓
5. 重置对话状态
   ↓
6. 将 prompt 填入输入框
   ↓
7. 调用 sendMessage() 重新发送
   ↓
8. 生成新的回复（Turn 1: outline → Turn 2: flowchart）
   ↓
9. 在 Turn 2 完成后显示 Copy 和 Redo 按钮
```

## 设计原则

1. **一致性**：所有按钮使用相同的样式和交互模式
2. **可见性**：按钮默认隐藏，鼠标悬停时显示，保持界面简洁
3. **反馈**：操作后有明确的视觉反馈（Toast 提示、图标变化）
4. **安全性**：删除操作有视觉区分（红色），避免误操作
5. **完整性**：Turn 1 和 Turn 2 算作一个完整回复，按钮统一显示

## 相关文件

- [chatbot.html](file:///d:/Project/PsyClaw/chatbot.html) - 聊天机器人界面
- [MiniMax设计系统样式引用记录.md](file:///d:/Project/PsyClaw/logics/MiniMax设计系统样式引用记录.md) - 设计系统规范

## 更新记录

| 日期 | 版本 | 说明 |
|------|------|------|
| 2026-04-15 | 1.0 | 初始文档，记录用户消息和 AI 消息的按钮设计逻辑 |

---

*注：此文档记录了 chatbot 界面中消息操作按钮的设计逻辑，用于维护和扩展功能。*
