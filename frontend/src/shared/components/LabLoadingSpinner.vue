<template>
  <div class="flex flex-col items-center justify-center" :class="containerClass">
    <!-- 粒子汇聚动画：12个蓝点汇聚成 A·L -->
    <div class="relative w-24 h-24" ref="containerRef">
      <!-- 12个粒子点 -->
      <div
        v-for="(particle, index) in particles"
        :key="index"
        class="absolute w-2 h-2 bg-primary-500 rounded-full"
        :style="getParticleStyle(index)"
      ></div>
      
      <!-- A·L 字母（汇聚后显示） -->
      <div
        v-if="showLetters"
        class="absolute inset-0 flex items-center justify-center text-4xl font-bold text-primary-500 dark:text-primary-400"
        style="animation: fadeIn 0.2s ease-out"
      >
        A·L
      </div>
    </div>
    
    <span v-if="text" class="mt-4 text-sm text-gray-600 dark:text-gray-400 font-mono">
      {{ text }}
    </span>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'

interface Props {
  text?: string
  containerClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  text: '系统自检中...'
})

const containerRef = ref<HTMLElement>()
const showLetters = ref(false)
const particles = Array(12).fill(null)

// 计算每个粒子的初始位置和动画延迟
const getParticleStyle = (index: number) => {
  const angle = (index / 12) * Math.PI * 2
  const radius = 40
  const startX = Math.cos(angle) * radius
  const startY = Math.sin(angle) * radius
  
  return {
    '--start-x': `${startX}px`,
    '--start-y': `${startY}px`,
    left: '50%',
    top: '50%',
    transform: 'translate(-50%, -50%)',
    animation: `particleConverge 0.3s ease-out ${index * 0.02}s forwards`,
  } as any
}

onMounted(() => {
  // 300ms后显示字母
  setTimeout(() => {
    showLetters.value = true
  }, 300)
})
</script>

<style scoped>
@keyframes fadeIn {
  from {
    opacity: 0;
  }
  to {
    opacity: 1;
  }
}
</style>

