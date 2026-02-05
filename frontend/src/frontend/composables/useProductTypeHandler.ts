import { ref, computed } from 'vue'
import type { Product } from '../../shared/types'

interface ProductTypeConfig {
  sandboxOptions: string[]
  allowedFeatures: string[]
  securityLevel: 'low' | 'medium' | 'high'
  resourceLimits: {
    maxMemory?: number
    maxCPU?: number
    maxStorage?: number
  }
  specialHandling?: {
    preload?: boolean
    caching?: boolean
    optimization?: boolean
  }
}

interface StaticWebAppConfig extends ProductTypeConfig {
  baseUrl: string
  entryPoint: string
  assetPaths: string[]
  routingMode: 'hash' | 'history' | 'none'
}

// 产品类型配置
const productTypeConfigs: Record<string, ProductTypeConfig> = {
  static: {
    sandboxOptions: [
      'allow-scripts',
      'allow-same-origin',
      'allow-forms',
      'allow-popups',
      'allow-modals',
      'allow-downloads'
    ],
    allowedFeatures: [
      'localStorage',
      'sessionStorage',
      'indexedDB',
      'webGL',
      'canvas',
      'audio',
      'video'
    ],
    securityLevel: 'medium',
    resourceLimits: {
      maxMemory: 512 * 1024 * 1024, // 512MB
      maxStorage: 100 * 1024 * 1024  // 100MB
    },
    specialHandling: {
      preload: true,
      caching: true,
      optimization: true
    }
  },
  
  spa: {
    sandboxOptions: [
      'allow-scripts',
      'allow-same-origin',
      'allow-forms',
      'allow-popups',
      'allow-modals',
      'allow-downloads'
    ],
    allowedFeatures: [
      'localStorage',
      'sessionStorage',
      'indexedDB',
      'webGL',
      'canvas',
      'audio',
      'video'
    ],
    securityLevel: 'medium',
    resourceLimits: {
      maxMemory: 512 * 1024 * 1024, // 512MB
      maxStorage: 100 * 1024 * 1024  // 100MB
    },
    specialHandling: {
      preload: true,
      caching: true,
      optimization: true
    }
  },
  
  web_app: {
    sandboxOptions: [
      'allow-scripts',
      'allow-same-origin',
      'allow-forms',
      'allow-popups',
      'allow-modals',
      'allow-downloads'
    ],
    allowedFeatures: [
      'localStorage',
      'sessionStorage',
      'indexedDB',
      'webGL',
      'canvas',
      'audio',
      'video'
    ],
    securityLevel: 'medium',
    resourceLimits: {
      maxMemory: 512 * 1024 * 1024, // 512MB
      maxStorage: 100 * 1024 * 1024  // 100MB
    },
    specialHandling: {
      preload: true,
      caching: true,
      optimization: true
    }
  },
  
  game: {
    sandboxOptions: [
      'allow-scripts',
      'allow-same-origin',
      'allow-forms',
      'allow-popups',
      'allow-modals',
      'allow-pointer-lock'
      // 注意：allow-fullscreen 不是有效的 sandbox 属性，应使用 allow="fullscreen" 属性
    ],
    allowedFeatures: [
      'localStorage',
      'sessionStorage',
      'webGL',
      'canvas',
      'audio',
      'gamepad',
      'pointerLock',
      'fullscreen'
    ],
    securityLevel: 'medium',
    resourceLimits: {
      maxMemory: 1024 * 1024 * 1024, // 1GB
      maxStorage: 200 * 1024 * 1024   // 200MB
    },
    specialHandling: {
      preload: true,
      caching: true,
      optimization: true
    }
  },
  
  tool: {
    sandboxOptions: [
      'allow-scripts',
      'allow-same-origin',
      'allow-forms',
      'allow-popups',
      'allow-modals',
      'allow-downloads'
    ],
    allowedFeatures: [
      'localStorage',
      'sessionStorage',
      'indexedDB',
      'canvas',
      'clipboard',
      'notifications'
    ],
    securityLevel: 'high',
    resourceLimits: {
      maxMemory: 256 * 1024 * 1024, // 256MB
      maxStorage: 50 * 1024 * 1024   // 50MB
    },
    specialHandling: {
      preload: false,
      caching: true,
      optimization: false
    }
  },
  
  demo: {
    sandboxOptions: [
      'allow-scripts',
      'allow-same-origin',
      'allow-forms',
      'allow-popups'
    ],
    allowedFeatures: [
      'localStorage',
      'canvas',
      'audio',
      'video'
    ],
    securityLevel: 'high',
    resourceLimits: {
      maxMemory: 128 * 1024 * 1024, // 128MB
      maxStorage: 25 * 1024 * 1024   // 25MB
    },
    specialHandling: {
      preload: false,
      caching: false,
      optimization: false
    }
  }
}

