import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { authAPI } from '../api'
import type { LoginRequest } from '../types'

const isAuthenticated = ref(false)
const isLoading = ref(false)
const error = ref<string | null>(null)

// 检查本地存储中的 token
const token = localStorage.getItem('admin_token')
if (token) {
  isAuthenticated.value = true
}

export function useAuth() {
  const router = useRouter()

  const login = async (credentials: LoginRequest) => {
    try {
      isLoading.value = true
      error.value = null
      
      const response = await authAPI.login(credentials)
      const { access_token } = response.data
      
      // 存储 token
      localStorage.setItem('admin_token', access_token)
      isAuthenticated.value = true
      
      // 重定向到管理后台
      router.push('/admin')
      
      return true
    } catch (err: any) {
      error.value = err.response?.data?.error?.message || '登录失败，请检查用户名和密码'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const logout = async () => {
    try {
      await authAPI.logout()
    } catch (err) {
      // 即使后端登出失败，也要清除本地状态
      console.warn('后端登出失败:', err)
    } finally {
      // 清除本地状态
      localStorage.removeItem('admin_token')
      isAuthenticated.value = false
      router.push('/admin/login')
    }
  }

  const verifyToken = async () => {
    try {
      await authAPI.verify()
      return true
    } catch (err) {
      // Token 无效，清除本地状态
      localStorage.removeItem('admin_token')
      isAuthenticated.value = false
      return false
    }
  }

  const clearError = () => {
    error.value = null
  }

  return {
    // 状态
    isAuthenticated: computed(() => isAuthenticated.value),
    isLoading: computed(() => isLoading.value),
    error: computed(() => error.value),
    
    // 方法
    login,
    logout,
    verifyToken,
    clearError
  }
}