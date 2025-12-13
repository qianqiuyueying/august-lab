import { ref, computed } from 'vue'
import api from '../../shared/api'
import type { Product, ProductCreateData, ProductUpdateData } from '../../shared/types'

// 全局产品状态
const products = ref<Product[]>([])
const currentProduct = ref<Product | null>(null)
const loading = ref(false)
const error = ref<string | null>(null)

export function useProductStore() {
  // 计算属性
  const publishedProducts = computed(() => 
    products.value.filter(p => p.is_published)
  )
  
  const featuredProducts = computed(() => 
    publishedProducts.value.filter(p => p.is_featured)
  )
  
  const productsByType = computed(() => {
    const grouped: Record<string, Product[]> = {}
    publishedProducts.value.forEach(product => {
      if (!grouped[product.product_type]) {
        grouped[product.product_type] = []
      }
      grouped[product.product_type].push(product)
    })
    return grouped
  })
  
  // 获取产品列表
  const fetchProducts = async (options?: {
    search?: string
    product_type?: string
    published_only?: boolean
  }) => {
    loading.value = true
    error.value = null
    
    try {
      const params = new URLSearchParams()
      
      if (options?.search) {
        params.append('search', options.search)
      }
      if (options?.product_type) {
        params.append('product_type', options.product_type)
      }
      if (options?.published_only !== undefined) {
        params.append('published_only', String(options.published_only))
      }
      
      const response = await api.get(`/products?${params.toString()}`)
      products.value = response.data
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || '获取产品列表失败'
      console.error('获取产品列表失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 获取单个产品
  const fetchProduct = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      const response = await api.get(`/products/${id}`)
      const product = response.data
      
      // 更新当前产品
      currentProduct.value = product
      
      // 更新产品列表中的对应项
      const index = products.value.findIndex(p => p.id === id)
      if (index !== -1) {
        products.value[index] = product
      } else {
        products.value.push(product)
      }
      
      return product
    } catch (err: any) {
      error.value = err.response?.data?.message || '获取产品信息失败'
      console.error('获取产品信息失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 启动产品
  const launchProduct = async (id: number) => {
    try {
      const response = await api.get(`/products/${id}/launch`)
      return response.data
    } catch (err: any) {
      const errorMsg = err.response?.data?.message || '启动产品失败'
      error.value = errorMsg
      console.error('启动产品失败:', err)
      throw new Error(errorMsg)
    }
  }
  
  // 创建产品（管理员功能）
  const createProduct = async (productData: ProductCreateData) => {
    loading.value = true
    error.value = null
    
    try {
      // 确保用户已登录且有有效的token
      const token = localStorage.getItem('admin_token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      const response = await api.post('/products/', productData)
      const newProduct = response.data
    
      products.value.push(newProduct)
    
      return newProduct
    } catch (err: any) {
      error.value = err.response?.data?.message || '创建产品失败'
      console.error('创建产品失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 更新产品（管理员功能）
  const updateProduct = async (id: number, productData: ProductUpdateData) => {
    loading.value = true
    error.value = null
    
    try {
      // 确保用户已登录且有有效的token
      const token = localStorage.getItem('admin_token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      const response = await api.put(`/products/${id}`, productData)
      const updatedProduct = response.data
      
      // 更新产品列表
      const index = products.value.findIndex(p => p.id === id)
      if (index !== -1) {
        products.value[index] = updatedProduct
      }
      
      // 更新当前产品
      if (currentProduct.value?.id === id) {
        currentProduct.value = updatedProduct
      }
      
      return updatedProduct
    } catch (err: any) {
      error.value = err.response?.data?.message || '更新产品失败'
      console.error('更新产品失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 删除产品（管理员功能）
  const deleteProduct = async (id: number) => {
    loading.value = true
    error.value = null
    
    try {
      // 确保用户已登录且有有效的token
      const token = localStorage.getItem('admin_token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      await api.delete(`/products/${id}`)
      
      // 从产品列表中移除
      products.value = products.value.filter(p => p.id !== id)
      
      // 清除当前产品
      if (currentProduct.value?.id === id) {
        currentProduct.value = null
      }
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.message || '删除产品失败'
      console.error('删除产品失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 上传产品文件（管理员功能）
  const uploadProductFiles = async (id: number, file: File) => {
    loading.value = true
    error.value = null
    
    try {
      // 确保用户已登录且有有效的token
      const token = localStorage.getItem('admin_token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      const formData = new FormData()
      formData.append('file', file)
      
      const response = await api.post(`/products/${id}/upload`, formData)
      
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || '上传产品文件失败'
      console.error('上传产品文件失败:', err)
      throw err
    } finally {
      loading.value = false
    }
  }
  
  // 获取产品文件列表（管理员功能）
  const getProductFiles = async (id: number) => {
    try {
      // 确保用户已登录且有有效的token
      const token = localStorage.getItem('admin_token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      const response = await api.get(`/products/${id}/files`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || '获取产品文件失败'
      console.error('获取产品文件失败:', err)
      throw err
    }
  }
  
  // 验证产品完整性（管理员功能）
  const verifyProductIntegrity = async (id: number) => {
    try {
      // 确保用户已登录且有有效的token
      const token = localStorage.getItem('admin_token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      const response = await api.get(`/products/${id}/verify`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || '验证产品完整性失败'
      console.error('验证产品完整性失败:', err)
      throw err
    }
  }
  
  // 获取存储统计（管理员功能）
  const getStorageStats = async () => {
    try {
      // 确保用户已登录且有有效的token
      const token = localStorage.getItem('admin_token')
      if (!token) {
        throw new Error('请先登录')
      }
      
      const response = await api.get('/products/storage/stats')
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.message || '获取存储统计失败'
      console.error('获取存储统计失败:', err)
      throw err
    }
  }
  
  // 清除错误
  const clearError = () => {
    error.value = null
  }
  
  // 重置状态
  const reset = () => {
    products.value = []
    currentProduct.value = null
    loading.value = false
    error.value = null
  }
  
  return {
    // 状态
    products: readonly(products),
    currentProduct: readonly(currentProduct),
    loading: readonly(loading),
    error: readonly(error),
    
    // 计算属性
    publishedProducts,
    featuredProducts,
    productsByType,
    
    // 方法
    fetchProducts,
    fetchProduct,
    launchProduct,
    createProduct,
    updateProduct,
    deleteProduct,
    uploadProductFiles,
    getProductFiles,
    verifyProductIntegrity,
    getStorageStats,
    clearError,
    reset
  }
}

// 只读包装函数
function readonly<T>(refValue: any) {
  return computed(() => refValue.value)
}