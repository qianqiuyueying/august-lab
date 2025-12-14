<template>
  <div class="validated-form">
    <el-form
      ref="formRef"
      :model="formData"
      :rules="elRules"
      :label-width="labelWidth"
      :label-position="labelPosition"
      :size="size"
      :disabled="formState.submitting"
      @submit.prevent="handleSubmit"
    >
      <slot 
        :form-data="formData"
        :form-state="formState"
        :field-errors="fieldErrors"
        :set-field-value="setFieldValue"
        :touch-field="touchField"
        :validate-field="validateField"
        :can-submit="canSubmit"
        :is-submitting="formState.submitting"
      />
      
      <!-- 默认提交按钮 -->
      <el-form-item v-if="showSubmitButton" class="submit-button-container">
        <el-button
          type="primary"
          :loading="formState.submitting"
          :disabled="!canSubmit || (requireValidation && hasErrors)"
          @click="handleSubmit"
          :size="size"
        >
          <template v-if="formState.submitting">
            {{ submittingText }}
          </template>
          <template v-else>
            {{ submitText }}
          </template>
        </el-button>
        
        <el-button
          v-if="showResetButton"
          :disabled="formState.submitting"
          @click="handleReset"
          :size="size"
        >
          {{ resetText }}
        </el-button>
      </el-form-item>
    </el-form>

    <!-- 表单状态指示器 -->
    <div v-if="showStatusIndicator" class="form-status-indicator">
      <div v-if="formState.submitting" class="status-item submitting">
        <el-icon class="is-loading"><Loading /></el-icon>
        <span>{{ submittingText }}</span>
      </div>
      
      <div v-else-if="hasErrors && formState.touched" class="status-item error">
        <el-icon><WarningFilled /></el-icon>
        <span>请检查表单输入</span>
      </div>
      
      <div v-else-if="formState.valid && formState.touched" class="status-item success">
        <el-icon><SuccessFilled /></el-icon>
        <span>表单验证通过</span>
      </div>
    </div>

    <!-- 错误汇总 -->
    <div v-if="showErrorSummary && hasErrors && formState.touched" class="error-summary">
      <h4 class="error-summary-title">
        <el-icon><WarningFilled /></el-icon>
        请修正以下错误：
      </h4>
      <ul class="error-list">
        <li v-for="(error, field) in fieldErrors" :key="field" class="error-item">
          <strong>{{ getFieldLabel(field) }}:</strong> {{ error }}
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElForm, ElFormItem, ElButton, ElIcon, ElMessage } from 'element-plus'
import { Loading, WarningFilled, SuccessFilled } from '@element-plus/icons-vue'
import { useFormValidation, validators } from '../composables/useFormValidation'
import { useUserFeedback } from '../composables/useUserFeedback'
import type { ValidationRule } from '../composables/useFormValidation'
import type { FormInstance, FormRules } from 'element-plus'

interface Props {
  // 表单配置
  initialValues: Record<string, any>
  validationRules?: Record<string, ValidationRule[]>
  fieldLabels?: Record<string, string>
  
  // 外观配置
  labelWidth?: string
  labelPosition?: 'left' | 'right' | 'top'
  size?: 'large' | 'default' | 'small'
  
  // 按钮配置
  showSubmitButton?: boolean
  showResetButton?: boolean
  submitText?: string
  resetText?: string
  submittingText?: string
  
  // 验证配置
  requireValidation?: boolean
  validateOnMount?: boolean
  
  // 状态显示
  showStatusIndicator?: boolean
  showErrorSummary?: boolean
  
  // 提交配置
  preventDuplicateSubmit?: boolean
  submitSuccessMessage?: string
  autoResetOnSuccess?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  labelWidth: '120px',
  labelPosition: 'right',
  size: 'default',
  showSubmitButton: true,
  showResetButton: false,
  submitText: '提交',
  resetText: '重置',
  submittingText: '提交中...',
  requireValidation: true,
  validateOnMount: false,
  showStatusIndicator: true,
  showErrorSummary: true,
  preventDuplicateSubmit: true,
  submitSuccessMessage: '提交成功',
  autoResetOnSuccess: false
})

const emit = defineEmits<{
  submit: [data: Record<string, any>]
  reset: []
  validate: [valid: boolean, errors: Record<string, string>]
  change: [field: string, value: any]
}>()

// 表单引用
const formRef = ref<FormInstance>()

// 用户反馈
const { showSuccess, showError, showConfirm } = useUserFeedback()

