<template>
  <div class="mobile-product-viewer" :class="viewerClasses">
    <!-- 移动端导航栏 -->
    <div class="mobile-navbar">
      <div class="navbar-left">
        <el-button
          @click="goBack"
          type="text"
          size="large"
          icon="ArrowLeft"
          class="back-button"
        />
        
        <div class="product-info">
          <h3 class="product-title">{{ product?.title || '产品' }}</h3>
          <span class="product-type">{{ getTypeLabel(product?.product_type) }}</span>
        </div>
      </div>
      
      <div class="navbar-right">
        <el-button
          @click="toggleFullscreen"
          type="text"
          size="large"
          :icon="isFullscreen ? 'Aim' : 'FullScreen'"
          class="fullscreen-button"
        />
        
        <el-dropdown @command="handleMenuCommand" trigger="click">
          <el-button type="text" size="large" icon="More" class="menu-button" />
          
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="reload" icon="Refresh">
                重新加载
              </el-dropdown-item>
              <el-dropdown-item command="share" icon="Share">
                分享产品
              </el-dropdown-item>
              <el-dropdown-item command="info" icon="InfoFilled">
                产品信息
              </el-dropdown-item>
              <el-dropdown-item command="feedback" icon="ChatDotRound">
                反馈建议
              </el-dropdown-item>
              <el-dropdown-item divided command="settings" icon="Setting">
                显示设置
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
    
    <!-- 产品内容区域 -->
    <div class="mobile-content" :style="contentStyles">
      <ResponsiveProductContainer
        :product="product"
        :show-controls="false"
        :enable-gestures="true"
        :auto-fit="autoFit"
        @scale-change="onScaleChange"
        @orientation-change="onOrientationChange"
        @gesture="onGesture"
        @error="onError"
      >
        <template #default>
          <ProductIframe
            v-if="product && productUrl"
            :src="productUrl"
            :product="product"
            :sandbox-options="sandboxOptions"
            :style="iframeStyles"
            @load="onProductLoad"
            @error="onProductError"
            @message="onProductMessage"
          />
        </template>
      </ResponsiveProductContainer>
    </div>
    
    <!-- 移动端控制栏 -->
    <div v-if="showMobileControls" class="mobile-controls">
      <div class="control-item">
        <el-button
          @click="zoomOut"
          :disabled="currentScale <= minScale"
          circle
          icon="ZoomOut"
          size="large"
        />
      </div>
      
      <div class="control-item scale-display">
        <span>{{ Math.round(currentScale * 100) }}%</span>
      </div>
      
      <div class="control-item">
        <el-button
          @click="zoomIn"
          :disabled="currentScale >= maxScale"
          circle
          icon="ZoomIn"
          size="large"
        />
      </div>
      
      <div class="control-divider" />
      
      <div class="control-item">
        <el-button
          @click="resetZoom"
          circle
          icon="Refresh"
          size="large"
        />
      </div>
      
      <div class="control-item">
        <el-button
          @click="toggleAutoFit"
          :type="autoFit ? 'primary' : ''"
          circle
          icon="FullScreen"
          size="large"
        />
      </div>
    </div>
    
    <!-- 手势提示 -->
    <div v-if="showGestureHint" class="gesture-hint">
      <div class="hint-content">
        <div class="hint-icon">
          <svg viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm-2 15l-5-5 1.41-1.41L10 14.17l7.59-7.59L19 8l-9 9z"/>
          </svg>
        </div>
        <div class="hint-text">
          <p><strong>双指缩放</strong> 调整大小</p>
          <p><strong>单指拖拽</strong> 移动位置</p>
          <p><strong>双击</strong> 重置视图</p>
        </div>
        <el-button @click="hideGestureHint" type="text" size="small">
          知道了
        </el-button>
      </div>
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="mobile-loading">
      <div class="loading-content">
        <el-icon class="loading-icon" size="48">
          <Loading />
        </el-icon>
        <p>{{ loadingText }}</p>
      </div>
    </div>
    
    <!-- 错误状态 -->
    <div v-if="error" class="mobile-error">
      <div class="error-content">
        <el-icon class="error-icon" size="48">
          <WarningFilled />
        </el-icon>
        <h3>加载失败</h3>
        <p>{{ error }}</p>
        <div class="error-actions">
          <el-button @click="retry" type="primary">重试</el-button>
          <el-button @click="goBack">返回</el-button>
        </div>
      </div>
    </div>
    
    <!-- 产品信息弹窗 -->
    <el-drawer
      v-model="showProductInfo"
      title="产品信息"
      direction="btt"
      size="60%"
    >
      <div class="product-info-content">
        <div class="info-section">
          <h4>基本信息</h4>
          <div class="info-item">
            <span class="label">名称:</span>
            <span class="value">{{ product?.title }}</span>
          </div>
          <div class="info-item">
            <span class="label">类型:</span>
            <span class="value">{{ getTypeLabel(product?.product_type) }}</span>
          </div>
          <div class="info-item">
            <span class="label">版本:</span>
            <span class="value">{{ product?.version || '1.0.0' }}</span>
          </div>
        </div>
        
        <div v-if="product?.description" class="info-section">
          <h4>产品描述</h4>
          <p class="description">{{ product.description }}</p>
        </div>
        
        <div v-if="product?.tech_stack?.length" class="info-section">
          <h4>技术栈</h4>
          <div class="tech-stack">
            <el-tag
              v-for="tech in product.tech_stack"
              :key="tech"
              size="small"
              effect="plain"
            >
              {{ tech }}
            </el-tag>
          </div>
        </div>
      </div>
    </el-drawer>
    
    <!-- 显示设置弹窗 -->
    <el-drawer
      v-model="showDisplaySettings"
      title="显示设置"
      direction="btt"
      size="50%"
    >
      <div class="display-settings-content">
        <div class="setting-item">
          <div class="setting-label">自动适应屏幕</div>
          <el-switch v-model="autoFit" />
        </div>
        
        <div class="setting-item">
          <div class="setting-label">显示控制栏</div>
          <el-switch v-model="showMobileControls" />
        </div>
        
        <div class="setting-item">
          <div class="setting-label">启用手势操作</div>
          <el-switch v-model="enableGestures" />
        </div>
        
        <div class="setting-item">
          <div class="setting-label">缩放范围</div>
          <div class="scale-range">
            <span>{{ Math.round(minScale * 100) }}%</span>
            <el-slider
              v-model="scaleRange"
              range
              :min="25"
              :max="400"
              :step="25"
              class="scale-slider"
            />
            <span>{{ Math.round(maxScale * 100) }}%</span>
          </div>
        </div>
      </div>
    </el-drawer>
    
    <!-- 分享弹窗 -->
    <el-drawer
      v-model="showShareDialog"
      title="分享产品"
      direction="btt"
      size="40%"
    >
      <div class="share-content">
        <div class="share-url">
          <el-input
            v-model="shareUrl"
            readonly
            placeholder="产品链接"
          >
            <template #append>
              <el-button @click="copyShareUrl" icon="CopyDocument">
                复制
              </el-button>
            </template>
          </el-input>
        </div>
        
        <div class="share-actions">
          <el-button @click="shareToWeChat" icon="ChatDotRound">
            微信分享
          </el-button>
          <el-button @click="shareToQQ" icon="ChatRound">
            QQ分享
          </el-button>
          <el-button @click="shareToWeibo" icon="Share">
            微博分享
          </el-button>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { 
  Loading, 
  WarningFilled, 
  ArrowLeft, 
  FullScreen, 
  Aim, 
  More,
  ZoomIn,
  ZoomOut,
  Refresh
} from '@element-plus/icons-vue'
import ResponsiveProductContainer from './ResponsiveProductContainer.vue'
import ProductIframe from './ProductIframe.vue'
import { useResponsiveDesign } from '../../composables/useResponsiveDesign'
import type { Product } from '../../../shared/types'

