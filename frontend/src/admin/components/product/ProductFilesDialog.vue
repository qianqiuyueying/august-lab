<template>
  <el-dialog
    v-model="visible"
    title="产品文件"
    width="700px"
    @close="handleClose"
  >
    <div v-if="product" class="files-dialog">
      <!-- 产品信息 -->
      <div class="product-header">
        <h3>{{ product.title }}</h3>
        <div class="product-meta">
          <el-tag :type="getTypeTagType(product.product_type)" size="small">
            {{ getTypeLabel(product.product_type) }}
          </el-tag>
          <span class="version">v{{ product.version }}</span>
          <span class="entry-file">入口: {{ product.entry_file }}</span>
        </div>
      </div>
      
      <!-- 文件统计 -->
      <div v-if="fileInfo" class="file-stats">
        <div class="stat-item">
          <span class="stat-label">文件数量:</span>
          <span class="stat-value">{{ fileInfo.total_files }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">总大小:</span>
          <span class="stat-value">{{ formatSize(fileInfo.total_size) }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">上传时间:</span>
          <span class="stat-value">{{ formatUploadTime() }}</span>
        </div>
      </div>
      
      <!-- 文件列表 -->
      <div class="files-section">
        <div class="section-header">
          <h4>文件列表</h4>
          <div class="header-actions">
            <el-button size="small" @click="refreshFiles">
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button
              v-if="product.is_published"
              type="primary"
              size="small"
              @click="previewProduct"
            >
              <el-icon><View /></el-icon>
              预览产品
            </el-button>
          </div>
        </div>
        
        <!-- 加载状态 -->
        <div v-if="loading" class="loading-state">
          <el-icon class="is-loading"><Loading /></el-icon>
          <span>加载文件列表中...</span>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <el-alert type="error" :title="error" :closable="false" />
          <el-button type="primary" @click="loadFiles" style="margin-top: 12px">
            重试
          </el-button>
        </div>
        
        <!-- 文件表格 -->
        <el-table
          v-else-if="fileInfo?.files?.length"
          :data="fileInfo.files"
          stripe
          size="small"
          max-height="400"
        >
          <el-table-column label="文件名" min-width="200">
            <template #default="{ row }">
              <div class="file-name">
                <el-icon class="file-icon">
                  <component :is="getFileIcon(row.name)" />
                </el-icon>
                <span class="name">{{ row.name }}</span>
                <el-tag
                  v-if="row.path === product.entry_file"
                  type="success"
                  size="small"
                  class="entry-tag"
                >
                  入口
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="路径" min-width="150">
            <template #default="{ row }">
              <code class="file-path">{{ row.path }}</code>
            </template>
          </el-table-column>
          
          <el-table-column label="大小" width="100">
            <template #default="{ row }">
              {{ formatSize(row.size) }}
            </template>
          </el-table-column>
          
          <el-table-column label="类型" width="120">
            <template #default="{ row }">
              <el-tag size="small" :type="getFileTypeTag(row.type)">
                {{ getFileTypeLabel(row.type) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="修改时间" width="150">
            <template #default="{ row }">
              {{ formatFileTime(row.modified) }}
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 空状态 -->
        <div v-else class="empty-state">
          <el-empty description="暂无文件" />
        </div>
      </div>
      
      <!-- 完整性验证 -->
      <div class="integrity-section">
        <div class="section-header">
          <h4>文件完整性</h4>
          <el-button size="small" @click="verifyIntegrity">
            <el-icon><Shield /></el-icon>
            验证完整性
          </el-button>
        </div>
        
        <div v-if="integrityResult" class="integrity-result">
          <el-alert
            :type="integrityResult.valid ? 'success' : 'error'"
            :title="integrityResult.message"
            :closable="false"
            show-icon
          />
        </div>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button
          v-if="product?.is_published && product?.file_path"
          type="primary"
          @click="previewProduct"
        >
          预览产品
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  View,
  Loading,
  Document,
  Picture,
  VideoPlay,
  Headset,
  Files,
  Lock
} from '@element-plus/icons-vue'
import { useProductStore } from '../../../frontend/composables/useProductStore'
import type { Product } from '../../../shared/types'

interface Props {
  modelValue: boolean
  product?: Product | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
}

interface FileInfo {
  files: Array<{
    name: string
    path: string
    size: number
    type: string
    modified: number
  }>
  total_files: number
  total_size: number
  metadata?: {
    upload_time: string
    file_hash: string
  }
}

interface IntegrityResult {
  valid: boolean
  message: string
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const visible = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
const fileInfo = ref<FileInfo | null>(null)
const integrityResult = ref<IntegrityResult | null>(null)

// 使用组合式函数
const { getProductFiles, verifyProductIntegrity } = useProductStore()

// 计算属性
const product = computed(() => props.product)

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && product.value) {
    loadFiles()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const loadFiles = async () => {
  if (!product.value?.id) return

  loading.value = true
  error.value = null
  
  try {
    fileInfo.value = await getProductFiles(product.value.id)
  } catch (err: any) {
    error.value = err.message || '加载文件列表失败'
  } finally {
    loading.value = false
  }
}

const refreshFiles = () => {
  loadFiles()
}

const verifyIntegrity = async () => {
  if (!product.value?.id) return

  try {
    const result = await verifyProductIntegrity(product.value.id)
    integrityResult.value = result
    
    if (result.valid) {
      ElMessage.success('文件完整性验证通过')
    } else {
      ElMessage.error('文件完整性验证失败')
    }
  } catch (err: any) {
    ElMessage.error(err.message || '验证失败')
  }
}

const previewProduct = () => {
  if (product.value) {
    const url = `/product/${product.value.id}`
    window.open(url, '_blank')
  }
}

const handleClose = () => {
  visible.value = false
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

const formatSize = (bytes: number) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i]
}

const formatUploadTime = () => {
  if (!fileInfo.value?.metadata?.upload_time) return '未知'
  
  const date = new Date(fileInfo.value.metadata.upload_time)
  return date.toLocaleString('zh-CN')
}

const formatFileTime = (timestamp: number) => {
  const date = new Date(timestamp * 1000)
  return date.toLocaleString('zh-CN')
}

const getFileIcon = (filename: string) => {
  const ext = filename.split('.').pop()?.toLowerCase()
  
  switch (ext) {
    case 'jpg':
    case 'jpeg':
    case 'png':
    case 'gif':
    case 'svg':
    case 'webp':
      return Picture
    case 'mp4':
    case 'webm':
    case 'avi':
    case 'mov':
      return VideoPlay
    case 'mp3':
    case 'wav':
    case 'ogg':
      return Headset
    case 'html':
    case 'htm':
    case 'css':
    case 'js':
    case 'json':
    case 'txt':
    case 'md':
      return Document
    default:
      return Files
  }
}

const getFileTypeLabel = (mimeType: string) => {
  if (!mimeType || mimeType === 'unknown') return '未知'
  
  const typeMap = {
    'text/html': 'HTML',
    'text/css': 'CSS',
    'application/javascript': 'JavaScript',
    'application/json': 'JSON',
    'text/plain': '文本',
    'image/jpeg': 'JPEG',
    'image/png': 'PNG',
    'image/gif': 'GIF',
    'image/svg+xml': 'SVG',
    'audio/mpeg': 'MP3',
    'video/mp4': 'MP4'
  }
  
  return typeMap[mimeType as keyof typeof typeMap] || mimeType.split('/')[1]?.toUpperCase() || '未知'
}

const getFileTypeTag = (mimeType: string) => {
  if (!mimeType || mimeType === 'unknown') return 'info'
  
  if (mimeType.startsWith('text/') || mimeType.includes('javascript') || mimeType.includes('json')) {
    return 'primary'
  } else if (mimeType.startsWith('image/')) {
    return 'success'
  } else if (mimeType.startsWith('audio/') || mimeType.startsWith('video/')) {
    return 'warning'
  } else {
    return 'info'
  }
}
</script>

<style scoped>
.files-dialog {
  padding: 0;
}

.product-header {
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.product-header h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 12px;
}

.version {
  color: #9ca3af;
}

.entry-file {
  color: #6b7280;
}

.file-stats {
  display: flex;
  gap: 24px;
  margin-bottom: 20px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.stat-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.files-section {
  margin-bottom: 20px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.section-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 40px;
  color: #6b7280;
}

.loading-state {
  gap: 12px;
}

.error-state {
  text-align: center;
}

.file-name {
  display: flex;
  align-items: center;
  gap: 8px;
}

.file-icon {
  color: #6b7280;
  font-size: 16px;
}

.name {
  flex: 1;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.entry-tag {
  margin-left: 8px;
}

.file-path {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  background: #f3f4f6;
  padding: 2px 4px;
  border-radius: 3px;
  color: #374151;
}

.integrity-section {
  margin-bottom: 20px;
}

.integrity-result {
  margin-top: 12px;
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
  
  .file-stats {
    flex-direction: column;
    gap: 12px;
  }
  
  .section-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: center;
  }
  
  .product-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>