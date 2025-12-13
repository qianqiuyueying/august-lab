// 产品配置模板管理器
import type { ProductConfigSchema } from '../composables/useProductConfig'

export interface ConfigTemplate {
  id: string
  name: string
  description: string
  type: 'static' | 'spa' | 'game' | 'tool'
  category: string
  tags: string[]
  config: Partial<ProductConfigSchema>
  preview?: string
  author?: string
  version?: string
  created?: string
  updated?: string
}

// 预定义模板
export const builtinTemplates: ConfigTemplate[] = [
  // 静态网页模板
  {
    id: 'static-basic',
    name: '基础静态网页',
    description: '适用于简单的HTML/CSS/JS静态网页',
    type: 'static',
    category: '静态网页',
    tags: ['基础', '静态', 'HTML'],
    config: {
      type: 'static',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        features: ['responsive-design']
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
    }
  },
  
  {
    id: 'static-portfolio',
    name: '作品展示网页',
    description: '适用于个人作品展示、简历等静态页面',
    type: 'static',
    category: '静态网页',
    tags: ['作品集', '展示', '响应式'],
    config: {
      type: 'static',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        features: ['responsive-design', 'dark-mode']
      },
      display: {
        responsive: true,
        fullscreenSupport: true,
        aspectRatio: '16:10'
      },
      permissions: {
        clipboard: true,
        storage: {
          localStorage: true,
          sessionStorage: true
        }
      },
      performance: {
        preload: ['css/', 'images/', 'fonts/'],
        caching: {
          enabled: true,
          strategy: 'cache-first',
          maxAge: 3600
        }
      }
    }
  },
  
  // SPA模板
  {
    id: 'spa-react',
    name: 'React单页应用',
    description: '适用于React开发的单页应用',
    type: 'spa',
    category: '单页应用',
    tags: ['React', 'SPA', '现代框架'],
    config: {
      type: 'spa',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        publicPath: '/',
        features: ['pwa', 'offline-support', 'real-time-sync']
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
        preload: ['static/js/main.js', 'static/css/main.css'],
        caching: {
          enabled: true,
          strategy: 'stale-while-revalidate',
          maxAge: 1800
        }
      },
      integration: {
        parentCommunication: true,
        dataBinding: true,
        eventForwarding: ['resize', 'scroll']
      },
      security: {
        sandbox: ['allow-scripts', 'allow-same-origin', 'allow-forms']
      }
    }
  },
  
  {
    id: 'spa-vue',
    name: 'Vue单页应用',
    description: '适用于Vue.js开发的单页应用',
    type: 'spa',
    category: '单页应用',
    tags: ['Vue', 'SPA', '现代框架'],
    config: {
      type: 'spa',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        publicPath: '/',
        features: ['pwa', 'offline-support', 'responsive-design']
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
      performance: {
        preload: ['js/app.js', 'css/app.css'],
        lazy: ['js/vendor.js'],
        caching: {
          enabled: true,
          strategy: 'network-first',
          maxAge: 3600
        }
      },
      integration: {
        parentCommunication: true,
        dataBinding: true
      }
    }
  },
  
  // 游戏模板
  {
    id: 'game-canvas',
    name: 'Canvas 2D游戏',
    description: '适用于基于Canvas的2D游戏',
    type: 'game',
    category: '游戏',
    tags: ['Canvas', '2D', '游戏'],
    config: {
      type: 'game',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        features: ['touch-support', 'gamepad-support', 'fullscreen']
      },
      display: {
        fullscreenSupport: true,
        aspectRatio: '16:9',
        responsive: false,
        width: 800,
        height: 600
      },
      permissions: {
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
          strategy: 'cache-first',
          maxAge: 7200
        },
        optimization: {
          minify: true,
          compress: true
        }
      },
      integration: {
        parentCommunication: true,
        eventForwarding: ['gamepad', 'keyboard', 'mouse', 'touchstart', 'touchmove']
      },
      security: {
        sandbox: ['allow-scripts', 'allow-same-origin', 'allow-pointer-lock', 'allow-fullscreen']
      }
    }
  },
  
  {
    id: 'game-webgl',
    name: 'WebGL 3D游戏',
    description: '适用于基于WebGL的3D游戏',
    type: 'game',
    category: '游戏',
    tags: ['WebGL', '3D', '游戏'],
    config: {
      type: 'game',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        features: ['webgl', 'touch-support', 'gamepad-support', 'fullscreen']
      },
      display: {
        fullscreenSupport: true,
        aspectRatio: '16:9',
        responsive: false,
        width: 1024,
        height: 768
      },
      permissions: {
        storage: {
          localStorage: true,
          indexedDB: true
        }
      },
      performance: {
        preload: ['assets/models/', 'assets/textures/', 'assets/shaders/'],
        caching: {
          enabled: true,
          strategy: 'cache-first',
          maxAge: 10800
        },
        optimization: {
          minify: true,
          compress: true,
          bundling: true
        }
      },
      integration: {
        parentCommunication: true,
        eventForwarding: ['gamepad', 'keyboard', 'mouse', 'touchstart']
      },
      security: {
        sandbox: ['allow-scripts', 'allow-same-origin', 'allow-pointer-lock', 'allow-fullscreen']
      }
    }
  },
  
  // 工具模板
  {
    id: 'tool-calculator',
    name: '计算器工具',
    description: '适用于计算器、转换器等数值计算工具',
    type: 'tool',
    category: '工具',
    tags: ['计算器', '工具', '实用'],
    config: {
      type: 'tool',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        features: ['keyboard-shortcuts', 'responsive-design']
      },
      display: {
        responsive: true,
        fullscreenSupport: false,
        width: 400,
        height: 600
      },
      permissions: {
        clipboard: true,
        storage: {
          localStorage: true,
          sessionStorage: true
        }
      },
      integration: {
        parentCommunication: true,
        dataBinding: true,
        eventForwarding: ['keydown', 'paste']
      },
      security: {
        sandbox: ['allow-scripts', 'allow-same-origin']
      }
    }
  },
  
  {
    id: 'tool-editor',
    name: '文本编辑器',
    description: '适用于在线文本编辑器、代码编辑器等',
    type: 'tool',
    category: '工具',
    tags: ['编辑器', '文本', '代码'],
    config: {
      type: 'tool',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        features: ['keyboard-shortcuts', 'drag-drop', 'file-upload']
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
      performance: {
        preload: ['js/editor.js', 'css/themes/'],
        lazy: ['js/plugins/']
      },
      integration: {
        parentCommunication: true,
        dataBinding: true,
        eventForwarding: ['keydown', 'paste', 'drop'],
        customAPI: {
          saveFile: true,
          loadFile: true,
          exportFile: true
        }
      },
      security: {
        sandbox: ['allow-scripts', 'allow-same-origin', 'allow-forms', 'allow-downloads']
      }
    }
  },
  
  {
    id: 'tool-converter',
    name: '格式转换器',
    description: '适用于文件格式转换、数据处理等工具',
    type: 'tool',
    category: '工具',
    tags: ['转换器', '处理', '格式'],
    config: {
      type: 'tool',
      version: '1.0',
      runtime: {
        entryFile: 'index.html',
        features: ['drag-drop', 'file-upload', 'responsive-design']
      },
      display: {
        responsive: true,
        fullscreenSupport: false
      },
      permissions: {
        clipboard: true,
        storage: {
          localStorage: true,
          indexedDB: true
        }
      },
      performance: {
        preload: ['js/workers/'],
        lazy: ['js/converters/']
      },
      integration: {
        parentCommunication: true,
        eventForwarding: ['drop', 'paste']
      },
      security: {
        sandbox: ['allow-scripts', 'allow-same-origin', 'allow-downloads']
      }
    }
  }
]

