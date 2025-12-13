<template>
  <div class="performance-analyzer">
    <div class="analyzer-header">
      <h3>性能分析</h3>
      <div class="header-actions">
        <el-select
          v-model="selectedTimeRange"
          size="small"
          style="width: 120px"
          @change="handleTimeRangeChange"
        >
          <el-option label="最近1小时" value="1h" />
          <el-option label="最近24小时" value="24h" />
          <el-option label="最近7天" value="7d" />
          <el-option label="最近30天" value="30d" />
        </el-select>
        
        <el-button @click="refreshData" size="small" icon="Refresh">
          刷新
        </el-button>
      </div>
    </div>
    
    <!-- 性能概览 -->
    <div class="performance-overview">
      <div class="overview-grid">
        <div class="performance-card">
          <div class="card-header">
            <h4>加载性能</h4>
            <el-icon class="card-icon load-icon">
              <Timer />
            </el-icon>
          </div>
          <div class="card-metrics">
            <div class="metric">
              <span class="metric-label">平均加载时间</span>
              <span class="metric-value">{{ performanceData.avgLoadTime }}ms</span>
            </div>
            <div class="metric">
              <span class="metric-label">首屏渲染</span>
              <span class="metric-value">{{ performanceData.firstPaint }}ms</span>
            </div>
            <div class="metric">
              <span class="metric-label">可交互时间</span>
              <span class="metric-value">{{ performanceData.timeToInteractive }}ms</span>
            </div>
          </div>
          <div class="card-trend">
            <span class="trend-label">较昨日</span>
            <span class="trend-value" :class="getTrendClass(performanceData.loadTimeTrend)">
              {{ formatTrend(performanceData.loadTimeTrend) }}
            </span>
          </div>
        </div>
        
        <div class="performance-card">
          <div class="card-header">
            <h4>资源使用</h4>
            <el-icon class="card-icon resource-icon">
              <Monitor />
            </el-icon>
          </div>
          <div class="card-metrics">
            <div class="metric">
              <span class="metric-label">内存使用</span>
              <span class="metric-value">{{ formatMemory(performanceData.memoryUsage) }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">CPU使用率</span>
              <span class="metric-value">{{ performanceData.cpuUsage }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">网络流量</span>
              <span class="metric-value">{{ formatBytes(performanceData.networkUsage) }}</span>
            </div>
          </div>
        </div>
        
        <div class="performance-card">
          <div class="card-header">
            <h4>用户体验</h4>
            <el-icon class="card-icon ux-icon">
              <User />
            </el-icon>
          </div>
          <div class="card-metrics">
            <div class="metric">
              <span class="metric-label">跳出率</span>
              <span class="metric-value">{{ performanceData.bounceRate }}%</span>
            </div>
            <div class="metric">
              <span class="metric-label">平均会话时长</span>
              <span class="metric-value">{{ formatDuration(performanceData.avgSessionDuration) }}</span>
            </div>
            <div class="metric">
              <span class="metric-label">错误率</span>
              <span class="metric-value error-rate" :class="getErrorRateClass()">
                {{ performanceData.errorRate }}%
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 性能图表 -->
    <div class="performance-charts">
      <el-row :gutter="20">
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <div class="chart-header">
                <h4>加载时间趋势</h4>
                <el-button-group size="small">
                  <el-button
                    v-for="metric in loadMetrics"
                    :key="metric.key"
                    :type="selectedLoadMetric === metric.key ? 'primary' : ''"
                    @click="selectedLoadMetric = metric.key"
                  >
                    {{ metric.label }}
                  </el-button>
                </el-button-group>
              </div>
            </template>
            
            <div class="chart-container">
              <canvas
                ref="loadTimeChart"
                class="performance-chart"
                width="400"
                height="200"
              />
            </div>
          </el-card>
        </el-col>
        
        <el-col :span="12">
          <el-card class="chart-card">
            <template #header>
              <h4>资源使用分布</h4>
            </template>
            
            <div class="resource-distribution">
              <div class="resource-item">
                <div class="resource-label">JavaScript</div>
                <div class="resource-bar">
                  <div 
                    class="resource-fill js-fill"
                    :style="{ width: getResourcePercentage('js') + '%' }"
                  />
                </div>
                <div class="resource-value">{{ formatBytes(resourceUsage.js) }}</div>
              </div>
              
              <div class="resource-item">
                <div class="resource-label">CSS</div>
                <div class="resource-bar">
                  <div 
                    class="resource-fill css-fill"
                    :style="{ width: getResourcePercentage('css') + '%' }"
                  />
                </div>
                <div class="resource-value">{{ formatBytes(resourceUsage.css) }}</div>
              </div>
              
              <div class="resource-item">
                <div class="resource-label">图片</div>
                <div class="resource-bar">
                  <div 
                    class="resource-fill image-fill"
                    :style="{ width: getResourcePercentage('images') + '%' }"
                  />
                </div>
                <div class="resource-value">{{ formatBytes(resourceUsage.images) }}</div>
              </div>
              
              <div class="resource-item">
                <div class="resource-label">其他</div>
                <div class="resource-bar">
                  <div 
                    class="resource-fill other-fill"
                    :style="{ width: getResourcePercentage('other') + '%' }"
                  />
                </div>
                <div class="resource-value">{{ formatBytes(resourceUsage.other) }}</div>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 性能建议 -->
    <div class="performance-suggestions">
      <el-card>
        <template #header>
          <h4>性能优化建议</h4>
        </template>
        
        <div class="suggestions-list">
          <div
            v-for="suggestion in suggestions"
            :key="suggestion.id"
            class="suggestion-item"
            :class="getSuggestionClass(suggestion.priority)"
          >
            <div class="suggestion-icon">
              <el-icon>
                <WarningFilled v-if="suggestion.priority === 'high'" />
                <Warning v-else-if="suggestion.priority === 'medium'" />
                <InfoFilled v-else />
              </el-icon>
            </div>
            
            <div class="suggestion-content">
              <h5 class="suggestion-title">{{ suggestion.title }}</h5>
              <p class="suggestion-description">{{ suggestion.description }}</p>
              <div v-if="suggestion.impact" class="suggestion-impact">
                预期提升: {{ suggestion.impact }}
              </div>
            </div>
            
            <div class="suggestion-actions">
              <el-button size="small" type="text" @click="showSuggestionDetails(suggestion)">
                查看详情
              </el-button>
            </div>
          </div>
          
          <div v-if="suggestions.length === 0" class="suggestions-empty">
            <el-icon size="32" color="#10b981">
              <SuccessFilled />
            </el-icon>
            <p>性能表现良好，暂无优化建议</p>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick } from 'vue'
import { 
  Timer, 
  Monitor, 
  User, 
  Refresh,
  WarningFilled,
  Warning,
  InfoFilled,
  SuccessFilled
} from '@element-plus/icons-vue'

interface PerformanceData {
  avgLoadTime: number
  firstPaint: number
  timeToInteractive: number
  memoryUsage: number
  cpuUsage: number
  networkUsage: number
  bounceRate: number
  avgSessionDuration: number
  errorRate: number
  loadTimeTrend: number
}

interface ResourceUsage {
  js: number
  css: number
  images: number
  other: number
}

interface PerformanceSuggestion {
  id: string
  title: string
  description: string
  priority: 'high' | 'medium' | 'low'
  impact?: string
  details?: string
}

interface Props {
  productId?: number
}

const props = defineProps<Props>()

// 响应式数据
const selectedTimeRange = ref('24h')
const selectedLoadMetric = ref('loadTime')
const performanceData = ref<PerformanceData>({
  avgLoadTime: 1250,
  firstPaint: 800,
  timeToInteractive: 1800,
  memoryUsage: 45 * 1024 * 1024,
  cpuUsage: 15,
  networkUsage: 2.5 * 1024 * 1024,
  bounceRate: 25,
  avgSessionDuration: 180,
  errorRate: 2.1,
  loadTimeTrend: -5.2
})

const resourceUsage = ref<ResourceUsage>({
  js: 850 * 1024,
  css: 120 * 1024,
  images: 1.2 * 1024 * 1024,
  other: 300 * 1024
})

const suggestions = ref<PerformanceSuggestion[]>([
  {
    id: '1',
    title: '压缩JavaScript文件',
    description: '检测到未压缩的JavaScript文件，建议启用Gzip压缩',
    priority: 'high',
    impact: '减少30%加载时间'
  },
  {
    id: '2',
    title: '优化图片格式',
    description: '部分图片可以转换为WebP格式以减少文件大小',
    priority: 'medium',
    impact: '减少20%网络传输'
  }
])

// 模板引用
const loadTimeChart = ref<HTMLCanvasElement>()

// 配置数据
const loadMetrics = [
  { key: 'loadTime', label: '加载时间' },
  { key: 'firstPaint', label: '首屏' },
  { key: 'interactive', label: '可交互' }
]

// 计算属性
const totalResourceSize = computed(() => {
  return Object.values(resourceUsage.value).reduce((sum, size) => sum + size, 0)
})

// 方法
const handleTimeRangeChange = () => {
  refreshData()
}

const refreshData = async () => {
  // 模拟刷新数据
  await new Promise(resolve => setTimeout(resolve, 500))
  
  // 生成模拟数据
  performanceData.value = {
    ...performanceData.value,
    avgLoadTime: Math.floor(Math.random() * 500) + 1000,
    errorRate: Math.random() * 5,
    loadTimeTrend: (Math.random() - 0.5) * 20
  }
  
  drawLoadTimeChart()
}

const drawLoadTimeChart = async () => {
  await nextTick()
  
  if (!loadTimeChart.value) return
  
  const ctx = loadTimeChart.value.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, 400, 200)
  
  // 绘制简单的折线图
  const data = Array.from({ length: 24 }, (_, i) => ({
    time: i,
    value: Math.floor(Math.random() * 500) + 800
  }))
  
  const maxValue = Math.max(...data.map(d => d.value))
  const minValue = Math.min(...data.map(d => d.value))
  const range = maxValue - minValue || 1
  
  // 绘制网格
  ctx.strokeStyle = '#f3f4f6'
  ctx.lineWidth = 1
  
  for (let i = 0; i <= 4; i++) {
    const y = (200 / 4) * i
    ctx.beginPath()
    ctx.moveTo(0, y)
    ctx.lineTo(400, y)
    ctx.stroke()
  }
  
  // 绘制数据线
  ctx.strokeStyle = '#3b82f6'
  ctx.lineWidth = 2
  ctx.beginPath()
  
  data.forEach((point, index) => {
    const x = (400 / (data.length - 1)) * index
    const y = 200 - ((point.value - minValue) / range) * 200
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
}

const getResourcePercentage = (type: keyof ResourceUsage) => {
  return (resourceUsage.value[type] / totalResourceSize.value) * 100
}

const getTrendClass = (trend: number) => {
  if (trend > 0) return 'trend-up'
  if (trend < 0) return 'trend-down'
  return 'trend-neutral'
}

const getErrorRateClass = () => {
  if (performanceData.value.errorRate > 3) return 'high'
  if (performanceData.value.errorRate > 1) return 'medium'
  return 'low'
}

const getSuggestionClass = (priority: string) => {
  return `suggestion-${priority}`
}

const showSuggestionDetails = (suggestion: PerformanceSuggestion) => {
  // 显示建议详情
  console.log('显示建议详情:', suggestion)
}

// 格式化方法
const formatMemory = (bytes: number) => {
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(1)}MB`
}

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
}

const formatDuration = (seconds: number) => {
  const minutes = Math.floor(seconds / 60)
  const remainingSeconds = seconds % 60
  return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
}

const formatTrend = (trend: number) => {
  const sign = trend > 0 ? '+' : ''
  return `${sign}${trend.toFixed(1)}%`
}

// 生命周期
onMounted(() => {
  drawLoadTimeChart()
})
</script>

<style scoped>
.performance-analyzer {
  padding: 0;
}

.analyzer-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 24px;
}

.analyzer-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.header-actions {
  display: flex;
  gap: 12px;
  align-items: center;
}

.performance-overview {
  margin-bottom: 24px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 20px;
}

.performance-card {
  background: white;
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.card-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.card-icon {
  font-size: 20px;
}

.card-icon.load-icon {
  color: #3b82f6;
}

.card-icon.resource-icon {
  color: #10b981;
}

.card-icon.ux-icon {
  color: #f59e0b;
}

.card-metrics {
  margin-bottom: 12px;
}

.metric {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.metric-label {
  font-size: 12px;
  color: #6b7280;
}

.metric-value {
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.metric-value.error-rate.high {
  color: #ef4444;
}

.metric-value.error-rate.medium {
  color: #f59e0b;
}

.metric-value.error-rate.low {
  color: #10b981;
}

.card-trend {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding-top: 12px;
  border-top: 1px solid #f3f4f6;
}

.trend-label {
  font-size: 12px;
  color: #6b7280;
}

.trend-value {
  font-size: 12px;
  font-weight: 600;
}

.trend-value.trend-up {
  color: #ef4444;
}

.trend-value.trend-down {
  color: #10b981;
}

.trend-value.trend-neutral {
  color: #6b7280;
}

.performance-charts {
  margin-bottom: 24px;
}

.chart-card {
  height: 320px;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-header h4 {
  margin: 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.chart-container {
  height: 240px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.performance-chart {
  max-width: 100%;
  max-height: 100%;
}

.resource-distribution {
  padding: 20px 0;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 16px;
}

.resource-label {
  width: 80px;
  font-size: 12px;
  color: #374151;
  font-weight: 500;
}

.resource-bar {
  flex: 1;
  height: 8px;
  background: #f3f4f6;
  border-radius: 4px;
  overflow: hidden;
}

.resource-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.resource-fill.js-fill {
  background: #f59e0b;
}

.resource-fill.css-fill {
  background: #3b82f6;
}

.resource-fill.image-fill {
  background: #10b981;
}

.resource-fill.other-fill {
  background: #8b5cf6;
}

.resource-value {
  width: 60px;
  font-size: 12px;
  color: #6b7280;
  text-align: right;
}

.performance-suggestions {
  margin-bottom: 24px;
}

.suggestions-list {
  padding: 0;
}

.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 16px;
  border-radius: 6px;
  margin-bottom: 12px;
  border-left: 4px solid transparent;
}

.suggestion-item.suggestion-high {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.suggestion-item.suggestion-medium {
  background: #fffbeb;
  border-left-color: #f59e0b;
}

.suggestion-item.suggestion-low {
  background: #f0f9ff;
  border-left-color: #3b82f6;
}

.suggestion-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.suggestion-high .suggestion-icon {
  color: #ef4444;
}

.suggestion-medium .suggestion-icon {
  color: #f59e0b;
}

.suggestion-low .suggestion-icon {
  color: #3b82f6;
}

.suggestion-content {
  flex: 1;
}

.suggestion-title {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.suggestion-description {
  margin: 0 0 8px 0;
  font-size: 13px;
  color: #6b7280;
  line-height: 1.4;
}

.suggestion-impact {
  font-size: 12px;
  color: #10b981;
  font-weight: 500;
}

.suggestion-actions {
  flex-shrink: 0;
}

.suggestions-empty {
  text-align: center;
  padding: 40px 20px;
  color: #6b7280;
}

.suggestions-empty p {
  margin: 8px 0 0 0;
  font-size: 14px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analyzer-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .suggestion-item {
    flex-direction: column;
    gap: 8px;
  }
}
</style>