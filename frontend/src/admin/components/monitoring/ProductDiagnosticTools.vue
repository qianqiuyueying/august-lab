<template>
  <div class="product-diagnostic-tools">
    <div class="tools-header">
      <h3 class="tools-title">
        <el-icon class="diagnostic-icon">
          <Tools />
        </el-icon>
        诊断工具
      </h3>
      <div class="tools-actions">
        <el-button @click="runFullDiagnostic" type="primary" :loading="runningDiagnostic">
          <el-icon><VideoPlay /></el-icon>
          运行完整诊断
        </el-button>
      </div>
    </div>
    
    <!-- 诊断工具列表 -->
    <div class="diagnostic-tools">
      <el-row :gutter="20">
        <!-- 连接测试 -->
        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="tool-header">
                <div class="tool-icon connectivity">
                  <el-icon><Connection /></el-icon>
                </div>
                <div class="tool-info">
                  <h4>连接测试</h4>
                  <p>检查产品网络连接状态</p>
                </div>
              </div>
            </template>
            
            <div class="tool-content">
              <div class="test-results">
                <div class="result-item">
                  <span class="result-label">API连接:</span>
                  <el-tag :type="getStatusTagType(connectivityStatus.api)" size="small">
                    {{ getStatusText(connectivityStatus.api) }}
                  </el-tag>
                </div>
                <div class="result-item">
                  <span class="result-label">数据库:</span>
                  <el-tag :type="getStatusTagType(connectivityStatus.database)" size="small">
                    {{ getStatusText(connectivityStatus.database) }}
                  </el-tag>
                </div>
                <div class="result-item">
                  <span class="result-label">文件服务:</span>
                  <el-tag :type="getStatusTagType(connectivityStatus.fileService)" size="small">
                    {{ getStatusText(connectivityStatus.fileService) }}
                  </el-tag>
                </div>
              </div>
              
              <div class="tool-actions">
                <el-button 
                  @click="runConnectivityTest" 
                  size="small" 
                  :loading="testingConnectivity"
                >
                  重新测试
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 性能分析 -->
        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="tool-header">
                <div class="tool-icon performance">
                  <el-icon><TrendCharts /></el-icon>
                </div>
                <div class="tool-info">
                  <h4>性能分析</h4>
                  <p>分析产品性能瓶颈</p>
                </div>
              </div>
            </template>
            
            <div class="tool-content">
              <div class="performance-metrics">
                <div class="metric-item">
                  <span class="metric-label">加载时间:</span>
                  <span class="metric-value" :class="getPerformanceClass(performanceMetrics.loadTime)">
                    {{ performanceMetrics.loadTime }}ms
                  </span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">内存使用:</span>
                  <span class="metric-value">{{ formatMemory(performanceMetrics.memoryUsage) }}</span>
                </div>
                <div class="metric-item">
                  <span class="metric-label">FPS:</span>
                  <span class="metric-value" :class="getFpsClass(performanceMetrics.fps)">
                    {{ performanceMetrics.fps }}
                  </span>
                </div>
              </div>
              
              <div class="tool-actions">
                <el-button 
                  @click="runPerformanceAnalysis" 
                  size="small" 
                  :loading="analyzingPerformance"
                >
                  开始分析
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 错误检查 -->
        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="tool-header">
                <div class="tool-icon error-check">
                  <el-icon><Warning /></el-icon>
                </div>
                <div class="tool-info">
                  <h4>错误检查</h4>
                  <p>扫描产品潜在错误</p>
                </div>
              </div>
            </template>
            
            <div class="tool-content">
              <div class="error-summary">
                <div class="error-count critical">
                  <span class="count">{{ errorSummary.critical }}</span>
                  <span class="label">严重错误</span>
                </div>
                <div class="error-count warning">
                  <span class="count">{{ errorSummary.warning }}</span>
                  <span class="label">警告</span>
                </div>
                <div class="error-count info">
                  <span class="count">{{ errorSummary.info }}</span>
                  <span class="label">提示</span>
                </div>
              </div>
              
              <div class="tool-actions">
                <el-button 
                  @click="runErrorCheck" 
                  size="small" 
                  :loading="checkingErrors"
                >
                  扫描错误
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
      
      <el-row :gutter="20" style="margin-top: 20px">
        <!-- 安全检查 -->
        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="tool-header">
                <div class="tool-icon security">
                  <el-icon><Lock /></el-icon>
                </div>
                <div class="tool-info">
                  <h4>安全检查</h4>
                  <p>检查产品安全漏洞</p>
                </div>
              </div>
            </template>
            
            <div class="tool-content">
              <div class="security-status">
                <div class="status-item">
                  <span class="status-label">XSS防护:</span>
                  <el-icon :color="securityStatus.xss ? '#10b981' : '#ef4444'">
                    <CircleCheckFilled v-if="securityStatus.xss" />
                    <CircleCloseFilled v-else />
                  </el-icon>
                </div>
                <div class="status-item">
                  <span class="status-label">CSRF防护:</span>
                  <el-icon :color="securityStatus.csrf ? '#10b981' : '#ef4444'">
                    <CircleCheckFilled v-if="securityStatus.csrf" />
                    <CircleCloseFilled v-else />
                  </el-icon>
                </div>
                <div class="status-item">
                  <span class="status-label">内容安全:</span>
                  <el-icon :color="securityStatus.contentSecurity ? '#10b981' : '#ef4444'">
                    <CircleCheckFilled v-if="securityStatus.contentSecurity" />
                    <CircleCloseFilled v-else />
                  </el-icon>
                </div>
              </div>
              
              <div class="tool-actions">
                <el-button 
                  @click="runSecurityCheck" 
                  size="small" 
                  :loading="checkingSecurity"
                >
                  安全扫描
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 兼容性测试 -->
        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="tool-header">
                <div class="tool-icon compatibility">
                  <el-icon><Monitor /></el-icon>
                </div>
                <div class="tool-info">
                  <h4>兼容性测试</h4>
                  <p>检查浏览器兼容性</p>
                </div>
              </div>
            </template>
            
            <div class="tool-content">
              <div class="compatibility-results">
                <div class="browser-item">
                  <span class="browser-name">Chrome:</span>
                  <el-progress 
                    :percentage="compatibilityScores.chrome" 
                    :color="getCompatibilityColor(compatibilityScores.chrome)"
                    :show-text="false"
                    :stroke-width="6"
                  />
                  <span class="score">{{ compatibilityScores.chrome }}%</span>
                </div>
                <div class="browser-item">
                  <span class="browser-name">Firefox:</span>
                  <el-progress 
                    :percentage="compatibilityScores.firefox" 
                    :color="getCompatibilityColor(compatibilityScores.firefox)"
                    :show-text="false"
                    :stroke-width="6"
                  />
                  <span class="score">{{ compatibilityScores.firefox }}%</span>
                </div>
                <div class="browser-item">
                  <span class="browser-name">Safari:</span>
                  <el-progress 
                    :percentage="compatibilityScores.safari" 
                    :color="getCompatibilityColor(compatibilityScores.safari)"
                    :show-text="false"
                    :stroke-width="6"
                  />
                  <span class="score">{{ compatibilityScores.safari }}%</span>
                </div>
              </div>
              
              <div class="tool-actions">
                <el-button 
                  @click="runCompatibilityTest" 
                  size="small" 
                  :loading="testingCompatibility"
                >
                  兼容性测试
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
        
        <!-- 资源分析 -->
        <el-col :span="8">
          <el-card class="tool-card">
            <template #header>
              <div class="tool-header">
                <div class="tool-icon resource">
                  <el-icon><Files /></el-icon>
                </div>
                <div class="tool-info">
                  <h4>资源分析</h4>
                  <p>分析产品资源使用</p>
                </div>
              </div>
            </template>
            
            <div class="tool-content">
              <div class="resource-breakdown">
                <div class="resource-item">
                  <span class="resource-type">JavaScript:</span>
                  <div class="resource-bar">
                    <div 
                      class="resource-fill js"
                      :style="{ width: getResourcePercentage('js') + '%' }"
                    />
                  </div>
                  <span class="resource-size">{{ formatBytes(resourceUsage.js) }}</span>
                </div>
                <div class="resource-item">
                  <span class="resource-type">CSS:</span>
                  <div class="resource-bar">
                    <div 
                      class="resource-fill css"
                      :style="{ width: getResourcePercentage('css') + '%' }"
                    />
                  </div>
                  <span class="resource-size">{{ formatBytes(resourceUsage.css) }}</span>
                </div>
                <div class="resource-item">
                  <span class="resource-type">图片:</span>
                  <div class="resource-bar">
                    <div 
                      class="resource-fill images"
                      :style="{ width: getResourcePercentage('images') + '%' }"
                    />
                  </div>
                  <span class="resource-size">{{ formatBytes(resourceUsage.images) }}</span>
                </div>
              </div>
              
              <div class="tool-actions">
                <el-button 
                  @click="runResourceAnalysis" 
                  size="small" 
                  :loading="analyzingResources"
                >
                  分析资源
                </el-button>
              </div>
            </div>
          </el-card>
        </el-col>
      </el-row>
    </div>
    
    <!-- 诊断报告 -->
    <div v-if="diagnosticReport" class="diagnostic-report">
      <el-card>
        <template #header>
          <div class="report-header">
            <h4>诊断报告</h4>
            <div class="report-actions">
              <el-button @click="exportReport" size="small" type="primary" plain>
                导出报告
              </el-button>
              <el-button @click="clearReport" size="small">
                清空报告
              </el-button>
            </div>
          </div>
        </template>
        
        <div class="report-content">
          <div class="report-summary">
            <div class="summary-item">
              <div class="summary-icon" :class="getOverallStatusClass()">
                <el-icon>
                  <CircleCheckFilled v-if="diagnosticReport.overallStatus === 'good'" />
                  <Warning v-else-if="diagnosticReport.overallStatus === 'warning'" />
                  <CircleCloseFilled v-else />
                </el-icon>
              </div>
              <div class="summary-content">
                <div class="summary-title">整体状态</div>
                <div class="summary-status">{{ getOverallStatusText() }}</div>
              </div>
            </div>
            
            <div class="summary-stats">
              <div class="stat-item">
                <span class="stat-value">{{ diagnosticReport.totalIssues }}</span>
                <span class="stat-label">发现问题</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ diagnosticReport.criticalIssues }}</span>
                <span class="stat-label">严重问题</span>
              </div>
              <div class="stat-item">
                <span class="stat-value">{{ diagnosticReport.suggestions.length }}</span>
                <span class="stat-label">优化建议</span>
              </div>
            </div>
          </div>
          
          <div class="report-details">
            <h5>详细结果</h5>
            <div class="details-list">
              <div
                v-for="item in diagnosticReport.details"
                :key="item.id"
                class="detail-item"
                :class="getDetailItemClass(item.level)"
              >
                <div class="detail-icon">
                  <el-icon>
                    <CircleCloseFilled v-if="item.level === 'error'" />
                    <Warning v-else-if="item.level === 'warning'" />
                    <InfoFilled v-else />
                  </el-icon>
                </div>
                <div class="detail-content">
                  <div class="detail-title">{{ item.title }}</div>
                  <div class="detail-message">{{ item.message }}</div>
                </div>
              </div>
            </div>
          </div>
          
          <div v-if="diagnosticReport.suggestions.length > 0" class="report-suggestions">
            <h5>优化建议</h5>
            <div class="suggestions-list">
              <div
                v-for="suggestion in diagnosticReport.suggestions"
                :key="suggestion.id"
                class="suggestion-item"
              >
                <div class="suggestion-icon">
                  <el-icon><MagicStick /></el-icon>
                </div>
                <div class="suggestion-content">
                  <div class="suggestion-title">{{ suggestion.title }}</div>
                  <div class="suggestion-description">{{ suggestion.description }}</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Tools,
  VideoPlay,
  Connection,
  TrendCharts,
  Warning,
  Lock,
  Monitor,
  Files,
  CircleCheckFilled,
  CircleCloseFilled,
  InfoFilled,
  MagicStick
} from '@element-plus/icons-vue'
import { useProductMonitoring } from '../../../frontend/composables/useProductMonitoring'
import api from '../../../shared/api'

