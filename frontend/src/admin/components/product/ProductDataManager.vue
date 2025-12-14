<template>
  <div class="product-data-manager">
    <!-- 存储概览 -->
    <el-card class="storage-overview-card">
      <template #header>
        <div class="card-header">
          <h3>存储概览</h3>
          <el-button
            type="primary"
            size="small"
            @click="loadStorageStats"
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <div class="storage-stats">
        <div class="stat-item">
          <div class="stat-label">已用存储</div>
          <div class="stat-value">{{ formatBytes(storageStats.total_size_bytes) }}</div>
        </div>
        
        <div class="stat-item">
          <div class="stat-label">数据记录</div>
          <div class="stat-value">{{ storageStats.total_records }}</div>
        </div>
        
        <div class="stat-item">
          <div class="stat-label">存储配额</div>
          <div class="stat-value">{{ formatBytes(storageQuota.total_bytes) }}</div>
        </div>
        
        <div class="stat-item">
          <div class="stat-label">使用率</div>
          <div class="stat-value">{{ storageQuota.usage_percentage.toFixed(1) }}%</div>
        </div>
      </div>
      
      <div class="storage-progress">
        <el-progress
          :percentage="storageQuota.usage_percentage"
          :color="getProgressColor(storageQuota.usage_percentage)"
          :show-text="false"
        />
        <div class="progress-text">
          {{ formatBytes(storageQuota.used_bytes) }} / {{ formatBytes(storageQuota.total_bytes) }}
        </div>
      </div>
    </el-card>
    
    <!-- 数据管理操作 -->
    <el-card class="data-actions-card">
      <template #header>
        <h3>数据管理</h3>
      </template>
      
      <div class="action-buttons">
        <el-button
          type="primary"
          @click="showCreateDataDialog = true"
        >
          <el-icon><Plus /></el-icon>
          添加数据
        </el-button>
        
        <el-button
          type="success"
          @click="exportAllData"
          :loading="exporting"
        >
          <el-icon><Download /></el-icon>
          导出数据
        </el-button>
        
        <el-upload
          ref="uploadRef"
          :show-file-list="false"
          :before-upload="handleImportData"
          accept=".json"
          class="import-upload"
        >
          <el-button type="info">
            <el-icon><Upload /></el-icon>
            导入数据
          </el-button>
        </el-upload>
        
        <el-button
          type="warning"
          @click="clearAllData"
          :loading="clearing"
        >
          <el-icon><Delete /></el-icon>
          清空数据
        </el-button>
      </div>
    </el-card>
    
    <!-- 数据列表 -->
    <el-card class="data-list-card">
      <template #header>
        <div class="card-header">
          <h3>数据记录</h3>
          <div class="header-actions">
            <el-input
              v-model="searchKey"
              placeholder="搜索键名"
              size="small"
              style="width: 200px; margin-right: 8px"
              @input="filterData"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            
            <el-button
              size="small"
              @click="loadStorageData"
              :loading="loadingData"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="filteredData"
        v-loading="loadingData"
        class="data-table"
      >
        <el-table-column prop="key" label="键名" width="200">
          <template #default="{ row }">
            <code class="data-key">{{ row.key }}</code>
          </template>
        </el-table-column>
        
        <el-table-column prop="size_bytes" label="大小" width="100">
          <template #default="{ row }">
            {{ formatBytes(row.size_bytes) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="access_count" label="访问次数" width="100" />
        
        <el-table-column prop="created_at" label="创建时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="updated_at" label="更新时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.updated_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="accessed_at" label="最后访问" width="180">
          <template #default="{ row }">
            {{ row.accessed_at ? formatDate(row.accessed_at) : '未访问' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200">
          <template #default="{ row }">
            <el-button
              type="primary"
              size="small"
              @click="viewData(row)"
            >
              查看
            </el-button>
            
            <el-button
              type="warning"
              size="small"
              @click="editData(row)"
            >
              编辑
            </el-button>
            
            <el-button
              type="danger"
              size="small"
              @click="deleteDataRecord(row)"
            >
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="pagination.page"
          v-model:page-size="pagination.size"
          :total="pagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadStorageData"
          @current-change="loadStorageData"
        />
      </div>
    </el-card>
    
    <!-- 创建/编辑数据对话框 -->
    <el-dialog
      v-model="showCreateDataDialog"
      :title="editingData ? '编辑数据' : '添加数据'"
      width="600px"
    >
      <el-form
        ref="dataFormRef"
        :model="dataForm"
        :rules="dataRules"
        label-width="80px"
      >
        <el-form-item label="键名" prop="key">
          <el-input
            v-model="dataForm.key"
            placeholder="请输入数据键名"
            :disabled="!!editingData"
          />
        </el-form-item>
        
        <el-form-item label="数据类型" prop="dataType">
          <el-radio-group v-model="dataForm.dataType">
            <el-radio label="json">JSON对象</el-radio>
            <el-radio label="text">文本</el-radio>
            <el-radio label="number">数字</el-radio>
            <el-radio label="boolean">布尔值</el-radio>
          </el-radio-group>
        </el-form-item>
        
        <el-form-item label="数据内容" prop="content">
          <el-input
            v-if="dataForm.dataType === 'text'"
            v-model="dataForm.content"
            type="textarea"
            :rows="6"
            placeholder="请输入文本内容"
          />
          
          <el-input-number
            v-else-if="dataForm.dataType === 'number'"
            v-model="dataForm.content"
            style="width: 100%"
            placeholder="请输入数字"
          />
          
          <el-switch
            v-else-if="dataForm.dataType === 'boolean'"
            v-model="dataForm.content"
          />
          
          <div v-else class="json-editor">
            <el-input
              v-model="dataForm.content"
              type="textarea"
              :rows="8"
              placeholder="请输入JSON格式的数据"
            />
            <div class="json-help">
              <el-text size="small" type="info">
                请输入有效的JSON格式数据，例如：{"name": "value", "count": 123}
              </el-text>
            </div>
          </div>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="cancelDataEdit">取消</el-button>
        <el-button
          type="primary"
          @click="saveData"
          :loading="saving"
        >
          保存
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 查看数据对话框 -->
    <el-dialog
      v-model="showViewDataDialog"
      title="查看数据"
      width="700px"
    >
      <div v-if="viewingData" class="data-viewer">
        <div class="data-meta">
          <el-descriptions :column="2" border>
            <el-descriptions-item label="键名">
              <code>{{ viewingData.key }}</code>
            </el-descriptions-item>
            <el-descriptions-item label="大小">
              {{ formatBytes(viewingData.size_bytes) }}
            </el-descriptions-item>
            <el-descriptions-item label="访问次数">
              {{ viewingData.access_count }}
            </el-descriptions-item>
            <el-descriptions-item label="创建时间">
              {{ formatDate(viewingData.created_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="更新时间">
              {{ formatDate(viewingData.updated_at) }}
            </el-descriptions-item>
            <el-descriptions-item label="最后访问">
              {{ viewingData.accessed_at ? formatDate(viewingData.accessed_at) : '未访问' }}
            </el-descriptions-item>
          </el-descriptions>
        </div>
        
        <div class="data-content">
          <h4>数据内容：</h4>
          <pre class="data-preview">{{ formatDataForDisplay(viewingData.data) }}</pre>
        </div>
      </div>
      
      <template #footer>
        <el-button @click="showViewDataDialog = false">关闭</el-button>
        <el-button
          type="primary"
          @click="copyDataContent"
        >
          <el-icon><CopyDocument /></el-icon>
          复制内容
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  Plus,
  Download,
  Upload,
  Delete,
  Search,
  CopyDocument
} from '@element-plus/icons-vue'
import { useProductStorage } from '../../../frontend/composables/useProductStorage'
import type { ProductStorageRecord, ProductStorageStats } from '../../../frontend/composables/useProductStorage'

interface Props {
  productId: number
}

const props = defineProps<Props>()

// 响应式数据
const loading = ref(false)
const loadingData = ref(false)
const saving = ref(false)
const exporting = ref(false)
const clearing = ref(false)

const showCreateDataDialog = ref(false)
const showViewDataDialog = ref(false)
const searchKey = ref('')

const dataFormRef = ref()
const uploadRef = ref()

const storageStats = reactive<ProductStorageStats>({
  product_id: props.productId,
  total_records: 0,
  total_size_bytes: 0,
  records: []
})

const storageQuota = reactive({
  used_bytes: 0,
  total_bytes: 100 * 1024 * 1024, // 100MB
  available_bytes: 0,
  usage_percentage: 0
})

const dataForm = reactive<{
  key: string
  dataType: 'text' | 'number' | 'boolean' | 'json'
  content: string | number | boolean
}>({
  key: '',
  dataType: 'json',
  content: ''
})

const editingData = ref<ProductStorageRecord | null>(null)
const viewingData = ref<ProductStorageRecord | null>(null)

const pagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 使用组合式函数
const {
  storeData,
  getData,
  deleteData,
  listData,
  getStorageQuota,
  clearAllData: clearStorage,
  exportData,
  importData
} = useProductStorage()

// 计算属性
const filteredData = computed(() => {
  if (!searchKey.value) return storageStats.records
  
  return storageStats.records.filter(record =>
    record.key.toLowerCase().includes(searchKey.value.toLowerCase())
  )
})

// 表单验证规则
const dataRules = {
  key: [
    { required: true, message: '请输入键名', trigger: 'blur' },
    { min: 1, max: 255, message: '键名长度必须在1-255字符之间', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入数据内容', trigger: 'blur' }
  ]
}

// 方法
const loadStorageStats = async () => {
  loading.value = true
  
  try {
    const [stats, quota] = await Promise.all([
      listData(props.productId, {
        skip: (pagination.page - 1) * pagination.size,
        limit: pagination.size
      }),
      getStorageQuota(props.productId).catch(() => ({
        used_bytes: 0,
        total_bytes: 100 * 1024 * 1024,
        available_bytes: 100 * 1024 * 1024,
        usage_percentage: 0
      }))
    ])
    
    Object.assign(storageStats, stats)
    Object.assign(storageQuota, quota)
    pagination.total = stats.total_records
  } catch (error: any) {
    ElMessage.error(error.message || '加载存储统计失败')
  } finally {
    loading.value = false
  }
}

const loadStorageData = async () => {
  loadingData.value = true
  
  try {
    const stats = await listData(props.productId, {
      skip: (pagination.page - 1) * pagination.size,
      limit: pagination.size
    })
    
    Object.assign(storageStats, stats)
    pagination.total = stats.total_records
  } catch (error: any) {
    ElMessage.error(error.message || '加载数据列表失败')
  } finally {
    loadingData.value = false
  }
}

const filterData = () => {
  // 过滤逻辑在计算属性中处理
}

const viewData = async (record: ProductStorageRecord) => {
  try {
    const fullData = await getData(props.productId, record.key)
    viewingData.value = fullData
    showViewDataDialog.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取数据详情失败')
  }
}

const editData = async (record: ProductStorageRecord) => {
  try {
    const fullData = await getData(props.productId, record.key)
    
    editingData.value = fullData
    dataForm.key = fullData.key
    
    // 根据数据类型设置表单
    const data = fullData.data
    if (typeof data === 'string') {
      dataForm.dataType = 'text'
      dataForm.content = data
    } else if (typeof data === 'number') {
      dataForm.dataType = 'number'
      dataForm.content = data
    } else if (typeof data === 'boolean') {
      dataForm.dataType = 'boolean'
      dataForm.content = data
    } else {
      dataForm.dataType = 'json'
      dataForm.content = JSON.stringify(data, null, 2)
    }
    
    showCreateDataDialog.value = true
  } catch (error: any) {
    ElMessage.error(error.message || '获取数据详情失败')
  }
}

const saveData = async () => {
  if (!dataFormRef.value) return
  
  const valid = await dataFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  
  try {
    let processedData: any
    
    // 根据数据类型处理内容
    switch (dataForm.dataType) {
      case 'text':
        processedData = dataForm.content
        break
      case 'number':
        processedData = Number(dataForm.content)
        break
      case 'boolean':
        processedData = Boolean(dataForm.content)
        break
      case 'json':
        try {
          processedData = JSON.parse(dataForm.content as string)
        } catch (e) {
          ElMessage.error('JSON格式无效，请检查语法')
          return
        }
        break
      default:
        processedData = dataForm.content
    }
    
    await storeData(props.productId, dataForm.key, processedData)
    
    ElMessage.success(editingData.value ? '数据更新成功' : '数据创建成功')
    
    cancelDataEdit()
    loadStorageData()
  } catch (error: any) {
    ElMessage.error(error.message || '保存数据失败')
  } finally {
    saving.value = false
  }
}

const cancelDataEdit = () => {
  showCreateDataDialog.value = false
  editingData.value = null
  
  // 重置表单
  dataForm.key = ''
  dataForm.dataType = 'json'
  dataForm.content = ''
  
  if (dataFormRef.value) {
    dataFormRef.value.resetFields()
  }
}

const deleteDataRecord = async (record: ProductStorageRecord) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除数据记录 "${record.key}" 吗？删除后无法恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await deleteData(props.productId, record.key)
    
    ElMessage.success('数据删除成功')
    loadStorageData()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除数据失败')
    }
  }
}

const exportAllData = async () => {
  exporting.value = true
  
  try {
    const blob = await exportData(props.productId)
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `product-${props.productId}-data-${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    ElMessage.success('数据导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出数据失败')
  } finally {
    exporting.value = false
  }
}

const handleImportData = async (file: File) => {
  try {
    const result = await importData(props.productId, file)
    
    ElMessage.success(`导入成功：${result.imported_count} 条记录`)
    
    if (result.errors.length > 0) {
      ElMessage.warning(`部分数据导入失败：${result.errors.join(', ')}`)
    }
    
    loadStorageData()
  } catch (error: any) {
    ElMessage.error(error.message || '导入数据失败')
  }
  
  return false // 阻止默认上传行为
}

const clearAllData = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空所有数据吗？此操作无法恢复。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    clearing.value = true
    
    await clearStorage(props.productId)
    
    ElMessage.success('数据清空成功')
    loadStorageStats()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '清空数据失败')
    }
  } finally {
    clearing.value = false
  }
}

const copyDataContent = async () => {
  if (!viewingData.value) return
  
  try {
    const content = formatDataForDisplay(viewingData.value.data)
    await navigator.clipboard.writeText(content)
    ElMessage.success('内容已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

// 工具方法
const formatBytes = (bytes: number) => {
  if (bytes === 0) return '0 B'
  
  const k = 1024
  const sizes = ['B', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

const formatDataForDisplay = (data: any) => {
  if (typeof data === 'string') return data
  return JSON.stringify(data, null, 2)
}

const getProgressColor = (percentage: number) => {
  if (percentage < 50) return '#67c23a'
  if (percentage < 80) return '#e6a23c'
  return '#f56c6c'
}

// 生命周期
onMounted(() => {
  loadStorageStats()
})
</script>

<style scoped>
.product-data-manager {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.storage-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-bottom: 16px;
}

.stat-item {
  text-align: center;
  padding: 16px;
  background: #f9fafb;
  border-radius: 8px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.stat-value {
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.storage-progress {
  margin-top: 16px;
}

.progress-text {
  text-align: center;
  margin-top: 8px;
  font-size: 12px;
  color: #6b7280;
}

.action-buttons {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.import-upload {
  display: inline-block;
}

.data-key {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #f3f4f6;
  padding: 2px 4px;
  border-radius: 4px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.json-editor {
  width: 100%;
}

.json-help {
  margin-top: 8px;
}

.data-viewer {
  max-height: 500px;
  overflow-y: auto;
}

.data-meta {
  margin-bottom: 16px;
}

.data-content h4 {
  margin: 16px 0 8px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.data-preview {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 4px;
  padding: 12px;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  line-height: 1.4;
  max-height: 300px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-all;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .storage-stats {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .storage-stats {
    grid-template-columns: 1fr;
  }
  
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-end;
  }
  
  .action-buttons {
    flex-direction: column;
  }
}
</style>