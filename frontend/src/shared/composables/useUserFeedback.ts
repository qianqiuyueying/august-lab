import { ref, computed } from 'vue'
import { ElMessage, ElNotification, ElMessageBox } from 'element-plus'

// 反馈类型定义
export interface FeedbackOptions {
  title?: string
  message: string
  type?: 'success' | 'warning' | 'info' | 'error'
  duration?: number
  showClose?: boolean
  center?: boolean
  onClose?: () => void
}

export interface NotificationOptions extends FeedbackOptions {
  position?: 'top-right' | 'top-left' | 'bottom-right' | 'bottom-left'
  offset?: number
}

export interface ConfirmOptions {
  title?: string
  message: string
  confirmButtonText?: string
  cancelButtonText?: string
  type?: 'warning' | 'info' | 'success' | 'error'
  showCancelButton?: boolean
  beforeClose?: (action: string, instance: any, done: () => void) => void
}

// 操作状态管理
class OperationManager {
  private operations = ref<Map<string, boolean>>(new Map())
  private operationMessages = ref<Map<string, string>>(new Map())

  // 开始操作
  startOperation(key: string, message?: string): void {
    this.operations.value.set(key, true)
    if (message) {
      this.operationMessages.value.set(key, message)
    }
  }

  // 结束操作
  endOperation(key: string): void {
    this.operations.value.set(key, false)
    this.operationMessages.value.delete(key)
  }

  // 检查操作状态
  isOperating(key: string): boolean {
    return this.operations.value.get(key) || false
  }

  // 获取操作消息
  getOperationMessage(key: string): string | undefined {
    return this.operationMessages.value.get(key)
  }

  // 获取所有进行中的操作
  getActiveOperations(): Array<{ key: string; message?: string }> {
    const active: Array<{ key: string; message?: string }> = []
    this.operations.value.forEach((isActive, key) => {
      if (isActive) {
        active.push({
          key,
          message: this.operationMessages.value.get(key)
        })
      }
    })
    return active
  }

  // 清除所有操作
  clearAll(): void {
    this.operations.value.clear()
    this.operationMessages.value.clear()
  }
}

const operationManager = new OperationManager()

