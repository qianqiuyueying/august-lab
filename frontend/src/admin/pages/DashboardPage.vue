<template>
  <div>
    <!-- 欢迎信息：模块化留白 -->
    <div class="admin-page-header admin-section">
      <h1 :class="['admin-page-title mb-1', isDark ? 'text-gray-100' : 'text-gray-900']">
        欢迎回来
      </h1>
      <p :class="['admin-page-desc', isDark ? 'text-gray-400' : 'text-gray-600']">
        这里是您的管理后台概览
      </p>
    </div>

    <!-- 统计卡片 -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 admin-section">
      <el-card
        v-for="stat in stats"
        :key="stat.title"
        class="text-center cursor-pointer"
        :class="stat.color"
      >
        <div class="flex items-center justify-center mb-3">
          <el-icon :size="24" :class="stat.iconColor">
            <component :is="stat.icon" />
          </el-icon>
        </div>
        <div :class="['text-2xl font-bold mb-2', isDark ? 'text-gray-100' : 'text-gray-900']">
          <el-skeleton v-if="loading" :rows="1" animated />
          <span v-else>{{ stat.value }}</span>
        </div>
        <div :class="isDark ? 'text-gray-400' : 'text-gray-600'">{{ stat.title }}</div>
        <div v-if="stat.change" class="text-xs mt-2" :class="stat.changeColor">
          {{ stat.change }}
        </div>
      </el-card>
    </div>
    
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 admin-section">
      <!-- 最新作品 -->
      <el-card>
        <template #header>
          <div class="flex items-center justify-between">
            <span :class="['font-semibold', isDark ? 'text-gray-100' : 'text-gray-900']">最新作品</span>
            <router-link 
              to="/admin/portfolio" 
              :class="['text-sm', isDark ? 'text-blue-400 hover:text-blue-300' : 'text-primary-600 hover:text-primary-700']"
            >
              查看全部 →
            </router-link>
          </div>
        </template>
        
        <div v-if="portfolioLoading" class="space-y-4">
          <el-skeleton v-for="i in 3" :key="i" :rows="2" animated />
        </div>
        
        <div v-else-if="recentPortfolios.length > 0" class="space-y-4">
          <div 
            v-for="portfolio in recentPortfolios" 
            :key="portfolio.id" 
            :class="['flex items-center space-x-3 p-3 rounded-lg transition-colors', isDark ? 'hover:bg-slate-700/50' : 'hover:bg-gray-50']"
          >
            <div class="w-12 h-12 bg-gradient-to-br from-primary-400 to-blue-500 rounded-lg flex items-center justify-center">
              <el-icon class="text-white"><Briefcase /></el-icon>
            </div>
            <div class="flex-1 min-w-0">
              <div :class="['font-medium truncate', isDark ? 'text-gray-100' : 'text-gray-900']">{{ portfolio.title }}</div>
              <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-500']">{{ formatDate(portfolio.created_at) }}</div>
            </div>
            <el-tag v-if="portfolio.is_featured" type="success" size="small">推荐</el-tag>
          </div>
        </div>
        
        <div :class="['text-center py-8', isDark ? 'text-gray-400' : 'text-gray-500']">
          <el-icon size="48" class="mb-4"><Briefcase /></el-icon>
          <p>暂无作品</p>
          <router-link to="/admin/portfolio" :class="isDark ? 'text-blue-400 hover:text-blue-300' : 'text-primary-600 hover:text-primary-700'">
            创建第一个作品
          </router-link>
        </div>
      </el-card>
      
      <!-- 最新博客 -->
      <el-card>
        <template #header>
          <div class="flex items-center justify-between">
            <span :class="['font-semibold', isDark ? 'text-gray-100' : 'text-gray-900']">最新博客</span>
            <router-link 
              to="/admin/blog" 
              :class="['text-sm', isDark ? 'text-blue-400 hover:text-blue-300' : 'text-primary-600 hover:text-primary-700']"
            >
              查看全部 →
            </router-link>
          </div>
        </template>
        
        <div v-if="blogLoading" class="space-y-4">
          <el-skeleton v-for="i in 3" :key="i" :rows="2" animated />
        </div>
        
        <div v-else-if="recentBlogs.length > 0" class="space-y-4">
          <div 
            v-for="blog in recentBlogs" 
            :key="blog.id" 
            :class="['pb-3 last:border-b-0 p-3 rounded-lg transition-colors', isDark ? 'border-b border-slate-700/50 hover:bg-slate-700/50' : 'border-b border-gray-100 hover:bg-gray-50']"
          >
            <div class="flex items-start justify-between">
              <div class="flex-1 min-w-0">
                <div :class="['font-medium mb-1 truncate', isDark ? 'text-gray-100' : 'text-gray-900']">{{ blog.title }}</div>
                <div :class="['text-sm', isDark ? 'text-gray-400' : 'text-gray-500']">{{ formatDate(blog.created_at) }}</div>
              </div>
              <el-tag 
                :type="blog.is_published ? 'success' : 'warning'" 
                size="small"
              >
                {{ blog.is_published ? '已发布' : '草稿' }}
              </el-tag>
            </div>
          </div>
        </div>
        
        <div :class="['text-center py-8', isDark ? 'text-gray-400' : 'text-gray-500']">
          <el-icon size="48" class="mb-4"><Document /></el-icon>
          <p>暂无博客</p>
          <router-link to="/admin/blog" :class="isDark ? 'text-blue-400 hover:text-blue-300' : 'text-primary-600 hover:text-primary-700'">
            写第一篇博客
          </router-link>
        </div>
      </el-card>
    </div>

    <!-- 快速操作 -->
    <el-card class="admin-section">
      <template #header>
        <span :class="['font-semibold', isDark ? 'text-gray-100' : 'text-gray-900']">快速操作</span>
      </template>
      
      <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
        <router-link 
          to="/admin/portfolio" 
          :class="['flex flex-col items-center p-4 rounded-lg border hover:shadow-sm transition-all', isDark ? 'border-slate-700/50 hover:border-primary-500' : 'border-gray-200 hover:border-primary-300']"
        >
          <el-icon size="24" :class="['mb-2', isDark ? 'text-blue-400' : 'text-primary-600']"><Plus /></el-icon>
          <span :class="['text-sm', isDark ? 'text-gray-200' : 'text-gray-700']">新建作品</span>
        </router-link>
        
        <router-link 
          to="/admin/blog" 
          :class="['flex flex-col items-center p-4 rounded-lg border hover:shadow-sm transition-all', isDark ? 'border-slate-700/50 hover:border-primary-500' : 'border-gray-200 hover:border-primary-300']"
        >
          <el-icon size="24" :class="['mb-2', isDark ? 'text-blue-400' : 'text-primary-600']"><EditPen /></el-icon>
          <span :class="['text-sm', isDark ? 'text-gray-200' : 'text-gray-700']">写博客</span>
        </router-link>
        
        <router-link 
          to="/admin/profile" 
          :class="['flex flex-col items-center p-4 rounded-lg border hover:shadow-sm transition-all', isDark ? 'border-slate-700/50 hover:border-primary-500' : 'border-gray-200 hover:border-primary-300']"
        >
          <el-icon size="24" :class="['mb-2', isDark ? 'text-blue-400' : 'text-primary-600']"><User /></el-icon>
          <span :class="['text-sm', isDark ? 'text-gray-200' : 'text-gray-700']">编辑资料</span>
        </router-link>
        
        <a 
          href="/" 
          target="_blank"
          :class="['flex flex-col items-center p-4 rounded-lg border hover:shadow-sm transition-all', isDark ? 'border-slate-700/50 hover:border-primary-500' : 'border-gray-200 hover:border-primary-300']"
        >
          <el-icon size="24" :class="['mb-2', isDark ? 'text-blue-400' : 'text-primary-600']"><View /></el-icon>
          <span :class="['text-sm', isDark ? 'text-gray-200' : 'text-gray-700']">预览网站</span>
        </a>
      </div>
    </el-card>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, defineAsyncComponent } from 'vue'
