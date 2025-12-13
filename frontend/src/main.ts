import { createApp } from 'vue'
import { createRouter, createWebHistory } from 'vue-router'
import ElementPlus from 'element-plus'
import 'element-plus/dist/index.css'
import './style.css'

import App from './App.vue'
import { frontendRoutes } from './frontend/router'
import { adminRoutes } from './admin/router'
import { setupGlobalErrorHandler } from './shared/composables/useErrorHandler'
import { authAPI } from './shared/api'

const router = createRouter({
  history: createWebHistory(),
  routes: [
    ...frontendRoutes,
    ...adminRoutes,
    {
      path: '/:pathMatch(.*)*',
      redirect: '/'
    }
  ]
})

// 路由守卫
router.beforeEach(async (to, from, next) => {
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