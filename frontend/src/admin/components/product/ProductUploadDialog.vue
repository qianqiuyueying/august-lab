<template>
  <el-dialog
    v-model="visible"
    title="上传产品文件"
    width="600px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <div v-if="product" class="upload-dialog">
      <!-- 产品信息 -->
      <div class="product-info">
        <h3>{{ product.title }}</h3>
        <p>{{ product.description }}</p>
        <div class="product-meta">
          <el-tag :type="getTypeTagType(product.product_type)" size="small">
            {{ getTypeLabel(product.product_type) }}
          </el-tag>
          <span class="version">v{{ product.version }}</span>
          <span class="entry-file">入口文件: {{ product.entry_file }}</span>
        </div>
      </div>
      
      <!-- 上传区域 -->
      <div class="upload-section">
        <el-upload
          ref="uploadRef"
          :auto-upload="false"
          :show-file-list="true"
          :limit="1"
          :accept="'.zip'"
          :before-upload="beforeUpload"
          :on-change="handleFileChange"
          :on-remove="handleFileRemove"
          :on-exceed="handleExceed"
          drag
          class="upload-dragger"
        >
          <div class="upload-content">
            <el-icon class="upload-icon"><UploadFilled /></el-icon>
            <div class="upload-text">
              <p>点击或拖拽 ZIP 文件到此区域上传</p>
              <p class="upload-hint">
                请确保 ZIP 文件中包含 <code>{{ product.entry_file }}</code> 文件
              </p>
            </div>
          </div>
        </el-upload>
        
        <!-- 上传要求 -->
        <div class="upload-requirements">
          <h4>上传要求：</h4>
          <ul>
            <li>文件格式：ZIP 压缩包</li>
            <li>文件大小：不超过 100MB</li>
            <li>必须包含入口文件：<code>{{ product.entry_file }}</code></li>
            <li>支持的文件类型：HTML、CSS、JS、图片、字体等静态资源</li>
            <li>不支持服务器端可执行文件（如 .php、.py、.exe 等）</li>
          </ul>
        </div>
        
        <!-- 当前文件状态 -->
        <div v-if="product.file_path" class="current-files">
          <h4>当前文件状态：</h4>
          <div class="file-status">
            <el-tag type="success" size="small">已上传文件</el-tag>
            <span class="file-path">{{ product.file_path }}</span>
            <el-button
              type="text"
              size="small"
              @click="viewCurrentFiles"
            >
              查看文件列表
            </el-button>
          </div>
          <el-alert
            type="warning"
            :closable="false"
            show-icon
          >
            <template #title>
              上传新文件将覆盖现有文件，此操作不可恢复
            </template>
          </el-alert>
        </div>
      </div>
      
      <!-- 上传进度 -->
      <div v-if="uploading" class="upload-progress">
        <el-progress
          :percentage="uploadProgress"
          :status="uploadStatus"
          :stroke-width="8"
        />
        <p class="progress-text">{{ progressText }}</p>
      </div>
      
      <!-- 上传结果 -->
      <div v-if="uploadResult" class="upload-result">
        <el-alert
          :type="uploadResult.success ? 'success' : 'error'"
          :title="uploadResult.message"
          :closable="false"
          show-icon
        >
          <template v-if="uploadResult.success && uploadResult.files" #default>
            <div class="result-details">
              <p>成功解压 {{ uploadResult.files.length }} 个文件：</p>
              <ul class="file-list">
                <li v-for="file in uploadResult.files.slice(0, 10)" :key="file">
                  {{ file }}
                </li>
                <li v-if="uploadResult.files.length > 10">
                  ... 还有 {{ uploadResult.files.length - 10 }} 个文件
                </li>
              </ul>
            </div>
          </template>
        </el-alert>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose" :disabled="uploading">
          {{ uploadResult?.success ? '完成' : '取消' }}
        </el-button>
        <el-button
          v-if="!uploadResult?.success"
          type="primary"
          :loading="uploading"
          :disabled="!selectedFile"
          @click="handleUpload"
        >
          {{ uploading ? '上传中...' : '开始上传' }}
        </el-button>
        <el-button
          v-if="uploadResult?.success"
          type="success"
          @click="previewProduct"
        >
          预览产品
        </el-button>
      </div>
    </template>
    
    <!-- 文件查看对话框 -->
    <ProductFilesDialog
      v-model="showFilesDialog"
      :product="product"
    />
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import ProductFilesDialog from './ProductFilesDialog.vue'
import { useProductStore } from '../../../frontend/composables/useProductStore'
import type { Product } from '../../../shared/types'
import type { UploadFile, UploadFiles, UploadInstance } from 'element-plus'

