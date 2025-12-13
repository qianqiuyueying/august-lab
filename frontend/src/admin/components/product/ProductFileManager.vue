<template>
  <div class="product-file-manager">
    <div class="file-manager-header">
      <h3>产品文件管理</h3>
      <div class="header-actions">
        <button @click="refreshFiles" class="btn btn-secondary">
          <i class="fas fa-sync-alt"></i> 刷新
        </button>
        <button @click="showUploadDialog = true" class="btn btn-primary">
          <i class="fas fa-upload"></i> 上传文件
        </button>
        <button @click="scanSecurity" class="btn btn-warning">
          <i class="fas fa-shield-alt"></i> 安全扫描
        </button>
      </div>
    </div>

    <!-- 文件列表 -->
    <div class="file-list">
      <div class="file-stats">
        <div class="stat-item">
          <span class="label">总文件数:</span>
          <span class="value">{{ fileStats.totalFiles }}</span>
        </div>
        <div class="stat-item">
          <span class="label">总大小:</span>
          <span class="value">{{ formatFileSize(fileStats.totalSize) }}</span>
        </div>
        <div class="stat-item">
          <span class="label">最后更新:</span>
          <span class="value">{{ formatDate(fileStats.lastUpdated) }}</span>
        </div>
      </div>

      <div class="file-table">
        <table>
          <thead>
            <tr>
              <th>文件名</th>
              <th>类型</th>
              <th>大小</th>
              <th>修改时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="file in files" :key="file.path">
              <td>
                <i :class="getFileIcon(file.type)"></i>
                {{ file.name }}
              </td>
              <td>{{ file.type }}</td>
              <td>{{ formatFileSize(file.size) }}</td>
              <td>{{ formatDate(file.modified) }}</td>
              <td>
                <button @click="downloadFile(file)" class="btn btn-sm btn-secondary">
                  <i class="fas fa-download"></i>
                </button>
                <button @click="deleteFile(file)" class="btn btn-sm btn-danger">
                  <i class="fas fa-trash"></i>
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 版本管理 -->
    <div class="version-manager">
      <h4>版本管理</h4>
      <div class="version-actions">
        <button @click="createVersion" class="btn btn-primary">
          <i class="fas fa-tag"></i> 创建版本
        </button>
        <button @click="loadVersions" class="btn btn-secondary">
          <i class="fas fa-history"></i> 查看历史
        </button>
      </div>

      <div class="version-list" v-if="versions.length > 0">
        <div v-for="version in versions" :key="version.version" class="version-item">
          <div class="version-info">
            <span class="version-number">{{ version.version }}</span>
            <span class="version-date">{{ formatDate(version.timestamp) }}</span>
            <span class="version-description">{{ version.description }}</span>
          </div>
          <div class="version-actions">
            <button @click="restoreVersion(version)" class="btn btn-sm btn-warning">
              <i class="fas fa-undo"></i> 恢复
            </button>
            <button @click="deleteVersion(version)" class="btn btn-sm btn-danger">
              <i class="fas fa-trash"></i> 删除
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 安全扫描结果 -->
    <div class="security-scan" v-if="scanResult">
      <h4>安全扫描结果</h4>
      <div class="scan-summary" :class="{ 'safe': scanResult.is_safe, 'unsafe': !scanResult.is_safe }">
        <i :class="scanResult.is_safe ? 'fas fa-check-circle' : 'fas fa-exclamation-triangle'"></i>
        <span>{{ scanResult.is_safe ? '安全' : '发现威胁' }}</span>
        <span class="scan-date">{{ formatDate(scanResult.scan_time) }}</span>
      </div>
      
      <div class="scan-details">
        <div class="scan-stats">
          <span>扫描文件: {{ scanResult.total_files }}</span>
          <span>安全文件: {{ scanResult.safe_files }}</span>
          <span>威胁数量: {{ scanResult.total_threats }}</span>
          <span>警告数量: {{ scanResult.total_warnings }}</span>
        </div>

        <div v-if="scanResult.total_threats > 0" class="threats">
          <h5>发现的威胁:</h5>
          <div v-for="file in scanResult.files.filter(f => !f.is_safe)" :key="file.file_path" class="threat-item">
            <strong>{{ file.file_path }}</strong>
            <ul>
              <li v-for="threat in file.threats" :key="threat" class="threat">{{ threat }}</li>
            </ul>
          </div>
        </div>
      </div>
    </div>

    <!-- 上传文件对话框 -->
    <div v-if="showUploadDialog" class="modal-overlay" @click="showUploadDialog = false">
      <div class="modal-content" @click.stop>
        <h4>上传文件</h4>
        <form @submit.prevent="uploadFile">
          <div class="form-group">
            <label>选择文件:</label>
            <input type="file" ref="fileInput" @change="handleFileSelect" required>
          </div>
          <div class="form-group">
            <label>文件描述:</label>
            <textarea v-model="uploadDescription" placeholder="可选的文件描述"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showUploadDialog = false" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary" :disabled="!selectedFile">上传</button>
          </div>
        </form>
      </div>
    </div>

    <!-- 创建版本对话框 -->
    <div v-if="showVersionDialog" class="modal-overlay" @click="showVersionDialog = false">
      <div class="modal-content" @click.stop>
        <h4>创建版本</h4>
        <form @submit.prevent="submitCreateVersion">
          <div class="form-group">
            <label>版本号:</label>
            <input v-model="newVersion.version" type="text" placeholder="例如: v1.0.1" required>
          </div>
          <div class="form-group">
            <label>版本描述:</label>
            <textarea v-model="newVersion.description" placeholder="版本更新说明"></textarea>
          </div>
          <div class="form-actions">
            <button type="button" @click="showVersionDialog = false" class="btn btn-secondary">取消</button>
            <button type="submit" class="btn btn-primary">创建</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script>
