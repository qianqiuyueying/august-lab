<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0b0c10] py-12 md:py-20 relative overflow-hidden font-mono">
    <!-- 发射台背景 -->
    <div class="absolute inset-0 pointer-events-none opacity-5 dark:opacity-10 bg-[length:40px_40px] bg-grid-pattern dark:bg-grid-pattern-dark z-0"></div>
    <CircuitPattern />

    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <header class="mb-12 border-b-2 border-slate-200 dark:border-slate-800 pb-8 reveal-on-scroll">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div class="flex items-center gap-3 mb-4">
               <div class="w-3 h-3 bg-green-500 rounded-full animate-ping"></div>
               <span class="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">Applications Deck</span>
            </div>
            <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter text-slate-900 dark:text-white">
              <ScrambleText text="LAUNCHPAD" />
            </h1>
          </div>
          
          <div class="flex items-center gap-4 text-xs font-bold">
             <div class="px-4 py-2 bg-slate-900 text-white rounded shadow-lg border border-slate-700">
                活跃节点: <span class="text-green-400">{{ filteredProducts.length }}</span>
             </div>
             <div class="px-4 py-2 bg-slate-900 text-white rounded shadow-lg border border-slate-700 flex items-center gap-2">
                系统负载: <span class="text-lab-accent animate-pulse">OPTIMAL</span>
             </div>
          </div>
        </div>
      </header>

      <!-- 控制面板 -->
      <div class="mb-12 bg-white/50 dark:bg-[#1f2833]/50 backdrop-blur-md border border-slate-200 dark:border-slate-700 p-6 rounded-lg reveal-on-scroll shadow-lg">
         <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            <!-- 搜索框 -->
            <div class="relative group">
               <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-lab-accent transition-colors">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path></svg>
               </span>
               <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="检索模块..." 
                  class="w-full bg-slate-100 dark:bg-slate-900 border-none rounded pl-10 py-2.5 text-sm font-bold text-slate-900 dark:text-white focus:ring-2 focus:ring-lab-accent transition-all"
               >
            </div>

            <!-- 类型筛选 -->
            <div class="flex items-center gap-3 text-sm">
               <span class="text-slate-500 dark:text-slate-400 font-bold uppercase">类型协议:</span>
               <div class="flex gap-2">
                  <button 
                    v-for="type in ['', 'web_app', 'game', 'tool']" 
                    :key="type"
                    @click="selectedType = type"
                    class="px-3 py-1 rounded text-xs font-bold uppercase transition-all border"
                    :class="selectedType === type ? 'bg-lab-accent text-slate-900 border-lab-accent' : 'bg-transparent text-slate-500 border-slate-300 dark:border-slate-700 hover:border-slate-400'"
                  >
                    {{ type || 'ALL' }}
                  </button>
               </div>
            </div>

            <!-- 统计 -->
            <div class="md:text-right text-xs text-slate-500 dark:text-slate-400 flex justify-end items-center gap-2">
               <span class="w-2 h-2 bg-green-500 rounded-full"></span>
               <span>网络连接正常</span>
            </div>
         </div>
      </div>

      <!-- 产品网格 -->
      <div class="relative min-h-[400px]">
         <div v-if="isLoading" class="absolute inset-0 z-20 bg-slate-50/80 dark:bg-[#0b0c10]/80 backdrop-blur-sm flex items-center justify-center">
            <div class="flex flex-col items-center">
               <div class="w-16 h-16 border-4 border-slate-200 dark:border-slate-800 border-t-lab-accent rounded-full animate-spin mb-4 shadow-[0_0_15px_rgba(102,252,241,0.3)]"></div>
               <div class="font-mono text-sm uppercase animate-pulse text-lab-accent">初始化模块中...</div>
            </div>
         </div>

         <div v-if="error" class="flex flex-col items-center justify-center py-20 text-red-500">
            <div class="text-6xl mb-4 opacity-50">⚠</div>
            <p class="font-bold uppercase text-lg">连接失败: {{ error }}</p>
            <button @click="loadProducts" class="mt-6 px-6 py-2 bg-red-500 text-white rounded hover:bg-red-600 transition-colors uppercase text-sm font-bold shadow-lg">
               重试连接序列
            </button>
         </div>

         <div v-else-if="filteredProducts.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <article 
               v-for="(product, idx) in filteredProducts" 
               :key="product.id"
               class="group relative bg-white dark:bg-[#151f2e] rounded-xl overflow-hidden shadow-lg border border-slate-200 dark:border-slate-700 hover:border-lab-accent dark:hover:border-lab-accent transition-all duration-300 transform hover:-translate-y-1 hover:shadow-[0_0_20px_rgba(102,252,241,0.15)] cursor-pointer reveal-on-scroll"
               @click="launchProduct(product)"
            >
               <!-- 全息光效 -->
               <div class="absolute inset-0 bg-gradient-to-b from-transparent via-transparent to-lab-accent/5 opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none"></div>

               <!-- 顶部状态栏 -->
               <div class="h-8 bg-slate-100 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-4 text-[10px] font-mono text-slate-500">
                  <div class="flex items-center gap-2">
                     <span class="w-1.5 h-1.5 bg-green-500 rounded-full animate-pulse"></span>
                     <span>PID: {{ product.id }}</span>
                  </div>
                  <span class="font-bold text-slate-400 group-hover:text-lab-accent transition-colors">READY</span>
               </div>

               <!-- 预览区域 -->
               <div class="relative aspect-video bg-slate-200 dark:bg-slate-900 overflow-hidden">
                  <img 
                     v-if="product.preview_image" 
                     :src="product.preview_image" 
                     :alt="product.title"
                     class="w-full h-full object-cover transition-all duration-700 group-hover:scale-110"
                  >
                  <div v-else class="w-full h-full flex items-center justify-center text-5xl text-slate-400 bg-grid-pattern dark:bg-grid-pattern-dark">
                     {{ getProductIcon(product.product_type) }}
                  </div>
                  
                  <!-- 启动覆盖层 -->
                  <div class="absolute inset-0 flex items-center justify-center bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-[2px]">
                     <button class="px-8 py-3 bg-lab-accent text-slate-900 font-black uppercase tracking-widest hover:bg-white transition-all transform scale-90 group-hover:scale-100 shadow-[0_0_20px_rgba(102,252,241,0.5)] skew-x-[-10deg]">
                        <span class="skew-x-[10deg] inline-block">启动应用</span>
                     </button>
                  </div>
               </div>

               <!-- 信息区域 -->
               <div class="p-6 relative">
                  <div class="absolute top-0 right-6 -translate-y-1/2 bg-slate-900 text-white text-[10px] font-bold px-3 py-1 rounded-full border border-slate-700 uppercase shadow-md">
                     {{ product.product_type }}
                  </div>

                  <h3 class="text-xl font-bold uppercase text-slate-900 dark:text-white mb-2 group-hover:text-lab-darkAccent transition-colors truncate">
                     {{ product.title }}
                  </h3>
                  
                  <p class="text-sm text-slate-600 dark:text-slate-400 mb-6 line-clamp-2 h-10 leading-relaxed">
                     {{ product.description }}
                  </p>
                  
                  <!-- 底部数据 -->
                  <div class="flex justify-between items-center pt-4 border-t border-slate-100 dark:border-slate-800 text-xs font-mono text-slate-500">
                     <div class="flex items-center gap-1">
                        <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path></svg>
                        <span>{{ product.view_count }}</span>
                     </div>
                     <span>VER: 1.0.{{ product.id }}</span>
                  </div>
               </div>
            </article>
         </div>

         <div v-else class="flex flex-col items-center justify-center py-20 text-slate-400 font-mono">
            <div class="text-6xl mb-4 opacity-30">∅</div>
            <p class="text-lg font-bold">未探测到模块</p>
            <p class="text-xs mt-2 opacity-60">请调整传感器参数 (搜索条件)。</p>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useProductStore } from '../composables/useProductStore'