// 表单验证
const {
  formData,
  formState,
  fieldErrors,
  hasErrors,
  canSubmit,
  validateForm,
  resetForm,
  setFieldValue,
  touchField,
  validateField,
  submitForm
} = useFormValidation(props.initialValues, props.validationRules)

// Element Plus 验证规则转换
const elRules = computed<FormRules>(() => {
  const rules: FormRules = {}
  
  Object.keys(props.validationRules || {}).forEach(field => {
    const fieldRules = props.validationRules![field] || []
    rules[field] = fieldRules.map(rule => ({
      required: rule.required,
      min: rule.min,
      max: rule.max,
      pattern: rule.pattern,
      message: rule.message,
      validator: rule.validator ? (validationRule, value, callback) => {
        const result = rule.validator!(value)
        if (result === true) {
          callback()
        } else {
          let errorMessage: string
          if (typeof result === 'string') {
            errorMessage = result
          } else if (typeof rule.message === 'string') {
            errorMessage = rule.message
          } else if (rule.message && typeof rule.message === 'function') {
            errorMessage = (rule.message as (value: any) => string)(value) || '验证失败'
          } else {
            errorMessage = '验证失败'
          }
          callback(new Error(errorMessage))
        }
      } : undefined,
      trigger: ['blur', 'change']
    }))
  })
  
  return rules
})

// 获取字段标签
const getFieldLabel = (field: string): string => {
  return props.fieldLabels?.[field] || field
}

// 处理提交
const handleSubmit = async () => {
  const success = await submitForm(
    async (data) => {
      emit('submit', data)
    },
    {
      showSuccess: !!props.submitSuccessMessage,
      successMessage: props.submitSuccessMessage,
      preventDuplicate: props.preventDuplicateSubmit
    }
  )

  if (success && props.autoResetOnSuccess) {
    handleReset()
  }
}

// 处理重置
const handleReset = async () => {
  const confirmed = await showConfirm('确定要重置表单吗？所有输入将被清空。')
  if (confirmed) {
    resetForm()
    formRef.value?.resetFields()
    emit('reset')
  }
}

// 监听表单数据变化
watch(
  formData,
  (newData) => {
    Object.keys(newData).forEach(field => {
      emit('change', field, newData[field])
    })
  },
  { deep: true }
)

// 监听验证状态变化
watch(
  [() => formState.valid, fieldErrors],
  ([valid, errors]) => {
    emit('validate', valid, errors)
  },
  { deep: true }
)

// 挂载时验证
onMounted(() => {
  if (props.validateOnMount) {
    validateForm()
  }
})

// 暴露方法给父组件
defineExpose({
  validate: validateForm,
  reset: handleReset,
  submit: handleSubmit,
  setFieldValue,
  getFormData: () => formData,
  getFormState: () => formState,
  getFieldErrors: () => fieldErrors.value
})
</script>

<style scoped>
.validated-form {
  @apply w-full;
}

.submit-button-container {
  @apply flex gap-3 justify-end mt-6;
}

.form-status-indicator {
  @apply mt-4 p-3 rounded-lg border;
}

.status-item {
  @apply flex items-center gap-2 text-sm;
}

.status-item.submitting {
  @apply text-blue-600 bg-blue-50 border-blue-200;
}

.status-item.error {
  @apply text-red-600 bg-red-50 border-red-200;
}

.status-item.success {
  @apply text-green-600 bg-green-50 border-green-200;
}

.error-summary {
  @apply mt-4 p-4 bg-red-50 border border-red-200 rounded-lg;
}

.error-summary-title {
  @apply flex items-center gap-2 text-red-700 font-medium mb-2;
}

.error-list {
  @apply list-none space-y-1;
}

.error-item {
  @apply text-sm text-red-600;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .submit-button-container {
    @apply flex-col;
  }
  
  .submit-button-container .el-button {
    @apply w-full;
  }
}

/* 加载状态动画 */
.is-loading {
  animation: rotating 2s linear infinite;
}

@keyframes rotating {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

/* 表单项间距 */
:deep(.el-form-item) {
  @apply mb-6;
}

:deep(.el-form-item__label) {
  @apply font-medium text-gray-700;
}

:deep(.el-form-item__error) {
  @apply text-red-500 text-xs mt-1;
}

/* 禁用状态样式 */
:deep(.el-form--disabled .el-input__inner) {
  @apply bg-gray-100 cursor-not-allowed;
}

:deep(.el-form--disabled .el-textarea__inner) {
  @apply bg-gray-100 cursor-not-allowed;
}
</style>