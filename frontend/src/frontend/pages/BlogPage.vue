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
               <span class="font-mono text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">Knowledge Base</span>
            </div>
            <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter text-slate-900 dark:text-white">
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-lab-accent to-lab-darkAccent">Dev</span> Logs
            </h1>
          </div>
          
          <!-- 统计信息 -->
          <div class="flex flex-col sm:flex-row gap-4">
             <div class="bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 min-w-[140px]">
                <div class="text-xs font-mono text-slate-500 mb-1">TOTAL_LOGS</div>
                <div class="text-2xl font-bold font-mono text-slate-900 dark:text-white">{{ publishedBlogs.length }}</div>
             </div>
             <div class="bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 min-w-[140px]">
                <div class="text-xs font-mono text-slate-500 mb-1">LAST_UPDATE</div>
                <div class="text-2xl font-bold font-mono text-slate-900 dark:text-white">{{ lastUpdateDate }}</div>
             </div>
          </div>
        </div>
      </header>

      <!-- 过滤器区域 - 终端输入风格 -->
      <div class="mb-12 bg-slate-100 dark:bg-[#1f2833] border border-slate-200 dark:border-slate-700 p-4 font-mono text-sm">
         <div class="flex flex-col md:flex-row gap-6 items-start md:items-center justify-between">
            <div class="flex items-center gap-2 w-full md:w-auto">
               <span class="text-lab-accent">></span>
               <span class="text-slate-500 dark:text-slate-400 whitespace-nowrap">SORT_BY:</span>
               <select 
                  v-model="sortBy" 
                  class="bg-transparent border-none text-slate-900 dark:text-white font-bold focus:ring-0 cursor-pointer w-full md:w-auto uppercase"
               >
                  <option value="created_at">DATE_PUBLISHED</option>
                  <option value="updated_at">DATE_MODIFIED</option>
                  <option value="title">TITLE_INDEX</option>
               </select>
            </div>
            
            <div class="flex items-center gap-4 text-xs">
               <button 
                 @click="toggleSortOrder"
                 class="hover:text-lab-accent transition-colors uppercase"
               >
                 ORDER: {{ sortOrder === 'desc' ? 'DESC' : 'ASC' }}
               </button>
               <span class="w-px h-4 bg-slate-300 dark:bg-slate-700"></span>
               <span class="text-green-500">SYSTEM: ONLINE</span>
            </div>
         </div>
      </div>

      <!-- 内容列表 -->
      <div class="min-h-[400px] relative">
         <!-- 加载遮罩 -->
         <div v-if="loading" class="absolute inset-0 z-20 bg-slate-50/80 dark:bg-[#0b0c10]/80 backdrop-blur-sm flex items-center justify-center">
            <div class="font-mono text-lab-accent animate-pulse">> FETCHING_LOGS...</div>
         </div>

         <!-- 博客列表 - 工业风列表 -->
         <div v-if="!loading && sortedBlogs.length > 0" class="space-y-4">
            <article 
               v-for="(blog, index) in sortedBlogs" 
               :key="blog.id"
               class="group relative bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 p-6 md:p-8 hover:border-l-8 hover:border-l-lab-accent transition-all duration-200 cursor-pointer overflow-hidden"
               @click="goToDetail(blog.id)"
            >
               <div class="flex flex-col md:flex-row gap-8 relative z-10">
                  <!-- 元信息列 -->
                  <div class="md:w-48 flex flex-col justify-between shrink-0 border-b md:border-b-0 md:border-r border-slate-100 dark:border-slate-800 pb-4 md:pb-0 md:pr-8">
                     <div class="font-mono text-xs text-slate-500 dark:text-slate-400 space-y-2">
                        <div class="flex items-center gap-2">
                           <span class="w-2 h-2 bg-slate-300 dark:bg-slate-600 rounded-sm"></span>
                           <span>{{ formatDate(blog.created_at) }}</span>
                        </div>
                        <div class="flex items-center gap-2">
                           <span class="w-2 h-2 bg-slate-300 dark:bg-slate-600 rounded-sm"></span>
                           <span>{{ getReadingTime(blog.content) }} MIN READ</span>
                        </div>
                     </div>
                     <div class="mt-4 md:mt-0">
                        <span class="text-[10px] font-mono font-bold uppercase px-2 py-1 bg-slate-100 dark:bg-slate-800 text-slate-600 dark:text-slate-300 border border-slate-200 dark:border-slate-700">
                           {{ blog.tags[0] || 'LOG' }}
                        </span>
                     </div>
                  </div>

                  <!-- 内容主体 -->
                  <div class="flex-1">
                     <h2 class="text-2xl font-bold mb-4 text-slate-900 dark:text-white group-hover:text-lab-darkAccent transition-colors">
                        {{ blog.title }}
                     </h2>
                     <p class="text-slate-600 dark:text-slate-400 leading-relaxed mb-6 font-mono text-sm line-clamp-2">
                        {{ blog.summary || extractSummary(blog.content) }}
                     </p>
                     
                     <div class="flex items-center justify-between">
                        <div class="flex gap-2">
                           <span 
                              v-for="tag in blog.tags.slice(1, 4)" 
                              :key="tag"
                              class="text-[10px] text-slate-400 uppercase font-mono"
                           >
                              #{{ tag }}
                           </span>
                        </div>
                        <div class="flex items-center gap-2 text-xs font-mono font-bold uppercase text-lab-accent group-hover:translate-x-2 transition-transform">
                           <span>Access Log</span>
                           <span class="text-lg">→</span>
                        </div>
                     </div>
                  </div>
               </div>
               
               <!-- 背景装饰数字 -->
               <div class="absolute -right-4 -bottom-8 font-black text-9xl text-slate-100 dark:text-slate-800 opacity-50 pointer-events-none select-none z-0">
                  {{ String(index + 1).padStart(2, '0') }}
               </div>
            </article>
         </div>

         <!-- 空状态 -->
         <div v-if="!loading && sortedBlogs.length === 0" class="flex flex-col items-center justify-center py-20 text-slate-400 font-mono">
            <div class="text-4xl mb-4">∅</div>
            <p>> NO_LOGS_FOUND</p>
         </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { blogAPI } from '../../shared/api'
