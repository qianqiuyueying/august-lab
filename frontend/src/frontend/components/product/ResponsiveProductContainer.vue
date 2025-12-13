<template>
  <div 
    ref="containerRef"
    class="responsive-product-container"
    :class="containerClasses"
    :style="containerStyles"
  >
    <!-- 设备信息显示（开发模式） -->
    <div v-if="showDeviceInfo" class="device-info">
      <div class="device-badge">
        <span class="device-type">{{ deviceInfo.type }}</span>
        <span class="device-size">{{ deviceInfo.width }}×{{ deviceInfo.height }}</span>
        <span class="device-orientation">{{ deviceInfo.orientation }}</span>
      </div>
    </div>
    
    <!-- 响应式控制栏 -->
    <div v-if="showControls" class="responsive-controls">
      <div class="control-group">
        <el-button-group size="small">
          <el-button 
            :type="currentScale === 1 ? 'primary' : ''"
            @click="setScale(1)"
            icon="Refresh"
          >
            100%
          </el-button>
          <el-button 
            :type="fitToScreen ? 'primary' : ''"
            @click="toggleFitToScreen"
            icon="FullScreen"
          >
            适应屏幕
          </el-button>
        </el-button-group>
      </div>
      
      <div class="control-group">
        <el-slider
          v-model="scalePercentage"
          :min="minScalePercentage"
          :max="maxScalePercentage"
          :step="10"
          :show-tooltip="false"
          class="scale-slider"
          @change="onScaleChange"
        />
        <span class="scale-text">{{ Math.round(currentScale * 100) }}%</span>
      </div>
      
      <div class="control-group">
        <el-button
          @click="toggleOrientation"
          size="small"
          icon="RefreshRight"
          :disabled="!canRotate"
        >
          旋转
        </el-button>
      </div>
    </div>
    
    <!-- 产品容器 -->
    <div 
      ref="productWrapperRef"
      class="product-wrapper"
      :style="wrapperStyles"
      @wheel="handleWheel"
    >
      <div 
        ref="productContentRef"
        class="product-content"
        :style="contentStyles"
      >
        <slot :device-info="deviceInfo" :layout="currentLayout" />
      </div>
      
      <!-- 触摸手势覆盖层 -->
      <div 
        v-if="enableGestures && touchSupport"
        ref="gestureOverlayRef"
        class="gesture-overlay"
        @touchstart="handleTouchStart"
        @touchmove="handleTouchMove"
        @touchend="handleTouchEnd"
      />
    </div>
    
    <!-- 加载状态 -->
    <div v-if="isLoading" class="loading-overlay">
      <el-loading 
        :text="loadingText"
        background="rgba(255, 255, 255, 0.8)"
      />
    </div>
    
    <!-- 错误状态 -->
    <div v-if="error" class="error-overlay">
      <div class="error-content">
        <el-icon class="error-icon" size="48">
          <WarningFilled />
        </el-icon>
        <h3>响应式适配错误</h3>
        <p>{{ error }}</p>
        <el-button @click="retry" type="primary">重试</el-button>
      </div>
    </div>
    
    <!-- 响应式提示 -->
    <el-dialog
      v-model="showResponsiveTip"
      title="响应式适配提示"
      width="400px"
      :show-close="false"
    >
      <div class="responsive-tip">
        <p>检测到您正在使用{{ deviceTypeLabel }}设备</p>
        <p>为了获得最佳体验，建议：</p>
        <ul>
          <li v-for="tip in responsiveTips" :key="tip">{{ tip }}</li>
        </ul>
      </div>
      
      <template #footer>
        <el-checkbox v-model="dontShowAgain">不再显示</el-checkbox>
        <el-button @click="showResponsiveTip = false" type="primary">知道了</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { WarningFilled } from '@element-plus/icons-vue'
import { useResponsiveDesign } from '../composables/useResponsiveDesign'
import type { Product } from '../../shared/types'

interface Props {
  product?: Product
  showControls?: boolean
  showDeviceInfo?: boolean
  enableGestures?: boolean
  autoFit?: boolean
  minScale?: number
  maxScale?: number
  loadingText?: string
}

interface Emits {
  (e: 'scale-change', scale: number): void
  (e: 'orientation-change', orientation: string): void
  (e: 'layout-change', layout: any): void
  (e: 'gesture', type: string, data: any): void
  (e: 'error', error: string): void
}

const props = withDefaults(defineProps<Props>(), {
  showControls: true,
  showDeviceInfo: false,
  enableGestures: true,
  autoFit: true,
  minScale: 0.25,
  maxScale: 4.0,
  loadingText: '正在适配响应式布局...'
})

