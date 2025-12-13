<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 页面头部 -->
    <section class="section-padding-sm bg-white border-b border-gray-200">
      <ResponsiveContainer size="xl">
        <div class="text-center">
          <h1 class="heading-1 mb-4">博客文章</h1>
          <p class="text-responsive-lg text-gray-600 max-w-3xl mx-auto">
            分享技术心得、开发经验和生活感悟，记录成长路上的点点滴滴
          </p>
        </div>
      </ResponsiveContainer>
    </section>

    <!-- 博客展示区域 -->
    <section class="section-padding">
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
        <div v-if="loading" class="loading-responsive">
          <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
          <p class="text-gray-500 mt-4">加载博客中...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-responsive">
          <svg class="w-16 h-16 text-red-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <h3 class="heading-5 text-red-600 mb-2">加载失败</h3>
          <p class="text-red-500 mb-4">{{ error }}</p>
          <button @click="loadBlogs" class="btn-primary">
            重试
          </button>
        </div>

        <!-- 博客列表 -->
        <div v-else-if="sortedBlogs.length > 0" class="space-y-8">
          <article 
            v-for="blog in sortedBlogs" 
            :key="blog.id"
            class="bg-white rounded-xl shadow-sm hover:shadow-md transition-all duration-300 overflow-hidden group cursor-pointer"
            @click="goToDetail(blog.id)"
          >
            <!-- 封面图片 -->
            <div v-if="blog.cover_image" class="relative overflow-hidden">
              <ResponsiveImage
                :src="blog.cover_image"
                :alt="blog.title"
                aspect-ratio="video"
                class="group-hover:scale-105 transition-transform duration-300"
                loading="lazy"
              />
            </div>
            
            <!-- 文章内容 -->
            <div class="p-6 md:p-8">
              <!-- 文章元信息 -->
              <div class="flex items-center text-sm text-gray-500 mb-4">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                <time>{{ formatDate(blog.created_at) }}</time>
                <span class="mx-2">•</span>
                <span class="text-primary-600">{{ getReadingTime(blog.content) }} 分钟阅读</span>
              </div>
              
              <!-- 文章标题 -->
              <h2 class="heading-3 mb-4 group-hover:text-primary-600 transition-colors duration-200 line-clamp-2">
                {{ blog.title }}
              </h2>
              
              <!-- 文章摘要 -->
              <p class="text-gray-600 leading-relaxed mb-6 line-clamp-3">
                {{ blog.summary || extractSummary(blog.content) }}
              </p>
              
              <!-- 标签和阅读更多 -->
              <div class="flex items-center justify-between">
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="tag in blog.tags.slice(0, 3)" 
                    :key="tag"
                    class="tag tag-secondary text-xs"
                  >
                    {{ tag }}
                  </span>
                  <span 
                    v-if="blog.tags.length > 3"
                    class="tag tag-secondary text-xs"
                  >
                    +{{ blog.tags.length - 3 }}
                  </span>
                </div>
                
                <div class="text-primary-600 hover:text-primary-700 font-medium flex items-center group-hover:translate-x-1 transition-transform duration-200">
                  阅读更多
                  <svg class="w-4 h-4 ml-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
              </div>
            </div>
          </article>
        </div>

        <!-- 空状态 -->
        <div v-else class="empty-responsive">
          <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <h3 class="heading-5 text-gray-500 mb-2">暂无博客</h3>
          <p class="text-gray-400">博客内容正在准备中，敬请期待</p>
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

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>