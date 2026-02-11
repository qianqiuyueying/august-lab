<template>
  <div class="space-y-8">
    <!-- 欢迎头部 -->
    <div class="flex flex-col md:flex-row md:items-end justify-between gap-4 animate-fade-in">
      <div>
        <h1 class="text-3xl font-display font-bold text-gray-900 dark:text-white mb-2 tracking-tight">
          欢迎回来，<span class="text-primary-600 dark:text-lab-accent">管理员</span>
        </h1>
        <p class="text-gray-500 dark:text-lab-muted">
          系统概览与性能指标
        </p>
      </div>
      <div class="flex gap-3">
        <button class="px-4 py-2 bg-white dark:bg-lab-surface border border-gray-200 dark:border-lab-border rounded-lg text-sm font-medium hover:border-primary-500 dark:hover:border-lab-accent transition-colors shadow-sm">
          下载报告
        </button>
        <button class="px-4 py-2 bg-primary-600 dark:bg-lab-accent text-white dark:text-black rounded-lg text-sm font-bold hover:bg-primary-700 dark:hover:bg-lab-accent-hover transition-colors shadow-lg shadow-primary-500/20 dark:shadow-lab-accent/20">
          新建项目
        </button>
      </div>
    </div>

    <!-- 核心指标卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div 
        v-for="(stat, index) in stats" 
        :key="stat.title"
        class="group relative p-6 rounded-xl bg-white dark:bg-lab-card border border-gray-100 dark:border-lab-border hover:border-primary-500 dark:hover:border-lab-accent transition-all duration-300 hover:shadow-xl hover:-translate-y-1 overflow-hidden animate-slide-up"
        :style="{ animationDelay: `${index * 100}ms` }"
      >
        <!-- 背景光晕 -->
        <div class="absolute -right-6 -top-6 w-24 h-24 bg-gradient-to-br from-primary-500/10 to-transparent rounded-full blur-2xl group-hover:from-primary-500/20 transition-all"></div>
        
        <div class="relative z-10">
          <div class="flex items-center justify-between mb-4">
            <div class="p-2 rounded-lg bg-gray-50 dark:bg-lab-surface text-gray-400 dark:text-lab-muted group-hover:text-primary-600 dark:group-hover:text-lab-accent transition-colors">
              <el-icon :size="24"><component :is="stat.icon" /></el-icon>
            </div>
            <span class="text-xs font-mono px-2 py-1 rounded bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400">
              +12.5%
            </span>
          </div>
          
          <div class="text-3xl font-bold text-gray-900 dark:text-white mb-1 font-display">
            <el-skeleton v-if="loading" :rows="1" animated class="w-24" />
            <span v-else>{{ stat.value }}</span>
          </div>
          <div class="text-sm text-gray-500 dark:text-lab-muted font-medium">{{ stat.title }}</div>
        </div>
      </div>
    </div>
    
    <!-- 主要内容区 -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- 左侧：最近活动 (占2列) -->
      <div class="lg:col-span-2 space-y-8 animate-slide-up" style="animation-delay: 400ms">
        <!-- 最新作品 -->
        <div class="bg-white dark:bg-lab-card rounded-xl border border-gray-100 dark:border-lab-border overflow-hidden">
          <div class="p-6 border-b border-gray-100 dark:border-lab-border flex items-center justify-between">
            <h3 class="font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <el-icon class="text-primary-500 dark:text-lab-accent"><Briefcase /></el-icon>
              最近作品
            </h3>
            <router-link to="/admin/portfolio" class="text-sm text-primary-600 dark:text-lab-accent hover:underline">查看全部</router-link>
          </div>
          
          <div v-if="portfolioLoading" class="p-6 space-y-4">
            <el-skeleton :rows="3" animated />
          </div>
          
          <div v-else-if="recentPortfolios.length > 0" class="divide-y divide-gray-100 dark:divide-lab-border">
            <div 
              v-for="portfolio in recentPortfolios" 
              :key="portfolio.id" 
              class="p-4 hover:bg-gray-50 dark:hover:bg-lab-surface transition-colors flex items-center gap-4 group"
            >
              <div class="w-12 h-12 rounded-lg bg-gray-100 dark:bg-lab-surface flex items-center justify-center shrink-0 group-hover:scale-105 transition-transform">
                <img v-if="portfolio.cover_image" :src="portfolio.cover_image" class="w-full h-full object-cover rounded-lg" />
                <el-icon v-else class="text-gray-400"><Briefcase /></el-icon>
              </div>
              <div class="flex-1 min-w-0">
                <h4 class="font-medium text-gray-900 dark:text-white truncate group-hover:text-primary-600 dark:group-hover:text-lab-accent transition-colors">
                  {{ portfolio.title }}
                </h4>
                <p class="text-xs text-gray-500 dark:text-lab-muted mt-1 flex items-center gap-2">
                  <span>{{ formatDate(portfolio.created_at) }}</span>
                  <span class="w-1 h-1 rounded-full bg-gray-300 dark:bg-gray-600"></span>
                  <span>{{ portfolio.category || '未分类' }}</span>
                </p>
              </div>
              <div class="flex items-center gap-2">
                <span v-if="portfolio.is_featured" class="px-2 py-0.5 rounded text-xs font-medium bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 border border-yellow-100 dark:border-yellow-900/30">推荐</span>
                <button class="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-white/10 text-gray-400 hover:text-gray-600 dark:hover:text-white transition-colors">
                  <el-icon><EditPen /></el-icon>
                </button>
              </div>
            </div>
          </div>
          
          <div v-else class="p-12 text-center text-gray-500 dark:text-lab-muted">
            <el-icon size="48" class="mb-4 opacity-20"><Briefcase /></el-icon>
            <p>暂无作品</p>
          </div>
        </div>
        
        <!-- 最新博客 -->
        <div class="bg-white dark:bg-lab-card rounded-xl border border-gray-100 dark:border-lab-border overflow-hidden">
          <div class="p-6 border-b border-gray-100 dark:border-lab-border flex items-center justify-between">
            <h3 class="font-bold text-gray-900 dark:text-white flex items-center gap-2">
              <el-icon class="text-green-500 dark:text-green-400"><Document /></el-icon>
              最新文章
            </h3>
            <router-link to="/admin/blog" class="text-sm text-primary-600 dark:text-lab-accent hover:underline">查看全部</router-link>
          </div>
          
          <div v-if="blogLoading" class="p-6 space-y-4">
            <el-skeleton :rows="3" animated />
          </div>
          
          <div v-else-if="recentBlogs.length > 0" class="divide-y divide-gray-100 dark:divide-lab-border">
            <div 
              v-for="blog in recentBlogs" 
              :key="blog.id" 
              class="p-4 hover:bg-gray-50 dark:hover:bg-lab-surface transition-colors flex items-start gap-4 group"
            >
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <span 
                    class="w-2 h-2 rounded-full"
                    :class="blog.is_published ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.4)]' : 'bg-yellow-500'"
                  ></span>
                  <span class="text-xs font-mono text-gray-400 uppercase">{{ blog.is_published ? '已发布' : '草稿' }}</span>
                </div>
                <h4 class="font-medium text-gray-900 dark:text-white truncate group-hover:text-primary-600 dark:group-hover:text-lab-accent transition-colors">
                  {{ blog.title }}
                </h4>
                <p class="text-xs text-gray-500 dark:text-lab-muted mt-1">
                  {{ formatDate(blog.created_at) }} · {{ blog.views || 0 }} 阅读
                </p>
              </div>
              <button class="p-2 rounded-full hover:bg-gray-200 dark:hover:bg-white/10 text-gray-400 hover:text-gray-600 dark:hover:text-white transition-colors opacity-0 group-hover:opacity-100">
                <el-icon><EditPen /></el-icon>
              </button>
            </div>
          </div>
          
          <div v-else class="p-12 text-center text-gray-500 dark:text-lab-muted">
            <el-icon size="48" class="mb-4 opacity-20"><Document /></el-icon>
            <p>暂无文章</p>
          </div>
        </div>
      </div>

      <!-- 右侧：快速操作 (占1列) -->
      <div class="space-y-6 animate-slide-up" style="animation-delay: 600ms">
        <div class="bg-gradient-to-br from-primary-600 to-blue-700 dark:from-lab-card dark:to-lab-surface rounded-xl p-6 text-white shadow-lg relative overflow-hidden border border-transparent dark:border-lab-border">
          <div class="absolute top-0 right-0 w-32 h-32 bg-white/10 rounded-full blur-3xl -mr-10 -mt-10"></div>
          <h3 class="text-lg font-bold mb-4 relative z-10">快速操作</h3>
          <div class="grid grid-cols-2 gap-3 relative z-10">
            <router-link 
              to="/admin/portfolio" 
              class="flex flex-col items-center justify-center p-3 rounded-lg bg-white/10 hover:bg-white/20 transition-colors backdrop-blur-sm border border-white/5"
            >
              <el-icon size="20" class="mb-2"><Plus /></el-icon>
              <span class="text-xs font-medium">添加作品</span>
            </router-link>
            <router-link 
              to="/admin/blog" 
              class="flex flex-col items-center justify-center p-3 rounded-lg bg-white/10 hover:bg-white/20 transition-colors backdrop-blur-sm border border-white/5"
            >
              <el-icon size="20" class="mb-2"><EditPen /></el-icon>
              <span class="text-xs font-medium">写博客</span>
            </router-link>
            <router-link 
              to="/admin/profile" 
              class="flex flex-col items-center justify-center p-3 rounded-lg bg-white/10 hover:bg-white/20 transition-colors backdrop-blur-sm border border-white/5"
            >
              <el-icon size="20" class="mb-2"><User /></el-icon>
              <span class="text-xs font-medium">个人资料</span>
            </router-link>
            <a 
              href="/" 
              target="_blank"
              class="flex flex-col items-center justify-center p-3 rounded-lg bg-white/10 hover:bg-white/20 transition-colors backdrop-blur-sm border border-white/5"
            >
              <el-icon size="20" class="mb-2"><View /></el-icon>
              <span class="text-xs font-medium">预览网站</span>
            </a>
          </div>
        </div>

        <!-- 系统状态 -->
        <div class="bg-white dark:bg-lab-card rounded-xl border border-gray-100 dark:border-lab-border p-6">
          <h3 class="font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
            <el-icon class="text-orange-500"><Warning /></el-icon>
            系统状态
          </h3>
          <div class="space-y-4">
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-gray-500 dark:text-lab-muted">存储使用</span>
                <span class="text-gray-900 dark:text-white font-mono">45%</span>
              </div>
              <div class="h-1.5 bg-gray-100 dark:bg-lab-surface rounded-full overflow-hidden">
                <div class="h-full bg-primary-500 dark:bg-lab-accent w-[45%] rounded-full"></div>
              </div>
            </div>
            <div>
              <div class="flex justify-between text-xs mb-1">
                <span class="text-gray-500 dark:text-lab-muted">API 请求</span>
                <span class="text-gray-900 dark:text-white font-mono">8.2k/10k</span>
              </div>
              <div class="h-1.5 bg-gray-100 dark:bg-lab-surface rounded-full overflow-hidden">
                <div class="h-full bg-green-500 w-[82%] rounded-full"></div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, onUnmounted } from 'vue'
