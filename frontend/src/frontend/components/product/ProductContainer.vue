<template>
  <div class="product-container" :class="containerClasses">
    <!-- 产品导航栏 -->
    <ProductNavbar
      v-if="showNavbar"
      :product="product"
      :is-fullscreen="isFullscreen"
      :is-loading="isLoading"
      @toggle-fullscreen="toggleFullscreen"
      @go-back="goBack"
      @reload="reloadProduct"
      @show-info="showProductInfo = true"
      @show-feedback="showFeedbackForm = true"
    />
    
    <!-- 产品主容器 -->
    <div class="product-main" :class="mainClasses">
      <!-- 加载状态 -->
      <ProductLoader v-if="isLoading" :message="loadingMessage" />
      
      <!-- 错误状态 -->
      <ProductError
        v-else-if="error"
        :error="error"
        @retry="loadProduct"
        @go-back="goBack"
      />
      
      <!-- 产品iframe容器 -->
      <div 
        v-else-if="product && productUrl"
        class="product-iframe-wrapper"
        :style="containerStyles"
      >
        <ProductIframe
          :src="productUrl"
          :product="product"
          :sandbox-options="sandboxOptions"
          @load="onProductLoad"
          @error="onProductError"
          @message="onProductMessage"
        />
      </div>
      
      <!-- 空状态 -->
      <div v-else class="product-empty">
        <div class="empty-content">
          <svg class="empty-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          <h3>产品未找到</h3>
          <p>请检查产品ID或联系管理员</p>
          <button @click="goBack" class="btn-primary">返回</button>
        </div>
      </div>
    </div>
    
    <!-- 产品信息弹窗 -->
    <ProductInfoModal
      v-if="showProductInfo"
      :product="product"
      @close="showProductInfo = false"
    />
    
    <!-- 产品反馈表单 -->
    <ProductFeedbackForm
      v-if="product"
      v-model="showFeedbackForm"
      :product-id="product.id"
      @feedback-submitted="onFeedbackSubmitted"
    />
    
    <!-- 显示设置面板 -->
    <ProductDisplaySettings
      @settings-change="onSettingsChange"
      @display-mode-change="onDisplayModeChange"
      @container-size-change="onContainerSizeChange"
      @zoom-change="onZoomChange"
      @theme-change="onThemeChange"
    />
    
    <!-- 状态栏 -->
    <div v-if="showStatusBar" class="product-status-bar">
      <div class="status-left">
        <span v-if="product" class="product-title">{{ product.title }}</span>
        <span v-if="connectionStatus" class="connection-status" :class="connectionStatus">
          {{ connectionStatusText }}
        </span>
      </div>
      <div class="status-right">
        <span v-if="loadTime" class="load-time">加载时间: {{ loadTime }}ms</span>
        <button @click="showHelp" class="help-btn" title="帮助">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import ProductNavbar from './ProductNavbar.vue'
import ProductLoader from './ProductLoader.vue'
import ProductError from './ProductError.vue'
import ProductIframe from './ProductIframe.vue'
import ProductInfoModal from './ProductInfoModal.vue'
import ProductDisplaySettings from './ProductDisplaySettings.vue'
import ProductFeedbackForm from './ProductFeedbackForm.vue'
import { useProductStore } from '../../composables/useProductStore'
import { useProductStats } from '../../composables/useProductStats'
import { useProductState } from '../../composables/useProductState'
import { useProductTypeHandler } from '../../composables/useProductTypeHandler'
import { useGameToolHandler } from '../../composables/useGameToolHandler'
import type { Product } from '../../../shared/types'

interface Props {
  productId?: number
  showNavbar?: boolean
  showStatusBar?: boolean
  allowFullscreen?: boolean
  autoLoad?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showNavbar: true,
  showStatusBar: true,
  allowFullscreen: true,
  autoLoad: true
})

const route = useRoute()
const router = useRouter()

// 响应式数据
const product = ref<Product | null>(null)
const isLoading = ref(false)
const error = ref<string | null>(null)
const loadingMessage = ref('正在加载产品...')
const isFullscreen = ref(false)
const showProductInfo = ref(false)
const showFeedbackForm = ref(false)
const connectionStatus = ref<'connected' | 'disconnected' | 'error' | null>(null)
const loadTime = ref<number | null>(null)
const containerWidth = ref<number>(0)
const containerHeight = ref<number>(0)
const zoomLevel = ref<number>(100)
const currentTheme = ref<'light' | 'dark' | 'auto'>('auto')

// 使用组合式函数
const { fetchProduct, launchProduct } = useProductStore()
const { recordAccess, recordDuration } = useProductStats()
const { 
  startSession, 
  endSession, 
  restoreProductState, 
  saveProductState,
  updateDisplayMode,
  updateZoomLevel,
  recordInteraction 
} = useProductState()
const {
  generateSandboxOptions,
  validateCompatibility,
  optimizeLoading,
  handleProductError,
  preprocessResources
} = useProductTypeHandler()