interface Props {
  modelValue: boolean
  product?: Product | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

interface UploadResult {
  success: boolean
  message: string
  files?: string[]
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const uploadRef = ref<UploadInstance>()
const visible = ref(false)
const uploading = ref(false)
const uploadProgress = ref(0)
const uploadStatus = ref<'success' | 'exception' | undefined>()
const progressText = ref('')
const selectedFile = ref<File | null>(null)
const uploadResult = ref<UploadResult | null>(null)
const showFilesDialog = ref(false)

// 使用组合式函数
const { uploadProductFiles } = useProductStore()

// 计算属性
const product = computed(() => props.product)

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    resetUpload()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

// 方法
const resetUpload = () => {
  uploading.value = false
  uploadProgress.value = 0
  uploadStatus.value = undefined
  progressText.value = ''
  selectedFile.value = null
  uploadResult.value = null
  uploadRef.value?.clearFiles()
}

const beforeUpload = (file: File) => {
  const isZip = file.type === 'application/zip' || file.name.endsWith('.zip')
  const isLt100M = file.size / 1024 / 1024 < 100

  if (!isZip) {
    ElMessage.error('只能上传 ZIP 格式的文件!')
    return false
  }
  if (!isLt100M) {
    ElMessage.error('文件大小不能超过 100MB!')
    return false
  }
  return false // 阻止自动上传
}

const handleFileChange = (file: UploadFile, files: UploadFiles) => {
  if (file.raw) {
    selectedFile.value = file.raw
    uploadResult.value = null
  }
}

const handleFileRemove = () => {
  selectedFile.value = null
  uploadResult.value = null
}

const handleExceed = () => {
  ElMessage.warning('只能上传一个文件')
}

const handleUpload = async () => {
  if (!selectedFile.value || !product.value) {
    return
  }

  uploading.value = true
  uploadProgress.value = 0
  uploadStatus.value = undefined
  progressText.value = '正在上传文件...'

  try {
    // 模拟上传进度
    const progressInterval = setInterval(() => {
      if (uploadProgress.value < 90) {
        uploadProgress.value += Math.random() * 10
      }
    }, 200)

    const result = await uploadProductFiles(product.value.id, selectedFile.value)

    clearInterval(progressInterval)
    uploadProgress.value = 100
    uploadStatus.value = 'success'
    progressText.value = '上传完成'

    uploadResult.value = {
      success: true,
      message: '文件上传成功',
      files: result.extracted_files
    }

    ElMessage.success('产品文件上传成功')
    emit('success')

  } catch (error: any) {
    uploadProgress.value = 100
    uploadStatus.value = 'exception'
    progressText.value = '上传失败'

    uploadResult.value = {
      success: false,
      message: error.message || '文件上传失败'
    }

    ElMessage.error(error.message || '文件上传失败')
  } finally {
    uploading.value = false
  }
}

const viewCurrentFiles = () => {
  showFilesDialog.value = true
}

const previewProduct = () => {
  if (product.value) {
    const url = `/product/${product.value.id}`
    window.open(url, '_blank')
  }
}

const handleClose = () => {
  if (!uploading.value) {
    visible.value = false
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
.upload-dialog {
  padding: 0;
}

.product-info {
  margin-bottom: 24px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.product-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.product-info p {
  margin: 0 0 12px 0;
  color: #6b7280;
  font-size: 14px;
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

.entry-file code {
  background: #e5e7eb;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.upload-section {
  margin-bottom: 24px;
}

.upload-dragger {
  width: 100%;
}

.upload-content {
  padding: 40px 20px;
  text-align: center;
}

.upload-icon {
  font-size: 48px;
  color: #c0c4cc;
  margin-bottom: 16px;
}

.upload-text p {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #606266;
}

.upload-hint {
  font-size: 14px !important;
  color: #909399 !important;
}

.upload-hint code {
  background: #f5f5f5;
  padding: 2px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.upload-requirements {
  margin-top: 16px;
  padding: 16px;
  background: #f8f9fa;
  border-radius: 8px;
}

.upload-requirements h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.upload-requirements ul {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.6;
}

.upload-requirements li {
  margin-bottom: 4px;
}

.upload-requirements code {
  background: #e5e7eb;
  padding: 1px 4px;
  border-radius: 3px;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.current-files {
  margin-top: 16px;
  padding: 16px;
  background: #fef3c7;
  border-radius: 8px;
}

.current-files h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #92400e;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  font-size: 13px;
}

.file-path {
  color: #6b7280;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.upload-progress {
  margin: 24px 0;
}

.progress-text {
  text-align: center;
  margin-top: 8px;
  font-size: 14px;
  color: #6b7280;
}

.upload-result {
  margin: 24px 0;
}

.result-details {
  margin-top: 12px;
}

.result-details p {
  margin: 0 0 8px 0;
  font-size: 14px;
  font-weight: 500;
}

.file-list {
  margin: 0;
  padding-left: 20px;
  font-size: 13px;
  color: #6b7280;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  line-height: 1.4;
  max-height: 120px;
  overflow-y: auto;
}

.file-list li {
  margin-bottom: 2px;
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
  
  .upload-content {
    padding: 30px 15px;
  }
  
  .upload-icon {
    font-size: 36px;
  }
  
  .product-meta {
    flex-direction: column;
    align-items: flex-start;
    gap: 8px;
  }
}
</style>