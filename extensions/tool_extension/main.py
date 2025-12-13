"""
工具产品类型扩展示例
支持在线工具、计算器等实用应用
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.product_extension_service import (
    ProductTypeExtension, ExtensionMetadata, ProductTypeDefinition, 
    ExtensionType, ProductRenderer
)
from typing import Dict, List


class ToolExtension(ProductTypeExtension):
    """工具产品类型扩展"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="tool_extension",
            version="1.0.0",
            description="支持在线工具、计算器等实用应用",
            author="Tool Extension Team",
            extension_type=ExtensionType.PRODUCT_TYPE,
            dependencies=[],
            config_schema={
                "type": "object",
                "properties": {
                    "enable_fullscreen": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否启用全屏功能"
                    },
                    "enable_responsive": {
                        "type": "boolean", 
                        "default": True,
                        "description": "是否启用响应式设计"
                    },
                    "auto_save_state": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否自动保存状态"
                    },
                    "theme": {
                        "type": "string",
                        "enum": ["light", "dark", "auto"],
                        "default": "light",
                        "description": "主题模式"
                    }
                }
            }
        )
    
    def get_product_type_definition(self) -> ProductTypeDefinition:
        return ProductTypeDefinition(
            type_name="tool",
            display_name="在线工具",
            description="支持计算器、编辑器、转换器等在线实用工具",
            file_extensions=[
                ".html", ".htm", ".js", ".css", ".json",
                ".png", ".jpg", ".jpeg", ".gif", ".svg",
                ".woff", ".woff2", ".ttf", ".eot",  # 字体文件
                ".xml", ".csv", ".txt", ".md"       # 数据文件
            ],
            entry_files=["index.html", "tool.html", "app.html", "main.html"],
            config_schema={
                "type": "object",
                "properties": {
                    "tool_type": {
                        "type": "string",
                        "enum": ["calculator", "editor", "converter", "generator", "analyzer", "other"],
                        "description": "工具类型"
                    },
                    "features": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "工具功能列表"
                    },
                    "ui_config": {
                        "type": "object",
                        "properties": {
                            "layout": {"type": "string", "enum": ["single", "split", "tabs"], "default": "single"},
                            "toolbar": {"type": "boolean", "default": True},
                            "sidebar": {"type": "boolean", "default": False},
                            "footer": {"type": "boolean", "default": True}
                        }
                    },
                    "data_config": {
                        "type": "object",
                        "properties": {
                            "auto_save": {"type": "boolean", "default": True},
                            "export_formats": {"type": "array", "items": {"type": "string"}},
                            "import_formats": {"type": "array", "items": {"type": "string"}}
                        }
                    },
                    "performance": {
                        "type": "object",
                        "properties": {
                            "max_memory": {"type": "string", "default": "128MB"},
                            "cache_enabled": {"type": "boolean", "default": True},
                            "lazy_loading": {"type": "boolean", "default": True}
                        }
                    }
                }
            },
            renderer_class="tool_renderer"
        )
    
    def validate_product_files(self, files: Dict[str, bytes]) -> tuple[bool, str]:
        """验证工具文件"""
        # 检查入口文件
        entry_files = ["index.html", "tool.html", "app.html", "main.html"]
        has_entry = any(f in files for f in entry_files)
        if not has_entry:
            return False, f"工具应用必须包含以下入口文件之一: {', '.join(entry_files)}"
        
        # 检查是否包含工具相关的HTML结构
        has_tool_structure = False
        
        for filename, content in files.items():
            if filename.endswith(('.html', '.htm')):
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    # 检查常见的工具应用标识
                    tool_indicators = [
                        'calculator', 'tool', 'input', 'button', 'form',
                        'textarea', 'select', 'canvas', 'editor'
                    ]
                    if any(indicator in text_content.lower() for indicator in tool_indicators):
                        has_tool_structure = True
                        break
                except:
                    pass
        
        if not has_tool_structure:
            return False, "工具应用应该包含交互式界面元素（如输入框、按钮等）"
        
        # 检查文件大小限制（工具应用通常比较小）
        total_size = sum(len(content) for content in files.values())
        if total_size > 50 * 1024 * 1024:  # 50MB
            return False, "工具应用文件总大小不应超过50MB"
        
        return True, ""
    
    def process_product_files(self, files: Dict[str, bytes]) -> Dict[str, bytes]:
        """处理工具文件"""
        processed_files = files.copy()
        
        # 为工具添加状态管理脚本
        state_script = '''
// 工具状态管理脚本
(function() {
    const STORAGE_KEY = 'tool_state_' + window.location.pathname;
    
    // 状态管理对象
    window.ToolStateManager = {
        // 保存状态
        saveState: function(data) {
            try {
                localStorage.setItem(STORAGE_KEY, JSON.stringify({
                    data: data,
                    timestamp: Date.now(),
                    version: '1.0'
                }));
                
                // 通知父窗口状态已保存
                if (window.parent !== window) {
                    window.parent.postMessage({
                        type: 'tool_state_saved',
                        timestamp: Date.now()
                    }, '*');
                }
            } catch (e) {
                console.warn('保存状态失败:', e);
            }
        },
        
        // 加载状态
        loadState: function() {
            try {
                const saved = localStorage.getItem(STORAGE_KEY);
                if (saved) {
                    const parsed = JSON.parse(saved);
                    return parsed.data;
                }
            } catch (e) {
                console.warn('加载状态失败:', e);
            }
            return null;
        },
        
        // 清除状态
        clearState: function() {
            try {
                localStorage.removeItem(STORAGE_KEY);
            } catch (e) {
                console.warn('清除状态失败:', e);
            }
        },
        
        // 导出数据
        exportData: function(data, filename, format = 'json') {
            try {
                let content, mimeType;
                
                switch (format.toLowerCase()) {
                    case 'json':
                        content = JSON.stringify(data, null, 2);
                        mimeType = 'application/json';
                        break;
                    case 'csv':
                        content = this.convertToCSV(data);
                        mimeType = 'text/csv';
                        break;
                    case 'txt':
                        content = typeof data === 'string' ? data : JSON.stringify(data, null, 2);
                        mimeType = 'text/plain';
                        break;
                    default:
                        throw new Error('不支持的导出格式: ' + format);
                }
                
                const blob = new Blob([content], { type: mimeType });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename + '.' + format;
                document.body.appendChild(a);
                a.click();
                document.body.removeChild(a);
                URL.revokeObjectURL(url);
                
                // 通知父窗口数据已导出
                if (window.parent !== window) {
                    window.parent.postMessage({
                        type: 'tool_data_exported',
                        filename: filename + '.' + format,
                        format: format
                    }, '*');
                }
            } catch (e) {
                console.error('导出数据失败:', e);
                alert('导出失败: ' + e.message);
            }
        },
        
        // 转换为CSV格式
        convertToCSV: function(data) {
            if (Array.isArray(data)) {
                if (data.length === 0) return '';
                
                const headers = Object.keys(data[0]);
                const csvRows = [headers.join(',')];
                
                for (const row of data) {
                    const values = headers.map(header => {
                        const value = row[header];
                        return typeof value === 'string' && value.includes(',') 
                            ? `"${value}"` 
                            : value;
                    });
                    csvRows.push(values.join(','));
                }
                
                return csvRows.join('\\n');
            } else if (typeof data === 'object') {
                const entries = Object.entries(data);
                return entries.map(([key, value]) => `${key},${value}`).join('\\n');
            } else {
                return String(data);
            }
        }
    };
    
    // 监听页面卸载事件，自动保存状态
    window.addEventListener('beforeunload', function() {
        if (window.ToolApp && typeof window.ToolApp.getCurrentState === 'function') {
            const state = window.ToolApp.getCurrentState();
            if (state) {
                window.ToolStateManager.saveState(state);
            }
        }
    });
    
    // 监听来自父窗口的消息
    window.addEventListener('message', function(event) {
        if (event.data.type === 'tool_export_request') {
            if (window.ToolApp && typeof window.ToolApp.getCurrentData === 'function') {
                const data = window.ToolApp.getCurrentData();
                const filename = event.data.filename || 'tool_data';
                const format = event.data.format || 'json';
                window.ToolStateManager.exportData(data, filename, format);
            }
        } else if (event.data.type === 'tool_clear_state') {
            window.ToolStateManager.clearState();
            if (window.ToolApp && typeof window.ToolApp.resetState === 'function') {
                window.ToolApp.resetState();
            }
        }
    });
    
    // 页面加载完成后尝试恢复状态
    document.addEventListener('DOMContentLoaded', function() {
        setTimeout(function() {
            const savedState = window.ToolStateManager.loadState();
            if (savedState && window.ToolApp && typeof window.ToolApp.restoreState === 'function') {
                window.ToolApp.restoreState(savedState);
            }
        }, 100);
    });
})();
'''
        
        processed_files['_tool_state.js'] = state_script.encode('utf-8')
        
        # 修改HTML文件以包含状态管理脚本
        for filename in list(processed_files.keys()):
            if filename.endswith('.html'):
                try:
                    html_content = processed_files[filename].decode('utf-8')
                    
                    # 在</head>前插入状态管理脚本
                    if '</head>' in html_content:
                        script_tag = '<script src="_tool_state.js"></script>\n</head>'
                        html_content = html_content.replace('</head>', script_tag)
                        processed_files[filename] = html_content.encode('utf-8')
                except:
                    pass
        
        return processed_files
    
    def get_launch_config(self, product_config: Dict[str, any]) -> Dict[str, any]:
        """获取工具启动配置"""
        config = {
            "sandbox_permissions": [
                "allow-scripts",
                "allow-same-origin",
                "allow-forms",
                "allow-downloads"  # 工具可能需要下载功能
            ],
            "performance_monitoring": False,  # 工具通常不需要性能监控
            "auto_save_state": True,          # 自动保存状态
            "memory_limit": "128MB"           # 较小的内存限制
        }
        
        # 根据产品配置调整
        tool_config = product_config.get("performance", {})
        if tool_config.get("max_memory"):
            config["memory_limit"] = tool_config["max_memory"]
        
        return config