// 计算属性
const currentProductId = computed(() => {
  return props.productId || Number(route.params.id)
})

const productUrl = computed(() => {
  if (!product.value) return null
  return `/products/${product.value.id}/${product.value.entry_file}`
})

const containerClasses = computed(() => ({
  'product-container--fullscreen': isFullscreen.value,
  'product-container--loading': isLoading.value,
  'product-container--error': !!error.value
}))

const mainClasses = computed(() => ({
  'product-main--no-navbar': !props.showNavbar,
  'product-main--no-statusbar': !props.showStatusBar,
  'product-main--fullscreen': isFullscreen.value,
  [`product-main--theme-${currentTheme.value}`]: true
}))

const containerStyles = computed(() => {
  const styles: Record<string, string> = {}
  
  if (containerWidth.value && containerHeight.value) {
    styles.width = `${containerWidth.value}px`
    styles.height = `${containerHeight.value}px`
    styles.maxWidth = '100%'
    styles.maxHeight = '100%'
    styles.margin = '0 auto'
  }
  
  if (zoomLevel.value !== 100) {
    styles.transform = `scale(${zoomLevel.value / 100})`
    styles.transformOrigin = 'center center'
  }
  
  return styles
})

const sandboxOptions = computed(() => {
  if (!product.value) return 'allow-scripts allow-same-origin'
  return generateSandboxOptions(product.value)
})

const connectionStatusText = computed(() => {
  switch (connectionStatus.value) {
    case 'connected': return '已连接'
    case 'disconnected': return '连接断开'
    case 'error': return '连接错误'
    default: return ''
  }
})

// 方法
const loadProduct = async () => {
  if (!currentProductId.value) {
    error.value = '无效的产品ID'
    return
  }
  
  isLoading.value = true
  error.value = null
  loadingMessage.value = '正在加载产品信息...'
  
  const startTime = Date.now()
  
  try {
    // 获取产品信息
    const productData = await fetchProduct(currentProductId.value)
    
    if (!productData) {
      throw new Error('产品不存在')
    }
    
    if (!productData.is_published) {
      throw new Error('产品未发布')
    }
    
    product.value = productData
    
    // 验证产品兼容性
    const compatibility = validateCompatibility(productData)
    if (!compatibility.compatible) {
      throw new Error(`产品兼容性问题: ${compatibility.issues.join(', ')}`)
    }
    
    loadingMessage.value = '正在优化资源...'
    
    // 预处理资源
    const resourceInfo = await preprocessResources(productData)
    
    loadingMessage.value = '正在启动产品...'
    
    // 启动产品
    await launchProduct(currentProductId.value)
    
    // 开始状态会话
    startSession(currentProductId.value)
    
    // 恢复之前的状态
    const savedState = restoreProductState(currentProductId.value)
    if (savedState) {
      zoomLevel.value = savedState.zoomLevel
      isFullscreen.value = savedState.displayMode === 'fullscreen'
      // 可以在这里恢复其他状态
    }
    
    // 记录访问统计
    await recordAccess(currentProductId.value, {
      referrer: document.referrer,
      user_agent: navigator.userAgent
    })
    
    loadTime.value = Date.now() - startTime
    connectionStatus.value = 'connected'
    
  } catch (err: any) {
    error.value = err.message || '加载产品失败'
    connectionStatus.value = 'error'
    console.error('产品加载失败:', err)
  } finally {
    isLoading.value = false
  }
}

const reloadProduct = () => {
  loadProduct()
}

const toggleFullscreen = () => {
  if (!props.allowFullscreen) return
  
  isFullscreen.value = !isFullscreen.value
  
  if (isFullscreen.value) {
    // 进入全屏
    document.documentElement.requestFullscreen?.()
  } else {
    // 退出全屏
    document.exitFullscreen?.()
  }
}

const goBack = () => {
  // 记录使用时长
  if (product.value) {
    recordDuration(product.value.id)
  }
  
  // 返回上一页或产品列表
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/portfolio')
  }
}

const showHelp = () => {
  ElMessage.info('使用 ESC 键退出全屏，点击导航栏按钮返回主站')
}

const onFeedbackSubmitted = () => {
  ElMessage.success('感谢您的反馈！我们会认真考虑您的建议。')
}

// 事件处理
const onProductLoad = () => {
  connectionStatus.value = 'connected'
  console.log('产品加载完成')
}

const onProductError = (errorMsg: string) => {
  error.value = errorMsg
  connectionStatus.value = 'error'
  
  // 使用类型处理器处理错误
  if (product.value) {
    handleProductError(product.value, errorMsg)
  }
}

const onProductMessage = (message: any) => {
  // 处理来自产品的消息
  console.log('产品消息:', message)
}

// 显示设置事件处理
const onSettingsChange = (settings: any) => {
  console.log('显示设置变更:', settings)
}