import { 
  Briefcase, 
  Document, 
  User, 
  View, 
  Plus, 
  EditPen,
  TrendCharts,
  ChatDotRound
} from '@element-plus/icons-vue'
import { useDataSync } from '../../shared/composables/useDataStore'
import { useDarkMode } from '../composables/useDarkMode'
import type { Portfolio, Blog } from '../../shared/types'

const { isDark } = useDarkMode()

// 数据存储
const { portfolioStore, blogStore, startAutoSync, stopAutoSync } = useDataSync()

// 环境检测
const isDevelopment = computed(() => {
  // @ts-ignore
  return import.meta.env && import.meta.env.MODE === 'development'
})

// 加载状态
const loading = computed(() => portfolioStore.loading.value || blogStore.loading.value)
const portfolioLoading = computed(() => portfolioStore.loading.value)
const blogLoading = computed(() => blogStore.loading.value)

// 最新数据
const recentPortfolios = computed(() => 
  portfolioStore.portfolios.value
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3)
)

const recentBlogs = computed(() => 
  blogStore.blogs.value
    .sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
    .slice(0, 3)
)

// 统计数据
const stats = computed(() => {
  const dark = isDark.value
  return [
    { 
      title: '总作品数', 
      value: portfolioStore.portfolios.value.length.toString(),
      icon: Briefcase,
      color: dark ? 'bg-slate-800/50' : 'bg-blue-50',
      iconColor: dark ? 'text-blue-400' : 'text-blue-600',
      change: '',
      changeColor: ''
    },
    { 
      title: '博客文章', 
      value: blogStore.blogs.value.length.toString(),
      icon: Document,
      color: dark ? 'bg-slate-800/50' : 'bg-green-50',
      iconColor: dark ? 'text-green-400' : 'text-green-600',
      change: '',
      changeColor: ''
    },
    { 
      title: '已发布博客', 
      value: blogStore.publishedBlogs.value.length.toString(),
      icon: ChatDotRound,
      color: dark ? 'bg-slate-800/50' : 'bg-purple-50',
      iconColor: dark ? 'text-purple-400' : 'text-purple-600',
      change: '',
      changeColor: ''
    },
    { 
      title: '推荐作品', 
      value: portfolioStore.featuredPortfolios.value.length.toString(),
      icon: TrendCharts,
      color: dark ? 'bg-slate-800/50' : 'bg-orange-50',
      iconColor: dark ? 'text-orange-400' : 'text-orange-600',
      change: '',
      changeColor: ''
    }
  ]
})

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

const loadDashboardData = async () => {
  // 启动自动同步
  startAutoSync()
  
  // 并行加载数据
  await Promise.all([
    portfolioStore.fetchPortfolios(),
    blogStore.fetchBlogs(false, true) // 包含未发布的博客
  ])
}

onMounted(() => {
  loadDashboardData()
})

// 组件卸载时停止自动同步
import { onUnmounted } from 'vue'
onUnmounted(() => {
  stopAutoSync()
})
</script>