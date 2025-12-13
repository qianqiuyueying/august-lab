<template>
  <div class="product-metrics-chart">
    <div class="chart-header">
      <h3 class="chart-title">{{ title }}</h3>
      <div class="chart-controls">
        <el-select
          v-model="selectedMetric"
          size="small"
          style="width: 120px"
          @change="handleMetricChange"
        >
          <el-option
            v-for="metric in availableMetrics"
            :key="metric.key"
            :label="metric.label"
            :value="metric.key"
          />
        </el-select>
        
        <el-button-group size="small" class="period-selector">
          <el-button
            v-for="period in periods"
            :key="period.key"
            :type="selectedPeriod === period.key ? 'primary' : ''"
            @click="handlePeriodChange(period.key)"
          >
            {{ period.label }}
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <div class="chart-container" :style="{ height: chartHeight + 'px' }">
      <div v-if="loading" class="chart-loading">
        <el-icon class="is-loading" size="32">
          <Loading />
        </el-icon>
        <span>加载图表数据...</span>
      </div>
      
      <div v-else-if="error" class="chart-error">
        <el-icon size="32" color="#f56565">
          <WarningFilled />
        </el-icon>
        <p>{{ error }}</p>
        <el-button size="small" @click="retry">重试</el-button>
      </div>
      
      <div v-else-if="!chartData || chartData.length === 0" class="chart-empty">
        <el-icon size="32" color="#9ca3af">
          <DataLine />
        </el-icon>
        <p>暂无数据</p>
      </div>
      
      <canvas
        v-else
        ref="chartCanvas"
        class="chart-canvas"
        :width="canvasWidth"
        :height="canvasHeight"
      />
    </div>
    
    <div v-if="showLegend && chartData?.length" class="chart-legend">
      <div class="legend-items">
        <div
          v-for="(item, index) in legendItems"
          :key="index"
          class="legend-item"
          @click="toggleSeries(index)"
        >
          <div
            class="legend-color"
            :style="{ backgroundColor: item.color, opacity: item.visible ? 1 : 0.3 }"
          />
          <span class="legend-label" :class="{ disabled: !item.visible }">
            {{ item.label }}
          </span>
          <span class="legend-value">{{ item.value }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted, nextTick } from 'vue'
import { Loading, WarningFilled, DataLine } from '@element-plus/icons-vue'

interface ChartDataPoint {
  timestamp: string
  value: number
  label?: string
  metadata?: Record<string, any>
}

interface MetricConfig {
  key: string
  label: string
  color: string
  format?: (value: number) => string
}

interface PeriodConfig {
  key: string
  label: string
  days: number
}

interface LegendItem {
  label: string
  color: string
  value: string
  visible: boolean
}

interface Props {
  title?: string
  data?: ChartDataPoint[]
  loading?: boolean
  error?: string
  chartHeight?: number
  showLegend?: boolean
  chartType?: 'line' | 'bar' | 'area'
  metrics?: MetricConfig[]
  defaultMetric?: string
  defaultPeriod?: string
}

interface Emits {
  (e: 'metric-change', metric: string): void
  (e: 'period-change', period: string): void
  (e: 'retry'): void
}

const props = withDefaults(defineProps<Props>(), {
  title: '数据图表',
  chartHeight: 300,
  showLegend: true,
  chartType: 'line',
  defaultMetric: 'visits',
  defaultPeriod: 'week'
})

const emit = defineEmits<Emits>()

// 模板引用
const chartCanvas = ref<HTMLCanvasElement>()

// 响应式数据
const selectedMetric = ref(props.defaultMetric)
const selectedPeriod = ref(props.defaultPeriod)
const canvasWidth = ref(800)
const canvasHeight = ref(300)
const visibleSeries = ref<boolean[]>([])

// 默认配置
const defaultMetrics: MetricConfig[] = [
  { key: 'visits', label: '访问量', color: '#3b82f6' },
  { key: 'users', label: '用户数', color: '#10b981' },
  { key: 'duration', label: '使用时长', color: '#f59e0b', format: (v) => `${Math.round(v)}s` },
  { key: 'errors', label: '错误数', color: '#ef4444' }
]

const defaultPeriods: PeriodConfig[] = [
  { key: 'day', label: '今日', days: 1 },
  { key: 'week', label: '本周', days: 7 },
  { key: 'month', label: '本月', days: 30 },
  { key: 'quarter', label: '本季', days: 90 }
]

// 计算属性
const availableMetrics = computed(() => props.metrics || defaultMetrics)
const periods = computed(() => defaultPeriods)

const chartData = computed(() => {
  if (!props.data) return []
  return props.data.filter((_, index) => visibleSeries.value[index] !== false)
})