const onDisplayModeChange = (mode: 'normal' | 'fullscreen') => {
  if (mode === 'fullscreen' && !isFullscreen.value) {
    toggleFullscreen()
  } else if (mode === 'normal' && isFullscreen.value) {
    toggleFullscreen()
  }
  
  // 保存显示模式状态
  if (currentProductId.value) {
    updateDisplayMode(currentProductId.value, mode)
    recordInteraction(currentProductId.value, 'display_mode_change', { mode })
  }
}

const onContainerSizeChange = (size: { width: number; height: number }) => {
  containerWidth.value = size.width
  containerHeight.value = size.height
}

const onZoomChange = (level: number) => {
  zoomLevel.value = level
  
  // 保存缩放级别状态
  if (currentProductId.value) {
    updateZoomLevel(currentProductId.value, level)
    recordInteraction(currentProductId.value, 'zoom_change', { level })
  }
}

const onThemeChange = (theme: 'light' | 'dark' | 'auto') => {
  currentTheme.value = theme
  
  // 应用主题到文档根元素
  const root = document.documentElement
  root.classList.remove('theme-light', 'theme-dark')
  
  if (theme === 'auto') {
    // 根据系统偏好设置主题
    const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
    root.classList.add(prefersDark ? 'theme-dark' : 'theme-light')
  } else {
    root.classList.add(`theme-${theme}`)
  }
}

// 键盘事件处理
const handleKeydown = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && isFullscreen.value) {
    toggleFullscreen()
  }
}

// 全屏状态监听
const handleFullscreenChange = () => {
  isFullscreen.value = !!document.fullscreenElement
}

// 生命周期
onMounted(() => {
  if (props.autoLoad) {
    loadProduct()
  }
  
  // 添加事件监听
  document.addEventListener('keydown', handleKeydown)
  document.addEventListener('fullscreenchange', handleFullscreenChange)
})

onUnmounted(() => {
  // 结束状态会话
  endSession()
  
  // 记录使用时长
  if (product.value) {
    recordDuration(product.value.id)
  }
  
  // 移除事件监听
  document.removeEventListener('keydown', handleKeydown)
  document.removeEventListener('fullscreenchange', handleFullscreenChange)
})

// 监听产品ID变化
watch(currentProductId, (newId) => {
  if (newId && props.autoLoad) {
    loadProduct()
  }
})

// 暴露方法给父组件
defineExpose({
  loadProduct,
  reloadProduct,
  toggleFullscreen,
  goBack
})
</script>

<style scoped>
.product-container {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #f5f5f5;
  position: relative;
  overflow: hidden;
}

.product-container--fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: #000;
}

.product-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  position: relative;
  overflow: hidden;
}

.product-main--no-navbar {
  height: 100vh;
}

.product-main--no-statusbar {
  padding-bottom: 0;
}

.product-main--fullscreen {
  background: #000;
}

.product-main--theme-light {
  background: #ffffff;
}

.product-main--theme-dark {
  background: #1f2937;
}

.product-iframe-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
  transition: all 0.3s ease;
  overflow: hidden;
}

.product-empty {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 2rem;
}

.empty-content {
  text-align: center;
  max-width: 400px;
}

.empty-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1rem;
  color: #9ca3af;
}

.empty-content h3 {
  font-size: 1.25rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.empty-content p {
  color: #6b7280;
  margin-bottom: 1.5rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
  border: none;
  padding: 0.5rem 1rem;
  border-radius: 0.375rem;
  cursor: pointer;
  font-weight: 500;
  transition: background-color 0.2s;
}

.btn-primary:hover {
  background: #2563eb;
}

.product-status-bar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 0.5rem 1rem;
  background: #fff;
  border-top: 1px solid #e5e7eb;
  font-size: 0.875rem;
  color: #6b7280;
}

.status-left {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.product-title {
  font-weight: 500;
  color: #374151;
}

.connection-status {
  padding: 0.125rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.connection-status.connected {
  background: #dcfce7;
  color: #166534;
}

.connection-status.disconnected {
  background: #fef3c7;
  color: #92400e;
}

.connection-status.error {
  background: #fee2e2;
  color: #dc2626;
}

.status-right {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.help-btn {
  background: none;
  border: none;
  cursor: pointer;
  padding: 0.25rem;
  border-radius: 0.25rem;
  color: #6b7280;
  transition: color 0.2s;
}

.help-btn:hover {
  color: #374151;
}

.help-btn svg {
  width: 1rem;
  height: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .product-status-bar {
    padding: 0.375rem 0.75rem;
    font-size: 0.75rem;
  }
  
  .status-left,
  .status-right {
    gap: 0.5rem;
  }
  
  .load-time {
    display: none;
  }
}

/* 动画效果 */
.product-container {
  transition: all 0.3s ease;
}

.product-main {
  transition: all 0.3s ease;
}
</style>