import type { Blog } from '../../shared/types'

const router = useRouter()

// State
const blogs = ref<Blog[]>([])
const loading = ref(true)
const sortBy = ref<'created_at' | 'updated_at' | 'title'>('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')

// Computed
const publishedBlogs = computed(() => blogs.value.filter(blog => blog.is_published))

const sortedBlogs = computed(() => {
  return [...publishedBlogs.value].sort((a, b) => {
    let comparison = 0
    if (sortBy.value === 'title') {
      comparison = a.title.localeCompare(b.title)
    } else {
      comparison = new Date(a[sortBy.value]).getTime() - new Date(b[sortBy.value]).getTime()
    }
    return sortOrder.value === 'desc' ? -comparison : comparison
  })
})

const lastUpdateDate = computed(() => {
  if (publishedBlogs.value.length === 0) return 'N/A'
  const dates = publishedBlogs.value.map(b => new Date(b.created_at).getTime())
  const maxDate = Math.max(...dates)
  return new Date(maxDate).toISOString().split('T')[0]
})

// Methods
const loadBlogs = async () => {
  try {
    loading.value = true
    const response = await blogAPI.getAll()
    blogs.value = response.data
  } catch (err) {
    console.error('System Error:', err)
  } finally {
    loading.value = false
  }
}

const goToDetail = (id: number) => router.push(`/blog/${id}`)

const formatDate = (dateString: string) => {
  return new Date(dateString).toISOString().split('T')[0]
}

const getReadingTime = (content: string) => {
  const wordCount = content.length
  return Math.max(1, Math.ceil(wordCount / 500)) // 假设阅读速度稍快
}

const extractSummary = (content: string) => {
  const plainText = content.replace(/[#*`_~\[\]()]/g, '').replace(/<[^>]*>/g, '').trim()
  return plainText
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
}

onMounted(loadBlogs)
</script>
