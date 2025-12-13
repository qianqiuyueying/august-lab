"""
游戏产品类型扩展示例
支持Canvas、WebGL游戏应用
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'backend'))

from app.services.product_extension_service import (
    ProductTypeExtension, ExtensionMetadata, ProductTypeDefinition, 
    ExtensionType, ProductRenderer
)
from typing import Dict, List


class GameExtension(ProductTypeExtension):
    """游戏产品类型扩展"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="game_extension",
            version="1.0.0",
            description="支持Canvas和WebGL游戏应用",
            author="Game Extension Team",
            extension_type=ExtensionType.PRODUCT_TYPE,
            dependencies=[],
            config_schema={
                "type": "object",
                "properties": {
                    "enable_fullscreen": {
                        "type": "boolean",
                        "default": True,
                        "description": "是否启用全屏功能"
                    },
                    "enable_sound": {
                        "type": "boolean", 
                        "default": True,
                        "description": "是否启用声音"
                    },
                    "performance_mode": {
                        "type": "string",
                        "enum": ["low", "medium", "high"],
                        "default": "medium",
                        "description": "性能模式"
                    }
                }
            }
        )
    
    def get_product_type_definition(self) -> ProductTypeDefinition:
        return ProductTypeDefinition(
            type_name="game",
            display_name="游戏应用",
            description="支持Canvas、WebGL等游戏技术的Web游戏",
            file_extensions=[
                ".html", ".htm", ".js", ".css", ".json",
                ".png", ".jpg", ".jpeg", ".gif", ".svg",
                ".mp3", ".wav", ".ogg", ".mp4", ".webm",
                ".wasm", ".data", ".mem"  # WebAssembly和Emscripten文件
            ],
            entry_files=["index.html", "game.html", "main.html"],
            config_schema={
                "type": "object",
                "properties": {
                    "game_engine": {
                        "type": "string",
                        "enum": ["unity", "unreal", "phaser", "threejs", "babylonjs", "custom"],
                        "description": "游戏引擎类型"
                    },
                    "graphics_api": {
                        "type": "string",
                        "enum": ["canvas2d", "webgl", "webgl2", "webgpu"],
                        "description": "图形API"
                    },
                    "controls": {
                        "type": "object",
                        "properties": {
                            "keyboard": {"type": "boolean", "default": True},
                            "mouse": {"type": "boolean", "default": True},
                            "touch": {"type": "boolean", "default": True},
                            "gamepad": {"type": "boolean", "default": False}
                        }
                    },
                    "audio": {
                        "type": "object",
                        "properties": {
                            "enabled": {"type": "boolean", "default": True},
                            "autoplay": {"type": "boolean", "default": False},
                            "volume": {"type": "number", "minimum": 0, "maximum": 1, "default": 0.8}
                        }
                    },
                    "performance": {
                        "type": "object",
                        "properties": {
                            "target_fps": {"type": "number", "default": 60},
                            "vsync": {"type": "boolean", "default": True},
                            "quality": {"type": "string", "enum": ["low", "medium", "high"], "default": "medium"}
                        }
                    }
                }
            },
            renderer_class="game_renderer"
        )
    
    def validate_product_files(self, files: Dict[str, bytes]) -> tuple[bool, str]:
        """验证游戏文件"""
        # 检查入口文件
        entry_files = ["index.html", "game.html", "main.html"]
        has_entry = any(f in files for f in entry_files)
        if not has_entry:
            return False, f"游戏应用必须包含以下入口文件之一: {', '.join(entry_files)}"
        
        # 检查是否包含游戏相关文件
        has_canvas = False
        has_webgl = False
        
        for filename, content in files.items():
            if filename.endswith(('.html', '.js')):
                try:
                    text_content = content.decode('utf-8', errors='ignore')
                    if 'canvas' in text_content.lower():
                        has_canvas = True
                    if any(api in text_content.lower() for api in ['webgl', 'gl.', 'getcontext']):
                        has_webgl = True
                except:
                    pass
        
        if not has_canvas and not has_webgl:
            return False, "游戏应用应该包含Canvas或WebGL相关代码"
        
        # 检查WebAssembly文件（如果存在）
        wasm_files = [f for f in files.keys() if f.endswith('.wasm')]
        if wasm_files:
            # 验证WASM文件的基本格式
            for wasm_file in wasm_files:
                wasm_content = files[wasm_file]
                if not wasm_content.startswith(b'\x00asm'):
                    return False, f"无效的WebAssembly文件: {wasm_file}"
        
        return True, ""
    
    def process_product_files(self, files: Dict[str, bytes]) -> Dict[str, bytes]:
        """处理游戏文件"""
        processed_files = files.copy()
        
        # 为游戏添加性能监控脚本
        performance_script = '''
// 游戏性能监控脚本
(function() {
    let fps = 0;
    let lastTime = performance.now();
    let frameCount = 0;
    
    function updateFPS() {
        frameCount++;
        const currentTime = performance.now();
        if (currentTime - lastTime >= 1000) {
            fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
            frameCount = 0;
            lastTime = currentTime;
            
            // 发送性能数据到父窗口
            if (window.parent !== window) {
                window.parent.postMessage({
                    type: 'game_performance',
                    fps: fps,
                    memory: performance.memory ? performance.memory.usedJSHeapSize : 0
                }, '*');
            }
        }
        requestAnimationFrame(updateFPS);
    }
    
    // 启动FPS监控
    requestAnimationFrame(updateFPS);
    
    // 监听游戏事件
    window.addEventListener('gamestart', function() {
        if (window.parent !== window) {
            window.parent.postMessage({type: 'game_started'}, '*');
        }
    });
    
    window.addEventListener('gameover', function(event) {
        if (window.parent !== window) {
            window.parent.postMessage({
                type: 'game_over',
                score: event.detail ? event.detail.score : null
            }, '*');
        }
    });
})();
'''
        
        processed_files['_game_monitor.js'] = performance_script.encode('utf-8')
        
        # 修改HTML文件以包含监控脚本
        for filename in list(processed_files.keys()):
            if filename.endswith('.html'):
                try:
                    html_content = processed_files[filename].decode('utf-8')
                    
                    # 在</head>前插入监控脚本
                    if '</head>' in html_content:
                        script_tag = '<script src="_game_monitor.js"></script>\n</head>'
                        html_content = html_content.replace('</head>', script_tag)
                        processed_files[filename] = html_content.encode('utf-8')
                except:
                    pass
        
        return processed_files
    
    def get_launch_config(self, product_config: Dict[str, any]) -> Dict[str, any]:
        """获取游戏启动配置"""
        config = {
            "sandbox_permissions": [
                "allow-scripts",
                "allow-same-origin",
                "allow-pointer-lock",  # 游戏可能需要指针锁定
                "allow-fullscreen"     # 游戏可能需要全屏
            ],
            "performance_monitoring": True,
            "auto_pause_on_blur": True,  # 失去焦点时自动暂停
            "memory_limit": "512MB"      # 内存限制
        }
        
        # 根据产品配置调整
        if product_config.get("performance", {}).get("quality") == "high":
            config["memory_limit"] = "1GB"
        elif product_config.get("performance", {}).get("quality") == "low":
            config["memory_limit"] = "256MB"
        
        return config


