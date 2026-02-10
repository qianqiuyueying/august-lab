<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0b0c10] text-slate-900 dark:text-lab-text transition-colors">
    <!-- 加载状态 -->
    <div v-if="loading" class="min-h-screen flex items-center justify-center">
      <div class="loading-responsive">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-lab-accent"></div>
        <p class="text-slate-500 dark:text-slate-400 mt-4">加载文章中...</p>
      </div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="min-h-screen flex items-center justify-center">
      <div class="error-responsive">
        <svg class="w-16 h-16 text-red-300 dark:text-red-500/60 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
        </svg>
        <h3 class="heading-5 text-red-600 dark:text-red-400 mb-2">加载失败</h3>
        <p class="text-red-500 dark:text-red-400 mb-4">{{ error }}</p>
        <div class="flex gap-4 justify-center">
          <button @click="loadBlog" class="btn-primary">
            重试
          </button>
          <router-link to="/blog" class="btn-outline">
            返回列表
          </router-link>
        </div>
      </div>
    </div>

    <!-- 博客详情内容 -->
    <div v-else-if="blog" class="section-padding">
      <ResponsiveContainer size="lg">
        <!-- 返回按钮 -->
        <div class="mb-8">
          <router-link 
            to="/blog" 
            class="inline-flex items-center text-primary-600 dark:text-lab-accent hover:text-primary-700 dark:hover:text-lab-accent/80 transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            返回博客列表
          </router-link>
        </div>

        <!-- 文章内容 -->
        <article class="bg-white dark:bg-[#1f2833] rounded-xl shadow-sm overflow-hidden border border-slate-200 dark:border-slate-800">
          <!-- 封面图片 -->
          <div v-if="blog.cover_image" class="relative">
            <ResponsiveImage
              :src="blog.cover_image"
              :alt="blog.title"
              aspect-ratio="video"
              class="w-full"
              loading="eager"
            />
          </div>

          <!-- 文章内容 -->
          <div class="p-6 md:p-8 lg:p-12">
            <!-- 文章头部 -->
            <header class="mb-8">
              <!-- 文章元信息 -->
              <div class="flex flex-wrap items-center text-sm text-slate-500 dark:text-slate-400 mb-6">
                <div class="flex items-center mr-6">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                  </svg>
                  <time>{{ formatDate(blog.created_at) }}</time>
                </div>
                <div class="flex items-center mr-6">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>{{ getReadingTime(blog.content) }} 分钟阅读</span>
                </div>
                <div v-if="blog.updated_at !== blog.created_at" class="flex items-center">
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>更新于 {{ formatDate(blog.updated_at) }}</span>
                </div>
              </div>
              
              <!-- 文章标题 -->
              <h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-6">{{ blog.title }}</h1>
              
              <!-- 文章摘要 -->
              <div v-if="blog.summary" class="text-responsive-lg text-slate-600 dark:text-slate-300 leading-relaxed mb-6 p-4 bg-slate-50 dark:bg-slate-800/50 rounded-lg border-l-4 border-primary-500 dark:border-lab-accent">
                {{ blog.summary }}
              </div>
              
              <!-- 标签 -->
              <div v-if="blog.tags.length > 0" class="flex flex-wrap gap-2 mb-8">
                <span 
                  v-for="tag in blog.tags" 
                  :key="tag"
                  class="tag tag-secondary dark:bg-slate-700 dark:text-slate-200 dark:border-slate-600"
                >
                  {{ tag }}
                </span>
              </div>
            </header>
            
            <!-- 文章正文（Markdown 渲染，深色模式由内联 class 与下方 prose 样式共同支持） -->
            <div class="prose prose-lg prose-content max-w-none" v-html="renderedContent"></div>
            
            <!-- 文章底部 -->
            <footer class="mt-12 pt-8 border-t border-slate-200 dark:border-slate-700">
              <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
                <div class="text-sm text-slate-500 dark:text-slate-400">
                  <div>发布时间：{{ formatDate(blog.created_at) }}</div>
                  <div v-if="blog.updated_at !== blog.created_at">
                    最后更新：{{ formatDate(blog.updated_at) }}
                  </div>
                </div>
                
                <div class="flex items-center gap-4">
                  <button 
                    @click="shareArticle"
                    class="flex items-center text-slate-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-lab-accent transition-colors duration-200"
                  >
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                    </svg>
                    分享文章
                  </button>
                  
                  <button 
                    @click="copyLink"
                    class="flex items-center text-slate-600 dark:text-slate-400 hover:text-primary-600 dark:hover:text-lab-accent transition-colors duration-200"
                    :class="{ 'text-primary-600 dark:text-lab-accent': linkCopied }"
                  >
                    <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                    </svg>
                    {{ linkCopied ? '已复制' : '复制链接' }}
                  </button>
                </div>
              </div>
            </footer>
          </div>
        </article>
      </ResponsiveContainer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ResponsiveContainer from '../../shared/components/ResponsiveContainer.vue'
