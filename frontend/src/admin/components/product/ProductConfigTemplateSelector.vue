<template>
  <div class="template-selector">
    <div class="selector-header">
      <h4>选择配置模板</h4>
      <div class="search-filters">
        <el-input
          v-model="searchQuery"
          placeholder="搜索模板..."
          prefix-icon="Search"
          clearable
          class="search-input"
        />
        
        <el-select
          v-model="selectedType"
          placeholder="产品类型"
          clearable
          class="type-filter"
        >
          <el-option label="全部类型" value="" />
          <el-option label="静态网页" value="static" />
          <el-option label="单页应用" value="spa" />
          <el-option label="游戏应用" value="game" />
          <el-option label="工具应用" value="tool" />
        </el-select>
        
        <el-select
          v-model="selectedCategory"
          placeholder="分类"
          clearable
          class="category-filter"
        >
          <el-option label="全部分类" value="" />
          <el-option
            v-for="category in categories"
            :key="category"
            :label="category"
            :value="category"
          />
        </el-select>
      </div>
    </div>
    
    <div class="template-grid">
      <div
        v-for="template in filteredTemplates"
        :key="template.id"
        class="template-card"
        :class="{ 'selected': selectedTemplate?.id === template.id }"
        @click="selectTemplate(template)"
      >
        <div class="template-header">
          <h5 class="template-name">{{ template.name }}</h5>
          <div class="template-badges">
            <el-tag :type="getTypeColor(template.type)" size="small">
              {{ getTypeLabel(template.type) }}
            </el-tag>
            <el-tag
              v-if="isCustomTemplate(template.id)"
              type="warning"
              size="small"
            >
              自定义
            </el-tag>
          </div>
        </div>
        
        <p class="template-description">{{ template.description }}</p>
        
        <div class="template-tags">
          <el-tag
            v-for="tag in template.tags.slice(0, 3)"
            :key="tag"
            size="small"
            effect="plain"
          >
            {{ tag }}
          </el-tag>
          <span v-if="template.tags.length > 3" class="more-tags">
            +{{ template.tags.length - 3 }}
          </span>
        </div>
        
        <div class="template-actions">
          <el-button
            @click.stop="previewTemplate(template)"
            size="small"
            text
            icon="View"
          >
            预览
          </el-button>
          
          <el-button
            v-if="isCustomTemplate(template.id)"
            @click.stop="editTemplate(template)"
            size="small"
            text
            icon="Edit"
          >
            编辑
          </el-button>
          
          <el-button
            @click.stop="exportTemplate(template)"
            size="small"
            text
            icon="Download"
          >
            导出
          </el-button>
          
          <el-button
            v-if="isCustomTemplate(template.id)"
            @click.stop="deleteTemplate(template)"
            size="small"
            text
            type="danger"
            icon="Delete"
          >
            删除
          </el-button>
        </div>
      </div>
      
      <!-- 创建新模板卡片 -->
      <div class="template-card create-card" @click="showCreateDialog = true">
        <div class="create-content">
          <el-icon class="create-icon" size="48">
            <Plus />
          </el-icon>
          <h5>创建新模板</h5>
          <p>基于当前配置创建自定义模板</p>
        </div>
      </div>
    </div>
    
    <div class="selector-footer">
      <div class="selected-info">
        <span v-if="selectedTemplate">
          已选择: {{ selectedTemplate.name }}
        </span>
        <span v-else class="no-selection">
          请选择一个模板
        </span>
      </div>
      
      <div class="footer-actions">
        <el-button @click="importTemplate">导入模板</el-button>
        <el-button @click="$emit('cancel')">取消</el-button>
        <el-button
          @click="applySelectedTemplate"
          type="primary"
          :disabled="!selectedTemplate"
        >
          应用模板
        </el-button>
      </div>
    </div>
    
    <!-- 预览对话框 -->
    <el-dialog
      v-model="showPreviewDialog"
      title="模板预览"
      width="800px"
      class="preview-dialog"
    >
      <div v-if="previewingTemplate" class="template-preview">
        <div class="preview-header">
          <h4>{{ previewingTemplate.name }}</h4>
          <div class="preview-meta">
            <el-tag :type="getTypeColor(previewingTemplate.type)">
              {{ getTypeLabel(previewingTemplate.type) }}
            </el-tag>
            <span class="preview-category">{{ previewingTemplate.category }}</span>
            <span v-if="previewingTemplate.author" class="preview-author">
              作者: {{ previewingTemplate.author }}
            </span>
          </div>
        </div>
        
        <p class="preview-description">{{ previewingTemplate.description }}</p>
        
        <div class="preview-tags">
          <el-tag
            v-for="tag in previewingTemplate.tags"
            :key="tag"
            size="small"
            effect="plain"
          >
            {{ tag }}
          </el-tag>
        </div>
        
        <el-divider>配置详情</el-divider>
        
        <el-input
          v-model="previewJson"
          type="textarea"
          :rows="15"
          readonly
          class="preview-json"
        />
      </div>
      
      <template #footer>
        <el-button @click="showPreviewDialog = false">关闭</el-button>
        <el-button
          @click="selectAndApplyTemplate(previewingTemplate)"
          type="primary"
        >
          使用此模板
        </el-button>
      </template>
    </el-dialog>
    
    <!-- 创建模板对话框 -->
    <el-dialog
      v-model="showCreateDialog"
      title="创建新模板"
      width="600px"
    >
      <el-form
        ref="createFormRef"
        :model="createForm"
        :rules="createRules"
        label-width="100px"
      >
        <el-form-item label="模板名称" prop="name">
          <el-input v-model="createForm.name" placeholder="输入模板名称" />
        </el-form-item>
        
        <el-form-item label="描述" prop="description">
          <el-input
            v-model="createForm.description"
            type="textarea"
            :rows="3"
            placeholder="描述模板的用途和特点"
          />
        </el-form-item>
        
        <el-form-item label="分类" prop="category">
          <el-select
            v-model="createForm.category"
            filterable
            allow-create
            placeholder="选择或输入分类"
            class="full-width"
          >
            <el-option
              v-for="category in categories"
              :key="category"
              :label="category"
              :value="category"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="标签">
          <el-select
            v-model="createForm.tags"
            multiple
            filterable
            allow-create
            placeholder="添加标签"
            class="full-width"
          >
            <el-option
              v-for="tag in allTags"
              :key="tag"
              :label="tag"
              :value="tag"
            />
          </el-select>
        </el-form-item>
        
        <el-form-item label="作者">
          <el-input v-model="createForm.author" placeholder="作者名称（可选）" />
        </el-form-item>
      </el-form>
      
      <template #footer>
        <el-button @click="showCreateDialog = false">取消</el-button>
        <el-button @click="createNewTemplate" type="primary">创建</el-button>
      </template>
    </el-dialog>
    
    <!-- 导入模板对话框 -->
    <el-dialog
      v-model="showImportDialog"
      title="导入模板"
      width="600px"
    >
      <div class="import-methods">
        <el-tabs v-model="importMethod">
          <el-tab-pane label="JSON文本" name="json">
            <el-input
              v-model="importJson"
              type="textarea"
              :rows="12"
              placeholder="粘贴模板JSON内容..."
            />
          </el-tab-pane>
          
          <el-tab-pane label="文件上传" name="file">
            <el-upload
              ref="uploadRef"
              :auto-upload="false"
              :show-file-list="false"
              accept=".json"
              :on-change="handleFileChange"
              drag
            >
              <el-icon class="upload-icon" size="48">
                <UploadFilled />
              </el-icon>
              <div class="upload-text">
                <p>点击或拖拽JSON文件到此处</p>
                <p class="upload-hint">支持 .json 格式</p>
              </div>
            </el-upload>
          </el-tab-pane>
        </el-tabs>
      </div>
      
      <template #footer>
        <el-button @click="showImportDialog = false">取消</el-button>
        <el-button @click="doImportTemplate" type="primary">导入</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, UploadFilled } from '@element-plus/icons-vue'