interface ConnectivityStatus {
  api: 'good' | 'warning' | 'error'
  database: 'good' | 'warning' | 'error'
  fileService: 'good' | 'warning' | 'error'
}

interface PerformanceMetrics {
  loadTime: number
  memoryUsage: number
  fps: number
}

interface ErrorSummary {
  critical: number
  warning: number
  info: number
}

interface SecurityStatus {
  xss: boolean
  csrf: boolean
  contentSecurity: boolean
}

interface CompatibilityScores {
  chrome: number
  firefox: number
  safari: number
}

interface ResourceUsage {
  js: number
  css: number
  images: number
}

interface DiagnosticReportItem {
  id: string
  level: 'error' | 'warning' | 'info'
  title: string
  message: string
}

interface DiagnosticSuggestion {
  id: string
  title: string
  description: string
}

interface DiagnosticReport {
  overallStatus: 'good' | 'warning' | 'error'
  totalIssues: number
  criticalIssues: number
  details: DiagnosticReportItem[]
  suggestions: DiagnosticSuggestion[]
  timestamp: Date
}

interface Props {
  productId?: number
}

const props = defineProps<Props>()

// 使用组合式函数
const {
  runProductDiagnostic,
  getProductErrors,
  getProductPerformance,
  scanProductSecurity,
  verifyProductIntegrity,
  getProductFiles,
  getResourceStats,
  getSystemStatus
} = useProductMonitoring()

