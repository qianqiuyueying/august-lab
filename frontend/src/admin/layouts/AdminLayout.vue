<template>
  <div
    class="min-h-screen flex bg-gray-50 dark:bg-lab-bg text-gray-900 dark:text-lab-text transition-colors duration-300 font-sans"
  >
    <!-- 侧边栏 -->
    <aside
      class="fixed inset-y-0 left-0 z-50 flex flex-col transition-all duration-300 ease-out glass-panel border-r border-gray-200 dark:border-lab-border"
      :class="collapsed ? 'w-16' : 'w-64'"
    >
      <!-- Logo 区域 -->
      <div class="h-16 flex items-center justify-center border-b border-gray-200 dark:border-lab-border/50">
        <div class="flex items-center gap-3 overflow-hidden px-4 w-full" :class="collapsed ? 'justify-center' : ''">
          <div class="w-8 h-8 rounded bg-gradient-to-br from-lab-accent to-blue-600 flex items-center justify-center shadow-[0_0_15px_rgba(0,240,255,0.3)] shrink-0">
            <span class="text-black font-bold text-sm font-mono">A</span>
          </div>
          <span 
            v-show="!collapsed" 
            class="text-lg font-bold tracking-wider font-display whitespace-nowrap dark:text-white"
          >
            AUGUST<span class="text-lab-accent">.ADMIN</span>
          </span>
        </div>
      </div>

      <!-- 导航菜单 -->
      <el-scrollbar class="flex-1">
        <el-menu
          :default-active="$route.path"
          :collapse="collapsed"
          router
          class="border-none bg-transparent !w-full"
          :collapse-transition="false"
        >
          <template v-for="item in menuItems" :key="item.index">
            <!-- 有子菜单的项 -->
            <el-sub-menu v-if="item.children" :index="item.index">
              <template #title>
                <el-icon :size="18"><component :is="item.icon" /></el-icon>
                <span class="font-medium">{{ item.title }}</span>
              </template>
              <el-menu-item 
                v-for="child in item.children" 
                :key="child.index"
                :index="child.index"
                class="!pl-12"
              >
                <template #title>
                  <span class="text-sm">{{ child.title }}</span>
                </template>
              </el-menu-item>
            </el-sub-menu>
            
            <!-- 普通菜单项 -->
            <el-menu-item v-else :index="item.index">
              <el-icon :size="18"><component :is="item.icon" /></el-icon>
              <template #title>
                <span class="font-medium">{{ item.title }}</span>
              </template>
            </el-menu-item>
          </template>
        </el-menu>
      </el-scrollbar>

      <!-- 底部操作 -->
      <div class="p-4 border-t border-gray-200 dark:border-lab-border/50">
        <button 
          @click="toggleSidebar"
          class="w-full flex items-center justify-center p-2 rounded hover:bg-gray-100 dark:hover:bg-white/5 transition-colors text-gray-500 dark:text-lab-muted"
        >
          <el-icon><component :is="collapsed ? Expand : Fold" /></el-icon>
        </button>
      </div>
    </aside>

    <!-- 主内容区 -->
    <div 
      class="flex-1 flex flex-col min-h-screen transition-all duration-300"
      :class="collapsed ? 'ml-16' : 'ml-64'"
    >
      <!-- 顶部栏 -->
      <header class="h-16 sticky top-0 z-40 glass-panel border-b border-gray-200 dark:border-lab-border/50 px-6 flex items-center justify-between backdrop-blur-md bg-white/80 dark:bg-lab-bg/80">
        <!-- 页面标题 -->
        <div class="flex items-center">
          <h1 class="text-xl font-display font-semibold text-gray-800 dark:text-white tracking-tight">
            {{ pageTitle }}
          </h1>
        </div>

        <!-- 右侧工具栏 -->
        <div class="flex items-center gap-4">
          <!-- 主题切换 -->
          <button
            @click="toggleTheme"
            class="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-white/10 transition-colors text-gray-600 dark:text-lab-muted hover:text-primary-600 dark:hover:text-lab-accent"
            title="切换主题"
          >
            <el-icon :size="20">
              <component :is="isDark ? Sunny : Moon" />
            </el-icon>
          </button>

          <!-- 预览按钮 -->
          <button 
            @click="goToFrontend"
            class="flex items-center gap-2 px-3 py-1.5 rounded-full border border-gray-200 dark:border-lab-border hover:border-primary-500 dark:hover:border-lab-accent text-sm font-medium transition-all hover:shadow-lg hover:shadow-primary-500/20 dark:hover:shadow-lab-accent/20"
          >
            <el-icon><Monitor /></el-icon>
            <span class="hidden sm:inline">Live Preview</span>
          </button>
          
          <!-- 用户下拉 -->
          <el-dropdown trigger="click">
            <div class="flex items-center gap-3 cursor-pointer pl-4 border-l border-gray-200 dark:border-lab-border">
              <div class="text-right hidden sm:block">
                <div class="text-sm font-medium dark:text-white">{{ userInfo.name }}</div>
                <div class="text-xs text-gray-500 dark:text-lab-muted">Administrator</div>
              </div>
              <el-avatar :size="36" :src="userInfo.avatar" class="border-2 border-white dark:border-lab-border shadow-sm">
                {{ userInfo.name.charAt(0) }}
              </el-avatar>
            </div>
            <template #dropdown>
              <el-dropdown-menu class="w-48">
                <el-dropdown-item @click="router.push('/admin/profile')">
                  <el-icon><User /></el-icon>个人资料
                </el-dropdown-item>
                <el-dropdown-item divided @click="logout">
                  <el-icon class="text-red-500"><SwitchButton /></el-icon>
                  <span class="text-red-500">退出登录</span>
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <!-- 内容区域 -->
      <main class="flex-1 p-6 overflow-x-hidden">
        <div class="max-w-7xl mx-auto animate-fade-in">
          <router-view v-slot="{ Component }">
            <transition name="fade" mode="out-in">
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
      </main>
    </div>
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
    '/admin': 'Dashboard',
    '/admin/portfolio': 'Portfolio',
    '/admin/products': 'Products',
    '/admin/analytics': 'Analytics',
    '/admin/monitoring': 'Monitoring',
    '/admin/blog': 'Blog',
    '/admin/extensions': 'Extensions',
    '/admin/profile': 'Profile'
  }
  // 支持匹配父路径
  if (route.path.startsWith('/admin/portfolio')) return 'Portfolio Manager'
  if (route.path.startsWith('/admin/products')) return 'Product Manager'
  if (route.path.startsWith('/admin/analytics')) return 'Analytics Center'
  if (route.path.startsWith('/admin/monitoring')) return 'System Monitor'
  return titleMap[route.path] || 'Admin Console'
})

