<template>
  <div class="min-h-screen bg-white dark:bg-slate-900 flex items-center justify-center relative overflow-hidden">
    <!-- 示波器背景 -->
    <div class="absolute inset-0 opacity-10 dark:opacity-20">
      <svg class="w-full h-full" viewBox="0 0 1200 800" preserveAspectRatio="none">
        <!-- 网格线 -->
        <defs>
          <pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">
            <path d="M 40 0 L 0 0 0 40" fill="none" stroke="currentColor" stroke-width="0.5" opacity="0.3"/>
          </pattern>
        </defs>
        <rect width="100%" height="100%" fill="url(#grid)" class="text-primary-500"/>
        
        <!-- ERR_LAB_SAMPLE_LOST 波形 -->
        <path
          :d="waveformPath"
          fill="none"
          stroke="currentColor"
          stroke-width="2"
          class="text-primary-500 dark:text-primary-400"
          opacity="0.6"
        />
        
        <!-- 触发线 -->
        <line
          x1="0"
          y1="400"
          x2="1200"
          y2="400"
          stroke="currentColor"
          stroke-width="1"
          stroke-dasharray="5,5"
          class="text-primary-500 dark:text-primary-400"
          opacity="0.4"
        />
      </svg>
    </div>
    
    <!-- 内容 -->
    <div class="relative z-10 text-center px-4 max-w-2xl">
      <!-- 错误代码 -->
      <div class="mb-8">
        <div class="inline-block px-4 py-2 bg-primary-50 dark:bg-primary-900/30 border border-primary-200 dark:border-primary-800 rounded-lg mb-4">
          <code class="text-primary-600 dark:text-primary-400 font-mono text-sm">
            ERR_LAB_SAMPLE_LOST
          </code>
        </div>
        <h1 class="text-6xl md:text-8xl font-bold text-gray-900 dark:text-gray-50 mb-4">
          404
        </h1>
        <p class="text-xl text-gray-600 dark:text-gray-400 mb-8">
          样本丢失，实验数据未找到
        </p>
      </div>
      
      <!-- 按钮 -->
      <div class="flex flex-col sm:flex-row gap-4 justify-center">
        <router-link
          to="/"
          class="btn-primary inline-flex items-center justify-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          重做实验
        </router-link>
        <button
          @click="$router.go(-1)"
          class="btn-secondary inline-flex items-center justify-center gap-2"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回上一步
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

// 生成 ERR_LAB_SAMPLE_LOST 的 ASCII 波形路径
const waveformPath = computed(() => {
  const text = 'ERR_LAB_SAMPLE_LOST'
  const points: string[] = []
  const width = 1200
  const height = 400
  const centerY = height / 2
  const amplitude = 100
  
  for (let i = 0; i < text.length; i++) {
    const x = (i / text.length) * width
    // 使用字符的ASCII码生成波形
    const charCode = text.charCodeAt(i)
    const y = centerY + Math.sin(charCode / 10) * amplitude
    points.push(`${x},${y}`)
  }
  
  return `M ${points.join(' L ')}`
})
</script>

