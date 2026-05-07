# Project Menu 功能测试记录

## 测试日期
2026-05-07

## 测试内容

### 1. New Project 按钮
**功能**: 选择新的项目文件夹
**按钮 ID**: `newProjectBtn`
**事件处理**: 第 4326-4333 行

**测试步骤**:
1. 点击 "New Project" 按钮
2. 选择一个新的文件夹
3. 验证文件夹是否被设置为项目文件夹

**预期结果**:
- 打开文件夹选择对话框
- 选择后更新 `projectFolderHandle`
- 自动扫描并导入第一个 .psyclaw 文件
- 更新 UI 显示当前项目名称

**代码逻辑**:
```javascript
newProjectBtn.addEventListener('click', async () => {
    const success = await selectProjectFolder();
    if (success) {
        handleProjectFolderSelection();
    }
});
```

---

### 2. Change Folder 按钮
**功能**: 更改当前项目文件夹
**按钮 ID**: `changeProjectBtn`
**事件处理**: 第 4335-4342 行

**测试步骤**:
1. 点击 "Change Folder" 按钮
2. 选择另一个文件夹
3. 验证文件夹是否被更新

**预期结果**:
- 与 New Project 按钮功能相同
- 更新项目文件夹并刷新文件列表

**问题**: 
- 与 New Project 按钮功能重复，只是图标和文字不同

---

### 3. 创建新文件按钮
**功能**: 在当前项目文件夹中创建新的 .psyclaw 文件
**按钮 ID**: `addNewProjectFileBtn`
**事件处理**: 第 4345-4377 行

**测试步骤**:
1. 确保已选择项目文件夹
2. 点击 "+" 按钮（创建新文件）
3. 验证是否创建了新文件

**预期结果**:
- 创建格式为 `project_YYYY-MM-DDTHH-MM-SS.psyclaw` 的新文件
- 文件包含基本的空项目结构
- 刷新文件列表显示新文件
- 自动加载新创建的文件

**代码逻辑**:
```javascript
addNewProjectFileBtn.addEventListener('click', async (e) => {
    e.stopPropagation();
    if (!projectFolderHandle) {
        showToast('请先选择项目文件夹！', 'warning', 3000);
        return;
    }
    addNewProjectFileBtn.disabled = true;
    addNewProjectFileBtn.style.opacity = '0.5';
    try {
        await createNewProjectFile();
    } finally {
        addNewProjectFileBtn.disabled = false;
        addNewProjectFileBtn.style.opacity = '1';
    }
});
```

**createNewProjectFile 函数** (第 8008-8088 行):
- 生成带时间戳的文件名
- 创建空项目数据结构
- 使用 `getFileHandle(newFileName, { create: true })` 创建文件
- 写入 JSON 数据
- 清空当前 flowchart
- 更新任务列表
- 刷新文件列表 (`refreshImportDropdown()`)
- 通知 chatbot 加载新任务

---

### 4. 文件列表显示功能 ⚠️
**功能**: 显示项目文件夹中的所有 .psyclaw 文件
**容器 ID**: `menuImportFileList`
**刷新函数**: `refreshImportDropdown()` (第 8437-8483 行)

**测试步骤**:
1. 选择包含 .psyclaw 文件的文件夹
2. 打开 project menu dropdown
3. 查看 "Project Files" 部分

**预期结果**:
- 显示所有 .psyclaw 文件（不包括临时文件 ~*.psyclaw）
- 每个文件显示文件图标、文件名、删除按钮
- 文件名显示完整相对路径
- 如果没有文件，显示 "No .psyclaw files found"

**代码逻辑**:
```javascript
async function refreshImportDropdown() {
    if (!projectFolderHandle) {
        importFileListEl.innerHTML = '<div class="project-menu-import-files-empty">No project folder selected</div>';
        currentPsyclawFiles = [];
        return;
    }

    const psyclawFiles = await scanDirectory(projectFolderHandle, {
        filterFn: (name) => PathUtils.isProjectFile(name),
        maxDepth: 10,
        cacheKey: 'import'
    });

    currentPsyclawFiles = psyclawFiles;
    importFileListEl.innerHTML = '';

    if (psyclawFiles.length === 0) {
        importFileListEl.innerHTML = '<div class="project-menu-import-files-empty">No .psyclaw files found</div>';
        return;
    }

    psyclawFiles.forEach((file, index) => {
        const item = document.createElement('div');
        item.className = 'project-menu-import-files-item';
        item.title = file.path;
        item.dataset.fileIndex = index;
        item.innerHTML = `
            <svg class="file-icon">...</svg>
            <span class="project-menu-import-files-filename">${file.path}</span>
            <button class="project-menu-file-delete" data-file-index="${index}">...</button>
        `;
        importFileListEl.appendChild(item);
    });
}
```