const legendItems = computed((): LegendItem[] => {
  if (!props.data?.length) return []
  
  const metric = availableMetrics.value.find(m => m.key === selectedMetric.value)
  if (!metric) return []
  
  return props.data.map((point, index) => ({
    label: point.label || `数据点 ${index + 1}`,
    color: metric.color,
    value: metric.format ? metric.format(point.value) : point.value.toString(),
    visible: visibleSeries.value[index] !== false
  }))
})

// 方法
const handleMetricChange = (metric: string) => {
  selectedMetric.value = metric
  emit('metric-change', metric)
  drawChart()
}

const handlePeriodChange = (period: string) => {
  selectedPeriod.value = period
  emit('period-change', period)
}

const toggleSeries = (index: number) => {
  visibleSeries.value[index] = !visibleSeries.value[index]
  drawChart()
}

const retry = () => {
  emit('retry')
}

const initializeCanvas = () => {
  if (!chartCanvas.value) return
  
  const container = chartCanvas.value.parentElement
  if (!container) return
  
  const rect = container.getBoundingClientRect()
  canvasWidth.value = rect.width
  canvasHeight.value = props.chartHeight
  
  // 设置高DPI支持
  const dpr = window.devicePixelRatio || 1
  chartCanvas.value.width = canvasWidth.value * dpr
  chartCanvas.value.height = canvasHeight.value * dpr
  chartCanvas.value.style.width = canvasWidth.value + 'px'
  chartCanvas.value.style.height = canvasHeight.value + 'px'
  
  const ctx = chartCanvas.value.getContext('2d')
  if (ctx) {
    ctx.scale(dpr, dpr)
  }
}

const drawChart = async () => {
  await nextTick()
  
  if (!chartCanvas.value || !chartData.value.length) return
  
  const ctx = chartCanvas.value.getContext('2d')
  if (!ctx) return
  
  // 清空画布
  ctx.clearRect(0, 0, canvasWidth.value, canvasHeight.value)
  
  // 绘制图表
  switch (props.chartType) {
    case 'line':
      drawLineChart(ctx)
      break
    case 'bar':
      drawBarChart(ctx)
      break
    case 'area':
      drawAreaChart(ctx)
      break
  }
}

const drawLineChart = (ctx: CanvasRenderingContext2D) => {
  const data = chartData.value
  if (!data.length) return
  
  const metric = availableMetrics.value.find(m => m.key === selectedMetric.value)
  if (!metric) return
  
  // 计算绘图区域
  const padding = 40
  const chartWidth = canvasWidth.value - padding * 2
  const chartHeight = canvasHeight.value - padding * 2
  
  // 计算数据范围
  const values = data.map(d => d.value)
  const minValue = Math.min(...values)
  const maxValue = Math.max(...values)
  const valueRange = maxValue - minValue || 1
  
  // 绘制网格线
  ctx.strokeStyle = '#f3f4f6'
  ctx.lineWidth = 1
  
  // 水平网格线
  for (let i = 0; i <= 5; i++) {
    const y = padding + (chartHeight / 5) * i
    ctx.beginPath()
    ctx.moveTo(padding, y)
    ctx.lineTo(padding + chartWidth, y)
    ctx.stroke()
  }
  
  // 垂直网格线
  const stepX = chartWidth / (data.length - 1 || 1)
  for (let i = 0; i < data.length; i++) {
    const x = padding + stepX * i
    ctx.beginPath()
    ctx.moveTo(x, padding)
    ctx.lineTo(x, padding + chartHeight)
    ctx.stroke()
  }
  
  // 绘制数据线
  ctx.strokeStyle = metric.color
  ctx.lineWidth = 2
  ctx.beginPath()
  
  data.forEach((point, index) => {
    const x = padding + stepX * index
    const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight
    
    if (index === 0) {
      ctx.moveTo(x, y)
    } else {
      ctx.lineTo(x, y)
    }
  })
  
  ctx.stroke()
  
  // 绘制数据点
  ctx.fillStyle = metric.color
  data.forEach((point, index) => {
    const x = padding + stepX * index
    const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight
    
    ctx.beginPath()
    ctx.arc(x, y, 4, 0, Math.PI * 2)
    ctx.fill()
  })
  
  // 绘制坐标轴标签
  ctx.fillStyle = '#6b7280'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  
  // X轴标签
  data.forEach((point, index) => {
    const x = padding + stepX * index
    const date = new Date(point.timestamp)
    const label = date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    ctx.fillText(label, x, canvasHeight.value - 10)
  })
  
  // Y轴标签
  ctx.textAlign = 'right'
  for (let i = 0; i <= 5; i++) {
    const value = minValue + (valueRange / 5) * i
    const y = padding + chartHeight - (chartHeight / 5) * i
    const label = metric.format ? metric.format(value) : Math.round(value).toString()
    ctx.fillText(label, padding - 10, y + 4)
  }
}

