<template>
  <div class="product-feedback-list">
    <div class="feedback-header">
      <h3 class="feedback-title">
        <el-icon class="feedback-icon"><ChatDotRound /></el-icon>
        用户反馈与回复
      </h3>
      <p class="feedback-subtitle">查看其他用户对产品的反馈和管理员的回复</p>
    </div>

    <!-- 加载状态 -->
    <div v-if="loading" class="loading-state">
      <el-icon class="is-loading"><Loading /></el-icon>
      <span>加载反馈中...</span>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="error-state">
      <el-icon><WarningFilled /></el-icon>
      <span>{{ error }}</span>
      <el-button size="small" @click="loadFeedback">重试</el-button>
    </div>

    <!-- 反馈列表 -->
    <div v-else-if="feedbackList.length > 0" class="feedback-items">
      <div
        v-for="feedback in feedbackList"
        :key="feedback.id"
        class="feedback-item"
      >
        <div class="feedback-header-item">
          <div class="feedback-meta">
            <el-tag :type="getFeedbackTypeTagType(feedback.feedback_type)" size="small">
              {{ getFeedbackTypeLabel(feedback.feedback_type) }}
            </el-tag>
            <el-rate
              v-if="feedback.rating"
              :model-value="feedback.rating"
              disabled
              size="small"
              class="feedback-rating"
            />
            <span class="feedback-time">{{ formatDate(feedback.created_at) }}</span>
          </div>
        </div>

        <div class="feedback-content-item">
          <h4 class="feedback-item-title">{{ feedback.title }}</h4>
          <p class="feedback-item-content">{{ feedback.content }}</p>
        </div>

        <!-- 管理员回复 -->
        <div v-if="feedback.admin_reply" class="admin-reply-item">
          <div class="reply-header">
            <el-icon class="reply-icon"><UserFilled /></el-icon>
            <span class="reply-label">管理员回复</span>
            <span v-if="feedback.replied_at" class="reply-time">
              {{ formatDate(feedback.replied_at) }}
            </span>
          </div>
          <div class="reply-content">{{ feedback.admin_reply }}</div>
        </div>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else class="empty-state">
      <el-icon class="empty-icon"><ChatDotRound /></el-icon>
      <p>暂无已处理的反馈</p>
      <p class="empty-hint">成为第一个提交反馈的用户吧！</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { ChatDotRound, Loading, WarningFilled, UserFilled } from '@element-plus/icons-vue'
import { useProductFeedback } from '../../composables/useProductFeedback'
import type { ProductFeedbackPublic } from '../../../shared/types'

interface Props {
  productId: number
}

const props = defineProps<Props>()

// 响应式数据
const loading = ref(false)
const error = ref<string | null>(null)
const feedbackList = ref<ProductFeedbackPublic[]>([])

// 使用组合式函数
const { getPublicFeedback } = useProductFeedback()

// 方法
const loadFeedback = async () => {
  if (!props.productId) {
    console.warn('ProductFeedbackList: productId is missing', props.productId)
    return
  }

  loading.value = true
  error.value = null

  try {
    console.log('ProductFeedbackList: Loading feedback for product', props.productId)
    const result = await getPublicFeedback(props.productId, {
      limit: 10
    })
    console.log('ProductFeedbackList: Loaded feedback', result)
    feedbackList.value = result
  } catch (err: any) {
    console.error('ProductFeedbackList: Error loading feedback', err)
    error.value = err.message || '加载反馈失败'
  } finally {
    loading.value = false
  }
}

// 工具方法
const getFeedbackTypeTagType = (type: string) => {
  const types = {
    bug: 'danger',
    feature: 'primary',
    improvement: 'warning',
    general: 'info'
  }
  return types[type as keyof typeof types] || 'info'
}

const getFeedbackTypeLabel = (type: string) => {
  const labels = {
    bug: '错误报告',
    feature: '功能建议',
    improvement: '改进建议',
    general: '一般反馈'
  }
  return labels[type as keyof typeof labels] || type
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(() => {
  if (props.productId) {
    loadFeedback()
  }
})

// 监听productId变化
watch(() => props.productId, (newId) => {
  if (newId) {
    loadFeedback()
  }
})
</script>

<style scoped>
.product-feedback-list {
  padding: 0;
  background: transparent;
  border-radius: 0;
  max-height: 450px;
  overflow-y: auto;
  min-height: 100px;
  display: block;
  visibility: visible;
}

.feedback-header {
  margin-bottom: 20px;
  padding-bottom: 16px;
  border-bottom: 2px solid #e5e7eb;
}

.feedback-title {
  display: flex;
  align-items: center;
  gap: 8px;
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.feedback-icon {
  color: #3b82f6;
}

.feedback-subtitle {
  margin: 0;
  font-size: 14px;
  color: #6b7280;
}

.loading-state,
.error-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px 20px;
  color: #6b7280;
  gap: 12px;
}

.error-state {
  color: #ef4444;
}

.empty-icon {
  font-size: 48px;
  color: #d1d5db;
}

.empty-hint {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.feedback-items {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.feedback-item {
  padding: 12px;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  background: #f9fafb;
  transition: all 0.2s;
}

.feedback-item:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.feedback-header-item {
  margin-bottom: 12px;
}

.feedback-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  flex-wrap: wrap;
}

.feedback-rating {
  margin: 0;
}

.feedback-time {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto;
}

.feedback-content-item {
  margin-bottom: 12px;
}

.feedback-item-title {
  margin: 0 0 8px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.feedback-item-content {
  margin: 0;
  font-size: 14px;
  color: #4b5563;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

.admin-reply-item {
  margin-top: 16px;
  padding: 12px;
  background: white;
  border-left: 3px solid #3b82f6;
  border-radius: 4px;
}

.reply-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.reply-icon {
  color: #3b82f6;
  font-size: 16px;
}

.reply-label {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.reply-time {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto;
}

.reply-content {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.6;
  white-space: pre-wrap;
  word-break: break-word;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .product-feedback-list {
    padding: 16px;
  }

  .feedback-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }

  .feedback-time {
    margin-left: 0;
  }
}
</style>
