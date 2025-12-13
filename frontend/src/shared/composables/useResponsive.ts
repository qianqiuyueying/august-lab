/**
 * 响应式工具组合函数
 * 提供屏幕尺寸检测和响应式功能
 */

import { ref, computed, onMounted, onUnmounted } from 'vue'

// 断点定义
export const breakpoints = {
  xs: 475,
  sm: 640,
  md: 768,
  lg: 1024,
  xl: 1280,
  '2xl': 1536,
  '3xl': 1920,
} as const

export type Breakpoint = keyof typeof breakpoints

export function useResponsive() {
  const windowWidth = ref(0)
  const windowHeight = ref(0)

  // 更新窗口尺寸
  const updateSize = () => {
    windowWidth.value = window.innerWidth
    windowHeight.value = window.innerHeight
  }

  // 检查是否匹配指定断点
  const isBreakpoint = (breakpoint: Breakpoint) => {
    return computed(() => windowWidth.value >= breakpoints[breakpoint])
  }

  // 检查是否在指定断点范围内
  const isBetween = (min: Breakpoint, max: Breakpoint) => {
    return computed(() => 
      windowWidth.value >= breakpoints[min] && 
      windowWidth.value < breakpoints[max]
    )
  }

  // 各种屏幕尺寸检测
  const isXs = computed(() => windowWidth.value < breakpoints.sm)
  const isSm = computed(() => windowWidth.value >= breakpoints.sm && windowWidth.value < breakpoints.md)
  const isMd = computed(() => windowWidth.value >= breakpoints.md && windowWidth.value < breakpoints.lg)
  const isLg = computed(() => windowWidth.value >= breakpoints.lg && windowWidth.value < breakpoints.xl)
  const isXl = computed(() => windowWidth.value >= breakpoints.xl && windowWidth.value < breakpoints['2xl'])
  const is2xl = computed(() => windowWidth.value >= breakpoints['2xl'])

  // 便捷的尺寸检测
  const isMobile = computed(() => windowWidth.value < breakpoints.md)
  const isTablet = computed(() => windowWidth.value >= breakpoints.md && windowWidth.value < breakpoints.lg)
  const isDesktop = computed(() => windowWidth.value >= breakpoints.lg)
  const isLargeScreen = computed(() => windowWidth.value >= breakpoints.xl)

  // 获取当前断点
  const currentBreakpoint = computed((): Breakpoint => {
    if (windowWidth.value >= breakpoints['3xl']) return '3xl'
    if (windowWidth.value >= breakpoints['2xl']) return '2xl'
    if (windowWidth.value >= breakpoints.xl) return 'xl'
    if (windowWidth.value >= breakpoints.lg) return 'lg'
    if (windowWidth.value >= breakpoints.md) return 'md'
    if (windowWidth.value >= breakpoints.sm) return 'sm'
    if (windowWidth.value >= breakpoints.xs) return 'xs'
    return 'xs'
  })

  // 获取响应式网格列数
  const getGridCols = (config: Partial<Record<Breakpoint, number>>) => {
    return computed(() => {
      const bp = currentBreakpoint.value
      
      // 从当前断点开始向下查找配置
      const orderedBreakpoints: Breakpoint[] = ['3xl', '2xl', 'xl', 'lg', 'md', 'sm', 'xs']
      const currentIndex = orderedBreakpoints.indexOf(bp)
      
      for (let i = currentIndex; i < orderedBreakpoints.length; i++) {
        const breakpoint = orderedBreakpoints[i]
        if (config[breakpoint] !== undefined) {
          return config[breakpoint]
        }
      }
      
      return 1 // 默认值
    })
  }

  // 获取响应式间距
  const getResponsiveSpacing = (config: Partial<Record<Breakpoint, string>>) => {
    return computed(() => {
      const bp = currentBreakpoint.value
      
      const orderedBreakpoints: Breakpoint[] = ['3xl', '2xl', 'xl', 'lg', 'md', 'sm', 'xs']
      const currentIndex = orderedBreakpoints.indexOf(bp)
      
      for (let i = currentIndex; i < orderedBreakpoints.length; i++) {
        const breakpoint = orderedBreakpoints[i]
        if (config[breakpoint] !== undefined) {
          return config[breakpoint]
        }
      }
      
      return '1rem' // 默认值
    })
  }

  // 获取响应式文本大小
  const getResponsiveTextSize = (config: Partial<Record<Breakpoint, string>>) => {
    return computed(() => {
      const bp = currentBreakpoint.value
      
      const orderedBreakpoints: Breakpoint[] = ['3xl', '2xl', 'xl', 'lg', 'md', 'sm', 'xs']
      const currentIndex = orderedBreakpoints.indexOf(bp)
      
      for (let i = currentIndex; i < orderedBreakpoints.length; i++) {
        const breakpoint = orderedBreakpoints[i]
        if (config[breakpoint] !== undefined) {
          return config[breakpoint]
        }
      }
      
      return '1rem' // 默认值
    })
  }

  // 屏幕方向
  const isPortrait = computed(() => windowHeight.value > windowWidth.value)
  const isLandscape = computed(() => windowWidth.value > windowHeight.value)

  // 设备类型检测
  const deviceType = computed(() => {
    if (isMobile.value) return 'mobile'
    if (isTablet.value) return 'tablet'
    return 'desktop'
  })

  // 触摸设备检测
  const isTouchDevice = computed(() => {
    return 'ontouchstart' in window || navigator.maxTouchPoints > 0
  })

  // 生命周期管理
  onMounted(() => {
    updateSize()
    window.addEventListener('resize', updateSize)
  })

  onUnmounted(() => {
    window.removeEventListener('resize', updateSize)
  })

  return {
    // 窗口尺寸
    windowWidth: readonly(windowWidth),
    windowHeight: readonly(windowHeight),
    
    // 断点检测函数
    isBreakpoint,
    isBetween,
    
    // 具体断点检测
    isXs,
    isSm,
    isMd,
    isLg,
    isXl,
    is2xl,
    
    // 便捷检测
    isMobile,
    isTablet,
    isDesktop,
    isLargeScreen,
    
    // 当前断点
    currentBreakpoint,
    
    // 响应式工具
    getGridCols,
    getResponsiveSpacing,
    getResponsiveTextSize,
    
    // 屏幕方向
    isPortrait,
    isLandscape,
    
    // 设备类型
    deviceType,
    isTouchDevice,
    
    // 断点常量
    breakpoints,
    
    // 预设配置
    responsivePresets,
  }
}