import { ref, reactive, onMounted } from 'vue'
import { useNotification } from '@/composables/useNotification'
import { productApi } from '@/api/products'

export default {
  name: 'ProductFileManager',
  props: {
    productId: {
      type: Number,
      required: true
    }
  },
  setup(props) {
    const { showSuccess, showError } = useNotification()
    
    // 响应式数据
    const files = ref([])
    const versions = ref([])
    const scanResult = ref(null)
    const fileStats = reactive({
      totalFiles: 0,
      totalSize: 0,
      lastUpdated: null
    })
    
    // 对话框状态
    const showUploadDialog = ref(false)
    const showVersionDialog = ref(false)
    
    // 上传相关
    const selectedFile = ref(null)
    const uploadDescription = ref('')
    const fileInput = ref(null)
    
    // 版本创建
    const newVersion = reactive({
      version: '',
      description: ''
    })
    
    // 方法
    const refreshFiles = async () => {
      try {
        const response = await productApi.getProductFiles(props.productId)
        files.value = response.files || []
        fileStats.totalFiles = response.total_files || 0
        fileStats.totalSize = response.total_size || 0
        fileStats.lastUpdated = new Date()
      } catch (error) {
        showError('获取文件列表失败: ' + error.message)
      }
    }
    
    const handleFileSelect = (event) => {
      selectedFile.value = event.target.files[0]
    }
    
    const uploadFile = async () => {
      if (!selectedFile.value) return
      
      try {
        const formData = new FormData()
        formData.append('file', selectedFile.value)
        if (uploadDescription.value) {
          formData.append('description', uploadDescription.value)
        }
        
        await productApi.uploadSingleFile(props.productId, formData)
        showSuccess('文件上传成功')
        
        // 重置表单
        showUploadDialog.value = false
        selectedFile.value = null
        uploadDescription.value = ''
        fileInput.value.value = ''
        
        // 刷新文件列表
        refreshFiles()
      } catch (error) {
        showError('文件上传失败: ' + error.message)
      }
    }
    
    const downloadFile = async (file) => {
      try {
        const response = await productApi.downloadFile(props.productId, file.path)
        
        // 创建下载链接
        const url = window.URL.createObjectURL(new Blob([response.data]))
        const link = document.createElement('a')
        link.href = url
        link.download = file.name
        document.body.appendChild(link)
        link.click()
        document.body.removeChild(link)
        window.URL.revokeObjectURL(url)
        
        showSuccess('文件下载成功')
      } catch (error) {
        showError('文件下载失败: ' + error.message)
      }
    }
    
    const deleteFile = async (file) => {
      if (!confirm(`确定要删除文件 "${file.name}" 吗？`)) return
      
      try {
        await productApi.deleteFile(props.productId, file.path)
        showSuccess('文件删除成功')
        refreshFiles()
      } catch (error) {
        showError('文件删除失败: ' + error.message)
      }
    }
    
    const scanSecurity = async () => {
      try {
        const response = await productApi.scanProductSecurity(props.productId)
        scanResult.value = response
        
        if (response.is_safe) {
          showSuccess('安全扫描完成，未发现威胁')
        } else {
          showError(`安全扫描发现 ${response.total_threats} 个威胁`)
        }
      } catch (error) {
        showError('安全扫描失败: ' + error.message)
      }
    }
    
    const loadVersions = async () => {
      try {
        const response = await productApi.getVersions(props.productId)
        versions.value = response.versions || []
      } catch (error) {
        showError('获取版本列表失败: ' + error.message)
      }
    }
    
    const createVersion = () => {
      showVersionDialog.value = true
    }
    
    const submitCreateVersion = async () => {
      try {
        await productApi.createVersion(props.productId, {
          version: newVersion.version,
          description: newVersion.description
        })
        
        showSuccess('版本创建成功')
        showVersionDialog.value = false
        
        // 重置表单
        newVersion.version = ''
        newVersion.description = ''
        
        // 刷新版本列表
        loadVersions()
      } catch (error) {
        showError('版本创建失败: ' + error.message)
      }
    }
    
    const restoreVersion = async (version) => {
      if (!confirm(`确定要恢复到版本 "${version.version}" 吗？当前版本将被备份。`)) return
      
      try {
        await productApi.restoreVersion(props.productId, version.version)
        showSuccess('版本恢复成功')
        refreshFiles()
      } catch (error) {
        showError('版本恢复失败: ' + error.message)
      }
    }
    
    const deleteVersion = async (version) => {
      if (!confirm(`确定要删除版本 "${version.version}" 吗？此操作不可撤销。`)) return
      
      try {
        await productApi.deleteVersion(props.productId, version.version)
        showSuccess('版本删除成功')
        loadVersions()
      } catch (error) {
        showError('版本删除失败: ' + error.message)
      }
    }
    
    // 工具函数
    const formatFileSize = (bytes) => {
      if (bytes === 0) return '0 B'
      const k = 1024
      const sizes = ['B', 'KB', 'MB', 'GB']
      const i = Math.floor(Math.log(bytes) / Math.log(k))
      return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
    }
    
    const formatDate = (date) => {
      if (!date) return '-'
      return new Date(date).toLocaleString('zh-CN')
    }
    
    const getFileIcon = (type) => {
      const iconMap = {
        'html': 'fab fa-html5',
        'css': 'fab fa-css3-alt',
        'javascript': 'fab fa-js-square',
        'image': 'fas fa-image',
        'font': 'fas fa-font',
        'audio': 'fas fa-music',
        'video': 'fas fa-video',
        'data': 'fas fa-database',
        'unknown': 'fas fa-file'
      }
      return iconMap[type] || 'fas fa-file'
    }
    
    // 生命周期
    onMounted(() => {
      refreshFiles()
      loadVersions()
    })
    
    return {
      files,
      versions,
      scanResult,
      fileStats,
      showUploadDialog,
      showVersionDialog,
      selectedFile,
      uploadDescription,
      fileInput,
      newVersion,
      refreshFiles,
      handleFileSelect,
      uploadFile,
      downloadFile,
      deleteFile,
      scanSecurity,
      loadVersions,
      createVersion,
      submitCreateVersion,
      restoreVersion,
      deleteVersion,
      formatFileSize,
      formatDate,
      getFileIcon
    }
  }
}
</script>

