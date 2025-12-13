<template>
  <div class="product-error-monitor">
    <div class="monitor-header">
      <div class="header-left">
        <h3 class="monitor-title">
          <el-icon class="error-icon">
            <Warning />
          </el-icon>
          错误监控
        </h3>
        <el-badge :value="errorCount" :max="99" class="error-badge">
          <span class="status-text">{{ errorCount > 0 ? '有错误' : '正常' }}</span>
        </el-badge>
      </div>
      
      <div class="header-actions">
        <el-select
          v-model="selectedSeverity"
          size="small"
          placeholder="错误级别"
          style="width: 120px"
          @change="handleSeverityChange"
        >
          <el-option label="全部" value="" />
          <el-option label="严重" value="critical" />
          <el-option label="错误" value="error" />
          <el-option label="警告" value="warning" />
        </el-select>
        
        <el-button @click="clearErrors" size="small" type="danger" plain>
          清空错误
        </el-button>
        
        <el-button @click="refreshErrors" size="small" icon="Refresh">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 错误统计 -->
    <div class="error-stats">
      <div class="stat-item critical">
        <div class="stat-icon">
          <el-icon><CircleCloseFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ errorStats.critical }}</div>
          <div class="stat-label">严重错误</div>
        </div>
      </div>
      
      <div class="stat-item error">
        <div class="stat-icon">
          <el-icon><WarningFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ errorStats.error }}</div>
          <div class="stat-label">一般错误</div>
        </div>
      </div>
      
      <div class="stat-item warning">
        <div class="stat-icon">
          <el-icon><Warning /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ errorStats.warning }}</div>
          <div class="stat-label">警告</div>
        </div>
      </div>
      
      <div class="stat-item resolved">
        <div class="stat-icon">
          <el-icon><CircleCheckFilled /></el-icon>
        </div>
        <div class="stat-content">
          <div class="stat-value">{{ errorStats.resolved }}</div>
          <div class="stat-label">已解决</div>
        </div>
      </div>
    </div>
    
    <!-- 错误列表 -->
    <div class="error-list">
      <el-card>
        <template #header>
          <div class="list-header">
            <h4>错误日志</h4>
            <div class="list-controls">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索错误信息"
                size="small"
                style="width: 200px"
                clearable
                @input="handleSearch"
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>
        
        <div class="error-table">
          <el-table
            v-loading="loading"
            :data="filteredErrors"
            stripe
            size="small"
            max-height="500"
            @row-click="showErrorDetails"
          >
            <el-table-column label="级别" width="80">
              <template #default="{ row }">
                <el-tag
                  :type="getSeverityTagType(row.severity)"
                  size="small"
                  effect="dark"
                >
                  {{ getSeverityLabel(row.severity) }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="错误信息" min-width="300">
              <template #default="{ row }">
                <div class="error-message">
                  <div class="message-text">{{ row.message }}</div>
                  <div v-if="row.file" class="message-location">
                    {{ row.file }}:{{ row.line }}:{{ row.column }}
                  </div>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="产品" width="120">
              <template #default="{ row }">
                <span class="product-name">{{ row.productName || '未知' }}</span>
              </template>
            </el-table-column>
            
            <el-table-column label="用户代理" width="150">
              <template #default="{ row }">
                <div class="user-agent">
                  <el-icon class="browser-icon">
                    <Monitor />
                  </el-icon>
                  <span>{{ getBrowserName(row.userAgent) }}</span>
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="发生时间" width="160">
              <template #default="{ row }">
                <div class="error-time">
                  {{ formatDateTime(row.timestamp) }}
                </div>
              </template>
            </el-table-column>
            
            <el-table-column label="状态" width="80">
              <template #default="{ row }">
                <el-tag
                  :type="row.resolved ? 'success' : 'danger'"
                  size="small"
                >
                  {{ row.resolved ? '已解决' : '未解决' }}
                </el-tag>
              </template>
            </el-table-column>
            
            <el-table-column label="操作" width="120" fixed="right">
              <template #default="{ row }">
                <el-button-group size="small">
                  <el-button
                    type="text"
                    @click.stop="showErrorDetails(row)"
                  >
                    详情
                  </el-button>
                  <el-button
                    v-if="!row.resolved"
                    type="text"
                    @click.stop="markAsResolved(row)"
                  >
                    标记解决
                  </el-button>
                </el-button-group>
              </template>
            </el-table-column>
          </el-table>
        </div>
        
        <div v-if="filteredErrors.length === 0 && !loading" class="empty-state">
          <el-empty description="暂无错误日志" />
        </div>
      </el-card>
    </div>
    
    <!-- 错误详情弹窗 -->
    <el-dialog
      v-model="showErrorDialog"
      title="错误详情"
      width="800px"
      :close-on-click-modal="false"
    >
      <div v-if="selectedError" class="error-details">
        <div class="detail-section">
          <h4>基本信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <label>错误级别:</label>
              <el-tag :type="getSeverityTagType(selectedError.severity)" size="small">
                {{ getSeverityLabel(selectedError.severity) }}
              </el-tag>
            </div>
            <div class="detail-item">
              <label>发生时间:</label>
              <span>{{ formatDateTime(selectedError.timestamp) }}</span>
            </div>
            <div class="detail-item">
              <label>产品名称:</label>
              <span>{{ selectedError.productName || '未知' }}</span>
            </div>
            <div class="detail-item">
              <label>用户ID:</label>
              <span>{{ selectedError.userId || '匿名用户' }}</span>
            </div>
          </div>
        </div>
        
        <div class="detail-section">
          <h4>错误信息</h4>
          <div class="error-message-detail">
            {{ selectedError.message }}
          </div>
        </div>
        
        <div v-if="selectedError.stack" class="detail-section">
          <h4>堆栈跟踪</h4>
          <pre class="stack-trace">{{ selectedError.stack }}</pre>
        </div>
        
        <div v-if="selectedError.context" class="detail-section">
          <h4>上下文信息</h4>
          <pre class="context-info">{{ JSON.stringify(selectedError.context, null, 2) }}</pre>
        </div>
        
        <div class="detail-section">
          <h4>环境信息</h4>
          <div class="detail-grid">
            <div class="detail-item">
              <label>用户代理:</label>
              <span class="user-agent-full">{{ selectedError.userAgent }}</span>
            </div>
            <div class="detail-item">
              <label>页面URL:</label>
              <span>{{ selectedError.url || '未知' }}</span>
            </div>
            <div class="detail-item">
              <label>来源文件:</label>
              <span>{{ selectedError.file || '未知' }}</span>
            </div>
            <div class="detail-item">
              <label>行号:</label>
              <span>{{ selectedError.line || '未知' }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showErrorDialog = false">关闭</el-button>
          <el-button
            v-if="selectedError && !selectedError.resolved"
            type="primary"
            @click="markAsResolved(selectedError)"
          >
            标记为已解决
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Warning,
  CircleCloseFilled,
  WarningFilled,
  CircleCheckFilled,
  Search,
  Monitor,
  Refresh
} from '@element-plus/icons-vue'
import { useProductMonitoring, type ProductError as APIProductError } from '../../../frontend/composables/useProductMonitoring'
import { useProductStore } from '../../../frontend/composables/useProductStore'

interface ProductError {
  id: string
  severity: 'critical' | 'error' | 'warning'
  message: string
  stack?: string
  file?: string
  line?: number
  column?: number
  url?: string
  userAgent?: string
  userId?: string
  productId: number
  productName?: string
  timestamp: Date
  resolved: boolean
  context?: Record<string, any>
}

interface ErrorStats {
  critical: number
  error: number
  warning: number
  resolved: number
}

interface Props {
  productId?: number
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: true,
  refreshInterval: 30000
})

