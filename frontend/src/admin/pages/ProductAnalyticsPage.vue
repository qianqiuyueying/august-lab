<template>
  <div class="product-analytics">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">产品分析</h1>
          <p class="page-description">查看产品使用数据和性能指标</p>
        </div>
        <div class="header-actions">
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleDateRangeChange"
            style="margin-right: 12px"
          />
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 产品选择器 -->
    <div class="product-selector">
      <el-card shadow="never">
        <div class="selector-content">
          <label class="selector-label">选择产品:</label>
          <el-select
            v-model="selectedProductId"
            placeholder="请选择要分析的产品"
            @change="handleProductChange"
            style="width: 300px"
          >
            <el-option
              v-for="product in products"
              :key="product.id"
              :label="product.title"
              :value="product.id"
            >
              <div class="product-option">
                <span class="product-title">{{ product.title }}</span>
                <el-tag :type="getTypeTagType(product.product_type)" size="small">
                  {{ getTypeLabel(product.product_type) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
        </div>
      </el-card>
    </div>

    <!-- 分析数据 -->
    <div v-if="selectedProductId && analytics" class="analytics-content">
      <!-- 概览卡片 -->
      <div class="overview-cards">
        <el-row :gutter="20">
          <el-col :span="6">
            <el-card class="metric-card">
              <div class="metric-content">
                <div class="metric-icon visits">
                  <el-icon size="24"><View /></el-icon>
                </div>
                <div class="metric-info">
                  <div class="metric-value">{{ analytics.total_visits }}</div>
                  <div class="metric-label">总访问次数</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card">
              <div class="metric-content">
                <div class="metric-icon users">
                  <el-icon size="24"><User /></el-icon>
                </div>
                <div class="metric-info">
                  <div class="metric-value">{{ analytics.unique_visitors }}</div>
                  <div class="metric-label">独立访客</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card">
              <div class="metric-content">
                <div class="metric-icon duration">
                  <el-icon size="24"><Timer /></el-icon>
                </div>
                <div class="metric-info">
                  <div class="metric-value">{{ formatDuration(analytics.average_duration) }}</div>
                  <div class="metric-label">平均使用时长</div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <el-col :span="6">
            <el-card class="metric-card">
              <div class="metric-content">
                <div class="metric-icon last-access">
                  <el-icon size="24"><Clock /></el-icon>
                </div>
                <div class="metric-info">
                  <div class="metric-value">{{ formatLastAccess(analytics.last_access) }}</div>
                  <div class="metric-label">最后访问</div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 图表区域 -->
      <div class="charts-section">
        <el-row :gutter="20">
          <!-- 访问趋势图 -->
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <div class="chart-header">
                  <h3>访问趋势</h3>
                  <el-button-group size="small">
                    <el-button 
                      :type="trendPeriod === 'day' ? 'primary' : ''"
                      @click="trendPeriod = 'day'"
                    >
                      日
                    </el-button>
                    <el-button 
                      :type="trendPeriod === 'week' ? 'primary' : ''"
                      @click="trendPeriod = 'week'"
                    >
                      周
                    </el-button>
                    <el-button 
                      :type="trendPeriod === 'month' ? 'primary' : ''"
                      @click="trendPeriod = 'month'"
                    >
                      月
                    </el-button>
                  </el-button-group>
                </div>
              </template>
              <div class="chart-container">
                <div v-if="loading" class="chart-loading">
                  <el-icon class="is-loading"><Loading /></el-icon>
                  <span>加载中...</span>
                </div>
                <div v-else class="trend-chart">
                  <!-- 这里可以集成图表库如ECharts -->
                  <div class="chart-placeholder">
                    <el-icon size="48"><TrendCharts /></el-icon>
                    <p>访问趋势图表</p>
                    <small>集成图表库后显示</small>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
          
          <!-- 热门时间分布 -->
          <el-col :span="12">
            <el-card class="chart-card">
              <template #header>
                <h3>访问时间分布</h3>
              </template>
              <div class="chart-container">
                <div class="time-distribution">
                  <div 
                    v-for="time in analytics.popular_times" 
                    :key="time.hour"
                    class="time-bar"
                  >
                    <div class="time-label">{{ time.hour }}:00</div>
                    <div class="time-progress">
                      <div 
                        class="time-fill"
                        :style="{ width: getTimeBarWidth(time.visits) + '%' }"
                      />
                    </div>
                    <div class="time-value">{{ time.visits }}</div>
                  </div>
                </div>
              </div>
            </el-card>
          </el-col>
        </el-row>
      </div>

      <!-- 详细数据表格 -->
      <div class="data-tables">
        <el-card>
          <template #header>
            <div class="table-header">
              <h3>详细数据</h3>
              <el-button-group size="small">
                <el-button 
                  :type="activeTab === 'logs' ? 'primary' : ''"
                  @click="activeTab = 'logs'"
                >
                  访问日志
                </el-button>
                <el-button 
                  :type="activeTab === 'errors' ? 'primary' : ''"
                  @click="activeTab = 'errors'"
                >
                  错误日志
                </el-button>
                <el-button 
                  :type="activeTab === 'performance' ? 'primary' : ''"
                  @click="activeTab = 'performance'"
                >
                  性能数据
                </el-button>
              </el-button-group>
            </div>
          </template>
          
          <!-- 访问日志表格 -->
          <div v-if="activeTab === 'logs'" class="data-table">
            <el-table
              v-loading="logsLoading"
              :data="logs"
              stripe
              size="small"
              max-height="400"
            >
              <el-table-column label="时间" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.timestamp) }}
                </template>
              </el-table-column>
              <el-table-column label="类型" width="100">
                <template #default="{ row }">
                  <el-tag :type="getLogTypeTag(row.log_type)" size="small">
                    {{ row.log_type }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="级别" width="80">
                <template #default="{ row }">
                  <el-tag :type="getLogLevelTag(row.log_level)" size="small">
                    {{ row.log_level }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column label="消息" min-width="200">
                <template #default="{ row }">
                  {{ row.message }}
                </template>
              </el-table-column>
              <el-table-column label="详情" width="100">
                <template #default="{ row }">
                  <el-button 
                    v-if="row.details"
                    type="text" 
                    size="small"
                    @click="showLogDetails(row)"
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <!-- 错误日志表格 -->
          <div v-else-if="activeTab === 'errors'" class="data-table">
            <el-table
              v-loading="logsLoading"
              :data="errorLogs"
              stripe
              size="small"
              max-height="400"
            >
              <el-table-column label="时间" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.timestamp) }}
                </template>
              </el-table-column>
              <el-table-column label="错误信息" min-width="300">
                <template #default="{ row }">
                  <div class="error-message">
                    {{ row.message }}
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="操作" width="100">
                <template #default="{ row }">
                  <el-button 
                    type="text" 
                    size="small"
                    @click="showLogDetails(row)"
                  >
                    查看详情
                  </el-button>
                </template>
              </el-table-column>
            </el-table>
          </div>
          
          <!-- 性能数据表格 -->
          <div v-else-if="activeTab === 'performance'" class="data-table">
            <el-table
              v-loading="logsLoading"
              :data="performanceLogs"
              stripe
              size="small"
              max-height="400"
            >
              <el-table-column label="时间" width="180">
                <template #default="{ row }">
                  {{ formatDateTime(row.timestamp) }}
                </template>
              </el-table-column>
              <el-table-column label="加载时间" width="100">
                <template #default="{ row }">
                  {{ row.details?.loadTime || '-' }}ms
                </template>
              </el-table-column>
              <el-table-column label="渲染时间" width="100">
                <template #default="{ row }">
                  {{ row.details?.renderTime || '-' }}ms
                </template>
              </el-table-column>
              <el-table-column label="内存使用" width="100">
                <template #default="{ row }">
                  {{ formatMemory(row.details?.memoryUsage) }}
                </template>
              </el-table-column>
              <el-table-column label="错误数" width="80">
                <template #default="{ row }">
                  {{ row.details?.errorCount || 0 }}
                </template>
              </el-table-column>
            </el-table>
          </div>
        </el-card>
      </div>
    </div>

    <!-- 空状态 -->
    <div v-else-if="!selectedProductId" class="empty-state">
      <el-empty description="请选择一个产品查看分析数据" />
    </div>

    <!-- 日志详情弹窗 -->
    <el-dialog
      v-model="showLogDetailDialog"
      title="日志详情"
      width="600px"
    >
      <div v-if="selectedLog" class="log-detail">
        <div class="detail-item">
          <label>时间:</label>
          <span>{{ formatDateTime(selectedLog.timestamp) }}</span>
        </div>
        <div class="detail-item">
          <label>类型:</label>
          <el-tag :type="getLogTypeTag(selectedLog.log_type)" size="small">
            {{ selectedLog.log_type }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>级别:</label>
          <el-tag :type="getLogLevelTag(selectedLog.log_level)" size="small">
            {{ selectedLog.log_level }}
          </el-tag>
        </div>
        <div class="detail-item">
          <label>消息:</label>
          <span>{{ selectedLog.message }}</span>
        </div>
        <div v-if="selectedLog.details" class="detail-item">
          <label>详细信息:</label>
          <pre class="detail-json">{{ JSON.stringify(selectedLog.details, null, 2) }}</pre>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  View,
  User,
  Timer,
  Clock,
  Loading,
  TrendCharts
} from '@element-plus/icons-vue'
import { useProductStore } from '../../frontend/composables/useProductStore'
import { useProductStats } from '../../frontend/composables/useProductStats'
import type { Product, ProductAnalytics, ProductLog } from '../../shared/types'

