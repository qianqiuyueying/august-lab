<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900">
    <!-- 导航头部 -->
    <header class="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700 sticky top-0 z-50">
      <ResponsiveContainer size="xl" :padding="{ xs: '0 1rem', sm: '0 1.5rem', lg: '0 2rem' }">
        <div class="flex justify-between items-center h-16">
          <!-- Logo -->
          <router-link to="/" class="flex items-center space-x-2 flex-shrink-0">
            <div class="w-8 h-8 bg-primary-600 rounded-lg flex items-center justify-center">
              <span class="text-white font-bold text-sm">A</span>
            </div>
            <span class="text-xl font-semibold text-gray-900 hidden xs:block">August.Lab</span>
          </router-link>
          
          <!-- 导航菜单 -->
          <nav class="show-desktop">
            <div class="flex space-x-8">
              <router-link 
                v-for="item in navItems" 
                :key="item.name"
                :to="item.path"
                class="nav-link"
                :class="{ 'nav-link-active': $route.path === item.path }"
              >
                {{ item.name }}
              </router-link>
            </div>
          </nav>
          
          <!-- 移动端菜单按钮 -->
          <button 
            @click="toggleMobileMenu"
            class="show-mobile p-2 rounded-md text-gray-600 hover:text-gray-900 hover:bg-gray-100 transition-colors duration-200"
            :class="{ 'text-primary-600': mobileMenuOpen }"
            aria-label="切换菜单"
          >
            <svg 
              class="w-6 h-6 transition-transform duration-200" 
              :class="{ 'rotate-90': mobileMenuOpen }"
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path 
                stroke-linecap="round" 
                stroke-linejoin="round" 
                stroke-width="2" 
                :d="mobileMenuOpen ? 'M6 18L18 6M6 6l12 12' : 'M4 6h16M4 12h16M4 18h16'"
              />
            </svg>
          </button>
        </div>
        
        <!-- 移动端菜单 -->
        <Transition
          enter-active-class="transition-all duration-300 ease-out"
          enter-from-class="opacity-0 -translate-y-2"
          enter-to-class="opacity-100 translate-y-0"
          leave-active-class="transition-all duration-200 ease-in"
          leave-from-class="opacity-100 translate-y-0"
          leave-to-class="opacity-0 -translate-y-2"
        >
          <div v-show="mobileMenuOpen" class="show-mobile py-4 border-t border-gray-200">
            <nav class="space-y-2">
              <router-link 
                v-for="item in navItems" 
                :key="item.name"
                :to="item.path"
                @click="closeMobileMenu"
                class="block px-3 py-2 text-base font-medium text-gray-600 hover:text-primary-600 hover:bg-gray-50 rounded-md transition-all duration-200"
                :class="{ 'text-primary-600 bg-primary-50': $route.path === item.path }"
              >
                {{ item.name }}
              </router-link>
            </nav>
          </div>
        </Transition>
      </ResponsiveContainer>
    </header>
    
    <!-- 主要内容区域 -->
    <main class="flex-1">
      <router-view />
    </main>
    
    <!-- 页脚 - 实验室彩蛋 -->
    <footer class="bg-white dark:bg-slate-800 border-t border-gray-200 dark:border-slate-700 py-6">
      <ResponsiveContainer size="xl">
        <div class="text-center">
          <div class="flex items-center justify-center space-x-2 mb-2">
            <div class="w-5 h-5 bg-primary-500 rounded-md flex items-center justify-center shadow-md">
              <span class="text-white font-bold text-xs">A</span>
            </div>
            <span class="text-base font-semibold text-gray-900 dark:text-gray-50">August.Lab</span>
          </div>
          <p class="text-gray-600 dark:text-gray-400 text-xs mb-2">
            © {{ new Date().getFullYear() }} August.Lab. All rights reserved.
          </p>
          <!-- 实验室彩蛋：Build in Public + 实时时间 + Git commit -->
          <div class="group relative inline-block">
            <code class="text-gray-500 dark:text-gray-500 text-xs font-mono">
              // Build in Public • Last sync: {{ currentTime }}
            </code>
            <!-- Hover时显示Git commit -->
            <div 
              v-if="gitCommit"
              class="absolute bottom-full left-1/2 transform -translate-x-1/2 mb-2 px-2 py-1 bg-gray-900 dark:bg-slate-700 text-white text-xs rounded opacity-0 group-hover:opacity-100 transition-opacity pointer-events-none whitespace-nowrap"
            >
              {{ gitCommit }}
              <div class="absolute top-full left-1/2 transform -translate-x-1/2 w-0 h-0 border-l-4 border-r-4 border-t-4 border-transparent border-t-gray-900 dark:border-t-slate-700"></div>
            </div>
          </div>
          <p class="text-gray-500 dark:text-gray-500 text-xs mt-2">
            <a href="https://beian.miit.gov.cn/" target="_blank" rel="noopener noreferrer" class="hover:text-primary-500 dark:hover:text-primary-400 transition-colors">
              冀ICP备2025117309号
            </a>
          </p>
        </div>
      </ResponsiveContainer>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import ResponsiveContainer from '../../shared/components/ResponsiveContainer.vue'
import { useResponsive } from '../../shared/composables/useResponsive'

const route = useRoute()
const { isMobile } = useResponsive()

const mobileMenuOpen = ref(false)

// 实验室彩蛋：实时时间
const currentTime = ref('')
const updateTime = () => {
  const now = new Date()
  currentTime.value = now.toLocaleTimeString('zh-CN', { 
    hour12: false,
    hour: '2-digit',
    minute: '2-digit',
    second: '2-digit'
  })
}

// Git commit（从环境变量获取，构建时注入）
const gitCommit = computed(() => {
  // @ts-ignore
  return import.meta.env.VITE_GIT_COMMIT || null
})

const navItems = [
  { name: '首页', path: '/' },
  { name: '作品集', path: '/portfolio' },
  { name: '博客', path: '/blog' },
  { name: '关于我', path: '/about' }
]

// 切换移动端菜单
const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

// 关闭移动端菜单
const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

// 监听路由变化，自动关闭移动端菜单
const handleRouteChange = () => {
  if (mobileMenuOpen.value) {
    closeMobileMenu()
  }
}

// 监听点击外部区域关闭菜单
const handleClickOutside = (event: Event) => {
  if (!mobileMenuOpen.value) return
  
  const target = event.target as HTMLElement
  const header = document.querySelector('header')
  
  if (header && !header.contains(target)) {
    closeMobileMenu()
  }
}

// 监听ESC键关闭菜单
const handleEscKey = (event: KeyboardEvent) => {
  if (event.key === 'Escape' && mobileMenuOpen.value) {
    closeMobileMenu()
  }
}

// 监听屏幕尺寸变化，桌面端自动关闭移动菜单
const handleResize = () => {
  if (!isMobile.value && mobileMenuOpen.value) {
    closeMobileMenu()
  }
}

let timeInterval: ReturnType<typeof setInterval> | null = null

onMounted(() => {
  document.addEventListener('click', handleClickOutside)
  document.addEventListener('keydown', handleEscKey)
  window.addEventListener('resize', handleResize)
  
  // 初始化时间并每秒更新
  updateTime()
  timeInterval = setInterval(updateTime, 1000)
})

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside)
  document.removeEventListener('keydown', handleEscKey)
  window.removeEventListener('resize', handleResize)
  
  if (timeInterval) {
    clearInterval(timeInterval)
  }
})

// 监听路由变化
import { watch } from 'vue'
watch(() => route.path, handleRouteChange)
</script>