**潜在问题**:
1. **文件路径显示**: 使用 `file.path` 显示完整路径，但如果文件在子目录中，路径可能很长
2. **缓存问题**: 使用了 5 秒缓存 (`cacheKey: 'import'`)，可能导致文件创建/删除后列表不立即更新
3. **文件名截断**: 没有 CSS 限制长文件名，可能导致布局问题

---

### 5. 文件删除功能 ⚠️ **有问题**
**功能**: 删除选定的 .psyclaw 文件
**删除按钮类**: `project-menu-file-delete`
**事件处理**: 第 8486-8498 行
**删除函数**: `deleteProjectFile()` (第 8511-8525 行)

**测试步骤**:
1. 在文件列表中选择一个文件
2. 点击文件右侧的删除图标
3. 确认删除对话框
4. 验证文件是否被删除

**预期结果**:
- 显示确认对话框 "Are you sure you want to delete ...?"
- 确认后删除文件
- 显示删除成功通知
- 刷新文件列表
- 清除缓存

**代码逻辑**:
```javascript
// 事件委托处理删除按钮点击
importFileListEl.addEventListener('click', async (e) => {
    const deleteBtn = e.target.closest('.project-menu-file-delete');
    if (deleteBtn) {
        e.stopPropagation();
        e.preventDefault();
        const fileIndex = deleteBtn.dataset.fileIndex;
        const file = currentPsyclawFiles[fileIndex];
        if (!file) return;
        const confirmed = confirm(`Are you sure you want to delete "${file.path}"?`);
        if (!confirmed) return;
        await deleteProjectFile(file.path);
        return;
    }
    
    // 处理文件项点击（导入文件）
    const fileItem = e.target.closest('.project-menu-import-files-item');
    if (fileItem) {
        const fileIndex = fileItem.dataset.fileIndex;
        const file = currentPsyclawFiles[fileIndex];
        if (file) {
            await importProjectFile(file.handle);
        }
    }
});

// 删除函数
async function deleteProjectFile(filePath) {
    try {
        await projectFolderHandle.removeEntry(filePath);
        console.log('Deleted file:', filePath);
        showNotification(`🗑️ Deleted: ${filePath}`);
        if (window.PsyClawFS && window.PsyClawFS.dirCache) {
            window.PsyClawFS.dirCache.clear();
        }
        await refreshImportDropdown();
    } catch (error) {
        console.error('Failed to delete file:', error);
        showNotification('❌ Failed to delete file');
    }
}
```

**⚠️ 发现的问题**:

1. **`removeEntry` 参数问题**:
   - 当前代码传入 `filePath`（如 "subfolder/file.psyclaw"）
   - `removeEntry` 只能删除**直接子项**，不能删除子目录中的文件
   - 如果文件在子目录中，会抛出错误

2. **正确的做法**:
   ```javascript
   // 方案 1: 使用 file.handle（推荐）
   // 但 File System Access API 没有直接删除 handle 的方法
   // 需要通过父目录删除
   
   // 方案 2: 解析路径，递归获取父目录
   async function deleteProjectFile(filePath) {
       const parts = filePath.split('/');
       const fileName = parts.pop();
       let dirHandle = projectFolderHandle;
       
       // 遍历到父目录
       for (const part of parts) {
           dirHandle = await dirHandle.getDirectoryHandle(part);
       }
       
       await dirHandle.removeEntry(fileName);
   }
   ```

3. **没有检查文件是否正在使用**:
   - 如果删除的是当前打开的文件，可能导致数据丢失
   - 应该在删除前检查 `currentProjectFile` 是否匹配

4. **错误处理不完善**:
   - 只显示通用错误消息
   - 没有区分不同类型的错误（权限、文件不存在等）

---

## 修复记录

### 2026-05-07 修复

#### 修复 1: 文件删除功能 - 支持子目录文件删除 ✅
**问题**: `removeEntry` 只能删除直接子项，无法删除子目录中的文件

