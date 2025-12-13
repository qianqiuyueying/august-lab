import { ref, computed } from 'vue'
import { ElLoading } from 'element-plus'
import type { LoadingInstance } from 'element-plus/es/components/loading/src/loading'

// 全局加载状态管理
class LoadingManager {
  private loadingStates = ref<Map<string, boolean>>(new Map())
  private loadingInstances = new Map<string, LoadingInstance>()

  // 设置加载状态
  setLoading(key: string, loading: boolean, options?: {
    text?: string
    target?: string | HTMLElement
    fullscreen?: boolean
  }): void {
    this.loadingStates.value.set(key, loading)

    if (loading && options) {
      // 创建加载实例
      const loadingInstance = ElLoading.service({
        text: options.text || '加载中...',
        target: options.target,
        fullscreen: options.fullscreen || false,
        background: 'rgba(0, 0, 0, 0.7)'
      })
      this.loadingInstances.set(key, loadingInstance)
    } else if (!loading) {
      // 关闭加载实例
      const instance = this.loadingInstances.get(key)
      if (instance) {
        instance.close()
        this.loadingInstances.delete(key)
      }
    }
  }

  // 获取加载状态
  isLoading(key: string): boolean {
    return this.loadingStates.value.get(key) || false
  }

  // 获取全局加载状态
  get globalLoading(): boolean {
    return Array.from(this.loadingStates.value.values()).some(loading => loading)
  }

  // 清除所有加载状态
  clearAll(): void {
    this.loadingInstances.forEach(instance => instance.close())
    this.loadingInstances.clear()
    this.loadingStates.value.clear()
  }
}

const loadingManager = new LoadingManager()

// 组合式函数
export function useLoading(key?: string) {
  const loadingKey = key || `loading_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`

  const loading = computed(() => loadingManager.isLoading(loadingKey))
  const globalLoading = computed(() => loadingManager.globalLoading)

  const setLoading = (
    isLoading: boolean, 
    options?: {
      text?: string
      target?: string | HTMLElement
      fullscreen?: boolean
    }
  ) => {
    loadingManager.setLoading(loadingKey, isLoading, options)
  }

  const withLoading = async <T>(
    asyncFn: () => Promise<T>,
    options?: {
      text?: string
      target?: string | HTMLElement
      fullscreen?: boolean
    }
  ): Promise<T> => {
    try {
      setLoading(true, options)
      return await asyncFn()
    } finally {
      setLoading(false)
    }
  }

  return {
    loading,
    globalLoading,
    setLoading,
    withLoading,
    clearAll: () => loadingManager.clearAll()
  }
}

// 页面级加载状态
export function usePageLoading() {
  return useLoading('page_loading')
}

// API 请求加载状态
export function useApiLoading(apiName: string) {
  return useLoading(`api_${apiName}`)
}

export default loadingManager