import { ref, watch } from 'vue'

/**
 * 管理后台深色模式
 * 立即初始化，不等待组件挂载
 */
export function useDarkMode() {
  // 立即从localStorage读取，不等待组件挂载
  const getInitialTheme = (): boolean => {
    if (typeof window === 'undefined') return false
    
    const savedTheme = localStorage.getItem('admin_theme')
    if (savedTheme === 'dark') {
      return true
    } else if (savedTheme === 'light') {
      return false
    } else {
      // 如果没有保存的主题，使用系统偏好
      const prefersDark = window.matchMedia('(prefers-color-scheme: dark)').matches
      return prefersDark
    }
  }

  const isDark = ref(getInitialTheme())

  // 立即应用主题（不等待组件挂载）
  updateElementPlusTheme(isDark.value)

  // 监听变化并保存到localStorage
  watch(isDark, (dark) => {
    localStorage.setItem('admin_theme', dark ? 'dark' : 'light')
    // 更新Element Plus主题
    updateElementPlusTheme(dark)
  }, { immediate: true })

  const toggle = () => {
    isDark.value = !isDark.value
  }

  return {
    isDark,
    toggle,
  }
}

/**
 * 更新Element Plus主题 - 使用实验室色彩
 */
function updateElementPlusTheme(isDark: boolean) {
  if (typeof document === 'undefined') return
  
  const html = document.documentElement
  if (isDark) {
    html.classList.add('dark')
    // 设置Element Plus的CSS变量 - 实验室显示器光晕色彩
    html.style.setProperty('--el-bg-color', '#1e293b') // Slate 800
    html.style.setProperty('--el-bg-color-page', '#0f172a') // Slate 950
    html.style.setProperty('--el-text-color-primary', '#f3f4f6') // Gray 50
    html.style.setProperty('--el-text-color-regular', '#d1d5db') // Gray 300
    html.style.setProperty('--el-text-color-secondary', '#9ca3af') // Gray 400
    html.style.setProperty('--el-border-color', 'rgba(148, 163, 184, 0.15)') // Slate 400 15%
    html.style.setProperty('--el-border-color-light', 'rgba(148, 163, 184, 0.2)') // Slate 400 20%
    html.style.setProperty('--el-border-color-lighter', 'rgba(148, 163, 184, 0.25)') // Slate 400 25%
    html.style.setProperty('--el-fill-color', '#334155') // Slate 700
    html.style.setProperty('--el-fill-color-light', '#475569') // Slate 600
    html.style.setProperty('--el-fill-color-lighter', '#64748b') // Slate 500
    html.style.setProperty('--el-fill-color-extra-light', '#94a3b8') // Slate 400
    html.style.setProperty('--el-fill-color-dark', '#1e293b') // Slate 800
    html.style.setProperty('--el-fill-color-darker', '#0f172a') // Slate 950
    html.style.setProperty('--el-fill-color-blank', 'transparent')
  } else {
    html.classList.remove('dark')
    // 重置为默认值
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
}

