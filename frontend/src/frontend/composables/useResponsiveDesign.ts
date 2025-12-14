import { ref, computed, onMounted, onUnmounted } from 'vue'
import type { Product } from '../../shared/types'

// 扩展 CSSStyleDeclaration 接口以支持 WebKit 和 Mozilla 特定属性
declare global {
  interface CSSStyleDeclaration {
    webkitOverflowScrolling?: string
    overflowScrolling?: string
    webkitTouchCallout?: string
    webkitTapHighlightColor?: string
    webkitFontSmoothing?: string
    mozOsxFontSmoothing?: string
  }
}

// 设备类型定义
export type DeviceType = 'mobile' | 'tablet' | 'desktop' | 'large-desktop'

// 屏幕方向
export type Orientation = 'portrait' | 'landscape'

// 响应式断点
export interface Breakpoints {
  mobile: number
  tablet: number
  desktop: number
  largeDesktop: number
}

// 设备信息
export interface DeviceInfo {
  type: DeviceType
  orientation: Orientation
  width: number
  height: number
  pixelRatio: number
  touchSupport: boolean
  isMobile: boolean
  isTablet: boolean
  isDesktop: boolean
}

// 响应式配置
export interface ResponsiveConfig {
  breakpoints: Breakpoints
  enableTouch: boolean
  enableGestures: boolean
  adaptiveLayout: boolean
  scaleToFit: boolean
  minScale: number
  maxScale: number
  autoRotate: boolean
}

// 布局配置
export interface LayoutConfig {
  width: number | 'auto'
  height: number | 'auto'
  minWidth?: number
  minHeight?: number
  maxWidth?: number
  maxHeight?: number
  aspectRatio?: string
  padding?: number
  margin?: number
}

// 触摸手势配置
export interface TouchConfig {
  enablePinch: boolean
  enablePan: boolean
  enableRotate: boolean
  enableSwipe: boolean
  sensitivity: number
  threshold: number
}