interface Props {
  product?: Product
  autoLoad?: boolean
}

interface Emits {
  (e: 'back'): void
  (e: 'fullscreen-change', isFullscreen: boolean): void
  (e: 'scale-change', scale: number): void
  (e: 'error', error: string): void
}

const props = withDefaults(defineProps<Props>(), {
  autoLoad: true
})

const emit = defineEmits<Emits>()

const route = useRoute()
const router = useRouter()

// 使用响应式设计
const { isMobileDevice, deviceInfo } = useResponsiveDesign()

// 响应式状态
const isFullscreen = ref(false)
const currentScale = ref(1)
const autoFit = ref(true)
const showMobileControls = ref(true)
const enableGestures = ref(true)
const minScale = ref(0.25)
const maxScale = ref(4.0)
const isLoading = ref(false)
const error = ref<string | null>(null)
const loadingText = ref('正在加载产品...')

// 弹窗状态
const showProductInfo = ref(false)
const showDisplaySettings = ref(false)
const showShareDialog = ref(false)
const showGestureHint = ref(false)

// 计算属性
const viewerClasses = computed(() => ({
  'mobile-product-viewer--fullscreen': isFullscreen.value,
  'mobile-product-viewer--loading': isLoading.value,
  'mobile-product-viewer--error': !!error.value
}))