export class ConfigTemplateManager {
  private templates: Map<string, ConfigTemplate> = new Map()
  private customTemplates: ConfigTemplate[] = []
  
  constructor() {
    // 加载内置模板
    builtinTemplates.forEach(template => {
      this.templates.set(template.id, template)
    })
    
    // 加载自定义模板
    this.loadCustomTemplates()
  }
  
  // 获取所有模板
  getAllTemplates(): ConfigTemplate[] {
    return Array.from(this.templates.values())
  }
  
  // 根据类型获取模板
  getTemplatesByType(type: string): ConfigTemplate[] {
    return this.getAllTemplates().filter(template => template.type === type)
  }
  
  // 根据分类获取模板
  getTemplatesByCategory(category: string): ConfigTemplate[] {
    return this.getAllTemplates().filter(template => template.category === category)
  }
  
  // 根据标签搜索模板
  searchTemplatesByTag(tag: string): ConfigTemplate[] {
    return this.getAllTemplates().filter(template => 
      template.tags.some(t => t.toLowerCase().includes(tag.toLowerCase()))
    )
  }
  
  // 搜索模板
  searchTemplates(query: string): ConfigTemplate[] {
    const lowerQuery = query.toLowerCase()
    return this.getAllTemplates().filter(template => 
      template.name.toLowerCase().includes(lowerQuery) ||
      template.description.toLowerCase().includes(lowerQuery) ||
      template.tags.some(tag => tag.toLowerCase().includes(lowerQuery))
    )
  }
  
  // 获取单个模板
  getTemplate(id: string): ConfigTemplate | undefined {
    return this.templates.get(id)
  }
  
  // 添加自定义模板
  addCustomTemplate(template: Omit<ConfigTemplate, 'id' | 'created' | 'updated'>): string {
    const id = `custom-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`
    const fullTemplate: ConfigTemplate = {
      ...template,
      id,
      created: new Date().toISOString(),
      updated: new Date().toISOString()
    }
    
    this.templates.set(id, fullTemplate)
    this.customTemplates.push(fullTemplate)
    this.saveCustomTemplates()
    
    return id
  }
  
