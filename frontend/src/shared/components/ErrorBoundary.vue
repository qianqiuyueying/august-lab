<template>
  <div class="error-boundary">
    <!-- 正常内容 -->
    <slot v-if="!hasError" />
    
    <!-- 错误状态 -->
    <div v-else class="error-container" :class="errorContainerClass">
      <!-- 自定义错误内容 -->
      <slot name="error" :error="error" :retry="retry" v-if="$slots.error" />
      
      <!-- 默认错误内容 -->
      <div v-else class="error-content">
        <div class="error-icon">
          <svg class="w-16 h-16 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        
        <h3 class="error-title">{{ errorTitle }}</h3>
        <p class="error-message">{{ errorMessage }}</p>
        
        <!-- 错误详情（开发环境） -->
        <details v-if="showDetails && error" class="error-details">
          <summary class="error-details-summary">错误详情</summary>
          <pre class="error-stack">{{ error.stack || error.message || error }}</pre>
        </details>
        
        <!-- 操作按钮 -->
        <div class="error-actions">
          <button 
            @click="retry" 
            class="retry-button"
            :disabled="retrying"
          >
            <svg v-if="retrying" class="animate-spin -ml-1 mr-2 h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ retrying ? '重试中...' : '重试' }}
          </button>
          
          <button 
            v-if="showReload" 
            @click="reload" 
            class="reload-button"
          >
            刷新页面
          </button>
          
          <button 
            v-if="showReport" 
            @click="reportError" 
            class="report-button"
          >
            报告问题
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onErrorCaptured, onMounted } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  fallbackTitle?: string
  fallbackMessage?: string
  showDetails?: boolean
  showReload?: boolean
  showReport?: boolean
  autoRetry?: boolean
  maxRetries?: number
  retryDelay?: number
  onError?: (error: Error) => void
  onRetry?: () => void | Promise<void>
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  fallbackTitle: '出现了一些问题',
  fallbackMessage: '页面加载失败，请稍后重试',
  showDetails: process.env.NODE_ENV === 'development',
  showReload: true,
  showReport: false,
  autoRetry: false,
  maxRetries: 3,
  retryDelay: 2000,
  theme: 'light'
})

const emit = defineEmits<{
  error: [error: Error]
  retry: []
}>()

const hasError = ref(false)
const error = ref<Error | null>(null)
const retrying = ref(false)
const retryCount = ref(0)

const errorTitle = computed(() => {
  if (error.value?.name === 'ChunkLoadError') {
    return '资源加载失败'
  }
  if (error.value?.name === 'NetworkError') {
    return '网络连接失败'
  }
  return props.fallbackTitle
})

const errorMessage = computed(() => {
  if (error.value?.name === 'ChunkLoadError') {
    return '页面资源加载失败，可能是网络问题或版本更新，请刷新页面重试'
  }
  if (error.value?.name === 'NetworkError') {
    return '网络连接异常，请检查网络设置后重试'
  }
  return error.value?.message || props.fallbackMessage
})

const errorContainerClass = computed(() => [
  'error-container',
  `error-${props.theme}`
])

// 捕获组件错误
onErrorCaptured((err: Error) => {
  handleError(err)
  return false // 阻止错误继续传播
})

// 捕获全局错误
onMounted(() => {
  // 捕获未处理的 Promise 错误
  window.addEventListener('unhandledrejection', (event) => {
    handleError(new Error(event.reason))
  })
  
  // 捕获 JavaScript 错误
  window.addEventListener('error', (event) => {
    handleError(event.error || new Error(event.message))
  })
  
  // 捕获资源加载错误
  window.addEventListener('error', (event) => {
    if (event.target !== window) {
      handleError(new Error(`资源加载失败: ${(event.target as any)?.src || (event.target as any)?.href}`))
    }
  }, true)
})

function handleError(err: Error) {
  console.error('ErrorBoundary caught error:', err)
  
  hasError.value = true
  error.value = err
  retryCount.value = 0
  
  // 触发错误回调
  props.onError?.(err)
  emit('error', err)
  
  // 自动重试
  if (props.autoRetry && retryCount.value < props.maxRetries) {
    setTimeout(() => {
      retry()
    }, props.retryDelay)
  }
}

async function retry() {
  if (retrying.value) return
  
  retrying.value = true
  retryCount.value++
  
  try {
    // 执行重试回调
    await props.onRetry?.()
    
    // 重置错误状态
    hasError.value = false
    error.value = null
    
    emit('retry')
    ElMessage.success('重试成功')
  } catch (err) {
    console.error('重试失败:', err)
    ElMessage.error('重试失败，请稍后再试')
    
    // 如果还有重试次数且开启自动重试
    if (props.autoRetry && retryCount.value < props.maxRetries) {
      setTimeout(() => {
        retry()
      }, props.retryDelay)
    }
  } finally {
    retrying.value = false
  }
}

function reload() {
  window.location.reload()
}

function reportError() {
  // 这里可以集成错误报告服务
  const errorReport = {
    message: error.value?.message,
    stack: error.value?.stack,
    url: window.location.href,
    userAgent: navigator.userAgent,
    timestamp: new Date().toISOString()
  }
  
  console.log('错误报告:', errorReport)
  ElMessage.info('错误报告已记录')
  
  // 可以发送到错误监控服务
  // errorReportingService.report(errorReport)
}

// 暴露方法给父组件
defineExpose({
  retry,
  reload,
  hasError: () => hasError.value,
  getError: () => error.value
})
</script>

<style scoped>
.error-boundary {
  @apply w-full h-full;
}

.error-container {
  @apply flex items-center justify-center min-h-96 p-8;
}

.error-container.error-dark {
  @apply bg-gray-900 text-white;
}

.error-content {
  @apply text-center max-w-md mx-auto;
}

.error-icon {
  @apply flex justify-center mb-4;
}

.error-title {
  @apply text-xl font-semibold text-gray-900 mb-2;
}

.error-dark .error-title {
  @apply text-white;
}

.error-message {
  @apply text-gray-600 mb-6 leading-relaxed;
}

.error-dark .error-message {
  @apply text-gray-300;
}

.error-details {
  @apply mt-4 text-left;
}

.error-details-summary {
  @apply cursor-pointer text-sm text-gray-500 hover:text-gray-700 mb-2;
}

.error-dark .error-details-summary {
  @apply text-gray-400 hover:text-gray-200;
}

.error-stack {
  @apply text-xs bg-gray-100 p-3 rounded border overflow-auto max-h-32 text-gray-800;
}

.error-dark .error-stack {
  @apply bg-gray-800 text-gray-200 border-gray-600;
}

.error-actions {
  @apply flex flex-col sm:flex-row gap-3 justify-center items-center;
}

.retry-button {
  @apply inline-flex items-center px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-colors;
}

.reload-button {
  @apply inline-flex items-center px-4 py-2 bg-gray-600 text-white rounded-md hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-gray-500 focus:ring-offset-2 transition-colors;
}

.report-button {
  @apply inline-flex items-center px-4 py-2 bg-orange-600 text-white rounded-md hover:bg-orange-700 focus:outline-none focus:ring-2 focus:ring-orange-500 focus:ring-offset-2 transition-colors;
}

/* 响应式适配 */
@media (max-width: 640px) {
  .error-container {
    @apply p-4;
  }
  
  .error-content {
    @apply max-w-sm;
  }
  
  .error-actions {
    @apply flex-col w-full;
  }
  
  .retry-button,
  .reload-button,
  .report-button {
    @apply w-full justify-center;
  }
}
</style>