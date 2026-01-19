<template>
  <div class="product-iframe-container" :class="containerClasses">
    <!-- iframe容器 -->
    <iframe
      ref="iframeRef"
      :src="src"
      :sandbox="sanitizedSandboxOptions"
      class="product-iframe"
      :class="iframeClasses"
      @load="onLoad"
      @error="onError"
      :allow="allowAttributes"
      loading="lazy"
    ></iframe>
    
    <!-- 加载遮罩 -->
    <div v-if="isLoading" class="iframe-loading">
      <div class="loading-spinner"></div>
      <span>正在加载产品...</span>
    </div>
    
    <!-- 错误遮罩 -->
    <div v-if="hasError" class="iframe-error">
      <div class="error-content">
        <svg class="error-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
        <h3>产品加载失败</h3>
        <p>{{ errorMessage }}</p>
        <button @click="reload" class="retry-btn">重试</button>
      </div>
    </div>
    
    <!-- 安全提示 -->
    <div v-if="showNotice" class="security-notice">
      <div class="notice-content">
        <svg class="notice-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
        </svg>
        <div class="notice-text">
          <h4>安全沙箱</h4>
          <p>此产品运行在安全沙箱环境中，确保您的设备安全</p>
        </div>
        <button @click="hideSecurityNotice" class="notice-close">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useSPAHandler } from '../../composables/useSPAHandler'
import type { Product } from '../../../shared/types'

interface Props {
  src: string
  product?: Product | null
  sandboxOptions?: string
  showSecurityNotice?: boolean
  loadTimeout?: number
}

const props = withDefaults(defineProps<Props>(), {
  // 注意：同时使用 allow-scripts 和 allow-same-origin 会降低沙箱安全性
  // 这是为了支持某些产品功能（如SPA路由、跨域通信等）而必要的权衡
  // 浏览器会显示安全警告，这是预期的行为
  sandboxOptions: 'allow-scripts allow-same-origin allow-forms allow-popups allow-modals',
  showSecurityNotice: true,
  loadTimeout: 30000 // 30秒超时
})

// 清理sandbox选项，移除无效的allow-fullscreen
const sanitizedSandboxOptions = computed(() => {
  // 移除allow-fullscreen，因为它不是有效的sandbox属性
  return props.sandboxOptions
    .split(' ')
    .filter(opt => opt && opt !== 'allow-fullscreen')
    .join(' ')
})

// 如果sandbox选项包含allow-fullscreen，则添加到allow属性
const allowAttributes = computed(() => {
  const allowList: string[] = []
  
  // 检查是否需要全屏支持
  if (props.sandboxOptions.includes('allow-fullscreen')) {
    allowList.push('fullscreen')
  }
  
  // 可以根据需要添加其他allow属性
  // 例如：allowList.push('camera', 'microphone', 'geolocation')
  
  return allowList.length > 0 ? allowList.join('; ') : undefined
})

const emit = defineEmits<{
  'load': []
  'error': [message: string]
  'message': [data: any]
  'route-change': [route: any]
}>()

// 响应式数据
const iframeRef = ref<HTMLIFrameElement | null>(null)
const isLoading = ref(true)
const hasError = ref(false)
const errorMessage = ref('')
const showNotice = ref(props.showSecurityNotice)
const loadStartTime = ref(0)
let loadTimeout: number | null = null
let spaCleanup: (() => void) | null = null

// 使用SPA处理器
const { 
  initializeSPARouting, 
  detectSPAFramework, 
  clearRouteState,
  currentRoute 
} = useSPAHandler()

// 计算属性
const containerClasses = computed(() => ({
  'iframe-container--loading': isLoading.value,
  'iframe-container--error': hasError.value
}))

const iframeClasses = computed(() => ({
  'iframe--hidden': isLoading.value || hasError.value
}))

