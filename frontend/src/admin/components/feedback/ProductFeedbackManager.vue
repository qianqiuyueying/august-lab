<template>
  <div class="product-feedback-manager">
    <div class="manager-header">
      <div class="header-left">
        <h3 class="manager-title">
          <el-icon class="feedback-icon">
            <ChatDotRound />
          </el-icon>
          用户反馈管理
        </h3>
        <div class="feedback-stats">
          <el-tag type="info" size="small">
            总计: {{ feedbackStats?.total_feedback || 0 }}
          </el-tag>
          <el-tag type="warning" size="small">
            待处理: {{ feedbackStats?.feedback_by_status?.pending || 0 }}
          </el-tag>
          <el-tag type="success" size="small">
            已解决: {{ feedbackStats?.feedback_by_status?.resolved || 0 }}
          </el-tag>
        </div>
      </div>
      
      <div class="header-actions">
        <el-select
          v-model="selectedType"
          placeholder="反馈类型"
          size="small"
          style="width: 120px"
          clearable
          @change="handleFilterChange"
        >
          <el-option label="错误报告" value="bug" />
          <el-option label="功能建议" value="feature" />
          <el-option label="改进建议" value="improvement" />
          <el-option label="一般反馈" value="general" />
        </el-select>
        
        <el-select
          v-model="selectedStatus"
          placeholder="处理状态"
          size="small"
          style="width: 120px"
          clearable
          @change="handleFilterChange"
        >
          <el-option label="待处理" value="pending" />
          <el-option label="已查看" value="reviewed" />
          <el-option label="已解决" value="resolved" />
          <el-option label="已关闭" value="closed" />
        </el-select>
        
        <el-button @click="refreshFeedback" size="small" icon="Refresh">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 反馈统计卡片 -->
    <div v-if="feedbackStats" class="feedback-overview">
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon total">
                <el-icon><ChatDotRound /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ feedbackStats.total_feedback }}</div>
                <div class="stat-label">总反馈数</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon rating">
                <el-icon><Star /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">
                  {{ feedbackStats.average_rating ? feedbackStats.average_rating.toFixed(1) : '-' }}
                </div>
                <div class="stat-label">平均评分</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon pending">
                <el-icon><Clock /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ feedbackStats.feedback_by_status.pending || 0 }}</div>
                <div class="stat-label">待处理</div>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="6">
          <el-card class="stat-card">
            <div class="stat-content">
              <div class="stat-icon resolved">
                <el-icon><CircleCheckFilled /></el-icon>
              </div>
              <div class="stat-info">
                <div class="stat-value">{{ feedbackStats.feedback_by_status.resolved || 0 }}</div>
                <div class="stat-label">已解决</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 反馈列表 -->
    <div class="feedback-list">
      <el-card>
        <template #header>
          <div class="list-header">
            <h4>反馈列表</h4>
            <div class="list-controls">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索反馈内容"
                size="small"
                style="width: 200px"
                clearable
                @input="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>
        
        <el-table
          v-loading="loading"
          :data="filteredFeedback"
          stripe
          size="small"
          max-height="600"
          @row-click="showFeedbackDetail"
        >
          <el-table-column label="类型" width="100">
            <template #default="{ row }">
              <el-tag :type="getFeedbackTypeTagType(row.feedback_type)" size="small">
                {{ getFeedbackTypeLabel(row.feedback_type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="评分" width="80">
            <template #default="{ row }">
              <el-rate
                v-if="row.rating"
                :model-value="row.rating"
                disabled
                size="small"
                :show-text="false"
              />
              <span v-else class="no-rating">-</span>
            </template>
          </el-table-column>
          
          <el-table-column label="标题" min-width="200">
            <template #default="{ row }">
              <div class="feedback-title">
                {{ row.title }}
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="用户" width="120">
            <template #default="{ row }">
              <div class="user-info">
                <div class="user-name">{{ row.user_name || '匿名用户' }}</div>
                <div v-if="row.user_email" class="user-email">{{ row.user_email }}</div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getStatusTagType(row.status)" size="small">
                {{ getStatusLabel(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="提交时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="150" fixed="right">
            <template #default="{ row }">
              <el-button-group size="small">
                <el-button
                  type="text"
                  @click.stop="showFeedbackDetail(row)"
                >
                  查看
                </el-button>
                <el-button
                  v-if="row.status === 'pending'"
                  type="text"
                  @click.stop="markAsReviewed(row)"
                >
                  标记已读
                </el-button>
                <el-button
                  type="text"
                  @click.stop="replyToFeedback(row)"
                >
                  回复
                </el-button>
              </el-button-group>
            </template>
          </el-table-column>
        </el-table>
        
        <div v-if="filteredFeedback.length === 0 && !loading" class="empty-state">
          <el-empty description="暂无反馈数据" />
        </div>
      </el-card>
    </div>
    
    <!-- 反馈详情弹窗 -->
    <el-dialog
      v-model="showDetailDialog"
      title="反馈详情"
      width="700px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedFeedback" class="feedback-detail">
        <div class="detail-header">
          <div class="feedback-meta">
            <el-tag :type="getFeedbackTypeTagType(selectedFeedback.feedback_type)" size="small">
              {{ getFeedbackTypeLabel(selectedFeedback.feedback_type) }}
            </el-tag>
            <el-tag :type="getStatusTagType(selectedFeedback.status)" size="small">
              {{ getStatusLabel(selectedFeedback.status) }}
            </el-tag>
            <el-rate
              v-if="selectedFeedback.rating"
              :model-value="selectedFeedback.rating"
              disabled
              size="small"
            />
          </div>
          <div class="feedback-time">
            {{ formatDateTime(selectedFeedback.created_at) }}
          </div>
        </div>
        
        <div class="detail-content">
          <h4>{{ selectedFeedback.title }}</h4>
          <div class="feedback-content">
            {{ selectedFeedback.content }}
          </div>
        </div>
        
        <div class="user-info-section">
          <h5>用户信息</h5>
          <div class="user-details">
            <div class="detail-item">
              <span class="label">姓名:</span>
              <span>{{ selectedFeedback.user_name || '未提供' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">邮箱:</span>
              <span>{{ selectedFeedback.user_email || '未提供' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">IP地址:</span>
              <span>{{ selectedFeedback.ip_address || '未知' }}</span>
            </div>
          </div>
        </div>
        
        <div v-if="selectedFeedback.admin_reply" class="admin-reply-section">
          <h5>管理员回复</h5>
          <div class="admin-reply">
            {{ selectedFeedback.admin_reply }}
          </div>
          <div v-if="selectedFeedback.replied_at" class="reply-time">
            回复时间: {{ formatDateTime(selectedFeedback.replied_at) }}
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showDetailDialog = false">关闭</el-button>
          <el-button
            v-if="selectedFeedback && selectedFeedback.status === 'pending'"
            type="warning"
            @click="markAsReviewed(selectedFeedback)"
          >
            标记已读
          </el-button>
          <el-button
            type="primary"
            @click="selectedFeedback && replyToFeedback(selectedFeedback)"
          >
            回复反馈
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 回复反馈弹窗 -->
    <el-dialog
      v-model="showReplyDialog"
      title="回复反馈"
      width="600px"
      :close-on-click-modal="false"
    >
      <div v-if="replyingFeedback" class="reply-form">
        <div class="original-feedback">
          <h4>原反馈内容</h4>
          <div class="original-title">{{ replyingFeedback.title }}</div>
          <div class="original-content">{{ replyingFeedback.content }}</div>
        </div>
        
        <el-form
          ref="replyFormRef"
          :model="replyForm"
          :rules="replyRules"
          label-width="80px"
        >
          <el-form-item label="状态" prop="status">
            <el-select v-model="replyForm.status" style="width: 200px">
              <el-option label="已查看" value="reviewed" />
              <el-option label="已解决" value="resolved" />
              <el-option label="已关闭" value="closed" />
            </el-select>
          </el-form-item>
          
          <el-form-item label="回复内容" prop="admin_reply">
            <el-input
              v-model="replyForm.admin_reply"
              type="textarea"
              :rows="6"
              placeholder="请输入回复内容..."
              maxlength="2000"
              show-word-limit
            />
          </el-form-item>
        </el-form>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showReplyDialog = false">取消</el-button>
          <el-button
            type="primary"
            @click="submitReply"
            :loading="submittingReply"
          >
            提交回复
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  ChatDotRound,
  Star,
  Clock,
  CircleCheckFilled,
  Search,
  Refresh
} from '@element-plus/icons-vue'
import { useProductFeedback } from '../../../frontend/composables/useProductFeedback'
import type { ProductFeedback, ProductFeedbackStats } from '../../../shared/types'

interface Props {
  productId?: number
}

const props = defineProps<Props>()

// 响应式数据
const loading = ref(false)
const feedback = ref<ProductFeedback[]>([])
const feedbackStats = ref<ProductFeedbackStats | null>(null)
const selectedType = ref('')
const selectedStatus = ref('')
const searchKeyword = ref('')
const showDetailDialog = ref(false)
const showReplyDialog = ref(false)
const selectedFeedback = ref<ProductFeedback | null>(null)
const replyingFeedback = ref<ProductFeedback | null>(null)
const submittingReply = ref(false)

const replyFormRef = ref<FormInstance>()
const replyForm = reactive({
  status: '',
  admin_reply: ''
})

// 使用组合式函数
const { getFeedback, getFeedbackStats, updateFeedback } = useProductFeedback()

// 计算属性
const filteredFeedback = computed(() => {
  let filtered = feedback.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(item =>
      item.title.toLowerCase().includes(keyword) ||
      item.content.toLowerCase().includes(keyword) ||
      (item.user_name && item.user_name.toLowerCase().includes(keyword))
    )
  }
  
  return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

// 表单验证规则
const replyRules: FormRules = {
  status: [
    { required: true, message: '请选择状态', trigger: 'change' }
  ],
  admin_reply: [
    { required: true, message: '请输入回复内容', trigger: 'blur' },
    { min: 1, max: 2000, message: '回复内容长度应在1-2000个字符之间', trigger: 'blur' }
  ]
}

// 方法
const loadFeedback = async () => {
  if (!props.productId) return
  
  loading.value = true
  try {
    feedback.value = await getFeedback(props.productId, {
      feedback_type: selectedType.value || undefined,
      status: selectedStatus.value || undefined
    })
  } catch (error: any) {
    ElMessage.error(error.message || '加载反馈失败')
  } finally {
    loading.value = false
  }
}

const loadFeedbackStats = async () => {
  if (!props.productId) return
  
  try {
    feedbackStats.value = await getFeedbackStats(props.productId)
  } catch (error: any) {
    ElMessage.error(error.message || '加载统计数据失败')
  }
}

const handleFilterChange = () => {
  loadFeedback()
}

const handleSearch = () => {
  // 搜索逻辑在计算属性中处理
}

const refreshFeedback = () => {
  loadFeedback()
  loadFeedbackStats()
}

const showFeedbackDetail = (feedbackItem: ProductFeedback) => {
  selectedFeedback.value = feedbackItem
  showDetailDialog.value = true
}

const markAsReviewed = async (feedbackItem: ProductFeedback) => {
  if (!props.productId) return
  
  try {
    await updateFeedback(props.productId, feedbackItem.id, {
      status: 'reviewed'
    })
    
    ElMessage.success('已标记为已读')
    refreshFeedback()
    
    if (showDetailDialog.value) {
      showDetailDialog.value = false
    }
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const replyToFeedback = (feedbackItem: ProductFeedback) => {
  replyingFeedback.value = feedbackItem
  replyForm.status = feedbackItem.status === 'pending' ? 'reviewed' : feedbackItem.status
  replyForm.admin_reply = feedbackItem.admin_reply || ''
  showReplyDialog.value = true
  
  if (showDetailDialog.value) {
    showDetailDialog.value = false
  }
}

const submitReply = async () => {
  if (!replyFormRef.value || !replyingFeedback.value || !props.productId) return
  
  try {
    const valid = await replyFormRef.value.validate()
    if (!valid) return
    
    submittingReply.value = true
    
    await updateFeedback(props.productId, replyingFeedback.value.id, {
      status: replyForm.status,
      admin_reply: replyForm.admin_reply
    })
    
    ElMessage.success('回复提交成功')
    showReplyDialog.value = false
    refreshFeedback()
    
  } catch (error: any) {
    ElMessage.error(error.message || '提交回复失败')
  } finally {
    submittingReply.value = false
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

const getStatusTagType = (status: string) => {
  const types = {
    pending: 'warning',
    reviewed: 'info',
    resolved: 'success',
    closed: 'info'
  }
  return types[status as keyof typeof types] || 'info'
}

const getStatusLabel = (status: string) => {
  const labels = {
    pending: '待处理',
    reviewed: '已查看',
    resolved: '已解决',
    closed: '已关闭'
  }
  return labels[status as keyof typeof labels] || status
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  if (props.productId) {
    loadFeedback()
    loadFeedbackStats()
  }
})
</script>

<style scoped>
.product-feedback-manager {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.manager-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.feedback-icon {
  color: #3b82f6;
}

.feedback-stats {
  display: flex;
  gap: 8px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.feedback-overview {
  padding: 20px;
}

.stat-card {
  height: 100px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 100%;
}

.stat-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.stat-icon.total {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.stat-icon.rating {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.stat-icon.pending {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.stat-icon.resolved {
  background: linear-gradient(135deg, #10b981, #047857);
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.2;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.feedback-list {
  padding: 0 20px 20px 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.list-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.feedback-title {
  font-size: 14px;
  color: #1f2937;
  line-height: 1.4;
}

.user-info {
  font-size: 12px;
}

.user-name {
  color: #374151;
  font-weight: 500;
  margin-bottom: 2px;
}

.user-email {
  color: #6b7280;
}

.no-rating {
  color: #9ca3af;
  font-size: 12px;
}

.empty-state {
  margin-top: 20px;
}

.feedback-detail {
  padding: 0;
}

.detail-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
  padding-bottom: 12px;
  border-bottom: 1px solid #f3f4f6;
}

.feedback-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.feedback-time {
  font-size: 12px;
  color: #6b7280;
}

.detail-content h4 {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.feedback-content {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px;
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin-bottom: 20px;
}

.user-info-section,
.admin-reply-section {
  margin-bottom: 20px;
}

.user-info-section h5,
.admin-reply-section h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.user-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  display: flex;
  gap: 8px;
  font-size: 13px;
}

.detail-item .label {
  font-weight: 500;
  color: #6b7280;
  min-width: 50px;
}

.admin-reply {
  background: #f0f9ff;
  border: 1px solid #bae6fd;
  border-radius: 6px;
  padding: 12px;
  font-size: 14px;
  color: #0c4a6e;
  line-height: 1.5;
  margin-bottom: 8px;
}

.reply-time {
  font-size: 12px;
  color: #6b7280;
}

.reply-form {
  padding: 0;
}

.original-feedback {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 16px;
  margin-bottom: 20px;
}

.original-feedback h4 {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.original-title {
  font-size: 14px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 8px;
}

.original-content {
  font-size: 13px;
  color: #6b7280;
  line-height: 1.5;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .feedback-overview .el-col {
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  .manager-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .feedback-overview {
    padding: 16px;
  }
  
  .feedback-overview .el-row {
    margin: 0 -10px;
  }
  
  .feedback-overview .el-col {
    padding: 0 10px;
    margin-bottom: 20px;
  }
  
  .list-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .user-details {
    grid-template-columns: 1fr;
  }
}
</style>