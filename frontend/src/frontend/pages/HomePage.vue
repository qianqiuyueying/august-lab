<template>
  <div class="space-y-24">
    <!-- 主视觉区域 - 工业风终端 -->
    <section class="relative min-h-[85vh] flex items-center justify-center overflow-hidden">
      <!-- 动态数据背景 -->
      <div class="absolute inset-0 pointer-events-none opacity-5 dark:opacity-10">
         <div class="absolute top-10 left-10 font-mono text-xs space-y-2">
            <p>> INITIALIZING SYSTEM...</p>
            <p>> LOADING ASSETS... [OK]</p>
            <p>> CONNECTING TO NEURAL NET... [OK]</p>
         </div>
         <div class="absolute bottom-10 right-10 font-mono text-xs text-right space-y-2">
            <p>CPU: 45% | MEM: 32% | NET: 1.2Gbps</p>
            <p>LOCATION: SECTOR 7G</p>
         </div>
      </div>

      <div class="relative z-10 max-w-5xl mx-auto text-center px-4">
        <!-- 装饰性标签 - 芯片风格 -->
        <div class="inline-flex items-center gap-2 px-3 py-1 mb-8 bg-slate-100 dark:bg-slate-800/50 border border-slate-300 dark:border-slate-700 rounded-sm font-mono text-xs uppercase tracking-widest text-slate-500 dark:text-slate-400">
          <span class="w-2 h-2 bg-lab-accent rounded-full animate-pulse"></span>
          <span>System Status: Online</span>
        </div>
        
        <!-- 主标题 - 打字机效果 -->
        <h1 class="text-5xl md:text-7xl lg:text-8xl font-black tracking-tighter mb-6 relative inline-block">
          <span class="text-slate-900 dark:text-white">HELLO, I'M </span>
          <span class="text-transparent bg-clip-text bg-gradient-to-r from-lab-accent to-lab-darkAccent relative">
            AUGUST
            <!-- 故障效果层 -->
            <span class="absolute top-0 left-0 -ml-1 text-lab-accent opacity-50 animate-pulse hidden group-hover:block" style="clip-path: polygon(0 0, 100% 0, 100% 45%, 0 45%); transform: translate(-2px, 0)">AUGUST</span>
            <span class="absolute top-0 left-0 ml-1 text-red-500 opacity-50 animate-pulse hidden group-hover:block" style="clip-path: polygon(0 60%, 100% 60%, 100% 100%, 0 100%); transform: translate(2px, 0)">AUGUST</span>
          </span>
        </h1>
        
        <!-- 副标题 - 数据流 -->
        <p class="text-xl md:text-2xl text-slate-600 dark:text-slate-400 font-mono mb-12 max-w-2xl mx-auto leading-relaxed border-l-2 border-lab-accent pl-6 text-left">
          <span class="text-lab-accent">const</span> role = <span class="text-green-500">'Full Stack Developer'</span>;<br>
          <span class="text-lab-accent">const</span> mission = <span class="text-green-500">'Crafting Digital Experiences'</span>;<br>
          <span class="text-slate-400">// Combining creativity with engineering precision.</span>
        </p>
        
        <!-- CTA 按钮组 - 硬朗风格 -->
        <div class="flex flex-col sm:flex-row gap-6 justify-center items-center">
          <router-link 
            to="/portfolio" 
            class="group relative px-8 py-4 bg-slate-900 dark:bg-white text-white dark:text-black font-bold uppercase tracking-widest hover:bg-lab-accent dark:hover:bg-lab-accent transition-colors duration-300 overflow-hidden"
          >
            <span class="relative z-10 flex items-center gap-2">
              Explore Projects
              <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3" /></svg>
            </span>
            <!-- 按钮背景扫描动画 -->
            <div class="absolute inset-0 bg-white/20 -translate-x-full group-hover:translate-x-full transition-transform duration-700 ease-in-out skew-x-12"></div>
          </router-link>
          
          <router-link 
            to="/about" 
            class="px-8 py-4 bg-transparent border-2 border-slate-900 dark:border-white text-slate-900 dark:text-white font-bold uppercase tracking-widest hover:bg-slate-900 hover:text-white dark:hover:bg-white dark:hover:text-black transition-all duration-300"
          >
            Read Documentation
          </router-link>
        </div>
      </div>
    </section>

    <!-- 精选作品 - 仪表盘风格 -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div class="flex items-end justify-between mb-12 border-b-2 border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h2 class="text-4xl font-black uppercase tracking-tighter mb-2">
            <span class="text-lab-accent mr-2">/</span>Selected Works
          </h2>
          <p class="font-mono text-sm text-slate-500 dark:text-slate-400">Deployments & Experiments</p>
        </div>
        <router-link to="/portfolio" class="hidden md:flex items-center gap-2 font-mono text-sm font-bold uppercase hover:text-lab-accent transition-colors">
          View All Modules <span class="text-lg">→</span>
        </router-link>
      </div>

      <ErrorBoundary 
        :on-retry="loadPortfolios"
        fallback-title="DATA FETCH FAILED"
        fallback-message="Unable to retrieve project data. Retrying connection..."
      >
        <div v-if="portfolioLoading" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
           <div v-for="i in 3" :key="i" class="bg-slate-100 dark:bg-slate-800 h-96 animate-pulse rounded-sm"></div>
        </div>
        
        <div v-else-if="featuredPortfolios.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          <article 
            v-for="(portfolio, idx) in featuredPortfolios" 
            :key="portfolio.id" 
            class="group bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 hover:border-lab-accent dark:hover:border-lab-accent transition-all duration-300 cursor-pointer flex flex-col h-full"
            @click="goToPortfolioDetail(portfolio.id)"
          >
            <!-- 图片区域 - 带遮罩 -->
            <div class="relative aspect-video overflow-hidden border-b border-slate-200 dark:border-slate-800">
              <ResponsiveImage
                v-if="portfolio.image_url"
                :src="portfolio.image_url"
                :alt="portfolio.title"
                aspect-ratio="video"
                class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500 grayscale group-hover:grayscale-0"
              />
              <div v-else class="w-full h-full bg-slate-100 dark:bg-slate-800 flex items-center justify-center font-mono text-4xl text-slate-300">
                NO_IMG
              </div>
              <!-- 覆盖层 -->
              <div class="absolute inset-0 bg-lab-accent/10 opacity-0 group-hover:opacity-100 transition-opacity duration-300 pointer-events-none mix-blend-overlay"></div>
            </div>
            
            <!-- 内容区域 -->
            <div class="p-6 flex-1 flex flex-col">
              <div class="flex justify-between items-start mb-4">
                 <h3 class="text-xl font-bold uppercase tracking-wide group-hover:text-lab-darkAccent transition-colors line-clamp-1">
                  {{ portfolio.title }}
                </h3>
                <span class="font-mono text-xs text-slate-400">#0{{ idx + 1 }}</span>
              </div>
              
              <p class="text-slate-600 dark:text-slate-400 text-sm font-mono mb-6 line-clamp-3 flex-1">
                {{ portfolio.description || '// No description available.' }}
              </p>
              
              <!-- 底部标签 -->
              <div class="flex flex-wrap gap-2 mt-auto">
                 <span 
                    v-for="tech in portfolio.tech_stack.slice(0, 3)" 
                    :key="tech"
                    class="px-2 py-1 text-[10px] font-mono font-bold uppercase border border-slate-300 dark:border-slate-600 text-slate-600 dark:text-slate-300"
                  >
                    {{ tech }}
                  </span>
              </div>
            </div>
          </article>
        </div>
      </ErrorBoundary>
    </section>

    <!-- 最新日志 - 终端列表风格 -->
    <section class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-24">
      <div class="flex items-end justify-between mb-12 border-b-2 border-slate-200 dark:border-slate-800 pb-4">
        <div>
          <h2 class="text-4xl font-black uppercase tracking-tighter mb-2">
            <span class="text-lab-accent mr-2">/</span>Dev Logs
          </h2>
          <p class="font-mono text-sm text-slate-500 dark:text-slate-400">Thoughts & Updates</p>
        </div>
        <router-link to="/blog" class="hidden md:flex items-center gap-2 font-mono text-sm font-bold uppercase hover:text-lab-accent transition-colors">
          Access Archives <span class="text-lg">→</span>
        </router-link>
      </div>

      <ErrorBoundary :on-retry="loadBlogs">
        <div class="space-y-4">
          <article 
            v-for="blog in recentBlogs" 
            :key="blog.id"
            class="group relative bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 p-6 hover:border-l-8 hover:border-l-lab-accent transition-all duration-200 cursor-pointer"
            @click="goToBlogDetail(blog.id)"
          >
            <div class="flex flex-col md:flex-row md:items-center justify-between gap-4">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2 font-mono text-xs text-slate-500 dark:text-slate-400">
                  <span>{{ formatDate(blog.created_at) }}</span>
                  <span>::</span>
                  <span class="uppercase">{{ blog.tags[0] || 'GENERAL' }}</span>
                </div>
                <h3 class="text-2xl font-bold mb-2 group-hover:text-lab-darkAccent transition-colors">
                  {{ blog.title }}
                </h3>
                <p class="text-slate-600 dark:text-slate-400 line-clamp-1 font-mono text-sm">
                  {{ blog.summary || extractSummary(blog.content) }}
                </p>
              </div>
              <div class="md:text-right">
                <span class="inline-block px-4 py-2 border border-slate-300 dark:border-slate-600 font-mono text-xs font-bold uppercase hover:bg-slate-900 hover:text-white dark:hover:bg-white dark:hover:text-black transition-colors">
                  Read File
                </span>
              </div>
            </div>
          </article>
        </div>
      </ErrorBoundary>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import ResponsiveContainer from '../../shared/components/ResponsiveContainer.vue'
