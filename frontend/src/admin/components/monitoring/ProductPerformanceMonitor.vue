<template>
  <div class="product-performance-monitor">
    <div class="monitor-header">
      <div class="header-left">
        <h3 class="monitor-title">
          <el-icon class="performance-icon">
            <TrendCharts />
          </el-icon>
          性能监控
        </h3>
        <div class="performance-status" :class="getPerformanceStatusClass()">
          {{ getPerformanceStatusText() }}
        </div>
      </div>
      
      <div class="header-actions">
        <el-select
          v-model="selectedMetric"
          size="small"
          style="width: 140px"
          @change="handleMetricChange"
        >
          <el-option label="响应时间" value="response_time" />
          <el-option label="内存使用" value="memory_usage" />
          <el-option label="CPU使用率" value="cpu_usage" />
          <el-option label="错误率" value="error_rate" />
        </el-select>
        
        <el-button @click="exportReport" size="small" type="primary" plain>
          导出报告
        </el-button>
        
        <el-button @click="refreshData" size="small" icon="Refresh">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 实时性能指标 -->
    <div class="performance-metrics">
      <div class="metric-card response-time">
        <div class="metric-header">
          <div class="metric-icon">
            <el-icon><Timer /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-title">响应时间</div>
            <div class="metric-subtitle">平均响应延迟</div>
          </div>
        </div>
        <div class="metric-value">
          {{ performanceData.responseTime }}ms
        </div>
        <div class="metric-trend" :class="getTrendClass(performanceData.responseTimeTrend)">
          <el-icon>
            <ArrowUp v-if="performanceData.responseTimeTrend > 0" />
            <ArrowDown v-else-if="performanceData.responseTimeTrend < 0" />
            <Minus v-else />
          </el-icon>
          {{ Math.abs(performanceData.responseTimeTrend) }}%
        </div>
      </div>
      
      <div class="metric-card memory-usage">
        <div class="metric-header">
          <div class="metric-icon">
            <el-icon><Monitor /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-title">内存使用</div>
            <div class="metric-subtitle">当前内存占用</div>
          </div>
        </div>
        <div class="metric-value">
          {{ formatMemory(performanceData.memoryUsage) }}
        </div>
        <div class="metric-progress">
          <el-progress
            :percentage="getMemoryPercentage()"
            :color="getMemoryProgressColor()"
            :show-text="false"
            :stroke-width="4"
          />
        </div>
      </div>
      
      <div class="metric-card cpu-usage">
        <div class="metric-header">
          <div class="metric-icon">
            <el-icon><Cpu /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-title">CPU使用率</div>
            <div class="metric-subtitle">处理器负载</div>
          </div>
        </div>
        <div class="metric-value">
          {{ performanceData.cpuUsage }}%
        </div>
        <div class="metric-gauge">
          <div class="gauge-container">
            <div 
              class="gauge-fill"
              :style="{ 
                transform: `rotate(${(performanceData.cpuUsage / 100) * 180}deg)`,
                background: getCpuGaugeColor()
              }"
            />
          </div>
        </div>
      </div>
      
      <div class="metric-card error-rate">
        <div class="metric-header">
          <div class="metric-icon">
            <el-icon><Warning /></el-icon>
          </div>
          <div class="metric-info">
            <div class="metric-title">错误率</div>
            <div class="metric-subtitle">错误发生频率</div>
          </div>
        </div>
        <div class="metric-value" :class="getErrorRateClass()">
          {{ performanceData.errorRate }}%
        </div>
        <div class="metric-status">
          <el-tag
            :type="getErrorRateTagType()"
            size="small"
            effect="dark"
          >
            {{ getErrorRateStatus() }}
          </el-tag>
        </div>
      </div>
    </div>
    
    <!-- 性能图表 -->
    <div class="performance-charts">
      <el-row :gutter="20">
        <el-col :span="16">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <h4>性能趋势</h4>
                <el-button-group size="small">
                  <el-button
                    v-for="period in timePeriods"
                    :key="period.key"
                    :type="selectedPeriod === period.key ? 'primary' : ''"
                    @click="handlePeriodChange(period.key)"
                  >
                    {{ period.label }}
                  </el-button>
                </el-button-group>
              </div>
            </template>
            
            <div class="chart-container">
              <canvas
                ref="performanceChart"
                class="performance-chart"
                width="600"
                height="300"
              />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="8">
          <el-card class="alert-card">
            <template #header>
              <h4>性能告警</h4>
            </template>
            
            <div class="alerts-list">
              <div
                v-for="alert in performanceAlerts"
                :key="alert.id"
                class="alert-item"
                :class="getAlertClass(alert.level)"
              >
                <div class="alert-icon">
                  <el-icon>
                    <WarningFilled v-if="alert.level === 'critical'" />
                    <Warning v-else-if="alert.level === 'warning'" />
                    <InfoFilled v-else />
                  </el-icon>
                </div>
                <div class="alert-content">
                  <div class="alert-title">{{ alert.title }}</div>
                  <div class="alert-message">{{ alert.message }}</div>
                  <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
                </div>
              </div>
              
              <div v-if="performanceAlerts.length === 0" class="alerts-empty">
                <el-icon size="24" color="#10b981">
                  <CircleCheckFilled />
                </el-icon>
                <p>暂无性能告警</p>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 性能详情表格 -->
    <div class="performance-details">
      <el-card>
        <template #header>
          <div class="details-header">
            <h4>性能详情</h4>
            <div class="details-controls">
              <el-input
                v-model="searchKeyword"
                placeholder="搜索性能记录"
                size="small"
                style="width: 200px"
                clearable
              >
                <template #prefix>
                  <el-icon><Search /></el-icon>
                </template>
              </el-input>
            </div>
          </div>
        </template>
        
        <el-table
          v-loading="loading"
          :data="filteredPerformanceRecords"
          stripe
          size="small"
          max-height="400"
        >
          <el-table-column label="时间" width="160">
            <template #default="{ row }">
              {{ formatDateTime(row.timestamp) }}
            </template>
          </el-table-column>
          
          <el-table-column label="产品" width="120">
            <template #default="{ row }">
              {{ row.productName }}
            </template>
          </el-table-column>
          
          <el-table-column label="响应时间" width="100">
            <template #default="{ row }">
              <span :class="getResponseTimeClass(row.responseTime)">
                {{ row.responseTime }}ms
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="内存使用" width="100">
            <template #default="{ row }">
              {{ formatMemory(row.memoryUsage) }}
            </template>
          </el-table-column>
          
          <el-table-column label="CPU使用率" width="100">
            <template #default="{ row }">
              <span :class="getCpuUsageClass(row.cpuUsage)">
                {{ row.cpuUsage }}%
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="错误数" width="80">
            <template #default="{ row }">
              <span :class="getErrorCountClass(row.errorCount)">
                {{ row.errorCount }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column label="用户数" width="80">
            <template #default="{ row }">
              {{ row.userCount }}
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="80">
            <template #default="{ row }">
              <el-tag
                :type="getPerformanceRecordTagType(row.status)"
                size="small"
              >
                {{ getPerformanceRecordStatusText(row.status) }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="100" fixed="right">
            <template #default="{ row }">
              <el-button
                type="text"
                size="small"
                @click="showPerformanceDetails(row)"
              >
                详情
              </el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { useProductMonitoring, type ProductPerformanceLog } from '../../../frontend/composables/useProductMonitoring'
import { useProductStore } from '../../../frontend/composables/useProductStore'
import {
  TrendCharts,
  Timer,
  Monitor,
  Cpu,
  Warning,
  WarningFilled,
  InfoFilled,
  CircleCheckFilled,
  ArrowUp,
  ArrowDown,
  Minus,
  Search,
  Refresh
} from '@element-plus/icons-vue'

interface PerformanceData {
  responseTime: number
  responseTimeTrend: number
  memoryUsage: number
  cpuUsage: number
  errorRate: number
}

interface PerformanceAlert {
  id: string
  level: 'critical' | 'warning' | 'info'
  title: string
  message: string
  timestamp: Date
}

interface PerformanceRecord {
  id: string
  timestamp: Date
  productId: number
  productName: string
  responseTime: number
  memoryUsage: number
  cpuUsage: number
  errorCount: number
  userCount: number
  status: 'good' | 'warning' | 'critical'
}

interface Props {
  productId?: number
  autoRefresh?: boolean
  refreshInterval?: number
}

const props = withDefaults(defineProps<Props>(), {
  autoRefresh: true,
  refreshInterval: 10000
})

// 响应式数据
const loading = ref(false)
const selectedMetric = ref('response_time')
const selectedPeriod = ref('1h')
const searchKeyword = ref('')

const performanceData = ref<PerformanceData>({
  responseTime: 245,
  responseTimeTrend: -5.2,
  memoryUsage: 67 * 1024 * 1024,
  cpuUsage: 23,
  errorRate: 1.2
})

const performanceAlerts = ref<PerformanceAlert[]>([
  {
    id: '1',
    level: 'warning',
    title: '响应时间过长',
    message: '平均响应时间超过200ms',
    timestamp: new Date(Date.now() - 5 * 60 * 1000)
  },
  {
    id: '2',
    level: 'info',
    title: '内存使用正常',
    message: '内存使用率保持在合理范围',
    timestamp: new Date(Date.now() - 10 * 60 * 1000)
  }
])

const performanceRecords = ref<PerformanceRecord[]>([])

// 模板引用
const performanceChart = ref<HTMLCanvasElement>()

// 使用组合式函数
const { getProductPerformance } = useProductMonitoring()
const { fetchProducts } = useProductStore()
const products = ref<any[]>([])

// 定时器
let refreshTimer: number | null = null

// 配置数据
const timePeriods = [
  { key: '1h', label: '1小时' },
  { key: '6h', label: '6小时' },
  { key: '24h', label: '24小时' },
  { key: '7d', label: '7天' }
]

// 计算属性
const filteredPerformanceRecords = computed(() => {
  let filtered = performanceRecords.value
  
  if (searchKeyword.value) {
    const keyword = searchKeyword.value.toLowerCase()
    filtered = filtered.filter(record =>
      record.productName.toLowerCase().includes(keyword)
    )
  }
  
  return filtered.sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
})

// 方法
const loadPerformanceData = async () => {
  if (!props.productId) {
    performanceData.value = {
      responseTime: 0,
      responseTimeTrend: 0,
      memoryUsage: 0,
      cpuUsage: 0,
      errorRate: 0
    }
    performanceRecords.value = []
    return
  }
  
  loading.value = true
  try {
    // 加载产品列表以获取产品名称
    if (products.value.length === 0) {
      products.value = await fetchProducts({ published_only: false })
    }
    
    // 从API获取性能数据
    const apiLogs = await getProductPerformance(props.productId, {
      limit: 100
    })
    
    if (apiLogs.length === 0) {
      performanceData.value = {
        responseTime: 0,
        responseTimeTrend: 0,
        memoryUsage: 0,
        cpuUsage: 0,
        errorRate: 0
      }
      performanceRecords.value = []
      return
    }
    
    // 转换为组件使用的格式
    const records: PerformanceRecord[] = apiLogs.map((log: ProductPerformanceLog) => {
      const product = products.value.find(p => p.id === log.product_id)
      const details = log.details || {}
      
      const responseTime = details.loadTime || details.renderTime || 0
      const memoryUsage = details.memoryUsage || 0
      const cpuUsage = 0 // 后端暂无CPU使用率
      const errorCount = details.errorCount || 0
      
      let status: PerformanceRecord['status'] = 'good'
      if (responseTime > 300 || errorCount > 5) {
        status = 'critical'
      } else if (responseTime > 200 || errorCount > 2) {
        status = 'warning'
      }
      
      return {
        id: String(log.id),
        timestamp: new Date(log.timestamp),
        productId: log.product_id,
        productName: product?.title || `产品 ${log.product_id}`,
        responseTime,
        memoryUsage,
        cpuUsage,
        errorCount,
        userCount: 0, // 后端暂无用户数统计
        status
      }
    })
    
    performanceRecords.value = records
    
    // 计算平均性能指标
    if (records.length > 0) {
      const avgResponseTime = records.reduce((sum, r) => sum + r.responseTime, 0) / records.length
      const prevAvgResponseTime = records.length > 1 
        ? records.slice(1).reduce((sum, r) => sum + r.responseTime, 0) / (records.length - 1)
        : avgResponseTime
      const responseTimeTrend = prevAvgResponseTime > 0 
        ? ((avgResponseTime - prevAvgResponseTime) / prevAvgResponseTime) * 100 
        : 0
      
      const avgMemoryUsage = records.reduce((sum, r) => sum + r.memoryUsage, 0) / records.length
      const avgErrorRate = records.reduce((sum, r) => sum + r.errorCount, 0) / records.length
      
      performanceData.value = {
        responseTime: Math.round(avgResponseTime),
        responseTimeTrend: Math.round(responseTimeTrend * 10) / 10,
        memoryUsage: Math.round(avgMemoryUsage),
        cpuUsage: 0, // 后端暂无CPU使用率
        errorRate: Math.round(avgErrorRate * 10) / 10
      }
    }
    
    // 绘制图表
    await nextTick()
    drawPerformanceChart()
  } catch (error: any) {
    ElMessage.error(error.message || '加载性能数据失败')
  } finally {
    loading.value = false
  }
}

const drawPerformanceChart = () => {
  if (!performanceChart.value) return
  
  const ctx = performanceChart.value.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, 600, 300)
  
  // 使用真实的性能记录数据
  let data: Array<{ time: number; value: number }> = []
  
  if (performanceRecords.value.length > 0) {
    // 根据选定的指标获取数据
    const records = performanceRecords.value.slice(0, 24).reverse() // 取最近24条，并反转以时间顺序显示
    
    data = records.map((record, index) => {
      let value = 0
      switch (selectedMetric.value) {
        case 'response_time':
          value = record.responseTime
          break
        case 'memory_usage':
          value = record.memoryUsage / (1024 * 1024) // 转换为MB
          break
        case 'error_count':
          value = record.errorCount
          break
        default:
          value = record.responseTime
      }
      return {
        time: index,
        value: value
      }
    })
  } else {
    // 如果没有数据，显示空图表
    data = Array.from({ length: 24 }, (_, i) => ({
      time: i,
      value: 0
    }))
  }
  
  const maxValue = Math.max(...data.map(d => d.value), 1) // 确保至少为1，避免除零
  const minValue = Math.min(...data.map(d => d.value), 0)
  const range = maxValue - minValue || 1
  
  // 绘制网格
  ctx.strokeStyle = '#f3f4f6'
  ctx.lineWidth = 1
  
  for (let i = 0; i <= 5; i++) {
    const y = (300 / 5) * i
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(600, y)
    ctx.stroke()
  }
  
  // 绘制数据线
  ctx.strokeStyle = '#3b82f6'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  data.forEach((point, index) => {
    const x = (600 / (data.length - 1)) * index
    const y = 300 - ((point.value - minValue) / range) * 300
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
  
  // 绘制数据点
  ctx.fillStyle = '#3b82f6'
  data.forEach((point, index) => {
    const x = (600 / (data.length - 1)) * index
    const y = 300 - ((point.value - minValue) / range) * 300
    
    ctx.beginPath()
    ctx.arc(x, y, 3, 0, Math.PI * 2)
    ctx.fill()
  })
}

const handleMetricChange = () => {
  drawPerformanceChart()
}

const handlePeriodChange = (period: string) => {
  selectedPeriod.value = period
  loadPerformanceData()
}

const refreshData = () => {
  loadPerformanceData()
}

const exportReport = () => {
  ElMessage.success('性能报告导出功能开发中')
}

const showPerformanceDetails = (record: PerformanceRecord) => {
  ElMessage.info(`查看 ${record.productName} 的性能详情`)
}

const startAutoRefresh = () => {
  if (props.autoRefresh && !refreshTimer) {
    refreshTimer = window.setInterval(() => {
      loadPerformanceData()
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
const getPerformanceStatusClass = () => {
  const { responseTime, cpuUsage, errorRate } = performanceData.value
  
  if (responseTime > 300 || cpuUsage > 70 || errorRate > 3) {
    return 'status-critical'
  } else if (responseTime > 200 || cpuUsage > 50 || errorRate > 1) {
    return 'status-warning'
  }
  return 'status-good'
}

const getPerformanceStatusText = () => {
  const { responseTime, cpuUsage, errorRate } = performanceData.value
  
  if (responseTime > 300 || cpuUsage > 70 || errorRate > 3) {
    return '性能异常'
  } else if (responseTime > 200 || cpuUsage > 50 || errorRate > 1) {
    return '性能警告'
  }
  return '性能良好'
}

const getTrendClass = (trend: number) => {
  if (trend > 0) return 'trend-up'
  if (trend < 0) return 'trend-down'
  return 'trend-neutral'
}

const getMemoryPercentage = () => {
  const maxMemory = 512 * 1024 * 1024 // 512MB
  return Math.min((performanceData.value.memoryUsage / maxMemory) * 100, 100)
}

const getMemoryProgressColor = () => {
  const percentage = getMemoryPercentage()
  if (percentage > 80) return '#ef4444'
  if (percentage > 60) return '#f59e0b'
  return '#10b981'
}

const getCpuGaugeColor = () => {
  const usage = performanceData.value.cpuUsage
  if (usage > 70) return '#ef4444'
  if (usage > 50) return '#f59e0b'
  return '#10b981'
}

const getErrorRateClass = () => {
  const rate = performanceData.value.errorRate
  if (rate > 3) return 'error-rate-high'
  if (rate > 1) return 'error-rate-medium'
  return 'error-rate-low'
}

const getErrorRateTagType = () => {
  const rate = performanceData.value.errorRate
  if (rate > 3) return 'danger'
  if (rate > 1) return 'warning'
  return 'success'
}

const getErrorRateStatus = () => {
  const rate = performanceData.value.errorRate
  if (rate > 3) return '异常'
  if (rate > 1) return '警告'
  return '正常'
}

const getAlertClass = (level: string) => {
  return `alert-${level}`
}

const getResponseTimeClass = (time: number) => {
  if (time > 300) return 'response-time-high'
  if (time > 200) return 'response-time-medium'
  return 'response-time-low'
}

const getCpuUsageClass = (usage: number) => {
  if (usage > 70) return 'cpu-usage-high'
  if (usage > 50) return 'cpu-usage-medium'
  return 'cpu-usage-low'
}

const getErrorCountClass = (count: number) => {
  if (count > 5) return 'error-count-high'
  if (count > 2) return 'error-count-medium'
  return 'error-count-low'
}

const getPerformanceRecordTagType = (status: string) => {
  const types = {
    good: 'success',
    warning: 'warning',
    critical: 'danger'
  }
  return types[status as keyof typeof types] || 'info'
}

const getPerformanceRecordStatusText = (status: string) => {
  const texts = {
    good: '良好',
    warning: '警告',
    critical: '异常'
  }
  return texts[status as keyof typeof texts] || status
}

const formatMemory = (bytes: number) => {
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(1)}MB`
}

const formatTime = (date: Date) => {
  return date.toLocaleTimeString('zh-CN', { 
    hour: '2-digit', 
    minute: '2-digit' 
  })
}

const formatDateTime = (date: Date) => {
  return date.toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadPerformanceData()
  startAutoRefresh()
})

onUnmounted(() => {
  stopAutoRefresh()
})
</script>

<style scoped>
.product-performance-monitor {
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

.performance-icon {
  color: #3b82f6;
}

.performance-status {
  padding: 4px 12px;
  border-radius: 16px;
  font-size: 12px;
  font-weight: 500;
}

.performance-status.status-good {
  background: #dcfce7;
  color: #166534;
}

.performance-status.status-warning {
  background: #fef3c7;
  color: #92400e;
}

.performance-status.status-critical {
  background: #fecaca;
  color: #991b1b;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.performance-metrics {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 20px;
  padding: 20px;
}

.metric-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
  position: relative;
}

.metric-header {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.metric-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.response-time .metric-icon {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.memory-usage .metric-icon {
  background: linear-gradient(135deg, #10b981, #047857);
}

.cpu-usage .metric-icon {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.error-rate .metric-icon {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.metric-info {
  flex: 1;
}

.metric-title {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.metric-subtitle {
  font-size: 12px;
  color: #6b7280;
}

.metric-value {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 8px;
}

.metric-value.error-rate-high {
  color: #ef4444;
}

.metric-value.error-rate-medium {
  color: #f59e0b;
}

.metric-value.error-rate-low {
  color: #10b981;
}

.metric-trend {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 500;
}

.metric-trend.trend-up {
  color: #ef4444;
}

.metric-trend.trend-down {
  color: #10b981;
}

.metric-trend.trend-neutral {
  color: #6b7280;
}

.metric-progress {
  margin-top: 8px;
}

.metric-gauge {
  margin-top: 8px;
}

.gauge-container {
  width: 60px;
  height: 30px;
  border: 2px solid #f3f4f6;
  border-bottom: none;
  border-radius: 60px 60px 0 0;
  position: relative;
  overflow: hidden;
}

.gauge-fill {
  position: absolute;
  bottom: 0;
  left: 50%;
  width: 2px;
  height: 28px;
  transform-origin: bottom center;
  transition: transform 0.3s ease;
}

.metric-status {
  margin-top: 8px;
}

.performance-charts {
  padding: 0 20px 20px 20px;
}

.chart-card {
  height: 400px;
}

.alert-card {
  height: 400px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h4 {
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

.performance-chart {
  max-width: 100%;
  max-height: 100%;
}

.alerts-list {
  max-height: 320px;
  overflow-y: auto;
}

.alert-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  border-left: 3px solid transparent;
}

.alert-item.alert-critical {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.alert-item.alert-warning {
  background: #fffbeb;
  border-left-color: #f59e0b;
}

.alert-item.alert-info {
  background: #f0f9ff;
  border-left-color: #3b82f6;
}

.alert-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.alert-critical .alert-icon {
  color: #ef4444;
}

.alert-warning .alert-icon {
  color: #f59e0b;
}

.alert-info .alert-icon {
  color: #3b82f6;
}

.alert-content {
  flex: 1;
}

.alert-title {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.alert-message {
  font-size: 12px;
  color: #6b7280;
  margin-bottom: 4px;
}

.alert-time {
  font-size: 11px;
  color: #9ca3af;
}

.alerts-empty {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.alerts-empty p {
  margin: 8px 0 0 0;
  font-size: 14px;
}

.performance-details {
  padding: 0 20px 20px 20px;
}

.details-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.details-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.details-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.response-time-high {
  color: #ef4444;
}

.response-time-medium {
  color: #f59e0b;
}

.response-time-low {
  color: #10b981;
}

.cpu-usage-high {
  color: #ef4444;
}

.cpu-usage-medium {
  color: #f59e0b;
}

.cpu-usage-low {
  color: #10b981;
}

.error-count-high {
  color: #ef4444;
}

.error-count-medium {
  color: #f59e0b;
}

.error-count-low {
  color: #10b981;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .performance-metrics {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .monitor-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .performance-metrics {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .details-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
}
</style>