export function useResponsiveDesign() {
  // 默认断点
  const defaultBreakpoints: Breakpoints = {
    mobile: 768,
    tablet: 1024,
    desktop: 1440,
    largeDesktop: 1920
  }
  
  // 响应式状态
  const screenWidth = ref(0)
  const screenHeight = ref(0)
  const pixelRatio = ref(1)
  const orientation = ref<Orientation>('landscape')
  const touchSupport = ref(false)
  
  // 配置状态
  const breakpoints = ref<Breakpoints>(defaultBreakpoints)
  const responsiveConfig = ref<ResponsiveConfig>({
    breakpoints: defaultBreakpoints,
    enableTouch: true,
    enableGestures: true,
    adaptiveLayout: true,
    scaleToFit: true,
    minScale: 0.5,
    maxScale: 3.0,
    autoRotate: true
  })
  
  // 计算属性
  const deviceType = computed<DeviceType>(() => {
    const width = screenWidth.value
    if (width < breakpoints.value.mobile) return 'mobile'
    if (width < breakpoints.value.tablet) return 'tablet'
    if (width < breakpoints.value.desktop) return 'desktop'
    return 'large-desktop'
  })
  
  const deviceInfo = computed<DeviceInfo>(() => ({
    type: deviceType.value,
    orientation: orientation.value,
    width: screenWidth.value,
    height: screenHeight.value,
    pixelRatio: pixelRatio.value,
    touchSupport: touchSupport.value,
    isMobile: deviceType.value === 'mobile',
    isTablet: deviceType.value === 'tablet',
    isDesktop: ['desktop', 'large-desktop'].includes(deviceType.value)
  }))
  
  const isMobileDevice = computed(() => deviceInfo.value.isMobile)
  const isTabletDevice = computed(() => deviceInfo.value.isTablet)
  const isDesktopDevice = computed(() => deviceInfo.value.isDesktop)
  const isPortrait = computed(() => orientation.value === 'portrait')
  const isLandscape = computed(() => orientation.value === 'landscape')
  
  // 更新屏幕信息
  const updateScreenInfo = () => {
    screenWidth.value = window.innerWidth
    screenHeight.value = window.innerHeight
    pixelRatio.value = window.devicePixelRatio || 1
    orientation.value = window.innerHeight > window.innerWidth ? 'portrait' : 'landscape'
    touchSupport.value = 'ontouchstart' in window || navigator.maxTouchPoints > 0
  }
  
  // 获取产品的响应式配置
  const getProductResponsiveConfig = (product: Product): ResponsiveConfig => {
    const config = product.config_data?.responsive || {}
    
    return {
      breakpoints: { ...defaultBreakpoints, ...config.breakpoints },
      enableTouch: config.enableTouch !== false,
      enableGestures: config.enableGestures !== false,
      adaptiveLayout: config.adaptiveLayout !== false,
      scaleToFit: config.scaleToFit !== false,
      minScale: config.minScale || 0.5,
      maxScale: config.maxScale || 3.0,
      autoRotate: config.autoRotate !== false
    }
  }
  
  // 计算产品布局
  const calculateProductLayout = (
    product: Product,
    containerWidth: number,
    containerHeight: number
  ): LayoutConfig => {
    const config = getProductResponsiveConfig(product)
    const displayConfig = product.config_data?.display || {}
    
    let width: number | 'auto' = 'auto'
    let height: number | 'auto' = 'auto'
    
    // 处理固定尺寸
    if (typeof displayConfig.width === 'number') {
      width = displayConfig.width
    }
    if (typeof displayConfig.height === 'number') {
      height = displayConfig.height
    }
    
    // 响应式适配
    if (config.adaptiveLayout) {
      // 移动设备适配
      if (isMobileDevice.value) {
        width = Math.min(containerWidth - 32, typeof width === 'number' ? width : containerWidth)
        if (typeof height === 'number') {
          height = Math.min(containerHeight - 64, height)
        }
      }
      // 平板设备适配
      else if (isTabletDevice.value) {
        width = Math.min(containerWidth - 48, typeof width === 'number' ? width : containerWidth)
        if (typeof height === 'number') {
          height = Math.min(containerHeight - 96, height)
        }
      }
    }
    
    // 处理宽高比
    if (displayConfig.aspectRatio && typeof width === 'number') {
      const [w, h] = displayConfig.aspectRatio.split(':').map(Number)
      if (w && h) {
        height = (width * h) / w
      }
    }
    
    // 缩放适配
    if (config.scaleToFit && typeof width === 'number' && typeof height === 'number') {
      const scaleX = containerWidth / width
      const scaleY = containerHeight / height
      const scale = Math.min(scaleX, scaleY, config.maxScale)
      
      if (scale < 1 || scale > config.maxScale) {
        width = width * Math.max(scale, config.minScale)
        height = height * Math.max(scale, config.minScale)
      }
    }
    
    return {
      width,
      height,
      minWidth: displayConfig.minWidth,
      minHeight: displayConfig.minHeight,
      maxWidth: displayConfig.maxWidth,
      maxHeight: displayConfig.maxHeight,
      aspectRatio: displayConfig.aspectRatio,
      padding: isMobileDevice.value ? 16 : isTabletDevice.value ? 24 : 32,
      margin: isMobileDevice.value ? 8 : 16
    }
  }
  
  // 生成响应式CSS
  const generateResponsiveCSS = (layout: LayoutConfig): Record<string, string> => {
    const styles: Record<string, string> = {}
    
    if (typeof layout.width === 'number') {
      styles.width = `${layout.width}px`
    } else {
      styles.width = '100%'
    }
    
    if (typeof layout.height === 'number') {
      styles.height = `${layout.height}px`
    } else {
      styles.height = 'auto'
    }
    
    if (layout.minWidth) styles.minWidth = `${layout.minWidth}px`
    if (layout.minHeight) styles.minHeight = `${layout.minHeight}px`
    if (layout.maxWidth) styles.maxWidth = `${layout.maxWidth}px`
    if (layout.maxHeight) styles.maxHeight = `${layout.maxHeight}px`
    
    if (layout.padding) styles.padding = `${layout.padding}px`
    if (layout.margin) styles.margin = `${layout.margin}px`
    
    // 响应式适配
    styles.boxSizing = 'border-box'
    styles.overflow = 'hidden'
    
    return styles
  }
  
  // 设置触摸手势支持
  const setupTouchGestures = (
    element: HTMLElement,
    config: TouchConfig,
    callbacks: {
      onPinch?: (scale: number, center: { x: number; y: number }) => void
      onPan?: (delta: { x: number; y: number }) => void
      onRotate?: (angle: number) => void
      onSwipe?: (direction: 'up' | 'down' | 'left' | 'right', velocity: number) => void
    }
  ) => {
    if (!touchSupport.value) return
    
    let touches: Touch[] = []
    let initialDistance = 0
    let initialAngle = 0
    let initialCenter = { x: 0, y: 0 }
    let lastPanPosition = { x: 0, y: 0 }
    let swipeStartTime = 0
    let swipeStartPosition = { x: 0, y: 0 }
    
    const getTouchDistance = (touch1: Touch, touch2: Touch): number => {
      const dx = touch1.clientX - touch2.clientX
      const dy = touch1.clientY - touch2.clientY
      return Math.sqrt(dx * dx + dy * dy)
    }
    
    const getTouchAngle = (touch1: Touch, touch2: Touch): number => {
      const dx = touch1.clientX - touch2.clientX
      const dy = touch1.clientY - touch2.clientY
      return Math.atan2(dy, dx) * 180 / Math.PI
    }
    
    const getTouchCenter = (touch1: Touch, touch2: Touch) => ({
      x: (touch1.clientX + touch2.clientX) / 2,
      y: (touch1.clientY + touch2.clientY) / 2
    })
    
    const handleTouchStart = (e: TouchEvent) => {
      touches = Array.from(e.touches)
      swipeStartTime = Date.now()
      
      if (touches.length === 1) {
        lastPanPosition = { x: touches[0].clientX, y: touches[0].clientY }
        swipeStartPosition = { x: touches[0].clientX, y: touches[0].clientY }
      } else if (touches.length === 2) {
        initialDistance = getTouchDistance(touches[0], touches[1])
        initialAngle = getTouchAngle(touches[0], touches[1])
        initialCenter = getTouchCenter(touches[0], touches[1])
      }
    }
    
    const handleTouchMove = (e: TouchEvent) => {
      e.preventDefault()
      touches = Array.from(e.touches)
      
      if (touches.length === 1 && config.enablePan) {
        // 单指拖拽
        const delta = {
          x: touches[0].clientX - lastPanPosition.x,
          y: touches[0].clientY - lastPanPosition.y
        }
        
        if (Math.abs(delta.x) > config.threshold || Math.abs(delta.y) > config.threshold) {
          callbacks.onPan?.(delta)
          lastPanPosition = { x: touches[0].clientX, y: touches[0].clientY }
        }
      } else if (touches.length === 2) {
        const currentDistance = getTouchDistance(touches[0], touches[1])
        const currentAngle = getTouchAngle(touches[0], touches[1])
        const currentCenter = getTouchCenter(touches[0], touches[1])
        
        // 双指缩放
        if (config.enablePinch && initialDistance > 0) {
          const scale = currentDistance / initialDistance
          if (Math.abs(scale - 1) > 0.1) {
            callbacks.onPinch?.(scale, currentCenter)
          }
        }
        
        // 双指旋转
        if (config.enableRotate) {
          const angleDelta = currentAngle - initialAngle
          if (Math.abs(angleDelta) > 5) {
            callbacks.onRotate?.(angleDelta)
          }
        }
      }
    }
    
    const handleTouchEnd = (e: TouchEvent) => {
      if (config.enableSwipe && touches.length === 1) {
        const endTime = Date.now()
        const duration = endTime - swipeStartTime
        const endPosition = { x: touches[0].clientX, y: touches[0].clientY }
        
        const deltaX = endPosition.x - swipeStartPosition.x
        const deltaY = endPosition.y - swipeStartPosition.y
        const distance = Math.sqrt(deltaX * deltaX + deltaY * deltaY)
        const velocity = distance / duration
        
        if (velocity > config.sensitivity && distance > config.threshold) {
          let direction: 'up' | 'down' | 'left' | 'right'
          
          if (Math.abs(deltaX) > Math.abs(deltaY)) {
            direction = deltaX > 0 ? 'right' : 'left'
          } else {
            direction = deltaY > 0 ? 'down' : 'up'
          }
          
          callbacks.onSwipe?.(direction, velocity)
        }
      }
      
      touches = []
    }
    
    element.addEventListener('touchstart', handleTouchStart, { passive: false })
    element.addEventListener('touchmove', handleTouchMove, { passive: false })
    element.addEventListener('touchend', handleTouchEnd, { passive: false })
    
    return () => {
      element.removeEventListener('touchstart', handleTouchStart)
      element.removeEventListener('touchmove', handleTouchMove)
      element.removeEventListener('touchend', handleTouchEnd)
    }
  }
  
  // 优化移动端性能
  const optimizeForMobile = (element: HTMLElement) => {
    if (!isMobileDevice.value) return
    
    // 启用硬件加速
    element.style.transform = 'translateZ(0)'
    element.style.willChange = 'transform'
    
    // 优化滚动
    element.style.webkitOverflowScrolling = 'touch'
    element.style.overflowScrolling = 'touch'
    
    // 禁用选择和拖拽
    element.style.userSelect = 'none'
    element.style.webkitUserSelect = 'none'
    element.style.webkitTouchCallout = 'none'
    element.style.webkitTapHighlightColor = 'transparent'
    
    // 优化字体渲染
    element.style.webkitFontSmoothing = 'antialiased'
    element.style.mozOsxFontSmoothing = 'grayscale'
  }
  
  // 处理屏幕旋转
  const handleOrientationChange = (callback: (orientation: Orientation) => void) => {
    const handleChange = () => {
      setTimeout(() => {
        updateScreenInfo()
        callback(orientation.value)
      }, 100) // 延迟确保尺寸更新完成
    }
    
    window.addEventListener('orientationchange', handleChange)
    window.addEventListener('resize', handleChange)
    
    return () => {
      window.removeEventListener('orientationchange', handleChange)
      window.removeEventListener('resize', handleChange)
    }
  }
  
  // 自适应视口
  const setupViewport = (config?: { 
    userScalable?: boolean
    initialScale?: number
    minimumScale?: number
    maximumScale?: number
  }) => {
    const viewport = document.querySelector('meta[name="viewport"]') as HTMLMetaElement
    if (!viewport) return
    
    const settings = {
      userScalable: config?.userScalable ?? false,
      initialScale: config?.initialScale ?? 1.0,
      minimumScale: config?.minimumScale ?? 0.5,
      maximumScale: config?.maximumScale ?? 3.0
    }
    
    const content = [
      'width=device-width',
      `initial-scale=${settings.initialScale}`,
      `minimum-scale=${settings.minimumScale}`,
      `maximum-scale=${settings.maximumScale}`,
      `user-scalable=${settings.userScalable ? 'yes' : 'no'}`
    ].join(', ')
    
    viewport.setAttribute('content', content)
  }
  
  // 检测设备能力
  const detectDeviceCapabilities = () => {
    return {
      touchSupport: touchSupport.value,
      pointerEvents: 'PointerEvent' in window,
      gestureEvents: 'GestureEvent' in window,
      orientationSupport: 'orientation' in window,
      deviceMotion: 'DeviceMotionEvent' in window,
      deviceOrientation: 'DeviceOrientationEvent' in window,
      vibration: 'vibrate' in navigator,
      battery: 'getBattery' in navigator,
      connection: 'connection' in navigator,
      webgl: (() => {
        try {
          const canvas = document.createElement('canvas')
          return !!(canvas.getContext('webgl') || canvas.getContext('experimental-webgl'))
        } catch {
          return false
        }
      })()
    }
  }
  
  // 生命周期
  onMounted(() => {
    updateScreenInfo()
    window.addEventListener('resize', updateScreenInfo)
    window.addEventListener('orientationchange', updateScreenInfo)
  })
  
  onUnmounted(() => {
    window.removeEventListener('resize', updateScreenInfo)
    window.removeEventListener('orientationchange', updateScreenInfo)
  })
  
  return {
    // 状态
    screenWidth: computed(() => screenWidth.value),
    screenHeight: computed(() => screenHeight.value),
    pixelRatio: computed(() => pixelRatio.value),
    orientation: computed(() => orientation.value),
    deviceType: computed(() => deviceType.value),
    deviceInfo: computed(() => deviceInfo.value),
    
    // 设备检测
    isMobileDevice,
    isTabletDevice,
    isDesktopDevice,
    isPortrait,
    isLandscape,
    touchSupport: computed(() => touchSupport.value),
    
    // 配置
    breakpoints: computed(() => breakpoints.value),
    responsiveConfig: computed(() => responsiveConfig.value),
    
    // 方法
    updateScreenInfo,
    getProductResponsiveConfig,
    calculateProductLayout,
    generateResponsiveCSS,
    setupTouchGestures,
    optimizeForMobile,
    handleOrientationChange,
    setupViewport,
    detectDeviceCapabilities,
    
    // 工具方法
    setBreakpoints: (newBreakpoints: Partial<Breakpoints>) => {
      breakpoints.value = { ...breakpoints.value, ...newBreakpoints }
    },
    
    setResponsiveConfig: (config: Partial<ResponsiveConfig>) => {
      responsiveConfig.value = { ...responsiveConfig.value, ...config }
    }
  }
}