const emit = defineEmits<Emits>()

// 使用响应式设计
const {
  deviceInfo,
  isMobileDevice,
  isTabletDevice,
  isDesktopDevice,
  touchSupport,
  calculateProductLayout,
  generateResponsiveCSS,
  setupTouchGestures,
  optimizeForMobile,
  handleOrientationChange,
  setupViewport
} = useResponsiveDesign()

// 模板引用
const containerRef = ref<HTMLElement>()
const productWrapperRef = ref<HTMLElement>()
const productContentRef = ref<HTMLElement>()
const gestureOverlayRef = ref<HTMLElement>()

// 响应式状态
const currentScale = ref(1)
const fitToScreen = ref(props.autoFit)
const isLoading = ref(false)
const error = ref<string | null>(null)
const showResponsiveTip = ref(false)
const dontShowAgain = ref(false)
const canRotate = ref(false)

// 手势状态
const gestureState = ref({
  isPinching: false,
  isPanning: false,
  isRotating: false,
  lastScale: 1,
  lastRotation: 0,
  panOffset: { x: 0, y: 0 }
})

// 计算属性
const scalePercentage = computed({
  get: () => Math.round(currentScale.value * 100),
  set: (value: number) => {
    currentScale.value = value / 100
  }
})

const minScalePercentage = computed(() => Math.round(props.minScale * 100))
const maxScalePercentage = computed(() => Math.round(props.maxScale * 100))

const deviceTypeLabel = computed(() => {
  const labels = {
    mobile: '移动',
    tablet: '平板',
    desktop: '桌面',
    'large-desktop': '大屏桌面'
  }
  return labels[deviceInfo.value.type] || '未知'
})

const responsiveTips = computed(() => {
  const tips: string[] = []
  
  if (isMobileDevice.value) {
    tips.push('横屏使用可获得更好的视觉效果')
    tips.push('双指缩放调整内容大小')
    tips.push('单指滑动浏览内容')
  } else if (isTabletDevice.value) {
    tips.push('可以使用触摸手势操作')
    tips.push('支持多点触控缩放')
  } else {
    tips.push('使用鼠标滚轮缩放内容')
    tips.push('拖拽移动内容位置')
  }
  
  return tips
})

const currentLayout = computed(() => {
  if (!props.product || !containerRef.value) return null
  
  const containerRect = containerRef.value.getBoundingClientRect()
  return calculateProductLayout(
    props.product,
    containerRect.width,
    containerRect.height
  )
})

const containerClasses = computed(() => ({
  'responsive-product-container--mobile': isMobileDevice.value,
  'responsive-product-container--tablet': isTabletDevice.value,
  'responsive-product-container--desktop': isDesktopDevice.value,
  'responsive-product-container--portrait': deviceInfo.value.orientation === 'portrait',
  'responsive-product-container--landscape': deviceInfo.value.orientation === 'landscape',
  'responsive-product-container--touch': touchSupport.value,
  'responsive-product-container--loading': isLoading.value,
  'responsive-product-container--error': !!error.value
}))

const containerStyles = computed(() => {
  const styles: Record<string, string> = {
    width: '100%',
    height: '100%',
    position: 'relative',
    overflow: 'hidden'
  }
  
  return styles
})

const wrapperStyles = computed(() => {
  const styles: Record<string, string> = {
    width: '100%',
    height: '100%',
    position: 'relative',
    overflow: fitToScreen.value ? 'hidden' : 'auto',
    display: 'flex',
    alignItems: 'center',
    justifyContent: 'center'
  }
  
  return styles
})

const contentStyles = computed(() => {
  if (!currentLayout.value) return {}
  
  const layout = currentLayout.value
  const styles = generateResponsiveCSS(layout)
  
  // 应用缩放
  if (currentScale.value !== 1) {
    styles.transform = `scale(${currentScale.value}) ${styles.transform || ''}`
    styles.transformOrigin = 'center center'
  }
  
  // 应用手势偏移
  if (gestureState.value.panOffset.x !== 0 || gestureState.value.panOffset.y !== 0) {
    const translateX = gestureState.value.panOffset.x
    const translateY = gestureState.value.panOffset.y
    styles.transform = `translate(${translateX}px, ${translateY}px) ${styles.transform || ''}`
  }
  
  // 移动端优化
  if (isMobileDevice.value) {
    styles.willChange = 'transform'
    styles.backfaceVisibility = 'hidden'
  }
  
  return styles
})

