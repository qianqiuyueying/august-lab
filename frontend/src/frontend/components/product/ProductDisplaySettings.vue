<template>
  <div class="display-settings" :class="{ 'settings-visible': visible }">
    <!-- 设置触发按钮 -->
    <el-button
      class="settings-trigger"
      type="text"
      @click="toggleSettings"
      :class="{ 'trigger-active': visible }"
    >
      <el-icon><Setting /></el-icon>
    </el-button>
    
    <!-- 设置面板 -->
    <transition name="slide-fade">
      <div v-if="visible" class="settings-panel">
        <div class="panel-header">
          <h4>显示设置</h4>
          <el-button type="text" @click="visible = false" class="close-btn">
            <el-icon><Close /></el-icon>
          </el-button>
        </div>
        
        <div class="panel-content">
          <!-- 显示模式 -->
          <div class="setting-group">
            <label class="setting-label">显示模式</label>
            <el-radio-group v-model="displayMode" @change="onDisplayModeChange">
              <el-radio-button label="normal">窗口模式</el-radio-button>
              <el-radio-button label="fullscreen">全屏模式</el-radio-button>
            </el-radio-group>
          </div>
          
          <!-- 容器尺寸 -->
          <div class="setting-group">
            <label class="setting-label">容器尺寸</label>
            <el-select v-model="containerSize" @change="onContainerSizeChange">
              <el-option label="自适应" value="auto" />
              <el-option label="小屏 (800x600)" value="small" />
              <el-option label="中屏 (1024x768)" value="medium" />
              <el-option label="大屏 (1280x960)" value="large" />
              <el-option label="超宽 (1920x1080)" value="xlarge" />
              <el-option label="自定义" value="custom" />
            </el-select>
          </div>
          
          <!-- 自定义尺寸 -->
          <div v-if="containerSize === 'custom'" class="setting-group">
            <label class="setting-label">自定义尺寸</label>
            <div class="custom-size">
              <el-input-number
                v-model="customWidth"
                :min="320"
                :max="3840"
                :step="10"
                @change="onCustomSizeChange"
              />
              <span class="size-separator">×</span>
              <el-input-number
                v-model="customHeight"
                :min="240"
                :max="2160"
                :step="10"
                @change="onCustomSizeChange"
              />
            </div>
          </div>
          
          <!-- 缩放比例 -->
          <div class="setting-group">
            <label class="setting-label">缩放比例</label>
            <div class="zoom-control">
              <el-slider
                v-model="zoomLevel"
                :min="50"
                :max="200"
                :step="10"
                :format-tooltip="formatZoomTooltip"
                @change="onZoomChange"
              />
              <span class="zoom-value">{{ zoomLevel }}%</span>
            </div>
          </div>
          
          <!-- 主题模式 -->
          <div class="setting-group">
            <label class="setting-label">主题模式</label>
            <el-radio-group v-model="themeMode" @change="onThemeModeChange">
              <el-radio-button label="light">浅色</el-radio-button>
              <el-radio-button label="dark">深色</el-radio-button>
              <el-radio-button label="auto">自动</el-radio-button>
            </el-radio-group>
          </div>
          
          <!-- 性能选项 -->
          <div class="setting-group">
            <label class="setting-label">性能优化</label>
            <div class="performance-options">
              <el-checkbox v-model="enableGPU" @change="onPerformanceChange">
                启用GPU加速
              </el-checkbox>
              <el-checkbox v-model="enablePreload" @change="onPerformanceChange">
                预加载资源
              </el-checkbox>
              <el-checkbox v-model="enableCache" @change="onPerformanceChange">
                启用缓存
              </el-checkbox>
            </div>
          </div>
          
          <!-- 快捷操作 -->
          <div class="setting-group">
            <label class="setting-label">快捷操作</label>
            <div class="quick-actions">
              <el-button size="small" @click="resetSettings">
                <el-icon><RefreshLeft /></el-icon>
                重置设置
              </el-button>
              <el-button size="small" @click="saveAsPreset">
                <el-icon><Star /></el-icon>
                保存预设
              </el-button>
            </div>
          </div>
        </div>
      </div>
    </transition>
    
    <!-- 遮罩层 -->
    <div v-if="visible" class="settings-overlay" @click="visible = false" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Setting,
  Close,
  RefreshLeft,
  Star
} from '@element-plus/icons-vue'