const drawBarChart = (ctx: CanvasRenderingContext2D) => {
  const data = chartData.value
  if (!data.length) return
  
  const metric = availableMetrics.value.find(m => m.key === selectedMetric.value)
  if (!metric) return
  
  // 计算绘图区域
  const padding = 40
  const chartWidth = canvasWidth.value - padding * 2
  const chartHeight = canvasHeight.value - padding * 2
  
  // 计算数据范围
  const values = data.map(d => d.value)
  const maxValue = Math.max(...values)
  
  // 计算柱子宽度
  const barWidth = chartWidth / data.length * 0.8
  const barSpacing = chartWidth / data.length * 0.2
  
  // 绘制柱子
  ctx.fillStyle = metric.color
  data.forEach((point, index) => {
    const x = padding + (chartWidth / data.length) * index + barSpacing / 2
    const barHeight = (point.value / maxValue) * chartHeight
    const y = padding + chartHeight - barHeight
    
    ctx.fillRect(x, y, barWidth, barHeight)
  })
  
  // 绘制标签
  ctx.fillStyle = '#6b7280'
  ctx.font = '12px sans-serif'
  ctx.textAlign = 'center'
  
  data.forEach((point, index) => {
    const x = padding + (chartWidth / data.length) * index + (chartWidth / data.length) / 2
    const date = new Date(point.timestamp)
    const label = date.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' })
    ctx.fillText(label, x, canvasHeight.value - 10)
  })
}

const drawAreaChart = (ctx: CanvasRenderingContext2D) => {
  // 先绘制填充区域
  const data = chartData.value
  if (!data.length) return
  
  const metric = availableMetrics.value.find(m => m.key === selectedMetric.value)
  if (!metric) return
  
  const padding = 40
  const chartWidth = canvasWidth.value - padding * 2
  const chartHeight = canvasHeight.value - padding * 2
  
  const values = data.map(d => d.value)
  const minValue = Math.min(...values)
  const maxValue = Math.max(...values)
  const valueRange = maxValue - minValue || 1
  
  const stepX = chartWidth / (data.length - 1 || 1)
  
  // 创建渐变
  const gradient = ctx.createLinearGradient(0, padding, 0, padding + chartHeight)
  gradient.addColorStop(0, metric.color + '40')
  gradient.addColorStop(1, metric.color + '10')
  
  // 绘制填充区域
  ctx.fillStyle = gradient
  ctx.beginPath()
  ctx.moveTo(padding, padding + chartHeight)
  
  data.forEach((point, index) => {
    const x = padding + stepX * index
    const y = padding + chartHeight - ((point.value - minValue) / valueRange) * chartHeight
    ctx.lineTo(x, y)
  })
  
  ctx.lineTo(padding + chartWidth, padding + chartHeight)
  ctx.closePath()
  ctx.fill()
  
  // 然后绘制线条
  drawLineChart(ctx)
}

const handleResize = () => {
  initializeCanvas()
  drawChart()
}

// 监听器
watch(() => props.data, () => {
  if (props.data) {
    visibleSeries.value = new Array(props.data.length).fill(true)
    drawChart()
  }
}, { immediate: true })

watch(() => props.loading, (loading) => {
  if (!loading) {
    nextTick(() => {
      drawChart()
    })
  }
})

// 生命周期
onMounted(() => {
  initializeCanvas()
  window.addEventListener('resize', handleResize)
})

onUnmounted(() => {
  window.removeEventListener('resize', handleResize)
})
</script>

<style scoped>
.product-metrics-chart {
  width: 100%;
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
}

.chart-title {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.chart-controls {
  display: flex;
  align-items: center;
  gap: 12px;
}

.period-selector {
  margin-left: 8px;
}

.chart-container {
  position: relative;
  padding: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.chart-loading,
.chart-error,
.chart-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
  color: #6b7280;
}

.chart-error {
  color: #f56565;
}

.chart-canvas {
  display: block;
  max-width: 100%;
}

.chart-legend {
  padding: 16px 20px;
  border-top: 1px solid #f3f4f6;
  background: #fafafa;
}

.legend-items {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
}

.legend-item {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 4px;
  transition: background-color 0.2s;
}

.legend-item:hover {
  background: #f3f4f6;
}

.legend-color {
  width: 12px;
  height: 12px;
  border-radius: 2px;
  transition: opacity 0.2s;
}

.legend-label {
  font-size: 14px;
  color: #374151;
  transition: opacity 0.2s;
}

.legend-label.disabled {
  opacity: 0.5;
}

.legend-value {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .chart-controls {
    justify-content: space-between;
  }
  
  .legend-items {
    flex-direction: column;
    gap: 8px;
  }
}
</style>