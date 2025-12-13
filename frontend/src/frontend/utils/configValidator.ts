// 产品配置验证工具
export interface ValidationRule {
  field: string
  required?: boolean
  type?: 'string' | 'number' | 'boolean' | 'array' | 'object'
  min?: number
  max?: number
  pattern?: RegExp
  enum?: any[]
  custom?: (value: any) => boolean | string
  message?: string
}

export interface ValidationResult {
  valid: boolean
  errors: ValidationError[]
  warnings: ValidationWarning[]
}

export interface ValidationError {
  field: string
  message: string
  value?: any
}

export interface ValidationWarning {
  field: string
  message: string
  value?: any
}

// 基础验证规则
const baseRules: ValidationRule[] = [
  {
    field: 'type',
    required: true,
    type: 'string',
    enum: ['static', 'spa', 'game', 'tool'],
    message: '产品类型必须是 static、spa、game 或 tool 之一'
  },
  {
    field: 'version',
    required: true,
    type: 'string',
    pattern: /^\d+\.\d+$/,
    message: '版本号格式应为 "主版本.次版本"'
  },
  {
    field: 'runtime.entryFile',
    required: true,
    type: 'string',
    pattern: /\.(html|htm)$/i,
    message: '入口文件必须是HTML文件'
  }
]

// 类型特定验证规则
const typeSpecificRules: Record<string, ValidationRule[]> = {
  static: [
    {
      field: 'permissions.network.websocket',
      custom: (value) => value !== true,
      message: '静态应用不应启用WebSocket权限'
    },
    {
      field: 'integration.parentCommunication',
      custom: (value) => value !== true,
      message: '静态应用通常不需要父页面通信'
    }
  ],
  
  spa: [
    {
      field: 'runtime.publicPath',
      required: true,
      type: 'string',
      message: 'SPA应用需要指定公共路径'
    },
    {
      field: 'permissions.storage.localStorage',
      custom: (value) => value === true,
      message: 'SPA应用建议启用本地存储'
    }
  ],
  
  game: [
    {
      field: 'display.fullscreenSupport',
      custom: (value) => value === true,
      message: '游戏应用建议启用全屏支持'
    },
    {
      field: 'performance.preload',
      type: 'array',
      custom: (value) => Array.isArray(value) && value.length > 0,
      message: '游戏应用建议配置预加载资源'
    },
    {
      field: 'security.sandbox',
      custom: (value) => Array.isArray(value) && value.includes('allow-pointer-lock'),
      message: '游戏应用建议启用指针锁定权限'
    }
  ],
  
  tool: [
    {
      field: 'permissions.clipboard',
      custom: (value) => value === true,
      message: '工具应用建议启用剪贴板权限'
    },
    {
      field: 'integration.parentCommunication',
      custom: (value) => value === true,
      message: '工具应用建议启用父页面通信'
    }
  ]
}

// 安全验证规则
const securityRules: ValidationRule[] = [
  {
    field: 'security.sandbox',
    required: true,
    type: 'array',
    custom: (value) => Array.isArray(value) && value.includes('allow-scripts'),
    message: '沙箱配置必须包含 allow-scripts'
  },
  {
    field: 'security.allowedOrigins',
    type: 'array',
    custom: (value) => {
      if (!Array.isArray(value)) return true
      return value.every(origin => {
        try {
          new URL(origin)
          return true
        } catch {
          return false
        }
      })
    },
    message: '允许的来源必须是有效的URL'
  },
  {
    field: 'permissions.network.websocket',
    custom: (value, config) => {
      if (value && !config.permissions?.network?.fetch) {
        return '启用WebSocket需要同时启用Fetch权限'
      }
      return true
    }
  }
]

