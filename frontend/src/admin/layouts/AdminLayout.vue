<template>
  <div
    class="admin-app min-h-screen"
    :class="isDark ? 'bg-[#0F172A] text-gray-100' : 'bg-gray-50 text-gray-900'"
  >
    <el-container class="min-h-screen">
      <!-- 侧边栏：实验室模块区 -->
      <el-aside
        :width="sidebarWidth"
        :class="[
          'transition-all duration-300 border-r',
          isDark
            ? 'bg-[#1E293B] border-[rgba(148,163,184,0.15)]'
            : 'bg-white border-[rgba(59,130,246,0.1)]'
        ]"
      >
        <!-- 侧边栏头部 -->
        <div
          :class="[
            'p-4 border-b',
            isDark ? 'border-[rgba(148,163,184,0.15)]' : 'border-gray-200/80'
          ]"
        >
          <div class="flex items-center" :class="collapsed ? 'justify-center' : 'space-x-2'">
            <div
              class="w-8 h-8 rounded-lg flex items-center justify-center text-white font-bold text-sm"
              style="background: linear-gradient(135deg, #3b82f6, #8b5cf6)"
            >
              A
            </div>
            <span
              v-if="!collapsed"
              :class="['text-lg font-semibold tracking-tight', isDark ? 'text-gray-100' : 'text-gray-900']"
            >
              管理后台
            </span>
          </div>
        </div>

        <!-- 导航菜单 -->
        <el-menu
          :default-active="$route.path"
          :collapse="collapsed"
          router
          class="admin-menu border-none"
          :background-color="isDark ? '#1E293B' : '#ffffff'"
          :text-color="isDark ? '#94a3b8' : '#374151'"
          :active-text-color="isDark ? '#60a5fa' : '#2563eb'"
        >
          <template v-for="item in menuItems" :key="item.index">
            <!-- 有子菜单的项 -->
            <el-sub-menu v-if="item.children" :index="item.index">
              <template #title>
                <el-icon><component :is="item.icon" /></el-icon>
                <span>{{ item.title }}</span>
              </template>
              <el-menu-item 
                v-for="child in item.children" 
                :key="child.index"
                :index="child.index"
              >
                <el-icon><component :is="child.icon" /></el-icon>
                <template #title>{{ child.title }}</template>
              </el-menu-item>
            </el-sub-menu>
            
            <!-- 普通菜单项 -->
            <el-menu-item v-else :index="item.index">
              <el-icon><component :is="item.icon" /></el-icon>
              <template #title>{{ item.title }}</template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-aside>
      
      <el-container>
        <!-- 顶部栏：64px 固定节奏 -->
        <el-header
          :class="[
            'h-16 border-b flex items-center justify-between px-6 sticky top-0 z-50',
            isDark
              ? 'bg-[#1E293B] border-[rgba(148,163,184,0.15)] text-gray-100'
              : 'bg-white border-[rgba(59,130,246,0.1)] text-gray-900'
          ]"
        >
          <div class="flex items-center space-x-4">
            <!-- 侧边栏折叠按钮 -->
            <el-button 
              type="text" 
              @click="toggleSidebar"
              :class="isDark ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'"
            >
              <el-icon size="18">
                <component :is="collapsed ? Expand : Fold" />
              </el-icon>
            </el-button>
            
            <!-- 页面标题 -->
            <div :class="['text-lg font-medium', isDark ? 'text-gray-100' : 'text-gray-900']">
              {{ pageTitle }}
            </div>
          </div>
          
          <!-- 右侧操作区 -->
          <div class="flex items-center space-x-4">
            <!-- 深色/浅色模式切换 -->
            <el-button
              type="text"
              @click="toggleTheme"
              :class="isDark ? 'text-gray-300 hover:text-white' : 'text-gray-600 hover:text-gray-900'"
            >
              <el-icon>
                <component :is="isDark ? Sunny : Moon" />
              </el-icon>
              <span class="ml-1">{{ isDark ? '浅色模式' : '深色模式' }}</span>
            </el-button>

            <!-- 前台预览按钮 -->
            <el-button 
              type="text" 
              @click="goToFrontend"
              :class="isDark ? 'text-gray-300 hover:text-primary-400' : 'text-gray-600 hover:text-primary-600'"
            >
              <el-icon><Monitor /></el-icon>
              <span class="ml-1">预览网站</span>
            </el-button>
            
            <!-- 用户下拉菜单 -->
            <el-dropdown>
              <div :class="['flex items-center space-x-2 cursor-pointer px-2 py-1 rounded', isDark ? 'hover:bg-slate-700/50' : 'hover:bg-gray-50']">
                <el-avatar :size="32" :src="userInfo.avatar">
                  {{ userInfo.name.charAt(0) }}
                </el-avatar>
                <span :class="['text-sm', isDark ? 'text-gray-200' : 'text-gray-700']">{{ userInfo.name }}</span>
                <el-icon :class="isDark ? 'text-gray-400' : 'text-gray-400'"><ArrowDown /></el-icon>
              </div>
              <template #dropdown>
                <el-dropdown-menu>
                  <el-dropdown-item @click="logout">
                    <el-icon><SwitchButton /></el-icon>
                    <span class="ml-2">退出登录</span>
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </div>
        </el-header>
        
        <!-- 主要内容：黄金节奏 + 模块化留白 -->
        <el-main
          class="admin-main-wrap p-6 overflow-auto"
          :class="isDark ? 'bg-[#0F172A] text-gray-100' : 'bg-gray-50 text-gray-900'"
        >
          <router-view />
        </el-main>
      </el-container>
    </el-container>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  House, 
  Briefcase, 
  Document, 
  User, 
  ArrowDown, 
  SwitchButton,
  Setting,
  Monitor,
  Expand,
  Fold,
  Box,
  Warning,
  Tools,
  Moon,
  Sunny
} from '@element-plus/icons-vue'
import { authAPI } from '../../shared/api'
import { useDarkMode } from '../composables/useDarkMode'
import type { Component } from 'vue'

