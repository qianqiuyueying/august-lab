<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0b0c10] py-12 md:py-20 relative overflow-hidden font-mono">
    <!-- 档案风格背景 -->
    <div class="absolute inset-0 pointer-events-none opacity-5 dark:opacity-10 bg-[length:20px_20px] bg-grid-pattern dark:bg-grid-pattern-dark z-0"></div>
    
    <!-- 左侧装饰标尺 -->
    <div class="fixed left-4 top-1/2 -translate-y-1/2 h-[60vh] w-px bg-slate-300 dark:bg-slate-700 hidden lg:block">
      <div v-for="i in 10" :key="i" class="absolute w-2 h-px bg-slate-400 dark:bg-slate-600 left-[-1px]" :style="{ top: `${(i-1)*10}%` }"></div>
      <div class="absolute top-0 -left-6 text-[10px] text-slate-400 rotate-[-90deg]">ARCHIVE_V.2</div>
    </div>

    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <header class="mb-16 border-b-2 border-slate-200 dark:border-slate-800 pb-8 reveal-on-scroll">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div class="flex items-center gap-3 mb-4">
              <div class="w-3 h-3 border border-lab-accent rotate-45"></div>
              <span class="font-mono text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">DIGITAL ARCHIVE</span>
            </div>
            <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter text-slate-900 dark:text-white">
              <ScrambleText text="PROJECT_MATRIX" />
            </h1>
            <p class="mt-2 text-slate-500 dark:text-slate-400 text-sm max-w-md">
              // 这里的每一行代码，都是思想的快照。
            </p>
          </div>
          <div class="flex items-center gap-4 text-xs font-bold">
            <div class="px-3 py-1 bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-700">
              索引数量: {{ sortedPortfolios.length }}
            </div>
            <StatusHud />
          </div>
        </div>
      </header>

      <!-- 过滤器区域 -->
      <div class="mb-12 border-y border-slate-200 dark:border-slate-800 py-4 font-mono text-sm reveal-on-scroll flex flex-col md:flex-row justify-between items-center gap-4">
         <div class="flex items-center gap-2 w-full md:w-auto">
            <span class="w-1.5 h-1.5 bg-slate-400 rounded-full"></span>
            <span class="text-slate-500 dark:text-slate-400 whitespace-nowrap uppercase">Sort Sequence:</span>
            <select
              v-model="sortBy"
              class="bg-transparent text-slate-900 dark:text-white font-bold focus:ring-0 cursor-pointer w-full md:w-auto px-2 py-1 outline-none uppercase tracking-wider"
            >
              <option value="display_order" class="bg-white dark:bg-slate-800">推荐顺序 [DEF]</option>
              <option value="created_at" class="bg-white dark:bg-slate-800">最新归档 [NEW]</option>
              <option value="title" class="bg-white dark:bg-slate-800">名称索引 [A-Z]</option>
            </select>
         </div>
         <div class="text-xs text-slate-400 uppercase tracking-widest">
            READ_ONLY_ACCESS
         </div>
      </div>

      <!-- 内容网格 -->
      <div class="min-h-[400px] relative">
        <div v-if="isLoading" class="absolute inset-0 z-20 bg-slate-50/80 dark:bg-[#0b0c10]/80 backdrop-blur-sm flex items-center justify-center">
          <div class="font-mono text-lab-accent animate-pulse">> 正在检索档案...</div>
        </div>

        <div v-else-if="sortedPortfolios.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <article
            v-for="(item, idx) in sortedPortfolios"
            :key="item.id"
            class="group relative bg-white dark:bg-[#151f2e] border border-slate-200 dark:border-slate-800 hover:border-slate-400 dark:hover:border-slate-600 transition-all duration-300 cursor-pointer flex flex-col reveal-on-scroll"
            @click="goToDetail(item.id)"
          >
            <!-- 档案编号装饰 -->
            <div class="absolute -top-3 -left-3 bg-slate-100 dark:bg-slate-800 border border-slate-300 dark:border-slate-600 px-2 py-0.5 text-[10px] font-bold z-10 font-mono shadow-sm">
               NO.{{ String(idx + 1).padStart(3, '0') }}
            </div>

            <!-- 角落装饰 -->
            <TechBorder class="h-full flex flex-col">
              <!-- 图片容器 -->
              <div class="relative aspect-video overflow-hidden bg-slate-100 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800">
                <ResponsiveImage
                  v-if="item.image_url"
                  :src="item.image_url"
                  :alt="item.title"
                  aspect-ratio="video"
                  class="w-full h-full object-cover transition-all duration-700 group-hover:scale-105 filter sepia-[0.2] group-hover:sepia-0"
                />
                <div v-else class="w-full h-full flex items-center justify-center font-mono text-slate-300 dark:text-slate-700 text-6xl">
                   ■
                </div>
                <!-- 网格遮罩 -->
                <div class="absolute inset-0 bg-[length:4px_4px] bg-[radial-gradient(rgba(0,0,0,0.1)_1px,transparent_1px)] pointer-events-none"></div>
              </div>

              <!-- 信息区域 -->
              <div class="p-6 flex-1 flex flex-col">
                <h3 class="text-lg font-bold uppercase tracking-wide text-slate-900 dark:text-white mb-2 group-hover:underline decoration-1 underline-offset-4 decoration-slate-400">
                  {{ item.title }}
                </h3>
                <p class="text-slate-500 dark:text-slate-400 text-xs font-mono mb-6 line-clamp-3 flex-1 leading-relaxed border-l-2 border-slate-200 dark:border-slate-700 pl-3">
                  {{ item.description || '档案描述缺失。' }}
                </p>
                <div class="flex flex-wrap gap-2 mt-auto pt-4 border-t border-dashed border-slate-200 dark:border-slate-700">
                  <span
                    v-for="tech in item.tech_stack.slice(0, 4)"
                    :key="tech"
                    class="text-[10px] font-mono font-bold uppercase px-1.5 py-0.5 bg-slate-50 dark:bg-slate-800 text-slate-500 dark:text-slate-400 border border-slate-100 dark:border-slate-700"
                  >
                    {{ tech }}
                  </span>
                </div>
              </div>
            </TechBorder>
          </article>
        </div>

        <div v-else class="flex flex-col items-center justify-center py-20 text-slate-400 font-mono">
          <div class="text-4xl mb-4">∅</div>
          <p>> 档案库为空</p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import ResponsiveImage from '../../shared/components/ResponsiveImage.vue'
import { portfolioAPI } from '../../shared/api'
import type { Portfolio } from '../../shared/types'
import ScrambleText from '../components/decorations/ScrambleText.vue'
import TechBorder from '../components/decorations/TechBorder.vue'
import StatusHud from '../components/decorations/StatusHud.vue'

const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) entry.target.classList.add('is-visible')
  })
}, { threshold: 0.1 })

const router = useRouter()
const portfolios = ref<Portfolio[]>([])
const isLoading = ref(true)
const sortBy = ref<'display_order' | 'created_at' | 'title'>('display_order')

const sortedPortfolios = computed(() => {
  return [...portfolios.value].sort((a, b) => {
    if (sortBy.value === 'created_at') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    if (sortBy.value === 'title') return a.title.localeCompare(b.title)
    return (a.display_order || 0) - (b.display_order || 0)
  })
})

const loadPortfolios = async () => {
  isLoading.value = true
  try {
    const res = await portfolioAPI.getAll()
    portfolios.value = res.data
    setTimeout(() => {
      document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el))
    }, 100)
  } finally {
    isLoading.value = false
  }
}

const goToDetail = (id: number) => router.push(`/portfolio/${id}`)

onMounted(loadPortfolios)
</script>
