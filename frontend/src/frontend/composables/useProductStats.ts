import { ref } from 'vue'
import api from '../../shared/api'
import type { ProductStatsCreateData, ProductAnalytics } from '../../shared/types'

// 会话存储
const sessionData = ref(new Map<number, {
  startTime: number
  lastActivity: number
  totalDuration: number
}>())

export function useProductStats() {
  // 记录产品访问
  const recordAccess = async (productId: number, options?: {
    referrer?: string
    user_agent?: string
  }) => {
    try {
      // 生成会话ID
      const sessionId = generateSessionId()
      
      // 获取访客IP（在实际应用中，这通常由后端处理）
      const visitorIp = await getVisitorIp()
      
      const statsData: ProductStatsCreateData = {
        product_id: productId,
        visitor_ip: visitorIp,
        session_id: sessionId,
        duration_seconds: 0, // 初始为0，后续更新
        user_agent: options?.user_agent || navigator.userAgent,
        referrer: options?.referrer || document.referrer
      }
      
      const response = await api.post(`/products/${productId}/stats`, statsData)
      
      // 记录会话开始时间
      sessionData.value.set(productId, {
        startTime: Date.now(),
        lastActivity: Date.now(),
        totalDuration: 0
      })
      
      return response.data
    } catch (err: any) {
      console.error('记录产品访问失败:', err)
      // 不抛出错误，避免影响用户体验
    }
  }
  
  // 记录使用时长
  const recordDuration = async (productId: number) => {
    const session = sessionData.value.get(productId)
    if (!session) return
    
    try {
      const currentTime = Date.now()
      const sessionDuration = Math.floor((currentTime - session.startTime) / 1000)
      
      // 更新会话数据
      session.totalDuration = sessionDuration
      session.lastActivity = currentTime
      
      // 发送时长数据到后端
      const statsData: ProductStatsCreateData = {
        product_id: productId,
        duration_seconds: sessionDuration,
        session_id: generateSessionId()
      }
      
      await api.post(`/products/${productId}/stats`, statsData)
      
      // 清除会话数据
      sessionData.value.delete(productId)
    } catch (err: any) {
      console.error('记录使用时长失败:', err)
    }
  }
  
  // 获取产品分析数据（管理员功能）
  const getProductAnalytics = async (productId: number) => {
    try {
      const response = await api.get(`/products/${productId}/analytics`)
      return response.data as ProductAnalytics
    } catch (err: any) {
      console.error('获取产品分析数据失败:', err)
      throw err
    }
  }
  
  // 记录产品日志
  const recordLog = async (
    productId: number, 
    logType: 'access' | 'error' | 'performance' | 'security',
    message: string,
    details?: Record<string, any>,
    logLevel: 'debug' | 'info' | 'warning' | 'error' = 'info'
  ) => {
    try {
      const logData = {
        product_id: productId,
        log_type: logType,
        log_level: logLevel,
        message,
        details
      }
      
      const response = await api.post(`/products/${productId}/logs`, logData)
      return response.data
    } catch (err: any) {
      console.error('记录产品日志失败:', err)
      // 不抛出错误，避免影响用户体验
    }
  }
  
  // 获取产品日志（管理员功能），禁止使用 undefined 等无效 id 发起请求
  const getProductLogs = async (
    productId: number,
    options?: {
      log_type?: string
      log_level?: string
      skip?: number
      limit?: number
    }
  ) => {
    const valid =
      productId != null &&
      productId !== undefined &&
      String(productId) !== 'undefined' &&
      !Number.isNaN(Number(productId)) &&
      Number(productId) >= 0
    if (!valid) return []
    try {
      const params = new URLSearchParams()
      
      if (options?.log_type) {
        params.append('log_type', options.log_type)
      }
      if (options?.log_level) {
        params.append('log_level', options.log_level)
      }
      if (options?.skip !== undefined) {
        params.append('skip', String(options.skip))
      }
      if (options?.limit !== undefined) {
        params.append('limit', String(options.limit))
      }
      
      const response = await api.get(`/products/${productId}/logs?${params.toString()}`)
      return response.data
    } catch (err: any) {
      console.error('获取产品日志失败:', err)
      throw err
    }
  }
  
  // 开始活动跟踪
  const startActivityTracking = (productId: number) => {
    const session = sessionData.value.get(productId)
    if (!session) return
    
    // 更新最后活动时间
    const updateActivity = () => {
      const currentSession = sessionData.value.get(productId)
      if (currentSession) {
        currentSession.lastActivity = Date.now()
      }
    }
    
    // 监听用户活动
    const events = ['mousedown', 'mousemove', 'keypress', 'scroll', 'touchstart']
    events.forEach(event => {
      document.addEventListener(event, updateActivity, { passive: true })
    })
    
    // 定期检查活动状态
    const activityInterval = setInterval(() => {
      const currentSession = sessionData.value.get(productId)
      if (!currentSession) {
        clearInterval(activityInterval)
        return
      }
      
      const inactiveTime = Date.now() - currentSession.lastActivity
      
      // 如果超过5分钟无活动，记录日志
      if (inactiveTime > 5 * 60 * 1000) {
        recordLog(productId, 'access', '用户长时间无活动', {
          inactive_duration: inactiveTime,
          total_duration: currentSession.totalDuration
        })
      }
    }, 60000) // 每分钟检查一次
    
    // 返回清理函数
    return () => {
      events.forEach(event => {
        document.removeEventListener(event, updateActivity)
      })
      clearInterval(activityInterval)
    }
  }
  
  // 记录性能指标
  const recordPerformance = async (productId: number, metrics: {
    loadTime?: number
    renderTime?: number
    interactionTime?: number
    errorCount?: number
    memoryUsage?: number
  }) => {
    try {
      await recordLog(
        productId,
        'performance',
        '性能指标记录',
        {
          ...metrics,
          timestamp: Date.now(),
          user_agent: navigator.userAgent,
          viewport: {
            width: window.innerWidth,
            height: window.innerHeight
          }
        }
      )
    } catch (err: any) {
      console.error('记录性能指标失败:', err)
    }
  }
  
  // 记录错误
  const recordError = async (productId: number, error: Error | string, context?: Record<string, any>) => {
    try {
      const errorMessage = typeof error === 'string' ? error : error.message
      const errorDetails = {
        error_message: errorMessage,
        error_stack: typeof error === 'object' ? error.stack : undefined,
        context,
        timestamp: Date.now(),
        user_agent: navigator.userAgent,
        url: window.location.href
      }
      
      await recordLog(
        productId,
        'error',
        `产品运行错误: ${errorMessage}`,
        errorDetails,
        'error'
      )
    } catch (err: any) {
      console.error('记录错误失败:', err)
    }
  }
  
  // 获取会话信息
  const getSessionInfo = (productId: number) => {
    return sessionData.value.get(productId)
  }
  
  // 清除会话数据
  const clearSession = (productId: number) => {
    sessionData.value.delete(productId)
  }
  
  // 清除所有会话数据
  const clearAllSessions = () => {
    sessionData.value.clear()
  }
  
  return {
    // 基础统计
    recordAccess,
    recordDuration,
    getProductAnalytics,
    
    // 日志记录
    recordLog,
    getProductLogs,
    recordError,
    recordPerformance,
    
    // 活动跟踪
    startActivityTracking,
    getSessionInfo,
    clearSession,
    clearAllSessions
  }
}

// 辅助函数
function generateSessionId(): string {
  return `session_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
}

async function getVisitorIp(): Promise<string> {
  try {
    // 在实际应用中，可以使用第三方服务获取IP
    // 这里返回一个占位符
    return '127.0.0.1'
  } catch {
    return '127.0.0.1'
  }
}

// 全局错误处理
if (typeof window !== 'undefined') {
  window.addEventListener('error', (event) => {
    // 可以在这里记录全局错误
    console.error('全局错误:', event.error)
  })
  
  window.addEventListener('unhandledrejection', (event) => {
    // 可以在这里记录未处理的Promise拒绝
    console.error('未处理的Promise拒绝:', event.reason)
  })
}