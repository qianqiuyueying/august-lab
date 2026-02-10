<template>
  <div class="product-monitoring-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title">产品监控</h1>
          <p class="page-description">实时监控产品运行状态、性能指标和错误日志</p>
        </div>
        <div class="header-actions">
          <el-select
            v-model="selectedProductId"
            placeholder="选择产品"
            style="width: 200px; margin-right: 12px"
            @change="handleProductChange"
          >
            <el-option
              v-for="product in products"
              :key="product.id"
              :label="product.title"
              :value="product.id"
            >
              <div class="product-option">
                <span class="product-title">{{ product.title }}</span>
                <el-tag :type="getProductStatusTagType(product)" size="small">
                  {{ getProductStatusText(product) }}
                </el-tag>
              </div>
            </el-option>
          </el-select>
          
          <el-tooltip content="开启后每 60 秒刷新一次，避免请求过频触发限流">
            <el-switch
              v-model="monitoringAutoRefresh"
              active-text="自动刷新"
              size="default"
              style="margin-right: 12px"
            />
          </el-tooltip>
          <el-button-group>
            <el-button
              v-for="tab in monitoringTabs"
              :key="tab.key"
              :type="activeTab === tab.key ? 'primary' : ''"
              @click="activeTab = tab.key"
            >
              <el-icon>
                <component :is="tab.icon" />
              </el-icon>
              {{ tab.label }}
            </el-button>
          </el-button-group>
        </div>
      </div>
    </div>
    
    <!-- 监控内容 -->
    <div class="monitoring-content">
      <!-- 概览仪表盘 -->
      <div v-if="activeTab === 'overview'" class="tab-content">
        <div class="overview-grid">
          <!-- 系统状态卡片 -->
          <el-card class="status-card">
            <template #header>
              <div class="card-header">
                <h3>系统状态</h3>
                <div class="status-indicator" :class="getSystemStatusClass()">
                  <div class="status-dot"></div>
                  <span>{{ getSystemStatusText() }}</span>
                </div>
              </div>
            </template>
            
            <div class="status-metrics">
              <div class="metric-row">
                <div class="metric-item">
                  <span class="metric-label">在线产品:</span>
                  <span class="metric-value">{{ systemStatus.onlineProducts }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">活跃用户:</span>
                  <span class="metric-value">{{ systemStatus.activeUsers }}</span>
                </div>
              </div>
              <div class="metric-row">
                <div class="metric-item">
                  <span class="metric-label">错误率:</span>
                  <span class="metric-value" :class="getErrorRateClass()">
                    {{ systemStatus.errorRate }}%
                  </span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">平均响应:</span>
                  <span class="metric-value">{{ systemStatus.avgResponseTime }}ms</span>
                </div>
              </div>
            </div>
          </el-card>
          
          <!-- 快速操作 -->
          <el-card class="quick-actions-card">
            <template #header>
              <h3>快速操作</h3>
            </template>
            
            <div class="quick-actions">
              <el-button
                @click="runQuickDiagnostic"
                type="primary"
                :loading="runningQuickDiagnostic"
                class="action-button"
              >
                <el-icon><Tools /></el-icon>
                快速诊断
              </el-button>
              
              <el-button
                @click="exportMonitoringReport"
                type="success"
                class="action-button"
              >
                <el-icon><Download /></el-icon>
                导出报告
              </el-button>
              
              <el-button
                @click="clearAllLogs"
                type="warning"
                class="action-button"
              >
                <el-icon><Delete /></el-icon>
                清空日志
              </el-button>
              
              <el-button
                @click="refreshAllData"
                type="info"
                :loading="refreshingData"
                class="action-button"
              >
                <el-icon><Refresh /></el-icon>
                刷新数据
              </el-button>
            </div>
          </el-card>
          
          <!-- 最近告警 -->
          <el-card class="alerts-card">
            <template #header>
              <div class="card-header">
                <h3>最近告警</h3>
                <el-badge :value="recentAlerts.length" :max="99">
                  <el-icon><Bell /></el-icon>
                </el-badge>
              </div>
            </template>
            
            <div class="alerts-list">
              <div
                v-for="alert in recentAlerts.slice(0, 5)"
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
                  <div class="alert-time">{{ formatTime(alert.timestamp) }}</div>
                </div>
              </div>
              
              <div v-if="recentAlerts.length === 0" class="no-alerts">
                <el-icon size="24" color="#10b981">
                  <CircleCheckFilled />
                </el-icon>
                <p>暂无告警</p>
              </div>
            </div>
          </el-card>
        </div>
        
        <!-- 实时监控组件 -->
        <div class="real-time-section">
          <RealTimeMonitor :product-id="selectedProductId || undefined" />
        </div>
      </div>
      
      <!-- 错误监控：仅开启自动刷新时每 60s 轮询，避免占满限流 -->
      <div v-else-if="activeTab === 'errors'" class="tab-content">
        <ProductErrorMonitor
          :product-id="selectedProductId || undefined"
          :auto-refresh="monitoringAutoRefresh"
          :refresh-interval="60000"
        />
      </div>
      
      <!-- 性能监控：仅开启自动刷新时每 60s 轮询 -->
      <div v-else-if="activeTab === 'performance'" class="tab-content">
        <ProductPerformanceMonitor
          :product-id="selectedProductId || undefined"
          :auto-refresh="monitoringAutoRefresh"
          :refresh-interval="60000"
        />
      </div>
      
      <!-- 诊断工具 -->
      <div v-else-if="activeTab === 'diagnostic'" class="tab-content">
        <ProductDiagnosticTools :product-id="selectedProductId || undefined" />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Monitor,
  Warning,
  TrendCharts,
  Tools,
  Download,
  Delete,
  Refresh,
  Bell,
  WarningFilled,
  InfoFilled,
  CircleCheckFilled
} from '@element-plus/icons-vue'
import RealTimeMonitor from '../components/analytics/RealTimeMonitor.vue'
import ProductErrorMonitor from '../components/monitoring/ProductErrorMonitor.vue'
import ProductPerformanceMonitor from '../components/monitoring/ProductPerformanceMonitor.vue'
import ProductDiagnosticTools from '../components/monitoring/ProductDiagnosticTools.vue'
import { useProductStore } from '../../frontend/composables/useProductStore'
import { useProductMonitoring } from '../../frontend/composables/useProductMonitoring'
import type { Product } from '../../shared/types'

