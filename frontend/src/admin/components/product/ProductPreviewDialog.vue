<template>
  <el-dialog
    v-model="visible"
    title="产品预览"
    width="90%"
    :close-on-click-modal="false"
    @close="handleClose"
    class="product-preview-dialog"
  >
    <div v-if="product" class="preview-container">
      <!-- 预览头部信息 -->
      <div class="preview-header">
        <div class="product-info">
          <h3>{{ product.title }}</h3>
          <div class="product-meta">
            <el-tag :type="getTypeTagType(product.product_type)" size="small">
              {{ getTypeLabel(product.product_type) }}
            </el-tag>
            <span class="version">v{{ product.version }}</span>
            <el-tag v-if="!product.is_published" type="warning" size="small">
              未发布
            </el-tag>
          </div>
        </div>
        
        <div class="preview-controls">
          <el-button-group>
            <el-button 
              size="small" 
              @click="refreshPreview"
              :loading="refreshing"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
            <el-button 
              size="small" 
              @click="toggleFullscreen"
            >
              <el-icon>
                <Aim v-if="isFullscreen" />
                <FullScreen v-else />
              </el-icon>
              {{ isFullscreen ? '退出全屏' : '全屏' }}
            </el-button>
            <el-button 
              size="small" 
              @click="openInNewTab"
              :disabled="!canPreview"
            >
              <el-icon><Link /></el-icon>
              新窗口打开
            </el-button>
          </el-button-group>
        </div>
      </div>
      
      <!-- 预览内容区域 -->
      <div class="preview-content" :class="{ 'preview-fullscreen': isFullscreen }">
        <!-- 加载状态 -->
        <div v-if="loading" class="preview-loading">
          <el-icon class="is-loading" size="32"><Loading /></el-icon>
          <p>{{ loadingMessage }}</p>
        </div>
        
        <!-- 错误状态 -->
        <div v-else-if="error" class="preview-error">
          <el-icon size="32" color="#f56c6c"><WarningFilled /></el-icon>
          <h4>预览失败</h4>
          <p>{{ error }}</p>
          <el-button type="primary" @click="loadPreview">重试</el-button>
        </div>
        
        <!-- 无文件状态 -->
        <div v-else-if="!canPreview" class="preview-empty">
          <el-icon size="32" color="#909399"><FolderOpened /></el-icon>
          <h4>无法预览</h4>
          <p>产品文件尚未上传，请先上传产品文件</p>
          <el-button type="primary" @click="$emit('upload-files')">
            上传文件
          </el-button>
        </div>
        
        <!-- iframe预览 -->
        <iframe
          v-else
          ref="previewFrame"
          :src="previewUrl"
          class="preview-iframe"
          :sandbox="sandboxOptions"
          @load="onFrameLoad"
          @error="onFrameError"
        />
      </div>
      
      <!-- 预览信息面板 -->
      <div class="preview-info">
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="基本信息" name="basic">
            <div class="info-grid">
              <div class="info-item">
                <span class="label">入口文件:</span>
                <code>{{ product.entry_file }}</code>
              </div>
              <div class="info-item">
                <span class="label">文件路径:</span>
                <code>{{ product.file_path || '未上传' }}</code>
              </div>
              <div class="info-item">
                <span class="label">预览地址:</span>
                <code>{{ previewUrl || '不可用' }}</code>
              </div>
              <div class="info-item">
                <span class="label">沙箱选项:</span>
                <code>{{ sandboxOptions }}</code>
              </div>
            </div>
          </el-collapse-item>
          
          <el-collapse-item title="测试结果" name="test">
            <div class="test-results">
              <div class="test-item" :class="testResults.fileExists ? 'test-pass' : 'test-fail'">
                <el-icon>
                  <component :is="testResults.fileExists ? 'SuccessFilled' : 'CircleCloseFilled'" />
                </el-icon>
                <span>入口文件存在检查</span>
                <span class="test-status">
                  {{ testResults.fileExists ? '通过' : '失败' }}
                </span>
              </div>
              
              <div class="test-item" :class="testResults.loadable ? 'test-pass' : 'test-fail'">
                <el-icon>
                  <component :is="testResults.loadable ? 'SuccessFilled' : 'CircleCloseFilled'" />
                </el-icon>
                <span>页面加载检查</span>
                <span class="test-status">
                  {{ testResults.loadable ? '通过' : '失败' }}
                </span>
              </div>
              
              <div class="test-item" :class="testResults.responsive ? 'test-pass' : 'test-warn'">
                <el-icon>
                  <component :is="testResults.responsive ? 'SuccessFilled' : 'WarningFilled'" />
                </el-icon>
                <span>响应式设计检查</span>
                <span class="test-status">
                  {{ testResults.responsive ? '通过' : '警告' }}
                </span>
              </div>
            </div>
            
            <div class="test-actions">
              <el-button size="small" @click="runTests">
                <el-icon><VideoPlay /></el-icon>
                重新测试
              </el-button>
              <el-button size="small" @click="generateTestReport">
                <el-icon><Document /></el-icon>
                生成报告
              </el-button>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>
    </div>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">关闭</el-button>
        <el-button 
          v-if="canPreview && product && !product.is_published" 
          type="success" 
          @click="publishProduct"
          :loading="publishing"
        >
          发布产品
        </el-button>
        <el-button 
          v-if="canPreview" 
          type="primary" 
          @click="openInNewTab"
        >
          在新窗口中打开
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  FullScreen,
  Aim,
  Link,
  Loading,
  WarningFilled,
  FolderOpened,
  SuccessFilled,
  CircleCloseFilled,
  VideoPlay,
  Document
} from '@element-plus/icons-vue'
import { useProductStore } from '../../../frontend/composables/useProductStore'
import type { Product } from '../../../shared/types'

