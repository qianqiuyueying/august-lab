<template>
  <div class="product-navbar" :class="{ 'navbar-fullscreen': isFullscreen }">
    <div class="navbar-content">
      <!-- 左侧产品信息 -->
      <div class="navbar-left">
        <div class="product-info">
          <div class="product-icon">
            <el-icon size="20"><Box /></el-icon>
          </div>
          <div class="product-details">
            <h3 class="product-title">{{ product?.title || '产品' }}</h3>
            <span class="product-version">v{{ product?.version || '1.0.0' }}</span>
          </div>
        </div>
      </div>
      
      <!-- 中间控制按钮 -->
      <div class="navbar-center">
        <div class="control-buttons">
          <el-tooltip content="刷新产品" placement="bottom">
            <el-button 
              type="text" 
              @click="handleRefresh"
              :loading="refreshing"
              class="control-btn"
            >
              <el-icon><Refresh /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip :content="isFullscreen ? '退出全屏' : '全屏显示'" placement="bottom">
            <el-button 
              type="text" 
              @click="toggleFullscreen"
              class="control-btn"
            >
              <el-icon>
                <Aim v-if="isFullscreen" />
                <FullScreen v-else />
              </el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="产品信息" placement="bottom">
            <el-button 
              type="text" 
              @click="emit('show-info')"
              class="control-btn"
            >
              <el-icon><InfoFilled /></el-icon>
            </el-button>
          </el-tooltip>
          
          <el-tooltip content="反馈建议" placement="bottom">
            <el-button 
              type="text" 
              @click="emit('show-feedback')"
              class="control-btn"
            >
              <el-icon><ChatDotRound /></el-icon>
            </el-button>
          </el-tooltip>
        </div>
      </div>
      
      <!-- 右侧操作按钮 -->
      <div class="navbar-right">
        <div class="action-buttons">
          <el-tooltip content="返回主站" placement="bottom">
            <el-button 
              type="primary" 
              size="small"
              @click="goBack"
              class="back-btn"
            >
              <el-icon><ArrowLeft /></el-icon>
              <span>返回</span>
            </el-button>
          </el-tooltip>
        </div>
      </div>
    </div>
    

  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  Box,
  Refresh,
  FullScreen,
  Aim,
  InfoFilled,
  ArrowLeft,
  ChatDotRound
} from '@element-plus/icons-vue'

import type { Product } from '../../../shared/types'

interface Props {
  product?: Product | null
  isFullscreen?: boolean
}

interface Emits {
  (e: 'reload'): void
  (e: 'toggle-fullscreen'): void
  (e: 'go-back'): void
  (e: 'show-info'): void
  (e: 'show-feedback'): void
}

const props = withDefaults(defineProps<Props>(), {
  isFullscreen: false
})

const emit = defineEmits<Emits>()
const router = useRouter()

// 响应式数据
const refreshing = ref(false)

// 方法
const handleRefresh = async () => {
  refreshing.value = true
  try {
    emit('reload')
    ElMessage.success('产品已刷新')
  } catch (error) {
    ElMessage.error('刷新失败')
  } finally {
    setTimeout(() => {
      refreshing.value = false
    }, 500)
  }
}

const toggleFullscreen = () => {
  emit('toggle-fullscreen')
}

const goBack = () => {
  emit('go-back')
  // 尝试使用浏览器后退功能，如果没有历史记录则返回到产品列表页面
  if (window.history.length > 1) {
    router.go(-1)
  } else {
    router.push('/products')
  }
}
</script>

<style scoped>
.product-navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 60px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid #e5e7eb;
  z-index: 1000;
  transition: all 0.3s ease;
}

.navbar-fullscreen {
  background: rgba(0, 0, 0, 0.8);
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.navbar-fullscreen .product-title {
  color: white;
}

.navbar-fullscreen .product-version {
  color: rgba(255, 255, 255, 0.7);
}

.navbar-fullscreen .control-btn {
  color: white;
}

.navbar-fullscreen .control-btn:hover {
  background: rgba(255, 255, 255, 0.1);
}

.navbar-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  padding: 0 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.navbar-left {
  flex: 1;
  display: flex;
  align-items: center;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-icon {
  width: 40px;
  height: 40px;
  background: #f3f4f6;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
}

.navbar-fullscreen .product-icon {
  background: rgba(255, 255, 255, 0.1);
  color: white;
}

.product-details {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.product-title {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
  line-height: 1.2;
}

.product-version {
  font-size: 12px;
  color: #6b7280;
  line-height: 1;
}

.navbar-center {
  flex: 0 0 auto;
  display: flex;
  justify-content: center;
}

.control-buttons {
  display: flex;
  align-items: center;
  gap: 8px;
}

.control-btn {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: all 0.2s ease;
}

.control-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.navbar-right {
  flex: 1;
  display: flex;
  justify-content: flex-end;
}

.action-buttons {
  display: flex;
  align-items: center;
  gap: 12px;
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 16px;
  border-radius: 6px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .navbar-content {
    padding: 0 16px;
  }
  
  .product-details {
    display: none;
  }
  
  .control-buttons {
    gap: 4px;
  }
  
  .control-btn {
    width: 36px;
    height: 36px;
  }
  
  .back-btn span {
    display: none;
  }
}

@media (max-width: 480px) {
  .navbar-content {
    padding: 0 12px;
  }
  
  .product-info {
    gap: 8px;
  }
  
  .product-icon {
    width: 32px;
    height: 32px;
  }
  
  .control-btn {
    width: 32px;
    height: 32px;
  }
}
</style>