// 响应式数据
const loading = ref(false)
const logsLoading = ref(false)
const products = ref<Product[]>([])
const selectedProductId = ref<number | null>(null)
const analytics = ref<ProductAnalytics | null>(null)
const logs = ref<ProductLog[]>([])
const errorLogs = ref<ProductLog[]>([])
const performanceLogs = ref<ProductLog[]>([])
const dateRange = ref<[Date, Date] | null>(null)
const trendPeriod = ref<'day' | 'week' | 'month'>('day')
const activeTab = ref<'logs' | 'errors' | 'performance'>('logs')
const showLogDetailDialog = ref(false)
const selectedLog = ref<ProductLog | null>(null)

// 使用组合式函数
const { fetchProducts } = useProductStore()
const { getProductAnalytics, getProductLogs } = useProductStats()

// 计算属性
const maxVisits = computed(() => {
  if (!analytics.value?.popular_times?.length) return 1
  return Math.max(...analytics.value.popular_times.map((t: any) => t.visits))
})

// 方法
const loadProducts = async () => {
  try {
    products.value = await fetchProducts({ published_only: false })
  } catch (error: any) {
    ElMessage.error(error.message || '加载产品列表失败')
  }
}

const loadAnalytics = async () => {
  if (!selectedProductId.value) return
  
  loading.value = true
  try {
    analytics.value = await getProductAnalytics(selectedProductId.value)
  } catch (error: any) {
    ElMessage.error(error.message || '加载分析数据失败')
  } finally {
    loading.value = false
  }
}