import ResponsiveImage from '../../shared/components/ResponsiveImage.vue'
import { blogAPI } from '../../shared/api'
import type { Blog } from '../../shared/types'

const route = useRoute()
const router = useRouter()

// 响应式数据
const blog = ref<Blog | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const linkCopied = ref(false)

// 计算属性：Markdown 渲染，输出带深色模式适配的 class
const renderedContent = computed(() => {
  if (!blog.value?.content) return ''
  
  let html = blog.value.content
  const h1Cls = 'text-3xl font-bold text-slate-900 dark:text-white mt-12 mb-8'
  const h2Cls = 'text-2xl font-bold text-slate-900 dark:text-white mt-10 mb-6'
  const h3Cls = 'text-xl font-semibold text-slate-900 dark:text-white mt-8 mb-4'
  const pCls = 'text-slate-600 dark:text-slate-300 leading-relaxed mb-4'
  const preCls = 'bg-slate-900 dark:bg-slate-800 text-slate-100 dark:text-slate-200 p-4 rounded-lg overflow-x-auto my-6'
  const codeCls = 'bg-slate-100 dark:bg-slate-700 text-slate-800 dark:text-slate-200 px-2 py-1 rounded text-sm'
  const blockquoteCls = 'border-l-4 border-primary-500 dark:border-lab-accent pl-4 py-2 my-6 bg-slate-50 dark:bg-slate-800/60 text-slate-700 dark:text-slate-300 italic'
  const linkCls = 'text-primary-600 dark:text-lab-accent hover:text-primary-700 dark:hover:text-lab-accent/80 underline'

  // 标题
  html = html.replace(/^### (.*$)/gim, `<h3 class="${h3Cls}">$1</h3>`)
  html = html.replace(/^## (.*$)/gim, `<h2 class="${h2Cls}">$1</h2>`)
  html = html.replace(/^# (.*$)/gim, `<h1 class="${h1Cls}">$1</h1>`)
  
  // 粗体和斜体
  html = html.replace(/\*\*(.*?)\*\*/g, '<strong class="font-semibold">$1</strong>')
  html = html.replace(/\*(.*?)\*/g, '<em class="italic">$1</em>')
  
  // 代码块（先处理块，避免被行内 code 误伤）
  html = html.replace(/```([\s\S]*?)```/g, `<pre class="${preCls}"><code>$1</code></pre>`)
  html = html.replace(/`(.*?)`/g, `<code class="${codeCls}">$1</code>`)
  
  // 引用
  html = html.replace(/^> (.*$)/gim, `<blockquote class="${blockquoteCls}">$1</blockquote>`)
  
  // 链接
  html = html.replace(/\[([^\]]+)\]\(([^)]+)\)/g, `<a href="$2" class="${linkCls}" target="_blank" rel="noopener noreferrer">$1</a>`)
  
  // 段落
  html = html.replace(/\n\n/g, `</p><p class="${pCls}">`)
  html = `<p class="${pCls}">` + html + '</p>'
  
  // 换行
  html = html.replace(/\n/g, '<br>')
  
  return html
})

// 方法
const loadBlog = async () => {
  try {
    loading.value = true
    error.value = null
    
    const id = Number(route.params.id)
    if (isNaN(id)) {
      throw new Error('无效的文章ID')
    }
    
    const response = await blogAPI.getById(id)
    blog.value = response.data
    
    // 检查文章是否已发布
    if (!blog.value.is_published) {
      error.value = '文章未发布或不存在'
      return
    }
  } catch (err: any) {
    console.error('加载文章失败:', err)
    if (err.response?.status === 404) {
      error.value = '文章不存在'
    } else {
      error.value = '加载文章失败，请稍后重试'
    }
  } finally {
    loading.value = false
  }
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

const shareArticle = async () => {
  if (navigator.share && blog.value) {
    try {
      await navigator.share({
        title: blog.value.title,
        text: blog.value.summary || '查看这篇精彩的文章',
        url: window.location.href
      })
    } catch (err) {
      console.log('分享取消或失败')
    }
  } else {
    copyLink()
  }
}

const copyLink = async () => {
  try {
    await navigator.clipboard.writeText(window.location.href)
    linkCopied.value = true
    setTimeout(() => {
      linkCopied.value = false
    }, 2000)
  } catch (err) {
    console.error('复制链接失败:', err)
  }
}

// 生命周期
onMounted(() => {
  loadBlog()
})
</script>

<style scoped>
/* Prose 基础：继承颜色，深色由内联 class 与 Tailwind dark: 处理 */
.prose.prose-content {
  color: inherit;
}

.prose.prose-content p {
  margin-bottom: 1rem;
}

.prose.prose-content blockquote,
.prose.prose-content pre {
  margin: 1.5rem 0;
}

.prose.prose-content code {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
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