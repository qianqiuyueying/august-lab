"""
静态Web应用产品类型扩展
支持HTML、CSS、JavaScript静态网站
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


class StaticWebExtension(ProductTypeExtension):
    """静态Web应用产品类型扩展"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="static_web_extension",
            version="1.0.0",
            description="支持HTML、CSS、JavaScript静态网站",
            author="Static Web Extension Team",
            extension_type=ExtensionType.PRODUCT_TYPE,
            dependencies=[],
            config_schema={
                "type": "object",
                "properties": {
                    "enable_responsive": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用响应式设计检测"
                    },
                    "enable_seo": {
                        "type": "boolean", 
                        "default": True,
                        "description": "是否启用SEO优化检测"
                    },
                    "enable_pwa": {
                        "type": "boolean",
                        "default": False,
                        "description": "是否启用PWA功能"
                    },
                    "theme": {
                        "type": "string",
                        "enum": ["light", "dark", "auto"],
                        "default": "auto",
                        "description": "主题模式"
                    }
                }
            }
        )
    
    def get_product_type_definition(self) -> ProductTypeDefinition:
        return ProductTypeDefinition(
            type_name="static",
            display_name="静态Web应用",
            description="支持HTML、CSS、JavaScript的静态网站和单页面应用",
            file_extensions=[
                ".html", ".htm", ".css", ".js", ".json", ".txt", ".md",
                ".png", ".jpg", ".jpeg", ".gif", ".svg", ".ico", ".webp",
                ".woff", ".woff2", ".ttf", ".eot", ".otf",  # 字体文件
                ".xml", ".csv", ".pdf", ".map", ".yaml", ".yml",  # 数据文件
                ".mp3", ".wav", ".ogg", ".mp4", ".webm", ".avi"  # 媒体文件
            ],
            entry_files=["index.html", "main.html", "app.html", "home.html"],
            config_schema={
                "type": "object",
                "properties": {
                    "site_config": {
                        "type": "object",
                        "properties": {
                            "title": {"type": "string", "description": "网站标题"},
                            "description": {"type": "string", "description": "网站描述"},
                            "keywords": {"type": "array", "items": {"type": "string"}, "description": "关键词"},
                            "author": {"type": "string", "description": "作者"},
                            "language": {"type": "string", "default": "zh-CN", "description": "语言"}
                        }
                    },
                    "features": {
                        "type": "object",
                        "properties": {
                            "responsive": {"type": "boolean", "default": True},
                            "dark_mode": {"type": "boolean", "default": False},
                            "animations": {"type": "boolean", "default": True},
                            "lazy_loading": {"type": "boolean", "default": False}
                        }
                    },
                    "optimization": {
                        "type": "object",
                        "properties": {
                            "minify_css": {"type": "boolean", "default": False},
                            "minify_js": {"type": "boolean", "default": False},
                            "compress_images": {"type": "boolean", "default": False},
                            "cache_strategy": {"type": "string", "enum": ["none", "basic", "aggressive"], "default": "basic"}
                        }
                    },
                    "seo": {
                        "type": "object",
                        "properties": {
                            "meta_tags": {"type": "boolean", "default": True},
                            "open_graph": {"type": "boolean", "default": False},
                            "twitter_cards": {"type": "boolean", "default": False},
                            "structured_data": {"type": "boolean", "default": False}
                        }
                    }
                }
            },
            renderer_class="static_web_renderer"
        )
    
    def validate_product_files(self, files: Dict[str, bytes]) -> tuple[bool, str]:
        """验证静态Web应用文件"""
        # 检查入口文件
        entry_files = ["index.html", "main.html", "app.html", "home.html"]
        has_entry = any(f in files for f in entry_files)
        if not has_entry:
            return False, f"静态Web应用必须包含以下入口文件之一: {', '.join(entry_files)}"
        
        # 检查HTML文件的基本结构
        html_files = [f for f in files.keys() if f.endswith(('.html', '.htm'))]
        if not html_files:
            return False, "静态Web应用必须包含至少一个HTML文件"
        
        # 验证主要HTML文件的结构
        main_html_file = None
        for entry in entry_files:
            if entry in files:
                main_html_file = entry
                break
        
        if main_html_file:
            try:
                html_content = files[main_html_file].decode('utf-8', errors='ignore')
                
                # 检查基本HTML结构
                if not re.search(r'<html[^>]*>', html_content, re.IGNORECASE):
                    return False, f"{main_html_file} 缺少 <html> 标签"
                
                if not re.search(r'<head[^>]*>.*</head>', html_content, re.IGNORECASE | re.DOTALL):
                    return False, f"{main_html_file} 缺少 <head> 部分"
                
                if not re.search(r'<body[^>]*>.*</body>', html_content, re.IGNORECASE | re.DOTALL):
                    return False, f"{main_html_file} 缺少 <body> 部分"
                
                # 检查是否有标题
                if not re.search(r'<title[^>]*>.*</title>', html_content, re.IGNORECASE | re.DOTALL):
                    return False, f"{main_html_file} 缺少 <title> 标签"
                
            except Exception as e:
                return False, f"解析 {main_html_file} 失败: {str(e)}"
        
        # 检查资源文件引用的有效性
        for html_file in html_files:
            try:
                html_content = files[html_file].decode('utf-8', errors='ignore')
                
                # 检查CSS文件引用
                css_refs = re.findall(r'<link[^>]*href=["\']([^"\']+\.css)["\']', html_content, re.IGNORECASE)
                for css_ref in css_refs:
                    if not css_ref.startswith(('http://', 'https://', '//', 'data:')):
                        # 相对路径，检查文件是否存在
                        css_path = css_ref.lstrip('./')
                        if css_path not in files:
                            return False, f"{html_file} 引用的CSS文件不存在: {css_ref}"
                
                # 检查JavaScript文件引用
                js_refs = re.findall(r'<script[^>]*src=["\']([^"\']+\.js)["\']', html_content, re.IGNORECASE)
                for js_ref in js_refs:
                    if not js_ref.startswith(('http://', 'https://', '//', 'data:')):
                        # 相对路径，检查文件是否存在
                        js_path = js_ref.lstrip('./')
                        if js_path not in files:
                            return False, f"{html_file} 引用的JavaScript文件不存在: {js_ref}"
                
                # 检查图片文件引用
                img_refs = re.findall(r'<img[^>]*src=["\']([^"\']+)["\']', html_content, re.IGNORECASE)
                for img_ref in img_refs:
                    if not img_ref.startswith(('http://', 'https://', '//', 'data:')):
                        # 相对路径，检查文件是否存在
                        img_path = img_ref.lstrip('./')
                        if img_path not in files:
                            return False, f"{html_file} 引用的图片文件不存在: {img_ref}"
                
            except Exception as e:
                return False, f"验证 {html_file} 的资源引用失败: {str(e)}"
        
        # 检查文件大小限制
        total_size = sum(len(content) for content in files.values())
        if total_size > 100 * 1024 * 1024:  # 100MB
            return False, "静态Web应用文件总大小不应超过100MB"
        
        return True, ""
    
    def process_product_files(self, files: Dict[str, bytes]) -> Dict[str, bytes]:
        """处理静态Web应用文件"""
        processed_files = files.copy()
        
        # 为静态网站添加增强功能脚本
        enhancement_script = '''
// 静态网站增强功能脚本
(function() {
    // 响应式图片懒加载
    function initLazyLoading() {
        const images = document.querySelectorAll('img[data-src]');
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.removeAttribute('data-src');
                    imageObserver.unobserve(img);
                }
            });
        });
        
        images.forEach(img => imageObserver.observe(img));
    }
    
    // 平滑滚动
    function initSmoothScroll() {
        document.querySelectorAll('a[href^="#"]').forEach(anchor => {
            anchor.addEventListener('click', function (e) {
                e.preventDefault();
                const target = document.querySelector(this.getAttribute('href'));
                if (target) {
                    target.scrollIntoView({
                        behavior: 'smooth',
                        block: 'start'
                    });
                }
            });
        });
    }
    
    // 暗色模式切换
    function initDarkMode() {
        const darkModeToggle = document.querySelector('[data-dark-mode-toggle]');
        if (darkModeToggle) {
            const currentTheme = localStorage.getItem('theme') || 'light';
            document.documentElement.setAttribute('data-theme', currentTheme);
            
            darkModeToggle.addEventListener('click', function() {
                const currentTheme = document.documentElement.getAttribute('data-theme');
                const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
                
                document.documentElement.setAttribute('data-theme', newTheme);
                localStorage.setItem('theme', newTheme);
                
                // 通知父窗口主题变化
                if (window.parent !== window) {
                    window.parent.postMessage({
                        type: 'theme_changed',
                        theme: newTheme
                    }, '*');
                }
            });
        }
    }
    
    // 表单增强
    function initFormEnhancements() {
        const forms = document.querySelectorAll('form');
        forms.forEach(form => {
            // 添加表单验证
            form.addEventListener('submit', function(e) {
                const requiredFields = form.querySelectorAll('[required]');
                let isValid = true;
                
                requiredFields.forEach(field => {
                    if (!field.value.trim()) {
                        field.classList.add('error');
                        isValid = false;
                    } else {
                        field.classList.remove('error');
                    }
                });
                
                if (!isValid) {
                    e.preventDefault();
                    alert('请填写所有必填字段');
                }
            });
            
            // 实时验证
            const inputs = form.querySelectorAll('input, textarea, select');
            inputs.forEach(input => {
                input.addEventListener('blur', function() {
                    if (this.hasAttribute('required') && !this.value.trim()) {
                        this.classList.add('error');
                    } else {
                        this.classList.remove('error');
                    }
                });
            });
        });
    }
    
    // 性能监控
    function initPerformanceMonitoring() {
        if ('performance' in window) {
            window.addEventListener('load', function() {
                setTimeout(function() {
                    const perfData = performance.getEntriesByType('navigation')[0];
                    const loadTime = perfData.loadEventEnd - perfData.loadEventStart;
                    
                    // 发送性能数据到父窗口
                    if (window.parent !== window) {
                        window.parent.postMessage({
                            type: 'performance_data',
                            loadTime: loadTime,
                            domContentLoaded: perfData.domContentLoadedEventEnd - perfData.domContentLoadedEventStart,
                            resources: performance.getEntriesByType('resource').length
                        }, '*');
                    }
                }, 1000);
            });
        }
    }
    
    // 错误监控
    function initErrorMonitoring() {
        window.addEventListener('error', function(e) {
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: 'javascript_error',
                    message: e.message,
                    filename: e.filename,
                    lineno: e.lineno,
                    colno: e.colno
                }, '*');
            }
        });
        
        window.addEventListener('unhandledrejection', function(e) {
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: 'promise_rejection',
                    reason: e.reason
                }, '*');
            }
        });
    }
    
    // 初始化所有功能
    document.addEventListener('DOMContentLoaded', function() {
        initLazyLoading();
        initSmoothScroll();
        initDarkMode();
        initFormEnhancements();
        initPerformanceMonitoring();
        initErrorMonitoring();
        
        // 通知父窗口页面已准备就绪
        if (window.parent !== window) {
            window.parent.postMessage({
                type: 'page_ready',
                title: document.title,
                url: window.location.href
            }, '*');
        }
    });
    
    // 添加基础样式
    const style = document.createElement('style');
    style.textContent = `
        /* 错误状态样式 */
        .error {
            border-color: #dc3545 !important;
            box-shadow: 0 0 0 0.2rem rgba(220, 53, 69, 0.25) !important;
        }
        
        /* 暗色模式样式 */
        [data-theme="dark"] {
            filter: invert(1) hue-rotate(180deg);
        }
        
        [data-theme="dark"] img,
        [data-theme="dark"] video,
        [data-theme="dark"] iframe {
            filter: invert(1) hue-rotate(180deg);
        }
        
        /* 懒加载图片样式 */
        img[data-src] {
            opacity: 0.3;
            transition: opacity 0.3s;
        }
        
        img[data-src].loaded {
            opacity: 1;
        }
    `;
    document.head.appendChild(style);
})();
'''
        
        processed_files['_static_enhancements.js'] = enhancement_script.encode('utf-8')
        
        # 修改HTML文件以包含增强脚本
        for filename in list(processed_files.keys()):
            if filename.endswith('.html'):
                try:
                    html_content = processed_files[filename].decode('utf-8')
                    
                    # 在</body>前插入增强脚本
                    if '</body>' in html_content:
                        script_tag = '<script src="_static_enhancements.js"></script>\n</body>'
                        html_content = html_content.replace('</body>', script_tag)
                        processed_files[filename] = html_content.encode('utf-8')
                except:
                    pass
        
        return processed_files
    
    def get_launch_config(self, product_config: Dict[str, any]) -> Dict[str, any]:
        """获取静态Web应用启动配置"""
        config = {
            "sandbox_permissions": [
                "allow-scripts",
                "allow-same-origin",
                "allow-forms",
                "allow-popups"  # 静态网站可能需要弹窗
            ],
            "performance_monitoring": True,
            "error_monitoring": True,
            "memory_limit": "64MB",  # 静态网站通常内存需求较小
            "cache_enabled": True
        }
        
        # 根据产品配置调整
        features = product_config.get("features", {})
        if features.get("animations", True):
            config["sandbox_permissions"].append("allow-pointer-lock")
        
        optimization = product_config.get("optimization", {})
        if optimization.get("cache_strategy") == "aggressive":
            config["cache_ttl"] = 86400  # 24小时缓存
        elif optimization.get("cache_strategy") == "basic":
            config["cache_ttl"] = 3600   # 1小时缓存
        
        return config


