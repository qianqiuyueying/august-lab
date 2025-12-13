<template>
  <div class="product-api-manager">
    <!-- API配置卡片 -->
    <el-card class="api-config-card">
      <template #header>
        <div class="card-header">
          <h3>API配置</h3>
          <el-button
            type="primary"
            size="small"
            @click="loadAPIConfig"
            :loading="loading"
          >
            <el-icon><Refresh /></el-icon>
            刷新
          </el-button>
        </div>
      </template>
      
      <el-form
        ref="configFormRef"
        :model="apiConfig"
        :rules="configRules"
        label-width="120px"
      >
        <el-form-item label="API密钥" prop="api_key">
          <el-input
            v-model="apiConfig.api_key"
            readonly
            class="api-key-input"
          >
            <template #append>
              <el-button @click="copyAPIKey" size="small">
                <el-icon><CopyDocument /></el-icon>
                复制
              </el-button>
            </template>
          </el-input>
        </el-form-item>
        
        <el-form-item label="允许的域名" prop="allowed_origins">
          <el-tag
            v-for="(origin, index) in apiConfig.allowed_origins"
            :key="index"
            closable
            @close="removeOrigin(index)"
            class="origin-tag"
          >
            {{ origin }}
          </el-tag>
          
          <el-input
            v-if="showOriginInput"
            ref="originInputRef"
            v-model="newOrigin"
            size="small"
            class="origin-input"
            @keyup.enter="addOrigin"
            @blur="addOrigin"
          />
          
          <el-button
            v-else
            size="small"
            @click="showAddOrigin"
            class="add-origin-btn"
          >
            <el-icon><Plus /></el-icon>
            添加域名
          </el-button>
        </el-form-item>
        
        <el-form-item label="速率限制" prop="rate_limit">
          <el-input-number
            v-model="apiConfig.rate_limit"
            :min="1"
            :max="10000"
            :step="10"
            controls-position="right"
          />
          <span class="form-help">每分钟最大请求数</span>
        </el-form-item>
        
        <el-form-item label="默认权限" prop="permissions">
          <el-checkbox-group v-model="apiConfig.permissions">
            <el-checkbox label="read">读取权限</el-checkbox>
            <el-checkbox label="write">写入权限</el-checkbox>
            <el-checkbox label="admin">管理权限</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
        
        <el-form-item>
          <el-button
            type="primary"
            @click="saveAPIConfig"
            :loading="saving"
          >
            保存配置
          </el-button>
          <el-button @click="resetConfig">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>
    
    <!-- API令牌管理 -->
    <el-card class="api-tokens-card">
      <template #header>
        <div class="card-header">
          <h3>API令牌管理</h3>
          <el-button
            type="primary"
            size="small"
            @click="showCreateTokenDialog = true"
          >
            <el-icon><Plus /></el-icon>
            创建令牌
          </el-button>
        </div>
      </template>
      
      <el-table
        :data="apiTokens"
        v-loading="loadingTokens"
        class="tokens-table"
      >
        <el-table-column prop="token" label="令牌" width="200">
          <template #default="{ row }">
            <code class="token-display">{{ maskToken(row.token) }}</code>
          </template>
        </el-table-column>
        
        <el-table-column prop="permissions" label="权限">
          <template #default="{ row }">
            <el-tag
              v-for="perm in row.permissions"
              :key="perm"
              size="small"
              class="permission-tag"
            >
              {{ getPermissionLabel(perm) }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="expires_at" label="过期时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.expires_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="usage_count" label="使用次数" width="100" />
        
        <el-table-column prop="last_used_at" label="最后使用" width="180">
          <template #default="{ row }">
            {{ row.last_used_at ? formatDate(row.last_used_at) : '未使用' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button
              type="danger"
              size="small"
              @click="revokeToken(row)"
            >
              撤销
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
    
    <!-- API调用日志 -->
    <el-card class="api-calls-card">
      <template #header>
        <div class="card-header">
          <h3>API调用日志</h3>
          <div class="header-actions">
            <el-select
              v-model="callsFilter.status_code"
              placeholder="状态码"
              clearable
              size="small"
              style="width: 120px; margin-right: 8px"
            >
              <el-option label="200" :value="200" />
              <el-option label="400" :value="400" />
              <el-option label="401" :value="401" />
              <el-option label="500" :value="500" />
            </el-select>
            
            <el-button
              size="small"
              @click="loadAPICalls"
              :loading="loadingCalls"
            >
              <el-icon><Refresh /></el-icon>
              刷新
            </el-button>
          </div>
        </div>
      </template>
      
      <el-table
        :data="apiCalls"
        v-loading="loadingCalls"
        class="calls-table"
      >
        <el-table-column prop="endpoint" label="端点" width="200" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="getMethodTagType(row.method)" size="small">
              {{ row.method }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="status_code" label="状态码" width="100">
          <template #default="{ row }">
            <el-tag :type="getStatusTagType(row.status_code)" size="small">
              {{ row.status_code }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="response_time" label="响应时间" width="100">
          <template #default="{ row }">
            {{ row.response_time }}ms
          </template>
        </el-table-column>
        
        <el-table-column prop="client_ip" label="客户端IP" width="120" />
        
        <el-table-column prop="timestamp" label="时间" width="180">
          <template #default="{ row }">
            {{ formatDate(row.timestamp) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="error_message" label="错误信息" min-width="200">
          <template #default="{ row }">
            <span v-if="row.error_message" class="error-message">
              {{ row.error_message }}
            </span>
            <span v-else class="success-message">成功</span>
          </template>
        </el-table-column>
      </el-table>
      
      <div class="pagination-wrapper">
        <el-pagination
          v-model:current-page="callsPagination.page"
          v-model:page-size="callsPagination.size"
          :total="callsPagination.total"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          @size-change="loadAPICalls"
          @current-change="loadAPICalls"
        />
      </div>
    </el-card>
    
    <!-- 创建令牌对话框 -->
    <el-dialog
      v-model="showCreateTokenDialog"
      title="创建API令牌"
      width="500px"
    >
      <el-form
        ref="tokenFormRef"
        :model="newTokenForm"
        :rules="tokenRules"
        label-width="100px"
      >
        <el-form-item label="权限" prop="permissions">
          <el-checkbox-group v-model="newTokenForm.permissions">
            <el-checkbox label="read">读取权限</el-checkbox>
            <el-checkbox label="write">写入权限</el-checkbox>
            <el-checkbox label="admin">管理权限</el-checkbox>
          </el-checkbox-group>
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateTokenDialog = false">取消</el-button>
        <el-button
          type="primary"
          @click="createToken"
          :loading="creatingToken"
        >
          创建
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 令牌创建成功对话框 -->
    <el-dialog
      v-model="showTokenResultDialog"
      title="令牌创建成功"
      width="600px"
    >
      <el-alert
        title="请妥善保存以下令牌，关闭对话框后将无法再次查看"
        type="warning"
        :closable="false"
        class="token-warning"
      />
      
      <div class="token-result">
        <label>API令牌：</label>
        <el-input
          v-model="createdToken.token"
          readonly
          class="token-input"
        >
          <template #append>
            <el-button @click="copyToken" size="small">
              <el-icon><CopyDocument /></el-icon>
              复制
            </el-button>
          </template>
        </el-input>
        
        <div class="token-info">
          <p><strong>权限：</strong>{{ createdToken.permissions?.join(', ') }}</p>
          <p><strong>过期时间：</strong>{{ formatDate(createdToken.expires_at) }}</p>
        </div>
      </div>
      
      <template #footer>
        <el-button type="primary" @click="showTokenResultDialog = false">
          我已保存
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Refresh,
  CopyDocument,
  Plus
} from '@element-plus/icons-vue'
import { useProductAPI } from '../../frontend/composables/useProductAPI'
import type { ProductAPIConfig, ProductAPICall, ProductAPIToken } from '../../frontend/composables/useProductAPI'

interface Props {
  productId: number
}

const props = defineProps<Props>()

// 响应式数据
const loading = ref(false)
const saving = ref(false)
const loadingTokens = ref(false)
const loadingCalls = ref(false)
const creatingToken = ref(false)

const showCreateTokenDialog = ref(false)
const showTokenResultDialog = ref(false)
const showOriginInput = ref(false)
const newOrigin = ref('')

const configFormRef = ref()
const tokenFormRef = ref()
const originInputRef = ref()

const apiConfig = reactive<ProductAPIConfig>({
  product_id: props.productId,
  api_key: '',
  allowed_origins: ['*'],
  rate_limit: 100,
  permissions: ['read']
})

const newTokenForm = reactive({
  permissions: ['read']
})

const createdToken = ref<ProductAPIToken>({
  token: '',
  expires_at: '',
  permissions: [],
  product_id: props.productId
})

const apiTokens = ref<ProductAPIToken[]>([])
const apiCalls = ref<ProductAPICall[]>([])

const callsFilter = reactive({
  status_code: null as number | null
})

const callsPagination = reactive({
  page: 1,
  size: 20,
  total: 0
})

// 使用组合式函数
const {
  generateAPIToken,
  validateAPIToken,
  revokeAPIToken,
  getAPIConfig,
  updateAPIConfig,
  getAPICallLogs
} = useProductAPI()

// 表单验证规则
const configRules = {
  rate_limit: [
    { required: true, message: '请输入速率限制', trigger: 'blur' },
    { type: 'number', min: 1, max: 10000, message: '速率限制必须在1-10000之间', trigger: 'blur' }
  ],
  permissions: [
    { required: true, message: '请选择至少一个权限', trigger: 'change' }
  ]
}

const tokenRules = {
  permissions: [
    { required: true, message: '请选择至少一个权限', trigger: 'change' }
  ]
}

// 方法
const loadAPIConfig = async () => {
  loading.value = true
  
  try {
    const config = await getAPIConfig(props.productId)
    Object.assign(apiConfig, config)
  } catch (error: any) {
    ElMessage.error(error.message || '加载API配置失败')
  } finally {
    loading.value = false
  }
}

const saveAPIConfig = async () => {
  if (!configFormRef.value) return
  
  const valid = await configFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  saving.value = true
  
  try {
    const updatedConfig = await updateAPIConfig(props.productId, {
      allowed_origins: apiConfig.allowed_origins,
      rate_limit: apiConfig.rate_limit,
      permissions: apiConfig.permissions
    })
    
    Object.assign(apiConfig, updatedConfig)
    ElMessage.success('API配置保存成功')
  } catch (error: any) {
    ElMessage.error(error.message || '保存API配置失败')
  } finally {
    saving.value = false
  }
}

const resetConfig = () => {
  loadAPIConfig()
}

const copyAPIKey = async () => {
  try {
    await navigator.clipboard.writeText(apiConfig.api_key)
    ElMessage.success('API密钥已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const showAddOrigin = () => {
  showOriginInput.value = true
  nextTick(() => {
    originInputRef.value?.focus()
  })
}

const addOrigin = () => {
  if (newOrigin.value && newOrigin.value.trim()) {
    const origin = newOrigin.value.trim()
    if (!apiConfig.allowed_origins.includes(origin)) {
      apiConfig.allowed_origins.push(origin)
    }
    newOrigin.value = ''
  }
  showOriginInput.value = false
}

const removeOrigin = (index: number) => {
  apiConfig.allowed_origins.splice(index, 1)
}

const createToken = async () => {
  if (!tokenFormRef.value) return
  
  const valid = await tokenFormRef.value.validate().catch(() => false)
  if (!valid) return
  
  creatingToken.value = true
  
  try {
    const token = await generateAPIToken(props.productId, newTokenForm.permissions)
    
    createdToken.value = token
    showCreateTokenDialog.value = false
    showTokenResultDialog.value = true
    
    // 重新加载令牌列表
    loadAPITokens()
    
    ElMessage.success('API令牌创建成功')
  } catch (error: any) {
    ElMessage.error(error.message || '创建API令牌失败')
  } finally {
    creatingToken.value = false
  }
}

const copyToken = async () => {
  try {
    await navigator.clipboard.writeText(createdToken.value.token)
    ElMessage.success('令牌已复制到剪贴板')
  } catch (error) {
    ElMessage.error('复制失败，请手动复制')
  }
}

const revokeToken = async (token: ProductAPIToken) => {
  try {
    await ElMessageBox.confirm(
      '确定要撤销这个API令牌吗？撤销后将无法恢复。',
      '确认撤销',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await revokeAPIToken(props.productId, token.token)
    
    // 重新加载令牌列表
    loadAPITokens()
    
    ElMessage.success('API令牌已撤销')
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '撤销API令牌失败')
    }
  }
}

const loadAPITokens = async () => {
  loadingTokens.value = true
  
  try {
    // 这里需要实现获取令牌列表的API
    // 暂时使用模拟数据
    apiTokens.value = []
  } catch (error: any) {
    ElMessage.error(error.message || '加载API令牌失败')
  } finally {
    loadingTokens.value = false
  }
}

const loadAPICalls = async () => {
  loadingCalls.value = true
  
  try {
    const calls = await getAPICallLogs(props.productId, {
      skip: (callsPagination.page - 1) * callsPagination.size,
      limit: callsPagination.size,
      status_code: callsFilter.status_code || undefined
    })
    
    apiCalls.value = calls
    // 这里需要从API获取总数
    callsPagination.total = calls.length
  } catch (error: any) {
    ElMessage.error(error.message || '加载API调用日志失败')
  } finally {
    loadingCalls.value = false
  }
}

// 工具方法
const maskToken = (token: string) => {
  if (token.length <= 8) return token
  return token.substring(0, 4) + '****' + token.substring(token.length - 4)
}

const getPermissionLabel = (permission: string) => {
  const labels: Record<string, string> = {
    read: '读取',
    write: '写入',
    admin: '管理'
  }
  return labels[permission] || permission
}

const getMethodTagType = (method: string) => {
  const types: Record<string, string> = {
    GET: 'success',
    POST: 'primary',
    PUT: 'warning',
    DELETE: 'danger'
  }
  return types[method] || ''
}

const getStatusTagType = (statusCode: number) => {
  if (statusCode >= 200 && statusCode < 300) return 'success'
  if (statusCode >= 400 && statusCode < 500) return 'warning'
  if (statusCode >= 500) return 'danger'
  return ''
}

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  return new Date(dateString).toLocaleString('zh-CN')
}

// 生命周期
onMounted(() => {
  loadAPIConfig()
  loadAPITokens()
  loadAPICalls()
})
</script>

<style scoped>
.product-api-manager {
  display: flex;
  flex-direction: column;
  gap: 24px;
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

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.api-key-input {
  font-family: 'Courier New', monospace;
}

.origin-tag {
  margin-right: 8px;
  margin-bottom: 8px;
}

.origin-input {
  width: 120px;
  margin-right: 8px;
}

.add-origin-btn {
  margin-bottom: 8px;
}

.form-help {
  margin-left: 8px;
  font-size: 12px;
  color: #6b7280;
}

.permission-tag {
  margin-right: 4px;
}

.token-display {
  font-family: 'Courier New', monospace;
  font-size: 12px;
  background: #f3f4f6;
  padding: 2px 4px;
  border-radius: 4px;
}

.error-message {
  color: #ef4444;
  font-size: 12px;
}

.success-message {
  color: #10b981;
  font-size: 12px;
}

.pagination-wrapper {
  margin-top: 16px;
  display: flex;
  justify-content: center;
}

.token-warning {
  margin-bottom: 16px;
}

.token-result {
  margin: 16px 0;
}

.token-result label {
  display: block;
  margin-bottom: 8px;
  font-weight: 600;
  color: #1f2937;
}

.token-input {
  font-family: 'Courier New', monospace;
  margin-bottom: 16px;
}

.token-info p {
  margin: 8px 0;
  color: #6b7280;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .card-header {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .header-actions {
    justify-content: flex-end;
  }
}
</style>