import { 
  Briefcase, 
  Document, 
  User, 
  View, 
  Plus, 
  EditPen,
  TrendCharts,
  ChatDotRound,
  Warning
} from '@element-plus/icons-vue'
import { useDataSync } from '../../shared/composables/useDataStore'
import { useDarkMode } from '../composables/useDarkMode'

const { isDark } = useDarkMode()
const { portfolioStore, blogStore, startAutoSync, stopAutoSync } = useDataSync()

// Loading states
const loading = computed(() => portfolioStore.loading.value || blogStore.loading.value)
const portfolioLoading = computed(() => portfolioStore.loading.value)
const blogLoading = computed(() => blogStore.loading.value)

// Recent Data
const recentPortfolios = computed(() => 
  portfolioStore.portfolios.value
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
)

const recentBlogs = computed(() => 
  blogStore.blogs.value
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 5)
)

// Stats
const stats = computed(() => [
  { 
    title: '作品总数', 
    value: portfolioStore.portfolios.value.length.toString(),
    icon: Briefcase,
  },
  { 
    title: '博客文章', 
    value: blogStore.blogs.value.length.toString(),
    icon: Document,
  },
  { 
    title: '已发布', 
    value: blogStore.publishedBlogs.value.length.toString(),
    icon: ChatDotRound,
  },
  { 
    title: '推荐作品', 
    value: portfolioStore.featuredPortfolios.value.length.toString(),
    icon: TrendCharts,
  }
])

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    month: 'short',
    day: 'numeric',
    year: 'numeric'
  })
}

const loadDashboardData = async () => {
  startAutoSync()
  await Promise.all([
    portfolioStore.fetchPortfolios(),
    blogStore.fetchBlogs(false, true)
  ])
}

onMounted(() => {
  loadDashboardData()
})

onUnmounted(() => {
  stopAutoSync()
})
</script>