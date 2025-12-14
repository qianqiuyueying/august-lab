import { ref, computed, reactive, watch } from 'vue'
import { ElMessage } from 'element-plus'

// 验证规则类型
export interface ValidationRule {
  required?: boolean
  min?: number
  max?: number
  pattern?: RegExp
  validator?: (value: any) => boolean | string
  message?: string
}

// 字段验证状态
export interface FieldValidation {
  value: any
  rules: ValidationRule[]
  error: string | null
  touched: boolean
  validating: boolean
}

// 表单验证状态
export interface FormValidation {
  valid: boolean
  errors: Record<string, string>
  touched: boolean
  submitting: boolean
  submitCount: number
}

// 内置验证器
export const validators = {
  required: (message = '此字段为必填项'): ValidationRule => ({
    required: true,
    message
  }),

  minLength: (min: number, message?: string): ValidationRule => ({
    min,
    message: message || `最少需要 ${min} 个字符`
  }),

  maxLength: (max: number, message?: string): ValidationRule => ({
    max,
    message: message || `最多允许 ${max} 个字符`
  }),

  email: (message = '请输入有效的邮箱地址'): ValidationRule => ({
    pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/,
    message
  }),

  url: (message = '请输入有效的URL地址'): ValidationRule => ({
    pattern: /^https?:\/\/.+/,
    message
  }),

  phone: (message = '请输入有效的手机号码'): ValidationRule => ({
    pattern: /^1[3-9]\d{9}$/,
    message
  }),

  password: (message = '密码至少8位，包含字母和数字'): ValidationRule => ({
    pattern: /^(?=.*[A-Za-z])(?=.*\d)[A-Za-z\d@$!%*#?&]{8,}$/,
    message
  }),

  number: (message = '请输入有效的数字'): ValidationRule => ({
    validator: (value) => !isNaN(Number(value)),
    message
  }),

  integer: (message = '请输入有效的整数'): ValidationRule => ({
    validator: (value) => Number.isInteger(Number(value)),
    message
  }),

  positive: (message = '请输入正数'): ValidationRule => ({
    validator: (value) => Number(value) > 0,
    message
  }),

  range: (min: number, max: number, message?: string): ValidationRule => ({
    validator: (value) => {
      const num = Number(value)
      return num >= min && num <= max
    },
    message: message || `请输入 ${min} 到 ${max} 之间的数值`
  }),

  custom: (validator: (value: any) => boolean | string, message?: string): ValidationRule => ({
    validator: (value) => {
      const result = validator(value)
      return typeof result === 'string' ? result : result
    },
    message
  })
}

// 表单验证组合式函数
export function useFormValidation<T extends Record<string, any>>(
  initialValues: T,
  validationRules: Partial<Record<keyof T, ValidationRule[]>> = {}
) {
  // 表单数据
  const formData = reactive<T>({ ...initialValues })
  
  // 字段验证状态
  const fields = reactive<Record<keyof T, FieldValidation>>({} as any)
  
  // 表单验证状态
  const formState = reactive<FormValidation>({
    valid: false,
    errors: {},
    touched: false,
    submitting: false,
    submitCount: 0
  })

  // 防重复提交状态
  const submitCooldown = ref(false)
  const lastSubmitTime = ref(0)
  const minSubmitInterval = 1000 // 最小提交间隔（毫秒）

  // 初始化字段
  Object.keys(initialValues).forEach(key => {
    const fieldKey = key as keyof T
    ;(fields as any)[fieldKey] = {
      value: (formData as any)[fieldKey],
      rules: validationRules[fieldKey] || [],
      error: null,
      touched: false,
      validating: false
    }
  })

  // 验证单个字段
  const validateField = async (fieldName: keyof T): Promise<boolean> => {
    const field = (fields as any)[fieldName]
    if (!field) return true

    field.validating = true
    field.error = null

    const value = (formData as any)[fieldName]
    const rules = field.rules

    for (const rule of rules) {
      // 必填验证
      if (rule.required && (value === null || value === undefined || value === '')) {
        field.error = rule.message || '此字段为必填项'
        field.validating = false
        return false
      }

      // 跳过空值的其他验证（除非是必填）
      if (!rule.required && (value === null || value === undefined || value === '')) {
        continue
      }

      // 长度验证
      if (rule.min !== undefined && String(value).length < rule.min) {
        field.error = rule.message || `最少需要 ${rule.min} 个字符`
        field.validating = false
        return false
      }

      if (rule.max !== undefined && String(value).length > rule.max) {
        field.error = rule.message || `最多允许 ${rule.max} 个字符`
        field.validating = false
        return false
      }

      // 正则验证
      if (rule.pattern && !rule.pattern.test(String(value))) {
        field.error = rule.message || '格式不正确'
        field.validating = false
        return false
      }

      // 自定义验证器
      if (rule.validator) {
        const result = rule.validator(value)
        if (result !== true) {
          field.error = typeof result === 'string' ? result : (rule.message || '验证失败')
          field.validating = false
          return false
        }
      }
    }

    field.validating = false
    return true
  }

  // 验证所有字段
  const validateForm = async (): Promise<boolean> => {
    const results = await Promise.all(
      Object.keys(fields).map(key => validateField(key as keyof T))
    )
    
    const isValid = results.every(result => result)
    formState.valid = isValid
    
    // 更新错误状态
    formState.errors = {}
    Object.keys(fields).forEach(key => {
      const field = (fields as any)[key as keyof T]
      if (field.error) {
        formState.errors[key] = field.error
      }
    })

    return isValid
  }

  // 重置表单
  const resetForm = () => {
    Object.keys(initialValues).forEach(key => {
      const fieldKey = key as keyof T
      ;(formData as any)[fieldKey] = initialValues[fieldKey]
      const field = (fields as any)[fieldKey]
      if (field) {
        field.error = null
        field.touched = false
        field.validating = false
      }
    })
    
    formState.valid = false
    formState.errors = {}
    formState.touched = false
    formState.submitting = false
    formState.submitCount = 0
    submitCooldown.value = false
  }

  // 设置字段值
  const setFieldValue = (fieldName: keyof T, value: any) => {
    ;(formData as any)[fieldName] = value
    const field = (fields as any)[fieldName]
    if (field) {
      field.touched = true
      formState.touched = true
      // 实时验证
      validateField(fieldName)
    }
  }

  // 设置字段错误
  const setFieldError = (fieldName: keyof T, error: string | null) => {
    const field = (fields as any)[fieldName]
    if (field) {
      field.error = error
      if (error) {
        formState.errors[fieldName as string] = error
      } else {
        delete formState.errors[fieldName as string]
      }
    }
  }

  // 标记字段为已触摸
  const touchField = (fieldName: keyof T) => {
    const field = (fields as any)[fieldName]
    if (field) {
      field.touched = true
      formState.touched = true
    }
  }

  // 提交表单
  const submitForm = async (
    onSubmit: (data: T) => Promise<void> | void,
    options: {
      showSuccess?: boolean
      successMessage?: string
      preventDuplicate?: boolean
    } = {}
  ): Promise<boolean> => {
    const {
      showSuccess = true,
      successMessage = '提交成功',
      preventDuplicate = true
    } = options

    // 防重复提交检查
    if (preventDuplicate) {
      const now = Date.now()
      if (submitCooldown.value || (now - lastSubmitTime.value < minSubmitInterval)) {
        ElMessage.warning('请勿重复提交')
        return false
      }
    }

    formState.submitting = true
    submitCooldown.value = true

    try {
      // 验证表单
      const isValid = await validateForm()
      if (!isValid) {
        ElMessage.error('请检查表单输入')
        return false
      }

      // 执行提交
      await onSubmit({ ...formData } as T)
      
      formState.submitCount++
      lastSubmitTime.value = Date.now()

      if (showSuccess) {
        ElMessage.success(successMessage)
      }

      return true
    } catch (error: any) {
      console.error('表单提交失败:', error)
      ElMessage.error(error.message || '提交失败，请稍后重试')
      return false
    } finally {
      formState.submitting = false
      
      // 重置防重复提交状态
      setTimeout(() => {
        submitCooldown.value = false
      }, minSubmitInterval)
    }
  }

  // 监听表单数据变化
  Object.keys(formData).forEach(key => {
    watch(
      () => (formData as any)[key as keyof T],
      () => {
        const field = (fields as any)[key as keyof T]
        if (field && field.touched) {
          // 延迟验证，避免输入时频繁验证
          setTimeout(() => {
            validateField(key as keyof T)
          }, 300)
        }
      }
    )
  })

  // 计算属性
  const hasErrors = computed(() => Object.keys(formState.errors).length > 0)
  const canSubmit = computed(() => !formState.submitting && !submitCooldown.value)
  const fieldErrors = computed(() => {
    const errors: Record<string, string> = {}
    Object.keys(fields).forEach(key => {
      const field = (fields as any)[key as keyof T]
      if (field.error && field.touched) {
        errors[key] = field.error
      }
    })
    return errors
  })

  return {
    // 表单数据
    formData,
    
    // 验证状态
    fields,
    formState,
    
    // 计算属性
    hasErrors,
    canSubmit,
    fieldErrors,
    
    // 方法
    validateField,
    validateForm,
    resetForm,
    setFieldValue,
    setFieldError,
    touchField,
    submitForm,
    
    // 工具方法
    getFieldError: (fieldName: keyof T) => {
      const field = (fields as Record<string, FieldValidation>)[fieldName as string]
      return field?.error || null
    },
    isFieldValid: (fieldName: keyof T) => {
      const field = (fields as Record<string, FieldValidation>)[fieldName as string]
      return !field?.error
    },
    isFieldTouched: (fieldName: keyof T) => {
      const field = (fields as Record<string, FieldValidation>)[fieldName as string]
      return field?.touched || false
    },
    isFieldValidating: (fieldName: keyof T) => {
      const field = (fields as Record<string, FieldValidation>)[fieldName as string]
      return field?.validating || false
    }
  }
}

// 确认对话框组合式函数
export function useConfirmDialog() {
  const showConfirm = (
    message: string,
    title = '确认操作',
    _options: {
      confirmButtonText?: string
      cancelButtonText?: string
      type?: 'warning' | 'info' | 'success' | 'error'
    } = {}
  ): Promise<boolean> => {
    return new Promise((resolve) => {
      // 这里可以集成 Element Plus 的 MessageBox
      // 暂时使用浏览器原生确认框
      const result = confirm(`${title}\n\n${message}`)
      resolve(result)
    })
  }

  return {
    showConfirm
  }
}

export default useFormValidation