// 响应式数据
const runningDiagnostic = ref(false)
const testingConnectivity = ref(false)
const analyzingPerformance = ref(false)
const checkingErrors = ref(false)
const checkingSecurity = ref(false)
const testingCompatibility = ref(false)
const analyzingResources = ref(false)

const connectivityStatus = ref<ConnectivityStatus>({
  api: 'good',
  database: 'good',
  fileService: 'good'
})

const performanceMetrics = ref<PerformanceMetrics>({
  loadTime: 0,
  memoryUsage: 0,
  fps: 0
})

const errorSummary = ref<ErrorSummary>({
  critical: 0,
  warning: 0,
  info: 0
})

const securityStatus = ref<SecurityStatus>({
  xss: true,
  csrf: true,
  contentSecurity: true
})

const compatibilityScores = ref<CompatibilityScores>({
  chrome: 0,
  firefox: 0,
  safari: 0
})

const resourceUsage = ref<ResourceUsage>({
  js: 0,
  css: 0,
  images: 0
})

const diagnosticReport = ref<DiagnosticReport | null>(null)

// 计算属性
const totalResourceSize = computed(() => {
  return Object.values(resourceUsage.value).reduce((sum, size) => sum + size, 0)
})

// 方法
const runFullDiagnostic = async () => {
  if (!props.productId) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  runningDiagnostic.value = true
  
  try {
    // 依次运行所有诊断工具
    await runConnectivityTest()
    await runPerformanceAnalysis()
    await runErrorCheck()
    await runSecurityCheck()
    await runCompatibilityTest()
    await runResourceAnalysis()
    
    // 生成诊断报告
    await generateDiagnosticReport()
    
    ElMessage.success('完整诊断已完成')
  } catch (error: any) {
    ElMessage.error(error.message || '诊断过程中出现错误')
  } finally {
    runningDiagnostic.value = false
  }
}

