<template>
  <div class="extension-management">
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">扩展管理</h1>
          <p class="page-description">管理系统扩展和产品类型</p>
        </div>
        <div class="header-actions">
          <el-button 
            @click="reloadExtensions" 
            :loading="loading"
            :icon="Refresh"
          >
            重新加载
          </el-button>
          <el-button 
            @click="showInstallDialog = true" 
            type="primary"
            :icon="Plus"
          >
            安装扩展
          </el-button>
        </div>
      </div>
    </div>

    <!-- 扩展统计 -->
    <div class="stats-grid">
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="40"><Box /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ extensions.length }}</div>
            <div class="stat-label">已安装扩展</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="40"><CircleCheck /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ enabledExtensions }}</div>
            <div class="stat-label">已启用扩展</div>
          </div>
        </div>
      </el-card>
      <el-card class="stat-card">
        <div class="stat-content">
          <div class="stat-icon">
            <el-icon :size="40"><Setting /></el-icon>
          </div>
          <div class="stat-info">
            <div class="stat-number">{{ availableProductTypes.length }}</div>
            <div class="stat-label">产品类型</div>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 扩展列表 -->
    <el-card class="extensions-section">
      <template #header>
        <div class="section-header">
          <h2>已安装的扩展</h2>
          <el-select v-model="filterType" placeholder="筛选类型" style="width: 150px" clearable>
            <el-option label="所有类型" value="" />
            <el-option label="产品类型" value="product_type" />
            <el-option label="渲染器" value="renderer" />
            <el-option label="验证器" value="validator" />
            <el-option label="处理器" value="processor" />
            <el-option label="钩子" value="hook" />
            <el-option label="中间件" value="middleware" />
          </el-select>
        </div>
      </template>

      <div v-loading="loading" class="extensions-grid">
        <el-card 
          v-for="extension in filteredExtensions" 
          :key="extension.name"
          class="extension-card"
          :class="{ 'disabled': !extension.enabled }"
          shadow="hover"
        >
          <div class="extension-header">
            <div class="extension-info">
              <h3>{{ extension.name }}</h3>
              <el-tag :type="extension.enabled ? 'success' : 'info'" size="small">
                {{ getTypeLabel(extension.extension_type) }}
              </el-tag>
            </div>
            <div class="extension-actions">
              <el-button 
                @click="toggleExtension(extension)"
                :type="extension.enabled ? 'warning' : 'success'"
                size="small"
              >
                {{ extension.enabled ? '禁用' : '启用' }}
              </el-button>
              <el-button 
                @click="configureExtension(extension)"
                :icon="Setting"
                size="small"
              />
              <el-button 
                @click="uninstallExtension(extension)"
                :icon="Delete"
                type="danger"
                size="small"
              />
            </div>
          </div>

          <div class="extension-content">
            <p class="extension-description">{{ extension.description || '无描述' }}</p>
            <div class="extension-meta">
              <el-tag size="small" type="info">
                <el-icon><User /></el-icon>
                {{ extension.author || '未知作者' }}
              </el-tag>
              <el-tag size="small" type="info">
                <el-icon><PriceTag /></el-icon>
                v{{ extension.version || '1.0.0' }}
              </el-tag>
              <el-tag v-if="extension.dependencies && extension.dependencies.length > 0" size="small" type="info">
                <el-icon><Link /></el-icon>
                依赖: {{ extension.dependencies.join(', ') }}
              </el-tag>
            </div>
          </div>
        </el-card>
        
        <!-- 扩展列表空状态 -->
        <el-empty 
          v-if="!loading && filteredExtensions.length === 0" 
          description="暂无扩展"
          :image-size="120"
          style="width: 100%; padding: 40px;"
        />
      </div>
    </el-card>

    <!-- 可用产品类型 -->
    <el-card class="product-types-section">
      <template #header>
        <h2>可用产品类型</h2>
      </template>
      <div v-loading="loading" class="product-types-grid">
        <el-card 
          v-for="productType in availableProductTypes" 
          :key="productType.type_name"
          class="product-type-card"
          shadow="hover"
        >
          <div class="product-type-header">
            <h3>{{ productType.display_name }}</h3>
            <el-tag type="primary" size="small">{{ productType.type_name }}</el-tag>
          </div>
          <p class="product-type-description">{{ productType.description }}</p>
          <div class="product-type-details">
            <div class="detail-item">
              <strong>支持的文件扩展名:</strong>
              <div class="file-extensions">
                <el-tag 
                  v-for="ext in productType.file_extensions" 
                  :key="ext"
                  size="small"
                  style="margin: 4px 4px 4px 0;"
                >
                  {{ ext }}
                </el-tag>
              </div>
            </div>
            <div class="detail-item">
              <strong>入口文件:</strong>
              {{ productType.entry_files.join(', ') }}
            </div>
          </div>
        </el-card>
        
        <!-- 产品类型空状态 -->
        <el-empty 
          v-if="!loading && availableProductTypes.length === 0" 
          description="暂无产品类型"
          :image-size="120"
          style="width: 100%; padding: 40px;"
        />
      </div>
    </el-card>

    <!-- 安装扩展对话框 -->
    <el-dialog
      v-model="showInstallDialog"
      title="安装扩展"
      width="600px"
    >
      <el-form>
        <el-form-item label="扩展路径或URL">
          <el-input 
            v-model="installForm.path" 
            placeholder="输入扩展文件路径或Git仓库URL"
          />
        </el-form-item>
        <el-form-item label="配置 (JSON格式)">
          <el-input 
            v-model="installForm.config" 
            type="textarea"
            :rows="6"
            placeholder='{"key": "value"}'
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showInstallDialog = false">取消</el-button>
        <el-button @click="installExtension" type="primary" :loading="installing">
          安装
        </el-button>
      </template>
    </el-dialog>

    <!-- 配置扩展对话框 -->
    <el-dialog
      v-model="showConfigDialog"
      :title="`配置扩展: ${currentExtension?.name}`"
      width="700px"
    >
      <el-form>
        <el-form-item label="配置 (JSON格式)">
          <el-input 
            v-model="configForm.config" 
            type="textarea"
            :rows="10"
            placeholder='{"key": "value"}'
          />
        </el-form-item>
        <el-form-item v-if="currentExtension?.config_schema">
          <template #label>
            <span>配置说明</span>
          </template>
          <el-card>
            <pre class="config-schema">{{ JSON.stringify(currentExtension.config_schema, null, 2) }}</pre>
          </el-card>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="showConfigDialog = false">取消</el-button>
        <el-button @click="saveExtensionConfig" type="primary" :loading="configuring">
          保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox, ElCard, ElButton, ElSelect, ElOption, ElTag, ElDialog, ElForm, ElFormItem, ElInput, ElEmpty } from 'element-plus'
