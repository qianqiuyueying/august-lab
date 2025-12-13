<!--
响应式网格组件
提供灵活的响应式网格布局功能
-->

<template>
  <div 
    :class="gridClasses"
    :style="gridStyles"
  >
    <slot />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useResponsive, type ResponsiveGridConfig } from '../composables/useResponsive'

interface Props {
  // 响应式列数配置
  cols?: ResponsiveGridConfig
  // 预设配置
  preset?: 'auto' | 'cards' | 'features' | 'team' | 'gallery' | 'blog' | 'portfolio'
  // 间距
  gap?: string | number
  // 响应式间距
  responsiveGap?: {
    xs?: string
    sm?: string
    md?: string
    lg?: string
    xl?: string
    '2xl'?: string
    '3xl'?: string
  }
  // 对齐方式
  align?: 'start' | 'center' | 'end' | 'stretch'
  // 垂直对齐
  alignItems?: 'start' | 'center' | 'end' | 'stretch'
  // 最小列宽
  minColWidth?: string
  // 最大列宽
  maxColWidth?: string
  // 是否自动填充
  autoFit?: boolean
  // 是否自动填充到最小宽度
  autoFill?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  cols: () => ({ xs: 1, sm: 2, md: 3, lg: 4 }),
  gap: '1.5rem',
  align: 'stretch',
  alignItems: 'stretch',
  minColWidth: '250px',
  autoFit: false,
  autoFill: false,
})

const { currentBreakpoint, getGridCols, responsivePresets } = useResponsive()

// 获取网格列数配置
const gridConfig = computed(() => {
  if (props.preset) {
    return responsivePresets.grid[props.preset]
  }
  return props.cols
})

// 计算当前列数
const currentCols = getGridCols(gridConfig.value)

// 计算网格样式类
const gridClasses = computed(() => {
  const classes = ['grid']
  
  // 对齐方式
  if (props.align !== 'stretch') {
    classes.push(`justify-items-${props.align}`)
  }
  
  if (props.alignItems !== 'stretch') {
    classes.push(`items-${props.alignItems}`)
  }
  
  return classes
})

// 计算网格样式
const gridStyles = computed(() => {
  const styles: Record<string, string> = {}
  
  if (props.autoFit && props.minColWidth) {
    styles.gridTemplateColumns = `repeat(auto-fit, minmax(${props.minColWidth}, 1fr))`
  } else if (props.autoFill && props.minColWidth) {
    styles.gridTemplateColumns = `repeat(auto-fill, minmax(${props.minColWidth}, 1fr))`
  } else {
    styles.gridTemplateColumns = `repeat(${currentCols.value}, 1fr)`
  }
  
  // 设置间距
  if (props.responsiveGap) {
    const bp = currentBreakpoint.value
    const orderedBreakpoints = ['3xl', '2xl', 'xl', 'lg', 'md', 'sm', 'xs'] as const
    const currentIndex = orderedBreakpoints.indexOf(bp)
    
    for (let i = currentIndex; i < orderedBreakpoints.length; i++) {
      const breakpoint = orderedBreakpoints[i]
      if (props.responsiveGap[breakpoint]) {
        styles.gap = props.responsiveGap[breakpoint]!
        break
      }
    }
  } else {
    styles.gap = typeof props.gap === 'number' ? `${props.gap}px` : props.gap
  }
  
  // 最大列宽
  if (props.maxColWidth) {
    styles.gridTemplateColumns = styles.gridTemplateColumns.replace('1fr', `minmax(auto, ${props.maxColWidth})`)
  }
  
  return styles
})
</script>

<style scoped>
.grid {
  display: grid;
}
</style>