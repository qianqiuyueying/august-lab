"""
单页应用(SPA)产品类型扩展
支持React、Vue、Angular等SPA框架
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.product_extension_service import (
    ProductTypeExtension, ExtensionMetadata, ProductTypeDefinition, 
    ExtensionType, ProductRenderer
)
from typing import Dict, List
import re
import json


class SPAExtension(ProductTypeExtension):
    """单页应用产品类型扩展"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="spa_extension",
            version="1.0.0",
            description="支持React、Vue、Angular等单页应用框架",
            author="SPA Extension Team",
            extension_type=ExtensionType.PRODUCT_TYPE,
            dependencies=[],
            config_schema={
                "type": "object",
                "properties": {
                    "enable_router": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用路由支持"
                    },
                    "enable_dev_tools": {
                        "type": "boolean", 
                        "default": False,
                        "description": "是否启用开发工具"
                    },
                    "enable_hot_reload": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否启用热重载"
                    },
                    "framework": {
                        "type": "string",
                        "enum": ["auto", "react", "vue", "angular", "svelte", "other"],
                        "default": "auto",
                        "description": "SPA框架类型"
                    }
                }
            }
        )
    
    def get_product_type_definition(self) -> ProductTypeDefinition:
        return ProductTypeDefinition(
            type_name="spa",
            display_name="单页应用",
            description="支持React、Vue、Angular等现代前端框架的单页应用",
            file_extensions=[
                ".html", ".htm", ".js", ".jsx", ".ts", ".tsx", ".vue",
                ".css", ".scss", ".sass", ".less", ".json", ".map",
                ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
                ".woff", ".woff2", ".ttf", ".eot", ".otf",
                ".xml", ".txt", ".md", ".yaml", ".yml"
            ],
            entry_files=["index.html"],
            config_schema={
                "type": "object",
                "properties": {
                    "framework": {
                        "type": "string",
                        "enum": ["react", "vue", "angular", "svelte", "preact", "lit", "other"],
                        "description": "使用的前端框架"
                    },
                    "build_tool": {
                        "type": "string",
                        "enum": ["webpack", "vite", "parcel", "rollup", "esbuild", "other"],
                        "description": "构建工具"
                    },
                    "router": {
                        "type": "object",
                        "properties": {
                            "mode": {"type": "string", "enum": ["hash", "history", "memory"], "default": "hash"},
                            "base_url": {"type": "string", "default": "/"},
                            "scroll_behavior": {"type": "string", "enum": ["auto", "top", "smooth"], "default": "auto"}
                        }
                    },
                    "state_management": {
                        "type": "object",
                        "properties": {
                            "library": {"type": "string", "enum": ["redux", "vuex", "pinia", "mobx", "zustand", "none"]},
                            "persist": {"type": "boolean", "default": false},
                            "dev_tools": {"type": "boolean", "default": false}
                        }
                    },
                    "features": {
                        "type": "object",
                        "properties": {
                            "pwa": {"type": "boolean", "default": false},
                            "ssr": {"type": "boolean", "default": false},
                            "code_splitting": {"type": "boolean", "default": true},
                            "lazy_loading": {"type": "boolean", "default": true},
                            "hot_reload": {"type": "boolean", "default": false}
                        }
                    },
                    "optimization": {
                        "type": "object",
                        "properties": {
                            "bundle_analyzer": {"type": "boolean", "default": false},
                            "tree_shaking": {"type": "boolean", "default": true},
                            "minification": {"type": "boolean", "default": true},
                            "compression": {"type": "boolean", "default": true}
                        }
                    }
                }
            },
            renderer_class="spa_renderer"
        )
    
    def validate_product_files(self, files: Dict[str, bytes]) -> tuple[bool, str]:
        """验证SPA应用文件"""
        # 检查必需的index.html文件
        if "index.html" not in files:
            return False, "SPA应用必须包含index.html文件"
        
        # 检查HTML文件结构
        try:
            html_content = files["index.html"].decode('utf-8', errors='ignore')
            
            # 检查基本HTML结构
            if not re.search(r'<html[^>]*>', html_content, re.IGNORECASE):
                return False, "index.html 缺少 <html> 标签"
            
            if not re.search(r'<head[^>]*>.*</head>', html_content, re.IGNORECASE | re.DOTALL):
                return False, "index.html 缺少 <head> 部分"
            
            if not re.search(r'<body[^>]*>.*</body>', html_content, re.IGNORECASE | re.DOTALL):
                return False, "index.html 缺少 <body> 部分"
            
            # 检查是否有SPA应用的根元素
            if not re.search(r'<div[^>]*id=["\'](?:root|app|main)["\']', html_content, re.IGNORECASE):
                return False, "index.html 应该包含SPA应用的根元素（如 <div id=\"root\">）"
            
        except Exception as e:
            return False, f"解析index.html失败: {str(e)}"
        
        # 检测框架类型
        framework = self._detect_framework(files)
        if not framework:
            return False, "无法检测到支持的SPA框架"
        
        # 检查JavaScript文件
        js_files = [f for f in files.keys() if f.endswith(('.js', '.jsx', '.ts', '.tsx'))]
        if not js_files:
            return False, "SPA应用必须包含JavaScript文件"
        
        # 检查是否有构建产物的特征
        has_bundle = any('bundle' in f.lower() or 'chunk' in f.lower() or 'vendor' in f.lower() 
                        for f in js_files)
        has_main = any(f in ['main.js', 'app.js', 'index.js'] for f in js_files)
        
        if not has_bundle and not has_main:
            return False, "SPA应用应该包含主要的JavaScript入口文件或构建产物"
        
        # 检查文件大小限制
        total_size = sum(len(content) for content in files.values())
        if total_size > 200 * 1024 * 1024:  # 200MB
            return False, "SPA应用文件总大小不应超过200MB"
        
        # 检查资源引用
        try:
            # 检查JavaScript文件引用
            js_refs = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
            for js_ref in js_refs:
                if not js_ref.startswith(('http://', 'https://', '//', 'data:')):
                    js_path = js_ref.lstrip('./')
                    if js_path not in files:
                        return False, f"index.html 引用的JavaScript文件不存在: {js_ref}"
            
            # 检查CSS文件引用
            css_refs = re.findall(r'<link[^>]*href=["\']([^"\']+\.css)["\']', html_content, re.IGNORECASE)
            for css_ref in css_refs:
                if not css_ref.startswith(('http://', 'https://', '//', 'data:')):
                    css_path = css_ref.lstrip('./')
                    if css_path not in files:
                        return False, f"index.html 引用的CSS文件不存在: {css_ref}"
                        
        except Exception as e:
            return False, f"验证资源引用失败: {str(e)}"
        
        return True, ""
    
    def _detect_framework(self, files: Dict[str, bytes]) -> str:
        """检测SPA框架类型"""
        # 检查package.json
        if "package.json" in files:
            try:
                package_content = files["package.json"].decode('utf-8')
                package_data = json.loads(package_content)
                dependencies = {**package_data.get("dependencies", {}), 
                              **package_data.get("devDependencies", {})}
                
                if "react" in dependencies or "react-dom" in dependencies:
                    return "react"
                elif "vue" in dependencies or "@vue/core" in dependencies:
                    return "vue"
                elif "@angular/core" in dependencies:
                    return "angular"
                elif "svelte" in dependencies:
                    return "svelte"
                elif "preact" in dependencies:
                    return "preact"
                elif "lit" in dependencies:
                    return "lit"
            except:
                pass
        
        # 检查文件扩展名
        file_extensions = set(f.split('.')[-1].lower() for f in files.keys() if '.' in f)
        
        if "jsx" in file_extensions or "tsx" in file_extensions:
            return "react"
        elif "vue" in file_extensions:
            return "vue"
        elif "ts" in file_extensions and any("angular" in f.lower() for f in files.keys()):
            return "angular"
        
        # 检查文件内容
        for filename, content in files.items():
            if filename.endswith(('.js', '.jsx', '.ts', '.tsx')):
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    
                    if re.search(r'import\s+React|from\s+["\']react["\']', text_content):
                        return "react"
                    elif re.search(r'import\s+Vue|from\s+["\']vue["\']', text_content):
                        return "vue"
                    elif re.search(r'@Component|@Injectable|@NgModule', text_content):
                        return "angular"
                    elif re.search(r'import\s+.*from\s+["\']svelte', text_content):
                        return "svelte"
                except:
                    pass
        
        return "other"
    
    def process_product_files(self, files: Dict[str, bytes]) -> Dict[str, bytes]:
        """处理SPA应用文件"""
        processed_files = files.copy()
        
        # 检测框架类型
        framework = self._detect_framework(files)
        
        # 为SPA应用添加增强功能脚本
        spa_script = f'''
// SPA应用增强功能脚本
(function() {{
    const FRAMEWORK = '{framework}';
    
    // 路由监听
    function initRouterMonitoring() {{
        let currentPath = window.location.pathname + window.location.hash;
        
        // 监听路由变化
        function onRouteChange() {{
            const newPath = window.location.pathname + window.location.hash;
            if (newPath !== currentPath) {{
                currentPath = newPath;
                
                // 通知父窗口路由变化
                if (window.parent !== window) {{
                    window.parent.postMessage({{
                        type: 'spa_route_change',
                        path: newPath,
                        framework: FRAMEWORK
                    }}, '*');
                }}
            }}
        }}
        
        // 监听popstate事件（浏览器前进后退）
        window.addEventListener('popstate', onRouteChange);
        
        // 监听hashchange事件（hash路由）
        window.addEventListener('hashchange', onRouteChange);
        
        // 拦截pushState和replaceState
        const originalPushState = history.pushState;
        const originalReplaceState = history.replaceState;
        
        history.pushState = function(...args) {{
            originalPushState.apply(history, args);
            setTimeout(onRouteChange, 0);
        }};
        
        history.replaceState = function(...args) {{
            originalReplaceState.apply(history, args);
            setTimeout(onRouteChange, 0);
        }};
    }}
    
    // 状态管理监听
    function initStateMonitoring() {{
        // Redux DevTools支持
        if (window.__REDUX_DEVTOOLS_EXTENSION__) {{
            console.log('Redux DevTools detected');
        }}
        
        // Vue DevTools支持
        if (window.__VUE_DEVTOOLS_GLOBAL_HOOK__) {{
            console.log('Vue DevTools detected');
        }}
        
        // 监听全局错误
        window.addEventListener('error', function(e) {{
            if (window.parent !== window) {{
                window.parent.postMessage({{
                    type: 'spa_error',
                    framework: FRAMEWORK,
                    message: e.message,
                    filename: e.filename,
                    lineno: e.lineno,
                    colno: e.colno,
                    stack: e.error ? e.error.stack : null
                }}, '*');
            }}
        }});
        
        // 监听Promise rejection
        window.addEventListener('unhandledrejection', function(e) {{
            if (window.parent !== window) {{
                window.parent.postMessage({{
                    type: 'spa_promise_rejection',
                    framework: FRAMEWORK,
                    reason: e.reason,
                    stack: e.reason && e.reason.stack ? e.reason.stack : null
                }}, '*');
            }}
        }});
    }}
    
    // 性能监控
    function initPerformanceMonitoring() {{
        if ('performance' in window) {{
            // 监听导航性能
            window.addEventListener('load', function() {{
                setTimeout(function() {{
                    const perfData = performance.getEntriesByType('navigation')[0];
                    const paintEntries = performance.getEntriesByType('paint');
                    
                    const performanceInfo = {{
                        framework: FRAMEWORK,
                        loadTime: perfData.loadEventEnd - perfData.loadEventStart,
                        domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                        firstPaint: paintEntries.find(entry => entry.name === 'first-paint')?.startTime || 0,
                        firstContentfulPaint: paintEntries.find(entry => entry.name === 'first-contentful-paint')?.startTime || 0,
                        resources: performance.getEntriesByType('resource').length
                    }};
                    
                    if (window.parent !== window) {{
                        window.parent.postMessage({{
                            type: 'spa_performance',
                            data: performanceInfo
                        }}, '*');
                    }}
                }}, 1000);
            }});
            
            // 监听资源加载
            const observer = new PerformanceObserver((list) => {{
                for (const entry of list.getEntries()) {{
                    if (entry.entryType === 'resource' && entry.duration > 1000) {{
                        // 慢资源警告
                        if (window.parent !== window) {{
                            window.parent.postMessage({{
                                type: 'spa_slow_resource',
                                framework: FRAMEWORK,
                                resource: entry.name,
                                duration: entry.duration
                            }}, '*');
                        }}
                    }}
                }}
            }});
            
            try {{
                observer.observe({{entryTypes: ['resource']}});
            }} catch (e) {{
                // 某些浏览器可能不支持
            }}
        }}
    }}
    
    // 热重载支持
    function initHotReload() {{
        if (window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1') {{
            // 开发环境下的热重载检测
            let lastModified = Date.now();
            
            setInterval(function() {{
                fetch(window.location.href, {{method: 'HEAD'}})
                    .then(response => {{
                        const modified = new Date(response.headers.get('last-modified')).getTime();
                        if (modified > lastModified) {{
                            lastModified = modified;
                            if (window.parent !== window) {{
                                window.parent.postMessage({{
                                    type: 'spa_hot_reload',
                                    framework: FRAMEWORK
                                }}, '*');
                            }}
                        }}
                    }})
                    .catch(() => {{
                        // 忽略错误
                    }});
            }}, 5000);
        }}
    }}
    
    // 框架特定的增强
    function initFrameworkSpecific() {{
        switch (FRAMEWORK) {{
            case 'react':
                // React特定增强
                if (window.React) {{
                    console.log('React应用已加载');
                    
                    // 检测React版本
                    if (window.React.version) {{
                        if (window.parent !== window) {{
                            window.parent.postMessage({{
                                type: 'spa_framework_info',
                                framework: 'react',
                                version: window.React.version
                            }}, '*');
                        }}
                    }}
                }}
                break;
                
            case 'vue':
                // Vue特定增强
                if (window.Vue) {{
                    console.log('Vue应用已加载');
                    
                    // 检测Vue版本
                    if (window.Vue.version) {{
                        if (window.parent !== window) {{
                            window.parent.postMessage({{
                                type: 'spa_framework_info',
                                framework: 'vue',
                                version: window.Vue.version
                            }}, '*');
                        }}
                    }}
                }}
                break;
                
            case 'angular':
                // Angular特定增强
                if (window.ng) {{
                    console.log('Angular应用已加载');
                    
                    if (window.parent !== window) {{
                        window.parent.postMessage({{
                            type: 'spa_framework_info',
                            framework: 'angular',
                            version: 'detected'
                        }}, '*');
                    }}
                }}
                break;
        }}
    }}
    
    // 初始化所有功能
    document.addEventListener('DOMContentLoaded', function() {{
        initRouterMonitoring();
        initStateMonitoring();
        initPerformanceMonitoring();
        initHotReload();
        
        // 延迟执行框架特定初始化
        setTimeout(initFrameworkSpecific, 1000);
        
        // 通知父窗口SPA已准备就绪
        if (window.parent !== window) {{
            window.parent.postMessage({{
                type: 'spa_ready',
                framework: FRAMEWORK,
                title: document.title,
                url: window.location.href
            }}, '*');
        }}
    }});
    
    // 监听来自父窗口的消息
    window.addEventListener('message', function(event) {{
        const data = event.data;
        
        if (data.type === 'spa_navigate') {{
            // 程序化导航
            if (data.path) {{
                if (window.history && window.history.pushState) {{
                    window.history.pushState(null, '', data.path);
                    
                    // 触发路由变化事件
                    window.dispatchEvent(new PopStateEvent('popstate'));
                }} else {{
                    window.location.hash = data.path;
                }}
            }}
        }} else if (data.type === 'spa_reload') {{
            // 重新加载应用
            window.location.reload();
        }}
    }});
}})();
'''
        
        processed_files['_spa_enhancements.js'] = spa_script.encode('utf-8')
        
        # 修改HTML文件以包含SPA增强脚本
        if "index.html" in processed_files:
            try:
                html_content = processed_files["index.html"].decode('utf-8')
                
                # 在</body>前插入增强脚本
                if '</body>' in html_content:
                    script_tag = '<script src="_spa_enhancements.js"></script>\n</body>'
                    html_content = html_content.replace('</body>', script_tag)
                    processed_files["index.html"] = html_content.encode('utf-8')
            except:
                pass
        
        return processed_files
    
    def get_launch_config(self, product_config: Dict[str, any]) -> Dict[str, any]:
        """获取SPA应用启动配置"""
        config = {
            "sandbox_permissions": [
                "allow-scripts",
                "allow-same-origin",
                "allow-forms",
                "allow-popups",
                "allow-modals"  # SPA可能需要模态框
            ],
            "performance_monitoring": True,
            "router_support": True,
            "memory_limit": "256MB",  # SPA通常需要更多内存
            "cache_enabled": True
        }
        
        # 根据产品配置调整
        features = product_config.get("features", {})
        if features.get("hot_reload", False):
            config["hot_reload"] = True
            config["memory_limit"] = "512MB"  # 热重载需要更多内存
        
        if features.get("pwa", False):
            config["sandbox_permissions"].extend([
                "allow-downloads",
                "allow-storage-access-by-user-activation"
            ])
        
        router_config = product_config.get("router", {})
        if router_config.get("mode") == "history":
            config["history_api_fallback"] = True
        
        return config


