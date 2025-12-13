<template>
  <div class="product-config-editor">
    <div class="config-header">
      <h3>产品配置</h3>
      <div class="config-actions">
        <el-button @click="resetToDefault" size="small">重置默认</el-button>
        <el-button @click="importConfig" size="small">导入配置</el-button>
        <el-button @click="exportConfig" size="small">导出配置</el-button>
        <el-button @click="validateCurrentConfig" type="primary" size="small">验证配置</el-button>
      </div>
    </div>
    
    <el-form
      ref="configFormRef"
      :model="configForm"
      :rules="configRules"
      label-width="120px"
      class="config-form"
    >
      <!-- 基本信息 -->
      <el-card class="config-section">
        <template #header>
          <span>基本信息</span>
        </template>
        
        <el-form-item label="产品类型" prop="type">
          <el-select v-model="configForm.type" @change="onTypeChange">
            <el-option label="静态网页" value="static" />
            <el-option label="单页应用" value="spa" />
            <el-option label="游戏应用" value="game" />
            <el-option label="工具应用" value="tool" />
          </el-select>
        </el-form-item>
        
        <el-form-item label="配置版本" prop="version">
          <el-input v-model="configForm.version" placeholder="1.0" />
        </el-form-item>
        
        <el-form-item label="标题" prop="metadata.title">
          <el-input v-model="configForm.metadata.title" placeholder="产品标题" />
        </el-form-item>
        
        <el-form-item label="描述" prop="metadata.description">
          <el-input
            v-model="configForm.metadata.description"
            type="textarea"
            :rows="3"
            placeholder="产品描述"
          />
        </el-form-item>
        
        <el-form-item label="作者" prop="metadata.author">
          <el-input v-model="configForm.metadata.author" placeholder="作者名称" />
        </el-form-item>
        
        <el-form-item label="版本号" prop="metadata.version">
          <el-input v-model="configForm.metadata.version" placeholder="1.0.0" />
        </el-form-item>
      </el-card>
      
      <!-- 运行时配置 -->
      <el-card class="config-section">
        <template #header>
          <span>运行时配置</span>
        </template>
        
        <el-form-item label="入口文件" prop="runtime.entryFile" required>
          <el-input v-model="configForm.runtime.entryFile" placeholder="index.html" />
        </el-form-item>
        
        <el-form-item label="基础URL" prop="runtime.baseUrl">
          <el-input v-model="configForm.runtime.baseUrl" placeholder="/" />
        </el-form-item>
        
        <el-form-item label="公共路径" prop="runtime.publicPath">
          <el-input v-model="configForm.runtime.publicPath" placeholder="/" />
        </el-form-item>
        
        <el-form-item label="环境变量">
          <div class="env-variables">
            <div
              v-for="(value, key, index) in configForm.runtime.environment"
              :key="index"
              class="env-item"
            >
              <el-input
                v-model="envKeys[index]"
                placeholder="变量名"
                class="env-key"
                @blur="updateEnvKey(index, envKeys[index])"
              />
              <el-input
                v-model="configForm.runtime.environment[key]"
                placeholder="变量值"
                class="env-value"
              />
              <el-button
                @click="removeEnvVariable(key)"
                type="danger"
                size="small"
                icon="Delete"
              />
            </div>
            <el-button @click="addEnvVariable" type="primary" size="small" icon="Plus">
              添加环境变量
            </el-button>
          </div>
        </el-form-item>
        
        <el-form-item label="功能特性">
          <el-select
            v-model="configForm.runtime.features"
            multiple
            filterable
            allow-create
            placeholder="选择或输入功能特性"
            class="full-width"
          >
            <el-option
              v-for="feature in commonFeatures"
              :key="feature"
              :label="feature"
              :value="feature"
            />
          </el-select>
        </el-form-item>
      </el-card>
      
      <!-- 显示配置 -->
      <el-card class="config-section">
        <template #header>
          <span>显示配置</span>
        </template>
        
        <el-form-item label="宽度">
          <el-radio-group v-model="displayWidthType" @change="onDisplaySizeChange">
            <el-radio label="auto">自动</el-radio>
            <el-radio label="fixed">固定</el-radio>
          </el-radio-group>
          <el-input-number
            v-if="displayWidthType === 'fixed'"
            v-model="configForm.display.width"
            :min="100"
            :max="3840"
            class="size-input"
          />
        </el-form-item>
        
        <el-form-item label="高度">
          <el-radio-group v-model="displayHeightType" @change="onDisplaySizeChange">
            <el-radio label="auto">自动</el-radio>
            <el-radio label="fixed">固定</el-radio>
          </el-radio-group>
          <el-input-number
            v-if="displayHeightType === 'fixed'"
            v-model="configForm.display.height"
            :min="100"
            :max="2160"
            class="size-input"
          />
        </el-form-item>
        
        <el-form-item label="宽高比" prop="display.aspectRatio">
          <el-input
            v-model="configForm.display.aspectRatio"
            placeholder="16:9"
            class="aspect-ratio-input"
          />
        </el-form-item>
        
        <el-form-item label="响应式设计">
          <el-switch v-model="configForm.display.responsive" />
        </el-form-item>
        
        <el-form-item label="全屏支持">
          <el-switch v-model="configForm.display.fullscreenSupport" />
        </el-form-item>
      </el-card>
      
      <!-- 权限配置 -->
      <el-card class="config-section">
        <template #header>
          <span>权限配置</span>
        </template>
        
        <el-form-item label="剪贴板访问">
          <el-switch v-model="configForm.permissions.clipboard" />
        </el-form-item>
        
        <el-form-item label="通知权限">
          <el-switch v-model="configForm.permissions.notifications" />
        </el-form-item>
        
        <el-form-item label="地理位置">
          <el-switch v-model="configForm.permissions.geolocation" />
        </el-form-item>
        
        <el-form-item label="存储权限">
          <div class="permission-group">
            <el-checkbox v-model="configForm.permissions.storage.localStorage">
              本地存储
            </el-checkbox>
            <el-checkbox v-model="configForm.permissions.storage.sessionStorage">
              会话存储
            </el-checkbox>
            <el-checkbox v-model="configForm.permissions.storage.indexedDB">
              IndexedDB
            </el-checkbox>
          </div>
        </el-form-item>
        
        <el-form-item label="网络权限">
          <div class="permission-group">
            <el-checkbox v-model="configForm.permissions.network.fetch">
              Fetch API
            </el-checkbox>
            <el-checkbox v-model="configForm.permissions.network.websocket">
              WebSocket
            </el-checkbox>
            <el-checkbox v-model="configForm.permissions.network.webrtc">
              WebRTC
            </el-checkbox>
          </div>
        </el-form-item>
      </el-card>
      
      <!-- 性能配置 -->
      <el-card class="config-section">
        <template #header>
          <span>性能配置</span>
        </template>
        
        <el-form-item label="预加载资源">
          <el-select
            v-model="configForm.performance.preload"
            multiple
            filterable
            allow-create
            placeholder="输入需要预加载的资源路径"
            class="full-width"
          />
        </el-form-item>
        
        <el-form-item label="懒加载资源">
          <el-select
            v-model="configForm.performance.lazy"
            multiple
            filterable
            allow-create
            placeholder="输入需要懒加载的资源路径"
            class="full-width"
          />
        </el-form-item>
        
        <el-form-item label="缓存配置">
          <div class="caching-config">
            <el-form-item label="启用缓存" class="inline-form-item">
              <el-switch v-model="configForm.performance.caching.enabled" />
            </el-form-item>
            
            <el-form-item
              v-if="configForm.performance.caching.enabled"
              label="缓存策略"
              class="inline-form-item"
            >
              <el-select v-model="configForm.performance.caching.strategy">
                <el-option label="缓存优先" value="cache-first" />
                <el-option label="网络优先" value="network-first" />
                <el-option label="过期重新验证" value="stale-while-revalidate" />
              </el-select>
            </el-form-item>
            
            <el-form-item
              v-if="configForm.performance.caching.enabled"
              label="最大缓存时间(秒)"
              class="inline-form-item"
            >
              <el-input-number
                v-model="configForm.performance.caching.maxAge"
                :min="0"
                :max="86400"
              />
            </el-form-item>
          </div>
        </el-form-item>
      </el-card>
      
      <!-- 集成配置 -->
      <el-card class="config-section">
        <template #header>
          <span>集成配置</span>
        </template>
        
        <el-form-item label="父页面通信">
          <el-switch v-model="configForm.integration.parentCommunication" />
        </el-form-item>
        
        <el-form-item label="数据绑定">
          <el-switch v-model="configForm.integration.dataBinding" />
        </el-form-item>
        
        <el-form-item label="事件转发">
          <el-select
            v-model="configForm.integration.eventForwarding"
            multiple
            filterable
            allow-create
            placeholder="选择需要转发的事件类型"
            class="full-width"
          >
            <el-option
              v-for="event in commonEvents"
              :key="event"
              :label="event"
              :value="event"
            />
          </el-select>
        </el-form-item>
      </el-card>
      
      <!-- 安全配置 -->
      <el-card class="config-section">
        <template #header>
          <span>安全配置</span>
        </template>
        
        <el-form-item label="沙箱权限">
          <el-select
            v-model="configForm.security.sandbox"
            multiple
            placeholder="选择沙箱权限"
            class="full-width"
          >
            <el-option
              v-for="permission in sandboxPermissions"
              :key="permission.value"
              :label="permission.label"
              :value="permission.value"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="内容安全策略" prop="security.csp">
          <el-input
            v-model="configForm.security.csp"
            type="textarea"
            :rows="3"
            placeholder="default-src 'self'; script-src 'self' 'unsafe-inline'"
          />
        </el-form-item>
        
        <el-form-item label="允许的来源">
          <el-select
            v-model="configForm.security.allowedOrigins"
            multiple
            filterable
            allow-create
            placeholder="输入允许的来源域名"
            class="full-width"
          />
        </el-form-item>
      </el-card>
    </el-form>
    
    <!-- 配置预览 -->
    <el-card class="config-preview" v-if="showPreview">
      <template #header>
        <span>配置预览</span>
        <el-button @click="showPreview = false" size="small" text>隐藏</el-button>
      </template>
      
      <el-input
        v-model="configJson"
        type="textarea"
        :rows="20"
        readonly
        class="config-json"
      />
    </el-card>
    
    <!-- 验证结果 -->
    <el-alert
      v-if="validationErrors.length > 0"
      title="配置验证失败"
      type="error"
      :closable="false"
      class="validation-alert"
    >
      <ul>
        <li v-for="error in validationErrors" :key="error">{{ error }}</li>
      </ul>
    </el-alert>
    
    <!-- 导入对话框 -->
    <el-dialog v-model="showImportDialog" title="导入配置" width="600px">
      <el-input
        v-model="importJson"
        type="textarea"
        :rows="15"
        placeholder="粘贴配置JSON..."
      />
      
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button @click="doImportConfig" type="primary">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { useProductConfig } from '../../frontend/composables/useProductConfig'
import type { Product } from '../../shared/types'