interface SystemStatus {
  onlineProducts: number
  activeUsers: number
  errorRate: number
  avgResponseTime: number
  overallStatus: 'good' | 'warning' | 'critical'
}

interface MonitoringAlert {
  id: string
  level: 'critical' | 'warning' | 'info'
  title: string
  message: string
  timestamp: Date
  productId?: number
}

interface MonitoringTab {
  key: string
  label: string
  icon: any
}

// 响应式数据（默认关闭自动刷新，避免高频请求触发后端限流）
const monitoringAutoRefresh = ref(false)
const activeTab = ref('overview')
const selectedProductId = ref<number | null>(null)
const products = ref<Product[]>([])
const runningQuickDiagnostic = ref(false)
const refreshingData = ref(false)

const systemStatus = ref<SystemStatus>({
  onlineProducts: 0,
  activeUsers: 0,
  errorRate: 0,
  avgResponseTime: 0,
  overallStatus: 'good'
})

const recentAlerts = ref<MonitoringAlert[]>([])

// 使用组合式函数
const { fetchProducts } = useProductStore()
const { getSystemStatus, getProductLogs } = useProductMonitoring()

// 配置数据
const monitoringTabs: MonitoringTab[] = [
  { key: 'overview', label: '概览', icon: Monitor },
  { key: 'errors', label: '错误监控', icon: Warning },
  { key: 'performance', label: '性能监控', icon: TrendCharts },
  { key: 'diagnostic', label: '诊断工具', icon: Tools }
]

// 方法
const loadProducts = async () => {
  try {
    products.value = await fetchProducts({ published_only: false })
    
    // 默认选择第一个产品
    if (products.value.length > 0 && !selectedProductId.value) {
      selectedProductId.value = products.value[0].id
    }
  } catch (error: any) {
    ElMessage.error(error.message || '加载产品列表失败')
  }
}

