<template>
  <div class="product-feedback-form">
    <el-dialog
      v-model="visible"
      title="产品反馈"
      width="600px"
      :close-on-click-modal="false"
      @close="handleClose"
    >
      <el-form
        ref="feedbackFormRef"
        :model="feedbackForm"
        :rules="feedbackRules"
        label-width="80px"
        @submit.prevent="submitFeedback"
      >
        <el-form-item label="反馈类型" prop="feedback_type">
          <el-select
            v-model="feedbackForm.feedback_type"
            placeholder="请选择反馈类型"
            style="width: 100%"
          >
            <el-option
              v-for="type in feedbackTypes"
              :key="type.value"
              :label="type.label"
              :value="type.value"
            >
              <div class="feedback-type-option">
                <el-icon>
                  <component :is="type.icon" />
                </el-icon>
                <span>{{ type.label }}</span>
              </div>
            </el-option>
          </el-select>
        </el-form-item>
        
        <el-form-item label="评分" prop="rating">
          <el-rate
            v-model="feedbackForm.rating"
            :colors="ratingColors"
            show-text
            :texts="ratingTexts"
          />
        </el-form-item>
        
        <el-form-item label="标题" prop="title">
          <el-input
            v-model="feedbackForm.title"
            placeholder="请输入反馈标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
        
        <el-form-item label="详细描述" prop="content">
          <el-input
            v-model="feedbackForm.content"
            type="textarea"
            :rows="6"
            placeholder="请详细描述您的反馈内容..."
            maxlength="5000"
            show-word-limit
          />
        </el-form-item>
        
        <el-divider content-position="left">
          <span class="divider-text">联系信息（可选）</span>
        </el-divider>
        
        <el-form-item label="姓名" prop="user_name">
          <el-input
            v-model="feedbackForm.user_name"
            placeholder="请输入您的姓名（可选）"
            maxlength="100"
          />
        </el-form-item>
        
        <el-form-item label="邮箱" prop="user_email">
          <el-input
            v-model="feedbackForm.user_email"
            placeholder="请输入您的邮箱（可选，用于回复）"
            maxlength="100"
          />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="handleClose">取消</el-button>
          <el-button
            type="primary"
            @click="submitFeedback"
            :loading="submitting"
          >
            提交反馈
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import {
  Warning,
  Star,
  Tools,
  ChatDotRound
} from '@element-plus/icons-vue'
import { useProductFeedback } from '../../composables/useProductFeedback'

interface Props {
  productId: number
  modelValue: boolean
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'feedback-submitted'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const feedbackFormRef = ref<FormInstance>()
const submitting = ref(false)

const feedbackForm = reactive({
  feedback_type: '',
  rating: 0,
  title: '',
  content: '',
  user_name: '',
  user_email: ''
})

// 使用组合式函数
const { createFeedback } = useProductFeedback()

// 计算属性
const visible = computed({
  get: () => props.modelValue,
  set: (value) => emit('update:modelValue', value)
})

// 配置数据
const feedbackTypes = [
  { value: 'bug', label: '错误报告', icon: Warning },
  { value: 'feature', label: '功能建议', icon: Star },
  { value: 'improvement', label: '改进建议', icon: Tools },
  { value: 'general', label: '一般反馈', icon: ChatDotRound }
]

const ratingColors = ['#F7BA2A', '#F7BA2A', '#F7BA2A']
const ratingTexts = ['很差', '较差', '一般', '很好', '非常好']

// 表单验证规则
const feedbackRules: FormRules = {
  feedback_type: [
    { required: true, message: '请选择反馈类型', trigger: 'change' }
  ],
  title: [
    { required: true, message: '请输入反馈标题', trigger: 'blur' },
    { min: 1, max: 200, message: '标题长度应在1-200个字符之间', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入反馈内容', trigger: 'blur' },
    { min: 10, max: 5000, message: '内容长度应在10-5000个字符之间', trigger: 'blur' }
  ],
  user_email: [
    { type: 'email', message: '请输入正确的邮箱地址', trigger: 'blur' }
  ]
}

// 方法
const submitFeedback = async () => {
  if (!feedbackFormRef.value) return
  
  try {
    const valid = await feedbackFormRef.value.validate()
    if (!valid) return
    
    submitting.value = true
    
    await createFeedback(props.productId, {
      product_id: props.productId,
      feedback_type: feedbackForm.feedback_type,
      rating: feedbackForm.rating || undefined,
      title: feedbackForm.title,
      content: feedbackForm.content,
      user_name: feedbackForm.user_name || undefined,
      user_email: feedbackForm.user_email || undefined
    })
    
    ElMessage.success('反馈提交成功，感谢您的建议！')
    emit('feedback-submitted')
    handleClose()
    
  } catch (error: any) {
    ElMessage.error(error.message || '提交反馈失败')
  } finally {
    submitting.value = false
  }
}

const handleClose = () => {
  visible.value = false
  resetForm()
}

const resetForm = () => {
  if (feedbackFormRef.value) {
    feedbackFormRef.value.resetFields()
  }
  
  Object.assign(feedbackForm, {
    feedback_type: '',
    rating: 0,
    title: '',
    content: '',
    user_name: '',
    user_email: ''
  })
}
</script>

<style scoped>
.product-feedback-form {
  /* 样式由 el-dialog 处理 */
}

.feedback-type-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.divider-text {
  font-size: 12px;
  color: #909399;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 评分组件样式调整 */
:deep(.el-rate) {
  display: flex;
  align-items: center;
}

:deep(.el-rate__text) {
  margin-left: 12px;
  font-size: 14px;
  color: #606266;
}

/* 表单项样式调整 */
:deep(.el-form-item__label) {
  font-weight: 500;
  color: #303133;
}

:deep(.el-textarea__inner) {
  resize: vertical;
}

/* 响应式设计 */
@media (max-width: 768px) {
  :deep(.el-dialog) {
    width: 90% !important;
    margin: 5vh auto !important;
  }
  
  :deep(.el-form-item) {
    margin-bottom: 18px;
  }
  
  :deep(.el-form-item__label) {
    width: 60px !important;
    font-size: 14px;
  }
}
</style>