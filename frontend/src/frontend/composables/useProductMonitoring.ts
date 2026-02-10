import { ref } from 'vue'
import api from '../../shared/api'

export interface ProductError {
  id: string
  product_id: number
  log_type: string
  log_level: string
  message: string
  details?: any
  timestamp: string
}

export interface ProductPerformanceLog {
  id: string
  product_id: number
  log_type: string
  message: string
  details?: {
    loadTime?: number
    renderTime?: number
    memoryUsage?: number
    errorCount?: number
  }
  timestamp: string
}

export interface DiagnosticResult {
  product_id: number
  timestamp: string
  overall_status: 'good' | 'warning' | 'critical'
  checks: {
    file_integrity: boolean
    entry_file_exists: boolean
    config_valid: boolean
    published_status: boolean
  }
  recommendations: string[]
}

export interface SystemStatus {
  timestamp: string
  overall_status: 'good' | 'warning' | 'critical'
  metrics: {
    total_products: number
    published_products: number
    error_rate: number
    recent_errors: number
  }
  storage: {
    total_size: number
    used_size: number
    available_size: number
  }
}

export function useProductMonitoring() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  const isValidProductId = (id: unknown): id is number =>
    id != null && id !== undefined && String(id) !== 'undefined' && !Number.isNaN(Number(id)) && Number(id) >= 0

  const getProductErrors = async (
    productId: number,
    options: {
      severity?: string
      skip?: number
      limit?: number
    } = {}
  ): Promise<ProductError[]> => {
    if (!isValidProductId(productId)) return []
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (options.severity) params.append('severity', options.severity)
      if (options.skip) params.append('skip', options.skip.toString())
      if (options.limit) params.append('limit', options.limit.toString())

      const response = await api.get(`/products/${productId}/monitoring/errors?${params}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取错误日志失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getProductPerformance = async (
    productId: number,
    options: {
      skip?: number
      limit?: number
    } = {}
  ): Promise<ProductPerformanceLog[]> => {
    if (!isValidProductId(productId)) return []
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (options.skip) params.append('skip', options.skip.toString())
      if (options.limit) params.append('limit', options.limit.toString())

      const response = await api.get(`/products/${productId}/monitoring/performance?${params}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取性能数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const runProductDiagnostic = async (productId: number): Promise<DiagnosticResult> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/monitoring/diagnostic`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '运行诊断失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSystemStatus = async (): Promise<SystemStatus> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get('/products/monitoring/system-status')
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取系统状态失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const createProductLog = async (
    productId: number,
    logData: {
      log_type: string
      log_level: string
      message: string
      details?: any
    }
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api.post(`/products/${productId}/logs`, {
        product_id: productId,
        ...logData
      })
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建日志失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getProductLogs = async (
    productId: number,
    options: {
      log_type?: string
      log_level?: string
      skip?: number
      limit?: number
    } = {}
  ): Promise<ProductError[]> => {
    if (!isValidProductId(productId)) return []
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (options.log_type) params.append('log_type', options.log_type)
      if (options.log_level) params.append('log_level', options.log_level)
      if (options.skip) params.append('skip', options.skip.toString())
      if (options.limit) params.append('limit', options.limit.toString())

      const response = await api.get(`/products/${productId}/logs?${params}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取产品日志失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const scanProductSecurity = async (productId: number) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/security/scan`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '安全扫描失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const verifyProductIntegrity = async (productId: number) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/verify`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '验证产品完整性失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getProductFiles = async (productId: number) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/files`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取产品文件失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getResourceStats = async (productId: number) => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/resources/stats`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取资源统计失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    getProductErrors,
    getProductPerformance,
    runProductDiagnostic,
    getSystemStatus,
    createProductLog,
    getProductLogs,
    scanProductSecurity,
    verifyProductIntegrity,
    getProductFiles,
    getResourceStats
  }
}