// 方法
const onLoad = async () => {
  isLoading.value = false
  hasError.value = false
  
  if (loadTimeout) {
    clearTimeout(loadTimeout)
    loadTimeout = null
  }
  
  const loadTime = Date.now() - loadStartTime.value
  console.log(`产品加载完成，耗时: ${loadTime}ms`)
  
  // 设置iframe通信
  setupIframeMessaging()
  
  // 如果是SPA产品，初始化SPA路由处理
  if (props.product && iframeRef.value) {
    await initializeSPASupport()
  }
  
  emit('load')
}

const onError = () => {
  isLoading.value = false
  hasError.value = true
  errorMessage.value = '产品加载失败，请检查网络连接或联系技术支持'
  
  if (loadTimeout) {
    clearTimeout(loadTimeout)
    loadTimeout = null
  }
  
  emit('error', errorMessage.value)
}

const reload = () => {
  if (!iframeRef.value) return
  
  isLoading.value = true
  hasError.value = false
  errorMessage.value = ''
  loadStartTime.value = Date.now()
  
  // 重新加载iframe
  iframeRef.value.src = props.src
  
  // 设置超时
  setupLoadTimeout()
}

const setupLoadTimeout = () => {
  if (loadTimeout) {
    clearTimeout(loadTimeout)
  }
  
  loadTimeout = window.setTimeout(() => {
    if (isLoading.value) {
      isLoading.value = false
      hasError.value = true
      errorMessage.value = '产品加载超时，请检查网络连接后重试'
      emit('error', errorMessage.value)
    }
  }, props.loadTimeout)
}

const setupIframeMessaging = () => {
  if (!iframeRef.value) return
  
  // 监听来自iframe的消息
  const handleMessage = (event: MessageEvent) => {
    // 验证消息来源
    if (!iframeRef.value || event.source !== iframeRef.value.contentWindow) {
      return
    }
    
    // 处理不同类型的消息
    try {
      const data = typeof event.data === 'string' ? JSON.parse(event.data) : event.data
      
      switch (data.type) {
        case 'product-ready':
          console.log('产品应用已就绪')
          break
        case 'product-error':
          console.error('产品应用错误:', data.error)
          hasError.value = true
          errorMessage.value = data.error || '产品运行时错误'
          emit('error', errorMessage.value)
          break
        case 'product-resize':
          // 处理产品请求调整大小
          handleResize(data.width, data.height)
          break
        case 'spa_route_change':
          // 处理SPA路由变化
          emit('route-change', data.route)
          break
        default:
          // 转发其他消息
          emit('message', data)
      }
    } catch (error) {
      console.warn('无法解析iframe消息:', event.data)
    }
  }
  
  window.addEventListener('message', handleMessage)
  
  // 清理函数
  return () => {
    window.removeEventListener('message', handleMessage)
  }
}

const handleResize = (width?: number, height?: number) => {
  if (!iframeRef.value) return
  
  // 根据产品请求调整iframe大小
  if (width) {
    iframeRef.value.style.width = `${width}px`
  }
  if (height) {
    iframeRef.value.style.height = `${height}px`
  }
}

const hideSecurityNotice = () => {
  showNotice.value = false
}

const sendMessageToProduct = (message: any) => {
  if (!iframeRef.value || !iframeRef.value.contentWindow) return
  
  try {
    iframeRef.value.contentWindow.postMessage(message, '*')
  } catch (error) {
    console.error('发送消息到产品失败:', error)
  }
}

// 初始化SPA支持
const initializeSPASupport = async () => {
  if (!props.product || !iframeRef.value) return
  
  try {
    // 检测SPA框架
    const framework = await detectSPAFramework(iframeRef.value)
    
    if (framework) {
      console.log(`检测到SPA框架: ${framework}`)
      
      // 初始化SPA路由处理
      spaCleanup = initializeSPARouting(props.product, iframeRef.value)
      
      // 监听路由变化
      watch(currentRoute, (route) => {
        emit('route-change', route)
      }, { deep: true })
    }
  } catch (error) {
    console.warn('SPA支持初始化失败:', error)
  }
}

