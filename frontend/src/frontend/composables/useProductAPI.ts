import { ref } from 'vue'
import api from '../../shared/api'

export interface ProductAPIConfig {
  product_id: number
  api_key: string
  allowed_origins: string[]
  rate_limit: number
  permissions: string[]
}

export interface ProductAPICall {
  id: string
  product_id: number
  endpoint: string
  method: string
  timestamp: string
  response_time: number
  status_code: number
  error_message?: string
}

export interface ProductAPIToken {
  id?: number
  token: string
  full_token?: string  // 完整token，仅用于显示
  expires_at: string
  permissions: string[]
  product_id: number
  is_active?: boolean
  created_at?: string
  last_used_at?: string
  usage_count?: number
}

export function useProductAPI() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  const generateAPIToken = async (
    productId: number,
    permissions: string[] = ['read']
  ): Promise<ProductAPIToken> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/api/token`, {
        permissions
      })
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '生成API令牌失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const validateAPIToken = async (
    productId: number,
    token: string
  ): Promise<boolean> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/api/validate`, {
        token
      })
      return response.data.valid
    } catch (err: any) {
      error.value = err.response?.data?.detail || '验证API令牌失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAPITokens = async (productId: number): Promise<ProductAPIToken[]> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/api/tokens`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取API令牌列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const revokeAPIToken = async (
    productId: number,
    token: string
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api.delete(`/products/${productId}/api/token`, {
        data: { token }
      })
    } catch (err: any) {
      error.value = err.response?.data?.detail || '撤销API令牌失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAPIConfig = async (productId: number): Promise<ProductAPIConfig> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/api/config`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取API配置失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateAPIConfig = async (
    productId: number,
    config: Partial<ProductAPIConfig>
  ): Promise<ProductAPIConfig> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.put(`/products/${productId}/api/config`, config)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新API配置失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getAPICallLogs = async (
    productId: number,
    options: {
      skip?: number
      limit?: number
      endpoint?: string
      status_code?: number
    } = {}
  ): Promise<ProductAPICall[]> => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (options.skip) params.append('skip', options.skip.toString())
      if (options.limit) params.append('limit', options.limit.toString())
      if (options.endpoint) params.append('endpoint', options.endpoint)
      if (options.status_code) params.append('status_code', options.status_code.toString())

      const response = await api.get(`/products/${productId}/api/calls?${params}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取API调用日志失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const makeSecureAPICall = async (
    productId: number,
    endpoint: string,
    method: string = 'GET',
    data?: any,
    token?: string
  ): Promise<any> => {
    loading.value = true
    error.value = null

    try {
      const headers: Record<string, string> = {}
      if (token) {
        headers['Authorization'] = `Bearer ${token}`
      }

      const config = {
        method,
        url: `/products/${productId}/api/proxy/${endpoint}`,
        headers,
        ...(data && { data })
      }

      const response = await api.request(config)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || 'API调用失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    generateAPIToken,
    validateAPIToken,
    getAPITokens,
    revokeAPIToken,
    getAPIConfig,
    updateAPIConfig,
    getAPICallLogs,
    makeSecureAPICall
  }
}