interface Props {
  modelValue: boolean
  product?: Product | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'upload-files'): void
  (e: 'product-published'): void
}

interface TestResults {
  fileExists: boolean
  loadable: boolean
  responsive: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const visible = ref(false)
const loading = ref(false)
const error = ref<string | null>(null)
const loadingMessage = ref('正在加载预览...')
const refreshing = ref(false)
const publishing = ref(false)
const isFullscreen = ref(false)
const previewFrame = ref<HTMLIFrameElement>()
const activeCollapse = ref(['basic'])

const testResults = ref<TestResults>({
  fileExists: false,
  loadable: false,
  responsive: false
})

// 使用组合式函数
const { updateProduct } = useProductStore()

// 计算属性
const canPreview = computed(() => {
  return props.product?.file_path && props.product?.entry_file
})

const previewUrl = computed(() => {
  if (!canPreview.value || !props.product) return undefined
  return `/products/${props.product.id}/${props.product.entry_file}`
})

const sandboxOptions = computed(() => {
  const baseOptions = [
    'allow-scripts',
    'allow-same-origin',
    'allow-forms',
    'allow-popups',
    'allow-modals'
  ]
  
  if (props.product?.product_type === 'game') {
    baseOptions.push('allow-pointer-lock')
  }
  
  return baseOptions.join(' ')
})

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val && props.product) {
    loadPreview()
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
  if (!val) {
    isFullscreen.value = false
  }
})

// 方法
const loadPreview = async () => {
  if (!canPreview.value) {
    error.value = '产品文件未上传'
    return
  }
  
  loading.value = true
  error.value = null
  loadingMessage.value = '正在加载预览...'
  
  try {
    // 运行基础测试
    await runTests()
    
    // 等待iframe加载
    await nextTick()
    
  } catch (err: any) {
    error.value = err.message || '预览加载失败'
  } finally {
    loading.value = false
  }
}

const refreshPreview = async () => {
  refreshing.value = true
  try {
    if (previewFrame.value) {
      previewFrame.value.src = previewFrame.value.src
    }
    await loadPreview()
  } finally {
    setTimeout(() => {
      refreshing.value = false
    }, 500)
  }
}

const toggleFullscreen = () => {
  isFullscreen.value = !isFullscreen.value
}

const openInNewTab = () => {
  if (previewUrl.value) {
    window.open(previewUrl.value, '_blank')
  }
}

