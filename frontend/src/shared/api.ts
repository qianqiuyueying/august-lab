import axios from 'axios'
import type { AxiosInstance, AxiosResponse, AxiosError } from 'axios'
import { ElMessage, ElNotification } from 'element-plus'

// 错误类型定义
export interface APIError {
  code: string
  message: string
  details?: any
  timestamp: string
}

// 网络状态管理
class NetworkManager {
  private isOnline = navigator.onLine
  private retryQueue: Array<() => Promise<any>> = []
  private maxRetries = 3
  private retryDelay = 1000

  constructor() {
    window.addEventListener('online', () => {
      this.isOnline = true
      this.processRetryQueue()
    })
    
    window.addEventListener('offline', () => {
      this.isOnline = false
      ElNotification({
        title: '网络连接',
        message: '网络连接已断开，请检查网络设置',
        type: 'warning',
        duration: 0
      })
    })
  }

  isNetworkAvailable(): boolean {
    return this.isOnline
  }

  addToRetryQueue(request: () => Promise<any>): void {
    this.retryQueue.push(request)
  }

  private async processRetryQueue(): Promise<void> {
    ElNotification({
      title: '网络连接',
      message: '网络连接已恢复，正在重试请求...',
      type: 'success'
    })

    const queue = [...this.retryQueue]
    this.retryQueue = []

    for (const request of queue) {
      try {
        await request()
      } catch (error) {
        console.error('重试请求失败:', error)
      }
    }
  }

  async retryRequest<T>(
    requestFn: () => Promise<T>,
    retries = this.maxRetries
  ): Promise<T> {
    try {
      return await requestFn()
    } catch (error) {
      if (retries > 0 && this.shouldRetry(error as AxiosError)) {
        await this.delay(this.retryDelay)
        return this.retryRequest(requestFn, retries - 1)
      }
      throw error
    }
  }

  private shouldRetry(error: AxiosError): boolean {
    // 网络错误或服务器错误时重试
    return !error.response || 
           error.response.status >= 500 || 
           error.code === 'NETWORK_ERROR' ||
           error.code === 'TIMEOUT'
  }

  private delay(ms: number): Promise<void> {
    return new Promise(resolve => setTimeout(resolve, ms))
  }
}

const networkManager = new NetworkManager()