  // 更新自定义模板
  updateCustomTemplate(id: string, updates: Partial<ConfigTemplate>): boolean {
    const template = this.templates.get(id)
    if (!template || !this.isCustomTemplate(id)) {
      return false
    }
    
    const updatedTemplate = {
      ...template,
      ...updates,
      id, // 保持ID不变
      updated: new Date().toISOString()
    }
    
    this.templates.set(id, updatedTemplate)
    
    // 更新自定义模板数组
    const index = this.customTemplates.findIndex(t => t.id === id)
    if (index !== -1) {
      this.customTemplates[index] = updatedTemplate
    }
    
    this.saveCustomTemplates()
    return true
  }
  
  // 删除自定义模板
  deleteCustomTemplate(id: string): boolean {
    if (!this.isCustomTemplate(id)) {
      return false
    }
    
    this.templates.delete(id)
    this.customTemplates = this.customTemplates.filter(t => t.id !== id)
    this.saveCustomTemplates()
    
    return true
  }
  
  // 检查是否为自定义模板
  isCustomTemplate(id: string): boolean {
    return id.startsWith('custom-')
  }
  
  // 从配置创建模板
  createTemplateFromConfig(
    config: ProductConfigSchema,
    metadata: {
      name: string
      description: string
      category?: string
      tags?: string[]
      author?: string
    }
  ): string {
    return this.addCustomTemplate({
      name: metadata.name,
      description: metadata.description,
      type: config.type,
      category: metadata.category || '自定义',
      tags: metadata.tags || [],
      author: metadata.author,
      version: config.version,
      config
    })
  }
  
  // 应用模板到配置
  applyTemplate(templateId: string, baseConfig?: Partial<ProductConfigSchema>): ProductConfigSchema | null {
    const template = this.getTemplate(templateId)
    if (!template) {
      return null
    }
    
    // 深度合并配置
    const mergedConfig = this.deepMerge(
      template.config,
      baseConfig || {}
    ) as ProductConfigSchema
    
    return mergedConfig
  }
  
  // 获取模板预览
  getTemplatePreview(templateId: string): string {
    const template = this.getTemplate(templateId)
    if (!template) {
      return ''
    }
    
    return JSON.stringify(template.config, null, 2)
  }
  
  // 导出模板
  exportTemplate(templateId: string): string | null {
    const template = this.getTemplate(templateId)
    if (!template) {
      return null
    }
    
    return JSON.stringify(template, null, 2)
  }
  
  // 导入模板
  importTemplate(templateJson: string): { success: boolean; templateId?: string; error?: string } {
    try {
      const template = JSON.parse(templateJson) as ConfigTemplate
      
      // 验证模板格式
      if (!template.name || !template.type || !template.config) {
        return { success: false, error: '模板格式不正确' }
      }
      
      // 生成新ID避免冲突
      const templateId = this.addCustomTemplate({
        name: template.name,
        description: template.description || '',
        type: template.type,
        category: template.category || '导入',
        tags: template.tags || [],
        author: template.author,
        version: template.version,
        config: template.config
      })
      
      return { success: true, templateId }
    } catch (error) {
      return { success: false, error: '无效的JSON格式' }
    }
  }
  
  // 获取所有分类
  getAllCategories(): string[] {
    const categories = new Set<string>()
    this.getAllTemplates().forEach(template => {
      categories.add(template.category)
    })
    return Array.from(categories).sort()
  }
  
  // 获取所有标签
  getAllTags(): string[] {
    const tags = new Set<string>()
    this.getAllTemplates().forEach(template => {
      template.tags.forEach(tag => tags.add(tag))
    })
    return Array.from(tags).sort()
  }
  
  // 深度合并对象
  private deepMerge(target: any, source: any): any {
    const result = { ...target }
    
    for (const key in source) {
      if (source[key] && typeof source[key] === 'object' && !Array.isArray(source[key])) {
        result[key] = this.deepMerge(result[key] || {}, source[key])
      } else {
        result[key] = source[key]
      }
    }
    
    return result
  }
  
  // 加载自定义模板
  private loadCustomTemplates() {
    try {
      const saved = localStorage.getItem('product-config-templates')
      if (saved) {
        this.customTemplates = JSON.parse(saved)
        this.customTemplates.forEach(template => {
          this.templates.set(template.id, template)
        })
      }
    } catch (error) {
      console.warn('加载自定义模板失败:', error)
    }
  }
  
  // 保存自定义模板
  private saveCustomTemplates() {
    try {
      localStorage.setItem('product-config-templates', JSON.stringify(this.customTemplates))
    } catch (error) {
      console.warn('保存自定义模板失败:', error)
    }
  }
}

// 创建默认模板管理器实例
export const templateManager = new ConfigTemplateManager()

// 便捷函数
export function getTemplatesByType(type: string): ConfigTemplate[] {
  return templateManager.getTemplatesByType(type)
}

export function applyTemplate(templateId: string, baseConfig?: Partial<ProductConfigSchema>): ProductConfigSchema | null {
  return templateManager.applyTemplate(templateId, baseConfig)
}

export function searchTemplates(query: string): ConfigTemplate[] {
  return templateManager.searchTemplates(query)
}