const handleProductChange = () => {
  // 产品切换时刷新数据
  refreshAllData()
}

const runQuickDiagnostic = async () => {
  if (!selectedProductId.value) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  runningQuickDiagnostic.value = true
  
  try {
    const monitoring = useProductMonitoring()
    const result = await monitoring.runProductDiagnostic(selectedProductId.value)
    
    // 根据诊断结果生成告警
    if (result.overall_status === 'critical') {
      recentAlerts.value.unshift({
        id: `diagnostic_${Date.now()}`,
        level: 'critical',
        title: '诊断发现问题',
        message: (result.recommendations || []).join('; ') || '发现严重问题',
        timestamp: new Date(result.timestamp),
        productId: selectedProductId.value
      })
    } else if (result.overall_status === 'warning') {
      recentAlerts.value.unshift({
        id: `diagnostic_${Date.now()}`,
        level: 'warning',
        title: '诊断发现警告',
        message: (result.recommendations || []).join('; ') || '发现警告',
        timestamp: new Date(result.timestamp),
        productId: selectedProductId.value
      })
    }
    
    ElMessage.success('快速诊断完成')
    await loadSystemStatus()
  } catch (error: any) {
    ElMessage.error(error.message || '诊断失败')
  } finally {
    runningQuickDiagnostic.value = false
  }
}

const exportMonitoringReport = async () => {
  if (!selectedProductId.value) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  try {
    const monitoring = useProductMonitoring()
    
    // 收集所有监控数据
    const [systemStatusData, errors, performance, diagnostic] = await Promise.all([
      monitoring.getSystemStatus().catch(() => null),
      monitoring.getProductErrors(selectedProductId.value, { limit: 100 }).catch(() => []),
      monitoring.getProductPerformance(selectedProductId.value, { limit: 100 }).catch(() => []),
      monitoring.runProductDiagnostic(selectedProductId.value).catch(() => null)
    ])
    
    // 构建报告数据
    const report = {
      export_time: new Date().toISOString(),
      product_id: selectedProductId.value,
      product_name: products.value.find(p => p.id === selectedProductId.value)?.title || '未知产品',
      system_status: systemStatusData,
      errors: {
        total: errors.length,
        critical: errors.filter(e => e.log_level === 'critical').length,
        error: errors.filter(e => e.log_level === 'error').length,
        warning: errors.filter(e => e.log_level === 'warning').length,
        recent_errors: errors.slice(0, 20)
      },
      performance: {
        total_records: performance.length,
        recent_records: performance.slice(0, 20)
      },
      diagnostic: diagnostic,
      alerts: recentAlerts.value.map(alert => ({
        id: alert.id,
        level: alert.level,
        title: alert.title,
        message: alert.message,
        timestamp: alert.timestamp.toISOString(),
        product_id: alert.productId
      }))
    }
    
    // 生成JSON文件并下载
    const jsonStr = JSON.stringify(report, null, 2)
    const blob = new Blob([jsonStr], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `监控报告_${selectedProductId.value}_${new Date().toISOString().split('T')[0]}.json`
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
    URL.revokeObjectURL(url)
    
    ElMessage.success('监控报告导出成功')
  } catch (error: any) {
    ElMessage.error(error.message || '导出报告失败')
  }
}

const clearAllLogs = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要清空告警列表吗？此操作只会清空前端显示的告警，不会删除后端日志记录。',
      '确认清空',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    // 清空本地告警列表（实际日志在后端，这里只清空前端显示的告警）
    recentAlerts.value = []
    ElMessage.success('告警列表已清空')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '清空日志失败')
    }
  }
}

const refreshAllData = async () => {
  refreshingData.value = true
  
  try {
    await loadSystemStatus()
    await loadRecentAlerts()
    ElMessage.success('数据已刷新')
  } catch (error: any) {
    ElMessage.error(error.message || '刷新数据失败')
  } finally {
    refreshingData.value = false
  }
}

