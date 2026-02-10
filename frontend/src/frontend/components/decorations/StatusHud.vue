<template>
  <div class="flex items-center gap-4 font-mono text-xs text-slate-500 border border-slate-800 bg-slate-900/50 p-2 rounded max-w-fit backdrop-blur-sm">
    <div class="flex flex-col gap-1">
      <div class="flex justify-between w-24">
        <span>CPU</span>
        <span class="text-lab-accent">{{ cpu }}%</span>
      </div>
      <div class="h-1 bg-slate-700 w-full overflow-hidden">
        <div class="h-full bg-lab-accent transition-all duration-300" :style="{ width: cpu + '%' }"></div>
      </div>
    </div>
    <div class="w-px h-6 bg-slate-700"></div>
    <div class="flex flex-col gap-1">
      <div class="flex justify-between w-24">
        <span>MEM</span>
        <span class="text-green-400">{{ mem }}%</span>
      </div>
      <div class="h-1 bg-slate-700 w-full overflow-hidden">
        <div class="h-full bg-green-400 transition-all duration-300" :style="{ width: mem + '%' }"></div>
      </div>
    </div>
    <div class="hidden sm:block w-px h-6 bg-slate-700"></div>
    <div class="hidden sm:flex flex-col gap-1">
      <div class="flex justify-between w-24">
        <span>NET</span>
        <span class="text-blue-400">{{ net }}ms</span>
      </div>
      <div class="flex gap-0.5 mt-0.5">
        <div v-for="i in 5" :key="i" class="w-4 h-1 bg-slate-700" :class="{ 'bg-blue-400': i <= (net < 50 ? 5 : net < 100 ? 3 : 1) }"></div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'

const cpu = ref(12)
const mem = ref(34)
const net = ref(24)
let timer: any

onMounted(() => {
  timer = setInterval(() => {
    cpu.value = Math.floor(Math.random() * 30) + 10
    mem.value = Math.min(Math.floor(mem.value + (Math.random() - 0.5) * 5), 80)
    net.value = Math.floor(Math.random() * 60) + 10
  }, 2000)
})

onUnmounted(() => clearInterval(timer))
</script>