const contentStyles = computed(() => ({
  paddingTop: isFullscreen.value ? '0' : '60px',
  paddingBottom: showMobileControls.value && !isFullscreen.value ? '80px' : '0'
}))

const iframeStyles = computed(() => ({
  width: '100%',
  height: '100%',
  border: 'none',
  borderRadius: isFullscreen.value ? '0' : '8px'
}))

const productUrl = computed(() => {
  if (!props.product) return null
  return `/products/${props.product.id}/${props.product.entry_file}`
})

const sandboxOptions = computed(() => {
  if (!props.product) return 'allow-scripts allow-same-origin'
  // 这里可以根据产品配置生成沙箱选项
  return 'allow-scripts allow-same-origin allow-forms allow-popups'
})

const shareUrl = computed(() => {
  if (!props.product) return ''
  return `${window.location.origin}/product/${props.product.id}`
})

const scaleRange = computed({
  get: () => [Math.round(minScale.value * 100), Math.round(maxScale.value * 100)],
  set: (value: number[]) => {
    minScale.value = value[0] / 100
    maxScale.value = value[1] / 100
  }
})

// 方法
const goBack = () => {
  emit('back')
  
  // 智能返回逻辑：与ProductContainer保持一致
  const referrer = document.referrer
  const currentOrigin = window.location.origin
  const hasHistory = window.history.length > 1
  const isFromSameOrigin = referrer && referrer.startsWith(currentOrigin)
  
  // 如果有历史记录且来源是当前域名，使用浏览器后退
  if (hasHistory && isFromSameOrigin) {
    router.go(-1)
    return
  }
  
  // 根据路由查询参数中的from字段返回
  const from = route.query.from as string
  if (from === 'portfolio') {
    router.push('/portfolio')
  } else if (from === 'home') {
    router.push('/')
  } else {
    // 默认返回到产品列表
    router.push({ path: '/portfolio', query: { tab: 'products' } })
  }
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
  emit('fullscreen-change', isFullscreen.value)
  
  if (isFullscreen.value) {
    document.documentElement.requestFullscreen?.()
  } else {
    document.exitFullscreen?.()
  }
}

const handleMenuCommand = (command: string) => {
  switch (command) {
    case 'reload':
      retry()
      break
    case 'share':
      showShareDialog.value = true
      break
    case 'info':
      showProductInfo.value = true
      break
    case 'feedback':
      // 实现反馈功能
      ElMessage.info('反馈功能待实现')
      break
    case 'settings':
      showDisplaySettings.value = true
      break
  }
}

const zoomIn = () => {
  const newScale = Math.min(currentScale.value * 1.2, maxScale.value)
  currentScale.value = newScale
  emit('scale-change', newScale)
}