<style scoped>
.product-file-manager {
  padding: 20px;
}

.file-manager-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.header-actions {
  display: flex;
  gap: 10px;
}

.file-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
}

.stat-item {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.stat-item .label {
  font-size: 0.9em;
  color: #666;
}

.stat-item .value {
  font-weight: bold;
  color: #333;
}

.file-table table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 30px;
}

.file-table th,
.file-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ddd;
}

.file-table th {
  background: #f8f9fa;
  font-weight: bold;
}

.version-manager {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.version-actions {
  display: flex;
  gap: 10px;
  margin: 15px 0;
}

.version-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 15px;
  border: 1px solid #ddd;
  border-radius: 8px;
  margin-bottom: 10px;
}

.version-info {
  display: flex;
  flex-direction: column;
  gap: 5px;
}

.version-number {
  font-weight: bold;
  color: #007bff;
}

.version-date {
  font-size: 0.9em;
  color: #666;
}

.security-scan {
  margin-top: 30px;
  padding-top: 20px;
  border-top: 1px solid #ddd;
}

.scan-summary {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 15px;
  border-radius: 8px;
  margin-bottom: 15px;
}

.scan-summary.safe {
  background: #d4edda;
  color: #155724;
}

.scan-summary.unsafe {
  background: #f8d7da;
  color: #721c24;
}

.scan-stats {
  display: flex;
  gap: 20px;
  margin-bottom: 15px;
}

.threat-item {
  margin-bottom: 15px;
  padding: 10px;
  background: #f8d7da;
  border-radius: 5px;
}

.threat {
  color: #721c24;
  margin: 5px 0;
}

.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  padding: 30px;
  border-radius: 8px;
  width: 90%;
  max-width: 500px;
}

.form-group {
  margin-bottom: 20px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group input,
.form-group textarea {
  width: 100%;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.form-actions {
  display: flex;
  gap: 10px;
  justify-content: flex-end;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  text-decoration: none;
  display: inline-flex;
  align-items: center;
  gap: 5px;
}

.btn-primary {
  background: #007bff;
  color: white;
}

.btn-secondary {
  background: #6c757d;
  color: white;
}

.btn-warning {
  background: #ffc107;
  color: #212529;
}

.btn-danger {
  background: #dc3545;
  color: white;
}

.btn-sm {
  padding: 4px 8px;
  font-size: 0.9em;
}

.btn:hover {
  opacity: 0.9;
}

.btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}
</style>