class StaticWebRenderer(ProductRenderer):
    """静态Web应用渲染器"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="static_web_renderer",
            version="1.0.0",
            description="静态Web应用产品渲染器",
            author="Static Web Extension Team",
            extension_type=ExtensionType.RENDERER,
            dependencies=["static_web_extension"],
            config_schema={}
        )
    
    def render_product(self, product_id: int, config: Dict[str, any]) -> str:
        """渲染静态Web应用产品"""
        # 获取静态网站配置
        site_config = config.get("site_config", {})
        features = config.get("features", {})
        seo = config.get("seo", {})
        
        # 构建静态网站容器HTML
        html = f'''
        <div class="static-web-container" id="static-web-container-{product_id}">
            <div class="static-web-header">
                <div class="site-info">
                    <h3 id="site-title">{site_config.get("title", "静态网站")}</h3>
                    <span id="site-status">加载中...</span>
                </div>
                <div class="site-controls">
                    <button id="refresh-btn" class="site-btn" title="刷新">
                        <i class="fas fa-sync-alt"></i>
                    </button>
                    <button id="theme-btn" class="site-btn" title="切换主题">
                        <i class="fas fa-moon"></i>
                    </button>
                    <button id="fullscreen-btn" class="site-btn" title="全屏">
                        <i class="fas fa-expand"></i>
                    </button>
                </div>
            </div>
            
            <div class="static-web-iframe-container">
                <iframe 
                    id="static-web-iframe-{product_id}"
                    src="/products/{product_id}/index.html"
                    frameborder="0"
                    allowfullscreen
                    sandbox="allow-scripts allow-same-origin allow-forms allow-popups">
                </iframe>
            </div>
            
            <div class="static-web-footer">
                <div class="performance-info">
                    <span id="load-time">加载时间: --</span>
                    <span id="resource-count">资源: --</span>
                </div>
                <div class="site-meta">
                    <span id="page-url">--</span>
                </div>
            </div>
        </div>
        
        <style>
        .static-web-container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #ffffff;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1);
        }}
        
        .static-web-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 12px 16px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
        }}
        
        .site-info h3 {{
            margin: 0;
            font-size: 16px;
            font-weight: 600;
        }}
        
        .site-info span {{
            font-size: 12px;
            opacity: 0.8;
        }}
        
        .site-controls {{
            display: flex;
            gap: 8px;
        }}
        
        .site-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 8px 10px;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.2s;
            font-size: 14px;
        }}
        
        .site-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
            transform: translateY(-1px);
        }}
        
        .site-btn:active {{
            transform: translateY(0);
        }}
        
        .static-web-iframe-container {{
            flex: 1;
            position: relative;
            background: #f8f9fa;
        }}
        
        .static-web-iframe-container iframe {{
            width: 100%;
            height: 100%;
            border: none;
        }}
        
        .static-web-footer {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 8px 16px;
            background: #f8f9fa;
            border-top: 1px solid #e9ecef;
            font-size: 12px;
            color: #6c757d;
        }}
        
        .performance-info {{
            display: flex;
            gap: 16px;
        }}
        
        .site-meta {{
            font-family: monospace;
            max-width: 300px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
        }}
        
        /* 响应式设计 */
        @media (max-width: 768px) {{
            .static-web-header {{
                padding: 8px 12px;
            }}
            
            .site-info h3 {{
                font-size: 14px;
            }}
            
            .site-btn {{
                padding: 6px 8px;
                font-size: 12px;
            }}
            
            .static-web-footer {{
                padding: 6px 12px;
                font-size: 11px;
            }}
            
            .performance-info {{
                gap: 12px;
            }}
            
            .site-meta {{
                max-width: 150px;
            }}
        }}
        
        /* 暗色主题 */
        .static-web-container.dark-theme {{
            background: #1a1a1a;
        }}
        
        .static-web-container.dark-theme .static-web-header {{
            background: linear-gradient(135deg, #2d3748 0%, #4a5568 100%);
        }}
        
        .static-web-container.dark-theme .static-web-footer {{
            background: #2d3748;
            border-top-color: #4a5568;
            color: #a0aec0;
        }}
        
        .static-web-container.dark-theme .static-web-iframe-container {{
            background: #2d3748;
        }}
        </style>
        
        <script>
        (function() {{
            const container = document.getElementById('static-web-container-{product_id}');
            const iframe = document.getElementById('static-web-iframe-{product_id}');
            const siteTitle = document.getElementById('site-title');
            const siteStatus = document.getElementById('site-status');
            const refreshBtn = document.getElementById('refresh-btn');
            const themeBtn = document.getElementById('theme-btn');
            const fullscreenBtn = document.getElementById('fullscreen-btn');
            const loadTimeSpan = document.getElementById('load-time');
            const resourceCountSpan = document.getElementById('resource-count');
            const pageUrlSpan = document.getElementById('page-url');
            
            let isDarkTheme = false;
            let loadStartTime = Date.now();
            
            // 页面加载完成处理
            iframe.addEventListener('load', function() {{
                siteStatus.textContent = '已加载';
                const loadTime = Date.now() - loadStartTime;
                loadTimeSpan.textContent = `加载时间: ${{loadTime}}ms`;
                
                // 尝试获取页面信息
                try {{
                    const iframeDoc = iframe.contentDocument || iframe.contentWindow.document;
                    const title = iframeDoc.title;
                    if (title) {{
                        siteTitle.textContent = title;
                    }}
                    pageUrlSpan.textContent = iframe.src.split('/').pop();
                }} catch (e) {{
                    // 跨域限制，忽略错误
                    pageUrlSpan.textContent = 'index.html';
                }}
            }});
            
            // 刷新功能
            refreshBtn.addEventListener('click', function() {{
                loadStartTime = Date.now();
                siteStatus.textContent = '刷新中...';
                iframe.src = iframe.src;
                
                // 旋转图标
                const icon = refreshBtn.querySelector('i');
                icon.style.transform = 'rotate(360deg)';
                setTimeout(() => {{
                    icon.style.transform = 'rotate(0deg)';
                }}, 500);
            }});
            
            // 主题切换
            themeBtn.addEventListener('click', function() {{
                isDarkTheme = !isDarkTheme;
                const icon = themeBtn.querySelector('i');
                
                if (isDarkTheme) {{
                    container.classList.add('dark-theme');
                    icon.className = 'fas fa-sun';
                    themeBtn.title = '切换到亮色主题';
                    
                    // 向iframe发送暗色主题消息
                    iframe.contentWindow.postMessage({{
                        type: 'theme_change',
                        theme: 'dark'
                    }}, '*');
                }} else {{
                    container.classList.remove('dark-theme');
                    icon.className = 'fas fa-moon';
                    themeBtn.title = '切换到暗色主题';
                    
                    // 向iframe发送亮色主题消息
                    iframe.contentWindow.postMessage({{
                        type: 'theme_change',
                        theme: 'light'
                    }}, '*');
                }}
            }});
            
            // 全屏功能
            fullscreenBtn.addEventListener('click', function() {{
                if (document.fullscreenElement) {{
                    document.exitFullscreen();
                }} else {{
                    container.requestFullscreen();
                }}
            }});
            
            // 监听来自iframe的消息
            window.addEventListener('message', function(event) {{
                if (event.source !== iframe.contentWindow) return;
                
                const data = event.data;
                
                if (data.type === 'page_ready') {{
                    siteStatus.textContent = '就绪';
                    if (data.title) {{
                        siteTitle.textContent = data.title;
                    }}
                }} else if (data.type === 'performance_data') {{
                    if (data.loadTime) {{
                        loadTimeSpan.textContent = `加载时间: ${{Math.round(data.loadTime)}}ms`;
                    }}
                    if (data.resources) {{
                        resourceCountSpan.textContent = `资源: ${{data.resources}}个`;
                    }}
                }} else if (data.type === 'javascript_error') {{
                    siteStatus.textContent = '脚本错误';
                    siteStatus.style.color = '#dc3545';
                    console.error('静态网站JavaScript错误:', data);
                }} else if (data.type === 'theme_changed') {{
                    // 同步主题状态
                    isDarkTheme = data.theme === 'dark';
                    const icon = themeBtn.querySelector('i');
                    if (isDarkTheme) {{
                        container.classList.add('dark-theme');
                        icon.className = 'fas fa-sun';
                    }} else {{
                        container.classList.remove('dark-theme');
                        icon.className = 'fas fa-moon';
                    }}
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