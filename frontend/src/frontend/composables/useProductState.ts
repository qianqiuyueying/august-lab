import { ref, computed, watch } from 'vue'
import type { Product } from '../../shared/types'

interface ProductState {
  productId: number
  scrollPosition: { x: number; y: number }
  zoomLevel: number
  displayMode: 'normal' | 'fullscreen'
  customSettings: Record<string, any>
  lastAccessed: string
  sessionDuration: number
  interactionCount: number
}

interface ProductSession {
  productId: number
  startTime: number
  endTime?: number
  duration: number
  interactions: Array<{
    type: string
    timestamp: number
    data?: any
  }>
}

// 全局状态存储
const productStates = ref<Map<number, ProductState>>(new Map())
const currentSession = ref<ProductSession | null>(null)
const sessionHistory = ref<ProductSession[]>([])

export function useProductState() {
  // 获取产品状态
  const getProductState = (productId: number): ProductState | null => {
    return productStates.value.get(productId) || null
  }
  
  // 保存产品状态
  const saveProductState = (productId: number, state: Partial<ProductState>) => {
    const existingState = productStates.value.get(productId)
    const newState: ProductState = {
      productId,
      scrollPosition: { x: 0, y: 0 },
      zoomLevel: 100,
      displayMode: 'normal',
      customSettings: {},
      lastAccessed: new Date().toISOString(),
      sessionDuration: 0,
      interactionCount: 0,
      ...existingState,
      ...state
    }
    
    productStates.value.set(productId, newState)
    persistState()
  }
  
  // 更新滚动位置
  const updateScrollPosition = (productId: number, x: number, y: number) => {
    const state = getProductState(productId)
    if (state) {
      state.scrollPosition = { x, y }
      state.lastAccessed = new Date().toISOString()
      productStates.value.set(productId, state)
      persistState()
    }
  }
  
  // 更新缩放级别
  const updateZoomLevel = (productId: number, level: number) => {
    const state = getProductState(productId)
    if (state) {
      state.zoomLevel = level
      state.lastAccessed = new Date().toISOString()
      productStates.value.set(productId, state)
      persistState()
    }
  }
  
  // 更新显示模式
  const updateDisplayMode = (productId: number, mode: 'normal' | 'fullscreen') => {
    const state = getProductState(productId)
    if (state) {
      state.displayMode = mode
      state.lastAccessed = new Date().toISOString()
      productStates.value.set(productId, state)
      persistState()
    }
  }
  
  // 更新自定义设置
  const updateCustomSettings = (productId: number, settings: Record<string, any>) => {
    const state = getProductState(productId)
    if (state) {
      state.customSettings = { ...state.customSettings, ...settings }
      state.lastAccessed = new Date().toISOString()
      productStates.value.set(productId, state)
      persistState()
    }
  }
  
  // 记录用户交互
  const recordInteraction = (productId: number, type: string, data?: any) => {
    const state = getProductState(productId)
    if (state) {
      state.interactionCount++
      state.lastAccessed = new Date().toISOString()
      productStates.value.set(productId, state)
    }
    
    // 记录到当前会话
    if (currentSession.value && currentSession.value.productId === productId) {
      currentSession.value.interactions.push({
        type,
        timestamp: Date.now(),
        data
      })
    }
  }
  
  // 开始产品会话
  const startSession = (productId: number) => {
    // 结束之前的会话
    if (currentSession.value) {
      endSession()
    }
    
    currentSession.value = {
      productId,
      startTime: Date.now(),
      duration: 0,
      interactions: []
    }
    
    // 初始化或获取产品状态
    if (!getProductState(productId)) {
      saveProductState(productId, {})
    }
  }
  
  // 结束产品会话
  const endSession = () => {
    if (currentSession.value) {
      const endTime = Date.now()
      currentSession.value.endTime = endTime
      currentSession.value.duration = endTime - currentSession.value.startTime
      
      // 更新产品状态中的会话时长
      const state = getProductState(currentSession.value.productId)
      if (state) {
        state.sessionDuration += currentSession.value.duration
        productStates.value.set(currentSession.value.productId, state)
      }
      
      // 保存到历史记录
      sessionHistory.value.push({ ...currentSession.value })
      
      // 限制历史记录数量
      if (sessionHistory.value.length > 100) {
        sessionHistory.value = sessionHistory.value.slice(-100)
      }
      
      currentSession.value = null
      persistState()
      persistSessionHistory()
    }
  }
  
  // 恢复产品状态
  const restoreProductState = (productId: number) => {
    const state = getProductState(productId)
    if (state) {
      return {
        scrollPosition: state.scrollPosition,
        zoomLevel: state.zoomLevel,
        displayMode: state.displayMode,
        customSettings: state.customSettings
      }
    }
    return null
  }
  
  // 获取产品使用历史
  const getProductHistory = (productId?: number) => {
    if (productId) {
      return sessionHistory.value.filter(session => session.productId === productId)
    }
    return sessionHistory.value
  }
  
  // 获取产品使用统计
  const getProductStats = (productId: number) => {
    const state = getProductState(productId)
    const history = getProductHistory(productId)
    
    return {
      totalSessions: history.length,
      totalDuration: state?.sessionDuration || 0,
      averageSessionDuration: history.length > 0 
        ? (state?.sessionDuration || 0) / history.length 
        : 0,
      totalInteractions: state?.interactionCount || 0,
      lastAccessed: state?.lastAccessed,
      mostUsedSettings: state?.customSettings || {}
    }
  }
  
  // 清除产品状态
  const clearProductState = (productId: number) => {
    productStates.value.delete(productId)
    persistState()
  }
  
  // 清除所有状态
  const clearAllStates = () => {
    productStates.value.clear()
    sessionHistory.value = []
    currentSession.value = null
    localStorage.removeItem('product_states')
    localStorage.removeItem('product_session_history')
  }
  
  // 持久化状态到本地存储
  const persistState = () => {
    try {
      const statesObject = Object.fromEntries(productStates.value)
      localStorage.setItem('product_states', JSON.stringify(statesObject))
    } catch (error) {
      console.error('保存产品状态失败:', error)
    }
  }
  
  // 持久化会话历史
  const persistSessionHistory = () => {
    try {
      localStorage.setItem('product_session_history', JSON.stringify(sessionHistory.value))
    } catch (error) {
      console.error('保存会话历史失败:', error)
    }
  }
  
  // 从本地存储加载状态
  const loadState = () => {
    try {
      const saved = localStorage.getItem('product_states')
      if (saved) {
        const statesObject = JSON.parse(saved)
        productStates.value = new Map(Object.entries(statesObject).map(([k, v]) => [Number(k), v as ProductState]))
      }
      
      const savedHistory = localStorage.getItem('product_session_history')
      if (savedHistory) {
        sessionHistory.value = JSON.parse(savedHistory)
      }
    } catch (error) {
      console.error('加载产品状态失败:', error)
    }
  }
  
  // 导出状态数据
  const exportStateData = () => {
    return {
      states: Object.fromEntries(productStates.value),
      sessions: sessionHistory.value,
      exportTime: new Date().toISOString()
    }
  }
  
  // 导入状态数据
  const importStateData = (data: any) => {
    try {
      if (data.states) {
        productStates.value = new Map(Object.entries(data.states).map(([k, v]) => [Number(k), v as ProductState]))
      }
      if (data.sessions) {
        sessionHistory.value = data.sessions
      }
      persistState()
      persistSessionHistory()
      return true
    } catch (error) {
      console.error('导入状态数据失败:', error)
      return false
    }
  }
  
  // 计算属性
  const hasActiveSession = computed(() => !!currentSession.value)
  const currentSessionDuration = computed(() => {
    if (currentSession.value) {
      return Date.now() - currentSession.value.startTime
    }
    return 0
  })
  
  // 监听页面卸载，自动结束会话
  const handleBeforeUnload = () => {
    endSession()
  }
  
  // 初始化
  loadState()
  
  // 添加页面卸载监听
  if (typeof window !== 'undefined') {
    window.addEventListener('beforeunload', handleBeforeUnload)
  }
  
  return {
    // 状态
    productStates: computed(() => productStates.value),
    currentSession: computed(() => currentSession.value),
    sessionHistory: computed(() => sessionHistory.value),
    hasActiveSession,
    currentSessionDuration,
    
    // 方法
    getProductState,
    saveProductState,
    updateScrollPosition,
    updateZoomLevel,
    updateDisplayMode,
    updateCustomSettings,
    recordInteraction,
    startSession,
    endSession,
    restoreProductState,
    getProductHistory,
    getProductStats,
    clearProductState,
    clearAllStates,
    exportStateData,
    importStateData
  }
}