// 定义菜单项类型
interface MenuItem {
  index: string
  icon: Component
  title: string
  children?: MenuItem[]
}

const route = useRoute()
const router = useRouter()
const collapsed = ref(false)
const { isDark, toggle: toggleTheme } = useDarkMode()
const userInfo = ref({
  name: '管理员',
  avatar: ''
})

const pageTitle = computed(() => {
  const titleMap: Record<string, string> = {
    '/admin': '仪表盘',
    '/admin/portfolio': '作品管理',
    '/admin/products': '产品管理',
    '/admin/analytics': '产品分析',
    '/admin/monitoring': '产品监控',
    '/admin/blog': '博客管理',
    '/admin/extensions': '扩展管理',
    '/admin/profile': '个人信息管理'
  }
  // 支持匹配父路径
  if (route.path.startsWith('/admin/portfolio')) {
    return '作品管理'
  }
  if (route.path.startsWith('/admin/products') || route.path.startsWith('/admin/analytics') || route.path.startsWith('/admin/monitoring')) {
    return titleMap[route.path] || '产品管理'
  }
  return titleMap[route.path] || '管理后台'
})

const sidebarWidth = computed(() => collapsed.value ? '64px' : '250px')

const menuItems: MenuItem[] = [
  {
    index: '/admin',
    icon: House,
    title: '仪表盘'
  },
  {
    index: '/admin/blog',
    icon: Document,
    title: '博客管理'
  },
  {
    index: '/admin/portfolio',
    icon: Briefcase,
    title: '作品管理'
  },
  {
    index: '/admin/products',
    icon: Box,
    title: '产品管理'
  },
  {
    index: 'product-analytics-group',
    icon: Setting,
    title: '产品分析',
    children: [
      {
        index: '/admin/analytics',
        icon: Setting,
        title: '产品分析'
      },
      {
        index: '/admin/monitoring',
        icon: Warning,
        title: '产品监控'
      }
    ]
  },
  {
    index: '/admin/extensions',
    icon: Tools,
    title: '扩展管理'
  },
  {
    index: '/admin/profile',
    icon: User,
    title: '个人信息'
  }
]

const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}

const logout = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要退出登录吗？',
      '确认退出',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    try {
      // 调用登出API
      await authAPI.logout()
    } catch (error) {
      console.warn('登出API调用失败:', error)
    }
    
    // 清除登录状态
    localStorage.removeItem('admin_token')
    ElMessage.success('已退出登录')
    router.push('/admin/login')
    
  } catch (error) {
    // 用户取消退出
  }
}

const goToFrontend = () => {
  window.open('/', '_blank')
}

// 验证登录状态
onMounted(async () => {
  try {
    await authAPI.verify()
  } catch (error) {
    console.error('Token验证失败:', error)
    localStorage.removeItem('admin_token')
    router.push('/admin/login')
  }
})
</script>