class SPARenderer(ProductRenderer):
    """SPA应用渲染器"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="spa_renderer",
            version="1.0.0",
            description="SPA应用产品渲染器",
            author="SPA Extension Team",
            extension_type=ExtensionType.RENDERER,
            dependencies=["spa_extension"],
            config_schema={}
        )
    
    def render_product(self, product_id: int, config: Dict[str, any]) -> str:
        """渲染SPA应用产品"""
        # 获取SPA配置
        framework = config.get("framework", "unknown")
        router_config = config.get("router", {})
        features = config.get("features", {})
        
        # 构建SPA容器HTML
        html = f'''
        <div class="spa-container" id="spa-container-{product_id}">
            <div class="spa-header">
                <div class="spa-info">
                    <h3 id="spa-title">SPA应用</h3>
                    <span id="spa-framework" class="framework-badge">{framework.title()}</span>
                    <span id="spa-status">加载中...</span>
                </div>
                <div class="spa-controls">
                    <button id="back-btn" class="spa-btn" title="后退" disabled>
                        <i class="fas fa-arrow-left"></i>
                    </button>
                    <button id="forward-btn" class="spa-btn" title="前进" disabled>
                        <i class="fas fa-arrow-right"></i>
                    </button>
                    <button id="refresh-btn" class="spa-btn" title="刷新">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                    <button id="devtools-btn" class="spa-btn" title="开发工具">
                        <i class="fas fa-code"></i>
                    </button>
                    <button id="fullscreen-btn" class="spa-btn" title="全屏">
                        <i class="fas fa-expand"></i>
                    </button>
                </div>
            </div>
            
            <div class="spa-nav-bar">
                <div class="current-route">
                    <i class="fas fa-route"></i>
                    <span id="current-path">/</span>
                </div>
                <div class="spa-metrics">
                    <span id="load-time">--</span>
                    <span id="bundle-size">--</span>
                </div>
            </div>
            
            <div class="spa-iframe-container">
                <iframe 
                    id="spa-iframe-{product_id}"
                    src="/products/{product_id}/index.html"
                    frameborder="0"
                    allowfullscreen
                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups allow-modals">
                </iframe>
            </div>
            
            <div class="spa-footer">
                <div class="performance-info">
                    <span id="fcp-time">FCP: --</span>
                    <span id="resource-count">资源: --</span>
                    <span id="memory-usage">内存: --</span>
                </div>
                <div class="spa-actions">
                    <button id="hot-reload-btn" class="spa-action-btn" title="热重载">
                        <i class="fas fa-fire"></i>
                    </button>
                    <button id="state-inspector-btn" class="spa-action-btn" title="状态检查器">
                        <i class="fas fa-search"></i>
                    </button>
                </div>
            </div>
        </div>
        
        <style>
        .spa-container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }}
        
        .spa-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .spa-info {{
            display: flex;
            align-items: center;
            gap: 12px;
        }}
        
        .spa-info h3 {{
            margin: 0;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .framework-badge {{
            background: rgba(255, 255, 255, 0.2);
            padding: 4px 8px;
            border-radius: 12px;
            font-size: 11px;
            font-weight: 500;
            text-transform: uppercase;
        }}
        
        .spa-info span:last-child {{
            font-size: 12px;
            opacity: 0.8;
        }}
        
        .spa-controls {{
            display: flex;
            gap: 6px;
        }}
        
        .spa-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 8px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
        }}
        
        .spa-btn:hover:not(:disabled) {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }}
        
        .spa-btn:disabled {{
            opacity: 0.5;
            cursor: not-allowed;
        }}
        
        .spa-nav-bar {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px;
            background: #f8f9fa;
            border-bottom: 1px solid #e9ecef;
            font-size: 12px;
        }}
        
        .current-route {{
            display: flex;
            align-items: center;
            gap: 8px;
            color: #495057;
            font-family: monospace;
        }}
        
        .spa-metrics {{
            display: flex;
            gap: 16px;
            color: #6c757d;
        }}
        
        .spa-iframe-container {{
            flex: 1;
            position: relative;
            background: #f8f9fa;
        }}
        
        .spa-iframe-container iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .spa-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            font-size: 11px;
            color: #6c757d;
        }}
        
        .performance-info {{
            display: flex;
            gap: 16px;
        }}
        
        .spa-actions {{
            display: flex;
            gap: 8px;
        }}
        
        .spa-action-btn {{
            background: transparent;
            border: 1px solid #dee2e6;
            color: #6c757d;
            padding: 4px 6px;
            border-radius: 4px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 10px;
        }}
        
        .spa-action-btn:hover {{
            background: #e9ecef;
            color: #495057;
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .spa-header {{
                padding: 8px 12px;
            }}
            
            .spa-info h3 {{
                font-size: 14px;
            }}
            
            .spa-controls {{
                gap: 4px;
            }}
            
            .spa-btn {{
                padding: 6px 8px;
                font-size: 12px;
            }}
            
            .spa-nav-bar {{
                padding: 6px 12px;
                font-size: 11px;
            }}
            
            .spa-metrics {{
                gap: 12px;
            }}
            
            .spa-footer {{
                padding: 6px 12px;
                font-size: 10px;
            }}
            
            .performance-info {{
                gap: 12px;
            }}
        }}
        
        /* 框架特定样式 */
        .framework-badge.react {{
            background: rgba(97, 218, 251, 0.3);
        }}
        
        .framework-badge.vue {{
            background: rgba(79, 192, 141, 0.3);
        }}
        
        .framework-badge.angular {{
            background: rgba(221, 0, 49, 0.3);
        }}
        </style>
        
        <script>
        (function() {{
            const container = document.getElementById('spa-container-{product_id}');
            const iframe = document.getElementById('spa-iframe-{product_id}');
            const spaTitle = document.getElementById('spa-title');
            const spaFramework = document.getElementById('spa-framework');
            const spaStatus = document.getElementById('spa-status');
            const currentPath = document.getElementById('current-path');
            const backBtn = document.getElementById('back-btn');
            const forwardBtn = document.getElementById('forward-btn');
            const refreshBtn = document.getElementById('refresh-btn');
            const devtoolsBtn = document.getElementById('devtools-btn');
            const fullscreenBtn = document.getElementById('fullscreen-btn');
            const hotReloadBtn = document.getElementById('hot-reload-btn');
            const stateInspectorBtn = document.getElementById('state-inspector-btn');
            const loadTimeSpan = document.getElementById('load-time');
            const bundleSizeSpan = document.getElementById('bundle-size');
            const fcpTimeSpan = document.getElementById('fcp-time');
            const resourceCountSpan = document.getElementById('resource-count');
            const memoryUsageSpan = document.getElementById('memory-usage');
            
            let navigationHistory = [];
            let currentHistoryIndex = -1;
            let loadStartTime = Date.now();
            
            // 页面加载完成处理
            iframe.addEventListener('load', function() {{
                spaStatus.textContent = '已加载';
                const loadTime = Date.now() - loadStartTime;
                loadTimeSpan.textContent = `加载: ${{loadTime}}ms`;
            }});
            
            // 后退按钮
            backBtn.addEventListener('click', function() {{
                iframe.contentWindow.postMessage({{
                    type: 'spa_navigate',
                    action: 'back'
                }}, '*');
            }});
            
            // 前进按钮
            forwardBtn.addEventListener('click', function() {{
                iframe.contentWindow.postMessage({{
                    type: 'spa_navigate',
                    action: 'forward'
                }}, '*');
            }});
            
            // 刷新按钮
            refreshBtn.addEventListener('click', function() {{
                loadStartTime = Date.now();
                spaStatus.textContent = '刷新中...';
                iframe.contentWindow.postMessage({{
                    type: 'spa_reload'
                }}, '*');
                
                // 旋转图标
                const icon = refreshBtn.querySelector('i');
                icon.style.transform = 'rotate(360deg)';
                setTimeout(() => {{
                    icon.style.transform = 'rotate(0deg)';
                }}, 500);
            }});
            
            // 开发工具按钮
            devtoolsBtn.addEventListener('click', function() {{
                // 打开开发者工具提示
                alert('请按F12打开浏览器开发者工具来调试SPA应用');
            }});
            
            // 全屏按钮
            fullscreenBtn.addEventListener('click', function() {{
                if (document.fullscreenElement) {{
                    document.exitFullscreen();
                }} else {{
                    container.requestFullscreen();
                }}
            }});
            
            // 热重载按钮
            hotReloadBtn.addEventListener('click', function() {{
                iframe.contentWindow.postMessage({{
                    type: 'spa_hot_reload'
                }}, '*');
                spaStatus.textContent = '热重载中...';
            }});
            
            // 状态检查器按钮
            stateInspectorBtn.addEventListener('click', function() {{
                iframe.contentWindow.postMessage({{
                    type: 'spa_inspect_state'
                }}, '*');
            }});
            
            // 监听来自SPA的消息
            window.addEventListener('message', function(event) {{
                if (event.source !== iframe.contentWindow) return;
                
                const data = event.data;
                
                if (data.type === 'spa_ready') {{
                    spaStatus.textContent = '就绪';
                    if (data.title) {{
                        spaTitle.textContent = data.title;
                    }}
                    if (data.framework) {{
                        spaFramework.textContent = data.framework.toUpperCase();
                        spaFramework.className = `framework-badge ${{data.framework}}`;
                    }}
                }} else if (data.type === 'spa_route_change') {{
                    currentPath.textContent = data.path || '/';
                    
                    // 更新导航历史
                    if (currentHistoryIndex === -1 || navigationHistory[currentHistoryIndex] !== data.path) {{
                        navigationHistory = navigationHistory.slice(0, currentHistoryIndex + 1);
                        navigationHistory.push(data.path);
                        currentHistoryIndex = navigationHistory.length - 1;
                    }}
                    
                    // 更新按钮状态
                    backBtn.disabled = currentHistoryIndex <= 0;
                    forwardBtn.disabled = currentHistoryIndex >= navigationHistory.length - 1;
                    
                }} else if (data.type === 'spa_performance') {{
                    const perfData = data.data;
                    if (perfData.loadTime) {{
                        loadTimeSpan.textContent = `加载: ${{Math.round(perfData.loadTime)}}ms`;
                    }}
                    if (perfData.firstContentfulPaint) {{
                        fcpTimeSpan.textContent = `FCP: ${{Math.round(perfData.firstContentfulPaint)}}ms`;
                    }}
                    if (perfData.resources) {{
                        resourceCountSpan.textContent = `资源: ${{perfData.resources}}个`;
                    }}
                    
                }} else if (data.type === 'spa_framework_info') {{
                    if (data.version) {{
                        spaFramework.title = `${{data.framework}} v${{data.version}}`;
                    }}
                    
                }} else if (data.type === 'spa_error') {{
                    spaStatus.textContent = '错误';
                    spaStatus.style.color = '#dc3545';
                    console.error('SPA错误:', data);
                    
                }} else if (data.type === 'spa_hot_reload') {{
                    spaStatus.textContent = '热重载完成';
                    setTimeout(() => {{
                        spaStatus.textContent = '就绪';
                    }}, 2000);
                    
                }} else if (data.type === 'spa_slow_resource') {{
                    console.warn(`慢资源警告: ${{data.resource}} (${{Math.round(data.duration)}}ms)`);
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
            
            // 内存使用监控
            if ('performance' in window && 'memory' in performance) {{
                setInterval(function() {{
                    const memoryMB = Math.round(performance.memory.usedJSHeapSize / 1024 / 1024);
                    memoryUsageSpan.textContent = `内存: ${{memoryMB}}MB`;
                }}, 5000);
            }}
            
            // 初始化
            loadStartTime = Date.now();
        }})();
        </script>
        '''
        
        return html
    
    def get_required_assets(self) -> List[str]:
        """获取所需资源"""
        return [
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ]