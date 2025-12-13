<template>
  <div class="product-loader">
    <div class="loader-content">
      <!-- 加载动画 -->
      <div class="loader-animation">
        <div class="loader-spinner">
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
          <div class="spinner-ring"></div>
        </div>
      </div>
      
      <!-- 加载信息 -->
      <div class="loader-info">
        <h3 class="loader-title">{{ message || '正在加载产品...' }}</h3>
        <p class="loader-description">{{ description }}</p>
        
        <!-- 进度条 -->
        <div v-if="showProgress" class="progress-container">
          <div class="progress-bar">
            <div 
              class="progress-fill" 
              :style="{ width: `${progress}%` }"
            ></div>
          </div>
          <span class="progress-text">{{ progress }}%</span>
        </div>
        
        <!-- 加载步骤 -->
        <div v-if="steps.length > 0" class="loading-steps">
          <div 
            v-for="(step, index) in steps" 
            :key="index"
            class="loading-step"
            :class="{
              'step--completed': index < currentStep,
              'step--active': index === currentStep,
              'step--pending': index > currentStep
            }"
          >
            <div class="step-icon">
              <svg v-if="index < currentStep" fill="currentColor" viewBox="0 0 20 20">
                <path fill-rule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clip-rule="evenodd" />
              </svg>
              <div v-else-if="index === currentStep" class="step-spinner"></div>
              <div v-else class="step-dot"></div>
            </div>
            <span class="step-text">{{ step }}</span>
          </div>
        </div>
        
        <!-- 提示信息 -->
        <div v-if="tips.length > 0" class="loader-tips">
          <div class="tip-item" :key="currentTip">
            <svg class="tip-icon" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                    d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            <span>{{ tips[currentTip] }}</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'

interface Props {
  message?: string
  description?: string
  progress?: number
  showProgress?: boolean
  steps?: string[]
  currentStep?: number
  tips?: string[]
}

const props = withDefaults(defineProps<Props>(), {
  message: '正在加载产品...',
  description: '请稍候，我们正在为您准备产品体验',
  progress: 0,
  showProgress: false,
  steps: () => [],
  currentStep: 0,
  tips: () => [
    '产品采用沙箱技术，确保安全隔离',
    '支持全屏模式，获得更好的体验',
    '使用 ESC 键可以快速退出全屏',
    '点击导航栏可以返回主站',
    '产品加载可能需要几秒钟时间'
  ]
})

// 响应式数据
const currentTip = ref(0)
let tipInterval: number | null = null

// 计算属性
const defaultSteps = computed(() => {
  if (props.steps.length > 0) return props.steps
  
  return [
    '验证产品信息',
    '加载产品文件',
    '初始化运行环境',
    '启动产品应用'
  ]
})

// 方法
const startTipRotation = () => {
  if (props.tips.length <= 1) return
  
  tipInterval = window.setInterval(() => {
    currentTip.value = (currentTip.value + 1) % props.tips.length
  }, 3000)
}

const stopTipRotation = () => {
  if (tipInterval) {
    clearInterval(tipInterval)
    tipInterval = null
  }
}

// 生命周期
onMounted(() => {
  startTipRotation()
})

onUnmounted(() => {
  stopTipRotation()
})
</script>

<style scoped>
.product-loader {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 400px;
  padding: 2rem;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

.loader-content {
  text-align: center;
  max-width: 500px;
  width: 100%;
}

.loader-animation {
  margin-bottom: 2rem;
}

.loader-spinner {
  position: relative;
  width: 80px;
  height: 80px;
  margin: 0 auto;
}

.spinner-ring {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  border: 3px solid transparent;
  border-top: 3px solid rgba(255, 255, 255, 0.8);
  border-radius: 50%;
  animation: spin 1.5s linear infinite;
}

.spinner-ring:nth-child(2) {
  width: 60px;
  height: 60px;
  top: 10px;
  left: 10px;
  animation-duration: 1.2s;
  animation-direction: reverse;
}

.spinner-ring:nth-child(3) {
  width: 40px;
  height: 40px;
  top: 20px;
  left: 20px;
  animation-duration: 0.9s;
}

@keyframes spin {
  0% {
    transform: rotate(0deg);
  }
  100% {
    transform: rotate(360deg);
  }
}

.loader-info {
  space-y: 1rem;
}

.loader-title {
  font-size: 1.5rem;
  font-weight: 600;
  margin-bottom: 0.5rem;
  color: white;
}

.loader-description {
  font-size: 1rem;
  opacity: 0.9;
  margin-bottom: 1.5rem;
  line-height: 1.5;
}

.progress-container {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.progress-bar {
  flex: 1;
  height: 8px;
  background: rgba(255, 255, 255, 0.2);
  border-radius: 4px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981, #34d399);
  border-radius: 4px;
  transition: width 0.3s ease;
}

.progress-text {
  font-size: 0.875rem;
  font-weight: 500;
  min-width: 3rem;
  text-align: right;
}

.loading-steps {
  margin-bottom: 1.5rem;
}

.loading-step {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.5rem 0;
  font-size: 0.875rem;
}

.step-icon {
  width: 1.5rem;
  height: 1.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 50%;
  flex-shrink: 0;
}

.step--completed .step-icon {
  background: #10b981;
  color: white;
}

.step--completed .step-icon svg {
  width: 1rem;
  height: 1rem;
}

.step--active .step-icon {
  background: rgba(255, 255, 255, 0.2);
}

.step-spinner {
  width: 1rem;
  height: 1rem;
  border: 2px solid transparent;
  border-top: 2px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

.step--pending .step-icon {
  background: rgba(255, 255, 255, 0.1);
}

.step-dot {
  width: 0.5rem;
  height: 0.5rem;
  background: rgba(255, 255, 255, 0.5);
  border-radius: 50%;
}

.step-text {
  opacity: 0.9;
}

.step--completed .step-text {
  opacity: 0.7;
}

.step--active .step-text {
  font-weight: 500;
  opacity: 1;
}

.step--pending .step-text {
  opacity: 0.6;
}

.loader-tips {
  margin-top: 1.5rem;
  padding: 1rem;
  background: rgba(255, 255, 255, 0.1);
  border-radius: 0.5rem;
  backdrop-filter: blur(10px);
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.875rem;
  opacity: 0.9;
  animation: fadeIn 0.5s ease-in-out;
}

.tip-icon {
  width: 1rem;
  height: 1rem;
  flex-shrink: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 0.9;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 640px) {
  .product-loader {
    padding: 1.5rem;
    min-height: 300px;
  }
  
  .loader-spinner {
    width: 60px;
    height: 60px;
  }
  
  .spinner-ring:nth-child(2) {
    width: 45px;
    height: 45px;
    top: 7.5px;
    left: 7.5px;
  }
  
  .spinner-ring:nth-child(3) {
    width: 30px;
    height: 30px;
    top: 15px;
    left: 15px;
  }
  
  .loader-title {
    font-size: 1.25rem;
  }
  
  .loader-description {
    font-size: 0.875rem;
  }
  
  .loading-step {
    font-size: 0.8125rem;
  }
}

/* 暗色主题适配 */
@media (prefers-color-scheme: dark) {
  .product-loader {
    background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
  }
}
</style>