// 导航到SPA路由
const navigateToSPARoute = (path: string) => {
  if (!iframeRef.value) return
  
  sendMessageToProduct({
    type: 'host_navigate',
    path: path
  })
}

// 生命周期
onMounted(() => {
  loadStartTime.value = Date.now()
  setupLoadTimeout()
})

onUnmounted(() => {
  if (loadTimeout) {
    clearTimeout(loadTimeout)
  }
  
  // 清理SPA路由处理
  if (spaCleanup) {
    spaCleanup()
  }
  
  // 清理路由状态
  clearRouteState()
})

// 监听src变化
watch(() => props.src, (newSrc) => {
  if (newSrc && iframeRef.value) {
    reload()
  }
})

// 暴露方法给父组件
defineExpose({
  reload,
  sendMessage: sendMessageToProduct,
  navigateToRoute: navigateToSPARoute,
  iframe: iframeRef,
  currentRoute
})
</script>

<style scoped>
.product-iframe-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #f9fafb;
  overflow: hidden;
}

.product-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: white;
  transition: opacity 0.3s ease;
}

.iframe--hidden {
  opacity: 0;
  pointer-events: none;
}

.iframe-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  z-index: 10;
}

.loading-spinner {
  width: 2rem;
  height: 2rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 1rem;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.iframe-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #fee2e2;
  z-index: 10;
}

.error-content {
  text-align: center;
  padding: 2rem;
  max-width: 400px;
}

.error-icon {
  width: 3rem;
  height: 3rem;
  color: #dc2626;
  margin: 0 auto 1rem;
}

.error-content h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-content p {
  color: #6b7280;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.retry-btn {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.2s;
}

.retry-btn:hover {
  background: #2563eb;
}

.security-notice {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 20;
  max-width: 300px;
}

.notice-content {
  display: flex;
  align-items: flex-start;
  gap: 0.75rem;
  background: rgba(59, 130, 246, 0.95);
  color: white;
  padding: 1rem;
  border-radius: 0.75rem;
  backdrop-filter: blur(10px);
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
}

.notice-icon {
  width: 1.5rem;
  height: 1.5rem;
  flex-shrink: 0;
  margin-top: 0.125rem;
}

.notice-text {
  flex: 1;
  min-width: 0;
}

.notice-text h4 {
  font-size: 0.875rem;
  font-weight: 600;
  margin-bottom: 0.25rem;
}

.notice-text p {
  font-size: 0.75rem;
  opacity: 0.9;
  line-height: 1.4;
  margin: 0;
}

.notice-close {
  background: none;
  border: none;
  color: white;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  transition: background-color 0.2s;
  flex-shrink: 0;
}

.notice-close:hover {
  background: rgba(255, 255, 255, 0.1);
}

.notice-close svg {
  width: 1rem;
  height: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .security-notice {
    top: 0.5rem;
    right: 0.5rem;
    left: 0.5rem;
    max-width: none;
  }
  
  .notice-content {
    padding: 0.75rem;
  }
  
  .notice-text h4 {
    font-size: 0.8125rem;
  }
  
  .notice-text p {
    font-size: 0.6875rem;
  }
}

/* 全屏模式适配 */
.iframe-container--fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: black;
}

.iframe-container--fullscreen .product-iframe {
  background: black;
}

/* 加载和错误状态动画 */
.iframe-loading,
.iframe-error {
  animation: fadeIn 0.3s ease-in-out;
}

@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}

/* 安全提示动画 */
.security-notice {
  animation: slideInRight 0.5s ease-out;
}

@keyframes slideInRight {
  from {
    transform: translateX(100%);
    opacity: 0;
  }
  to {
    transform: translateX(0);
    opacity: 1;
  }
}
</style>