// 用户反馈组合式函数
export function useUserFeedback() {
  // 显示消息提示
  const showMessage = (options: FeedbackOptions | string) => {
    if (typeof options === 'string') {
      ElMessage(options)
      return
    }

    ElMessage({
      message: options.message,
      type: options.type || 'info',
      duration: options.duration || 3000,
      showClose: options.showClose || false,
      center: options.center || false,
      onClose: options.onClose
    })
  }

  // 显示成功消息
  const showSuccess = (message: string, duration = 3000) => {
    ElMessage.success({
      message,
      duration,
      showClose: true
    })
  }

  // 显示错误消息
  const showError = (message: string, duration = 5000) => {
    ElMessage.error({
      message,
      duration,
      showClose: true
    })
  }

  // 显示警告消息
  const showWarning = (message: string, duration = 4000) => {
    ElMessage.warning({
      message,
      duration,
      showClose: true
    })
  }

  // 显示信息消息
  const showInfo = (message: string, duration = 3000) => {
    ElMessage.info({
      message,
      duration,
      showClose: true
    })
  }

  // 显示通知
  const showNotification = (options: NotificationOptions) => {
    ElNotification({
      title: options.title,
      message: options.message,
      type: options.type || 'info',
      duration: options.duration || 4500,
      position: options.position || 'top-right',
      offset: options.offset || 0,
      showClose: options.showClose !== false,
      onClose: options.onClose
    })
  }

  // 显示确认对话框
  const showConfirm = async (options: ConfirmOptions | string): Promise<boolean> => {
    try {
      if (typeof options === 'string') {
        await ElMessageBox.confirm(options, '确认', {
          confirmButtonText: '确定',
          cancelButtonText: '取消',
          type: 'warning'
        })
        return true
      }

      await ElMessageBox.confirm(options.message, options.title || '确认', {
        confirmButtonText: options.confirmButtonText || '确定',
        cancelButtonText: options.cancelButtonText || '取消',
        type: options.type || 'warning',
        showCancelButton: options.showCancelButton !== false,
        beforeClose: options.beforeClose
      })
      return true
    } catch {
      return false
    }
  }

  // 显示输入对话框
  const showPrompt = async (
    message: string,
    title = '输入',
    options: {
      inputValue?: string
      inputPlaceholder?: string
      inputPattern?: RegExp
      inputErrorMessage?: string
      confirmButtonText?: string
      cancelButtonText?: string
    } = {}
  ): Promise<string | null> => {
    try {
      const { value } = await ElMessageBox.prompt(message, title, {
        inputValue: options.inputValue || '',
        inputPlaceholder: options.inputPlaceholder || '',
        inputPattern: options.inputPattern,
        inputErrorMessage: options.inputErrorMessage || '输入格式不正确',
        confirmButtonText: options.confirmButtonText || '确定',
        cancelButtonText: options.cancelButtonText || '取消'
      })
      return value
    } catch {
      return null
    }
  }

  // 操作反馈（带加载状态）
  const withFeedback = async <T>(
    asyncFn: () => Promise<T>,
    options: {
      loadingMessage?: string
      successMessage?: string
      errorMessage?: string
      operationKey?: string
      showSuccess?: boolean
      showError?: boolean
    } = {}
  ): Promise<T | null> => {
    const {
      loadingMessage = '处理中...',
      successMessage = '操作成功',
      errorMessage = '操作失败',
      operationKey = `operation_${Date.now()}`,
      showSuccess = true,
      showError = true
    } = options

    try {
      // 开始操作
      operationManager.startOperation(operationKey, loadingMessage)

      // 执行异步操作
      const result = await asyncFn()

      // 显示成功消息
      if (showSuccess) {
        showSuccess(successMessage)
      }

      return result
    } catch (error: any) {
      console.error('操作失败:', error)
      
      // 显示错误消息
      if (showError) {
        const message = error.message || errorMessage
        showError(message)
      }

      return null
    } finally {
      // 结束操作
      operationManager.endOperation(operationKey)
    }
  }

  // 批量操作反馈
  const withBatchFeedback = async <T>(
    items: T[],
    asyncFn: (item: T, index: number) => Promise<void>,
    options: {
      batchSize?: number
      delay?: number
      successMessage?: string
      errorMessage?: string
      operationKey?: string
      onProgress?: (completed: number, total: number) => void
    } = {}
  ): Promise<{ success: number; failed: number; errors: Error[] }> => {
    const {
      batchSize = 5,
      delay = 100,
      successMessage = '批量操作完成',
      errorMessage = '批量操作部分失败',
      operationKey = `batch_${Date.now()}`,
      onProgress
    } = options

    const results = {
      success: 0,
      failed: 0,
      errors: [] as Error[]
    }

    try {
      operationManager.startOperation(operationKey, '批量处理中...')

      // 分批处理
      for (let i = 0; i < items.length; i += batchSize) {
        const batch = items.slice(i, i + batchSize)
        
        await Promise.allSettled(
          batch.map(async (item, batchIndex) => {
            try {
              await asyncFn(item, i + batchIndex)
              results.success++
            } catch (error) {
              results.failed++
              results.errors.push(error as Error)
            }
          })
        )

        // 进度回调
        onProgress?.(i + batch.length, items.length)

        // 延迟避免过载
        if (i + batchSize < items.length && delay > 0) {
          await new Promise(resolve => setTimeout(resolve, delay))
        }
      }

      // 显示结果消息
      if (results.failed === 0) {
        showSuccess(successMessage)
      } else if (results.success === 0) {
        showError(errorMessage)
      } else {
        showWarning(`处理完成：成功 ${results.success} 项，失败 ${results.failed} 项`)
      }

      return results
    } finally {
      operationManager.endOperation(operationKey)
    }
  }

  return {
    // 基础消息
    showMessage,
    showSuccess,
    showError,
    showWarning,
    showInfo,
    
    // 通知
    showNotification,
    
    // 对话框
    showConfirm,
    showPrompt,
    
    // 操作反馈
    withFeedback,
    withBatchFeedback,
    
    // 操作状态
    isOperating: (key: string) => operationManager.isOperating(key),
    getOperationMessage: (key: string) => operationManager.getOperationMessage(key),
    getActiveOperations: () => operationManager.getActiveOperations(),
    clearOperations: () => operationManager.clearAll()
  }
}

// 进度反馈组合式函数
export function useProgressFeedback() {
  const progress = ref(0)
  const message = ref('')
  const visible = ref(false)

  const showProgress = (initialMessage = '处理中...') => {
    progress.value = 0
    message.value = initialMessage
    visible.value = true
  }

  const updateProgress = (value: number, newMessage?: string) => {
    progress.value = Math.max(0, Math.min(100, value))
    if (newMessage) {
      message.value = newMessage
    }
  }

  const hideProgress = () => {
    visible.value = false
    progress.value = 0
    message.value = ''
  }

  const withProgress = async <T>(
    asyncFn: (updateFn: (progress: number, message?: string) => void) => Promise<T>,
    initialMessage = '处理中...'
  ): Promise<T> => {
    try {
      showProgress(initialMessage)
      return await asyncFn(updateProgress)
    } finally {
      hideProgress()
    }
  }

  return {
    progress: computed(() => progress.value),
    message: computed(() => message.value),
    visible: computed(() => visible.value),
    showProgress,
    updateProgress,
    hideProgress,
    withProgress
  }
}

export default useUserFeedback