interface Props {
  product?: Product
  modelValue?: any
}

interface Emits {
  (e: 'update:modelValue', value: any): void
  (e: 'change', value: any): void
  (e: 'validate', result: { valid: boolean; errors: string[] }): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 使用配置管理
const {
  createDefaultConfig,
  loadConfigFromProduct,
  validateConfig,
  exportConfig,
  importConfig,
  resetConfig
} = useProductConfig()

// 响应式数据
const configFormRef = ref()
const configForm = reactive({
  type: 'static',
  version: '1.0',
  metadata: {
    title: '',
    description: '',
    author: '',
    version: '1.0.0'
  },
  runtime: {
    entryFile: 'index.html',
    baseUrl: '',
    publicPath: '/',
    environment: {} as Record<string, string>,
    features: [] as string[]
  },
  display: {
    width: 'auto' as number | 'auto',
    height: 'auto' as number | 'auto',
    aspectRatio: '',
    responsive: true,
    fullscreenSupport: false
  },
  permissions: {
    clipboard: false,
    notifications: false,
    geolocation: false,
    storage: {
      localStorage: true,
      sessionStorage: true,
      indexedDB: false
    },
    network: {
      fetch: false,
      websocket: false,
      webrtc: false
    }
  },
  performance: {
    preload: [] as string[],
    lazy: [] as string[],
    caching: {
      enabled: false,
      strategy: 'cache-first' as 'cache-first' | 'network-first' | 'stale-while-revalidate',
      maxAge: 3600
    }
  },
  integration: {
    parentCommunication: false,
    dataBinding: false,
    eventForwarding: [] as string[]
  },
  security: {
    sandbox: ['allow-scripts', 'allow-same-origin'] as string[],
    csp: '',
    allowedOrigins: [] as string[]
  }
})

const displayWidthType = ref<'auto' | 'fixed'>('auto')
const displayHeightType = ref<'auto' | 'fixed'>('auto')
const envKeys = ref<string[]>([])
const showPreview = ref(false)
const showImportDialog = ref(false)
const importJson = ref('')
const validationErrors = ref<string[]>([])

// 常用选项
const commonFeatures = [
  'responsive-design',
  'dark-mode',
  'offline-support',
  'pwa',
  'touch-support',
  'keyboard-shortcuts',
  'drag-drop',
  'file-upload',
  'real-time-sync'
]

const commonEvents = [
  'click',
  'keydown',
  'keyup',
  'mousemove',
  'touchstart',
  'touchmove',
  'touchend',
  'gamepad',
  'resize',
  'scroll'
]

const sandboxPermissions = [
  { label: '允许脚本', value: 'allow-scripts' },
  { label: '允许同源', value: 'allow-same-origin' },
  { label: '允许表单', value: 'allow-forms' },
  { label: '允许弹窗', value: 'allow-popups' },
  { label: '允许指针锁定', value: 'allow-pointer-lock' },
  { label: '允许全屏', value: 'allow-fullscreen' },
  { label: '允许下载', value: 'allow-downloads' },
  { label: '允许模态框', value: 'allow-modals' }
]

// 表单验证规则
const configRules = {
  type: [
    { required: true, message: '请选择产品类型', trigger: 'change' }
  ],
  version: [
    { required: true, message: '请输入配置版本', trigger: 'blur' }
  ],
  'runtime.entryFile': [
    { required: true, message: '请输入入口文件', trigger: 'blur' }
  ],
  'display.aspectRatio': [
    { pattern: /^\d+:\d+$/, message: '宽高比格式应为 "width:height"', trigger: 'blur' }
  ]
}

// 计算属性
const configJson = computed(() => {
  try {
    return JSON.stringify(configForm, null, 2)
  } catch {
    return ''
  }
})

// 方法
const initializeConfig = () => {
  if (props.product) {
    const config = loadConfigFromProduct(props.product)
    Object.assign(configForm, config)
  } else if (props.modelValue) {
    Object.assign(configForm, props.modelValue)
  } else {
    const defaultConfig = createDefaultConfig('static')
    Object.assign(configForm, defaultConfig)
  }
  
  // 初始化显示类型
  displayWidthType.value = typeof configForm.display.width === 'number' ? 'fixed' : 'auto'
  displayHeightType.value = typeof configForm.display.height === 'number' ? 'fixed' : 'auto'
  
  // 初始化环境变量键
  envKeys.value = Object.keys(configForm.runtime.environment)
}

const onTypeChange = (newType: string) => {
  const defaultConfig = createDefaultConfig(newType)
  
  // 保留用户已修改的配置
  const userConfig = { ...configForm }
  
  // 合并默认配置
  Object.assign(configForm, defaultConfig, {
    metadata: { ...defaultConfig.metadata, ...userConfig.metadata },
    runtime: { ...defaultConfig.runtime, ...userConfig.runtime },
    display: { ...defaultConfig.display, ...userConfig.display }
  })
}

const onDisplaySizeChange = () => {
  if (displayWidthType.value === 'auto') {
    configForm.display.width = 'auto'
  } else if (typeof configForm.display.width !== 'number') {
    configForm.display.width = 800
  }
  
  if (displayHeightType.value === 'auto') {
    configForm.display.height = 'auto'
  } else if (typeof configForm.display.height !== 'number') {
    configForm.display.height = 600
  }
}

const addEnvVariable = () => {
  const key = `VAR_${Object.keys(configForm.runtime.environment).length + 1}`
  configForm.runtime.environment[key] = ''
  envKeys.value.push(key)
}

const removeEnvVariable = (key: string) => {
  delete configForm.runtime.environment[key]
  const index = envKeys.value.indexOf(key)
  if (index > -1) {
    envKeys.value.splice(index, 1)
  }
}

const updateEnvKey = (index: number, newKey: string) => {
  const oldKey = envKeys.value[index]
  if (oldKey !== newKey && newKey) {
    const value = configForm.runtime.environment[oldKey]
    delete configForm.runtime.environment[oldKey]
    configForm.runtime.environment[newKey] = value
    envKeys.value[index] = newKey
  }
}

const validateCurrentConfig = async () => {
  try {
    await configFormRef.value?.validate()
    
    const validation = validateConfig(configForm as any)
    validationErrors.value = validation.errors
    
    emit('validate', validation)
    
    if (validation.valid) {
      ElMessage.success('配置验证通过')
    } else {
      ElMessage.error('配置验证失败，请检查错误信息')
    }
  } catch {
    ElMessage.error('表单验证失败')
  }
}

const resetToDefault = async () => {
  try {
    await ElMessageBox.confirm('确定要重置为默认配置吗？这将丢失当前的所有配置。', '确认重置', {
      type: 'warning'
    })
    
    const defaultConfig = createDefaultConfig(configForm.type)
    Object.assign(configForm, defaultConfig)
    
    ElMessage.success('已重置为默认配置')
  } catch {
    // 用户取消
  }
}

const exportConfig = () => {
  const configString = exportConfig(configForm as any)
  
  // 创建下载链接
  const blob = new Blob([configString], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `product-config-${configForm.type}.json`
  a.click()
  
  URL.revokeObjectURL(url)
  ElMessage.success('配置已导出')
}

const importConfig = () => {
  showImportDialog.value = true
  importJson.value = ''
}

const doImportConfig = () => {
  const result = importConfig(importJson.value)
  
  if (result.success && result.config) {
    Object.assign(configForm, result.config)
    showImportDialog.value = false
    ElMessage.success('配置导入成功')
  } else {
    ElMessage.error(`导入失败: ${result.error}`)
  }
}

// 监听配置变化
watch(
  () => configForm,
  (newConfig) => {
    emit('update:modelValue', newConfig)
    emit('change', newConfig)
  },
  { deep: true }
)

// 初始化
initializeConfig()
</script>

<style scoped>
.product-config-editor {
  max-width: 1000px;
  margin: 0 auto;
}

.config-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 1rem;
}

.config-header h3 {
  margin: 0;
  font-size: 1.25rem;
  font-weight: 600;
}

.config-actions {
  display: flex;
  gap: 0.5rem;
}

.config-section {
  margin-bottom: 1.5rem;
}

.config-form {
  max-width: none;
}

.env-variables {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 1rem;
  background: #fafafa;
}

.env-item {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
  align-items: center;
}

.env-key {
  flex: 1;
}

.env-value {
  flex: 2;
}

.permission-group {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}

.caching-config {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  padding: 1rem;
  background: #fafafa;
}

.inline-form-item {
  margin-bottom: 1rem;
}

.size-input {
  margin-left: 1rem;
  width: 120px;
}

.aspect-ratio-input {
  width: 120px;
}

.full-width {
  width: 100%;
}

.config-preview {
  margin-top: 1.5rem;
}

.config-json {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.validation-alert {
  margin-top: 1rem;
}

.validation-alert ul {
  margin: 0;
  padding-left: 1.5rem;
}

.validation-alert li {
  margin-bottom: 0.25rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .config-header {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .config-actions {
    justify-content: center;
  }
  
  .env-item {
    flex-direction: column;
  }
  
  .env-key,
  .env-value {
    flex: none;
  }
  
  .permission-group {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>