const loadLogs = async () => {
  if (!selectedProductId.value) return
  
  logsLoading.value = true
  try {
    // 加载所有日志
    const allLogs = await getProductLogs(selectedProductId.value, { limit: 100 })
    logs.value = allLogs
    
    // 筛选错误日志
    errorLogs.value = allLogs.filter((log: ProductLog) => log.log_type === 'error')
    
    // 筛选性能日志
    performanceLogs.value = allLogs.filter((log: ProductLog) => log.log_type === 'performance')
  } catch (error: any) {
    ElMessage.error(error.message || '加载日志数据失败')
  } finally {
    logsLoading.value = false
  }
}

const handleProductChange = () => {
  if (selectedProductId.value) {
    loadAnalytics()
    loadLogs()
  }
}

const handleDateRangeChange = () => {
  // 根据日期范围重新加载数据
  if (selectedProductId.value) {
    loadAnalytics()
    loadLogs()
  }
}

const refreshData = () => {
  if (selectedProductId.value) {
    loadAnalytics()
    loadLogs()
  }
}

const showLogDetails = (log: ProductLog) => {
  selectedLog.value = log
  showLogDetailDialog.value = true
}

const getTimeBarWidth = (visits: number) => {
  return maxVisits.value > 0 ? (visits / maxVisits.value) * 100 : 0
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

const getLogTypeTag = (type: string) => {
  const types = {
    access: 'primary',
    error: 'danger',
    performance: 'success',
    security: 'warning'
  }
  return types[type as keyof typeof types] || 'info'
}

const getLogLevelTag = (level: string) => {
  const levels = {
    debug: 'info',
    info: 'primary',
    warning: 'warning',
    error: 'danger'
  }
  return levels[level as keyof typeof levels] || 'info'
}

const formatDuration = (seconds: number) => {
  if (seconds < 60) return `${Math.round(seconds)}秒`
  if (seconds < 3600) return `${Math.round(seconds / 60)}分钟`
  return `${Math.round(seconds / 3600)}小时`
}

const formatLastAccess = (dateString?: string) => {
  if (!dateString) return '从未访问'
  
  const date = new Date(dateString)
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

const formatDateTime = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN')
}

const formatMemory = (bytes?: number) => {
  if (!bytes) return '-'
  
  const units = ['B', 'KB', 'MB', 'GB']
  let size = bytes
  let unitIndex = 0
  
  while (size >= 1024 && unitIndex < units.length - 1) {
    size /= 1024
    unitIndex++
  }
  
  return `${size.toFixed(1)}${units[unitIndex]}`
}

// 生命周期
onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.product-analytics {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 8px 0;
}

.page-description {
  color: #6b7280;
  margin: 0;
}

.header-actions {
  display: flex;
  align-items: center;
}

.product-selector {
  margin-bottom: 24px;
}

.selector-content {
  display: flex;
  align-items: center;
  gap: 12px;
}

.selector-label {
  font-weight: 500;
  color: #374151;
}

.product-option {
  display: flex;
  justify-content: space-between;
  align-items: center;
  width: 100%;
}

.product-title {
  flex: 1;
}

.overview-cards {
  margin-bottom: 24px;
}

.metric-card {
  height: 120px;
}

.metric-content {
  display: flex;
  align-items: center;
  gap: 16px;
  height: 100%;
}

.metric-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.metric-icon.visits {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.metric-icon.users {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
}

.metric-icon.duration {
  background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
}

.metric-icon.last-access {
  background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);
}

.metric-info {
  flex: 1;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  line-height: 1.2;
}

.metric-label {
  font-size: 14px;
  color: #6b7280;
  margin-top: 4px;
}

.charts-section {
  margin-bottom: 24px;
}

.chart-card {
  height: 400px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.chart-container {
  height: 320px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-loading {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #6b7280;
}

.chart-placeholder {
  text-align: center;
  color: #9ca3af;
}

.chart-placeholder p {
  margin: 12px 0 4px 0;
  font-size: 16px;
  font-weight: 500;
}

.chart-placeholder small {
  font-size: 12px;
}

.time-distribution {
  width: 100%;
  padding: 20px;
}

.time-bar {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.time-label {
  width: 60px;
  font-size: 12px;
  color: #6b7280;
  text-align: right;
}

.time-progress {
  flex: 1;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.time-fill {
  height: 100%;
  background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
  transition: width 0.3s ease;
}

.time-value {
  width: 40px;
  font-size: 12px;
  color: #374151;
  font-weight: 500;
  text-align: right;
}

.data-tables {
  margin-bottom: 24px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.table-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.data-table {
  margin-top: 16px;
}

.error-message {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 12px;
  color: #dc2626;
}

.empty-state {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}

.log-detail {
  padding: 0;
}

.detail-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 16px;
}

.detail-item label {
  min-width: 80px;
  font-weight: 500;
  color: #374151;
}

.detail-json {
  background: #f3f4f6;
  padding: 12px;
  border-radius: 6px;
  font-size: 12px;
  color: #374151;
  overflow-x: auto;
  max-height: 300px;
  overflow-y: auto;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .product-analytics {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .selector-content {
    flex-direction: column;
    align-items: stretch;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .table-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>