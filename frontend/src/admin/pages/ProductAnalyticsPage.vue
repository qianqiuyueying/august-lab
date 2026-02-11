<template>
  <div class="product-analytics">
    <!-- 页面头部 -->
    <div class="page-header admin-page-header admin-section">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title admin-page-title">产品分析</h1>
          <p class="page-description admin-page-desc">查看产品使用数据和性能指标</p>
        </div>
        <div class="header-actions">
          <el-button :loading="diagnosing" @click="runDiagnostic">
            <el-icon><Promotion /></el-icon>
            运行诊断
          </el-button>
          <el-button :loading="securityScanning" @click="runSecurityScan">
            <el-icon><Warning /></el-icon>
            安全扫描
          </el-button>
          <el-date-picker
            v-model="dateRange"
            type="daterange"
            range-separator="至"
            start-placeholder="开始日期"
            end-placeholder="结束日期"
            @change="handleDateRangeChange"
            style="margin: 0 12px"
          />
          <el-button type="primary" @click="refreshData">
            <el-icon><Refresh /></el-icon>
            刷新数据
          </el-button>
        </div>
      </div>
    </div>

    <!-- 产品选择器 -->
    <div class="product-selector admin-section">
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
                  <div v-if="trendError" class="chart-placeholder">
                    <el-icon size="48"><Warning /></el-icon>
                    <p>{{ trendError }}</p>
                  </div>
                  <div v-else-if="!trendData.length" class="chart-placeholder">
                    <el-icon size="48"><TrendCharts /></el-icon>
                    <p>当前时间范围暂无趋势数据</p>
                    <small>可以切换产品或时间范围后重试</small>
                  </div>
                  <div v-else class="trend-bars">
                    <div
                      v-for="item in trendData"
                      :key="item.timestamp"
                      class="trend-row"
                    >
                      <div class="trend-label">{{ item.label }}</div>
                      <div class="trend-bar">
                        <div
                          class="trend-bar-fill"
                          :style="{ width: getTrendBarWidth(item.value) + '%' }"
                        />
                      </div>
                      <div class="trend-value">{{ item.value }}</div>
                    </div>
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

      <!-- 诊断与监控摘要 -->
      <div class="data-tables">
        <el-card>
          <template #header>
            <div class="table-header">
              <h3>诊断与监控摘要</h3>
            </div>
          </template>
          <div class="diagnostic-summary">
            <div class="summary-item">
              <div class="summary-label">系统状态</div>
              <div>
                <el-tag :type="getSystemStatusTag(systemStatus?.overall_status)">
                  {{ getSystemStatusText(systemStatus?.overall_status) }}
                </el-tag>
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-label">已发布产品数</div>
              <div class="summary-value">
                {{ systemStatus?.metrics?.published_products ?? 0 }}
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-label">错误率</div>
              <div class="summary-value">
                {{ systemStatus?.metrics?.error_rate?.toFixed
                  ? systemStatus.metrics.error_rate.toFixed(2)
                  : systemStatus?.metrics?.error_rate || 0
                }}%
              </div>
            </div>
            <div class="summary-item">
              <div class="summary-label">资源文件数</div>
              <div class="summary-value">
                {{ resourceStats?.files?.total_count ?? 0 }}
              </div>
            </div>
          </div>

          <div
            v-if="diagnosticResult?.recommendations?.length"
            class="recommendations-list"
          >
            <div
              v-for="(item, idx) in diagnosticResult.recommendations"
              :key="idx"
              class="recommendation-item"
            >
              {{ item }}
            </div>
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
import { ref, computed, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Refresh,
  View,
  User,
  Timer,
  Clock,
  Loading,
  TrendCharts,
  Promotion,
  Warning
} from '@element-plus/icons-vue'
import { useProductStore } from '../../frontend/composables/useProductStore'
import { useProductStats } from '../../frontend/composables/useProductStats'
import { useProductMonitoring } from '../../frontend/composables/useProductMonitoring'
import api from '../../shared/api'
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
const diagnosing = ref(false)
const securityScanning = ref(false)
const trendError = ref('')
const trendData = ref<Array<{ timestamp: string; label: string; value: number }>>([])
const systemStatus = ref<any | null>(null)
const diagnosticResult = ref<any | null>(null)
const resourceStats = ref<any | null>(null)

// 使用组合式函数
const { fetchProducts } = useProductStore()
const { getProductAnalytics, getProductLogs } = useProductStats()
const {
  getSystemStatus,
  runProductDiagnostic,
  getResourceStats
} = useProductMonitoring()

// 计算属性
const maxVisits = computed(() => {
  if (!analytics.value?.popular_times?.length) return 1
  return Math.max(...analytics.value.popular_times.map((t: any) => t.visits))
})

const maxTrendValue = computed(() => {
  if (!trendData.value.length) return 1
  return Math.max(...trendData.value.map((i) => i.value), 1)
})

// 方法
const loadProducts = async () => {
  try {
    products.value = await fetchProducts({ published_only: false })
    if (!selectedProductId.value && products.value.length > 0) {
      selectedProductId.value = products.value[0].id
      await Promise.all([
        loadAnalytics(),
        loadLogs(),
        loadTrendData(),
        loadMonitoringSummary()
      ])
    }
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

const isInDateRange = (iso: string) => {
  if (!dateRange.value) return true
  const [start, end] = dateRange.value
  const t = new Date(iso).getTime()
  return t >= start.getTime() && t <= end.getTime()
}

const loadTrendData = async () => {
  if (!selectedProductId.value) return
  trendError.value = ''
  try {
    const res = await api.get(`/products/${selectedProductId.value}/stats`)
    const stats = res.data?.stats || []
    const grouped: Record<string, { timestamp: string; label: string; value: number }> = {}

    for (const row of stats) {
      if (!row.access_time) continue
      if (!isInDateRange(row.access_time)) continue
      const d = new Date(row.access_time)
      let key = ''
      let label = ''
      if (trendPeriod.value === 'day') {
        key = `${d.getFullYear()}-${d.getMonth()}-${d.getDate()}-${d.getHours()}`
        label = `${String(d.getHours()).padStart(2, '0')}:00`
      } else if (trendPeriod.value === 'week') {
        key = d.toISOString().slice(0, 10)
        label = d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
      } else {
        key = d.toISOString().slice(0, 10)
        label = d.toLocaleDateString('zh-CN', { month: '2-digit', day: '2-digit' })
      }
      if (!grouped[key]) {
        grouped[key] = { timestamp: d.toISOString(), label, value: 0 }
      }
      grouped[key].value += 1
    }

    trendData.value = Object.values(grouped).sort(
      (a, b) => new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime()
    )
  } catch (err: any) {
    trendError.value = err.message || '加载访问趋势失败'
    trendData.value = []
  }
}

const loadMonitoringSummary = async () => {
  try {
    systemStatus.value = await getSystemStatus()
    if (selectedProductId.value) {
      resourceStats.value = await getResourceStats(selectedProductId.value)
    }
  } catch (err) {
    // 监控摘要失败不阻塞页面，其它区域仍可用
    console.warn('加载监控摘要失败:', err)
  }
}

const handleProductChange = () => {
  if (selectedProductId.value) {
    loadAnalytics()
    loadLogs()
    loadTrendData()
    loadMonitoringSummary()
  }
}

const handleDateRangeChange = () => {
  // 根据日期范围重新加载数据
  if (selectedProductId.value) {
    loadLogs()
    loadTrendData()
  }
}

const refreshData = () => {
  if (selectedProductId.value) {
    loadAnalytics()
    loadLogs()
    loadTrendData()
    loadMonitoringSummary()
  }
}

const runDiagnostic = async () => {
  if (!selectedProductId.value) return
  diagnosing.value = true
  try {
    diagnosticResult.value = await runProductDiagnostic(selectedProductId.value)
    ElMessage.success('诊断完成')
  } catch (err: any) {
    ElMessage.error(err.message || '运行诊断失败')
  } finally {
    diagnosing.value = false
  }
}

const runSecurityScan = async () => {
  if (!selectedProductId.value) return
  securityScanning.value = true
  try {
    await api.post(`/products/${selectedProductId.value}/security/scan`)
    ElMessage.success('安全扫描已触发，请在监控页查看详细结果')
  } catch (err: any) {
    ElMessage.error(err.message || '安全扫描失败')
  } finally {
    securityScanning.value = false
  }
}

const showLogDetails = (log: ProductLog) => {
  selectedLog.value = log
  showLogDetailDialog.value = true
}

const getTimeBarWidth = (visits: number) => {
  return maxVisits.value > 0 ? (visits / maxVisits.value) * 100 : 0
}

const getTrendBarWidth = (value: number) => {
  return maxTrendValue.value > 0 ? (value / maxTrendValue.value) * 100 : 0
}

// 工具方法
const getTypeLabel = (type: string) => {
  const labels = {
    static: '静态站点',
    spa: '单页应用',
    game: '游戏',
    tool: '工具'
  }
  return labels[type as keyof typeof labels] || type
}

const getTypeTagType = (type: string) => {
  const types = {
    static: 'primary',
    spa: 'success',
    game: 'danger',
    tool: 'warning'
  }
  return types[type as keyof typeof types] || 'info'
}

const getSystemStatusTag = (status?: string) => {
  if (status === 'good') return 'success'
  if (status === 'warning') return 'warning'
  if (status === 'critical') return 'danger'
  return 'info'
}

const getSystemStatusText = (status?: string) => {
  if (status === 'good') return '系统正常'
  if (status === 'warning') return '需要关注'
  if (status === 'critical') return '存在问题'
  return '未知'
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

watch(trendPeriod, () => {
  if (selectedProductId.value) {
    loadTrendData()
  }
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

.trend-bars {
  width: 100%;
  padding: 16px 20px;
}

.trend-row {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 10px;
}

.trend-label {
  width: 64px;
  font-size: 12px;
  color: #6b7280;
  text-align: right;
}

.trend-bar {
  flex: 1;
  height: 8px;
  border-radius: 4px;
  background: #f3f4f6;
  overflow: hidden;
}

.trend-bar-fill {
  height: 100%;
  background: linear-gradient(90deg, #10b981 0%, #059669 100%);
  transition: width 0.3s ease;
}

.trend-value {
  width: 40px;
  font-size: 12px;
  color: #374151;
  text-align: right;
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

.diagnostic-summary {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(180px, 1fr));
  gap: 12px;
}

.summary-item {
  padding: 10px 12px;
  border-radius: 8px;
  border: 1px solid #e5e7eb;
  background: #fafafa;
}

.summary-label {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.summary-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.recommendations-list {
  margin-top: 16px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.recommendation-item {
  padding: 10px 12px;
  border-radius: 6px;
  border-left: 3px solid #f59e0b;
  background: #fffbeb;
  color: #92400e;
  font-size: 13px;
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