// 方法
const setScale = (scale: number) => {
  const clampedScale = Math.max(props.minScale, Math.min(props.maxScale, scale))
  currentScale.value = clampedScale
  emit('scale-change', clampedScale)
}

const toggleFitToScreen = () => {
  fitToScreen.value = !fitToScreen.value
  
  if (fitToScreen.value) {
    calculateOptimalScale()
  } else {
    setScale(1)
  }
}

const calculateOptimalScale = () => {
  if (!currentLayout.value || !containerRef.value) return
  
  const layout = currentLayout.value
  const containerRect = containerRef.value.getBoundingClientRect()
  
  if (typeof layout.width === 'number' && typeof layout.height === 'number') {
    const scaleX = (containerRect.width - 64) / layout.width
    const scaleY = (containerRect.height - 64) / layout.height
    const optimalScale = Math.min(scaleX, scaleY, props.maxScale)
    
    setScale(Math.max(optimalScale, props.minScale))
  }
}

const onScaleChange = (value: number) => {
  setScale(value / 100)
}

const toggleOrientation = () => {
  // 这里可以实现模拟旋转功能
  ElMessage.info('旋转功能需要设备支持')
}

const handleWheel = (event: WheelEvent) => {
  if (!props.enableGestures) return
  
  event.preventDefault()
  
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  const newScale = currentScale.value + delta
  setScale(newScale)
}

const handleTouchStart = (event: TouchEvent) => {
  if (!props.enableGestures) return
  
  if (event.touches.length === 2) {
    gestureState.value.isPinching = true
    gestureState.value.lastScale = currentScale.value
  } else if (event.touches.length === 1) {
    gestureState.value.isPanning = true
  }
}

const handleTouchMove = (event: TouchEvent) => {
  if (!props.enableGestures) return
  
  event.preventDefault()
}

const handleTouchEnd = (event: TouchEvent) => {
  if (!props.enableGestures) return
  
  gestureState.value.isPinching = false
  gestureState.value.isPanning = false
  gestureState.value.isRotating = false
}

const setupGestures = () => {
  if (!gestureOverlayRef.value || !props.enableGestures) return
  
  const cleanup = setupTouchGestures(
    gestureOverlayRef.value,
    {
      enablePinch: true,
      enablePan: true,
      enableRotate: false,
      enableSwipe: true,
      sensitivity: 0.5,
      threshold: 10
    },
    {
      onPinch: (scale, center) => {
        const newScale = gestureState.value.lastScale * scale
        setScale(newScale)
        emit('gesture', 'pinch', { scale, center })
      },
      
      onPan: (delta) => {
        gestureState.value.panOffset.x += delta.x
        gestureState.value.panOffset.y += delta.y
        emit('gesture', 'pan', delta)
      },
      
      onSwipe: (direction, velocity) => {
        emit('gesture', 'swipe', { direction, velocity })
      }
    }
  )
  
  return cleanup
}

const initializeResponsive = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    await nextTick()
    
    // 设置视口
    if (isMobileDevice.value) {
      setupViewport({
        userScalable: false,
        initialScale: 1.0,
        minimumScale: 0.5,
        maximumScale: 3.0
      })
    }
    
    // 优化移动端性能
    if (productContentRef.value && isMobileDevice.value) {
      optimizeForMobile(productContentRef.value)
    }
    
    // 计算初始缩放
    if (fitToScreen.value) {
      calculateOptimalScale()
    }
    
    // 设置手势
    const gestureCleanup = setupGestures()
    
    // 处理屏幕旋转
    const orientationCleanup = handleOrientationChange((orientation) => {
      emit('orientation-change', orientation)
      
      // 重新计算布局
      if (fitToScreen.value) {
        setTimeout(calculateOptimalScale, 100)
      }
    })
    
    // 显示响应式提示
    if (isMobileDevice.value && !dontShowAgain.value) {
      const hasShown = localStorage.getItem('responsive-tip-shown')
      if (!hasShown) {
        showResponsiveTip.value = true
      }
    }
    
    // 返回清理函数
    return () => {
      gestureCleanup?.()
      orientationCleanup?.()
    }
    
  } catch (err: any) {
    error.value = err.message || '响应式初始化失败'
    emit('error', error.value)
  } finally {
    isLoading.value = false
  }
}

const retry = () => {
  initializeResponsive()
}

// 监听器
watch(() => props.product, () => {
  if (props.product) {
    initializeResponsive()
  }
}, { immediate: true })