import { Refresh, Plus, Setting, Delete, User, PriceTag, Link, Box, CircleCheck } from '@element-plus/icons-vue'
import api from '../../shared/api'

// 接口定义
interface Extension {
  name: string
  version: string
  description: string
  author: string
  extension_type: string
  enabled: boolean
  config?: any
  config_schema?: any
  dependencies: string[]
}

interface ProductType {
  type_name: string
  display_name: string
  description: string
  file_extensions: string[]
  entry_files: string[]
}

// 响应式数据
const extensions = ref<Extension[]>([])
const availableProductTypes = ref<ProductType[]>([])
const loading = ref(false)
const filterType = ref('')

// 对话框状态
const showInstallDialog = ref(false)
const showConfigDialog = ref(false)
const installing = ref(false)
const configuring = ref(false)

// 表单数据
const installForm = ref({
  path: '',
  config: '{}'
})

const configForm = ref({
  config: '{}'
})

const currentExtension = ref<Extension | null>(null)

// 计算属性
const enabledExtensions = computed(() => {
  return extensions.value.filter(ext => ext.enabled).length
})

const filteredExtensions = computed(() => {
  if (!filterType.value) return extensions.value
  return extensions.value.filter(ext => ext.extension_type === filterType.value)
})

// 方法
const loadExtensions = async () => {
  try {
    loading.value = true
    const response = await api.get('/products/extensions')
    extensions.value = response.data.extensions || []
  } catch (error: any) {
    ElMessage.error('加载扩展列表失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const loadProductTypes = async () => {
  try {
    const response = await api.get('/products/product-types')
    availableProductTypes.value = response.data.product_types || []
  } catch (error: any) {
    ElMessage.error('加载产品类型失败: ' + (error.response?.data?.detail || error.message))
  }
}

const reloadExtensions = async () => {
  try {
    loading.value = true
    await api.post('/products/extensions/reload')
    await loadExtensions()
    await loadProductTypes()
    ElMessage.success('扩展重新加载成功')
  } catch (error: any) {
    ElMessage.error('重新加载扩展失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    loading.value = false
  }
}

const installExtension = async () => {
  try {
    installing.value = true
    
    let config = {}
    if (installForm.value.config.trim()) {
      try {
        config = JSON.parse(installForm.value.config)
      } catch (e) {
        ElMessage.error('配置格式错误，请检查JSON格式')
        return
      }
    }

    await api.post('/products/extensions/install', {
      path: installForm.value.path,
      config: config
    })

    ElMessage.success('扩展安装成功')
    showInstallDialog.value = false
    installForm.value = { path: '', config: '{}' }
    await loadExtensions()
    await loadProductTypes()
  } catch (error: any) {
    ElMessage.error('安装扩展失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    installing.value = false
  }
}

const uninstallExtension = async (extension: Extension) => {
  try {
    await ElMessageBox.confirm(
      `确定要卸载扩展 "${extension.name}" 吗？`,
      '确认卸载',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    await api.delete(`/products/extensions/${extension.name}`)
    ElMessage.success('扩展卸载成功')
    await loadExtensions()
    await loadProductTypes()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error('卸载扩展失败: ' + (error.response?.data?.detail || error.message))
    }
  }
}

const toggleExtension = async (extension: Extension) => {
  // 保存原始状态，用于失败时回滚
  const originalEnabled = extension.enabled
  
  try {
    // 先更新本地状态（乐观更新）
    extension.enabled = !extension.enabled
    
    const newConfig = { ...(extension.config || {}), enabled: extension.enabled }
    await api.post(`/products/extensions/${extension.name}/configure`, { config: newConfig })
    
    ElMessage.success(`扩展已${extension.enabled ? '启用' : '禁用'}`)
  } catch (error: any) {
    // 失败时回滚状态
    extension.enabled = originalEnabled
    ElMessage.error('切换扩展状态失败: ' + (error.response?.data?.detail || error.message))
  }
}

const configureExtension = (extension: Extension) => {
  currentExtension.value = extension
  configForm.value.config = JSON.stringify(extension.config || {}, null, 2)
  showConfigDialog.value = true
}

const saveExtensionConfig = async () => {
  if (!currentExtension.value) return
  
  try {
    configuring.value = true
    
    let config = {}
    try {
      config = JSON.parse(configForm.value.config)
    } catch (e) {
      ElMessage.error('配置格式错误，请检查JSON格式')
      return
    }
    
    // 验证配置对象
    if (typeof config !== 'object' || Array.isArray(config)) {
      ElMessage.error('配置必须是对象类型')
      return
    }
    
    await api.post(`/products/extensions/${currentExtension.value.name}/configure`, { config })
    
    // 更新本地数据
    const index = extensions.value.findIndex(ext => ext.name === currentExtension.value!.name)
    if (index !== -1) {
      extensions.value[index].config = config
      // 如果配置中包含 enabled，也更新
      if ('enabled' in config) {
        extensions.value[index].enabled = config.enabled as boolean
      }
    }

    ElMessage.success('扩展配置保存成功')
    showConfigDialog.value = false
  } catch (error: any) {
    ElMessage.error('保存扩展配置失败: ' + (error.response?.data?.detail || error.message))
  } finally {
    configuring.value = false
  }
}

const getTypeLabel = (type: string) => {
  const labels: Record<string, string> = {
    'product_type': '产品类型',
    'renderer': '渲染器',
    'validator': '验证器',
    'processor': '处理器',
    'hook': '钩子',
    'middleware': '中间件'
  }
  return labels[type] || type
}

// 生命周期
onMounted(() => {
  loadExtensions()
  loadProductTypes()
})
</script>

<style scoped>
.extension-management {
  padding: 0;
}

.page-header {
  padding: 0 0 24px 0;
  margin-bottom: 24px;
  border-bottom: 1px solid #e5e7eb;
}

.dark .page-header {
  border-bottom-color: var(--lab-border);
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.header-left {
  flex: 1;
}

.page-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
}

.dark .page-title {
  color: #f3f4f6; /* Gray 50 */
}

.page-description {
  margin: 0;
  color: #6b7280;
  font-size: 14px;
}

.dark .page-description {
  color: #9ca3af; /* Gray 400 */
}

.header-actions {
  display: flex;
  gap: 12px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 20px;
  margin-bottom: 24px;
}

.stat-card {
  border-radius: 8px;
}

.stat-card :deep(.el-card__body) {
  padding: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
}

.stat-info {
  flex: 1;
}

.stat-number {
  font-size: 28px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.dark .stat-number {
  color: #f3f4f6; /* Gray 50 */
}

.stat-label {
  color: #6b7280;
  font-size: 14px;
}

.dark .stat-label {
  color: #9ca3af; /* Gray 400 */
}

.extensions-section, .product-types-section {
  margin-bottom: 24px;
}

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.section-header h2 {
  margin: 0;
  color: #1f2937;
  font-size: 18px;
  font-weight: 600;
}

.dark .section-header h2 {
  color: #f3f4f6; /* Gray 50 */
}

.extensions-grid, .product-types-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(400px, 1fr));
  gap: 20px;
}

.extension-card, .product-type-card {
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  padding: 20px;
  transition: all 0.2s;
}

.dark .extension-card, .dark .product-type-card {
  border-color: rgba(148, 163, 184, 0.15); /* Slate 400 15% */
}

.extension-card:hover, .product-type-card:hover {
  box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
}

.dark .extension-card:hover, .dark .product-type-card:hover {
  box-shadow: 0 4px 12px -4px rgba(59, 130, 246, 0.2);
}

.extension-card.disabled {
  opacity: 0.6;
}

.extension-card.disabled :deep(.el-card__body) {
  opacity: 0.85;
}

.extension-header, .product-type-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 15px;
}

.extension-info h3, .product-type-header h3 {
  margin: 0 0 5px 0;
  color: #333;
}

.dark .extension-info h3, .dark .product-type-header h3 {
  color: #f3f4f6; /* Gray 50 */
}

.extension-type, .product-type-name {
  background: #007bff;
  color: white;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.extension-actions {
  display: flex;
  gap: 5px;
}

.extension-description, .product-type-description {
  color: #666;
  margin-bottom: 15px;
  line-height: 1.5;
}

.dark .extension-description, .dark .product-type-description {
  color: #d1d5db; /* Gray 300 */
}

.extension-meta {
  display: flex;
  flex-wrap: wrap;
  gap: 15px;
  align-items: center;
}

.extension-meta :deep(.el-tag) {
  display: inline-flex !important;
  align-items: center !important;
  white-space: nowrap !important;
  flex-shrink: 0 !important;
  min-width: max-content !important;
  max-width: none !important;
}

.extension-meta :deep(.el-tag *),
.extension-meta :deep(.el-tag .el-icon) {
  white-space: nowrap !important;
  flex-shrink: 0 !important;
}

.extension-meta :deep(.el-tag .el-icon) {
  margin-right: 4px;
}

.meta-item {
  display: flex;
  align-items: center;
  gap: 5px;
  color: #666;
  font-size: 14px;
}

.product-type-details {
  margin-top: 15px;
}

.detail-item {
  margin-bottom: 10px;
}

.file-extensions {
  display: flex;
  flex-wrap: wrap;
  gap: 5px;
  margin-top: 5px;
}

.file-ext {
  background: #f8f9fa;
  border: 1px solid #e0e0e0;
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 12px;
  font-family: monospace;
}

/* 移除不再需要的模态框样式，使用 Element Plus Dialog */

.config-schema {
  margin: 0;
  padding: 0;
  background: transparent;
  font-size: 12px;
  overflow-x: auto;
  white-space: pre-wrap;
  word-wrap: break-word;
}

/* 移除不再需要的按钮样式，使用 Element Plus Button */
</style>