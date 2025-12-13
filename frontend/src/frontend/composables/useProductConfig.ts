import { ref, computed, reactive } from 'vue'
import type { Product } from '../../shared/types'

// 产品配置接口定义
interface ProductConfigSchema {
  type: 'static' | 'spa' | 'game' | 'tool'
  version: string
  metadata: {
    title: string
    description?: string
    author?: string
    version?: string
    license?: string
    homepage?: string
    repository?: string
  }
  runtime: {
    entryFile: string
    baseUrl?: string
    publicPath?: string
    environment?: Record<string, string>
    features?: string[]
  }
  display: {
    width?: number | 'auto'
    height?: number | 'auto'
    minWidth?: number
    minHeight?: number
    maxWidth?: number
    maxHeight?: number
    aspectRatio?: string
    responsive?: boolean
    fullscreenSupport?: boolean
  }
  permissions: {
    clipboard?: boolean
    notifications?: boolean
    geolocation?: boolean
    camera?: boolean
    microphone?: boolean
    storage?: {
      localStorage?: boolean
      sessionStorage?: boolean
      indexedDB?: boolean
    }
    network?: {
      fetch?: boolean
      websocket?: boolean
      webrtc?: boolean
    }
  }
  performance: {
    preload?: string[]
    lazy?: string[]
    caching?: {
      enabled?: boolean
      strategy?: 'cache-first' | 'network-first' | 'stale-while-revalidate'
      maxAge?: number
    }
    optimization?: {
      minify?: boolean
      compress?: boolean
      bundling?: boolean
    }
  }
  integration: {
    parentCommunication?: boolean
    dataBinding?: boolean
    eventForwarding?: string[]
    customAPI?: Record<string, any>
  }
  security: {
    sandbox?: string[]
    csp?: string
    allowedOrigins?: string[]
    trustedTypes?: boolean
  }
}

// 默认配置模板
const defaultConfigs: Record<string, Partial<ProductConfigSchema>> = {
  static: {
    type: 'static',
    version: '1.0',
    runtime: {
      entryFile: 'index.html'
    },
    display: {
      responsive: true,
      fullscreenSupport: false
    },
    permissions: {
      clipboard: false,
      notifications: false,
      storage: {
        localStorage: true,
        sessionStorage: true,
        indexedDB: false
      }
    },
    security: {
      sandbox: ['allow-scripts', 'allow-same-origin']
    }
  },
  
  spa: {
    type: 'spa',
    version: '1.0',
    runtime: {
      entryFile: 'index.html',
      publicPath: '/'
    },
    display: {
      responsive: true,
      fullscreenSupport: true
    },
    permissions: {
      clipboard: true,
      notifications: true,
      storage: {
        localStorage: true,
        sessionStorage: true,
        indexedDB: true
      },
      network: {
        fetch: true,
        websocket: false
      }
    },
    performance: {
      caching: {
        enabled: true,
        strategy: 'cache-first',
        maxAge: 3600
      }
    },
    integration: {
      parentCommunication: true,
      dataBinding: true
    },
    security: {
      sandbox: ['allow-scripts', 'allow-same-origin', 'allow-forms']
    }
  },
  
  game: {
    type: 'game',
    version: '1.0',
    runtime: {
      entryFile: 'index.html'
    },
    display: {
      fullscreenSupport: true,
      aspectRatio: '16:9'
    },
    permissions: {
      clipboard: false,
      storage: {
        localStorage: true,
        sessionStorage: true,
        indexedDB: true
      }
    },
    performance: {
      preload: ['assets/sprites/', 'assets/audio/'],
      caching: {
        enabled: true,
        strategy: 'cache-first'
      },
      optimization: {
        minify: true,
        compress: true
      }
    },
    integration: {
      parentCommunication: true,
      eventForwarding: ['gamepad', 'keyboard', 'mouse']
    },
    security: {
      sandbox: ['allow-scripts', 'allow-same-origin', 'allow-pointer-lock']
    }
  },
  
  tool: {
    type: 'tool',
    version: '1.0',
    runtime: {
      entryFile: 'index.html'
    },
    display: {
      responsive: true,
      fullscreenSupport: true
    },
    permissions: {
      clipboard: true,
      notifications: true,
      storage: {
        localStorage: true,
        sessionStorage: true,
        indexedDB: true
      },
      network: {
        fetch: true
      }
    },
    integration: {
      parentCommunication: true,
      dataBinding: true,
      customAPI: {}
    },
    security: {
      sandbox: ['allow-scripts', 'allow-same-origin', 'allow-forms', 'allow-downloads']
    }
  }
}

