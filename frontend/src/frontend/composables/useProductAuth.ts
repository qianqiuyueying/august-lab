import { ref, computed } from 'vue'
import { api } from '../../shared/api'

export interface ProductUser {
  id: string
  username?: string
  email?: string
  display_name?: string
  avatar_url?: string
  preferences: Record<string, any>
  created_at: string
  last_active_at?: string
}

export interface ProductSession {
  id: string
  product_id: number
  user_id?: string
  session_data: Record<string, any>
  expires_at: string
  created_at: string
  updated_at: string
}

export interface ProductUserPreferences {
  theme?: 'light' | 'dark' | 'auto'
  language?: string
  notifications?: boolean
  [key: string]: any
}

export function useProductAuth() {
  const loading = ref(false)
  const error = ref<string | null>(null)
  const currentUser = ref<ProductUser | null>(null)
  const currentSession = ref<ProductSession | null>(null)

  const isAuthenticated = computed(() => !!currentUser.value)
  const isGuest = computed(() => !currentUser.value)

  const createGuestSession = async (productId: number): Promise<ProductSession> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/auth/guest-session`)
      const session = response.data
      currentSession.value = session
      return session
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建访客会话失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const authenticateUser = async (
    productId: number,
    credentials: {
      username?: string
      email?: string
      password?: string
      token?: string
    }
  ): Promise<ProductUser> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/auth/login`, credentials)
      const user = response.data.user
      const session = response.data.session
      
      currentUser.value = user
      currentSession.value = session
      
      // 存储到本地存储
      localStorage.setItem(`product_${productId}_user`, JSON.stringify(user))
      localStorage.setItem(`product_${productId}_session`, JSON.stringify(session))
      
      return user
    } catch (err: any) {
      error.value = err.response?.data?.detail || '用户认证失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const logoutUser = async (productId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      if (currentSession.value) {
        await api.post(`/products/${productId}/auth/logout`, {
          session_id: currentSession.value.id
        })
      }
      
      // 清除本地状态
      currentUser.value = null
      currentSession.value = null
      
      // 清除本地存储
      localStorage.removeItem(`product_${productId}_user`)
      localStorage.removeItem(`product_${productId}_session`)
      
    } catch (err: any) {
      error.value = err.response?.data?.detail || '登出失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const restoreSession = async (productId: number): Promise<boolean> => {
    try {
      // 从本地存储恢复
      const storedUser = localStorage.getItem(`product_${productId}_user`)
      const storedSession = localStorage.getItem(`product_${productId}_session`)
      
      if (!storedUser || !storedSession) {
        return false
      }
      
      const user = JSON.parse(storedUser)
      const session = JSON.parse(storedSession)
      
      // 验证会话是否仍然有效
      const response = await api.post(`/products/${productId}/auth/validate-session`, {
        session_id: session.id
      })
      
      if (response.data.valid) {
        currentUser.value = user
        currentSession.value = session
        return true
      } else {
        // 会话无效，清除本地存储
        localStorage.removeItem(`product_${productId}_user`)
        localStorage.removeItem(`product_${productId}_session`)
        return false
      }
    } catch (error) {
      return false
    }
  }

  const updateUserPreferences = async (
    productId: number,
    preferences: ProductUserPreferences
  ): Promise<ProductUser> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.put(`/products/${productId}/auth/preferences`, preferences)
      const updatedUser = response.data
      
      if (currentUser.value) {
        currentUser.value = updatedUser
        localStorage.setItem(`product_${productId}_user`, JSON.stringify(updatedUser))
      }
      
      return updatedUser
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新用户偏好失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getUserPreferences = async (productId: number): Promise<ProductUserPreferences> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/auth/preferences`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取用户偏好失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const syncSessionData = async (
    productId: number,
    sessionData: Record<string, any>
  ): Promise<ProductSession> => {
    loading.value = true
    error.value = null

    try {
      if (!currentSession.value) {
        throw new Error('没有活跃的会话')
      }

      const response = await api.put(`/products/${productId}/auth/session-data`, {
        session_id: currentSession.value.id,
        session_data: sessionData
      })
      
      const updatedSession = response.data
      currentSession.value = updatedSession
      localStorage.setItem(`product_${productId}_session`, JSON.stringify(updatedSession))
      
      return updatedSession
    } catch (err: any) {
      error.value = err.response?.data?.detail || '同步会话数据失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getSessionData = async (productId: number): Promise<Record<string, any>> => {
    loading.value = true
    error.value = null

    try {
      if (!currentSession.value) {
        return {}
      }

      const response = await api.get(`/products/${productId}/auth/session-data/${currentSession.value.id}`)
      return response.data.session_data || {}
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取会话数据失败'
      return {}
    } finally {
      loading.value = false
    }
  }

  const registerUser = async (
    productId: number,
    userData: {
      username?: string
      email?: string
      password?: string
      display_name?: string
    }
  ): Promise<ProductUser> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/auth/register`, userData)
      const user = response.data.user
      const session = response.data.session
      
      currentUser.value = user
      currentSession.value = session
      
      // 存储到本地存储
      localStorage.setItem(`product_${productId}_user`, JSON.stringify(user))
      localStorage.setItem(`product_${productId}_session`, JSON.stringify(session))
      
      return user
    } catch (err: any) {
      error.value = err.response?.data?.detail || '用户注册失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateUserProfile = async (
    productId: number,
    profileData: {
      display_name?: string
      avatar_url?: string
      email?: string
    }
  ): Promise<ProductUser> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.put(`/products/${productId}/auth/profile`, profileData)
      const updatedUser = response.data
      
      if (currentUser.value) {
        currentUser.value = updatedUser
        localStorage.setItem(`product_${productId}_user`, JSON.stringify(updatedUser))
      }
      
      return updatedUser
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新用户资料失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteUserAccount = async (productId: number): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api.delete(`/products/${productId}/auth/account`)
      
      // 清除本地状态
      currentUser.value = null
      currentSession.value = null
      
      // 清除本地存储
      localStorage.removeItem(`product_${productId}_user`)
      localStorage.removeItem(`product_${productId}_session`)
      
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除用户账户失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    currentUser,
    currentSession,
    isAuthenticated,
    isGuest,
    createGuestSession,
    authenticateUser,
    logoutUser,
    restoreSession,
    updateUserPreferences,
    getUserPreferences,
    syncSessionData,
    getSessionData,
    registerUser,
    updateUserProfile,
    deleteUserAccount
  }
}