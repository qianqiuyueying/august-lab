<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0b0c10] text-slate-900 dark:text-lab-text transition-colors">
    <!-- 加载状态 -->
    <div v-if="loading" class="min-h-screen flex items-center justify-center">
      <div class="loading-responsive">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-lab-accent"></div>
        <p class="text-slate-500 dark:text-slate-400 mt-4">加载作品详情中...</p>
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
          <button @click="loadPortfolio" class="btn-primary">
            重试
          </button>
          <router-link to="/portfolio" class="btn-outline">
            返回列表
          </router-link>
        </div>
      </div>
    </div>

    <!-- 作品详情内容 -->
    <div v-else-if="portfolio" class="section-padding">
      <ResponsiveContainer size="xl">
        <!-- 返回按钮 -->
        <div class="mb-8">
          <router-link 
            to="/portfolio" 
            class="inline-flex items-center text-primary-600 dark:text-lab-accent hover:text-primary-700 dark:hover:text-lab-accent/80 transition-colors duration-200"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 19l-7-7 7-7"></path>
            </svg>
            返回作品列表
          </router-link>
        </div>

        <!-- 项目主要信息 -->
        <div class="bg-white dark:bg-[#1f2833] rounded-xl shadow-sm overflow-hidden mb-8 border border-slate-200 dark:border-slate-800">
          <!-- 项目图片 -->
          <div class="relative">
            <ResponsiveImage
              v-if="portfolio.image_url"
              :src="portfolio.image_url"
              :alt="portfolio.title"
              aspect-ratio="video"
              class="w-full"
              loading="eager"
            />
            <div v-else class="w-full h-64 md:h-96 bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-700 dark:to-slate-800 flex items-center justify-center">
              <svg class="w-16 h-16 text-slate-400 dark:text-slate-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
            </div>
            
            <!-- 精选标识 -->
            <div v-if="portfolio.is_featured" class="absolute top-4 right-4">
              <div class="bg-primary-600 dark:bg-lab-accent dark:text-black text-white px-3 py-1 rounded-full text-sm font-medium shadow-lg">
                <svg class="w-4 h-4 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z" />
                </svg>
                精选作品
              </div>
            </div>
          </div>

          <!-- 项目信息 -->
          <div class="p-6 md:p-8">
            <div class="flex flex-col lg:flex-row lg:items-start lg:justify-between gap-6">
              <!-- 左侧：标题和描述 -->
              <div class="flex-1">
                <h1 class="text-3xl md:text-4xl font-bold text-slate-900 dark:text-white mb-4">{{ portfolio.title }}</h1>
                
                <p v-if="portfolio.description" class="text-responsive-lg text-slate-600 dark:text-slate-300 leading-relaxed mb-6">
                  {{ portfolio.description }}
                </p>
                
                <!-- 技术栈 -->
                <div class="mb-6">
                  <h3 class="heading-5 mb-3 text-slate-900 dark:text-white">技术栈</h3>
                  <div class="flex flex-wrap gap-2">
                    <span 
                      v-for="tech in portfolio.tech_stack" 
                      :key="tech"
                      class="tag tag-primary dark:bg-lab-accent/20 dark:text-lab-accent dark:border-lab-accent/50"
                    >
                      {{ tech }}
                    </span>
                  </div>
                </div>
              </div>

              <!-- 右侧：操作按钮 -->
              <div class="flex flex-col sm:flex-row lg:flex-col gap-3 lg:min-w-[200px]">
                <a 
                  v-if="portfolio.project_url"
                  :href="portfolio.project_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn-primary btn-responsive flex items-center justify-center"
                >
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  在线预览
                </a>
                
                <a 
                  v-if="portfolio.github_url"
                  :href="portfolio.github_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="btn-outline btn-responsive flex items-center justify-center"
                >
                  <svg class="w-5 h-5 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                  查看源码
                </a>
                
                <button 
                  @click="shareProject"
                  class="btn-outline btn-responsive flex items-center justify-center"
                >
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.367 2.684 3 3 0 00-5.367-2.684z" />
                  </svg>
                  分享项目
                </button>
              </div>
            </div>
          </div>
        </div>

        <!-- 项目详细信息 -->
        <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <!-- 主要内容区域 -->
          <div class="lg:col-span-2 space-y-8">
            <!-- 项目详情 -->
            <div class="bg-white dark:bg-[#1f2833] rounded-xl shadow-sm p-6 md:p-8 border border-slate-200 dark:border-slate-800">
              <h2 class="heading-3 mb-6 text-slate-900 dark:text-white">项目详情</h2>
              <div class="prose prose-content max-w-none">
                <p class="text-slate-600 dark:text-slate-300 leading-relaxed">
                  {{ portfolio.description || '这是一个精心设计和开发的项目，展示了现代Web开发的最佳实践和创新技术的应用。' }}
                </p>
                
                <h3 class="heading-5 mt-8 mb-4 text-slate-900 dark:text-white">主要功能特性</h3>
                <ul class="list-disc list-inside text-slate-600 dark:text-slate-300 space-y-2">
                  <li>响应式设计，完美适配各种设备</li>
                  <li>现代化的用户界面和交互体验</li>
                  <li>高性能的前端架构和优化</li>
                  <li>完善的错误处理和用户反馈</li>
                  <li>可扩展的代码结构和组件设计</li>
                </ul>
                
                <h3 class="heading-5 mt-8 mb-4 text-slate-900 dark:text-white">技术亮点</h3>
                <p class="text-slate-600 dark:text-slate-300">
                  项目采用了{{ portfolio.tech_stack.join('、') }}等现代技术栈，
                  实现了高效的开发流程和优秀的用户体验。通过合理的架构设计和性能优化，
                  确保了应用的稳定性和可维护性。
                </p>
              </div>
            </div>

            <!-- 开发历程 -->
            <div class="bg-white dark:bg-[#1f2833] rounded-xl shadow-sm p-6 md:p-8 border border-slate-200 dark:border-slate-800">
              <h2 class="heading-3 mb-6 text-slate-900 dark:text-white">开发历程</h2>
              <div class="space-y-6">
                <div class="flex items-start gap-4">
                  <div class="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-lab-accent/20 rounded-full flex items-center justify-center">
                    <div class="w-3 h-3 bg-primary-600 dark:bg-lab-accent rounded-full"></div>
                  </div>
                  <div>
                    <h4 class="font-semibold text-slate-900 dark:text-white mb-2">需求分析与设计</h4>
                    <p class="text-slate-600 dark:text-slate-300 text-sm">深入分析用户需求，制定技术方案和设计规范</p>
                  </div>
                </div>
                
                <div class="flex items-start gap-4">
                  <div class="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-lab-accent/20 rounded-full flex items-center justify-center">
                    <div class="w-3 h-3 bg-primary-600 dark:bg-lab-accent rounded-full"></div>
                  </div>
                  <div>
                    <h4 class="font-semibold text-slate-900 dark:text-white mb-2">技术选型与架构</h4>
                    <p class="text-slate-600 dark:text-slate-300 text-sm">选择合适的技术栈，设计可扩展的系统架构</p>
                  </div>
                </div>
                
                <div class="flex items-start gap-4">
                  <div class="flex-shrink-0 w-8 h-8 bg-primary-100 dark:bg-lab-accent/20 rounded-full flex items-center justify-center">
                    <div class="w-3 h-3 bg-primary-600 dark:bg-lab-accent rounded-full"></div>
                  </div>
                  <div>
                    <h4 class="font-semibold text-slate-900 dark:text-white mb-2">开发与测试</h4>
                    <p class="text-slate-600 dark:text-slate-300 text-sm">迭代开发，持续集成，确保代码质量和功能完整性</p>
                  </div>
                </div>
                
                <div class="flex items-start gap-4">
                  <div class="flex-shrink-0 w-8 h-8 bg-green-100 dark:bg-green-900/40 rounded-full flex items-center justify-center">
                    <svg class="w-4 h-4 text-green-600 dark:text-green-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
                    </svg>
                  </div>
                  <div>
                    <h4 class="font-semibold text-slate-900 dark:text-white mb-2">部署与优化</h4>
                    <p class="text-slate-600 dark:text-slate-300 text-sm">项目上线部署，性能监控和持续优化</p>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 侧边栏信息 -->
          <div class="space-y-6">
            <!-- 项目信息 -->
            <div class="bg-white dark:bg-[#1f2833] rounded-xl shadow-sm p-6 border border-slate-200 dark:border-slate-800">
              <h3 class="heading-5 mb-4 text-slate-900 dark:text-white">项目信息</h3>
              <div class="space-y-3 text-sm">
                <div class="flex justify-between">
                  <span class="text-slate-500 dark:text-slate-400">创建时间</span>
                  <span class="text-slate-900 dark:text-slate-200">{{ formatDate(portfolio.created_at) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-500 dark:text-slate-400">更新时间</span>
                  <span class="text-slate-900 dark:text-slate-200">{{ formatDate(portfolio.updated_at) }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-500 dark:text-slate-400">项目状态</span>
                  <span class="text-green-600 dark:text-green-400 font-medium">已完成</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-slate-500 dark:text-slate-400">技术数量</span>
                  <span class="text-slate-900 dark:text-slate-200">{{ portfolio.tech_stack.length }} 项</span>
                </div>
              </div>
            </div>

            <!-- 相关链接 -->
            <div v-if="portfolio.project_url || portfolio.github_url" class="bg-white dark:bg-[#1f2833] rounded-xl shadow-sm p-6 border border-slate-200 dark:border-slate-800">
              <h3 class="heading-5 mb-4 text-slate-900 dark:text-white">相关链接</h3>
              <div class="space-y-3">
                <a 
                  v-if="portfolio.project_url"
                  :href="portfolio.project_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center text-primary-600 dark:text-lab-accent hover:text-primary-700 dark:hover:text-lab-accent/80 text-sm"
                >
                  <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                  </svg>
                  在线预览
                </a>
                <a 
                  v-if="portfolio.github_url"
                  :href="portfolio.github_url"
                  target="_blank"
                  rel="noopener noreferrer"
                  class="flex items-center text-slate-600 dark:text-slate-300 hover:text-slate-800 dark:hover:text-white text-sm"
                >
                  <svg class="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                  源码仓库
                </a>
              </div>
            </div>

            <!-- 分享 -->
            <div class="bg-white dark:bg-[#1f2833] rounded-xl shadow-sm p-6 border border-slate-200 dark:border-slate-800">
              <h3 class="heading-5 mb-4 text-slate-900 dark:text-white">分享项目</h3>
              <div class="flex gap-2">
                <button 
                  @click="copyLink"
                  class="flex-1 btn-outline btn-sm flex items-center justify-center"
                  :class="{ 'btn-primary': linkCopied }"
                >
                  <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                  </svg>
                  {{ linkCopied ? '已复制' : '复制链接' }}
                </button>
              </div>
            </div>
          </div>
        </div>
      </ResponsiveContainer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import ResponsiveContainer from '../../shared/components/ResponsiveContainer.vue'
import ResponsiveImage from '../../shared/components/ResponsiveImage.vue'
import { portfolioAPI } from '../../shared/api'
import type { Portfolio } from '../../shared/types'

const route = useRoute()
const router = useRouter()

// 响应式数据
const portfolio = ref<Portfolio | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const linkCopied = ref(false)

// 方法
const loadPortfolio = async () => {
  try {
    loading.value = true
    error.value = null
    
    const id = Number(route.params.id)
    if (isNaN(id)) {
      throw new Error('无效的作品ID')
    }
    
    const response = await portfolioAPI.getById(id)
    portfolio.value = response.data
  } catch (err: any) {
    console.error('加载作品详情失败:', err)
    if (err.response?.status === 404) {
      error.value = '作品不存在'
    } else {
      error.value = '加载作品详情失败，请稍后重试'
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

const shareProject = async () => {
  if (navigator.share && portfolio.value) {
    try {
      await navigator.share({
        title: portfolio.value.title,
        text: portfolio.value.description || '查看这个精彩的项目',
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
  loadPortfolio()
})
</script>

<style scoped>
.prose {
  color: inherit;
}

.prose h3 {
  margin-top: 2rem;
  margin-bottom: 1rem;
}

.prose p {
  margin-bottom: 1rem;
}

.prose ul {
  margin-bottom: 1rem;
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