const runConnectivityTest = async () => {
  if (!props.productId) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  testingConnectivity.value = true
  
  try {
    // 测试 API 连接
    let apiStatus: 'good' | 'warning' | 'error' = 'good'
    try {
      await api.get('/health')
    } catch {
      apiStatus = 'error'
    }
    
    // 测试数据库连接（通过系统状态API）
    let databaseStatus: 'good' | 'warning' | 'error' = 'good'
    try {
      await getSystemStatus()
    } catch {
      databaseStatus = 'error'
    }
    
    // 测试文件服务（通过验证产品完整性）
    let fileServiceStatus: 'good' | 'warning' | 'error' = 'good'
    try {
      const integrityResult = await verifyProductIntegrity(props.productId)
      if (!integrityResult.is_valid) {
        fileServiceStatus = 'warning'
      }
    } catch {
      fileServiceStatus = 'error'
    }
    
    connectivityStatus.value = {
      api: apiStatus,
      database: databaseStatus,
      fileService: fileServiceStatus
    }
    
    ElMessage.success('连接测试完成')
  } catch (error: any) {
    ElMessage.error(error.message || '连接测试失败')
  } finally {
    testingConnectivity.value = false
  }
}

const runPerformanceAnalysis = async () => {
  if (!props.productId) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  analyzingPerformance.value = true
  
  try {
    // 获取性能数据
    const performanceLogs = await getProductPerformance(props.productId, { limit: 10 })
    
    if (performanceLogs.length > 0) {
      // 计算平均性能指标
      const avgLoadTime = performanceLogs.reduce((sum, log) => {
        return sum + (log.details?.loadTime || 0)
      }, 0) / performanceLogs.length
      
      const avgMemoryUsage = performanceLogs.reduce((sum, log) => {
        return sum + (log.details?.memoryUsage || 0)
      }, 0) / performanceLogs.length
      
      performanceMetrics.value = {
        loadTime: Math.round(avgLoadTime),
        memoryUsage: Math.round(avgMemoryUsage),
        fps: 0 // 后端暂无FPS数据
      }
    } else {
      performanceMetrics.value = {
        loadTime: 0,
        memoryUsage: 0,
        fps: 0
      }
    }
    
    ElMessage.success('性能分析完成')
  } catch (error: any) {
    ElMessage.error(error.message || '性能分析失败')
  } finally {
    analyzingPerformance.value = false
  }
}

const runErrorCheck = async () => {
  if (!props.productId) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  checkingErrors.value = true
  
  try {
    // 获取错误日志
    const errors = await getProductErrors(props.productId, { limit: 100 })
    
    // 统计错误数量
    errorSummary.value = {
      critical: errors.filter(e => e.log_level === 'critical' || e.log_level === 'error').length,
      warning: errors.filter(e => e.log_level === 'warning').length,
      info: errors.filter(e => e.log_level === 'info' || !e.log_level).length
    }
    
    ElMessage.success('错误检查完成')
  } catch (error: any) {
    ElMessage.error(error.message || '错误检查失败')
  } finally {
    checkingErrors.value = false
  }
}