class GameRenderer(ProductRenderer):
    """游戏渲染器"""
    
    def get_metadata(self) -> ExtensionMetadata:
        return ExtensionMetadata(
            name="game_renderer",
            version="1.0.0",
            description="游戏产品渲染器",
            author="Game Extension Team",
            extension_type=ExtensionType.RENDERER,
            dependencies=["game_extension"],
            config_schema={}
        )
    
    def render_product(self, product_id: int, config: Dict[str, any]) -> str:
        """渲染游戏产品"""
        # 获取游戏配置
        game_config = config.get("game_config", {})
        controls = game_config.get("controls", {})
        audio = game_config.get("audio", {})
        performance = game_config.get("performance", {})
        
        # 构建游戏容器HTML
        html = f'''
        <div class="game-container" id="game-container-{product_id}">
            <div class="game-header">
                <div class="game-controls">
                    <button id="fullscreen-btn" class="game-btn" title="全屏">
                        <i class="fas fa-expand"></i>
                    </button>
                    <button id="sound-btn" class="game-btn" title="声音">
                        <i class="fas fa-volume-up"></i>
                    </button>
                    <button id="pause-btn" class="game-btn" title="暂停">
                        <i class="fas fa-pause"></i>
                    </button>
                </div>
                <div class="game-info">
                    <span id="fps-counter">FPS: --</span>
                    <span id="memory-usage">内存: --</span>
                </div>
            </div>
            
            <div class="game-iframe-container">
                <iframe 
                    id="game-iframe-{product_id}"
                    src="/products/{product_id}/index.html"
                    frameborder="0"
                    allowfullscreen
                    allow="gamepad; microphone; camera"
                    sandbox="allow-scripts allow-same-origin allow-pointer-lock allow-fullscreen">
                </iframe>
            </div>
            
            <div class="game-loading" id="game-loading-{product_id}">
                <div class="loading-spinner"></div>
                <div class="loading-text">游戏加载中...</div>
            </div>
        </div>
        
        <style>
        .game-container {{
            width: 100%;
            height: 100%;
            display: flex;
            flex-direction: column;
            background: #000;
            position: relative;
        }}
        
        .game-header {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            padding: 10px;
            background: rgba(0, 0, 0, 0.8);
            color: white;
            font-size: 14px;
        }}
        
        .game-controls {{
            display: flex;
            gap: 10px;
        }}
        
        .game-btn {{
            background: rgba(255, 255, 255, 0.2);
            border: none;
            color: white;
            padding: 8px 12px;
            border-radius: 4px;
            cursor: pointer;
            transition: background 0.2s;
        }}
        
        .game-btn:hover {{
            background: rgba(255, 255, 255, 0.3);
        }}
        
        .game-info {{
            display: flex;
            gap: 20px;
            font-family: monospace;
        }}
        
        .game-iframe-container {{
            flex: 1;
            position: relative;
        }}
        
        .game-iframe-container iframe {{
            width: 100%;
            height: 100%;
        }}
        
        .game-loading {{
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            bottom: 0;
            background: rgba(0, 0, 0, 0.9);
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            color: white;
            z-index: 10;
        }}
        
        .loading-spinner {{
            width: 40px;
            height: 40px;
            border: 4px solid rgba(255, 255, 255, 0.3);
            border-top: 4px solid white;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin-bottom: 20px;
        }}
        
        @keyframes spin {{
            0% {{ transform: rotate(0deg); }}
            100% {{ transform: rotate(360deg); }}
        }}
        
        .loading-text {{
            font-size: 16px;
        }}
        </style>
        
        <script>
        (function() {{
            const gameContainer = document.getElementById('game-container-{product_id}');
            const gameIframe = document.getElementById('game-iframe-{product_id}');
            const gameLoading = document.getElementById('game-loading-{product_id}');
            const fullscreenBtn = document.getElementById('fullscreen-btn');
            const soundBtn = document.getElementById('sound-btn');
            const pauseBtn = document.getElementById('pause-btn');
            const fpsCounter = document.getElementById('fps-counter');
            const memoryUsage = document.getElementById('memory-usage');
            
            let isPaused = false;
            let soundEnabled = {audio.get("enabled", True)};
            
            // 游戏加载完成处理
            gameIframe.addEventListener('load', function() {{
                setTimeout(() => {{
                    gameLoading.style.display = 'none';
                }}, 1000);
            }});
            
            // 全屏功能
            fullscreenBtn.addEventListener('click', function() {{
                if (document.fullscreenElement) {{
                    document.exitFullscreen();
                }} else {{
                    gameContainer.requestFullscreen();
                }}
            }});
            
            // 声音控制
            soundBtn.addEventListener('click', function() {{
                soundEnabled = !soundEnabled;
                soundBtn.innerHTML = soundEnabled ? 
                    '<i class="fas fa-volume-up"></i>' : 
                    '<i class="fas fa-volume-mute"></i>';
                
                // 向游戏发送声音控制消息
                gameIframe.contentWindow.postMessage({{
                    type: 'sound_control',
                    enabled: soundEnabled
                }}, '*');
            }});
            
            // 暂停功能
            pauseBtn.addEventListener('click', function() {{
                isPaused = !isPaused;
                pauseBtn.innerHTML = isPaused ? 
                    '<i class="fas fa-play"></i>' : 
                    '<i class="fas fa-pause"></i>';
                
                // 向游戏发送暂停消息
                gameIframe.contentWindow.postMessage({{
                    type: 'pause_control',
                    paused: isPaused
                }}, '*');
            }});
            
            // 监听游戏消息
            window.addEventListener('message', function(event) {{
                if (event.source !== gameIframe.contentWindow) return;
                
                const data = event.data;
                
                if (data.type === 'game_performance') {{
                    fpsCounter.textContent = `FPS: ${{data.fps}}`;
                    if (data.memory) {{
                        const memoryMB = Math.round(data.memory / 1024 / 1024);
                        memoryUsage.textContent = `内存: ${{memoryMB}}MB`;
                    }}
                }} else if (data.type === 'game_started') {{
                    console.log('游戏已启动');
                }} else if (data.type === 'game_over') {{
                    console.log('游戏结束', data.score ? `得分: ${{data.score}}` : '');
                }}
            }});
            
            // 失去焦点时自动暂停（如果配置启用）
            {f'''
            document.addEventListener('visibilitychange', function() {{
                if (document.hidden && !isPaused) {{
                    pauseBtn.click();
                }}
            }});
            ''' if config.get("auto_pause_on_blur", True) else ''}
        }})();
        </script>
        '''
        
        return html
    
    def get_required_assets(self) -> List[str]:
        """获取所需资源"""
        return [
            "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css"
        ]