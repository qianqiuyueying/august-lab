<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0b0c10] py-12 md:py-20 relative overflow-hidden">
    <!-- 背景扫描线 -->
    <div class="absolute inset-0 pointer-events-none opacity-5 dark:opacity-10 bg-[length:40px_40px] bg-grid-pattern dark:bg-grid-pattern-dark z-0"></div>

    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 - 数据面板风格 -->
      <header class="mb-16 border-b-2 border-slate-200 dark:border-slate-800 pb-8">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div class="flex items-center gap-3 mb-4">
               <div class="w-3 h-3 bg-lab-accent rounded-sm animate-pulse"></div>
               <span class="font-mono text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">System Module</span>
            </div>
            <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter text-slate-900 dark:text-white">
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-lab-accent to-lab-darkAccent">Project</span> Matrix
            </h1>
          </div>
          
          <!-- 控制台 -->
          <div class="flex flex-col sm:flex-row gap-4">
             <!-- 标签切换 - 物理开关风格 -->
             <div class="inline-flex bg-slate-200 dark:bg-slate-800 p-1 rounded-sm">
                <button
                  @click="currentTab = 'portfolio'"
                  class="px-6 py-2 font-mono text-sm font-bold uppercase transition-all duration-200 rounded-sm"
                  :class="currentTab === 'portfolio' ? 'bg-white dark:bg-lab-accent text-slate-900 dark:text-black shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'"
                >
                  Works
                </button>
                <button
                  @click="currentTab = 'products'"
                  class="px-6 py-2 font-mono text-sm font-bold uppercase transition-all duration-200 rounded-sm"
                  :class="currentTab === 'products' ? 'bg-white dark:bg-lab-accent text-slate-900 dark:text-black shadow-sm' : 'text-slate-500 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white'"
                >
                  Products
                </button>
             </div>
          </div>
        </div>
      </header>

      <!-- 过滤器区域 - 终端输入风格 -->
      <div class="mb-12 bg-slate-100 dark:bg-[#1f2833] border border-slate-200 dark:border-slate-700 p-4 font-mono text-sm">
         <div class="flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
            <div class="flex items-center gap-2 w-full md:w-auto">
               <span class="text-lab-accent">></span>
               <span class="text-slate-500 dark:text-slate-400 whitespace-nowrap">FILTER:</span>
               <select 
                  v-if="currentTab === 'portfolio'"
                  v-model="sortBy" 
                  class="bg-transparent border-none text-slate-900 dark:text-white font-bold focus:ring-0 cursor-pointer w-full md:w-auto"
               >
                  <option value="display_order">RECOMMENDED</option>
                  <option value="created_at">LATEST_DEPLOY</option>
                  <option value="title">ALPHABETICAL</option>
               </select>
               <select 
                  v-else
                  v-model="selectedProductType"
                  class="bg-transparent border-none text-slate-900 dark:text-white font-bold focus:ring-0 cursor-pointer w-full md:w-auto"
               >
                  <option value="">ALL_TYPES</option>
                  <option value="web_app">WEB_APP</option>
                  <option value="game">GAME_ENGINE</option>
                  <option value="tool">UTILITY</option>
               </select>
            </div>
            
            <div class="flex items-center gap-4 text-xs">
               <span class="text-slate-400">TOTAL_ITEMS: {{ currentItemsCount }}</span>
               <span class="w-px h-4 bg-slate-300 dark:bg-slate-700"></span>
               <span class="text-green-500">STATUS: READY</span>
            </div>
         </div>
      </div>

      <!-- 内容网格 -->
      <div class="min-h-[400px] relative">
         <!-- 加载遮罩 -->
         <div v-if="isLoading" class="absolute inset-0 z-20 bg-slate-50/80 dark:bg-[#0b0c10]/80 backdrop-blur-sm flex items-center justify-center">
            <div class="font-mono text-lab-accent animate-pulse">> FETCHING_DATA...</div>
         </div>

         <!-- 作品列表 -->
         <div v-if="currentTab === 'portfolio' && !isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <article 
               v-for="(item, idx) in sortedPortfolios" 
               :key="item.id"
               class="group relative bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 hover:border-lab-accent dark:hover:border-lab-accent transition-all duration-300 cursor-pointer flex flex-col"
               @click="goToDetail(item.id)"
            >
               <!-- 角标装饰 -->
               <div class="absolute top-0 right-0 p-2 z-10 opacity-0 group-hover:opacity-100 transition-opacity">
                  <div class="w-2 h-2 bg-lab-accent rounded-full shadow-[0_0_10px_#66fcf1]"></div>
               </div>

               <!-- 图片容器 -->
               <div class="relative aspect-video overflow-hidden border-b border-slate-200 dark:border-slate-800 bg-slate-100 dark:bg-slate-900">
                  <ResponsiveImage
                     v-if="item.image_url"
                     :src="item.image_url"
                     :alt="item.title"
                     aspect-ratio="video"
                     class="w-full h-full object-cover grayscale group-hover:grayscale-0 transition-all duration-500 group-hover:scale-105"
                  />
                  <div v-else class="w-full h-full flex items-center justify-center font-mono text-slate-400 dark:text-slate-600 text-4xl">
                     NO_SIGNAL
                  </div>
                  <!-- 扫描线遮罩 -->
                  <div class="absolute inset-0 bg-[linear-gradient(transparent_50%,rgba(0,0,0,0.2)_50%)] bg-[length:100%_4px] pointer-events-none opacity-20"></div>
               </div>

               <!-- 信息区域 -->
               <div class="p-6 flex-1 flex flex-col">
                  <div class="flex justify-between items-start mb-4">
                     <h3 class="text-xl font-bold uppercase tracking-wide text-slate-900 dark:text-white group-hover:text-lab-darkAccent transition-colors">
                        {{ item.title }}
                     </h3>
                     <span class="font-mono text-xs text-slate-400">ID:{{ String(item.id).padStart(3, '0') }}</span>
                  </div>
                  
                  <p class="text-slate-600 dark:text-slate-400 text-sm font-mono mb-6 line-clamp-3 flex-1">
                     {{ item.description || 'No description data.' }}
                  </p>
                  
                  <div class="flex flex-wrap gap-2 mt-auto pt-4 border-t border-slate-100 dark:border-slate-800/50">
                     <span 
                        v-for="tech in item.tech_stack.slice(0, 4)" 
                        :key="tech"
                        class="text-[10px] font-mono font-bold uppercase px-1.5 py-0.5 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300"
                     >
                        {{ tech }}
                     </span>
                  </div>
               </div>
            </article>
         </div>

         <!-- 产品列表 -->
         <div v-else-if="currentTab === 'products' && !isLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <article 
               v-for="product in filteredProducts" 
               :key="product.id"
               class="group relative bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 hover:border-lab-accent dark:hover:border-lab-accent transition-all duration-300 cursor-pointer overflow-hidden"
               @click="launchProduct(product)"
            >
               <div class="p-6 h-full flex flex-col">
                  <div class="flex justify-between items-start mb-6">
                     <div class="w-12 h-12 bg-slate-100 dark:bg-slate-800 flex items-center justify-center text-2xl group-hover:bg-lab-accent group-hover:text-black transition-colors duration-300">
                        {{ getProductIcon(product.product_type) }}
                     </div>
                     <span class="font-mono text-[10px] px-2 py-1 bg-slate-100 dark:bg-slate-800 uppercase tracking-wider">
                        {{ product.product_type }}
                     </span>
                  </div>
                  
                  <h3 class="text-xl font-bold uppercase mb-2 group-hover:text-lab-darkAccent transition-colors">
                     {{ product.title }}
                  </h3>
                  
                  <p class="text-slate-600 dark:text-slate-400 text-sm font-mono mb-6 flex-1">
                     {{ product.description }}
                  </p>
                  
                  <div class="flex items-center justify-between mt-auto">
                     <span class="text-xs font-mono text-slate-400">> EXECUTE</span>
                     <svg class="w-4 h-4 text-lab-accent transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
                  </div>
               </div>
               
               <!-- 底部进度条装饰 -->
               <div class="absolute bottom-0 left-0 h-1 bg-lab-accent w-0 group-hover:w-full transition-all duration-500 ease-in-out"></div>
            </article>
         </div>

         <!-- 空状态 -->
         <div v-if="!isLoading && currentItemsCount === 0" class="flex flex-col items-center justify-center py-20 text-slate-400 font-mono">
            <div class="text-4xl mb-4">⚠</div>
            <p>> NO_DATA_FOUND</p>
            <p class="text-xs mt-2">Check filter parameters or try again later.</p>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ResponsiveImage from '../../shared/components/ResponsiveImage.vue'
