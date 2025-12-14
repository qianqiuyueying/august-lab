<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-900 via-purple-900 to-slate-900">
    <!-- 页面头部 - 杂志风格 -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
        <div class="absolute inset-0 opacity-30">
          <div class="absolute top-0 right-0 w-96 h-96 bg-purple-500 rounded-full blur-3xl"></div>
          <div class="absolute bottom-0 left-0 w-96 h-96 bg-pink-500 rounded-full blur-3xl"></div>
        </div>
      </div>
      
      <ResponsiveContainer size="xl" class="relative z-10 py-20">
        <div class="text-center">
          <div class="inline-block mb-4">
            <span class="text-sm font-bold text-pink-400 uppercase tracking-wider">Blog</span>
          </div>
          <h1 class="text-6xl md:text-7xl font-black text-white mb-6 leading-tight">
            技术<span class="bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">博客</span>
          </h1>
          <p class="text-xl text-white/80 max-w-3xl mx-auto">
            分享技术心得、开发经验和生活感悟，记录成长路上的点点滴滴
          </p>
        </div>
      </ResponsiveContainer>
    </section>

    <!-- 博客展示区域 -->
    <section class="py-12">
      <ResponsiveContainer size="xl">
        <!-- 排序和筛选控制 -->
        <div v-if="!loading && !error && blogs.length > 0" class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div class="flex items-center gap-4">
            <label class="text-sm font-medium text-gray-700">排序方式:</label>
            <select 
              v-model="sortBy" 
              @change="sortBlogs"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="created_at">发布时间</option>
              <option value="updated_at">更新时间</option>
              <option value="title">文章标题</option>
            </select>
            <button 
              @click="toggleSortOrder"
              class="p-2 text-gray-500 hover:text-gray-700 transition-colors"
              :title="sortOrder === 'desc' ? '降序' : '升序'"
            >
              <svg 
                class="w-4 h-4 transition-transform duration-200" 
                :class="{ 'rotate-180': sortOrder === 'asc' }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
          
          <div class="flex items-center gap-2">
            <span class="text-sm text-gray-500">共 {{ publishedBlogs.length }} 篇文章</span>
            <button 
              v-if="hasFilteredResults"
              @click="clearFilters"
              class="text-sm text-primary-600 hover:text-primary-700"
            >
              清除筛选
            </button>
          </div>
        </div>

        <!-- 加载状态 -->
        <div v-if="loading" class="loading-responsive text-center py-20">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500 mx-auto"></div>
          <p class="text-white/60 mt-4">加载博客中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-responsive text-center py-20">
          <svg class="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="text-2xl font-bold text-red-400 mb-2">加载失败</h3>
          <p class="text-red-300 mb-4">{{ error }}</p>
          <button @click="loadBlogs" class="px-6 py-3 bg-gradient-to-r from-pink-600 to-purple-600 text-white font-bold rounded-xl hover:shadow-lg transition-all">
            重试
          </button>
        </div>

        <!-- 博客列表 - 杂志风格 -->
        <div v-else-if="sortedBlogs.length > 0" class="space-y-8">
          <article 
            v-for="(blog, index) in sortedBlogs" 
            :key="blog.id"
            class="group cursor-pointer"
            :class="index === 0 ? 'md:col-span-2' : ''"
            :style="{ animationDelay: `${index * 100}ms` }"
            @click="goToDetail(blog.id)"
          >
            <div class="bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 overflow-hidden shadow-2xl hover:bg-white/15 transition-all duration-500 transform hover:-translate-y-2 hover:scale-[1.01]">
              <!-- 封面图片 -->
              <div v-if="blog.cover_image" class="relative overflow-hidden bg-gradient-to-br from-pink-500/20 to-purple-500/20" :class="index === 0 ? 'h-64' : 'aspect-video'">
                <ResponsiveImage
                  :src="blog.cover_image"
                  :alt="blog.title"
                  :aspect-ratio="index === 0 ? undefined : 'video'"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                  loading="lazy"
                />
                <div class="absolute inset-0 bg-gradient-to-t from-black/60 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              </div>
              
              <!-- 文章内容 -->
              <div class="p-6 md:p-8">
                <!-- 文章元信息 -->
                <div class="flex items-center text-sm mb-5">
                  <div class="flex items-center bg-white/20 backdrop-blur-sm text-white px-3 py-1.5 rounded-full font-medium">
                    <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                    </svg>
                    <time>{{ formatDate(blog.created_at) }}</time>
                  </div>
                  <span class="mx-3 text-white/30">•</span>
                  <span class="text-pink-300 font-medium">{{ getReadingTime(blog.content) }} 分钟阅读</span>
                </div>
                
                <!-- 文章标题 -->
                <h2 class="text-2xl md:text-3xl font-black text-white mb-4 group-hover:text-pink-300 transition-colors duration-300 line-clamp-2">
                  {{ blog.title }}
                </h2>
                
                <!-- 文章摘要 -->
                <p class="text-white/70 leading-relaxed mb-6 line-clamp-3 text-base">
                  {{ blog.summary || extractSummary(blog.content) }}
                </p>
                
                <!-- 标签和阅读更多 -->
                <div class="flex items-center justify-between pt-4 border-t border-white/20">
                  <div class="flex flex-wrap gap-2">
                    <span 
                      v-for="tag in blog.tags.slice(0, 3)" 
                      :key="tag"
                      class="px-3 py-1.5 bg-white/20 backdrop-blur-sm text-white text-xs font-medium rounded-full border border-white/30 hover:bg-white/30 transition-colors"
                    >
                      {{ tag }}
                    </span>
                    <span 
                      v-if="blog.tags.length > 3"
                      class="px-3 py-1.5 bg-white/10 text-white/60 text-xs font-medium rounded-full"
                    >
                      +{{ blog.tags.length - 3 }}
                    </span>
                  </div>
                  
                  <div class="text-pink-300 hover:text-pink-200 font-bold flex items-center group-hover:translate-x-2 transition-transform duration-300">
                    阅读更多
                    <svg class="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
          </article>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-responsive text-center py-20">
          <svg class="w-16 h-16 text-white/30 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <h3 class="text-2xl font-bold text-white/60 mb-2">暂无博客</h3>
          <p class="text-white/40">博客内容正在准备中，敬请期待</p>
        </div>
      </ResponsiveContainer>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import ResponsiveContainer from '../../shared/components/ResponsiveContainer.vue'
