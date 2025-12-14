<template>
  <el-dialog
    v-model="visible"
    title="产品信息"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="product" class="product-info-modal">
      <el-tabs v-model="activeTab" class="product-tabs">
        <!-- 基本信息标签页 -->
        <el-tab-pane label="基本信息" name="basic">
          <div class="tab-content">
            <!-- 产品基本信息 -->
            <div class="info-section">
              <div class="info-grid">
                <div class="info-item">
                  <span class="label">产品名称</span>
                  <span class="value">{{ product.title }}</span>
                </div>
                <div class="info-item">
                  <span class="label">产品类型</span>
                  <el-tag :type="getTypeTagType(product.product_type)" size="small">
                    {{ getTypeLabel(product.product_type) }}
                  </el-tag>
                </div>
                <div class="info-item">
                  <span class="label">版本号</span>
                  <span class="value">v{{ product.version }}</span>
                </div>
                <div class="info-item">
                  <span class="label">访问次数</span>
                  <span class="value">{{ product.view_count || 0 }} 次</span>
                </div>
              </div>
            </div>
            
            <!-- 产品描述 -->
            <div v-if="product.description" class="info-section">
              <h4 class="section-title">产品描述</h4>
              <p class="description">{{ product.description }}</p>
            </div>
            
            <!-- 技术栈 -->
            <div v-if="product.tech_stack?.length" class="info-section">
              <h4 class="section-title">技术栈</h4>
              <div class="tech-stack">
                <el-tag
                  v-for="tech in product.tech_stack"
                  :key="tech"
                  size="small"
                  class="tech-tag"
                >
                  {{ tech }}
                </el-tag>
              </div>
            </div>
            
            <!-- 外部链接 -->
            <div v-if="product.project_url || product.github_url" class="info-section">
              <h4 class="section-title">相关链接</h4>
              <div class="links">
                <el-button
                  v-if="product.project_url"
                  type="primary"
                  size="small"
                  @click="openLink(product.project_url)"
                >
                  <el-icon><Link /></el-icon>
                  <span>项目主页</span>
                </el-button>
                <el-button
                  v-if="product.github_url"
                  size="small"
                  @click="openLink(product.github_url)"
                >
                  <el-icon><Link /></el-icon>
                  <span>源码仓库</span>
                </el-button>
              </div>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 使用说明标签页 -->
        <el-tab-pane label="使用说明" name="usage">
          <div class="tab-content">
            <div class="usage-tips">
              <ul>
                <li>点击刷新按钮可以重新加载产品</li>
                <li>点击全屏按钮可以全屏体验产品</li>
                <li>产品在安全的沙箱环境中运行</li>
                <li>您的使用数据将用于改进产品体验</li>
              </ul>
            </div>
          </div>
        </el-tab-pane>
        
        <!-- 用户反馈标签页 -->
        <el-tab-pane label="用户反馈" name="feedback">
          <div class="tab-content">
            <ProductFeedbackList v-if="product.id" :product-id="product.id" />
            <div v-else class="text-gray-500 text-sm">产品ID无效</div>
          </div>
        </el-tab-pane>
      </el-tabs>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button type="primary" @click="shareProduct">
          <el-icon><Share /></el-icon>
          分享产品
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Link, Share } from '@element-plus/icons-vue'
import { copyToClipboard } from '../../../shared/utils'
import ProductFeedbackList from './ProductFeedbackList.vue'
import type { Product } from '../../../shared/types'

interface Props {
  modelValue: boolean
  product?: Product | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const visible = ref(false)
const activeTab = ref('basic')

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  // 打开弹窗时重置到第一个标签页
  if (val) {
    activeTab.value = 'basic'
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const handleClose = () => {
  visible.value = false
}

const openLink = (url: string) => {
  window.open(url, '_blank')
}

const shareProduct = async () => {
  if (!props.product) return
  
  const shareUrl = window.location.href
  const shareData = {
    title: props.product.title,
    text: props.product.description || '来体验这个有趣的产品！',
    url: shareUrl
  }
  
  try {
    // 优先使用 Web Share API（如果支持）
    if (navigator.share && navigator.canShare && navigator.canShare(shareData)) {
      await navigator.share(shareData)
      ElMessage.success('分享成功')
      return
    }
    
    // 降级到复制链接到剪贴板
    const success = await copyToClipboard(shareUrl)
    if (success) {
      ElMessage.success('链接已复制到剪贴板')
    } else {
      // 如果复制失败，显示链接让用户手动复制
      ElMessage({
        message: `链接已准备，请手动复制：${shareUrl}`,
        type: 'info',
        duration: 5000,
        showClose: true
      })
    }
  } catch (error: any) {
    // 如果用户取消分享，不显示错误
    if (error.name === 'AbortError') {
      return
    }
    
    console.error('分享失败:', error)
    
    // 尝试降级到复制链接
    try {
      const success = await copyToClipboard(shareUrl)
      if (success) {
        ElMessage.success('链接已复制到剪贴板')
      } else {
        ElMessage.error('分享失败，请手动复制链接')
      }
    } catch (copyError) {
      ElMessage.error('分享失败，请手动复制链接')
    }
  }
}

// 工具方法
const getTypeLabel = (type: string) => {
  const labels = {
    web_app: 'Web应用',
    game: '游戏',
    tool: '工具',
    demo: '演示'
  }
  return labels[type as keyof typeof labels] || type
}

const getTypeTagType = (type: string) => {
  const types = {
    web_app: 'primary',
    game: 'danger',
    tool: 'success',
    demo: 'warning'
  }
  return types[type as keyof typeof types] || 'info'
}
</script>

<style scoped>
.product-info-modal {
  padding: 0;
}

.product-tabs {
  min-height: 400px;
}

.tab-content {
  padding: 8px 0;
  max-height: 500px;
  overflow-y: auto;
}

.info-section {
  margin-bottom: 20px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.info-section:last-child {
  margin-bottom: 0;
  padding-bottom: 0;
  border-bottom: none;
}

.section-title {
  margin: 0 0 12px 0;
  font-size: 15px;
  font-weight: 600;
  color: #1f2937;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px 24px;
}

.info-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.label {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.description {
  font-size: 14px;
  color: #4b5563;
  line-height: 1.7;
  margin: 0;
  padding: 12px;
  background: #f9fafb;
  border-radius: 6px;
  border-left: 3px solid #3b82f6;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.tech-tag {
  margin: 0;
}

.links {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.usage-tips {
  padding: 8px 0;
}

.usage-tips ul {
  margin: 0;
  padding-left: 24px;
  font-size: 14px;
  color: #4b5563;
  line-height: 2;
  list-style-type: disc;
}

.usage-tips li {
  margin-bottom: 8px;
}

.usage-tips li:last-child {
  margin-bottom: 0;
}

.dialog-footer {
  text-align: right;
}

/* 标签页样式优化 */
:deep(.el-tabs__header) {
  margin-bottom: 20px;
}

:deep(.el-tabs__item) {
  font-weight: 500;
  padding: 0 20px;
}

:deep(.el-tabs__content) {
  padding: 0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .el-dialog {
    width: 95% !important;
    margin: 5vh auto;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  
  .links {
    flex-direction: column;
    align-items: stretch;
  }
  
  .tab-content {
    max-height: 400px;
  }
}
</style>