const menuItems: MenuItem[] = [
  {
    index: '/admin',
    icon: House,
    title: 'Dashboard'
  },
  {
    index: '/admin/blog',
    icon: Document,
    title: 'Blog Posts'
  },
  {
    index: '/admin/portfolio',
    icon: Briefcase,
    title: 'Portfolio'
  },
  {
    index: '/admin/products',
    icon: Box,
    title: 'Products'
  },
  {
    index: 'product-analytics-group',
    icon: Setting,
    title: 'Analytics',
    children: [
      {
        index: '/admin/analytics',
        icon: Setting,
        title: 'Overview'
      },
      {
        index: '/admin/monitoring',
        icon: Warning,
        title: 'Health Check'
      }
    ]
  },
  {
    index: '/admin/extensions',
    icon: Tools,
    title: 'Extensions'
  },
  {
    index: '/admin/profile',
    icon: User,
    title: 'Profile'
  }
]

const toggleSidebar = () => {
  collapsed.value = !collapsed.value
}

const logout = async () => {
  try {
    await ElMessageBox.confirm(
      'Are you sure you want to logout?',
      'Confirm Logout',
      {
        confirmButtonText: 'Logout',
        cancelButtonText: 'Cancel',
        type: 'warning',
        customClass: 'dark:bg-lab-card dark:border-lab-border'
      }
    )
    
    try {
      await authAPI.logout()
    } catch (error) {
      console.warn('Logout API failed:', error)
    }
    
    localStorage.removeItem('admin_token')
    ElMessage.success('Logged out successfully')
    router.push('/admin/login')
    
  } catch (error) {
    // Cancelled
  }
}

const goToFrontend = () => {
  window.open('/', '_blank')
}

onMounted(async () => {
  try {
    await authAPI.verify()
  } catch (error) {
    console.error('Token verification failed:', error)
    localStorage.removeItem('admin_token')
    router.push('/admin/login')
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

/* Custom Scrollbar for Menu */
:deep(.el-scrollbar__bar.is-vertical) {
  width: 4px;
}
:deep(.el-scrollbar__thumb) {
  background-color: rgba(156, 163, 175, 0.3);
}
</style>