// 响应式数据
const loading = ref(false)
const errors = ref<ProductError[]>([])
const selectedSeverity = ref('')
const searchKeyword = ref('')
const showErrorDialog = ref(false)
const selectedError = ref<ProductError | null>(null)

// 定时器
let refreshTimer: number | null = null

// 使用组合式函数
const { getProductErrors } = useProductMonitoring()
const { fetchProducts } = useProductStore()
const products = ref<any[]>([])

// 计算属性
const errorCount = computed(() => {
  return errors.value.filter(error => !error.resolved).length
})

const errorStats = computed((): ErrorStats => {
  const stats = {
    critical: 0,
    error: 0,
    warning: 0,
    resolved: 0
  }
  
  errors.value.forEach(error => {
    if (error.resolved) {
      stats.resolved++
    } else {
      stats[error.severity]++
    }
  })
  
  return stats
})

const filteredErrors = computed(() => {
  let filtered = errors.value
  
  // 按严重程度筛选
  if (selectedSeverity.value) {
    filtered = filtered.filter(error => error.severity === selectedSeverity.value)
  }
  
  // 按关键词搜索
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(error =>
      error.message.toLowerCase().includes(keyword) ||
      error.file?.toLowerCase().includes(keyword) ||
      error.productName?.toLowerCase().includes(keyword)
    )
  }
  
  // 按时间倒序排列
  return filtered.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
})

