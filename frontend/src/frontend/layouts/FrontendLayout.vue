<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0b0c10] text-slate-900 dark:text-lab-text transition-colors duration-300 font-mono relative overflow-hidden flex flex-col md:cursor-none">
    <!-- 背景网格 - 工业风核心 -->
    <div class="fixed inset-0 z-0 pointer-events-none opacity-20 dark:opacity-10 bg-[length:40px_40px] bg-grid-pattern dark:bg-grid-pattern-dark"></div>
    <!-- 噪点纹理 -->
    <div class="bg-noise"></div>
    
    <!-- 互动装饰层 (看板娘 & 动效) -->
    <InteractiveOverlay />

    <!-- 顶部导航栏 - 硬朗的工业设计 -->
    <header class="sticky top-0 z-50 bg-white/90 dark:bg-[#1f2833]/90 backdrop-blur-md border-b-2 border-slate-200 dark:border-slate-800 shadow-sm">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="flex justify-between items-center h-16">
          <!-- Logo 区域 - 终端风格 -->
          <router-link to="/" class="group flex items-center space-x-3">
            <div class="w-10 h-10 bg-slate-900 dark:bg-lab-accent text-white dark:text-black flex items-center justify-center font-bold text-lg border-2 border-transparent group-hover:border-slate-900 dark:group-hover:border-white transition-all duration-300 shadow-md">
              <span class="group-hover:animate-pulse">&gt;_</span>
            </div>
            <div class="flex flex-col leading-none">
              <span class="font-bold text-lg tracking-wider uppercase text-slate-900 dark:text-white group-hover:text-lab-darkAccent transition-colors">AUGUST.LAB</span>
              <span class="text-[10px] text-slate-500 dark:text-slate-400 tracking-[0.2em] uppercase">系统在线</span>
            </div>
          </router-link>

          <!-- 桌面导航 - 标签式设计 -->
          <nav class="hidden md:flex space-x-1">
            <router-link 
              v-for="item in navItems" 
              :key="item.name"
              :to="item.path"
              class="relative px-5 py-2 text-sm font-bold uppercase tracking-wide transition-all duration-200 group overflow-hidden"
              :class="[
                $route.path === item.path 
                  ? 'text-white bg-slate-900 dark:bg-lab-accent dark:text-black shadow-md translate-y-[-2px]' 
                  : 'text-slate-600 dark:text-slate-400 hover:text-slate-900 dark:hover:text-white hover:bg-slate-100 dark:hover:bg-slate-800'
              ]"
            >
              <span class="relative z-10">{{ item.name }}</span>
              <!-- 选中状态下的指示器 -->
              <span v-if="$route.path === item.path" class="absolute bottom-0 left-0 w-full h-[2px] bg-lab-accent dark:bg-black"></span>
            </router-link>
          </nav>

          <!-- 右侧工具栏 -->
          <div class="flex items-center space-x-4">
             <!-- 移动端菜单按钮 -->
            <button 
              @click="toggleMobileMenu"
              class="md:hidden p-2 text-slate-600 dark:text-slate-300 hover:bg-slate-100 dark:hover:bg-slate-800 border-2 border-transparent hover:border-slate-300 dark:hover:border-slate-600 transition-all"
            >
              <span class="sr-only">Open menu</span>
              <div class="w-6 h-5 flex flex-col justify-between">
                <span class="w-full h-0.5 bg-current transform transition-transform duration-300" :class="{ 'rotate-45 translate-y-2': mobileMenuOpen }"></span>
                <span class="w-full h-0.5 bg-current transition-opacity duration-300" :class="{ 'opacity-0': mobileMenuOpen }"></span>
                <span class="w-full h-0.5 bg-current transform transition-transform duration-300" :class="{ '-rotate-45 -translate-y-2.5': mobileMenuOpen }"></span>
              </div>
            </button>
          </div>
        </div>
      </div>
      
      <!-- 移动端菜单 - 抽屉式 -->
      <transition
        enter-active-class="transition duration-200 ease-out"
        enter-from-class="transform -translate-y-2 opacity-0"
        enter-to-class="transform translate-y-0 opacity-100"
        leave-active-class="transition duration-150 ease-in"
        leave-from-class="transform translate-y-0 opacity-100"
        leave-to-class="transform -translate-y-2 opacity-0"
      >
        <div v-if="mobileMenuOpen" class="md:hidden absolute top-16 left-0 w-full bg-white dark:bg-[#1f2833] border-b-2 border-slate-200 dark:border-slate-800 shadow-xl z-40">
          <div class="px-4 py-4 space-y-2">
            <router-link 
              v-for="item in navItems" 
              :key="item.name"
              :to="item.path"
              @click="closeMobileMenu"
              class="block px-4 py-3 text-base font-bold uppercase tracking-wider border-l-4 transition-all duration-200"
              :class="[
                $route.path === item.path 
                  ? 'border-slate-900 dark:border-lab-accent bg-slate-50 dark:bg-slate-800 text-slate-900 dark:text-white' 
                  : 'border-transparent text-slate-500 dark:text-slate-400 hover:bg-slate-50 dark:hover:bg-slate-800 hover:text-slate-900 dark:hover:text-white'
              ]"
            >
              {{ item.name }}
            </router-link>
          </div>
        </div>
      </transition>
    </header>

    <!-- 主要内容区域 -->
    <main class="flex-1 relative z-10 w-full max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 md:py-12">
      <router-view v-slot="{ Component }">
        <transition 
          name="fade-slide" 
          mode="out-in"
          appear
        >
          <component :is="Component" />
        </transition>
      </router-view>
    </main>

    <!-- 页脚 - 系统状态栏风格 -->
    <footer class="mt-auto bg-slate-900 dark:bg-[#050608] text-slate-400 border-t-4 border-lab-accent dark:border-lab-darkAccent py-8 relative z-10">
      <div class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div class="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
           <!-- 列 1: 系统信息 -->
           <div class="space-y-4">
              <h3 class="text-white font-bold uppercase tracking-widest text-sm border-b border-slate-700 pb-2 inline-block">系统信息</h3>
              <p class="text-xs leading-relaxed font-mono">
                <span class="block mb-1">> 核心: AUGUST.LAB.CORE.V2</span>
                <span class="block mb-1">> 状态: 运行中</span>
                <span class="block">> 运行时间: {{ uptime }}</span>
              </p>
           </div>
           
           <!-- 列 2: 快速链接 -->
           <div class="space-y-4">
              <h3 class="text-white font-bold uppercase tracking-widest text-sm border-b border-slate-700 pb-2 inline-block">快速访问</h3>
              <div class="flex flex-wrap gap-4 text-xs font-mono">
                <router-link to="/portfolio" class="hover:text-lab-accent transition-colors">[ 作品集 ]</router-link>
                <router-link to="/blog" class="hover:text-lab-accent transition-colors">[ 博客日志 ]</router-link>
                <router-link to="/about" class="hover:text-lab-accent transition-colors">[ 关于开发者 ]</router-link>
              </div>
           </div>

           <!-- 列 3: 联系终端 -->
           <div class="space-y-4">
              <h3 class="text-white font-bold uppercase tracking-widest text-sm border-b border-slate-700 pb-2 inline-block">通信链路</h3>
               <div class="flex space-x-4">
                <a href="https://github.com" target="_blank" class="w-8 h-8 flex items-center justify-center bg-slate-800 hover:bg-lab-accent hover:text-black transition-all duration-300">
                  <svg class="w-4 h-4" fill="currentColor" viewBox="0 0 24 24" aria-hidden="true"><path fill-rule="evenodd" d="M12 2C6.477 2 2 6.484 2 12.017c0 4.425 2.865 8.18 6.839 9.504.5.092.682-.217.682-.483 0-.237-.008-.868-.013-1.703-2.782.605-3.369-1.343-3.369-1.343-.454-1.158-1.11-1.466-1.11-1.466-.908-.62.069-.608.069-.608 1.003.07 1.531 1.032 1.531 1.032.892 1.53 2.341 1.088 2.91.832.092-.647.35-1.088.636-1.338-2.22-.253-4.555-1.113-4.555-4.951 0-1.093.39-1.988 1.029-2.688-.103-.253-.446-1.272.098-2.65 0 0 .84-.27 2.75 1.026A9.564 9.564 0 0112 6.844c.85.004 1.705.115 2.504.337 1.909-1.296 2.747-1.027 2.747-1.027.546 1.379.202 2.398.1 2.651.64.7 1.028 1.595 1.028 2.688 0 3.848-2.339 4.695-4.566 4.943.359.309.678.92.678 1.855 0 1.338-.012 2.419-.012 2.747 0 .268.18.58.688.482A10.019 10.019 0 0022 12.017C22 6.484 17.522 2 12 2z" clip-rule="evenodd" /></svg>
                </a>
                <a href="mailto:hello@august.lab" class="w-8 h-8 flex items-center justify-center bg-slate-800 hover:bg-lab-accent hover:text-black transition-all duration-300">
                  <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path></svg>
                </a>
              </div>
           </div>
        </div>

        <!-- 底部版权栏 -->
        <div class="border-t border-slate-800 pt-8 flex flex-col md:flex-row justify-between items-center text-xs font-mono">
          <div class="mb-4 md:mb-0">
            <span class="text-lab-accent">© {{ new Date().getFullYear() }} AUGUST.LAB</span>
            <span class="mx-2 text-slate-700">|</span>
            <span>版权所有</span>
          </div>
          <div class="flex items-center space-x-4">
             <div class="flex items-center space-x-2 bg-slate-800 px-3 py-1 rounded">
                <span class="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                <span class="text-slate-300">系统状态: 正常</span>
             </div>
             <a href="https://beian.miit.gov.cn/" target="_blank" class="hover:text-white transition-colors">冀ICP备2025117309号</a>
          </div>
        </div>
      </div>
    </footer>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, computed } from 'vue'