**修复方案**:
- 解析文件路径，分离出父目录路径和文件名
- 递归获取父目录句柄
- 在父目录句柄上调用 `removeEntry`

**修改代码** (psyclaw.html 第 8516-8559 行):
```javascript
async function deleteProjectFile(filePath) {
    try {
        // 检查是否正在删除当前打开的文件
        if (currentProjectFile === filePath || fileHandle?.name === filePath) {
            const confirmed = confirm(`You are deleting the currently open file. Any unsaved changes will be lost. Continue?`);
            if (!confirmed) return;
        }
        
        // 解析路径，处理子目录中的文件
        const parts = filePath.split('/').filter(p => p);
        const fileName = parts.pop();
        let dirHandle = projectFolderHandle;
        
        // 递归获取父目录
        for (const part of parts) {
            dirHandle = await dirHandle.getDirectoryHandle(part);
        }
        
        // 删除文件
        await dirHandle.removeEntry(fileName);
        
        console.log('Deleted file:', filePath);
        showNotification(`🗑️ Deleted: ${filePath}`);
        
        // 清除目录缓存，确保文件列表立即更新
        if (window.PsyClawFS && window.PsyClawFS.dirCache) {
            window.PsyClawFS.dirCache.clear();
        }
        
        // 刷新列表
        await refreshImportDropdown();
    } catch (error) {
        console.error('Failed to delete file:', error);
        let message = 'Failed to delete file';
        if (error.name === 'NotAllowedError') {
            message = 'Permission denied. Cannot delete this file.';
        } else if (error.name === 'TypeMismatchError') {
            message = 'Path is not a file.';
        } else if (error.name === 'NotFoundError') {
            message = 'File not found.';
        }
        showNotification(`❌ ${message}`);
    }
}
```

**新增功能**:
- ✅ 支持删除子目录中的文件
- ✅ 删除前检查是否为当前打开的文件
- ✅ 更详细的错误提示（权限、类型错误、文件不存在）
- ✅ 清除缓存确保列表立即更新

#### 修复 2: 创建文件后清除缓存 ✅
**问题**: 创建新文件后，文件列表可能因为缓存而没有立即显示

**修复方案**:
- 在 `createNewProjectFile` 函数中，创建文件后立即清除目录缓存

**修改代码** (psyclaw.html 第 8052-8055 行):
```javascript
console.log('New project file created:', newFileName);

// 清除目录缓存，确保文件列表立即更新
if (window.PsyClawFS && window.PsyClawFS.dirCache) {
    window.PsyClawFS.dirCache.clear();
}

// 清空当前 flowchart
```

#### 修复 4: 删除确认弹窗顺序问题 ✅
**问题**: 
- 有两次确认弹窗，用户需要点击两次
- 第一次弹窗问是否删除 → 执行删除 → 第二次弹窗问是否确定删除当前文件
- 弹窗顺序不对，应该在删除前一次性确认

**修复方案**:
- 合并两个确认弹窗为一个
- 在事件处理阶段就检查是否是当前文件，一次性显示完整的确认信息
- 移除 `deleteProjectFile` 函数内部的二次确认

**修改代码**:
- 事件处理 (psyclaw.html 第 8492-8517 行):
```javascript
importFileListEl.addEventListener('click', async (e) => {
    const deleteBtn = e.target.closest('.project-menu-file-delete');
    if (deleteBtn) {
        e.stopPropagation();
        e.preventDefault();
        const fileIndex = deleteBtn.dataset.fileIndex;
        const file = currentPsyclawFiles[fileIndex];
        if (!file) {
            console.warn('Delete button clicked but file not found at index:', fileIndex);
            return;
        }
        
        // 合并确认弹窗：检查是否正在删除当前打开的文件
        let confirmMessage = `Are you sure you want to delete "${file.path}"?`;
        if (currentProjectFile === file.path || fileHandle?.name === file.path) {
            confirmMessage = `You are deleting the currently open file. Any unsaved changes will be lost.\n\nAre you sure you want to delete "${file.path}"?`;
        }
        
        const confirmed = confirm(confirmMessage);
        if (!confirmed) return;
        
        await deleteProjectFile(file.path);
        return;
    }
    // ... 其他代码
});
```