// 方法
const loadErrors = async () => {
  if (!props.productId) {
    errors.value = []
    return
  }
  
  loading.value = true
  try {
    // 加载产品列表以获取产品名称
    if (products.value.length === 0) {
      products.value = await fetchProducts({ published_only: false })
    }
    
    // 从API获取错误日志
    const apiErrors = await getProductErrors(props.productId, {
      limit: 100
    })
    
    // 转换为组件使用的格式
    errors.value = apiErrors.map((apiError: APIProductError) => {
      const product = products.value.find(p => p.id === apiError.product_id)
      const details = apiError.details || {}
      
      // 确定严重程度
      let severity: 'critical' | 'error' | 'warning' = 'warning'
      if (apiError.log_level === 'critical' || apiError.log_level === 'error') {
        severity = 'critical'
      } else if (apiError.log_level === 'warning') {
        severity = 'warning'
      } else {
        severity = 'error'
      }
      
      return {
        id: String(apiError.id),
        severity,
        message: apiError.message || '未知错误',
        stack: details.stack || details.error_stack,
        file: details.file || details.source,
        line: details.line,
        column: details.column,
        url: details.url,
        userAgent: details.user_agent || details.userAgent,
        userId: details.user_id || details.userId,
        productId: apiError.product_id,
        productName: product?.title || `产品 ${apiError.product_id}`,
        timestamp: new Date(apiError.timestamp),
        resolved: false, // 后端暂无已解决状态
        context: details.context || details
      }
    })
  } catch (error: any) {
    ElMessage.error(error.message || '加载错误日志失败')
    errors.value = []
  } finally {
    loading.value = false
  }
}

const handleSeverityChange = () => {
  // 筛选逻辑在计算属性中处理
}

const handleSearch = () => {
  // 搜索逻辑在计算属性中处理
}

const refreshErrors = () => {
  loadErrors()
}

const clearErrors = async () => {
  try {
    // 清空本地显示的错误（实际日志在后端，这里只清空前端显示）
    errors.value = []
    ElMessage.success('错误列表已清空')
  } catch (error: any) {
    ElMessage.error(error.message || '清空错误日志失败')
  }
}

const showErrorDetails = (error: ProductError) => {
  selectedError.value = error
  showErrorDialog.value = true
}

const markAsResolved = async (error: ProductError) => {
  try {
    // 标记为已解决（仅前端状态，后端暂无此功能）
    error.resolved = true
    ElMessage.success('已标记为已解决')
    
    if (showErrorDialog.value) {
      showErrorDialog.value = false
    }
  } catch (err: any) {
    ElMessage.error(err.message || '操作失败')
  }
}