import { useRoute } from 'vue-router'
import InteractiveOverlay from '../components/decorations/InteractiveOverlay.vue'

const route = useRoute()
const mobileMenuOpen = ref(false)
const startTime = ref(Date.now())
const uptime = ref('00:00:00')

const navItems = [
  { name: '首页', path: '/' },
  { name: '作品集', path: '/portfolio' },
  { name: '博客', path: '/blog' },
  { name: '产品', path: '/products' },
  { name: '关于', path: '/about' }
]

const toggleMobileMenu = () => {
  mobileMenuOpen.value = !mobileMenuOpen.value
}

const closeMobileMenu = () => {
  mobileMenuOpen.value = false
}

// 模拟系统运行时间
const updateUptime = () => {
  const diff = Math.floor((Date.now() - startTime.value) / 1000)
  const h = Math.floor(diff / 3600).toString().padStart(2, '0')
  const m = Math.floor((diff % 3600) / 60).toString().padStart(2, '0')
  const s = (diff % 60).toString().padStart(2, '0')
  uptime.value = `${h}:${m}:${s}`
}

let timer: ReturnType<typeof setInterval>

onMounted(() => {
  timer = setInterval(updateUptime, 1000)
})

onUnmounted(() => {
  clearInterval(timer)
})
</script>

<style>
/* 页面切换动画 */
.fade-slide-enter-active,
.fade-slide-leave-active {
  transition: all 0.3s ease;
}

.fade-slide-enter-from {
  opacity: 0;
  transform: translateY(10px);
}

.fade-slide-leave-to {
  opacity: 0;
  transform: translateY(-10px);
}
</style>

<style>
/* 全局光标控制 */
@media (min-width: 768px) {
  /* 强制在可交互元素上也隐藏系统光标，由自定义光标接管 */
  a, button, [role="button"], .cursor-pointer {
    cursor: none !important;
  }
  
  /* 输入框恢复系统光标，避免输入困难 */
  input, textarea, [contenteditable="true"] {
    cursor: text !important;
  }
}
</style>