import ResponsiveImage from '../../shared/components/ResponsiveImage.vue'
import ErrorBoundary from '../../shared/components/ErrorBoundary.vue'
import { useDataSync } from '../../shared/composables/useDataStore'
import type { Product } from '../../shared/types'

const router = useRouter()

// 数据存储
const { portfolioStore, blogStore, startAutoSync, stopAutoSync } = useDataSync()

// 计算属性
const featuredPortfolios = computed(() => portfolioStore.featuredPortfolios.value.slice(0, 3))
const recentBlogs = computed(() => blogStore.recentBlogs.value.slice(0, 4)) // 显示4条日志
const portfolioLoading = computed(() => portfolioStore.loading.value)

// 方法
const loadPortfolios = async () => await portfolioStore.fetchPortfolios()
const loadBlogs = async () => await blogStore.fetchBlogs()

const goToPortfolioDetail = (id: number) => router.push(`/portfolio/${id}`)
const goToBlogDetail = (id: number) => router.push(`/blog/${id}`)

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toISOString().split('T')[0] // 工业风只显示 YYYY-MM-DD
}

const extractSummary = (content: string) => {
  const plainText = content.replace(/[#*`_~\[\]()]/g, '').replace(/<[^>]*>/g, '').trim()
  return plainText.length > 100 ? plainText.substring(0, 100) + '...' : plainText
}

// 生命周期
onMounted(async () => {
  startAutoSync()
  await Promise.all([loadPortfolios(), loadBlogs()])
})

onUnmounted(() => stopAutoSync())
</script>

<style scoped>
/* 局部动画优化 */
.bg-clip-text {
  -webkit-background-clip: text;
  background-clip: text;
}
</style>