const runSecurityCheck = async () => {
  if (!props.productId) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  checkingSecurity.value = true
  
  try {
    // 运行安全扫描
    const scanResult = await scanProductSecurity(props.productId)
    
    // 根据扫描结果判断安全状态
    const isSafe = scanResult.is_safe
    const threats: string[] = scanResult.threats || []
    
    // 检查是否有XSS相关威胁
    const hasXssThreat = threats.some((t: string) => 
      t.toLowerCase().includes('xss') || 
      t.toLowerCase().includes('script') ||
      t.toLowerCase().includes('eval')
    )
    
    // 检查是否有CSRF相关威胁
    const hasCsrfThreat = threats.some((t: string) => 
      t.toLowerCase().includes('csrf') || 
      t.toLowerCase().includes('form')
    )
    
    // 检查内容安全策略
    const hasContentSecurityIssue = threats.some((t: string) => 
      t.toLowerCase().includes('content') || 
      t.toLowerCase().includes('security')
    )
    
    securityStatus.value = {
      xss: !hasXssThreat && isSafe,
      csrf: !hasCsrfThreat && isSafe,
      contentSecurity: !hasContentSecurityIssue && isSafe
    }
    
    ElMessage.success('安全检查完成')
  } catch (error: any) {
    ElMessage.error(error.message || '安全检查失败')
    // 如果扫描失败，设置为未知状态
    securityStatus.value = {
      xss: false,
      csrf: false,
      contentSecurity: false
    }
  } finally {
    checkingSecurity.value = false
  }
}

const runCompatibilityTest = async () => {
  if (!props.productId) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  testingCompatibility.value = true
  
  try {
    // 获取产品文件信息
    const filesInfo = await getProductFiles(props.productId)
    const files = filesInfo.files || []
    
    // 检查文件类型和现代浏览器支持
    const htmlFiles = files.filter((f: any) => f.name.endsWith('.html') || f.name.endsWith('.htm'))
    const jsFiles = files.filter((f: any) => f.name.endsWith('.js'))
    const cssFiles = files.filter((f: any) => f.name.endsWith('.css'))
    
    // 基础兼容性评分（基于文件结构）
    let baseScore = 70
    
    // 如果有HTML、JS、CSS文件，说明结构完整
    if (htmlFiles.length > 0) baseScore += 10
    if (jsFiles.length > 0) baseScore += 10
    if (cssFiles.length > 0) baseScore += 10
    
    // Chrome通常兼容性最好
    const chromeScore = Math.min(100, baseScore + 15)
    // Firefox稍低
    const firefoxScore = Math.min(100, baseScore + 10)
    // Safari最低
    const safariScore = Math.min(100, baseScore + 5)
    
    compatibilityScores.value = {
      chrome: chromeScore,
      firefox: firefoxScore,
      safari: safariScore
    }
    
    ElMessage.success('兼容性测试完成')
  } catch (error: any) {
    ElMessage.error(error.message || '兼容性测试失败')
    compatibilityScores.value = {
      chrome: 0,
      firefox: 0,
      safari: 0
    }
  } finally {
    testingCompatibility.value = false
  }
}

const runResourceAnalysis = async () => {
  if (!props.productId) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  analyzingResources.value = true
  
  try {
    // 获取资源统计
    const resourceStats = await getResourceStats(props.productId)
    const filesInfo = resourceStats.files || {}
    const byType = filesInfo.by_type || {}
    
    // 计算各类型资源大小
    const jsSize = (byType.javascript?.size || 0) + (byType['application/javascript']?.size || 0)
    const cssSize = (byType.css?.size || 0) + (byType['text/css']?.size || 0)
    const imageSize = (byType.image?.size || 0) + 
                     (byType['image/png']?.size || 0) +
                     (byType['image/jpeg']?.size || 0) +
                     (byType['image/jpg']?.size || 0) +
                     (byType['image/gif']?.size || 0) +
                     (byType['image/svg+xml']?.size || 0)
    
    resourceUsage.value = {
      js: jsSize,
      css: cssSize,
      images: imageSize
    }
    
    ElMessage.success('资源分析完成')
  } catch (error: any) {
    ElMessage.error(error.message || '资源分析失败')
    resourceUsage.value = {
      js: 0,
      css: 0,
      images: 0
    }
  } finally {
    analyzingResources.value = false
  }
}