const zoomOut = () => {
  const newScale = Math.max(currentScale.value / 1.2, minScale.value)
  currentScale.value = newScale
  emit('scale-change', newScale)
}

const resetZoom = () => {
  currentScale.value = 1
  emit('scale-change', 1)
}

const toggleAutoFit = () => {
  autoFit.value = !autoFit.value
}

const onScaleChange = (scale: number) => {
  currentScale.value = scale
  emit('scale-change', scale)
}

const onOrientationChange = (orientation: string) => {
  // 处理屏幕旋转
  setTimeout(() => {
    if (autoFit.value) {
      // 重新计算适应屏幕的缩放
    }
  }, 100)
}

const onGesture = (type: string, data: any) => {
  // 处理手势事件
  console.log('手势事件:', type, data)
}

const onError = (errorMsg: string) => {
  error.value = errorMsg
  emit('error', errorMsg)
}

const onProductLoad = () => {
  isLoading.value = false
  error.value = null
}

const onProductError = (errorMsg: string) => {
  error.value = errorMsg
  isLoading.value = false
}

const onProductMessage = (message: any) => {
  // 处理来自产品的消息
  console.log('产品消息:', message)
}

const retry = () => {
  isLoading.value = true
  error.value = null
  
  // 重新加载产品
  setTimeout(() => {
    isLoading.value = false
  }, 1000)
}

const getTypeLabel = (type?: string): string => {
  const labels: Record<string, string> = {
    static: '静态网页',
    spa: '单页应用',
    game: '游戏应用',
    tool: '工具应用'
  }
  return labels[type || ''] || '未知类型'
}