// 性能验证规则
const performanceRules: ValidationRule[] = [
  {
    field: 'performance.caching.maxAge',
    type: 'number',
    min: 0,
    max: 86400,
    message: '缓存最大时间必须在0-86400秒之间'
  },
  {
    field: 'performance.preload',
    type: 'array',
    custom: (value) => {
      if (!Array.isArray(value)) return true
      return value.length <= 20
    },
    message: '预加载资源不应超过20个'
  },
  {
    field: 'display.width',
    custom: (value) => {
      if (typeof value === 'number') {
        return value > 0 && value <= 3840
      }
      return value === 'auto'
    },
    message: '显示宽度必须是正数或 "auto"'
  },
  {
    field: 'display.height',
    custom: (value) => {
      if (typeof value === 'number') {
        return value > 0 && value <= 2160
      }
      return value === 'auto'
    },
    message: '显示高度必须是正数或 "auto"'
  }
]

export class ConfigValidator {
  private rules: ValidationRule[] = []
  
  constructor() {
    this.rules = [
      ...baseRules,
      ...securityRules,
      ...performanceRules
    ]
  }
  
  // 验证配置
  validate(config: any): ValidationResult {
    const errors: ValidationError[] = []
    const warnings: ValidationWarning[] = []
    
    // 基础验证
    this.validateWithRules(config, this.rules, errors, warnings)
    
    // 类型特定验证
    if (config.type && typeSpecificRules[config.type]) {
      this.validateWithRules(config, typeSpecificRules[config.type], errors, warnings, true)
    }
    
    // 自定义验证
    this.validateCustomRules(config, errors, warnings)
    
    return {
      valid: errors.length === 0,
      errors,
      warnings
    }
  }
  
  // 使用规则验证
  private validateWithRules(
    config: any,
    rules: ValidationRule[],
    errors: ValidationError[],
    warnings: ValidationWarning[],
    isWarning = false
  ) {
    for (const rule of rules) {
      const value = this.getNestedValue(config, rule.field)
      const error = this.validateRule(rule, value, config)
      
      if (error) {
        if (isWarning) {
          warnings.push({
            field: rule.field,
            message: error,
            value
          })
        } else {
          errors.push({
            field: rule.field,
            message: error,
            value
          })
        }
      }
    }
  }
  
  // 验证单个规则
  private validateRule(rule: ValidationRule, value: any, config: any): string | null {
    // 必填验证
    if (rule.required && (value === undefined || value === null || value === '')) {
      return rule.message || `${rule.field} 是必填字段`
    }
    
    // 如果值为空且不是必填，跳过其他验证
    if (value === undefined || value === null || value === '') {
      return null
    }
    
    // 类型验证
    if (rule.type && !this.validateType(value, rule.type)) {
      return rule.message || `${rule.field} 类型错误，期望 ${rule.type}`
    }
    
    // 最小值验证
    if (rule.min !== undefined && (typeof value === 'number' && value < rule.min)) {
      return rule.message || `${rule.field} 不能小于 ${rule.min}`
    }
    
    // 最大值验证
    if (rule.max !== undefined && (typeof value === 'number' && value > rule.max)) {
      return rule.message || `${rule.field} 不能大于 ${rule.max}`
    }
    
    // 正则验证
    if (rule.pattern && typeof value === 'string' && !rule.pattern.test(value)) {
      return rule.message || `${rule.field} 格式不正确`
    }
    
    // 枚举验证
    if (rule.enum && !rule.enum.includes(value)) {
      return rule.message || `${rule.field} 必须是 ${rule.enum.join(', ')} 之一`
    }
    
    // 自定义验证
    if (rule.custom) {
      const result = rule.custom(value, config)
      if (result !== true) {
        return typeof result === 'string' ? result : (rule.message || `${rule.field} 验证失败`)
      }
    }
    
    return null
  }
  
  // 类型验证
  private validateType(value: any, expectedType: string): boolean {
    switch (expectedType) {
      case 'string':
        return typeof value === 'string'
      case 'number':
        return typeof value === 'number' && !isNaN(value)
      case 'boolean':
        return typeof value === 'boolean'
      case 'array':
        return Array.isArray(value)
      case 'object':
        return typeof value === 'object' && value !== null && !Array.isArray(value)
      default:
        return true
    }
  }
  
  // 获取嵌套值
  private getNestedValue(obj: any, path: string): any {
    return path.split('.').reduce((current, key) => {
      return current && current[key] !== undefined ? current[key] : undefined
    }, obj)
  }
  