interface DisplaySettings {
  displayMode: 'normal' | 'fullscreen'
  containerSize: 'auto' | 'small' | 'medium' | 'large' | 'xlarge' | 'custom'
  customWidth: number
  customHeight: number
  zoomLevel: number
  themeMode: 'light' | 'dark' | 'auto'
  enableGPU: boolean
  enablePreload: boolean
  enableCache: boolean
}

interface Emits {
  (e: 'settings-change', settings: DisplaySettings): void
  (e: 'display-mode-change', mode: 'normal' | 'fullscreen'): void
  (e: 'container-size-change', size: { width: number; height: number }): void
  (e: 'zoom-change', level: number): void
  (e: 'theme-change', theme: 'light' | 'dark' | 'auto'): void
}

const emit = defineEmits<Emits>()

// 响应式数据
const visible = ref(false)
const displayMode = ref<'normal' | 'fullscreen'>('normal')
const containerSize = ref<'auto' | 'small' | 'medium' | 'large' | 'xlarge' | 'custom'>('auto')
const customWidth = ref(1024)
const customHeight = ref(768)
const zoomLevel = ref(100)
const themeMode = ref<'light' | 'dark' | 'auto'>('auto')
const enableGPU = ref(true)
const enablePreload = ref(true)
const enableCache = ref(true)

// 计算属性
const currentSettings = computed<DisplaySettings>(() => ({
  displayMode: displayMode.value,
  containerSize: containerSize.value,
  customWidth: customWidth.value,
  customHeight: customHeight.value,
  zoomLevel: zoomLevel.value,
  themeMode: themeMode.value,
  enableGPU: enableGPU.value,
  enablePreload: enablePreload.value,
  enableCache: enableCache.value
}))

const containerDimensions = computed(() => {
  const sizeMap = {
    auto: { width: 0, height: 0 }, // 自适应
    small: { width: 800, height: 600 },
    medium: { width: 1024, height: 768 },
    large: { width: 1280, height: 960 },
    xlarge: { width: 1920, height: 1080 },
    custom: { width: customWidth.value, height: customHeight.value }
  }
  return sizeMap[containerSize.value]
})

// 方法
const toggleSettings = () => {
  visible.value = !visible.value
}

const onDisplayModeChange = (mode: 'normal' | 'fullscreen') => {
  emit('display-mode-change', mode)
  emitSettingsChange()
}

const onContainerSizeChange = () => {
  emit('container-size-change', containerDimensions.value)
  emitSettingsChange()
}

const onCustomSizeChange = () => {
  if (containerSize.value === 'custom') {
    emit('container-size-change', containerDimensions.value)
    emitSettingsChange()
  }
}

const onZoomChange = (level: number) => {
  emit('zoom-change', level)
  emitSettingsChange()
}

const onThemeModeChange = (theme: 'light' | 'dark' | 'auto') => {
  emit('theme-change', theme)
  emitSettingsChange()
}

const onPerformanceChange = () => {
  emitSettingsChange()
}

const emitSettingsChange = () => {
  emit('settings-change', currentSettings.value)
  saveSettings()
}

const formatZoomTooltip = (value: number) => {
  return `${value}%`
}

const resetSettings = () => {
  displayMode.value = 'normal'
  containerSize.value = 'auto'
  customWidth.value = 1024
  customHeight.value = 768
  zoomLevel.value = 100
  themeMode.value = 'auto'
  enableGPU.value = true
  enablePreload.value = true
  enableCache.value = true
  
  emitSettingsChange()
  ElMessage.success('设置已重置')
}

const saveAsPreset = () => {
  const presetName = `preset_${Date.now()}`
  const presets = JSON.parse(localStorage.getItem('product_display_presets') || '{}')
  presets[presetName] = currentSettings.value
  
  localStorage.setItem('product_display_presets', JSON.stringify(presets))
  ElMessage.success('预设已保存')
}

const saveSettings = () => {
  localStorage.setItem('product_display_settings', JSON.stringify(currentSettings.value))
}