const startAutoRefresh = () => {
  if (props.autoRefresh && !refreshTimer) {
    refreshTimer = window.setInterval(() => {
      loadErrors()
    }, props.refreshInterval)
  }
}

const stopAutoRefresh = () => {
  if (refreshTimer) {
    clearInterval(refreshTimer)
    refreshTimer = null
  }
}

// 工具方法
const getSeverityTagType = (severity: string) => {
  const types = {
    critical: 'danger',
    error: 'warning',
    warning: 'info'
  }
  return types[severity as keyof typeof types] || 'info'
}

const getSeverityLabel = (severity: string) => {
  const labels = {
    critical: '严重',
    error: '错误',
    warning: '警告'
  }
  return labels[severity as keyof typeof labels] || severity
}

const getBrowserName = (userAgent: string) => {
  if (userAgent.includes('Chrome')) return 'Chrome'
  if (userAgent.includes('Firefox')) return 'Firefox'
  if (userAgent.includes('Safari')) return 'Safari'
  if (userAgent.includes('Edge')) return 'Edge'
  return '未知'
}

const formatDateTime = (date: Date) => {
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadErrors()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.product-error-monitor {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.monitor-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}

.header-left {
  display: flex;
  align-items: center;
  gap: 16px;
}

.monitor-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.error-icon {
  color: #ef4444;
}

.error-badge {
  margin-left: 8px;
}

.status-text {
  font-size: 12px;
  color: #6b7280;
  padding: 2px 8px;
  background: #f3f4f6;
  border-radius: 12px;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.error-stats {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 1px;
  background: #f3f4f6;
  margin: 0;
}

.stat-item {
  background: white;
  padding: 20px;
  display: flex;
  align-items: center;
  gap: 12px;
}

.stat-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.stat-item.critical .stat-icon {
  background: #ef4444;
}

.stat-item.error .stat-icon {
  background: #f59e0b;
}

.stat-item.warning .stat-icon {
  background: #3b82f6;
}

.stat-item.resolved .stat-icon {
  background: #10b981;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
  margin-top: 4px;
}

.error-list {
  padding: 20px;
}

.list-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.list-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.list-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.error-table {
  margin-top: 16px;
}

.error-message {
  line-height: 1.4;
}

.message-text {
  font-size: 13px;
  color: #1f2937;
  margin-bottom: 2px;
}

.message-location {
  font-size: 11px;
  color: #6b7280;
  font-family: monospace;
}

.product-name {
  font-size: 12px;
  color: #374151;
}

.user-agent {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #6b7280;
}

.browser-icon {
  font-size: 14px;
}

.error-time {
  font-size: 12px;
  color: #6b7280;
}

.empty-state {
  margin-top: 20px;
}

.error-details {
  padding: 0;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h4 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  border-bottom: 1px solid #f3f4f6;
  padding-bottom: 8px;
}

.detail-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 8px;
}

.detail-item label {
  min-width: 80px;
  font-size: 12px;
  font-weight: 500;
  color: #6b7280;
  flex-shrink: 0;
}

.detail-item span {
  font-size: 12px;
  color: #374151;
  word-break: break-all;
}

.error-message-detail {
  background: #fef2f2;
  border: 1px solid #fecaca;
  border-radius: 6px;
  padding: 12px;
  font-size: 13px;
  color: #dc2626;
  line-height: 1.4;
}

.stack-trace,
.context-info {
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  padding: 12px;
  font-size: 11px;
  color: #374151;
  line-height: 1.4;
  overflow-x: auto;
  max-height: 200px;
  overflow-y: auto;
}

.user-agent-full {
  font-family: monospace;
  font-size: 11px;
  word-break: break-all;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .monitor-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .error-stats {
    grid-template-columns: repeat(2, 1fr);
  }
  
  .list-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .detail-grid {
    grid-template-columns: 1fr;
  }
}

@media (max-width: 480px) {
  .error-stats {
    grid-template-columns: 1fr;
  }
}
</style>