const loadSystemStatus = async () => {
  try {
    const status = await getSystemStatus()
    
    systemStatus.value = {
      onlineProducts: status.metrics.published_products,
      activeUsers: 0, // 后端暂无活跃用户统计
      errorRate: status.metrics.error_rate,
      avgResponseTime: 0, // 后端暂无平均响应时间统计
      overallStatus: status.overall_status
    }
  } catch (error: any) {
    console.error('加载系统状态失败:', error)
  }
}

const loadRecentAlerts = async () => {
  try {
    // 从所有产品的错误日志中生成告警
    const allAlerts: MonitoringAlert[] = []
    
    for (const product of products.value) {
      try {
        const logs = await getProductLogs(product.id, {
          log_type: 'error',
          limit: 5
        })
        
        for (const log of logs) {
          const level = log.log_level === 'critical' ? 'critical' : 
                       log.log_level === 'error' ? 'critical' : 
                       log.log_level === 'warning' ? 'warning' : 'info'
          
          allAlerts.push({
            id: `log_${log.id}`,
            level: level as 'critical' | 'warning' | 'info',
            title: log.message || '错误日志',
            message: log.details ? JSON.stringify(log.details) : log.message || '',
            timestamp: new Date(log.timestamp),
            productId: product.id
          })
        }
      } catch (error) {
        // 忽略单个产品加载失败
        console.warn(`加载产品 ${product.id} 的日志失败:`, error)
      }
    }
    
    // 按时间排序，取最近5条
    recentAlerts.value = allAlerts
      .sort((a, b) => b.timestamp.getTime() - a.timestamp.getTime())
      .slice(0, 5)
  } catch (error: any) {
    console.error('加载告警失败:', error)
  }
}

// 工具方法
const getProductStatusTagType = (product: Product) => {
  if (!product.is_published) return 'info'
  // 这里可以根据产品的实际状态返回不同的标签类型
  return 'success'
}

const getProductStatusText = (product: Product) => {
  if (!product.is_published) return '未发布'
  return '正常'
}

const getSystemStatusClass = () => {
  return `status-${systemStatus.value.overallStatus}`
}

const getSystemStatusText = () => {
  const texts = {
    good: '系统正常',
    warning: '需要关注',
    critical: '存在问题'
  }
  return texts[systemStatus.value.overallStatus]
}

const getErrorRateClass = () => {
  const rate = systemStatus.value.errorRate
  if (rate > 3) return 'error-rate-high'
  if (rate > 1) return 'error-rate-medium'
  return 'error-rate-low'
}

const getAlertClass = (level: string) => {
  return `alert-${level}`
}