export function useProductTypeHandler() {
  // 获取产品类型配置
  const getProductTypeConfig = (productType: string): ProductTypeConfig => {
    return productTypeConfigs[productType] || productTypeConfigs.demo
  }
  
  // 生成沙箱选项字符串
  const generateSandboxOptions = (product: Product): string => {
    const config = getProductTypeConfig(product.product_type)
    return config.sandboxOptions.join(' ')
  }
  
  // 检查功能是否被允许
  const isFeatureAllowed = (product: Product, feature: string): boolean => {
    const config = getProductTypeConfig(product.product_type)
    return config.allowedFeatures.includes(feature)
  }
  
  // 获取资源限制
  const getResourceLimits = (product: Product) => {
    const config = getProductTypeConfig(product.product_type)
    return config.resourceLimits
  }
  
  // 处理静态Web应用
  const handleStaticWebApp = (product: Product): StaticWebAppConfig => {
    const baseConfig = getProductTypeConfig(product.product_type)
    
    return {
      ...baseConfig,
      baseUrl: `/products/${product.id}/`,
      entryPoint: product.entry_file,
      assetPaths: [
        'assets/',
        'css/',
        'js/',
        'images/',
        'fonts/',
        'static/'
      ],
      routingMode: 'hash' // 默认使用hash路由避免路径冲突
    }
  }
  
  // 预处理产品资源
  const preprocessResources = async (product: Product): Promise<{
    optimizedAssets: string[]
    preloadUrls: string[]
    cacheStrategy: 'aggressive' | 'normal' | 'minimal'
  }> => {
    const config = getProductTypeConfig(product.product_type)
    
    const result = {
      optimizedAssets: [] as string[],
      preloadUrls: [] as string[],
      cacheStrategy: 'normal' as 'aggressive' | 'normal' | 'minimal'
    }
    
    // 根据产品类型设置缓存策略
    if (config.specialHandling?.caching) {
      result.cacheStrategy = config.specialHandling.optimization ? 'aggressive' : 'normal'
    } else {
      result.cacheStrategy = 'minimal'
    }
    
    // 如果启用预加载，添加关键资源
    if (config.specialHandling?.preload) {
      result.preloadUrls = [
        `/products/${product.id}/${product.entry_file}`,
        `/products/${product.id}/css/`,
        `/products/${product.id}/js/`
      ]
    }
    
    return result
  }
  
  // 创建产品运行时环境
  const createRuntimeEnvironment = (product: Product) => {
    const config = getProductTypeConfig(product.product_type)
    
    return {
      productId: product.id,
      productType: product.product_type,
      securityLevel: config.securityLevel,
      allowedFeatures: config.allowedFeatures,
      resourceLimits: config.resourceLimits,
      
      // 运行时API
      api: {
        // 存储API
        storage: {
          get: (key: string) => {
            if (!isFeatureAllowed(product, 'localStorage')) return null
            return localStorage.getItem(`product_${product.id}_${key}`)
          },
          set: (key: string, value: string) => {
            if (!isFeatureAllowed(product, 'localStorage')) return false
            localStorage.setItem(`product_${product.id}_${key}`, value)
            return true
          },
          remove: (key: string) => {
            if (!isFeatureAllowed(product, 'localStorage')) return false
            localStorage.removeItem(`product_${product.id}_${key}`)
            return true
          }
        },
        
        // 通信API
        messaging: {
          postMessage: (message: any) => {
            window.parent.postMessage({
              type: 'product_message',
              productId: product.id,
              data: message
            }, '*')
          },
          
          onMessage: (callback: (message: any) => void) => {
            const handler = (event: MessageEvent) => {
              if (event.data?.type === 'host_message' && 
                  event.data?.productId === product.id) {
                callback(event.data.data)
              }
            }
            window.addEventListener('message', handler)
            return () => window.removeEventListener('message', handler)
          }
        },
        
        // 分析API
        analytics: {
          track: (event: string, data?: any) => {
            window.parent.postMessage({
              type: 'product_analytics',
              productId: product.id,
              event,
              data,
              timestamp: Date.now()
            }, '*')
          }
        }
      }
    }
  }
  
  // 验证产品兼容性
  const validateCompatibility = (product: Product): {
    compatible: boolean
    issues: string[]
    recommendations: string[]
  } => {
    const issues: string[] = []
    const recommendations: string[] = []
    
    // 检查入口文件
    if (!product.entry_file || !product.entry_file.endsWith('.html')) {
      issues.push('入口文件必须是HTML文件')
    }
    
    // 检查产品类型
    if (!productTypeConfigs[product.product_type]) {
      issues.push(`不支持的产品类型: ${product.product_type}`)
    }
    
    // 根据产品类型提供建议
    const config = getProductTypeConfig(product.product_type)
    
    if (product.product_type === 'static') {
      recommendations.push('静态网页产品建议优化资源加载速度')
      recommendations.push('建议使用响应式设计以适配不同设备')
    }
    
    if (product.product_type === 'spa') {
      recommendations.push('单页应用建议启用路由和状态管理')
      recommendations.push('建议配置适当的缓存策略以提升性能')
    }
    
    if (product.product_type === 'game') {
      recommendations.push('游戏类产品建议使用Canvas或WebGL技术')
      recommendations.push('建议启用全屏和指针锁定功能')
    }
    
    if (product.product_type === 'tool') {
      recommendations.push('工具类产品建议优化加载速度')
      recommendations.push('建议支持键盘快捷键操作')
    }
    
    if (config.securityLevel === 'high') {
      recommendations.push('高安全级别产品，某些功能可能受限')
    }
    
    return {
      compatible: issues.length === 0,
      issues,
      recommendations
    }
  }
  
  // 优化产品加载
  const optimizeLoading = (product: Product) => {
    const config = getProductTypeConfig(product.product_type)
    
    const optimizations = {
      preconnect: [] as string[],
      preload: [] as string[],
      prefetch: [] as string[],
      lazyLoad: [] as string[]
    }
    
    // 基础优化
    optimizations.preconnect.push(`/products/${product.id}/`)
    
    if (config.specialHandling?.preload) {
      optimizations.preload.push(
        `/products/${product.id}/${product.entry_file}`,
        `/products/${product.id}/css/main.css`,
        `/products/${product.id}/js/main.js`
      )
    }
    
    if (config.specialHandling?.optimization) {
      optimizations.prefetch.push(
        `/products/${product.id}/assets/`,
        `/products/${product.id}/images/`
      )
    }
    
    return optimizations
  }
  
  // 处理产品错误
  const handleProductError = (product: Product, error: Error | string) => {
    const errorMessage = typeof error === 'string' ? error : error.message
    
    // 发送错误信息到父窗口
    window.parent.postMessage({
      type: 'product_error',
      productId: product.id,
      error: errorMessage,
      timestamp: Date.now()
    }, '*')
    
    // 根据产品类型提供特定的错误处理
    const config = getProductTypeConfig(product.product_type)
    
    if (config.securityLevel === 'high') {
      // 高安全级别产品，记录详细错误信息
      console.error(`[Product ${product.id}] Security Error:`, error)
    }
  }
  
  return {
    // 配置相关
    getProductTypeConfig,
    generateSandboxOptions,
    isFeatureAllowed,
    getResourceLimits,
    
    // 类型处理
    handleStaticWebApp,
    preprocessResources,
    createRuntimeEnvironment,
    
    // 兼容性和优化
    validateCompatibility,
    optimizeLoading,
    handleProductError
  }
}