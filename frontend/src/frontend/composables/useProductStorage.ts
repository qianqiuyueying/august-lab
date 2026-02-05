import { ref } from 'vue'
import api from '../../shared/api'

export interface ProductStorageRecord {
  key: string
  data: any
  size_bytes: number
  access_count: number
  created_at: string
  updated_at: string
  accessed_at?: string
}

export interface ProductStorageStats {
  product_id: number
  total_records: number
  total_size_bytes: number
  records: ProductStorageRecord[]
}

export function useProductStorage() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  const storeData = async (
    productId: number,
    key: string,
    data: any
  ): Promise<ProductStorageRecord> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/data/${key}`, data)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '存储数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getData = async (
    productId: number,
    key: string
  ): Promise<ProductStorageRecord> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/data/${key}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteData = async (
    productId: number,
    key: string
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api.delete(`/products/${productId}/data/${key}`)
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const listData = async (
    productId: number,
    options: {
      skip?: number
      limit?: number
    } = {}
  ): Promise<ProductStorageStats> => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (options.skip) params.append('skip', options.skip.toString())
      if (options.limit) params.append('limit', options.limit.toString())

      const response = await api.get(`/products/${productId}/data?${params}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取数据列表失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getStorageQuota = async (productId: number): Promise<{
    used_bytes: number
    total_bytes: number
    available_bytes: number
    usage_percentage: number
  }> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/storage/quota`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取存储配额失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const clearAllData = async (productId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api.delete(`/products/${productId}/data`)
    } catch (err: any) {
      error.value = err.response?.data?.detail || '清空数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const exportData = async (productId: number): Promise<Blob> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/data/export`, {
        responseType: 'blob'
      })
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '导出数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const importData = async (
    productId: number,
    file: File
  ): Promise<{ imported_count: number; errors: string[] }> => {
    loading.value = true
    error.value = null

    try {
      const formData = new FormData()
      formData.append('file', file)

      const response = await api.post(`/products/${productId}/data/import`, formData)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '导入数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    storeData,
    getData,
    deleteData,
    listData,
    getStorageQuota,
    clearAllData,
    exportData,
    importData
  }
}