export function useProductConfig() {
  // 当前配置状态
  const currentConfig = ref<ProductConfigSchema | null>(null)
  const configErrors = ref<string[]>([])
  const isValidating = ref(false)
  
  // 创建默认配置
  const createDefaultConfig = (productType: string): ProductConfigSchema => {
    const template = defaultConfigs[productType] || defaultConfigs.static
    
    return {
      type: productType as any,
      version: '1.0',
      metadata: {
        title: '',
        description: '',
        version: '1.0.0'
      },
      runtime: {
        entryFile: 'index.html',
        environment: {},
        features: []
      },
      display: {
        responsive: true,
        fullscreenSupport: false
      },
      permissions: {
        storage: {
          localStorage: true,
          sessionStorage: true,
          indexedDB: false
        },
        network: {
          fetch: false,
          websocket: false
        }
      },
      performance: {
        preload: [],
        lazy: [],
        caching: {
          enabled: false
        }
      },
      integration: {
        parentCommunication: false,
        dataBinding: false,
        eventForwarding: []
      },
      security: {
        sandbox: ['allow-scripts', 'allow-same-origin']
      },
      ...template
    } as ProductConfigSchema
  }
  
  // 从产品数据加载配置
  const loadConfigFromProduct = (product: Product): ProductConfigSchema => {
    if (product.config_data && typeof product.config_data === 'object') {
      // 验证并合并配置
      const defaultConfig = createDefaultConfig(product.product_type)
      const mergedConfig = mergeConfigs(defaultConfig, product.config_data as any)
      
      currentConfig.value = mergedConfig
      return mergedConfig
    }
    
    // 使用默认配置
    const defaultConfig = createDefaultConfig(product.product_type)
    currentConfig.value = defaultConfig
    return defaultConfig
  }
  
  // 合并配置对象
  const mergeConfigs = (defaultConfig: ProductConfigSchema, customConfig: any): ProductConfigSchema => {
    const merged = JSON.parse(JSON.stringify(defaultConfig))
    
    // 深度合并配置
    const deepMerge = (target: any, source: any) => {
      for (const key in source) {
        if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
          if (!target[key]) target[key] = {}
          deepMerge(target[key], source[key])
        } else {
          target[key] = source[key]
        }
      }
    }
    
    deepMerge(merged, customConfig)
    return merged
  }
  
  // 验证配置
  const validateConfig = (config: ProductConfigSchema): { valid: boolean; errors: string[] } => {
    const errors: string[] = []
    
    // 基本字段验证
    if (!config.type || !['static', 'spa', 'game', 'tool'].includes(config.type)) {
      errors.push('产品类型必须是 static、spa、game 或 tool 之一')
    }
    
    if (!config.runtime?.entryFile) {
      errors.push('必须指定入口文件')
    }
    
    // 显示配置验证
    if (config.display) {
      if (config.display.width && typeof config.display.width === 'number' && config.display.width <= 0) {
        errors.push('显示宽度必须大于0')
      }
      
      if (config.display.height && typeof config.display.height === 'number' && config.display.height <= 0) {
        errors.push('显示高度必须大于0')
      }
      
      if (config.display.aspectRatio && !/^\d+:\d+$/.test(config.display.aspectRatio)) {
        errors.push('宽高比格式应为 "width:height"')
      }
    }
    
    // 权限配置验证
    if (config.permissions?.network?.websocket && !config.permissions?.network?.fetch) {
      errors.push('启用WebSocket需要同时启用Fetch权限')
    }
    
    // 性能配置验证
    if (config.performance?.caching?.maxAge && config.performance.caching.maxAge <= 0) {
      errors.push('缓存最大时间必须大于0')
    }
    
    // 安全配置验证
    if (config.security?.sandbox && !Array.isArray(config.security.sandbox)) {
      errors.push('沙箱配置必须是数组')
    }
    
    return {
      valid: errors.length === 0,
      errors
    }
  }
  
  // 应用配置到产品
  const applyConfigToProduct = (config: ProductConfigSchema, product: Product): Product => {
    return {
      ...product,
      config_data: config,
      entry_file: config.runtime.entryFile
    }
  }
  
  // 生成沙箱选项
  const generateSandboxOptions = (config: ProductConfigSchema): string => {
    const sandbox = config.security?.sandbox || ['allow-scripts', 'allow-same-origin']
    return sandbox.join(' ')
  }
  
  // 生成环境变量
  const generateEnvironmentVariables = (config: ProductConfigSchema): Record<string, string> => {
    const env = config.runtime?.environment || {}
    
    // 添加系统环境变量
    return {
      PRODUCT_TYPE: config.type,
      PRODUCT_VERSION: config.version,
      ENTRY_FILE: config.runtime?.entryFile || 'index.html',
      ...env
    }
  }
  
  // 生成运行时配置
  const generateRuntimeConfig = (config: ProductConfigSchema) => {
    return {
      entryFile: config.runtime?.entryFile || 'index.html',
      baseUrl: config.runtime?.baseUrl || '',
      publicPath: config.runtime?.publicPath || '/',
      environment: generateEnvironmentVariables(config),
      features: config.runtime?.features || [],
      
      display: {
        width: config.display?.width || 'auto',
        height: config.display?.height || 'auto',
        responsive: config.display?.responsive !== false,
        fullscreen: config.display?.fullscreenSupport === true,
        aspectRatio: config.display?.aspectRatio
      },
      
      permissions: {
        clipboard: config.permissions?.clipboard === true,
        notifications: config.permissions?.notifications === true,
        geolocation: config.permissions?.geolocation === true,
        storage: config.permissions?.storage || {},
        network: config.permissions?.network || {}
      },
      
      performance: {
        preload: config.performance?.preload || [],
        lazy: config.performance?.lazy || [],
        caching: config.performance?.caching || { enabled: false }
      },
      
      integration: {
        parentCommunication: config.integration?.parentCommunication === true,
        dataBinding: config.integration?.dataBinding === true,
        eventForwarding: config.integration?.eventForwarding || [],
        customAPI: config.integration?.customAPI || {}
      },
      
      security: {
        sandbox: generateSandboxOptions(config),
        csp: config.security?.csp,
        allowedOrigins: config.security?.allowedOrigins || [],
        trustedTypes: config.security?.trustedTypes === true
      }
    }
  }
  
  // 导出配置为JSON
  const exportConfig = (config: ProductConfigSchema): string => {
    return JSON.stringify(config, null, 2)
  }
  
  // 从JSON导入配置
  const importConfig = (jsonString: string): { success: boolean; config?: ProductConfigSchema; error?: string } => {
    try {
      const config = JSON.parse(jsonString)
      const validation = validateConfig(config)
      
      if (validation.valid) {
        currentConfig.value = config
        return { success: true, config }
      } else {
        return { success: false, error: validation.errors.join(', ') }
      }
    } catch (error) {
      return { success: false, error: '无效的JSON格式' }
    }
  }
  
  // 重置配置
  const resetConfig = (productType: string) => {
    currentConfig.value = createDefaultConfig(productType)
  }
  
  // 克隆配置
  const cloneConfig = (config: ProductConfigSchema): ProductConfigSchema => {
    return JSON.parse(JSON.stringify(config))
  }
  
  // 比较配置
  const compareConfigs = (config1: ProductConfigSchema, config2: ProductConfigSchema): boolean => {
    return JSON.stringify(config1) === JSON.stringify(config2)
  }
  
  // 获取配置差异
  const getConfigDiff = (oldConfig: ProductConfigSchema, newConfig: ProductConfigSchema) => {
    const diff: any = {}
    
    const findDifferences = (obj1: any, obj2: any, path = '') => {
      for (const key in obj2) {
        const currentPath = path ? `${path}.${key}` : key
        
        if (!(key in obj1)) {
          diff[currentPath] = { type: 'added', value: obj2[key] }
        } else if (typeof obj2[key] === 'object' && obj2[key] !== null && !Array.isArray(obj2[key])) {
          findDifferences(obj1[key], obj2[key], currentPath)
        } else if (obj1[key] !== obj2[key]) {
          diff[currentPath] = { type: 'changed', oldValue: obj1[key], newValue: obj2[key] }
        }
      }
      
      for (const key in obj1) {
        const currentPath = path ? `${path}.${key}` : key
        if (!(key in obj2)) {
          diff[currentPath] = { type: 'removed', value: obj1[key] }
        }
      }
    }
    
    findDifferences(oldConfig, newConfig)
    return diff
  }
  
  return {
    // 状态
    currentConfig: computed(() => currentConfig.value),
    configErrors: computed(() => configErrors.value),
    isValidating: computed(() => isValidating.value),
    
    // 配置管理
    createDefaultConfig,
    loadConfigFromProduct,
    mergeConfigs,
    validateConfig,
    applyConfigToProduct,
    
    // 运行时
    generateSandboxOptions,
    generateEnvironmentVariables,
    generateRuntimeConfig,
    
    // 导入导出
    exportConfig,
    importConfig,
    
    // 工具方法
    resetConfig,
    cloneConfig,
    compareConfigs,
    getConfigDiff
  }
}