const formatTime = (date: Date) => {
  const now = new Date()
  const diff = now.getTime() - date.getTime()
  
  if (diff < 60000) return '刚刚'
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`
  return `${Math.floor(diff / 86400000)}天前`
}

// 生命周期
onMounted(async () => {
  await loadProducts()
  await loadSystemStatus()
  await loadRecentAlerts()
})
</script>

<style scoped>
.product-monitoring-page {
  min-height: 100vh;
  background: #f5f5f5;
}

.dark .product-monitoring-page {
  background: #0f172a; /* Slate 950 */
}

.page-header {
  background: white;
  border-bottom: 1px solid #e5e7eb;
  padding: 24px;
}

.dark .page-header {
  background: #1e293b; /* Slate 800 */
  border-bottom-color: rgba(148, 163, 184, 0.15); /* Slate 400 15% */
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

.dark .page-title {
  color: #f3f4f6; /* Gray 50 */
}

.page-description {
  color: #6b7280;
  margin: 0;
}

.dark .page-description {
  color: #9ca3af; /* Gray 400 */
}

.header-actions {
  display: flex;
  align-items: center;
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

.monitoring-content {
  padding: 24px;
}

.tab-content {
  min-height: 600px;
}

.overview-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 20px;
  margin-bottom: 24px;
}

.status-card,
.quick-actions-card,
.alerts-card {
  /* 移除固定高度以避免滚动条 */
  min-height: auto;
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

.dark .card-header h3 {
  color: #f3f4f6; /* Gray 50 */
}

.status-indicator {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
  font-weight: 500;
}

.status-indicator.status-good {
  color: #10b981;
}

.status-indicator.status-warning {
  color: #f59e0b;
}

.status-indicator.status-critical {
  color: #ef4444;
}

.status-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: currentColor;
  animation: pulse 2s infinite;
}

.status-metrics {
  /* 调整padding以适应内容 */
  padding: 16px;
}

.metric-row {
  display: flex;
  justify-content: space-between;
  margin-bottom: 12px;
}

.metric-item {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.metric-label {
  font-size: 12px;
  color: #6b7280;
}

.dark .metric-label {
  color: #9ca3af; /* Gray 400 */
}

.metric-value {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.dark .metric-value {
  color: #f3f4f6; /* Gray 50 */
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

.quick-actions {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 12px;
  /* 使用min-height替代固定height并调整padding */
  min-height: 140px;
  padding: 16px;
}

.action-button {
  width: 100%;
  /* 调整按钮高度以适应容器 */
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.alerts-list {
  /* 调整最大高度以更好地适配卡片 */
  max-height: 110px;
  overflow-y: auto;
  padding: 8px 0;
  /* 隐藏滚动条但保持功能 */
  scrollbar-width: thin;
  scrollbar-color: #c7c7c7 transparent;
}

/* Webkit浏览器滚动条样式 */
.alerts-list::-webkit-scrollbar {
  width: 6px;
}

.alerts-list::-webkit-scrollbar-track {
  background: transparent;
}

.alerts-list::-webkit-scrollbar-thumb {
  background-color: #c7c7c7;
  border-radius: 3px;
}

.alert-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 6px;
  margin-bottom: 8px;
  border-left: 3px solid transparent;
}

.alert-item.alert-critical {
  background: #fef2f2;
  border-left-color: #ef4444;
}

.dark .alert-item.alert-critical {
  background: rgba(239, 68, 68, 0.1); /* Red 500 10% */
  border-left-color: #ef4444;
}

.alert-item.alert-warning {
  background: #fffbeb;
  border-left-color: #f59e0b;
}

.dark .alert-item.alert-warning {
  background: rgba(245, 158, 11, 0.1); /* Amber 500 10% */
  border-left-color: #f59e0b;
}

.alert-item.alert-info {
  background: #f0f9ff;
  border-left-color: #3b82f6;
}

.dark .alert-item.alert-info {
  background: rgba(59, 130, 246, 0.1); /* Blue 500 10% */
  border-left-color: #3b82f6;
}

.alert-icon {
  width: 16px;
  height: 16px;
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
  min-width: 0;
}

.alert-title {
  font-size: 12px;
  font-weight: 500;
  color: #1f2937;
  margin-bottom: 2px;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.dark .alert-title {
  color: #f3f4f6; /* Gray 50 */
}

.alert-time {
  font-size: 11px;
  color: #9ca3af;
}

.dark .alert-time {
  color: #6b7280; /* Gray 500 */
}

.no-alerts {
  text-align: center;
  padding: 20px;
  color: #6b7280;
}

.dark .no-alerts {
  color: #9ca3af; /* Gray 400 */
}

.no-alerts p {
  margin: 8px 0 0 0;
  font-size: 12px;
}

.real-time-section {
  margin-top: 24px;
}

/* 动画 */
@keyframes pulse {
  0%, 100% {
    opacity: 1;
  }
  50% {
    opacity: 0.5;
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .overview-grid {
    grid-template-columns: 1fr;
  }
  
  .status-card,
  .quick-actions-card,
  .alerts-card {
    /* 在小屏幕上移除固定高度 */
    height: auto;
  }
  
  .quick-actions {
    grid-template-columns: repeat(2, 1fr);
  }
}

@media (max-width: 768px) {
  .product-monitoring-page {
    padding: 0;
  }
  
  .page-header {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .header-actions {
    flex-direction: column;
    gap: 16px;
  }
  
  .monitoring-content {
    padding: 16px;
  }
  
  .quick-actions {
    grid-template-columns: 1fr;
  }
  
  .overview-grid {
    gap: 16px;
  }
}
</style>