class ToolRenderer(ProductRenderer):
    """工具渲染器"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="tool_renderer",
            version="1.0.0",
            description="工具产品渲染器",
            author="Tool Extension Team",
            extension_type=ExtensionType.RENDERER,
            dependencies=["tool_extension"],
            config_schema={}
        )
    
    def render_product(self, product_id: int, config: Dict[str, any]) -> str:
        """渲染工具产品"""
        # 获取工具配置
        tool_config = config.get("tool_config", {})
        ui_config = tool_config.get("ui_config", {})
        data_config = tool_config.get("data_config", {})
        
        # 构建工具容器HTML
        html = f'''
        <div class="tool-container" id="tool-container-{product_id}">
            <div class="tool-header">
                <div class="tool-title">
                    <h3 id="tool-title">在线工具</h3>
                </div>
                <div class="tool-controls">
                    <button id="save-btn" class="tool-btn" title="保存状态">
                        <i class="fas fa-save"></i>
                    </button>
                    <button id="export-btn" class="tool-btn" title="导出数据">
                        <i class="fas fa-download"></i>
                    </button>
                    <button id="clear-btn" class="tool-btn" title="清除数据">
                        <i class="fas fa-trash"></i>
                    </button>
                    <button id="fullscreen-btn" class="tool-btn" title="全屏">
                        <i class="fas fa-expand"></i>
                    </button>
                </div>
            </div>
            
            <div class="tool-iframe-container">
                <iframe 
                    id="tool-iframe-{product_id}"
                    src="/products/{product_id}/index.html"
                    frameborder="0"
                    allowfullscreen
                    sandbox="allow-scripts allow-same-origin allow-forms allow-downloads">
                </iframe>
            </div>
            
            <div class="tool-footer">
                <div class="tool-status">
                    <span id="status-text">就绪</span>
                </div>
                <div class="tool-info">
                    <span id="last-saved">未保存</span>
                </div>
            </div>
        </div>
        
        <style>
        .tool-container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #f8f9fa;
            border-radius: 8px;
            overflow: hidden;
        }}
        
        .tool-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: white;
            border-bottom: 1px solid #e0e0e0;
        }}
        
        .tool-title h3 {{
            margin: 0;
            color: #333;
            font-size: 16px;
        }}
        
        .tool-controls {{
            display: flex;
            gap: 8px;
        }}
        
        .tool-btn {{
            background: #f8f9fa;
            border: 1px solid #e0e0e0;
            color: #666;
            padding: 8px 10px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
        }}
        
        .tool-btn:hover {{
            background: #e9ecef;
            color: #333;
        }}
        
        .tool-btn:active {{
            background: #dee2e6;
        }}
        
        .tool-iframe-container {{
            flex: 1;
            position: relative;
            background: white;
        }}
        
        .tool-iframe-container iframe {{
            width: 100%;
            height: 100%;
        }}
        
        .tool-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px;
            background: white;
            border-top: 1px solid #e0e0e0;
            font-size: 12px;
            color: #666;
        }}
        
        .tool-status {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        .tool-info {{
            display: flex;
            align-items: center;
            gap: 8px;
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .tool-header {{
                padding: 8px 12px;
            }}
            
            .tool-title h3 {{
                font-size: 14px;
            }}
            
            .tool-btn {{
                padding: 6px 8px;
                font-size: 12px;
            }}
            
            .tool-footer {{
                padding: 6px 12px;
                font-size: 11px;
            }}
        }}
        </style>
        
        <script>
        (function() {{
            const toolContainer = document.getElementById('tool-container-{product_id}');
            const toolIframe = document.getElementById('tool-iframe-{product_id}');
            const saveBtn = document.getElementById('save-btn');
            const exportBtn = document.getElementById('export-btn');
            const clearBtn = document.getElementById('clear-btn');
            const fullscreenBtn = document.getElementById('fullscreen-btn');
            const statusText = document.getElementById('status-text');
            const lastSavedText = document.getElementById('last-saved');
            const toolTitle = document.getElementById('tool-title');
            
            // 工具加载完成处理
            toolIframe.addEventListener('load', function() {{
                statusText.textContent = '已加载';
                
                // 尝试获取工具标题
                try {{
                    const iframeDoc = toolIframe.contentDocument || toolIframe.contentWindow.document;
                    const title = iframeDoc.title || iframeDoc.querySelector('h1, h2, h3')?.textContent;
                    if (title) {{
                        toolTitle.textContent = title;
                    }}
                }} catch (e) {{
                    // 跨域限制，忽略错误
                }}
            }});
            
            // 保存状态
            saveBtn.addEventListener('click', function() {{
                toolIframe.contentWindow.postMessage({{
                    type: 'tool_save_request'
                }}, '*');
                statusText.textContent = '保存中...';
            }});
            
            // 导出数据
            exportBtn.addEventListener('click', function() {{
                const filename = prompt('请输入文件名:', 'tool_data');
                if (filename) {{
                    const format = prompt('请选择格式 (json/csv/txt):', 'json');
                    if (format && ['json', 'csv', 'txt'].includes(format.toLowerCase())) {{
                        toolIframe.contentWindow.postMessage({{
                            type: 'tool_export_request',
                            filename: filename,
                            format: format.toLowerCase()
                        }}, '*');
                        statusText.textContent = '导出中...';
                    }}
                }}
            }});
            
            // 清除数据
            clearBtn.addEventListener('click', function() {{
                if (confirm('确定要清除所有数据吗？此操作不可撤销。')) {{
                    toolIframe.contentWindow.postMessage({{
                        type: 'tool_clear_state'
                    }}, '*');
                    statusText.textContent = '已清除';
                    lastSavedText.textContent = '未保存';
                }}
            }});
            
            // 全屏功能
            fullscreenBtn.addEventListener('click', function() {{
                if (document.fullscreenElement) {{
                    document.exitFullscreen();
                }} else {{
                    toolContainer.requestFullscreen();
                }}
            }});
            
            // 监听来自工具的消息
            window.addEventListener('message', function(event) {{
                if (event.source !== toolIframe.contentWindow) return;
                
                const data = event.data;
                
                if (data.type === 'tool_state_saved') {{
                    statusText.textContent = '已保存';
                    lastSavedText.textContent = '刚刚保存';
                    setTimeout(() => {{
                        statusText.textContent = '就绪';
                    }}, 2000);
                }} else if (data.type === 'tool_data_exported') {{
                    statusText.textContent = '导出完成';
                    setTimeout(() => {{
                        statusText.textContent = '就绪';
                    }}, 2000);
                }} else if (data.type === 'tool_status_update') {{
                    statusText.textContent = data.status || '就绪';
                }}
            }});
            
            // 全屏状态变化
            document.addEventListener('fullscreenchange', function() {{
                const icon = fullscreenBtn.querySelector('i');
                if (document.fullscreenElement) {{
                    icon.className = 'fas fa-compress';
                    fullscreenBtn.title = '退出全屏';
                }} else {{
                    icon.className = 'fas fa-expand';
                    fullscreenBtn.title = '全屏';
                }}
            }});
        }})();
        </script>
        '''
        
        return html
    
    def get_required_assets(self) -> List[str]:
        """获取所需资源"""
        return [
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ]