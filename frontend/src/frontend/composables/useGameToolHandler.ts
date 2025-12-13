import { ref, computed } from 'vue'
import type { Product } from '../../shared/types'

interface GameConfig {
  enableFullscreen: boolean
  enablePointerLock: boolean
  enableGamepad: boolean
  enableWebGL: boolean
  enableAudio: boolean
  performanceMode: 'balanced' | 'performance' | 'quality'
  inputHandling: {
    keyboard: boolean
    mouse: boolean
    touch: boolean
    gamepad: boolean
  }
}

interface ToolConfig {
  enableClipboard: boolean
  enableNotifications: boolean
  enableFileAccess: boolean
  enableDownloads: boolean
  dataStorage: {
    localStorage: boolean
    sessionStorage: boolean
    indexedDB: boolean
  }
  shortcuts: {
    enabled: boolean
    customKeys: Record<string, string>
  }
}

interface PerformanceMetrics {
  fps: number
  memoryUsage: number
  cpuUsage: number
  renderTime: number
  inputLatency: number
}

export function useGameToolHandler() {
  // 性能监控状态
  const performanceMetrics = ref<PerformanceMetrics>({
    fps: 0,
    memoryUsage: 0,
    cpuUsage: 0,
    renderTime: 0,
    inputLatency: 0
  })
  
  const isMonitoring = ref(false)
  let performanceMonitor: number | null = null
  
  // 创建游戏配置
  const createGameConfig = (product: Product): GameConfig => {
    const customConfig = product.config_data?.game || {}
    
    return {
      enableFullscreen: customConfig.fullscreen !== false,
      enablePointerLock: customConfig.pointerLock !== false,
      enableGamepad: customConfig.gamepad !== false,
      enableWebGL: customConfig.webgl !== false,
      enableAudio: customConfig.audio !== false,
      performanceMode: customConfig.performanceMode || 'balanced',
      inputHandling: {
        keyboard: customConfig.keyboard !== false,
        mouse: customConfig.mouse !== false,
        touch: customConfig.touch !== false,
        gamepad: customConfig.gamepad !== false
      }
    }
  }
  
  // 创建工具配置
  const createToolConfig = (product: Product): ToolConfig => {
    const customConfig = product.config_data?.tool || {}
    
    return {
      enableClipboard: customConfig.clipboard !== false,
      enableNotifications: customConfig.notifications !== false,
      enableFileAccess: customConfig.fileAccess === true,
      enableDownloads: customConfig.downloads !== false,
      dataStorage: {
        localStorage: customConfig.localStorage !== false,
        sessionStorage: customConfig.sessionStorage !== false,
        indexedDB: customConfig.indexedDB !== false
      },
      shortcuts: {
        enabled: customConfig.shortcuts !== false,
        customKeys: customConfig.customKeys || {}
      }
    }
  }
  
  // 初始化游戏支持
  const initializeGameSupport = (product: Product, iframe: HTMLIFrameElement) => {
    const config = createGameConfig(product)
    
    // 注入游戏支持脚本
    const gameScript = `
      (function() {
        const GameSupport = {
          config: ${JSON.stringify(config)},
          
          init() {
            this.setupInputHandling();
            this.setupPerformanceMonitoring();
            this.setupGamepadSupport();
            this.setupFullscreenSupport();
            this.setupAudioContext();
          },
          
          // 设置输入处理
          setupInputHandling() {
            if (this.config.inputHandling.keyboard) {
              this.setupKeyboardHandling();
            }
            if (this.config.inputHandling.mouse) {
              this.setupMouseHandling();
            }
            if (this.config.inputHandling.touch) {
              this.setupTouchHandling();
            }
          },
          
          // 键盘处理
          setupKeyboardHandling() {
            let keyStates = {};
            
            document.addEventListener('keydown', (e) => {
              keyStates[e.code] = true;
              
              // 阻止某些默认行为
              if (['Space', 'ArrowUp', 'ArrowDown', 'ArrowLeft', 'ArrowRight'].includes(e.code)) {
                e.preventDefault();
              }
              
              this.notifyInputEvent('keyboard', {
                type: 'keydown',
                code: e.code,
                key: e.key,
                states: keyStates
              });
            });
            
            document.addEventListener('keyup', (e) => {
              keyStates[e.code] = false;
              
              this.notifyInputEvent('keyboard', {
                type: 'keyup',
                code: e.code,
                key: e.key,
                states: keyStates
              });
            });
          },
          
          // 鼠标处理
          setupMouseHandling() {
            let mouseState = { x: 0, y: 0, buttons: 0 };
            
            document.addEventListener('mousemove', (e) => {
              mouseState.x = e.clientX;
              mouseState.y = e.clientY;
              
              this.notifyInputEvent('mouse', {
                type: 'mousemove',
                x: e.clientX,
                y: e.clientY,
                movementX: e.movementX,
                movementY: e.movementY
              });
            });
            
            document.addEventListener('mousedown', (e) => {
              mouseState.buttons |= (1 << e.button);
              
              this.notifyInputEvent('mouse', {
                type: 'mousedown',
                button: e.button,
                x: e.clientX,
                y: e.clientY
              });
            });
            
            document.addEventListener('mouseup', (e) => {
              mouseState.buttons &= ~(1 << e.button);
              
              this.notifyInputEvent('mouse', {
                type: 'mouseup',
                button: e.button,
                x: e.clientX,
                y: e.clientY
              });
            });
          },
          
          // 触摸处理
          setupTouchHandling() {
            document.addEventListener('touchstart', (e) => {
              e.preventDefault();
              
              const touches = Array.from(e.touches).map(touch => ({
                id: touch.identifier,
                x: touch.clientX,
                y: touch.clientY
              }));
              
              this.notifyInputEvent('touch', {
                type: 'touchstart',
                touches: touches
              });
            }, { passive: false });
            
            document.addEventListener('touchmove', (e) => {
              e.preventDefault();
              
              const touches = Array.from(e.touches).map(touch => ({
                id: touch.identifier,
                x: touch.clientX,
                y: touch.clientY
              }));
              
              this.notifyInputEvent('touch', {
                type: 'touchmove',
                touches: touches
              });
            }, { passive: false });
            
            document.addEventListener('touchend', (e) => {
              const touches = Array.from(e.changedTouches).map(touch => ({
                id: touch.identifier,
                x: touch.clientX,
                y: touch.clientY
              }));
              
              this.notifyInputEvent('touch', {
                type: 'touchend',
                touches: touches
              });
            });
          },
          
          // 手柄支持
          setupGamepadSupport() {
            if (!this.config.enableGamepad) return;
            
            let gamepads = {};
            
            window.addEventListener('gamepadconnected', (e) => {
              gamepads[e.gamepad.index] = e.gamepad;
              
              this.notifyInputEvent('gamepad', {
                type: 'connected',
                gamepad: {
                  index: e.gamepad.index,
                  id: e.gamepad.id,
                  buttons: e.gamepad.buttons.length,
                  axes: e.gamepad.axes.length
                }
              });
            });
            
            window.addEventListener('gamepaddisconnected', (e) => {
              delete gamepads[e.gamepad.index];
              
              this.notifyInputEvent('gamepad', {
                type: 'disconnected',
                index: e.gamepad.index
              });
            });
            
            // 轮询手柄状态
            const pollGamepads = () => {
              const currentGamepads = navigator.getGamepads();
              
              for (let i = 0; i < currentGamepads.length; i++) {
                const gamepad = currentGamepads[i];
                if (gamepad && gamepads[i]) {
                  this.notifyInputEvent('gamepad', {
                    type: 'update',
                    index: i,
                    buttons: Array.from(gamepad.buttons).map(b => ({
                      pressed: b.pressed,
                      value: b.value
                    })),
                    axes: Array.from(gamepad.axes)
                  });
                }
              }
              
              requestAnimationFrame(pollGamepads);
            };
            
            requestAnimationFrame(pollGamepads);
          },
          
          // 全屏支持
          setupFullscreenSupport() {
            if (!this.config.enableFullscreen) return;
            
            document.addEventListener('fullscreenchange', () => {
              this.notifyEvent('fullscreen', {
                isFullscreen: !!document.fullscreenElement
              });
            });
          },
          
          // 音频上下文
          setupAudioContext() {
            if (!this.config.enableAudio) return;
            
            // 创建音频上下文（需要用户交互）
            let audioContext = null;
            
            const createAudioContext = () => {
              if (!audioContext) {
                audioContext = new (window.AudioContext || window.webkitAudioContext)();
                
                this.notifyEvent('audio', {
                  type: 'context_created',
                  sampleRate: audioContext.sampleRate,
                  state: audioContext.state
                });
              }
            };
            
            // 在用户交互时创建音频上下文
            document.addEventListener('click', createAudioContext, { once: true });
            document.addEventListener('keydown', createAudioContext, { once: true });
          },
          
          // 性能监控
          setupPerformanceMonitoring() {
            let frameCount = 0;
            let lastTime = performance.now();
            
            const measurePerformance = () => {
              const currentTime = performance.now();
              frameCount++;
              
              if (currentTime - lastTime >= 1000) {
                const fps = Math.round((frameCount * 1000) / (currentTime - lastTime));
                
                // 获取内存使用情况
                const memory = performance.memory ? {
                  used: performance.memory.usedJSHeapSize,
                  total: performance.memory.totalJSHeapSize,
                  limit: performance.memory.jsHeapSizeLimit
                } : null;
                
                this.notifyEvent('performance', {
                  fps: fps,
                  memory: memory,
                  timestamp: currentTime
                });
                
                frameCount = 0;
                lastTime = currentTime;
              }
              
              requestAnimationFrame(measurePerformance);
            };
            
            requestAnimationFrame(measurePerformance);
          },
          
          // 通知输入事件
          notifyInputEvent(inputType, data) {
            window.parent.postMessage({
              type: 'game_input',
              inputType: inputType,
              data: data,
              timestamp: performance.now()
            }, '*');
          },
          
          // 通知一般事件
          notifyEvent(eventType, data) {
            window.parent.postMessage({
              type: 'game_event',
              eventType: eventType,
              data: data,
              timestamp: performance.now()
            }, '*');
          }
        };
        
        // 初始化游戏支持
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', () => {
            GameSupport.init();
          });
        } else {
          GameSupport.init();
        }
        
        // 暴露到全局
        window.GameSupport = GameSupport;
      })();
    `
    
    injectScript(iframe, gameScript)
  }
  
  // 初始化工具支持
  const initializeToolSupport = (product: Product, iframe: HTMLIFrameElement) => {
    const config = createToolConfig(product)
    
    // 注入工具支持脚本
    const toolScript = `
      (function() {
        const ToolSupport = {
          config: ${JSON.stringify(config)},
          
          init() {
            this.setupClipboardAPI();
            this.setupNotificationAPI();
            this.setupShortcuts();
            this.setupDataStorage();
            this.setupFileHandling();
          },
          
          // 剪贴板API
          setupClipboardAPI() {
            if (!this.config.enableClipboard) return;
            
            window.ToolAPI = window.ToolAPI || {};
            
            window.ToolAPI.clipboard = {
              read: async () => {
                try {
                  return await navigator.clipboard.readText();
                } catch (error) {
                  console.warn('剪贴板读取失败:', error);
                  return null;
                }
              },
              
              write: async (text) => {
                try {
                  await navigator.clipboard.writeText(text);
                  return true;
                } catch (error) {
                  console.warn('剪贴板写入失败:', error);
                  return false;
                }
              }
            };
          },
          
          // 通知API
          setupNotificationAPI() {
            if (!this.config.enableNotifications) return;
            
            window.ToolAPI = window.ToolAPI || {};
            
            window.ToolAPI.notifications = {
              show: async (title, options = {}) => {
                if (Notification.permission === 'granted') {
                  return new Notification(title, options);
                } else if (Notification.permission !== 'denied') {
                  const permission = await Notification.requestPermission();
                  if (permission === 'granted') {
                    return new Notification(title, options);
                  }
                }
                return null;
              },
              
              requestPermission: () => {
                return Notification.requestPermission();
              }
            };
          },
          
          // 快捷键支持
          setupShortcuts() {
            if (!this.config.shortcuts.enabled) return;
            
            const shortcuts = this.config.shortcuts.customKeys;
            const activeKeys = new Set();
            
            document.addEventListener('keydown', (e) => {
              activeKeys.add(e.code);
              
              // 检查快捷键组合
              for (const [shortcut, action] of Object.entries(shortcuts)) {
                const keys = shortcut.split('+');
                const allPressed = keys.every(key => {
                  if (key === 'Ctrl') return e.ctrlKey;
                  if (key === 'Alt') return e.altKey;
                  if (key === 'Shift') return e.shiftKey;
                  if (key === 'Meta') return e.metaKey;
                  return activeKeys.has(key);
                });
                
                if (allPressed) {
                  e.preventDefault();
                  this.notifyShortcut(shortcut, action);
                }
              }
            });
            
            document.addEventListener('keyup', (e) => {
              activeKeys.delete(e.code);
            });
          },
          
          // 数据存储
          setupDataStorage() {
            window.ToolAPI = window.ToolAPI || {};
            
            window.ToolAPI.storage = {
              local: this.config.dataStorage.localStorage ? {
                get: (key) => localStorage.getItem('tool_' + key),
                set: (key, value) => localStorage.setItem('tool_' + key, value),
                remove: (key) => localStorage.removeItem('tool_' + key),
                clear: () => {
                  const keys = Object.keys(localStorage);
                  keys.forEach(key => {
                    if (key.startsWith('tool_')) {
                      localStorage.removeItem(key);
                    }
                  });
                }
              } : null,
              
              session: this.config.dataStorage.sessionStorage ? {
                get: (key) => sessionStorage.getItem('tool_' + key),
                set: (key, value) => sessionStorage.setItem('tool_' + key, value),
                remove: (key) => sessionStorage.removeItem('tool_' + key)
              } : null
            };
          },
          
          // 文件处理
          setupFileHandling() {
            if (!this.config.enableFileAccess) return;
            
            window.ToolAPI = window.ToolAPI || {};
            
            window.ToolAPI.files = {
              select: async (options = {}) => {
                return new Promise((resolve) => {
                  const input = document.createElement('input');
                  input.type = 'file';
                  input.multiple = options.multiple || false;
                  input.accept = options.accept || '*/*';
                  
                  input.onchange = (e) => {
                    const files = Array.from(e.target.files || []);
                    resolve(files);
                  };
                  
                  input.click();
                });
              },
              
              download: (data, filename, type = 'text/plain') => {
                const blob = new Blob([data], { type });
                const url = URL.createObjectURL(blob);
                
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                
                URL.revokeObjectURL(url);
              }
            };
          },
          
          // 通知快捷键
          notifyShortcut(shortcut, action) {
            window.parent.postMessage({
              type: 'tool_shortcut',
              shortcut: shortcut,
              action: action,
              timestamp: Date.now()
            }, '*');
          }
        };
        
        // 初始化工具支持
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', () => {
            ToolSupport.init();
          });
        } else {
          ToolSupport.init();
        }
        
        // 暴露到全局
        window.ToolSupport = ToolSupport;
      })();
    `
    
    injectScript(iframe, toolScript)
  }
  
  // 注入脚本到iframe
  const injectScript = (iframe: HTMLIFrameElement, script: string) => {
    try {
      const doc = iframe.contentDocument || iframe.contentWindow?.document
      if (doc) {
        const scriptElement = doc.createElement('script')
        scriptElement.textContent = script
        doc.head.appendChild(scriptElement)
      }
    } catch (error) {
      console.warn('无法注入脚本:', error)
    }
  }
  
  // 开始性能监控
  const startPerformanceMonitoring = () => {
    if (isMonitoring.value) return
    
    isMonitoring.value = true
    
    const monitor = () => {
      // 这里可以添加更详细的性能监控逻辑
      if (isMonitoring.value) {
        performanceMonitor = requestAnimationFrame(monitor)
      }
    }
    
    performanceMonitor = requestAnimationFrame(monitor)
  }
  
  // 停止性能监控
  const stopPerformanceMonitoring = () => {
    isMonitoring.value = false
    
    if (performanceMonitor) {
      cancelAnimationFrame(performanceMonitor)
      performanceMonitor = null
    }
  }
  
  // 处理游戏输入事件
  const handleGameInput = (inputType: string, data: any) => {
    // 可以在这里添加输入处理逻辑
    console.log(`游戏输入 [${inputType}]:`, data)
  }
  
  // 处理工具快捷键
  const handleToolShortcut = (shortcut: string, action: string) => {
    // 可以在这里添加快捷键处理逻辑
    console.log(`工具快捷键 [${shortcut}]: ${action}`)
  }
  
  // 优化游戏性能
  const optimizeGamePerformance = (product: Product) => {
    const config = createGameConfig(product)
    
    const optimizations = {
      webgl: config.enableWebGL,
      audio: config.enableAudio,
      performanceMode: config.performanceMode,
      inputOptimization: true
    }
    
    return optimizations
  }
  
  // 优化工具性能
  const optimizeToolPerformance = (product: Product) => {
    const config = createToolConfig(product)
    
    const optimizations = {
      dataStorage: config.dataStorage,
      shortcuts: config.shortcuts.enabled,
      clipboardAccess: config.enableClipboard
    }
    
    return optimizations
  }
  
  return {
    // 状态
    performanceMetrics: computed(() => performanceMetrics.value),
    isMonitoring: computed(() => isMonitoring.value),
    
    // 配置
    createGameConfig,
    createToolConfig,
    
    // 初始化
    initializeGameSupport,
    initializeToolSupport,
    
    // 性能监控
    startPerformanceMonitoring,
    stopPerformanceMonitoring,
    
    // 事件处理
    handleGameInput,
    handleToolShortcut,
    
    // 优化
    optimizeGamePerformance,
    optimizeToolPerformance
  }
}