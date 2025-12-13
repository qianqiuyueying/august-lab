import { ref, computed } from 'vue'
import type { Ref } from 'vue'

interface UseApiOptions {
  immediate?: boolean
  onSuccess?: (data: any) => void
  onError?: (error: any) => void
}

export function useApi<T = any>(
  apiCall: () => Promise<{ data: T }>,
  options: UseApiOptions = {}
) {
  const data = ref<T | null>(null) as Ref<T | null>
  const loading = ref(false)
  const error = ref<string | null>(null)

  const execute = async () => {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiCall()
      data.value = response.data
      
      if (options.onSuccess) {
        options.onSuccess(response.data)
      }
      
      return response.data
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || err.message || '请求失败'
      error.value = errorMessage
      
      if (options.onError) {
        options.onError(err)
      }
      
      throw err
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    data.value = null
    error.value = null
    loading.value = false
  }

  // 如果设置了 immediate，立即执行
  if (options.immediate) {
    execute()
  }

  return {
    data: computed(() => data.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    execute,
    reset
  }
}

// 专门用于列表数据的 hook
export function useApiList<T = any>(
  apiCall: () => Promise<{ data: T[] }>,
  options: UseApiOptions = {}
) {
  const { data, loading, error, execute, reset } = useApi<T[]>(apiCall, options)

  const isEmpty = computed(() => {
    return !loading.value && (!data.value || data.value.length === 0)
  })

  const count = computed(() => {
    return data.value?.length || 0
  })

  return {
    data,
    loading,
    error,
    isEmpty,
    count,
    execute,
    reset
  }
}

// 专门用于表单提交的 hook
export function useApiMutation<TData = any, TVariables = any>(
  apiCall: (variables: TVariables) => Promise<{ data: TData }>,
  options: UseApiOptions = {}
) {
  const data = ref<TData | null>(null) as Ref<TData | null>
  const loading = ref(false)
  const error = ref<string | null>(null)

  const mutate = async (variables: TVariables) => {
    try {
      loading.value = true
      error.value = null
      
      const response = await apiCall(variables)
      data.value = response.data
      
      if (options.onSuccess) {
        options.onSuccess(response.data)
      }
      
      return response.data
    } catch (err: any) {
      const errorMessage = err.response?.data?.error?.message || err.message || '操作失败'
      error.value = errorMessage
      
      if (options.onError) {
        options.onError(err)
      }
      
      throw err
    } finally {
      loading.value = false
    }
  }

  const reset = () => {
    data.value = null
    error.value = null
    loading.value = false
  }

  return {
    data: computed(() => data.value),
    loading: computed(() => loading.value),
    error: computed(() => error.value),
    mutate,
    reset
  }
}