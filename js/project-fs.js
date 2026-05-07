/**
 * PsyClaw Project File System Module
 * 统一封装文件路径处理、目录扫描、错误处理、安全校验等功能
 */
(function(global) {
    'use strict';

    const ALLOWED_ORIGIN = window.location.origin;

    function safePostMessage(target, message, targetOrigin) {
        if (!target || typeof target.postMessage !== 'function') return;
        target.postMessage(message, targetOrigin || ALLOWED_ORIGIN);
    }

    const FileErrorTypes = {
        INVALID_FORMAT: 'INVALID_FORMAT',
        SIZE_EXCEEDED: 'SIZE_EXCEEDED',
        PERMISSION_DENIED: 'PERMISSION_DENIED',
        PARSE_ERROR: 'PARSE_ERROR',
        NETWORK_ERROR: 'NETWORK_ERROR',
        UNSUPPORTED_BROWSER: 'UNSUPPORTED_BROWSER',
        UNKNOWN: 'UNKNOWN'
    };

    function handleFileError(error, context, showToastFn) {
        const prefix = context ? `[${context}] ` : '';
        console.error(prefix + 'File operation error:', error);

        let userMessage = error?.message || 'An unknown error occurred';
        let toastType = 'error';

        if (error?.name === 'AbortError') {
            return;
        }
        if (error?.name === 'NotAllowedError' || error?.name === 'SecurityError') {
            userMessage = 'Permission denied. Please check your browser settings.';
            toastType = 'warning';
        } else if (error?.name === 'SyntaxError' || error?.message?.includes('JSON')) {
            userMessage = 'Invalid file format. Please check your project file.';
        } else if (error?.type === FileErrorTypes.SIZE_EXCEEDED) {
            userMessage = error.message;
            toastType = 'warning';
        }

        if (typeof showToastFn === 'function') {
            showToastFn(prefix + userMessage, toastType, 5000);
        }
    }

    const MAX_FILE_SIZE = 50 * 1024 * 1024; // 50MB

    const PathUtils = {
        join(...parts) {
            return parts.join('/').replace(/\\/g, '/').replace(/\/+/g, '/');
        },
        normalize(path) {
            return path.replace(/\\/g, '/').replace(/\/+/g, '/');
        },
        getExt(filename) {
            const lastDot = filename.lastIndexOf('.');
            return lastDot > 0 ? filename.slice(lastDot + 1).toLowerCase() : '';
        },
        isTempFile(filename) {
            return filename.startsWith('~') && filename.endsWith('.psyclaw');
        },
        isProjectFile(filename) {
            return filename.endsWith('.psyclaw') && !filename.startsWith('~');
        }
    };

    class DirectoryCache {
        constructor(ttlMs = 5000) {
            this.cache = new Map();
            this.ttl = ttlMs;
        }

        _makeKey(dirHandle, filterKey) {
            return `${dirHandle.name}::${filterKey}`;
        }

        get(dirHandle, filterKey) {
            const key = this._makeKey(dirHandle, filterKey);
            const entry = this.cache.get(key);
            if (entry && (Date.now() - entry.time) < this.ttl) {
                return entry.results;
            }
            return null;
        }

        set(dirHandle, filterKey, results) {
            const key = this._makeKey(dirHandle, filterKey);
            this.cache.set(key, { results, time: Date.now() });
        }

        clear() {
            this.cache.clear();
        }
    }

    const dirCache = new DirectoryCache(5000);

    async function scanDirectory(dirHandle, options) {
        options = options || {};
        const filterFn = options.filterFn || function() { return true; };
        const maxDepth = options.maxDepth || 10;
        const includeDirs = options.includeDirs || false;
        const cacheKey = options.cacheKey || null;

        if (cacheKey) {
            const cached = dirCache.get(dirHandle, cacheKey);
            if (cached) return cached;
        }

        const results = [];

        async function scan(handle, path, depth) {
            if (depth > maxDepth) return;
            for await (const entry of handle.values()) {
                const entryPath = path ? PathUtils.join(path, entry.name) : entry.name;
                if (entry.kind === 'file') {
                    if (filterFn(entry.name, entryPath, 'file')) {
                        results.push({ handle: entry, path: entryPath, name: entry.name, kind: 'file' });
                    }
                } else if (entry.kind === 'directory') {
                    if (includeDirs && filterFn(entry.name, entryPath, 'directory')) {
                        results.push({ handle: entry, path: entryPath, name: entry.name, kind: 'directory' });
                    }
                    await scan(entry, entryPath, depth + 1);
                }
            }
        }

        await scan(dirHandle, '', 1);

        if (cacheKey) {
            dirCache.set(dirHandle, cacheKey, results);
        }

        return results;
    }

    // 暴露到全局
    global.PsyClawFS = {
        ALLOWED_ORIGIN,
        safePostMessage,
        FileErrorTypes,
        handleFileError,
        MAX_FILE_SIZE,
        PathUtils,
        DirectoryCache,
        dirCache,
        scanDirectory
    };

})(window);
