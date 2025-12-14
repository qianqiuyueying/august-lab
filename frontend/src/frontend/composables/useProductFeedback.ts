import { ref } from 'vue'
import  api  from '../../shared/api'
import type { ProductFeedbackPublic } from '../../shared/types'

export interface ProductFeedback {
  id: number
  product_id: number
  user_name?: string
  user_email?: string
  feedback_type: 'bug' | 'feature' | 'improvement' | 'general'
  rating?: number
  title: string
  content: string
  status: 'pending' | 'reviewed' | 'resolved' | 'closed'
  admin_reply?: string
  user_agent?: string
  ip_address?: string
  created_at: string
  updated_at: string
  replied_at?: string
}

export interface ProductFeedbackStats {
  product_id: number
  total_feedback: number
  average_rating?: number
  feedback_by_type: Record<string, number>
  feedback_by_status: Record<string, number>
  recent_feedback: ProductFeedback[]
}

export interface FeedbackCreateData {
  product_id: number
  user_name?: string
  user_email?: string
  feedback_type: string
  rating?: number
  title: string
  content: string
}

export interface FeedbackUpdateData {
  status?: string
  admin_reply?: string
}

export function useProductFeedback() {
  const loading = ref(false)
  const error = ref<string | null>(null)

  const createFeedback = async (
    productId: number,
    feedbackData: FeedbackCreateData
  ): Promise<ProductFeedback> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.post(`/products/${productId}/feedback`, feedbackData)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '创建反馈失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getFeedback = async (
    productId: number,
    options: {
      feedback_type?: string
      status?: string
      skip?: number
      limit?: number
    } = {}
  ): Promise<ProductFeedback[]> => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (options.feedback_type) params.append('feedback_type', options.feedback_type)
      if (options.status) params.append('status', options.status)
      if (options.skip) params.append('skip', options.skip.toString())
      if (options.limit) params.append('limit', options.limit.toString())

      const response = await api.get(`/products/${productId}/feedback?${params}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取反馈失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getFeedbackDetail = async (
    productId: number,
    feedbackId: number
  ): Promise<ProductFeedback> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/feedback/${feedbackId}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取反馈详情失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const updateFeedback = async (
    productId: number,
    feedbackId: number,
    updateData: FeedbackUpdateData
  ): Promise<ProductFeedback> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.put(`/products/${productId}/feedback/${feedbackId}`, updateData)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '更新反馈失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const deleteFeedback = async (
    productId: number,
    feedbackId: number
  ): Promise<void> => {
    loading.value = true
    error.value = null

    try {
      await api.delete(`/products/${productId}/feedback/${feedbackId}`)
    } catch (err: any) {
      error.value = err.response?.data?.detail || '删除反馈失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getFeedbackStats = async (productId: number): Promise<ProductFeedbackStats> => {
    loading.value = true
    error.value = null

    try {
      const response = await api.get(`/products/${productId}/feedback-stats`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取反馈统计失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  const getPublicFeedback = async (
    productId: number,
    options: {
      feedback_type?: string
      skip?: number
      limit?: number
    } = {}
  ): Promise<ProductFeedbackPublic[]> => {
    loading.value = true
    error.value = null

    try {
      const params = new URLSearchParams()
      if (options.feedback_type) params.append('feedback_type', options.feedback_type)
      if (options.skip) params.append('skip', options.skip.toString())
      if (options.limit) params.append('limit', options.limit.toString())

      const response = await api.get(`/products/${productId}/feedback/public?${params}`)
      return response.data
    } catch (err: any) {
      error.value = err.response?.data?.detail || '获取公开反馈失败'
      throw err
    } finally {
      loading.value = false
    }
  }

  return {
    loading,
    error,
    createFeedback,
    getFeedback,
    getFeedbackDetail,
    updateFeedback,
    deleteFeedback,
    getFeedbackStats,
    getPublicFeedback
  }
}