- 删除函数 (psyclaw.html 第 8520-8555 行):
```javascript
async function deleteProjectFile(filePath) {
    try {
        // 解析路径，处理子目录中的文件
        const parts = filePath.split('/').filter(p => p);
        const fileName = parts.pop();
        let dirHandle = projectFolderHandle;
        
        // 递归获取父目录
        for (const part of parts) {
            dirHandle = await dirHandle.getDirectoryHandle(part);
        }
        
        // 删除文件
        await dirHandle.removeEntry(fileName);
        
        console.log('Deleted file:', filePath);
        showNotification(`🗑️ Deleted: ${filePath}`);
        
        // 清除目录缓存，确保文件列表立即更新
        if (window.PsyClawFS && window.PsyClawFS.dirCache) {
            window.PsyClawFS.dirCache.clear();
        }
        
        // 刷新列表
        await refreshImportDropdown();
    } catch (error) {
        console.error('Failed to delete file:', error);
        // ... 错误处理
    }
}
```

**效果**:
- ✅ 只显示一次确认弹窗
- ✅ 如果是当前文件，弹窗会明确提示"正在删除当前打开的文件，未保存的更改将丢失"
- ✅ 弹窗在删除操作之前显示
- ✅ 用户体验更好

---

## 问题总结

### 已修复的问题
1. ✅ **文件删除功能无法删除子目录中的文件** - 已修复
2. ✅ **文件列表缓存可能导致显示不及时** - 已修复
3. ✅ **删除当前打开的文件没有警告** - 已修复
4. ✅ **错误提示不够详细** - 已修复
5. ✅ **删除按钮 SVG 事件处理问题** - 已修复
6. ✅ **删除确认弹窗顺序问题** - 已修复（合并为一次弹窗）

### 待改进的问题
1. 💡 **New Project 和 Change Folder 功能重复** - 两个按钮调用相同的函数
2. 💡 **删除确认使用原生对话框** - 可以使用自定义确认对话框

---

## 修复建议

### 修复 1: 文件删除功能
```javascript
async function deleteProjectFile(filePath) {
    try {
        // 解析路径
        const parts = filePath.split('/');
        const fileName = parts.pop();
        let dirHandle = projectFolderHandle;
        
        // 递归获取父目录
        for (const part of parts) {
            if (part) {
                dirHandle = await dirHandle.getDirectoryHandle(part);
            }
        }
        
        // 删除文件
        await dirHandle.removeEntry(fileName);
        
        console.log('Deleted file:', filePath);
        showNotification(`🗑️ Deleted: ${filePath}`);
        
        // 清除缓存
        if (window.PsyClawFS && window.PsyClawFS.dirCache) {
            window.PsyClawFS.dirCache.clear();
        }
        
        // 刷新列表
        await refreshImportDropdown();
    } catch (error) {
        console.error('Failed to delete file:', error);
        let message = 'Failed to delete file';
        if (error.name === 'NotAllowedError') {
            message = 'Permission denied. Cannot delete this file.';
        } else if (error.name === 'TypeMismatchError') {
            message = 'Path is not a file.';
        }
        showNotification(`❌ ${message}`);
    }
}
```

### 修复 2: 添加当前文件检查
```javascript
async function deleteProjectFile(filePath) {
    // 检查是否正在删除当前打开的文件
    if (currentProjectFile === filePath || fileHandle?.name === filePath) {
        const confirmed = confirm(`You are deleting the currently open file. Any unsaved changes will be lost. Continue?`);
        if (!confirmed) return;
    }
    
    // ... 删除逻辑
}
```

---

## 测试清单

- [ ] New Project 按钮 - 选择新文件夹
- [ ] Change Folder 按钮 - 切换文件夹
- [ ] 创建新文件按钮 - 创建 .psyclaw 文件
- [ ] 文件列表显示 - 显示所有 .psyclaw 文件
- [ ] 文件删除 - 删除根目录文件
- [ ] 文件删除 - 删除子目录文件（会失败，需要修复）
- [ ] 文件导入 - 点击文件项导入
- [ ] 缓存刷新 - 创建/删除后立即刷新

---

## 相关文件
- [psyclaw.html](file:///e:/ProjLegacy/DeepPsych/psyclaw.html) - 主文件
- [js/project-fs.js](file:///e:/ProjLegacy/DeepPsych/js/project-fs.js) - 文件系统工具