const loadSettings = () => {
  try {
    const saved = localStorage.getItem('product_display_settings')
    if (saved) {
      const settings = JSON.parse(saved)
      displayMode.value = settings.displayMode || 'normal'
      containerSize.value = settings.containerSize || 'auto'
      customWidth.value = settings.customWidth || 1024
      customHeight.value = settings.customHeight || 768
      zoomLevel.value = settings.zoomLevel || 100
      themeMode.value = settings.themeMode || 'auto'
      enableGPU.value = settings.enableGPU !== false
      enablePreload.value = settings.enablePreload !== false
      enableCache.value = settings.enableCache !== false
    }
  } catch (error) {
    console.error('加载显示设置失败:', error)
  }
}

// 生命周期
onMounted(() => {
  loadSettings()
})

// 监听设置变化
watch(currentSettings, (settings) => {
  emit('settings-change', settings)
}, { deep: true })
</script>

<style scoped>
.display-settings {
  position: relative;
  z-index: 100;
}

.settings-trigger {
  position: fixed;
  top: 50%;
  right: 20px;
  transform: translateY(-50%);
  width: 48px;
  height: 48px;
  border-radius: 50%;
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border: 1px solid #e5e7eb;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  display: flex;
  align-items: center;
  justify-content: center;
  color: #6b7280;
  transition: all 0.3s ease;
  z-index: 101;
}

.settings-trigger:hover,
.trigger-active {
  background: #3b82f6;
  color: white;
  transform: translateY(-50%) scale(1.1);
}

.settings-panel {
  position: fixed;
  top: 50%;
  right: 80px;
  transform: translateY(-50%);
  width: 320px;
  max-height: 80vh;
  background: white;
  border-radius: 12px;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.15);
  border: 1px solid #e5e7eb;
  overflow: hidden;
  z-index: 102;
}

.settings-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.1);
  z-index: 100;
}

.panel-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid #f3f4f6;
  background: #f9fafb;
}

.panel-header h4 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.close-btn {
  color: #6b7280;
}

.panel-content {
  padding: 20px;
  max-height: calc(80vh - 60px);
  overflow-y: auto;
}

.setting-group {
  margin-bottom: 20px;
}

.setting-group:last-child {
  margin-bottom: 0;
}

.setting-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 8px;
}

.custom-size {
  display: flex;
  align-items: center;
  gap: 8px;
}

.size-separator {
  color: #6b7280;
  font-weight: 500;
}

.zoom-control {
  display: flex;
  align-items: center;
  gap: 12px;
}

.zoom-value {
  font-size: 14px;
  color: #6b7280;
  min-width: 40px;
  text-align: right;
}

.performance-options {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.quick-actions {
  display: flex;
  gap: 8px;
}

/* 动画效果 */
.slide-fade-enter-active,
.slide-fade-leave-active {
  transition: all 0.3s ease;
}

.slide-fade-enter-from {
  opacity: 0;
  transform: translateY(-50%) translateX(20px);
}

.slide-fade-leave-to {
  opacity: 0;
  transform: translateY(-50%) translateX(20px);
}

/* 响应式设计 */
@media (max-width: 768px) {
  .settings-trigger {
    right: 16px;
    width: 44px;
    height: 44px;
  }
  
  .settings-panel {
    right: 16px;
    left: 16px;
    width: auto;
    top: 20px;
    bottom: 20px;
    transform: none;
    max-height: none;
  }
  
  .panel-content {
    max-height: calc(100vh - 140px);
  }
  
  .custom-size {
    flex-direction: column;
    align-items: stretch;
  }
  
  .quick-actions {
    flex-direction: column;
  }
}

/* 深色主题支持 */
@media (prefers-color-scheme: dark) {
  .settings-trigger {
    background: rgba(31, 41, 55, 0.9);
    border-color: #374151;
    color: #d1d5db;
  }
  
  .settings-panel {
    background: #1f2937;
    border-color: #374151;
  }
  
  .panel-header {
    background: #111827;
    border-color: #374151;
  }
  
  .panel-header h4 {
    color: #f9fafb;
  }
  
  .setting-label {
    color: #e5e7eb;
  }
  
  .size-separator,
  .zoom-value {
    color: #9ca3af;
  }
}
</style>