<!--
响应式图片组件
提供自适应图片显示和懒加载功能
-->

<template>
  <div 
    :class="containerClasses"
    :style="containerStyles"
  >
    <img
      v-if="!isLazyLoading || isIntersecting"
      :src="currentSrc"
      :alt="alt"
      :class="imageClasses"
      :style="imageStyles"
      @load="onLoad"
      @error="onError"
    />
    
    <!-- 加载占位符 -->
    <div 
      v-if="isLoading && showPlaceholder"
      :class="placeholderClasses"
    >
      <div class="animate-pulse bg-gray-200 w-full h-full rounded"></div>
    </div>
    
    <!-- 错误占位符 -->
    <div 
      v-if="hasError && showErrorPlaceholder"
      :class="placeholderClasses"
    >
      <div class="flex items-center justify-center w-full h-full bg-gray-100 rounded">
        <svg class="w-8 h-8 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z" />
        </svg>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { useResponsive } from '../composables/useResponsive'

interface ResponsiveSrc {
  xs?: string
  sm?: string
  md?: string
  lg?: string
  xl?: string
  '2xl'?: string
  '3xl'?: string
}

interface Props {
  // 图片源
  src?: string
  // 响应式图片源
  responsiveSrc?: ResponsiveSrc
  // 替代文本
  alt: string
  // 宽高比
  aspectRatio?: 'square' | 'video' | 'portrait' | 'landscape' | string
  // 对象适配
  objectFit?: 'contain' | 'cover' | 'fill' | 'none' | 'scale-down'
  // 对象位置
  objectPosition?: string
  // 圆角
  rounded?: boolean | 'sm' | 'md' | 'lg' | 'xl' | 'full'
  // 是否懒加载
  lazy?: boolean
  // 占位符
  placeholder?: string
  // 是否显示加载占位符
  showPlaceholder?: boolean
  // 是否显示错误占位符
  showErrorPlaceholder?: boolean
  // 自定义宽度
  width?: string
  // 自定义高度
  height?: string
  // 最大宽度
  maxWidth?: string
  // 最大高度
  maxHeight?: string
  // 是否响应式
  responsive?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  objectFit: 'cover',
  objectPosition: 'center',
  rounded: false,
  lazy: false,
  showPlaceholder: true,
  showErrorPlaceholder: true,
  responsive: true,
})

const emit = defineEmits<{
  load: [event: Event]
  error: [event: Event]
}>()

const { currentBreakpoint } = useResponsive()

const isLoading = ref(true)
const hasError = ref(false)
const isIntersecting = ref(false)
const imgRef = ref<HTMLImageElement>()
const observer = ref<IntersectionObserver>()

// 是否启用懒加载
const isLazyLoading = computed(() => props.lazy && 'IntersectionObserver' in window)

// 当前图片源
const currentSrc = computed(() => {
  if (props.responsiveSrc) {
    const bp = currentBreakpoint.value
    const orderedBreakpoints = ['3xl', '2xl', 'xl', 'lg', 'md', 'sm', 'xs'] as const
    const currentIndex = orderedBreakpoints.indexOf(bp)
    
    for (let i = currentIndex; i < orderedBreakpoints.length; i++) {
      const breakpoint = orderedBreakpoints[i]
      if (props.responsiveSrc[breakpoint]) {
        return props.responsiveSrc[breakpoint]!
      }
    }
  }
  
  return props.src || props.placeholder
})

// 容器类名
const containerClasses = computed(() => {
  const classes = ['relative overflow-hidden']
  
  if (props.responsive) {
    classes.push('w-full')
  }
  
  // 圆角
  if (props.rounded) {
    if (typeof props.rounded === 'boolean') {
      classes.push('rounded-lg')
    } else if (props.rounded === 'full') {
      classes.push('rounded-full')
    } else {
      classes.push(`rounded-${props.rounded}`)
    }
  }
  
  return classes
})

// 容器样式
const containerStyles = computed(() => {
  const styles: Record<string, string> = {}
  
  // 宽高比
  if (props.aspectRatio) {
    switch (props.aspectRatio) {
      case 'square':
        styles.aspectRatio = '1 / 1'
        break
      case 'video':
        styles.aspectRatio = '16 / 9'
        break
      case 'portrait':
        styles.aspectRatio = '3 / 4'
        break
      case 'landscape':
        styles.aspectRatio = '4 / 3'
        break
      default:
        styles.aspectRatio = props.aspectRatio
    }
  }
  
  // 自定义尺寸
  if (props.width) styles.width = props.width
  if (props.height) styles.height = props.height
  if (props.maxWidth) styles.maxWidth = props.maxWidth
  if (props.maxHeight) styles.maxHeight = props.maxHeight
  
  return styles
})

// 图片类名
const imageClasses = computed(() => {
  const classes = ['transition-opacity duration-300']
  
  if (props.responsive) {
    classes.push('w-full h-full')
  }
  
  if (isLoading.value) {
    classes.push('opacity-0')
  } else {
    classes.push('opacity-100')
  }
  
  return classes
})

// 图片样式
const imageStyles = computed(() => {
  const styles: Record<string, string> = {}
  
  styles.objectFit = props.objectFit
  styles.objectPosition = props.objectPosition
  
  return styles
})

// 占位符类名
const placeholderClasses = computed(() => {
  const classes = ['absolute inset-0']
  
  if (props.aspectRatio) {
    classes.push('w-full h-full')
  }
  
  return classes
})

// 图片加载完成
const onLoad = (event: Event) => {
  isLoading.value = false
  hasError.value = false
  emit('load', event)
}

// 图片加载错误
const onError = (event: Event) => {
  isLoading.value = false
  hasError.value = true
  emit('error', event)
}

// 设置交叉观察器
const setupIntersectionObserver = () => {
  if (!isLazyLoading.value) {
    isIntersecting.value = true
    return
  }
  
  observer.value = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (entry.isIntersecting) {
          isIntersecting.value = true
          observer.value?.disconnect()
        }
      })
    },
    {
      rootMargin: '50px',
    }
  )
  
  const container = document.querySelector(`[data-img-container]`)
  if (container) {
    observer.value.observe(container)
  }
}

onMounted(() => {
  setupIntersectionObserver()
})

onUnmounted(() => {
  observer.value?.disconnect()
})
</script>

<style scoped>
img {
  display: block;
}
</style>