import type { Product } from '../../shared/types'
import ScrambleText from '../components/decorations/ScrambleText.vue'
import CircuitPattern from '../components/decorations/CircuitPattern.vue'

const router = useRouter()
const { fetchProducts } = useProductStore()

const products = ref<Product[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)
const searchQuery = ref('')
const selectedType = ref('')

// 滚动监听
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible')
    }
  })
}, { threshold: 0.1 })

const filteredProducts = computed(() => {
  return products.value.filter(p => {
    if (!p.is_published) return false
    if (selectedType.value && p.product_type !== selectedType.value) return false
    if (searchQuery.value) {
      const q = searchQuery.value.toLowerCase()
      return p.title.toLowerCase().includes(q) || 
             p.description?.toLowerCase().includes(q) ||
             p.tech_stack?.some(t => t.toLowerCase().includes(q))
    }
    return true
  })
})

const loadProducts = async () => {
  isLoading.value = true
  error.value = null
  try {
    products.value = await fetchProducts()
    setTimeout(() => {
      document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el))
    }, 100)
  } catch (err: any) {
    error.value = err.message || '网络连接中断'
  } finally {
    isLoading.value = false
  }
}

const launchProduct = (product: Product) => {
  router.push({ path: `/product/${product.id}`, query: { from: 'products' } })
}

const getProductIcon = (type: string) => {
  const map: Record<string, string> = { web_app: '🌐', game: '🎮', tool: '🔧' }
  return map[type] || '📦'
}

const formatDate = (dateString: string) => {
  return new Date(dateString).toISOString().split('T')[0]
}

onMounted(loadProducts)
</script>