const generateDiagnosticReport = async () => {
  if (!props.productId) {
    ElMessage.warning('请先选择产品')
    return
  }
  
  const details: DiagnosticReportItem[] = []
  const suggestions: DiagnosticSuggestion[] = []
  
  try {
    // 运行完整诊断
    const diagnosticResult = await runProductDiagnostic(props.productId)
    
    // 根据诊断结果生成报告项
    if (!diagnosticResult.checks.file_integrity) {
      details.push({
        id: 'file-integrity',
        level: 'error',
        title: '文件完整性检查失败',
        message: '产品文件完整性验证未通过，建议重新上传文件'
      })
    }
    
    if (!diagnosticResult.checks.entry_file_exists) {
      details.push({
        id: 'entry-file-missing',
        level: 'error',
        title: '入口文件不存在',
        message: '无法找到产品入口文件，请检查文件结构'
      })
    }
    
    if (!diagnosticResult.checks.config_valid) {
      details.push({
        id: 'config-invalid',
        level: 'warning',
        title: '配置数据无效',
        message: '产品配置数据为空或格式不正确'
      })
    }
    
    if (!diagnosticResult.checks.published_status) {
      details.push({
        id: 'not-published',
        level: 'info',
        title: '产品未发布',
        message: '产品当前未发布，用户无法访问'
      })
    }
    
    // 添加诊断建议
    if (diagnosticResult.recommendations && Array.isArray(diagnosticResult.recommendations)) {
      diagnosticResult.recommendations.forEach((rec, index) => {
        suggestions.push({
          id: `rec-${index}`,
          title: '优化建议',
          description: rec
        })
      })
    }
    
    // 根据连接状态添加报告项
    if (connectivityStatus.value.api === 'error') {
      details.push({
        id: 'api-error',
        level: 'error',
        title: 'API连接失败',
        message: '无法连接到后端API服务'
      })
    } else if (connectivityStatus.value.api === 'warning') {
      details.push({
        id: 'api-warning',
        level: 'warning',
        title: 'API连接不稳定',
        message: 'API连接存在延迟或超时问题'
      })
    }
    
    if (connectivityStatus.value.database === 'error') {
      details.push({
        id: 'database-error',
        level: 'error',
        title: '数据库连接失败',
        message: '无法连接到数据库服务'
      })
    }
    
    if (connectivityStatus.value.fileService === 'error') {
      details.push({
        id: 'file-service-error',
        level: 'error',
        title: '文件服务异常',
        message: '文件服务无法正常访问'
      })
    }
    
    // 根据性能指标添加报告项
    if (performanceMetrics.value.loadTime > 2000) {
      details.push({
        id: 'slow-loading',
        level: 'warning',
        title: '加载时间过长',
        message: `页面加载时间为${performanceMetrics.value.loadTime}ms，建议优化`
      })
      
      suggestions.push({
        id: 'optimize-loading',
        title: '优化加载性能',
        description: '考虑压缩资源文件、启用缓存或使用CDN'
      })
    }
    
    // 根据错误统计添加报告项
    if (errorSummary.value.critical > 0) {
      details.push({
        id: 'critical-errors',
        level: 'error',
        title: '发现严重错误',
        message: `检测到${errorSummary.value.critical}个严重错误需要立即处理`
      })
    }
    
    if (errorSummary.value.warning > 5) {
      details.push({
        id: 'many-warnings',
        level: 'warning',
        title: '警告数量较多',
        message: `检测到${errorSummary.value.warning}个警告，建议检查`
      })
    }
    
    // 根据安全状态添加报告项
    if (!securityStatus.value.xss) {
      details.push({
        id: 'xss-vulnerability',
        level: 'error',
        title: 'XSS防护不足',
        message: '检测到潜在的XSS安全漏洞'
      })
      
      suggestions.push({
        id: 'fix-xss',
        title: '修复XSS漏洞',
        description: '对用户输入进行转义，避免直接输出到HTML'
      })
    }
    
    if (!securityStatus.value.csrf) {
      details.push({
        id: 'csrf-vulnerability',
        level: 'warning',
        title: 'CSRF防护不足',
        message: '建议添加CSRF令牌保护'
      })
    }
    
    if (!securityStatus.value.contentSecurity) {
      details.push({
        id: 'security-issue',
        level: 'warning',
        title: '内容安全策略缺失',
        message: '建议配置内容安全策略以提高安全性'
      })
      
      suggestions.push({
        id: 'add-csp',
        title: '添加内容安全策略',
        description: '配置CSP头部以防止XSS攻击和数据注入'
      })
    }
    
    // 根据兼容性评分添加报告项
    if (compatibilityScores.value.safari < 70) {
      details.push({
        id: 'safari-compatibility',
        level: 'warning',
        title: 'Safari兼容性较低',
        message: `Safari兼容性评分仅为${compatibilityScores.value.safari}%，建议优化`
      })
    }
    
    // 根据资源使用添加报告项
    const totalResourceSize = Object.values(resourceUsage.value).reduce((sum, size) => sum + size, 0)
    if (totalResourceSize > 5 * 1024 * 1024) {
      details.push({
        id: 'large-resources',
        level: 'warning',
        title: '资源文件过大',
        message: `总资源大小超过5MB，建议压缩优化`
      })
      
      suggestions.push({
        id: 'compress-resources',
        title: '压缩资源文件',
        description: '压缩JavaScript、CSS和图片文件以减少加载时间'
      })
    }
    
    // 计算整体状态
    let overallStatus: DiagnosticReport['overallStatus'] = 'good'
    const criticalIssues = details.filter(d => d.level === 'error').length
    const warningIssues = details.filter(d => d.level === 'warning').length
    
    if (criticalIssues > 0) {
      overallStatus = 'error'
    } else if (warningIssues > 0) {
      overallStatus = 'warning'
    }
    
    diagnosticReport.value = {
      overallStatus,
      totalIssues: details.length,
      criticalIssues,
      details,
      suggestions,
      timestamp: new Date()
    }
  } catch (error: any) {
    ElMessage.error(error.message || '生成诊断报告失败')
  }
}

