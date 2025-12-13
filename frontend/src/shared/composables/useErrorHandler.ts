import { ref, computed } from 'vue'
import { ElMessage, ElNotification } from 'element-plus'

// 错误类型定义
export interface AppError {
  id: string
  type: 'network' | 'validation' | 'permission' | 'system' | 'unknown'
  code?: string
  message: string
  details?: any
  timestamp: Date
  resolved: boolean
}

// 全局错误管理器
class ErrorManager {
  private errors = ref<Map<string, AppError>>(new Map())
  private maxErrors = 50 // 最大错误记录数

  // 添加错误
  addError(error: Partial<AppError>): string {
    const id = error.id || `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    
    const appError: AppError = {
      id,
      type: error.type || 'unknown',
      code: error.code,
      message: error.message || '未知错误',
      details: error.details,
      timestamp: new Date(),
      resolved: false
    }

    this.errors.value.set(id, appError)

    // 限制错误记录数量
    if (this.errors.value.size > this.maxErrors) {
      const oldestKey = Array.from(this.errors.value.keys())[0]
      this.errors.value.delete(oldestKey)
    }

    // 根据错误类型显示不同的提示
    this.showErrorNotification(appError)

    return id
  }

  // 解决错误
  resolveError(id: string): void {
    const error = this.errors.value.get(id)
    if (error) {
      error.resolved = true
      this.errors.value.set(id, error)
    }
  }

  // 清除错误
  clearError(id: string): void {
    this.errors.value.delete(id)
  }

  // 清除所有错误
  clearAllErrors(): void {
    this.errors.value.clear()
  }

  // 获取错误列表
  getErrors(): AppError[] {
    return Array.from(this.errors.value.values()).sort(
      (a, b) => b.timestamp.getTime() - a.timestamp.getTime()
    )
  }

  // 获取未解决的错误
  getUnresolvedErrors(): AppError[] {
    return this.getErrors().filter(error => !error.resolved)
  }

  // 显示错误通知
  private showErrorNotification(error: AppError): void {
    switch (error.type) {
      case 'network':
        ElMessage.error({
          message: error.message,
          duration: 5000,
          showClose: true
        })
        break
      
      case 'validation':
        ElMessage.warning({
          message: error.message,
          duration: 3000,
          showClose: true
        })
        break
      
      case 'permission':
        ElNotification({
          title: '权限错误',
          message: error.message,
          type: 'error',
          duration: 5000
        })
        break
      
      case 'system':
        ElNotification({
          title: '系统错误',
          message: error.message,
          type: 'error',
          duration: 0 // 不自动关闭
        })
        break
      
      default:
        ElMessage.error({
          message: error.message,
          duration: 3000,
          showClose: true
        })
    }
  }
}

const errorManager = new ErrorManager()

// 组合式函数
export function useErrorHandler() {
  const errors = computed(() => errorManager.getErrors())
  const unresolvedErrors = computed(() => errorManager.getUnresolvedErrors())
  const hasErrors = computed(() => errors.value.length > 0)
  const hasUnresolvedErrors = computed(() => unresolvedErrors.value.length > 0)

  // 处理错误
  const handleError = (
    error: Error | string | Partial<AppError>,
    type?: AppError['type']
  ): string => {
    if (typeof error === 'string') {
      return errorManager.addError({
        message: error,
        type: type || 'unknown'
      })
    }

    if (error instanceof Error) {
      return errorManager.addError({
        message: error.message,
        details: {
          name: error.name,
          stack: error.stack
        },
        type: type || 'system'
      })
    }

    return errorManager.addError(error)
  }

  // 处理网络错误
  const handleNetworkError = (error: any): string => {
    let message = '网络请求失败'
    let code = 'NETWORK_ERROR'

    if (error.code === 'NETWORK_ERROR') {
      message = '网络连接失败，请检查网络设置'
    } else if (error.code === 'TIMEOUT') {
      message = '请求超时，请稍后重试'
      code = 'TIMEOUT'
    } else if (error.response) {
      message = error.message || `请求失败 (${error.response.status})`
      code = error.response.status.toString()
    }

    return handleError({
      type: 'network',
      code,
      message,
      details: error
    })
  }

  // 处理验证错误
  const handleValidationError = (
    field: string, 
    message: string, 
    value?: any
  ): string => {
    return handleError({
      type: 'validation',
      code: 'VALIDATION_ERROR',
      message: `${field}: ${message}`,
      details: { field, value }
    })
  }

  // 处理权限错误
  const handlePermissionError = (action: string, resource?: string): string => {
    const message = resource 
      ? `无权限执行操作: ${action} on ${resource}`
      : `无权限执行操作: ${action}`

    return handleError({
      type: 'permission',
      code: 'PERMISSION_DENIED',
      message,
      details: { action, resource }
    })
  }

  // 批量处理错误
  const handleErrors = (errors: Array<Error | string | Partial<AppError>>): string[] => {
    return errors.map(error => handleError(error))
  }

  // 重试机制
  const withRetry = async <T>(
    asyncFn: () => Promise<T>,
    maxRetries = 3,
    delay = 1000
  ): Promise<T> => {
    let lastError: any

    for (let i = 0; i <= maxRetries; i++) {
      try {
        return await asyncFn()
      } catch (error) {
        lastError = error
        
        if (i === maxRetries) {
          handleNetworkError(error)
          throw error
        }

        // 等待后重试
        await new Promise(resolve => setTimeout(resolve, delay * Math.pow(2, i)))
      }
    }

    throw lastError
  }

  // 安全执行函数
  const safeExecute = async <T>(
    asyncFn: () => Promise<T>,
    fallback?: T,
    onError?: (error: any) => void
  ): Promise<T | undefined> => {
    try {
      return await asyncFn()
    } catch (error) {
      const errorId = handleError(error as Error)
      onError?.(error)
      
      if (fallback !== undefined) {
        return fallback
      }
      
      return undefined
    }
  }

  return {
    // 状态
    errors,
    unresolvedErrors,
    hasErrors,
    hasUnresolvedErrors,

    // 错误处理方法
    handleError,
    handleNetworkError,
    handleValidationError,
    handlePermissionError,
    handleErrors,

    // 工具方法
    withRetry,
    safeExecute,
    resolveError: errorManager.resolveError.bind(errorManager),
    clearError: errorManager.clearError.bind(errorManager),
    clearAllErrors: errorManager.clearAllErrors.bind(errorManager)
  }
}

// 全局错误处理器
export function setupGlobalErrorHandler() {
  const { handleError, handleNetworkError } = useErrorHandler()

  // 处理未捕获的 Promise 错误
  window.addEventListener('unhandledrejection', (event) => {
    console.error('Unhandled promise rejection:', event.reason)
    handleError(event.reason, 'system')
    event.preventDefault()
  })

  // 处理 JavaScript 错误
  window.addEventListener('error', (event) => {
    console.error('Global error:', event.error)
    handleError(event.error || new Error(event.message), 'system')
  })

  // 处理资源加载错误
  window.addEventListener('error', (event) => {
    if (event.target && event.target !== window) {
      const target = event.target as any
      const resourceUrl = target.src || target.href
      if (resourceUrl) {
        handleError({
          type: 'network',
          code: 'RESOURCE_LOAD_ERROR',
          message: `资源加载失败: ${resourceUrl}`,
          details: { url: resourceUrl, tagName: target.tagName }
        })
      }
    }
  }, true)

  console.log('全局错误处理器已设置')
}

export default errorManager