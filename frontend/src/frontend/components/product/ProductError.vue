<template>
  <div class="product-error">
    <div class="error-content">
      <!-- 错误图标 -->
      <div class="error-icon">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
        </svg>
      </div>
      
      <!-- 错误信息 -->
      <div class="error-info">
        <h3 class="error-title">{{ errorTitle }}</h3>
        <p class="error-message">{{ error }}</p>
        
        <!-- 错误详情 -->
        <div v-if="showDetails && errorDetails" class="error-details">
          <button @click="toggleDetails" class="details-toggle">
            <span>{{ showDetailsExpanded ? '隐藏' : '显示' }}详细信息</span>
            <svg 
              :class="{ 'rotate-180': showDetailsExpanded }" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
            </svg>
          </button>
          
          <div v-if="showDetailsExpanded" class="details-content">
            <pre>{{ errorDetails }}</pre>
          </div>
        </div>
        
        <!-- 建议解决方案 -->
        <div v-if="suggestions.length > 0" class="error-suggestions">
          <h4>建议解决方案:</h4>
          <ul>
            <li v-for="(suggestion, index) in suggestions" :key="index">
              {{ suggestion }}
            </li>
          </ul>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="error-actions">
        <button @click="$emit('retry')" class="btn btn-primary" :disabled="isRetrying">
          <svg v-if="isRetrying" class="btn-icon animate-spin" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          <svg v-else class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
          </svg>
          {{ isRetrying ? '重试中...' : '重试' }}
        </button>
        
        <button @click="$emit('go-back')" class="btn btn-secondary">
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M10 19l-7-7m0 0l7-7m-7 7h18" />
          </svg>
          返回
        </button>
        
        <button @click="reportError" class="btn btn-outline">
          <svg class="btn-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                  d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
          </svg>
          报告问题
        </button>
      </div>
      
      <!-- 帮助链接 -->
      <div class="error-help">
        <p>如果问题持续存在，请联系技术支持</p>
        <div class="help-links">
          <a href="mailto:support@august.lab" class="help-link">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
            </svg>
            邮件支持
          </a>
          
          <a href="/help" class="help-link" target="_blank">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M8.228 9c.549-1.165 2.03-2 3.772-2 2.21 0 4 1.343 4 3 0 1.4-1.278 2.575-3.006 2.907-.542.104-.994.54-.994 1.093m0 3h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            帮助中心
          </a>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'

interface Props {
  error: string
  errorDetails?: string
  errorCode?: string
  showDetails?: boolean
  isRetrying?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  showDetails: true,
  isRetrying: false
})

const emit = defineEmits<{
  'retry': []
  'go-back': []
}>()

// 响应式数据
const showDetailsExpanded = ref(false)

// 计算属性
const errorTitle = computed(() => {
  const errorMap: Record<string, string> = {
    'NETWORK_ERROR': '网络连接错误',
    'FILE_NOT_FOUND': '产品文件未找到',
    'LOAD_TIMEOUT': '加载超时',
    'PERMISSION_DENIED': '权限不足',
    'INVALID_PRODUCT': '产品无效',
    'SERVER_ERROR': '服务器错误'
  }
  
  return errorMap[props.errorCode || ''] || '产品加载失败'
})

const suggestions = computed(() => {
  const suggestionMap: Record<string, string[]> = {
    'NETWORK_ERROR': [
      '检查网络连接是否正常',
      '尝试刷新页面',
      '稍后再试'
    ],
    'FILE_NOT_FOUND': [
      '产品文件可能已被移动或删除',
      '联系管理员检查产品状态',
      '尝试访问其他产品'
    ],
    'LOAD_TIMEOUT': [
      '检查网络连接速度',
      '尝试重新加载',
      '清除浏览器缓存'
    ],
    'PERMISSION_DENIED': [
      '产品可能需要特殊权限',
      '联系管理员获取访问权限',
      '检查登录状态'
    ],
    'INVALID_PRODUCT': [
      '产品配置可能有误',
      '联系开发者修复问题',
      '尝试访问其他产品'
    ],
    'SERVER_ERROR': [
      '服务器暂时不可用',
      '稍后再试',
      '联系技术支持'
    ]
  }
  
  return suggestionMap[props.errorCode || ''] || [
    '尝试刷新页面',
    '检查网络连接',
    '联系技术支持'
  ]
})

// 方法
const toggleDetails = () => {
  showDetailsExpanded.value = !showDetailsExpanded.value
}