import { templateManager, type ConfigTemplate } from '../../frontend/utils/configTemplates'
import type { ProductConfigSchema } from '../../frontend/composables/useProductConfig'

interface Props {
  currentConfig?: ProductConfigSchema
  productType?: string
}

interface Emits {
  (e: 'select', template: ConfigTemplate): void
  (e: 'apply', config: ProductConfigSchema): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const searchQuery = ref('')
const selectedType = ref(props.productType || '')
const selectedCategory = ref('')
const selectedTemplate = ref<ConfigTemplate | null>(null)
const showPreviewDialog = ref(false)
const showCreateDialog = ref(false)
const showImportDialog = ref(false)
const previewingTemplate = ref<ConfigTemplate | null>(null)
const importMethod = ref('json')
const importJson = ref('')

// 表单数据
const createFormRef = ref()
const createForm = reactive({
  name: '',
  description: '',
  category: '',
  tags: [] as string[],
  author: ''
})

const createRules = {
  name: [
    { required: true, message: '请输入模板名称', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入模板描述', trigger: 'blur' }
  ]
}

// 计算属性
const allTemplates = computed(() => templateManager.getAllTemplates())

const filteredTemplates = computed(() => {
  let templates = allTemplates.value
  
  // 按搜索查询过滤
  if (searchQuery.value) {
    templates = templateManager.searchTemplates(searchQuery.value)
  }
  
  // 按类型过滤
  if (selectedType.value) {
    templates = templates.filter(t => t.type === selectedType.value)
  }
  
  // 按分类过滤
  if (selectedCategory.value) {
    templates = templates.filter(t => t.category === selectedCategory.value)
  }
  
  return templates
})

const categories = computed(() => templateManager.getAllCategories())
const allTags = computed(() => templateManager.getAllTags())

const previewJson = computed(() => {
  if (!previewingTemplate.value) return ''
  return templateManager.getTemplatePreview(previewingTemplate.value.id)
})

// 方法
const selectTemplate = (template: ConfigTemplate) => {
  selectedTemplate.value = template
  emit('select', template)
}

const selectAndApplyTemplate = (template: ConfigTemplate | null) => {
  if (!template) return
  
  selectedTemplate.value = template
  showPreviewDialog.value = false
  applySelectedTemplate()
}

const applySelectedTemplate = () => {
  if (!selectedTemplate.value) return
  
  const config = templateManager.applyTemplate(
    selectedTemplate.value.id,
    props.currentConfig
  )
  
  if (config) {
    emit('apply', config)
  } else {
    ElMessage.error('应用模板失败')
  }
}

const previewTemplate = (template: ConfigTemplate) => {
  previewingTemplate.value = template
  showPreviewDialog.value = true
}

const editTemplate = (template: ConfigTemplate) => {
  // 这里可以触发编辑事件或打开编辑对话框
  ElMessage.info('编辑功能待实现')
}

const exportTemplate = (template: ConfigTemplate) => {
  const json = templateManager.exportTemplate(template.id)
  if (json) {
    const blob = new Blob([json], { type: 'application/json' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `${template.name.replace(/\s+/g, '-')}.json`
    a.click()
    URL.revokeObjectURL(url)
    
    ElMessage.success('模板已导出')
  }
}

const deleteTemplate = async (template: ConfigTemplate) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除模板 "${template.name}" 吗？此操作不可撤销。`,
      '确认删除',
      { type: 'warning' }
    )
    
    const success = templateManager.deleteCustomTemplate(template.id)
    if (success) {
      ElMessage.success('模板已删除')
      
      // 如果删除的是当前选中的模板，清除选择
      if (selectedTemplate.value?.id === template.id) {
        selectedTemplate.value = null
      }
    } else {
      ElMessage.error('删除失败')
    }
  } catch {
    // 用户取消
  }
}

const createNewTemplate = async () => {
  try {
    await createFormRef.value?.validate()
    
    if (!props.currentConfig) {
      ElMessage.error('没有可用的配置数据')
      return
    }
    
    const templateId = templateManager.createTemplateFromConfig(
      props.currentConfig,
      {
        name: createForm.name,
        description: createForm.description,
        category: createForm.category || '自定义',
        tags: createForm.tags,
        author: createForm.author
      }
    )
    
    showCreateDialog.value = false
    
    // 重置表单
    Object.assign(createForm, {
      name: '',
      description: '',
      category: '',
      tags: [],
      author: ''
    })
    
    ElMessage.success('模板创建成功')
    
    // 选择新创建的模板
    const newTemplate = templateManager.getTemplate(templateId)
    if (newTemplate) {
      selectTemplate(newTemplate)
    }
  } catch {
    ElMessage.error('表单验证失败')
  }
}

const importTemplate = () => {
  showImportDialog.value = true
  importJson.value = ''
}

const handleFileChange = (file: any) => {
  const reader = new FileReader()
  reader.onload = (e) => {
    importJson.value = e.target?.result as string
  }
  reader.readAsText(file.raw)
}

const doImportTemplate = () => {
  if (!importJson.value.trim()) {
    ElMessage.error('请输入或选择模板内容')
    return
  }
  
  const result = templateManager.importTemplate(importJson.value)
  
  if (result.success && result.templateId) {
    showImportDialog.value = false
    importJson.value = ''
    
    ElMessage.success('模板导入成功')
    
    // 选择导入的模板
    const importedTemplate = templateManager.getTemplate(result.templateId)
    if (importedTemplate) {
      selectTemplate(importedTemplate)
    }
  } else {
    ElMessage.error(`导入失败: ${result.error}`)
  }
}

const isCustomTemplate = (templateId: string): boolean => {
  return templateManager.isCustomTemplate(templateId)
}

const getTypeLabel = (type: string): string => {
  const labels: Record<string, string> = {
    static: '静态网页',
    spa: '单页应用',
    game: '游戏应用',
    tool: '工具应用'
  }
  return labels[type] || type
}

const getTypeColor = (type: string): string => {
  const colors: Record<string, string> = {
    static: 'info',
    spa: 'success',
    game: 'warning',
    tool: 'primary'
  }
  return colors[type] || 'info'
}
</script>

<style scoped>
.template-selector {
  display: flex;
  flex-direction: column;
  height: 600px;
}

.selector-header {
  padding: 1rem;
  border-bottom: 1px solid #e5e7eb;
}

.selector-header h4 {
  margin: 0 0 1rem 0;
  font-size: 1.125rem;
  font-weight: 600;
}

.search-filters {
  display: flex;
  gap: 1rem;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.type-filter,
.category-filter {
  width: 120px;
}

.template-grid {
  flex: 1;
  padding: 1rem;
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 1rem;
  overflow-y: auto;
}

.template-card {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 1rem;
  cursor: pointer;
  transition: all 0.2s;
  background: white;
}

.template-card:hover {
  border-color: #3b82f6;
  box-shadow: 0 2px 8px rgba(59, 130, 246, 0.1);
}

.template-card.selected {
  border-color: #3b82f6;
  background: #eff6ff;
}

.template-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 0.5rem;
}

.template-name {
  margin: 0;
  font-size: 1rem;
  font-weight: 600;
  color: #374151;
}

.template-badges {
  display: flex;
  gap: 0.25rem;
  flex-shrink: 0;
}

.template-description {
  color: #6b7280;
  font-size: 0.875rem;
  line-height: 1.4;
  margin: 0 0 1rem 0;
}

.template-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.more-tags {
  color: #6b7280;
  font-size: 0.75rem;
}

.template-actions {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.create-card {
  border: 2px dashed #d1d5db;
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: 200px;
}

.create-card:hover {
  border-color: #3b82f6;
  background: #f9fafb;
}

.create-content {
  text-align: center;
}

.create-icon {
  color: #9ca3af;
  margin-bottom: 1rem;
}

.create-content h5 {
  margin: 0 0 0.5rem 0;
  color: #374151;
}

.create-content p {
  margin: 0;
  color: #6b7280;
  font-size: 0.875rem;
}

.selector-footer {
  padding: 1rem;
  border-top: 1px solid #e5e7eb;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.selected-info {
  font-weight: 500;
  color: #374151;
}

.no-selection {
  color: #9ca3af;
}

.footer-actions {
  display: flex;
  gap: 0.5rem;
}

.preview-dialog .template-preview {
  max-height: 500px;
  overflow-y: auto;
}

.preview-header {
  margin-bottom: 1rem;
}

.preview-header h4 {
  margin: 0 0 0.5rem 0;
}

.preview-meta {
  display: flex;
  gap: 1rem;
  align-items: center;
  font-size: 0.875rem;
  color: #6b7280;
}

.preview-description {
  color: #374151;
  line-height: 1.5;
  margin-bottom: 1rem;
}

.preview-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.25rem;
  margin-bottom: 1rem;
}

.preview-json {
  font-family: 'Courier New', monospace;
  font-size: 12px;
}

.import-methods {
  margin-bottom: 1rem;
}

.upload-icon {
  color: #9ca3af;
  margin-bottom: 1rem;
}

.upload-text {
  text-align: center;
}

.upload-text p {
  margin: 0.25rem 0;
}

.upload-hint {
  color: #9ca3af;
  font-size: 0.875rem;
}

.full-width {
  width: 100%;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .search-filters {
    flex-direction: column;
    align-items: stretch;
  }
  
  .search-input {
    max-width: none;
  }
  
  .template-grid {
    grid-template-columns: 1fr;
  }
  
  .selector-footer {
    flex-direction: column;
    gap: 1rem;
    align-items: stretch;
  }
  
  .footer-actions {
    justify-content: center;
  }
}
</style>