watch(currentLayout, (newLayout) => {
  if (newLayout) {
    emit('layout-change', newLayout)
  }
}, { deep: true })

watch(showResponsiveTip, (show) => {
  if (!show && dontShowAgain.value) {
    localStorage.setItem('responsive-tip-shown', 'true')
  }
})

// 生命周期
let cleanupFunctions: (() => void)[] = []

onMounted(async () => {
  const cleanup = await initializeResponsive()
  if (cleanup) {
    cleanupFunctions.push(cleanup)
  }
})

onUnmounted(() => {
  cleanupFunctions.forEach(cleanup => cleanup())
  cleanupFunctions = []
})

// 暴露方法
defineExpose({
  setScale,
  toggleFitToScreen,
  calculateOptimalScale,
  retry
})
</script>

<style scoped>
.responsive-product-container {
  position: relative;
  width: 100%;
  height: 100%;
  background: #f5f5f5;
  overflow: hidden;
}

.device-info {
  position: absolute;
  top: 1rem;
  left: 1rem;
  z-index: 100;
}

.device-badge {
  display: flex;
  gap: 0.5rem;
  padding: 0.25rem 0.5rem;
  background: rgba(0, 0, 0, 0.7);
  color: white;
  border-radius: 4px;
  font-size: 0.75rem;
  font-family: monospace;
}

.responsive-controls {
  position: absolute;
  top: 1rem;
  right: 1rem;
  z-index: 100;
  display: flex;
  gap: 1rem;
  align-items: center;
  padding: 0.5rem;
  background: rgba(255, 255, 255, 0.95);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(8px);
}

.control-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.scale-slider {
  width: 100px;
}

.scale-text {
  font-size: 0.875rem;
  color: #666;
  min-width: 40px;
  text-align: center;
}

.product-wrapper {
  position: relative;
  width: 100%;
  height: 100%;
}

.product-content {
  position: relative;
  transition: transform 0.3s ease;
  background: white;
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  overflow: hidden;
}

.gesture-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 10;
  touch-action: none;
}

.loading-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 1000;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.95);
}

.error-content {
  text-align: center;
  max-width: 400px;
  padding: 2rem;
}

.error-icon {
  color: #f56565;
  margin-bottom: 1rem;
}

.error-content h3 {
  margin: 0 0 0.5rem 0;
  color: #2d3748;
}

.error-content p {
  margin: 0 0 1.5rem 0;
  color: #718096;
}

.responsive-tip {
  line-height: 1.6;
}

.responsive-tip ul {
  margin: 1rem 0;
  padding-left: 1.5rem;
}

.responsive-tip li {
  margin-bottom: 0.5rem;
}

/* 设备特定样式 */
.responsive-product-container--mobile {
  background: #000;
}

.responsive-product-container--mobile .responsive-controls {
  position: fixed;
  bottom: 1rem;
  right: 1rem;
  top: auto;
  flex-direction: column;
  align-items: stretch;
}

.responsive-product-container--mobile .control-group {
  justify-content: center;
}

.responsive-product-container--tablet .responsive-controls {
  gap: 0.75rem;
}

.responsive-product-container--portrait .product-content {
  max-width: 100vw;
}

.responsive-product-container--landscape .product-content {
  max-height: 100vh;
}

/* 触摸设备优化 */
.responsive-product-container--touch .product-content {
  user-select: none;
  -webkit-user-select: none;
  -webkit-touch-callout: none;
  -webkit-tap-highlight-color: transparent;
}

/* 加载和错误状态 */
.responsive-product-container--loading .product-wrapper {
  opacity: 0.5;
  pointer-events: none;
}

.responsive-product-container--error .product-wrapper {
  opacity: 0.3;
  pointer-events: none;
}

/* 响应式断点 */
@media (max-width: 768px) {
  .responsive-controls {
    position: fixed !important;
    bottom: 1rem !important;
    right: 1rem !important;
    top: auto !important;
    left: 1rem !important;
    flex-direction: row !important;
    justify-content: space-between;
    padding: 0.75rem;
  }
  
  .control-group {
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .scale-slider {
    width: 80px;
  }
  
  .device-info {
    display: none;
  }
}

@media (max-width: 480px) {
  .responsive-controls {
    flex-direction: column !important;
    align-items: stretch !important;
  }
  
  .control-group {
    flex-direction: row !important;
    justify-content: center;
  }
}

/* 动画效果 */
.product-content {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.responsive-controls {
  transition: all 0.2s ease;
}

.responsive-controls:hover {
  background: rgba(255, 255, 255, 0.98);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
}
</style>