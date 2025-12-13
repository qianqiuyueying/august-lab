import { ElMessage, ElMessageBox, ElNotification } from 'element-plus'
import type { MessageOptions, NotificationOptions } from 'element-plus'

export function useNotification() {
  // 成功消息
  const success = (message: string, options?: Partial<MessageOptions>) => {
    ElMessage.success({
      message,
      duration: 3000,
      ...options
    })
  }

  // 错误消息
  const error = (message: string, options?: Partial<MessageOptions>) => {
    ElMessage.error({
      message,
      duration: 5000,
      ...options
    })
  }

  // 警告消息
  const warning = (message: string, options?: Partial<MessageOptions>) => {
    ElMessage.warning({
      message,
      duration: 4000,
      ...options
    })
  }

  // 信息消息
  const info = (message: string, options?: Partial<MessageOptions>) => {
    ElMessage.info({
      message,
      duration: 3000,
      ...options
    })
  }

  // 通知
  const notify = (options: Partial<NotificationOptions>) => {
    ElNotification({
      duration: 4000,
      ...options
    })
  }

  // 成功通知
  const notifySuccess = (title: string, message?: string) => {
    notify({
      title,
      message,
      type: 'success'
    })
  }

  // 错误通知
  const notifyError = (title: string, message?: string) => {
    notify({
      title,
      message,
      type: 'error',
      duration: 0 // 错误通知不自动关闭
    })
  }

  // 确认对话框
  const confirm = async (
    message: string,
    title: string = '确认操作',
    options?: any
  ): Promise<boolean> => {
    try {
      await ElMessageBox.confirm(message, title, {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning',
        ...options
      })
      return true
    } catch {
      return false
    }
  }

  // 删除确认对话框
  const confirmDelete = async (
    itemName: string = '此项',
    customMessage?: string
  ): Promise<boolean> => {
    const message = customMessage || `确定要删除${itemName}吗？此操作不可撤销。`
    return confirm(message, '确认删除', {
      confirmButtonText: '删除',
      confirmButtonClass: 'el-button--danger',
      type: 'error'
    })
  }

  // 输入对话框
  const prompt = async (
    message: string,
    title: string = '请输入',
    options?: any
  ): Promise<string | null> => {
    try {
      const { value } = await ElMessageBox.prompt(message, title, {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        ...options
      })
      return value
    } catch {
      return null
    }
  }

  // 加载提示
  const loading = (message: string = '加载中...') => {
    return ElMessage({
      message,
      type: 'info',
      duration: 0,
      showClose: false
    })
  }

  return {
    success,
    error,
    warning,
    info,
    notify,
    notifySuccess,
    notifyError,
    confirm,
    confirmDelete,
    prompt,
    loading
  }
}