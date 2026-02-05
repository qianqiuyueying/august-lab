import { ref, computed } from 'vue'
import type { Product } from '../../shared/types'

// 扩展 Window 接口以支持 SPA 框架检测
declare global {
  interface Window {
    React?: any
    Vue?: any
    ng?: any
    __REACT_DEVTOOLS_GLOBAL_HOOK__?: any
    __VUE__?: any
    getAllAngularRootElements?: () => any[]
    SPARouter?: any
  }
}

interface SPAConfig {
  routingMode: 'hash' | 'history' | 'memory'
  baseUrl: string
  fallbackRoute: string
  routeInterception: boolean
  historyManagement: boolean
}

interface RouteInfo {
  path: string
  hash: string
  search: string
  state: any
}

export function useSPAHandler() {
  // SPA路由状态
  const currentRoute = ref<RouteInfo>({
    path: '/',
    hash: '',
    search: '',
    state: null
  })
  
  const routeHistory = ref<RouteInfo[]>([])
  const isNavigating = ref(false)
  
  // 创建SPA配置
  const createSPAConfig = (product: Product): SPAConfig => {
    // 根据产品配置或默认设置确定路由模式
    const routingMode = product.config_data?.routingMode || 'hash'
    
    return {
      routingMode,
      baseUrl: `/products/${product.id}/`,
      fallbackRoute: product.entry_file,
      routeInterception: true,
      historyManagement: true
    }
  }
  
  // 初始化SPA路由处理
  const initializeSPARouting = (product: Product, iframe: HTMLIFrameElement) => {
    const config = createSPAConfig(product)
    
    // 监听iframe内的路由变化
    const handleRouteChange = (event: MessageEvent) => {
      if (event.source !== iframe.contentWindow) return
      
      if (event.data?.type === 'spa_route_change') {
        const routeInfo: RouteInfo = event.data.route
        updateCurrentRoute(routeInfo)
        
        // 记录路由历史
        if (config.historyManagement) {
          addToHistory(routeInfo)
        }
      }
    }
    
    // 监听浏览器历史变化
    const handlePopState = (event: PopStateEvent) => {
      if (config.routingMode === 'history' && config.routeInterception) {
        // 阻止主站路由变化，转发给SPA
        event.preventDefault()
        
        const newRoute: RouteInfo = {
          path: window.location.pathname.replace(config.baseUrl, '/'),
          hash: window.location.hash,
          search: window.location.search,
          state: event.state
        }
        
        // 通知SPA路由变化
        iframe.contentWindow?.postMessage({
          type: 'host_route_change',
          route: newRoute
        }, '*')
      }
    }
    
    // 添加事件监听
    window.addEventListener('message', handleRouteChange)
    window.addEventListener('popstate', handlePopState)
    
    // 注入路由处理脚本到SPA
    iframe.onload = () => {
      injectSPARoutingScript(iframe, config)
    }
    
    // 返回清理函数
    return () => {
      window.removeEventListener('message', handleRouteChange)
      window.removeEventListener('popstate', handlePopState)
    }
  }
  
  // 注入SPA路由处理脚本
  const injectSPARoutingScript = (iframe: HTMLIFrameElement, config: SPAConfig) => {
    const script = `
      (function() {
        // SPA路由处理器
        const SPARouter = {
          config: ${JSON.stringify(config)},
          
          // 初始化路由监听
          init() {
            this.setupRouteListening();
            this.setupHistoryInterception();
            this.notifyRouteChange();
          },
          
          // 设置路由监听
          setupRouteListening() {
            // 监听hash变化
            if (this.config.routingMode === 'hash') {
              window.addEventListener('hashchange', () => {
                this.notifyRouteChange();
              });
            }
            
            // 监听history变化
            if (this.config.routingMode === 'history') {
              const originalPushState = history.pushState;
              const originalReplaceState = history.replaceState;
              
              history.pushState = function(...args) {
                originalPushState.apply(history, args);
                SPARouter.notifyRouteChange();
              };
              
              history.replaceState = function(...args) {
                originalReplaceState.apply(history, args);
                SPARouter.notifyRouteChange();
              };
              
              window.addEventListener('popstate', () => {
                this.notifyRouteChange();
              });
            }
          },
          
          // 设置历史拦截
          setupHistoryInterception() {
            // 拦截链接点击
            document.addEventListener('click', (event) => {
              const link = event.target.closest('a');
              if (link && this.shouldInterceptLink(link)) {
                event.preventDefault();
                this.navigate(link.href);
              }
            });
          },
          
          // 判断是否应该拦截链接
          shouldInterceptLink(link) {
            const href = link.getAttribute('href');
            if (!href || href.startsWith('http') || href.startsWith('mailto:') || href.startsWith('tel:')) {
              return false;
            }
            return true;
          },
          
          // 导航到新路由
          navigate(url) {
            if (this.config.routingMode === 'hash') {
              window.location.hash = url;
            } else if (this.config.routingMode === 'history') {
              history.pushState(null, '', url);
              this.notifyRouteChange();
            }
          },
          
          // 通知路由变化
          notifyRouteChange() {
            const route = {
              path: this.config.routingMode === 'hash' 
                ? window.location.hash.slice(1) || '/'
                : window.location.pathname,
              hash: window.location.hash,
              search: window.location.search,
              state: history.state
            };
            
            // 发送到父窗口
            window.parent.postMessage({
              type: 'spa_route_change',
              route: route
            }, '*');
          },
          
          // 监听来自父窗口的路由变化
          handleHostRouteChange(event) {
            if (event.data?.type === 'host_route_change') {
              const route = event.data.route;
              
              if (this.config.routingMode === 'hash') {
                window.location.hash = route.path;
              } else if (this.config.routingMode === 'history') {
                history.pushState(route.state, '', route.path);
              }
            }
          }
        };
        
        // 监听来自父窗口的消息
        window.addEventListener('message', (event) => {
          SPARouter.handleHostRouteChange(event);
        });
        
        // 初始化路由器
        if (document.readyState === 'loading') {
          document.addEventListener('DOMContentLoaded', () => {
            SPARouter.init();
          });
        } else {
          SPARouter.init();
        }
        
        // 暴露到全局，供SPA框架使用
        window.SPARouter = SPARouter;
      })();
    `
    
    try {
      const doc = iframe.contentDocument || iframe.contentWindow?.document
      if (doc) {
        const scriptElement = doc.createElement('script')
        scriptElement.textContent = script
        doc.head.appendChild(scriptElement)
      }
    } catch (error) {
      console.warn('无法注入SPA路由脚本:', error)
    }
  }
  
  // 更新当前路由
  const updateCurrentRoute = (route: RouteInfo) => {
    currentRoute.value = { ...route }
  }
  
  // 添加到历史记录
  const addToHistory = (route: RouteInfo) => {
    routeHistory.value.push({ ...route })
    
    // 限制历史记录数量
    if (routeHistory.value.length > 50) {
      routeHistory.value = routeHistory.value.slice(-50)
    }
  }
  
  // 导航到指定路由
  const navigateToRoute = (iframe: HTMLIFrameElement, path: string) => {
    isNavigating.value = true
    
    iframe.contentWindow?.postMessage({
      type: 'host_navigate',
      path: path
    }, '*')
    
    setTimeout(() => {
      isNavigating.value = false
    }, 1000)
  }
  
  // 返回上一页
  const goBack = (iframe: HTMLIFrameElement) => {
    if (routeHistory.value.length > 1) {
      const previousRoute = routeHistory.value[routeHistory.value.length - 2]
      navigateToRoute(iframe, previousRoute.path)
      routeHistory.value.pop() // 移除当前路由
    }
  }
  
  // 刷新当前路由
  const refreshRoute = (iframe: HTMLIFrameElement) => {
    iframe.contentWindow?.postMessage({
      type: 'host_refresh'
    }, '*')
  }
  
  // 获取路由信息
  const getRouteInfo = () => {
    return {
      current: currentRoute.value,
      history: routeHistory.value,
      canGoBack: routeHistory.value.length > 1,
      isNavigating: isNavigating.value
    }
  }
  
  // 处理SPA框架特定的路由
  const handleFrameworkRouting = (product: Product, framework: string) => {
    const frameworkConfigs = {
      react: {
        routerLibrary: 'react-router',
        historyMode: 'browser',
        basePath: `/products/${product.id}/`
      },
      vue: {
        routerLibrary: 'vue-router',
        historyMode: 'history',
        basePath: `/products/${product.id}/`
      },
      angular: {
        routerLibrary: '@angular/router',
        historyMode: 'PathLocationStrategy',
        basePath: `/products/${product.id}/`
      }
    }
    
    return frameworkConfigs[framework as keyof typeof frameworkConfigs] || null
  }
  
  // 检测SPA框架
  const detectSPAFramework = (iframe: HTMLIFrameElement): Promise<string | null> => {
    return new Promise((resolve) => {
      const timeout = setTimeout(() => resolve(null), 3000)
      
      const checkFramework = () => {
        try {
          const win = iframe.contentWindow
          if (!win) return
          
          // 检测React
          if (win.React || win.__REACT_DEVTOOLS_GLOBAL_HOOK__) {
            clearTimeout(timeout)
            resolve('react')
            return
          }
          
          // 检测Vue
          if (win.Vue || win.__VUE__) {
            clearTimeout(timeout)
            resolve('vue')
            return
          }
          
          // 检测Angular
          if (win.ng || win.getAllAngularRootElements) {
            clearTimeout(timeout)
            resolve('angular')
            return
          }
          
          // 继续检测
          setTimeout(checkFramework, 500)
        } catch (error) {
          // 跨域限制，无法检测
          clearTimeout(timeout)
          resolve(null)
        }
      }
      
      iframe.onload = checkFramework
      if (iframe.contentDocument?.readyState === 'complete') {
        checkFramework()
      }
    })
  }
  
  // 清理路由状态
  const clearRouteState = () => {
    currentRoute.value = {
      path: '/',
      hash: '',
      search: '',
      state: null
    }
    routeHistory.value = []
    isNavigating.value = false
  }
  
  return {
    // 状态
    currentRoute: computed(() => currentRoute.value),
    routeHistory: computed(() => routeHistory.value),
    isNavigating: computed(() => isNavigating.value),
    
    // 方法
    createSPAConfig,
    initializeSPARouting,
    navigateToRoute,
    goBack,
    refreshRoute,
    getRouteInfo,
    handleFrameworkRouting,
    detectSPAFramework,
    clearRouteState
  }
}