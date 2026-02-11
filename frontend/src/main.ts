import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'
import './admin/styles/dark-mode.css'

import App from './App.vue'

/**
 * 抑制 ResizeObserver 的已知无害控制台错误。
 * 当一帧内发生多次尺寸变化（如 el-table 列宽重算、布局重排）时，浏览器会抛出此错误。
 * 来自 UI 库（如 Element Plus）内部，不影响功能，仅避免控制台噪音。
 * @see https://github.com/WICG/resize-observer/issues/38
 */
if (typeof window !== 'undefined') {
  const prevOnError = window.onerror
  window.onerror = function (
    message: string | Event,
    source?: string,
    lineno?: number,
    colno?: number,
    error?: Error
  ): boolean {
    const msg = typeof message === 'string' ? message : (message as ErrorEvent)?.message ?? ''
    if (msg.includes('ResizeObserver loop')) {
      return true // 阻止默认控制台输出
    }
    return prevOnError ? prevOnError.call(window, message, source, lineno, colno, error) : false
  }
}
import { frontendRoutes } from './frontend/router'
import { adminRoutes } from './admin/router'
import { setupGlobalErrorHandler } from './shared/composables/useErrorHandler'
import { authAPI } from './shared/api'

/**
 * 应用Element Plus深色模式CSS变量
 */
function applyElementPlusDarkTheme() {
  if (typeof document === 'undefined') return
  const html = document.documentElement
  html.style.setProperty('--el-bg-color', '#1e293b')
  html.style.setProperty('--el-bg-color-page', '#0f172a')
  html.style.setProperty('--el-text-color-primary', '#f3f4f6')
  html.style.setProperty('--el-text-color-regular', '#d1d5db')
  html.style.setProperty('--el-text-color-secondary', '#9ca3af')
  html.style.setProperty('--el-border-color', 'rgba(148, 163, 184, 0.15)')
  html.style.setProperty('--el-border-color-light', 'rgba(148, 163, 184, 0.2)')
  html.style.setProperty('--el-border-color-lighter', 'rgba(148, 163, 184, 0.25)')
  html.style.setProperty('--el-fill-color', '#334155')
  html.style.setProperty('--el-fill-color-light', '#475569')
  html.style.setProperty('--el-fill-color-lighter', '#64748b')
  html.style.setProperty('--el-fill-color-extra-light', '#94a3b8')
  html.style.setProperty('--el-fill-color-dark', '#1e293b')
  html.style.setProperty('--el-fill-color-darker', '#0f172a')
  html.style.setProperty('--el-fill-color-blank', 'transparent')
}

/**
 * 移除Element Plus深色模式CSS变量
 */
function removeElementPlusDarkTheme() {
  if (typeof document === 'undefined') return
  const html = document.documentElement
  html.style.removeProperty('--el-bg-color')
  html.style.removeProperty('--el-bg-color-page')
  html.style.removeProperty('--el-text-color-primary')
  html.style.removeProperty('--el-text-color-regular')
  html.style.removeProperty('--el-text-color-secondary')
  html.style.removeProperty('--el-border-color')
  html.style.removeProperty('--el-border-color-light')
  html.style.removeProperty('--el-border-color-lighter')
  html.style.removeProperty('--el-fill-color')
  html.style.removeProperty('--el-fill-color-light')
  html.style.removeProperty('--el-fill-color-lighter')
  html.style.removeProperty('--el-fill-color-extra-light')
  html.style.removeProperty('--el-fill-color-dark')
  html.style.removeProperty('--el-fill-color-darker')
  html.style.removeProperty('--el-fill-color-blank')
}

/**
 * 获取当前主题状态（仅用于管理后台）
 */
function getThemeState(): boolean {
  if (typeof window === 'undefined') return false
  const savedTheme = localStorage.getItem('admin_theme')
  return savedTheme === 'dark' || 
    (savedTheme === null && window.matchMedia('(prefers-color-scheme: dark)').matches)
}

/**
 * 应用深色模式主题
 */
function applyDarkTheme() {
  if (typeof document === 'undefined') return
  const html = document.documentElement
  html.classList.add('dark')
  applyElementPlusDarkTheme()
}

/**
 * 应用浅色模式主题
 */
function applyLightTheme() {
  if (typeof document === 'undefined') return
  const html = document.documentElement
  html.classList.remove('dark')
  removeElementPlusDarkTheme()
}

// 立即初始化深色/浅色模式（在应用启动前）
// 前台固定为深色模式；后台根据用户偏好
if (typeof window !== 'undefined') {
  const path = window.location.pathname
  if (path.startsWith('/admin')) {
    const isDark = getThemeState()
    if (isDark) {
      applyDarkTheme()
    } else {
      applyLightTheme()
    }
  } else {
    // 前台始终使用深色模式
    applyDarkTheme()
  }
}

const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...frontendRoutes,
    ...adminRoutes,
    {
      path: '/:pathMatch(.*)*',
      name: 'NotFound',
      component: () => import('./frontend/pages/NotFoundPage.vue')
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
  // 确保主题状态正确应用（每次路由切换时检查）
  // 前台固定深色，后台根据用户偏好
  const html = document.documentElement
  const isAdminRoute = to.path.startsWith('/admin')
  const hasDarkClass = html.classList.contains('dark')

  if (isAdminRoute) {
    const isDark = getThemeState()
    if (isDark && !hasDarkClass) {
      applyDarkTheme()
    } else if (!isDark && hasDarkClass) {
      applyLightTheme()
    }
  } else {
    // 前台路由：始终保持深色模式
    if (!hasDarkClass) {
      applyDarkTheme()
    }
  }
  
  const token = localStorage.getItem('admin_token')
  
  // 检查是否需要认证
  if (to.meta.requiresAuth) {
    if (!token) {
      // 未登录，重定向到登录页，并保存原始路径
      next({
        path: '/admin/login',
        query: { redirect: to.fullPath }
      })
      return
    }
    
    // 有token但需要验证有效性（仅在进入管理后台时验证）
    if (to.path.startsWith('/admin') && to.path !== '/admin/login') {
      try {
        // 验证token有效性
        await authAPI.verify()
      } catch (error) {
        // token无效，清除并重定向到登录页
        localStorage.removeItem('admin_token')
        next({
          path: '/admin/login',
          query: { redirect: to.fullPath }
        })
        return
      }
    }
  }
  
  // 如果已登录用户访问登录页，重定向到管理后台
  if (to.path === '/admin/login' && token) {
    next('/admin')
    return
  }
  
  next()
})

// 路由错误处理
router.onError((error) => {
  console.error('路由错误:', error)
  
  // 处理代码分割加载错误
  if (error.name === 'ChunkLoadError') {
    // 刷新页面重新加载资源
    window.location.reload()
  }
})

const app = createApp(App)

// 全局错误处理
app.config.errorHandler = (err, instance, info) => {
  console.error('Vue错误:', err, info)
  
  // 这里可以集成错误监控服务
  // errorReportingService.captureException(err, { extra: { info } })
}

// 全局警告处理（开发环境）
if (process.env.NODE_ENV === 'development') {
  app.config.warnHandler = (msg, instance, trace) => {
    console.warn('Vue警告:', msg, trace)
  }
}

app.use(router)
app.use(ElementPlus)

// 设置全局错误处理器
setupGlobalErrorHandler()

app.mount('#app')