  // 自定义验证规则
  private validateCustomRules(config: any, errors: ValidationError[], warnings: ValidationWarning[]) {
    // 验证宽高比
    if (config.display?.aspectRatio) {
      const aspectRatio = config.display.aspectRatio
      if (typeof aspectRatio === 'string' && !/^\d+:\d+$/.test(aspectRatio)) {
        errors.push({
          field: 'display.aspectRatio',
          message: '宽高比格式应为 "width:height"',
          value: aspectRatio
        })
      }
    }
    
    // 验证环境变量
    if (config.runtime?.environment) {
      const env = config.runtime.environment
      for (const [key, value] of Object.entries(env)) {
        if (typeof key !== 'string' || key.trim() === '') {
          errors.push({
            field: 'runtime.environment',
            message: '环境变量名不能为空',
            value: key
          })
        }
        
        if (typeof value !== 'string') {
          errors.push({
            field: 'runtime.environment',
            message: '环境变量值必须是字符串',
            value: value
          })
        }
      }
    }
    
    // 验证预加载资源路径
    if (config.performance?.preload) {
      const preload = config.performance.preload
      if (Array.isArray(preload)) {
        for (const path of preload) {
          if (typeof path !== 'string' || path.trim() === '') {
            errors.push({
              field: 'performance.preload',
              message: '预加载资源路径不能为空',
              value: path
            })
          }
        }
      }
    }
    
    // 验证权限一致性
    if (config.permissions?.network?.websocket && !config.permissions?.network?.fetch) {
      warnings.push({
        field: 'permissions.network',
        message: '启用WebSocket建议同时启用Fetch权限',
        value: config.permissions.network
      })
    }
    
    // 验证性能配置合理性
    if (config.performance?.caching?.enabled && !config.performance?.preload?.length) {
      warnings.push({
        field: 'performance',
        message: '启用缓存时建议配置预加载资源以提升性能',
        value: config.performance
      })
    }
    
    // 验证安全配置
    if (config.permissions?.clipboard && !config.security?.sandbox?.includes('allow-same-origin')) {
      errors.push({
        field: 'security.sandbox',
        message: '启用剪贴板权限需要 allow-same-origin 沙箱权限',
        value: config.security?.sandbox
      })
    }
  }
  
  // 添加自定义规则
  addRule(rule: ValidationRule) {
    this.rules.push(rule)
  }
  
  // 移除规则
  removeRule(field: string) {
    this.rules = this.rules.filter(rule => rule.field !== field)
  }
  
  // 获取所有规则
  getRules(): ValidationRule[] {
    return [...this.rules]
  }
}

// 创建默认验证器实例
export const defaultValidator = new ConfigValidator()

// 快速验证函数
export function validateProductConfig(config: any): ValidationResult {
  return defaultValidator.validate(config)
}

// 验证特定字段
export function validateField(config: any, field: string): ValidationError | null {
  const result = defaultValidator.validate(config)
  const error = result.errors.find(err => err.field === field)
  return error || null
}

// 获取字段建议
export function getFieldSuggestions(productType: string, field: string): string[] {
  const suggestions: Record<string, Record<string, string[]>> = {
    static: {
      'runtime.features': ['responsive-design', 'dark-mode'],
      'performance.preload': ['css/', 'images/', 'fonts/']
    },
    spa: {
      'runtime.features': ['pwa', 'offline-support', 'real-time-sync'],
      'performance.preload': ['js/vendor.js', 'css/app.css'],
      'integration.eventForwarding': ['resize', 'scroll']
    },
    game: {
      'runtime.features': ['touch-support', 'gamepad-support', 'fullscreen'],
      'performance.preload': ['assets/sprites/', 'assets/audio/', 'assets/textures/'],
      'integration.eventForwarding': ['gamepad', 'keyboard', 'mouse', 'touchstart']
    },
    tool: {
      'runtime.features': ['keyboard-shortcuts', 'drag-drop', 'file-upload'],
      'performance.preload': ['js/workers/', 'data/'],
      'integration.eventForwarding': ['keydown', 'paste', 'drop']
    }
  }
  
  return suggestions[productType]?.[field] || []
}