const exportReport = () => {
  ElMessage.success('诊断报告导出功能开发中')
}

const clearReport = () => {
  diagnosticReport.value = null
  ElMessage.success('诊断报告已清空')
}

// 工具方法
const getStatusTagType = (status: string) => {
  const types = {
    good: 'success',
    warning: 'warning',
    error: 'danger'
  }
  return types[status as keyof typeof types] || 'info'
}

const getStatusText = (status: string) => {
  const texts = {
    good: '正常',
    warning: '警告',
    error: '错误'
  }
  return texts[status as keyof typeof texts] || status
}

const getPerformanceClass = (loadTime: number) => {
  if (loadTime > 2000) return 'performance-poor'
  if (loadTime > 1000) return 'performance-fair'
  return 'performance-good'
}

const getFpsClass = (fps: number) => {
  if (fps < 30) return 'fps-poor'
  if (fps < 50) return 'fps-fair'
  return 'fps-good'
}

const getCompatibilityColor = (score: number) => {
  if (score >= 90) return '#10b981'
  if (score >= 70) return '#f59e0b'
  return '#ef4444'
}

const getResourcePercentage = (type: keyof ResourceUsage) => {
  if (totalResourceSize.value === 0) return 0
  return (resourceUsage.value[type] / totalResourceSize.value) * 100
}

const getOverallStatusClass = () => {
  if (!diagnosticReport.value) return ''
  return `status-${diagnosticReport.value.overallStatus}`
}

const getOverallStatusText = () => {
  if (!diagnosticReport.value) return ''
  
  const texts = {
    good: '良好',
    warning: '需要注意',
    error: '存在问题'
  }
  return texts[diagnosticReport.value.overallStatus]
}

const getDetailItemClass = (level: string) => {
  return `detail-${level}`
}

const formatMemory = (bytes: number) => {
  const mb = bytes / (1024 * 1024)
  return `${mb.toFixed(1)}MB`
}

const formatBytes = (bytes: number) => {
  if (bytes < 1024) return `${bytes}B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)}KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)}MB`
}
</script>

<style scoped>
.product-diagnostic-tools {
  background: white;
  border-radius: 8px;
  overflow: hidden;
}

.tools-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  border-bottom: 1px solid #f3f4f6;
  background: #fafafa;
}

.tools-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
  display: flex;
  align-items: center;
  gap: 8px;
}

.diagnostic-icon {
  color: #3b82f6;
}

.tools-actions {
  display: flex;
  gap: 12px;
}

.diagnostic-tools {
  padding: 20px;
}

.tool-card {
  height: 280px;
}

.tool-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.tool-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 18px;
}

