import { ref, watch } from 'vue'

const isDark = ref(false)
const initialized = ref(false)

/**
 * 管理后台深色模式 - Singleton
 */
export function useDarkMode() {
  // 初始化逻辑 (仅执行一次)
  if (!initialized.value) {
    if (typeof window !== 'undefined') {
      const savedTheme = localStorage.getItem('admin_theme')
      if (savedTheme === 'dark') {
        isDark.value = true
      } else if (savedTheme === 'light') {
        isDark.value = false
      } else {
        isDark.value = window.matchMedia('(prefers-color-scheme: dark)').matches
      }
      
      initialized.value = true
      updateElementPlusTheme(isDark.value)
    }
  }

  // 监听变化并保存到localStorage
  watch(isDark, (dark) => {
    if (typeof window !== 'undefined') {
      localStorage.setItem('admin_theme', dark ? 'dark' : 'light')
      updateElementPlusTheme(dark)
    }
  })

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
    html.style.setProperty('--el-bg-color', '#050505') // Lab BG
    html.style.setProperty('--el-bg-color-page', '#050505') // Lab BG
    html.style.setProperty('--el-bg-color-overlay', '#121212') // Lab Surface
    
    html.style.setProperty('--el-text-color-primary', '#E1E1E1') // Lab Text
    html.style.setProperty('--el-text-color-regular', '#a1a1aa')
    html.style.setProperty('--el-text-color-secondary', '#888888') // Lab Muted
    
    html.style.setProperty('--el-border-color', '#2A2A2A') // Lab Border
    html.style.setProperty('--el-border-color-light', '#333333')
    html.style.setProperty('--el-border-color-lighter', '#404040')
    html.style.setProperty('--el-border-color-extra-light', '#525252')
    
    html.style.setProperty('--el-fill-color', '#121212') // Lab Surface
    html.style.setProperty('--el-fill-color-light', '#1a1a1a')
    html.style.setProperty('--el-fill-color-lighter', '#262626')
    html.style.setProperty('--el-fill-color-extra-light', '#333333')
    html.style.setProperty('--el-fill-color-dark', '#050505') // Lab BG
    html.style.setProperty('--el-fill-color-darker', '#000000')
    html.style.setProperty('--el-fill-color-blank', 'transparent')

    // 修复输入框背景
    html.style.setProperty('--el-input-bg-color', '#121212')
    html.style.setProperty('--el-input-text-color', '#E1E1E1')
    html.style.setProperty('--el-input-border-color', '#2A2A2A')
    
  } else {
    html.classList.remove('dark')
    // 重置为默认值
    html.style.removeProperty('--el-bg-color')
    html.style.removeProperty('--el-bg-color-page')
    html.style.removeProperty('--el-bg-color-overlay')
    html.style.removeProperty('--el-text-color-primary')
    html.style.removeProperty('--el-text-color-regular')
    html.style.removeProperty('--el-text-color-secondary')
    html.style.removeProperty('--el-border-color')
    html.style.removeProperty('--el-border-color-light')
    html.style.removeProperty('--el-border-color-lighter')
    html.style.removeProperty('--el-border-color-extra-light')
    html.style.removeProperty('--el-fill-color')
    html.style.removeProperty('--el-fill-color-light')
    html.style.removeProperty('--el-fill-color-lighter')
    html.style.removeProperty('--el-fill-color-extra-light')
    html.style.removeProperty('--el-fill-color-dark')
    html.style.removeProperty('--el-fill-color-darker')
    html.style.removeProperty('--el-fill-color-blank')
    html.style.removeProperty('--el-input-bg-color')
    html.style.removeProperty('--el-input-text-color')
    html.style.removeProperty('--el-input-border-color')
  }
}