// 只读包装器
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}

// 响应式网格配置类型
export interface ResponsiveGridConfig {
  xs?: number
  sm?: number
  md?: number
  lg?: number
  xl?: number
  '2xl'?: number
  '3xl'?: number
}

// 响应式间距配置类型
export interface ResponsiveSpacingConfig {
  xs?: string
  sm?: string
  md?: string
  lg?: string
  xl?: string
  '2xl'?: string
  '3xl'?: string
}

// 预设的响应式配置
export const responsivePresets = {
  // 网格预设
  grid: {
    auto: { xs: 1, sm: 2, md: 3, lg: 4, xl: 5, '2xl': 6 },
    cards: { xs: 1, sm: 2, lg: 3, xl: 4 },
    features: { xs: 1, md: 2, lg: 3 },
    team: { xs: 1, sm: 2, lg: 3, xl: 4 },
    gallery: { xs: 2, sm: 3, md: 4, lg: 5, xl: 6 },
    blog: { xs: 1, md: 2, lg: 3 },
    portfolio: { xs: 1, sm: 2, lg: 3 },
  },
  
  // 间距预设
  spacing: {
    section: { xs: '3rem', sm: '4rem', lg: '5rem', xl: '6rem' },
    container: { xs: '1rem', sm: '1.5rem', lg: '2rem', xl: '2.5rem' },
    card: { xs: '1rem', sm: '1.5rem', lg: '2rem' },
    button: { xs: '0.5rem 1rem', sm: '0.75rem 1.5rem', lg: '1rem 2rem' },
  },
  
  // 文本大小预设
  text: {
    hero: { xs: '2rem', sm: '2.5rem', md: '3rem', lg: '3.5rem', xl: '4rem' },
    title: { xs: '1.5rem', sm: '1.875rem', md: '2.25rem', lg: '2.5rem' },
    subtitle: { xs: '1.125rem', sm: '1.25rem', md: '1.5rem' },
    body: { xs: '0.875rem', sm: '1rem', md: '1.125rem' },
    caption: { xs: '0.75rem', sm: '0.875rem' },
  },
} as const