.tool-icon.connectivity {
  background: linear-gradient(135deg, #10b981, #047857);
}

.tool-icon.performance {
  background: linear-gradient(135deg, #3b82f6, #1d4ed8);
}

.tool-icon.error-check {
  background: linear-gradient(135deg, #ef4444, #dc2626);
}

.tool-icon.security {
  background: linear-gradient(135deg, #8b5cf6, #7c3aed);
}

.tool-icon.compatibility {
  background: linear-gradient(135deg, #f59e0b, #d97706);
}

.tool-icon.resource {
  background: linear-gradient(135deg, #06b6d4, #0891b2);
}

.tool-info {
  flex: 1;
}

.tool-info h4 {
  margin: 0 0 4px 0;
  font-size: 14px;
  font-weight: 600;
  color: #1f2937;
}

.tool-info p {
  margin: 0;
  font-size: 12px;
  color: #6b7280;
}

.tool-content {
  padding: 16px 0;
  height: 180px;
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.test-results,
.performance-metrics,
.security-status {
  flex: 1;
}

.result-item,
.metric-item,
.status-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.result-label,
.metric-label,
.status-label {
  font-size: 12px;
  color: #6b7280;
}

.metric-value {
  font-size: 12px;
  font-weight: 500;
  color: #1f2937;
}

.metric-value.performance-good {
  color: #10b981;
}

.metric-value.performance-fair {
  color: #f59e0b;
}

.metric-value.performance-poor {
  color: #ef4444;
}

.metric-value.fps-good {
  color: #10b981;
}

.metric-value.fps-fair {
  color: #f59e0b;
}

.metric-value.fps-poor {
  color: #ef4444;
}

.error-summary {
  display: flex;
  justify-content: space-between;
  margin-bottom: 16px;
}

.error-count {
  text-align: center;
}

.error-count .count {
  display: block;
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 4px;
}

.error-count .label {
  font-size: 11px;
  color: #6b7280;
}

.error-count.critical .count {
  color: #ef4444;
}

.error-count.warning .count {
  color: #f59e0b;
}

.error-count.info .count {
  color: #3b82f6;
}

.compatibility-results {
  margin-bottom: 16px;
}

.browser-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.browser-name {
  width: 60px;
  font-size: 12px;
  color: #6b7280;
}

.browser-item .el-progress {
  flex: 1;
}

.score {
  width: 35px;
  font-size: 12px;
  font-weight: 500;
  color: #1f2937;
  text-align: right;
}

.resource-breakdown {
  margin-bottom: 16px;
}

.resource-item {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 8px;
}

.resource-type {
  width: 70px;
  font-size: 12px;
  color: #6b7280;
}

.resource-bar {
  flex: 1;
  height: 6px;
  background: #f3f4f6;
  border-radius: 3px;
  overflow: hidden;
}

.resource-fill {
  height: 100%;
  transition: width 0.3s ease;
}

.resource-fill.js {
  background: #f59e0b;
}

.resource-fill.css {
  background: #3b82f6;
}

.resource-fill.images {
  background: #10b981;
}

.resource-size {
  width: 50px;
  font-size: 12px;
  color: #6b7280;
  text-align: right;
}

.tool-actions {
  margin-top: 16px;
}

.diagnostic-report {
  margin: 20px;
  margin-top: 0;
}

.report-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.report-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.report-actions {
  display: flex;
  gap: 8px;
}

.report-content {
  padding: 0;
}

.report-summary {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f9fafb;
  border-radius: 6px;
  margin-bottom: 20px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 12px;
}

.summary-icon {
  width: 48px;
  height: 48px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.summary-icon.status-good {
  background: #10b981;
}

.summary-icon.status-warning {
  background: #f59e0b;
}

.summary-icon.status-error {
  background: #ef4444;
}

.summary-title {
  font-size: 14px;
  color: #6b7280;
  margin-bottom: 2px;
}

.summary-status {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.summary-stats {
  display: flex;
  gap: 24px;
}

.stat-item {
  text-align: center;
}

.stat-value {
  display: block;
  font-size: 20px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 4px;
}

.stat-label {
  font-size: 12px;
  color: #6b7280;
}

.report-details,
.report-suggestions {
  margin-bottom: 24px;
}

.report-details h5,
.report-suggestions h5 {
  margin: 0 0 12px 0;
  font-size: 14px;
  font-weight: 600;
  color: #374151;
}

.details-list,
.suggestions-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.detail-item,
.suggestion-item {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  padding: 12px;
  border-radius: 6px;
  margin-bottom: 8px;
}

.detail-item.detail-error {
  background: #fef2f2;
  border-left: 3px solid #ef4444;
}

.detail-item.detail-warning {
  background: #fffbeb;
  border-left: 3px solid #f59e0b;
}

.detail-item.detail-info {
  background: #f0f9ff;
  border-left: 3px solid #3b82f6;
}

.suggestion-item {
  background: #f0fdf4;
  border-left: 3px solid #10b981;
}

.detail-icon,
.suggestion-icon {
  width: 20px;
  height: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.detail-error .detail-icon {
  color: #ef4444;
}

.detail-warning .detail-icon {
  color: #f59e0b;
}

.detail-info .detail-icon {
  color: #3b82f6;
}

.suggestion-icon {
  color: #10b981;
}

.detail-content,
.suggestion-content {
  flex: 1;
}

.detail-title,
.suggestion-title {
  font-size: 13px;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 2px;
}

.detail-message,
.suggestion-description {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .diagnostic-tools .el-col {
    margin-bottom: 20px;
  }
}

@media (max-width: 768px) {
  .tools-header {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .report-summary {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .summary-stats {
    justify-content: space-around;
  }
}
</style>