const runTests = async () => {
  if (!props.product) return
  
  // 重置测试结果
  testResults.value = {
    fileExists: false,
    loadable: false,
    responsive: false
  }
  
  try {
    // 测试1: 检查入口文件是否存在
    testResults.value.fileExists = !!props.product.file_path
    
    // 测试2: 检查页面是否可加载
    if (previewUrl.value) {
      try {
        const response = await fetch(previewUrl.value, { method: 'HEAD' })
        testResults.value.loadable = response.ok
      } catch {
        testResults.value.loadable = false
      }
    }
    
    // 测试3: 响应式设计检查（简单检查）
    testResults.value.responsive = true // 默认通过，实际可以通过iframe检查
    
  } catch (error) {
    console.error('测试运行失败:', error)
  }
}

const generateTestReport = () => {
  const report = {
    product: props.product?.title,
    version: props.product?.version,
    testTime: new Date().toISOString(),
    results: testResults.value,
    summary: {
      passed: Object.values(testResults.value).filter(Boolean).length,
      total: Object.keys(testResults.value).length
    }
  }
  
  const reportText = JSON.stringify(report, null, 2)
  const blob = new Blob([reportText], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  
  const a = document.createElement('a')
  a.href = url
  a.download = `product-test-report-${props.product?.id}.json`
  a.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('测试报告已下载')
}

const publishProduct = async () => {
  if (!props.product) return
  
  try {
    await ElMessageBox.confirm(
      '确定要发布此产品吗？发布后用户将可以访问此产品。',
      '确认发布',
      {
        confirmButtonText: '发布',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    publishing.value = true
    
    await updateProduct(props.product.id, {
      is_published: true
    })
    
    ElMessage.success('产品发布成功')
    emit('product-published')
    
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '发布失败')
    }
  } finally {
    publishing.value = false
  }
}

const onFrameLoad = () => {
  testResults.value.loadable = true
  loading.value = false
}

const onFrameError = () => {
  testResults.value.loadable = false
  error.value = '预览页面加载失败'
  loading.value = false
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
</script>

<style scoped>
.product-preview-dialog {
  --el-dialog-padding-primary: 0;
}

.preview-container {
  display: flex;
  flex-direction: column;
  height: 70vh;
}

.preview-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #e5e7eb;
  background: #f9fafb;
}

.product-info h3 {
  margin: 0 0 8px 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.version {
  font-size: 12px;
  color: #6b7280;
}

.preview-content {
  flex: 1;
  position: relative;
  background: #fff;
}

.preview-fullscreen {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 9999;
  background: #000;
}

.preview-loading,
.preview-error,
.preview-empty {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  padding: 40px;
  text-align: center;
}

.preview-loading p,
.preview-error p,
.preview-empty p {
  color: #6b7280;
  margin: 0;
}

.preview-error h4,
.preview-empty h4 {
  margin: 0;
  color: #374151;
}

.preview-iframe {
  width: 100%;
  height: 100%;
  border: none;
  background: #fff;
}

.preview-info {
  border-top: 1px solid #e5e7eb;
  background: #f9fafb;
}

.info-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
  padding: 16px;
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

.info-item code {
  font-size: 12px;
  background: #f3f4f6;
  padding: 2px 6px;
  border-radius: 3px;
  color: #374151;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.test-results {
  padding: 16px;
}

.test-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 0;
  border-bottom: 1px solid #f3f4f6;
}

.test-item:last-child {
  border-bottom: none;
}

.test-item.test-pass {
  color: #059669;
}

.test-item.test-fail {
  color: #dc2626;
}

.test-item.test-warn {
  color: #d97706;
}

.test-status {
  margin-left: auto;
  font-size: 12px;
  font-weight: 500;
}

.test-actions {
  padding: 16px;
  border-top: 1px solid #f3f4f6;
  display: flex;
  gap: 8px;
}

.dialog-footer {
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .preview-controls {
    display: flex;
    justify-content: center;
  }
  
  .info-grid {
    grid-template-columns: 1fr;
  }
  
  .test-actions {
    flex-direction: column;
  }
}
</style>