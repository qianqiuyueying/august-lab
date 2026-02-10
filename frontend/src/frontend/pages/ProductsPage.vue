<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0b0c10] py-12 md:py-20 relative overflow-hidden font-mono">
    <!-- 背景扫描线 -->
    <div class="absolute inset-0 pointer-events-none opacity-5 dark:opacity-10 bg-[length:40px_40px] bg-grid-pattern dark:bg-grid-pattern-dark z-0"></div>

    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 - 控制台风格 -->
      <header class="mb-12 border-b-2 border-slate-200 dark:border-slate-800 pb-8 reveal-on-scroll">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div class="flex items-center gap-3 mb-4">
               <div class="w-3 h-3 bg-lab-accent rounded-sm animate-pulse"></div>
               <span class="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">Applications Deck</span>
            </div>
            <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter text-slate-900 dark:text-white">
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-lab-accent to-lab-darkAccent">在线</span> 产品
            </h1>
          </div>
          
          <div class="flex items-center gap-4 text-xs font-bold">
             <div class="px-3 py-1 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                活跃节点: {{ filteredProducts.length }}
             </div>
             <div class="px-3 py-1 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 text-green-500">
                系统状态: 稳定
             </div>
          </div>
        </div>
      </header>

      <!-- 控制面板 -->
      <div class="mb-12 bg-slate-100 dark:bg-[#1f2833] border border-slate-200 dark:border-slate-700 p-4 reveal-on-scroll">
         <div class="grid grid-cols-1 md:grid-cols-3 gap-6 items-center">
            <!-- 搜索框 -->
            <div class="relative group">
               <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 group-focus-within:text-lab-accent transition-colors">></span>
               <input 
                  v-model="searchQuery" 
                  type="text" 
                  placeholder="搜索模块..." 
                  class="w-full bg-transparent border-b-2 border-slate-300 dark:border-slate-600 focus:border-lab-accent pl-8 py-2 text-sm font-bold uppercase outline-none transition-colors text-slate-900 dark:text-white"
               >
            </div>

            <!-- 类型筛选 -->
            <div class="flex items-center gap-2 text-sm">
               <span class="text-slate-500 dark:text-slate-400">类型:</span>
               <select 
                  v-model="selectedType" 
                  class="bg-transparent border-none font-bold uppercase text-slate-900 dark:text-white focus:ring-0 cursor-pointer"
               >
                  <option value="" class="bg-white dark:bg-slate-800">所有模块</option>
                  <option value="web_app" class="bg-white dark:bg-slate-800">Web应用</option>
                  <option value="game" class="bg-white dark:bg-slate-800">模拟程序</option>
                  <option value="tool" class="bg-white dark:bg-slate-800">实用工具</option>
               </select>
            </div>

            <!-- 统计 -->
            <div class="md:text-right text-xs text-slate-500 dark:text-slate-400">
               <span>部署区域: 全球</span>
            </div>
         </div>
      </div>

      <!-- 产品网格 -->
      <div class="relative min-h-[400px]">
         <!-- 加载状态 -->
         <div v-if="isLoading" class="absolute inset-0 z-20 bg-slate-50/80 dark:bg-[#0b0c10]/80 backdrop-blur-sm flex items-center justify-center">
            <div class="flex flex-col items-center">
               <div class="w-12 h-12 border-4 border-slate-200 dark:border-slate-800 border-t-lab-accent rounded-full animate-spin mb-4"></div>
               <div class="font-mono text-xs uppercase animate-pulse">正在加载模块...</div>
            </div>
         </div>

         <!-- 错误提示 -->
         <div v-if="error" class="flex flex-col items-center justify-center py-20 text-red-500">
            <div class="text-4xl mb-4">⚠</div>
            <p class="font-bold uppercase">系统错误: {{ error }}</p>
            <button @click="loadProducts" class="mt-4 px-4 py-2 border border-red-500 hover:bg-red-500 hover:text-white transition-colors uppercase text-xs font-bold">
               重试连接
            </button>
         </div>

         <!-- 产品列表 -->
         <div v-else-if="filteredProducts.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
            <article 
               v-for="(product, idx) in filteredProducts" 
               :key="product.id"
               class="group relative bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 hover:border-lab-accent dark:hover:border-lab-accent transition-all duration-300 flex flex-col h-full overflow-hidden reveal-on-scroll"
               @click="launchProduct(product)"
            >
               <!-- 顶部状态栏 -->
               <div class="h-6 bg-slate-100 dark:bg-slate-900 border-b border-slate-200 dark:border-slate-800 flex items-center justify-between px-3 text-[10px] font-mono text-slate-500">
                  <span>ID: {{ product.id }}</span>
                  <div class="flex gap-1">
                     <div class="w-2 h-2 rounded-full bg-red-400"></div>
                     <div class="w-2 h-2 rounded-full bg-yellow-400"></div>
                     <div class="w-2 h-2 rounded-full bg-green-400"></div>
                  </div>
               </div>

               <!-- 预览区域 (去除灰度) -->
               <div class="relative aspect-video bg-slate-200 dark:bg-slate-900 overflow-hidden group-hover:opacity-90 transition-opacity">
                  <img 
                     v-if="product.preview_image" 
                     :src="product.preview_image" 
                     :alt="product.title"
                     class="w-full h-full object-cover transition-all duration-500"
                  >
                  <div v-else class="w-full h-full flex items-center justify-center text-4xl text-slate-400">
                     {{ getProductIcon(product.product_type) }}
                  </div>
                  
                  <!-- 启动覆盖层 -->
                  <div class="absolute inset-0 flex items-center justify-center bg-black/60 opacity-0 group-hover:opacity-100 transition-opacity backdrop-blur-sm">
                     <button class="px-6 py-2 border-2 border-lab-accent text-lab-accent font-bold uppercase tracking-widest hover:bg-lab-accent hover:text-black transition-all transform translate-y-4 group-hover:translate-y-0">
                        启动应用
                     </button>
                  </div>
               </div>

               <!-- 信息区域 -->
               <div class="p-6 flex-1 flex flex-col">
                  <div class="flex justify-between items-start mb-4">
                     <h3 class="text-xl font-bold uppercase text-slate-900 dark:text-white group-hover:text-lab-darkAccent transition-colors">
                        {{ product.title }}
                     </h3>
                     <span class="text-[10px] uppercase font-bold px-2 py-1 bg-slate-100 dark:bg-slate-800 border border-slate-200 dark:border-slate-700">
                        {{ product.product_type }}
                     </span>
                  </div>
                  
                  <p class="text-sm text-slate-600 dark:text-slate-400 mb-6 flex-1 line-clamp-3">
                     {{ product.description }}
                  </p>
                  
                  <!-- 底部数据 -->
                  <div class="flex justify-between items-center pt-4 border-t border-slate-100 dark:border-slate-800/50 text-xs font-mono text-slate-500">
                     <span>v1.0.{{ product.view_count }}</span>
                     <span>{{ formatDate(product.created_at) }}</span>
                  </div>
               </div>
            </article>
         </div>

         <!-- 空状态 -->
         <div v-else class="flex flex-col items-center justify-center py-20 text-slate-400 font-mono">
            <div class="text-4xl mb-4">∅</div>
            <p>> 未找到模块</p>
            <p class="text-xs mt-2">请调整搜索参数。</p>
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

const router = useRouter()
const { fetchProducts } = useProductStore()

// State
const products = ref<Product[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)
const searchQuery = ref('')
const selectedType = ref('')

// Computed
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

// 滚动监听
const observer = new IntersectionObserver((entries) => {
  entries.forEach(entry => {
    if (entry.isIntersecting) {
      entry.target.classList.add('is-visible')
    }
  })
}, { threshold: 0.1 })

// Methods
const loadProducts = async () => {
  isLoading.value = true
  error.value = null
  try {
    products.value = await fetchProducts()
    
    // 下一次 tick 启动监听
    setTimeout(() => {
      document.querySelectorAll('.reveal-on-scroll').forEach(el => observer.observe(el))
    }, 100)
  } catch (err: any) {
    error.value = err.message || 'CONNECTION_FAILED'
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
