<template>
  <el-dialog
    v-model="visible"
    title="产品信息"
    width="500px"
    @close="handleClose"
  >
    <div v-if="product" class="product-info-modal">
      <!-- 产品基本信息 -->
      <div class="info-section">
        <div class="section-header">
          <h3>基本信息</h3>
        </div>
        <div class="info-grid">
          <div class="info-item">
            <span class="label">产品名称:</span>
            <span class="value">{{ product.title }}</span>
          </div>
          <div class="info-item">
            <span class="label">产品类型:</span>
            <el-tag :type="getTypeTagType(product.product_type)" size="small">
              {{ getTypeLabel(product.product_type) }}
            </el-tag>
          </div>
          <div class="info-item">
            <span class="label">版本号:</span>
            <span class="value">v{{ product.version }}</span>
          </div>
          <div class="info-item">
            <span class="label">访问次数:</span>
            <span class="value">{{ product.view_count || 0 }} 次</span>
          </div>
        </div>
      </div>
      
      <!-- 产品描述 -->
      <div v-if="product.description" class="info-section">
        <div class="section-header">
          <h3>产品描述</h3>
        </div>
        <p class="description">{{ product.description }}</p>
      </div>
      
      <!-- 技术栈 -->
      <div v-if="product.tech_stack?.length" class="info-section">
        <div class="section-header">
          <h3>技术栈</h3>
        </div>
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
        <div class="section-header">
          <h3>相关链接</h3>
        </div>
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
      
      <!-- 使用说明 -->
      <div class="info-section">
        <div class="section-header">
          <h3>使用说明</h3>
        </div>
        <div class="usage-tips">
          <ul>
            <li>点击刷新按钮可以重新加载产品</li>
            <li>点击全屏按钮可以全屏体验产品</li>
            <li>产品在安全的沙箱环境中运行</li>
            <li>您的使用数据将用于改进产品体验</li>
          </ul>
        </div>
      </div>
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
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { Link, Share } from '@element-plus/icons-vue'
import type { Product } from '../../shared/types'

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

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
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
  
  const shareData = {
    title: props.product.title,
    text: props.product.description || '来体验这个有趣的产品！',
    url: window.location.href
  }
  
  try {
    if (navigator.share) {
      await navigator.share(shareData)
      ElMessage.success('分享成功')
    } else {
      // 降级到复制链接
      await navigator.clipboard.writeText(window.location.href)
      ElMessage.success('链接已复制到剪贴板')
    }
  } catch (error) {
    console.error('分享失败:', error)
    ElMessage.error('分享失败')
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

.info-section {
  margin-bottom: 24px;
}

.info-section:last-child {
  margin-bottom: 0;
}

.section-header {
  margin-bottom: 16px;
}

.section-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 16px;
}

.info-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.label {
  font-size: 14px;
  color: #6b7280;
  min-width: 80px;
}

.value {
  font-size: 14px;
  color: #1f2937;
  font-weight: 500;
}

.description {
  font-size: 14px;
  color: #374151;
  line-height: 1.6;
  margin: 0;
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

.usage-tips ul {
  margin: 0;
  padding-left: 20px;
  font-size: 14px;
  color: #6b7280;
  line-height: 1.6;
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

/* 响应式设计 */
@media (max-width: 768px) {
  .el-dialog {
    width: 95% !important;
    margin: 5vh auto;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
  
  .links {
    flex-direction: column;
    align-items: stretch;
  }
}
</style>