const reportError = () => {
  const errorInfo = {
    error: props.error,
    errorCode: props.errorCode,
    errorDetails: props.errorDetails,
    userAgent: navigator.userAgent,
    url: window.location.href,
    timestamp: new Date().toISOString()
  }
  
  const subject = `产品错误报告: ${props.errorCode || 'UNKNOWN'}`
  const body = `错误信息: ${props.error}\n\n错误详情:\n${JSON.stringify(errorInfo, null, 2)}`
  const mailtoUrl = `mailto:support@august.lab?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`
  
  window.open(mailtoUrl)
  ElMessage.success('已打开邮件客户端，请发送错误报告')
}
</script>

<style scoped>
.product-error {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
  background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
}

.error-content {
  text-align: center;
  max-width: 600px;
  width: 100%;
  background: white;
  border-radius: 1rem;
  padding: 2rem;
  box-shadow: 0 10px 25px rgba(0, 0, 0, 0.1);
}

.error-icon {
  width: 4rem;
  height: 4rem;
  margin: 0 auto 1.5rem;
  color: #dc2626;
}

.error-icon svg {
  width: 100%;
  height: 100%;
}

.error-info {
  margin-bottom: 2rem;
}

.error-title {
  font-size: 1.5rem;
  font-weight: 600;
  color: #dc2626;
  margin-bottom: 0.5rem;
}

.error-message {
  font-size: 1rem;
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.error-details {
  margin-top: 1rem;
  text-align: left;
}

.details-toggle {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  background: none;
  border: none;
  color: #3b82f6;
  cursor: pointer;
  font-size: 0.875rem;
  padding: 0.5rem 0;
  transition: color 0.2s;
}

.details-toggle:hover {
  color: #2563eb;
}

.details-toggle svg {
  width: 1rem;
  height: 1rem;
  transition: transform 0.2s;
}

.rotate-180 {
  transform: rotate(180deg);
}

.details-content {
  margin-top: 0.5rem;
  padding: 1rem;
  background: #f9fafb;
  border-radius: 0.5rem;
  border: 1px solid #e5e7eb;
}

.details-content pre {
  font-size: 0.75rem;
  color: #374151;
  white-space: pre-wrap;
  word-break: break-word;
  margin: 0;
}

.error-suggestions {
  margin-top: 1rem;
  text-align: left;
}

.error-suggestions h4 {
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
  margin-bottom: 0.5rem;
}

.error-suggestions ul {
  list-style: none;
  padding: 0;
  margin: 0;
}

.error-suggestions li {
  padding: 0.25rem 0;
  color: #6b7280;
  font-size: 0.875rem;
  position: relative;
  padding-left: 1.5rem;
}

.error-suggestions li::before {
  content: '•';
  color: #3b82f6;
  position: absolute;
  left: 0;
  font-weight: bold;
}

.error-actions {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
  margin-bottom: 1.5rem;
}

.btn {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
  border: none;
  font-size: 0.875rem;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.btn-icon {
  width: 1rem;
  height: 1rem;
}

.btn-primary {
  background: #3b82f6;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #2563eb;
}

.btn-secondary {
  background: #6b7280;
  color: white;
}

.btn-secondary:hover {
  background: #4b5563;
}

.btn-outline {
  background: transparent;
  color: #6b7280;
  border: 1px solid #d1d5db;
}

.btn-outline:hover {
  background: #f9fafb;
  border-color: #9ca3af;
}

.animate-spin {
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-help {
  border-top: 1px solid #e5e7eb;
  padding-top: 1rem;
  color: #6b7280;
  font-size: 0.875rem;
}

.error-help p {
  margin-bottom: 0.75rem;
}

.help-links {
  display: flex;
  gap: 1rem;
  justify-content: center;
  flex-wrap: wrap;
}

.help-link {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: #3b82f6;
  text-decoration: none;
  padding: 0.5rem;
  border-radius: 0.375rem;
  transition: all 0.2s;
}

.help-link:hover {
  background: #eff6ff;
  color: #2563eb;
}

.help-link svg {
  width: 1rem;
  height: 1rem;
}

/* 响应式设计 */
@media (max-width: 640px) {
  .product-error {
    padding: 1rem;
  }
  
  .error-content {
    padding: 1.5rem;
  }
  
  .error-icon {
    width: 3rem;
    height: 3rem;
  }
  
  .error-title {
    font-size: 1.25rem;
  }
  
  .error-actions {
    flex-direction: column;
    align-items: stretch;
  }
  
  .btn {
    justify-content: center;
  }
  
  .help-links {
    flex-direction: column;
    align-items: center;
  }
}
</style>