import ResponsiveImage from '../../shared/components/ResponsiveImage.vue'
import { blogAPI } from '../../shared/api'
import type { Blog } from '../../shared/types'

const router = useRouter()

// 响应式数据
const blogs = ref<Blog[]>([])
const loading = ref(true)
const error = ref<string | null>(null)
const sortBy = ref<'created_at' | 'updated_at' | 'title'>('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')

// 计算属性
const publishedBlogs = computed(() => {
  return blogs.value.filter(blog => blog.is_published)
})

const sortedBlogs = computed(() => {
  const sorted = [...publishedBlogs.value].sort((a, b) => {
    let comparison = 0
    
    switch (sortBy.value) {
      case 'created_at':
      case 'updated_at':
        comparison = new Date(a[sortBy.value]).getTime() - new Date(b[sortBy.value]).getTime()
        break
      case 'title':
        comparison = a.title.localeCompare(b.title, 'zh-CN')
        break
    }
    
    return sortOrder.value === 'desc' ? -comparison : comparison
  })
  
  return sorted
})

const hasFilteredResults = computed(() => {
  return sortBy.value !== 'created_at' || sortOrder.value !== 'desc'
})

// 方法
const loadBlogs = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await blogAPI.getAll()
    blogs.value = response.data
  } catch (err) {
    console.error('加载博客失败:', err)
    error.value = '加载博客失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const sortBlogs = () => {
  // 排序逻辑已在计算属性中处理
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
}

const clearFilters = () => {
  sortBy.value = 'created_at'
  sortOrder.value = 'desc'
}

const goToDetail = (id: number) => {
  router.push(`/blog/${id}`)
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const getReadingTime = (content: string) => {
  // 估算阅读时间（假设每分钟200字）
  const wordCount = content.length
  const readingTime = Math.max(1, Math.ceil(wordCount / 200))
  return readingTime
}

const extractSummary = (content: string, maxLength: number = 200) => {
  // 移除Markdown标记和HTML标签
  const plainText = content
    .replace(/[#*`_~\[\]()]/g, '')
    .replace(/<[^>]*>/g, '')
    .trim()
  
  if (plainText.length <= maxLength) {
    return plainText
  }
  
  return plainText.substring(0, maxLength) + '...'
}

// 生命周期
onMounted(() => {
  loadBlogs()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

.space-y-6 > article {
  animation: fadeInUp 0.6s ease-out backwards;
}
</style>