import { portfolioAPI } from '../../shared/api'
import { useProductStore } from '../composables/useProductStore'
import type { Portfolio, Product } from '../../shared/types'

const router = useRouter()
const route = useRoute()
const { fetchProducts } = useProductStore()

// State
const currentTab = ref<'portfolio' | 'products'>((route.query.tab as any) || 'portfolio')
const portfolios = ref<Portfolio[]>([])
const products = ref<Product[]>([])
const isLoading = ref(true)
const sortBy = ref('display_order')
const selectedProductType = ref('')

// Computed
const sortedPortfolios = computed(() => {
  return [...portfolios.value].sort((a, b) => {
    if (sortBy.value === 'created_at') return new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
    if (sortBy.value === 'title') return a.title.localeCompare(b.title)
    return (a.display_order || 0) - (b.display_order || 0)
  })
})

const filteredProducts = computed(() => {
  return products.value.filter(p => 
    p.is_published && (!selectedProductType.value || p.product_type === selectedProductType.value)
  )
})

const currentItemsCount = computed(() => 
  currentTab.value === 'portfolio' ? sortedPortfolios.value.length : filteredProducts.value.length
)

// Methods
const loadData = async () => {
  isLoading.value = true
  try {
    const [portData, prodData] = await Promise.all([
      portfolioAPI.getAll(),
      fetchProducts()
    ])
    portfolios.value = portData.data
    products.value = prodData
  } catch (e) {
    console.error('System Error:', e)
  } finally {
    isLoading.value = false
  }
}

const goToDetail = (id: number) => router.push(`/portfolio/${id}`)
const launchProduct = (product: Product) => router.push(`/product/${product.id}`)

const getProductIcon = (type: string) => {
  const map: Record<string, string> = { web_app: '🌐', game: '🎮', tool: '🔧', demo: '⚡' }
  return map[type] || '📦'
}

// Watchers
watch(currentTab, (val) => {
  router.replace({ query: { ...route.query, tab: val } })
})

onMounted(loadData)
</script>