// 创建 axios 实例
const api: AxiosInstance = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 检查网络状态
    if (!networkManager.isNetworkAvailable()) {
      return Promise.reject(new Error('网络连接不可用'))
    }

    // 添加请求时间戳
    config.metadata = { startTime: Date.now() }

    // 智能设置Content-Type
    if (!config.headers['Content-Type']) {
      // 如果是FormData，不设置Content-Type，让浏览器自动设置
      if (config.data instanceof FormData) {
        // FormData会自动设置正确的Content-Type和boundary
      } else {
        // 其他情况默认使用JSON
        config.headers['Content-Type'] = 'application/json'
      }
    }

    // 添加认证 token
    const token = localStorage.getItem('admin_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }

    // 添加请求ID用于追踪
    config.headers['X-Request-ID'] = `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;

    return config
  },
  (error) => {
    ElMessage.error('请求配置错误')
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response: AxiosResponse) => {
    // 记录响应时间
    const duration = Date.now() - (response.config.metadata?.startTime || 0)
    if (duration > 3000) {
      console.warn(`慢请求警告: ${response.config.url} 耗时 ${duration}ms`)
    }

    return response
  },
  async (error: AxiosError) => {
    const { response, config, code } = error

    // 构建错误信息
    const errorInfo: APIError = {
      code: response?.status?.toString() || code || 'UNKNOWN_ERROR',
      message: '请求失败',
      details: response?.data,
      timestamp: new Date().toISOString()
    }

    // 处理不同类型的错误
    if (!response) {
      // 网络错误
      if (code === 'NETWORK_ERROR') {
        errorInfo.message = '网络连接失败，请检查网络设置'
        ElMessage.error(errorInfo.message)
      } else if (code === 'TIMEOUT') {
        errorInfo.message = '请求超时，请稍后重试'
        ElMessage.error(errorInfo.message)
      } else {
        errorInfo.message = '网络异常，请检查连接'
        ElMessage.error(errorInfo.message)
      }

      // 添加到重试队列
      if (config && networkManager.isNetworkAvailable()) {
        networkManager.addToRetryQueue(() => api.request(config))
      }
    } else {
      // HTTP 错误
      switch (response.status) {
        case 400: {
          const data = response.data as any
          errorInfo.message = data?.message || '请求参数错误'
          ElMessage.error(errorInfo.message)
          break
        }
        case 401:
          errorInfo.message = '登录已过期，请重新登录'
          localStorage.removeItem('admin_token')
          ElMessage.error(errorInfo.message)
          // 延迟跳转，避免在路由守卫中重复跳转
          setTimeout(() => {
            if (window.location.pathname.startsWith('/admin') && 
                !window.location.pathname.includes('/login')) {
              window.location.href = '/admin/login'
            }
          }, 1000)
          break
        case 403:
          errorInfo.message = '权限不足，无法访问'
          ElMessage.error(errorInfo.message)
          break
        case 404:
          errorInfo.message = '请求的资源不存在'
          ElMessage.error(errorInfo.message)
          break
        case 422: {
          const data = response.data as any
          errorInfo.message = data?.message || '数据验证失败'
          ElMessage.error(errorInfo.message)
          break
        }
        case 429:
          errorInfo.message = '请求过于频繁，请稍后重试'
          ElMessage.warning(errorInfo.message)
          break
        case 500:
          errorInfo.message = '服务器内部错误'
          ElMessage.error(errorInfo.message)
          break
        case 502:
        case 503:
        case 504:
          errorInfo.message = '服务暂时不可用，请稍后重试'
          ElMessage.error(errorInfo.message)
          break
        default: {
          const data = response.data as any
          errorInfo.message = data?.message || `请求失败 (${response.status})`
          ElMessage.error(errorInfo.message)
        }
      }
    }

    // 记录错误日志
    console.error('API Error:', {
      url: config?.url,
      method: config?.method,
      status: response?.status,
      error: errorInfo
    })

    return Promise.reject(errorInfo)
  }
)

// 扩展 axios 配置类型
declare module 'axios' {
  interface AxiosRequestConfig {
    metadata?: {
      startTime: number
    }
  }
}

// API 接口定义
export interface Portfolio {
  id: number
  title: string
  description?: string
  tech_stack: string[]
  project_url?: string
  github_url?: string
  image_url?: string
  display_order: number
  is_featured: boolean
  created_at: string
  updated_at: string
}

export interface Blog {
  id: number
  title: string
  content: string
  summary?: string
  tags: string[]
  is_published: boolean
  cover_image?: string
  created_at: string
  updated_at: string
}

export interface Profile {
  id: number
  name: string
  title: string
  bio: string
  avatar_url?: string
  github_url?: string
  linkedin_url?: string
  twitter_url?: string
  skills: Skill[]
  created_at: string
  updated_at: string
}

export interface Skill {
  name: string
  category: string
  level: number
}

export interface LoginRequest {
  username: string
  password: string
}

export interface LoginResponse {
  access_token: string
  token_type: string
}

// API 方法包装器，自动处理重试
const withRetry = <T>(apiCall: () => Promise<T>): Promise<T> => {
  return networkManager.retryRequest(apiCall)
}

// API 方法
export const portfolioAPI = {
  // 获取所有作品
  getAll: () => withRetry(() => api.get<Portfolio[]>('/portfolio/')),
  
  // 获取单个作品
  getById: (id: number) => withRetry(() => api.get<Portfolio>(`/portfolio/${id}`)),
  
  // 创建作品
  create: (data: Omit<Portfolio, 'id' | 'created_at' | 'updated_at'>) => 
    withRetry(() => api.post<Portfolio>('/portfolio/', data)),
  
  // 更新作品
  update: (id: number, data: Partial<Portfolio>) => 
    withRetry(() => api.put<Portfolio>(`/portfolio/${id}`, data)),
  
  // 删除作品
  delete: (id: number) => withRetry(() => api.delete(`/portfolio/${id}`))
}

export const blogAPI = {
  // 获取所有博客
  getAll: () => withRetry(() => api.get<Blog[]>('/blog/')),
  
  // 获取单个博客
  getById: (id: number) => withRetry(() => api.get<Blog>(`/blog/${id}`)),
  
  // 创建博客
  create: (data: Omit<Blog, 'id' | 'created_at' | 'updated_at'>) => 
    withRetry(() => api.post<Blog>('/blog/', data)),
  
  // 更新博客
  update: (id: number, data: Partial<Blog>) => 
    withRetry(() => api.put<Blog>(`/blog/${id}`, data)),
  
  // 删除博客
  delete: (id: number) => withRetry(() => api.delete(`/blog/${id}`)),
  
  // 管理员获取所有博客（包括草稿）
  getAllAdmin: () => withRetry(() => api.get<Blog[]>('/blog/admin/all'))
}

export const profileAPI = {
  // 获取个人信息
  get: () => withRetry(() => api.get<Profile>('/profile/')),
  
  // 更新个人信息
  update: (data: Partial<Profile>) => withRetry(() => api.put<Profile>('/profile/', data))
}

export const authAPI = {
  // 登录
  login: (data: LoginRequest) => withRetry(() => api.post<LoginResponse>('/auth/login', data)),
  
  // 登出
  logout: () => withRetry(() => api.post('/auth/logout')),
  
  // 验证 token
  verify: () => withRetry(() => api.get('/auth/verify'))
}

export const uploadAPI = {
  // 上传图片
  uploadImage: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return withRetry(() => api.post<{ url: string; filename: string }>('/upload/image', formData))
  },
  
  // 删除图片
  deleteImage: (filename: string) => withRetry(() => api.delete(`/upload/image/${filename}`))
}

// 产品相关接口定义
export interface Product {
  id: number
  title: string
  description?: string
  tech_stack: string[]
  product_type: 'static' | 'spa' | 'game' | 'tool'
  entry_file: string
  file_path?: string
  config_data: Record<string, any>
  is_published: boolean
  is_featured: boolean
  display_order: number
  version: string
  created_at: string
  updated_at: string
}

export interface ProductFile {
  name: string
  path: string
  size: number
  modified: number
  type: string
}

export interface ProductVersion {
  version: string
  timestamp: string
  file_hash: string
  size: number
  description?: string
  files: string[]
  product_id: number
}

export interface SecurityScanResult {
  product_id: number
  scan_time: string
  total_files: number
  safe_files: number
  total_threats: number
  total_warnings: number
  is_safe: boolean
  files: Array<{
    file_path: string
    is_safe: boolean
    threats: string[]
    warnings: string[]
    scan_time: string
  }>
}

export interface ProductUploadResponse {
  message: string
  product_id: number
  file_path: string
  extracted_files: string[]
}

// 产品API
export const productAPI = {
  // 基础CRUD操作
  getAll: () => withRetry(() => api.get<Product[]>('/products/')),
  getById: (id: number) => withRetry(() => api.get<Product>(`/products/${id}`)),
  create: (data: Omit<Product, 'id' | 'created_at' | 'updated_at'>) => 
    withRetry(() => api.post<Product>('/products/', data)),
  update: (id: number, data: Partial<Product>) => 
    withRetry(() => api.put<Product>(`/products/${id}`, data)),
  delete: (id: number) => withRetry(() => api.delete(`/products/${id}`)),

  // 文件上传和管理
  uploadProductFiles: (id: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return withRetry(() => api.post<ProductUploadResponse>(`/products/${id}/upload`, formData))
  },

  uploadSingleFile: (id: number, formData: FormData) => 
    withRetry(() => api.post(`/products/${id}/files/upload-single`, formData)),

  downloadFile: (id: number, filePath: string) => 
    withRetry(() => api.get(`/products/${id}/files/download/${filePath}`, {
      responseType: 'blob'
    })),

  deleteFile: (id: number, filePath: string) => 
    withRetry(() => api.delete(`/products/${id}/files/${filePath}`)),

  getProductFiles: (id: number) => 
    withRetry(() => api.get<{
      files: ProductFile[]
      metadata: Record<string, any>
      total_files: number
      total_size: number
    }>(`/products/${id}/files`)),

  // 版本控制
  createVersion: (id: number, data: { version: string; description?: string }) => 
    withRetry(() => api.post(`/products/${id}/versions`, data)),

  getVersions: (id: number) => 
    withRetry(() => api.get<{ versions: ProductVersion[] }>(`/products/${id}/versions`)),

  restoreVersion: (id: number, version: string) => 
    withRetry(() => api.post(`/products/${id}/versions/${version}/restore`)),

  deleteVersion: (id: number, version: string) => 
    withRetry(() => api.delete(`/products/${id}/versions/${version}`)),

  // 安全扫描
  scanProductSecurity: (id: number) => 
    withRetry(() => api.post<SecurityScanResult>(`/products/${id}/security/scan`)),

  scanFileSecurity: (id: number, file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return withRetry(() => api.post(`/products/${id}/security/scan-file`, formData))
  },

  verifyFilesIntegrity: (id: number) => 
    withRetry(() => api.get<{
      product_id: number
      is_valid: boolean
      message: string
      verified_at: string
    }>(`/products/${id}/files/integrity`)),

  // 资源管理
  getResourceStats: (id: number) => 
    withRetry(() => api.get(`/products/${id}/resources/stats`)),

  getStorageStats: () => 
    withRetry(() => api.get('/products/storage/stats')),

  cleanupResources: (id: number, options: {
    old_versions?: boolean
    temp_files?: boolean
    old_backups?: boolean
    keep_versions?: number
    keep_backups?: number
  }) => withRetry(() => api.post(`/products/${id}/resources/cleanup`, options)),

  // 产品统计
  getStats: (id: number) => 
    withRetry(() => api.get(`/products/${id}/stats`)),

  recordAccess: (id: number, data: {
    visitor_ip?: string
    session_id?: string
    duration_seconds?: number
    user_agent?: string
    referrer?: string
  }) => withRetry(() => api.post(`/products/${id}/stats`, data)),

  // 产品启动和配置
  launchProduct: (id: number) => 
    withRetry(() => api.get(`/products/${id}/launch`)),

  getProductConfig: (id: number) => 
    withRetry(() => api.get(`/products/${id}/config`))
}

export default api