const copyShareUrl = async () => {
  try {
    await navigator.clipboard.writeText(shareUrl.value)
    ElMessage.success('链接已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

const shareToWeChat = () => {
  // 实现微信分享
  ElMessage.info('微信分享功能待实现')
}

const shareToQQ = () => {
  // 实现QQ分享
  ElMessage.info('QQ分享功能待实现')
}

const shareToWeibo = () => {
  // 实现微博分享
  ElMessage.info('微博分享功能待实现')
}

const hideGestureHint = () => {
  showGestureHint.value = false
  localStorage.setItem('gesture-hint-shown', 'true')
}

// 生命周期
onMounted(() => {
  // 显示手势提示
  const hasShownHint = localStorage.getItem('gesture-hint-shown')
  if (!hasShownHint && isMobileDevice.value) {
    setTimeout(() => {
      showGestureHint.value = true
    }, 2000)
  }
  
  // 监听全屏变化
  const handleFullscreenChange = () => {
    isFullscreen.value = !!document.fullscreenElement
  }
  
  document.addEventListener('fullscreenchange', handleFullscreenChange)
  
  // 清理函数
  return () => {
    document.removeEventListener('fullscreenchange', handleFullscreenChange)
  }
})

onUnmounted(() => {
  // 清理工作
})
</script>

<style scoped>
.mobile-product-viewer {
  position: relative;
  width: 100%;
  height: 100vh;
  background: #000;
  overflow: hidden;
}

.mobile-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 1rem;
  z-index: 1000;
  color: white;
}

.navbar-left {
  display: flex;
  align-items: center;
  gap: 1rem;
  flex: 1;
  min-width: 0;
}

.back-button,
.fullscreen-button,
.menu-button {
  color: white !important;
  border: none !important;
  background: transparent !important;
}

.product-info {
  flex: 1;
  min-width: 0;
}

.product-title {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: white;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.product-type {
  font-size: 0.75rem;
  color: #999;
}

.navbar-right {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.mobile-content {
  width: 100%;
  height: 100vh;
  position: relative;
  transition: padding 0.3s ease;
}

.mobile-controls {
  position: fixed;
  bottom: 0;
  left: 0;
  right: 0;
  height: 80px;
  background: rgba(0, 0, 0, 0.9);
  backdrop-filter: blur(10px);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 1rem;
  padding: 0 1rem;
  z-index: 1000;
}

.control-item {
  display: flex;
  align-items: center;
  justify-content: center;
}

.scale-display {
  min-width: 60px;
  color: white;
  font-size: 0.875rem;
  font-weight: 500;
}

.control-divider {
  width: 1px;
  height: 30px;
  background: rgba(255, 255, 255, 0.2);
}

.gesture-hint {
  position: fixed;
  bottom: 100px;
  left: 1rem;
  right: 1rem;
  z-index: 1001;
  background: rgba(0, 0, 0, 0.9);
  border-radius: 12px;
  padding: 1rem;
  color: white;
  animation: slideUp 0.3s ease;
}

.hint-content {
  display: flex;
  align-items: center;
  gap: 1rem;
}

.hint-icon {
  width: 40px;
  height: 40px;
  color: #4ade80;
  flex-shrink: 0;
}

.hint-text {
  flex: 1;
}

.hint-text p {
  margin: 0.25rem 0;
  font-size: 0.875rem;
}

.mobile-loading {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.8);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
}

.loading-content {
  text-align: center;
  color: white;
}

.loading-icon {
  color: #3b82f6;
  margin-bottom: 1rem;
  animation: spin 1s linear infinite;
}

.mobile-error {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.9);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 2000;
  padding: 2rem;
}

.error-content {
  text-align: center;
  color: white;
  max-width: 300px;
}

.error-icon {
  color: #f56565;
  margin-bottom: 1rem;
}

.error-content h3 {
  margin: 0 0 0.5rem 0;
  color: white;
}

.error-content p {
  margin: 0 0 1.5rem 0;
  color: #ccc;
  line-height: 1.5;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
}

.product-info-content {
  padding: 1rem;
}

.info-section {
  margin-bottom: 2rem;
}

.info-section h4 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
  color: #374151;
}

.info-item {
  display: flex;
  margin-bottom: 0.75rem;
  align-items: center;
}

.info-item .label {
  width: 80px;
  color: #6b7280;
  font-size: 0.875rem;
}

.info-item .value {
  flex: 1;
  color: #374151;
  font-weight: 500;
}

.description {
  color: #6b7280;
  line-height: 1.6;
  margin: 0;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.display-settings-content {
  padding: 1rem;
}

.setting-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 1rem 0;
  border-bottom: 1px solid #f3f4f6;
}

.setting-item:last-child {
  border-bottom: none;
}

.setting-label {
  font-weight: 500;
  color: #374151;
}

.scale-range {
  display: flex;
  align-items: center;
  gap: 1rem;
  width: 200px;
}

.scale-slider {
  flex: 1;
}

.share-content {
  padding: 1rem;
}

.share-url {
  margin-bottom: 2rem;
}

.share-actions {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}

/* 全屏模式 */
.mobile-product-viewer--fullscreen .mobile-navbar {
  display: none;
}

.mobile-product-viewer--fullscreen .mobile-controls {
  display: none;
}

/* 动画 */
@keyframes slideUp {
  from {
    transform: translateY(100%);
    opacity: 0;
  }
  to {
    transform: translateY(0);
    opacity: 1;
  }
}

@keyframes spin {
  from {
    transform: rotate(0deg);
  }
  to {
    transform: rotate(360deg);
  }
}

/* 响应式适配 */
@media (max-width: 480px) {
  .mobile-navbar {
    padding: 0 0.75rem;
  }
  
  .product-title {
    font-size: 0.875rem;
  }
  
  .mobile-controls {
    padding: 0 0.75rem;
    gap: 0.75rem;
  }
  
  .gesture-hint {
    left: 0.75rem;
    right: 0.75rem;
    bottom: 90px;
  }
}

@media (orientation: landscape) and (max-height: 500px) {
  .mobile-navbar {
    height: 50px;
  }
  
  .mobile-content {
    padding-top: 50px;
  }
  
  .mobile-controls {
    height: 60px;
  }
}
</style>