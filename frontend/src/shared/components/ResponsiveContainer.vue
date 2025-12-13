<!--
响应式容器组件
提供响应式的容器布局和间距
-->

<template>
  <div 
    :class="containerClasses"
    :style="containerStyles"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useResponsive } from '../composables/useResponsive'

interface Props {
  // 容器大小
  size?: 'sm' | 'md' | 'lg' | 'xl' | 'full'
  // 是否居中
  center?: boolean
  // 响应式内边距
  padding?: {
    xs?: string
    sm?: string
    md?: string
    lg?: string
    xl?: string
    '2xl'?: string
    '3xl'?: string
  }
  // 响应式外边距
  margin?: {
    xs?: string
    sm?: string
    md?: string
    lg?: string
    xl?: string
    '2xl'?: string
    '3xl'?: string
  }
  // 固定内边距
  fixedPadding?: string
  // 固定外边距
  fixedMargin?: string
  // 是否流体布局
  fluid?: boolean
  // 自定义最大宽度
  maxWidth?: string
  // 背景色
  background?: 'transparent' | 'white' | 'gray' | 'primary'
  // 是否有阴影
  shadow?: boolean
  // 圆角
  rounded?: boolean | 'sm' | 'md' | 'lg' | 'xl'
  // 边框
  border?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  size: 'lg',
  center: true,
  background: 'transparent',
  shadow: false,
  rounded: false,
  border: false,
})

const { currentBreakpoint } = useResponsive()

// 容器大小映射
const sizeMap = {
  sm: 'max-w-2xl',
  md: 'max-w-4xl',
  lg: 'max-w-7xl',
  xl: 'max-w-8xl',
  full: 'max-w-full',
}

// 计算容器类名
const containerClasses = computed(() => {
  const classes = []
  
  // 基础容器类
  if (!props.fluid) {
    classes.push('container')
  }
  
  // 大小
  if (props.size !== 'full' && !props.maxWidth) {
    classes.push(sizeMap[props.size])
  }
  
  // 居中
  if (props.center) {
    classes.push('mx-auto')
  }
  
  // 背景色
  switch (props.background) {
    case 'white':
      classes.push('bg-white')
      break
    case 'gray':
      classes.push('bg-gray-50')
      break
    case 'primary':
      classes.push('bg-primary-50')
      break
  }
  
  // 阴影
  if (props.shadow) {
    classes.push('shadow-sm')
  }
  
  // 圆角
  if (props.rounded) {
    if (typeof props.rounded === 'boolean') {
      classes.push('rounded-lg')
    } else {
      classes.push(`rounded-${props.rounded}`)
    }
  }
  
  // 边框
  if (props.border) {
    classes.push('border border-gray-200')
  }
  
  return classes
})

// 计算容器样式
const containerStyles = computed(() => {
  const styles: Record<string, string> = {}
  
  // 自定义最大宽度
  if (props.maxWidth) {
    styles.maxWidth = props.maxWidth
  }
  
  // 响应式内边距
  if (props.padding) {
    const bp = currentBreakpoint.value
    const orderedBreakpoints = ['3xl', '2xl', 'xl', 'lg', 'md', 'sm', 'xs'] as const
    const currentIndex = orderedBreakpoints.indexOf(bp)
    
    for (let i = currentIndex; i < orderedBreakpoints.length; i++) {
      const breakpoint = orderedBreakpoints[i]
      if (props.padding[breakpoint]) {
        styles.padding = props.padding[breakpoint]!
        break
      }
    }
  } else if (props.fixedPadding) {
    styles.padding = props.fixedPadding
  }
  
  // 响应式外边距
  if (props.margin) {
    const bp = currentBreakpoint.value
    const orderedBreakpoints = ['3xl', '2xl', 'xl', 'lg', 'md', 'sm', 'xs'] as const
    const currentIndex = orderedBreakpoints.indexOf(bp)
    
    for (let i = currentIndex; i < orderedBreakpoints.length; i++) {
      const breakpoint = orderedBreakpoints[i]
      if (props.margin[breakpoint]) {
        styles.margin = props.margin[breakpoint]!
        break
      }
    }
  } else if (props.fixedMargin) {
    styles.margin = props.fixedMargin
  }
  
  return styles
})
</script>

<style scoped>
.container {
  width: 100%;
  padding-left: 1rem;
  padding-right: 1rem;
}

@media (min-width: 640px) {
  .container {
    padding-left: 1.5rem;
    padding-right: 1.5rem;
  }
}

@media (min-width: 1024px) {
  .container {
    padding-left: 2rem;
    padding-right: 2rem;
  }
}
</style>