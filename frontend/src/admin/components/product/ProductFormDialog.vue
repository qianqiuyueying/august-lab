<template>
  <el-dialog
    v-model="visible"
    :title="isEdit ? '编辑产品' : '新建产品'"
    width="800px"
    :close-on-click-modal="false"
    @close="handleClose"
  >
    <el-form
      ref="formRef"
      :model="form"
      :rules="rules"
      label-width="100px"
      @submit.prevent
    >
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="产品名称" prop="title">
            <el-input
              v-model="form.title"
              placeholder="请输入产品名称"
              maxlength="100"
              show-word-limit
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="产品类型" prop="product_type">
            <el-select v-model="form.product_type" placeholder="选择产品类型" style="width: 100%">
              <el-option label="静态网站" value="static" />
              <el-option label="单页应用" value="spa" />
              <el-option label="游戏" value="game" />
              <el-option label="工具" value="tool" />
            </el-select>
          </el-form-item>
        </el-col>
      </el-row>
      
      <!-- 产品类型说明提示 -->
      <el-form-item>
        <el-collapse v-model="activeTypeHelp" accordion>
          <el-collapse-item name="type-help">
            <template #title>
              <el-icon style="margin-right: 8px;"><InfoFilled /></el-icon>
              <span style="font-weight: 500;">产品类型说明（点击查看区别）</span>
            </template>
            <div class="product-type-help">
              <el-descriptions :column="1" border size="small">
                <el-descriptions-item label="静态网站 (static)">
                  <div class="type-description">
                    <p><strong>适用场景：</strong>传统 HTML/CSS/JS 网站、展示型网站、文档站点</p>
                    <p><strong>特点：</strong>必须包含 HTML 文件，基础权限，内存 512MB，存储 100MB</p>
                    <p><strong>入口文件：</strong>index.html、main.html、app.html</p>
                  </div>
                </el-descriptions-item>
                <el-descriptions-item label="单页应用 (spa)">
                  <div class="type-description">
                    <p><strong>适用场景：</strong>React、Vue、Angular 等 SPA 框架应用</p>
                    <p><strong>特点：</strong>必须包含 index.html，支持路由模式，启用缓存优化，支持父窗口通信</p>
                    <p><strong>资源限制：</strong>内存 512MB，存储 100MB</p>
                  </div>
                </el-descriptions-item>
                <el-descriptions-item label="游戏 (game)">
                  <div class="type-description">
                    <p><strong>适用场景：</strong>HTML5 游戏、交互式游戏应用</p>
                    <p><strong>特点：</strong>支持全屏、指针锁定、WebGL、Canvas、Audio、Gamepad</p>
                    <p><strong>资源限制：</strong>内存 1GB，存储 200MB（更高限制）</p>
                  </div>
                </el-descriptions-item>
                <el-descriptions-item label="工具 (tool)">
                  <div class="type-description">
                    <p><strong>适用场景：</strong>计算工具、转换工具、实用小程序</p>
                    <p><strong>特点：</strong>高安全级别，支持剪贴板、通知、网络请求</p>
                    <p><strong>资源限制：</strong>内存 256MB，存储 50MB（更严格限制）</p>
                  </div>
                </el-descriptions-item>
              </el-descriptions>
            </div>
          </el-collapse-item>
        </el-collapse>
      </el-form-item>
      
      <el-form-item label="产品描述" prop="description">
        <el-input
          v-model="form.description"
          type="textarea"
          :rows="3"
          placeholder="请输入产品描述"
          maxlength="500"
          show-word-limit
        />
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="12">
          <el-form-item label="版本号" prop="version">
            <el-input
              v-model="form.version"
              placeholder="如: 1.0.0"
              maxlength="20"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="12">
          <el-form-item label="入口文件" prop="entry_file">
            <el-input
              v-model="form.entry_file"
              placeholder="如: index.html"
              maxlength="100"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="技术栈">
        <div class="tech-stack-input">
          <el-tag
            v-for="tech in form.tech_stack"
            :key="tech"
            closable
            @close="removeTech(tech)"
            class="tech-tag"
          >
            {{ tech }}
          </el-tag>
          <el-input
            v-if="showTechInput"
            ref="techInputRef"
            v-model="newTech"
            size="small"
            @keyup.enter="addTech"
            @blur="addTech"
            style="width: 120px"
            placeholder="添加技术"
          />
          <el-button
            v-else
            size="small"
            @click="showTechInput = true"
          >
            + 添加技术
          </el-button>
        </div>
      </el-form-item>
      
      <el-form-item label="预览图片">
        <div class="image-upload">
          <el-upload
            :show-file-list="false"
            :before-upload="beforeImageUpload"
            :http-request="handleImageUpload"
            accept="image/*"
            drag
          >
            <div v-if="form.preview_image" class="image-preview">
              <img :src="form.preview_image" alt="预览图" />
              <div class="image-overlay">
                <el-button type="primary" size="small">更换图片</el-button>
              </div>
            </div>
            <div v-else class="upload-placeholder">
              <el-icon class="upload-icon"><Plus /></el-icon>
              <div class="upload-text">点击或拖拽上传预览图</div>
              <div class="upload-hint">支持 JPG、PNG 格式，建议尺寸 800x600</div>
            </div>
          </el-upload>
          <el-button
            v-if="form.preview_image"
            type="danger"
            size="small"
            @click="removeImage"
            style="margin-top: 8px"
          >
            删除图片
          </el-button>
        </div>
      </el-form-item>
      
      <el-row :gutter="20">
        <el-col :span="8">
          <el-form-item label="发布状态">
            <el-switch
              v-model="form.is_published"
              active-text="已发布"
              inactive-text="草稿"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="8">
          <el-form-item label="推荐产品">
            <el-switch
              v-model="form.is_featured"
              active-text="推荐"
              inactive-text="普通"
            />
          </el-form-item>
        </el-col>
        
        <el-col :span="8">
          <el-form-item label="显示顺序" prop="display_order">
            <el-input-number
              v-model="form.display_order"
              :min="0"
              :max="9999"
              style="width: 100%"
            />
          </el-form-item>
        </el-col>
      </el-row>
      
      <el-form-item label="项目链接">
        <el-input
          v-model="form.project_url"
          placeholder="产品的在线访问地址（可选）"
          maxlength="500"
        />
      </el-form-item>
      
      <el-form-item label="源码链接">
        <el-input
          v-model="form.github_url"
          placeholder="GitHub 或其他代码仓库地址（可选）"
          maxlength="500"
        />
      </el-form-item>
    </el-form>
    
    <template #footer>
      <div class="dialog-footer">
        <el-button @click="handleClose">取消</el-button>
        <el-button type="primary" :loading="saving" @click="handleSave">
          {{ isEdit ? '保存' : '创建' }}
        </el-button>
      </div>
    </template>
  </el-dialog>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, InfoFilled } from '@element-plus/icons-vue'
import { useProductStore } from '../../../frontend/composables/useProductStore'
import { uploadAPI } from '../../../shared/api'
import type { Product } from '../../../shared/types'
import type { FormInstance, FormRules, UploadRequestOptions } from 'element-plus'

interface Props {
  modelValue: boolean
  product?: Product | null
}

interface Emits {
  (e: 'update:modelValue', value: boolean): void
  (e: 'success'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// 响应式数据
const formRef = ref<FormInstance>()
const techInputRef = ref()
const visible = ref(false)
const saving = ref(false)
const showTechInput = ref(false)
const newTech = ref('')
const activeTypeHelp = ref<string[]>([])

// 表单数据
const form = ref<{
  title: string
  description: string
  product_type: 'static' | 'spa' | 'game' | 'tool'
  version: string
  entry_file: string
  tech_stack: string[]
  preview_image: string
  project_url: string
  github_url: string
  is_published: boolean
  is_featured: boolean
  display_order: number
}>({
  title: '',
  description: '',
  product_type: 'static',
  version: '1.0.0',
  entry_file: 'index.html',
  tech_stack: [],
  preview_image: '',
  project_url: '',
  github_url: '',
  is_published: false,
  is_featured: false,
  display_order: 0
})

// 表单验证规则
const rules: FormRules = {
  title: [
    { required: true, message: '请输入产品名称', trigger: 'blur' },
    { min: 2, max: 100, message: '产品名称长度在 2 到 100 个字符', trigger: 'blur' }
  ],
  product_type: [
    { required: true, message: '请选择产品类型', trigger: 'change' }
  ],
  version: [
    { required: true, message: '请输入版本号', trigger: 'blur' },
    { pattern: /^\d+\.\d+\.\d+$/, message: '版本号格式应为 x.y.z', trigger: 'blur' }
  ],
  entry_file: [
    { required: true, message: '请输入入口文件', trigger: 'blur' },
    { pattern: /^[a-zA-Z0-9._-]+\.(html|htm)$/, message: '入口文件必须是有效的HTML文件名', trigger: 'blur' }
  ],
  display_order: [
    { type: 'number', min: 0, max: 9999, message: '显示顺序必须在 0-9999 之间', trigger: 'blur' }
  ]
}

// 使用组合式函数
const { createProduct, updateProduct } = useProductStore()

// 计算属性
const isEdit = computed(() => !!props.product?.id)

// 监听器
watch(() => props.modelValue, (val) => {
  visible.value = val
  if (val) {
    resetForm()
    if (props.product) {
      loadProduct(props.product)
    }
  }
})

watch(visible, (val) => {
  emit('update:modelValue', val)
})

watch(showTechInput, (val) => {
  if (val) {
    nextTick(() => {
      techInputRef.value?.focus()
    })
  }
})

// 方法
const resetForm = () => {
  form.value = {
    title: '',
    description: '',
    product_type: 'static',
    version: '1.0.0',
    entry_file: 'index.html',
    tech_stack: [],
    preview_image: '',
    project_url: '',
    github_url: '',
    is_published: false,
    is_featured: false,
    display_order: 0
  }
  formRef.value?.clearValidate()
}

const loadProduct = (product: Product) => {
  form.value = {
    title: product.title,
    description: product.description || '',
    product_type: product.product_type,
    version: product.version,
    entry_file: product.entry_file,
    tech_stack: [...(product.tech_stack || [])],
    preview_image: product.preview_image || '',
    project_url: product.project_url || '',
    github_url: product.github_url || '',
    is_published: product.is_published,
    is_featured: product.is_featured,
    display_order: product.display_order
  }
}

const addTech = () => {
  const tech = newTech.value.trim()
  if (tech && !form.value.tech_stack.includes(tech)) {
    form.value.tech_stack.push(tech)
  }
  newTech.value = ''
  showTechInput.value = false
}

const removeTech = (tech: string) => {
  const index = form.value.tech_stack.indexOf(tech)
  if (index > -1) {
    form.value.tech_stack.splice(index, 1)
  }
}

const beforeImageUpload = (file: File) => {
  const isImage = file.type.startsWith('image/')
  const isLt5M = file.size / 1024 / 1024 < 5

  if (!isImage) {
    ElMessage.error('只能上传图片文件!')
    return false
  }
  if (!isLt5M) {
    ElMessage.error('图片大小不能超过 5MB!')
    return false
  }
  return true
}

const handleImageUpload = async (options: UploadRequestOptions) => {
  try {
    const response = await uploadAPI.uploadImage(options.file as File)
    form.value.preview_image = response.data.url
    ElMessage.success('图片上传成功')
  } catch (error: any) {
    ElMessage.error(error.message || '图片上传失败')
  }
}

const removeImage = () => {
  form.value.preview_image = ''
}

const handleSave = async () => {
  if (!formRef.value) return

  try {
    await formRef.value.validate()
    saving.value = true

    const productData = {
      ...form.value,
      tech_stack: form.value.tech_stack.length > 0 ? form.value.tech_stack : []
    }

    if (isEdit.value && props.product) {
      await updateProduct(props.product.id, productData)
      ElMessage.success('产品更新成功')
    } else {
      await createProduct(productData)
      ElMessage.success('产品创建成功')
    }

    emit('success')
  } catch (error: any) {
    // 特别处理权限错误
    if (error.response && error.response.status === 401) {
      ElMessage.error('权限不足，请重新登录后再试')
      // 跳转到登录页面
      window.location.href = '/admin/login'
    } else if (error.message) {
      ElMessage.error(error.message)
    } else {
      ElMessage.error('操作失败，请重试')
    }
  } finally {
    saving.value = false
  }
}

const handleClose = () => {
  visible.value = false
}
</script>

<style scoped>
.tech-stack-input {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  align-items: center;
}

.tech-tag {
  margin: 0;
}

.image-upload {
  width: 100%;
}

.image-preview {
  position: relative;
  width: 200px;
  height: 150px;
  border-radius: 6px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}

.upload-placeholder {
  width: 200px;
  height: 150px;
  border: 2px dashed #dcdfe6;
  border-radius: 6px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: #8c939d;
  transition: border-color 0.3s;
}

.upload-placeholder:hover {
  border-color: #409eff;
  color: #409eff;
}

.upload-icon {
  font-size: 28px;
  margin-bottom: 8px;
}

.upload-text {
  font-size: 14px;
  margin-bottom: 4px;
}

.upload-hint {
  font-size: 12px;
  color: #a8abb2;
}

.product-type-help {
  padding: 12px 0;
}

.type-description {
  font-size: 13px;
  line-height: 1.8;
}

.type-description p {
  margin: 4px 0;
}

.type-description strong {
  color: #409eff;
  font-weight: 600;
}

.dialog-footer {
  text-align: right;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .el-dialog {
    width: 95% !important;
    margin: 5vh auto;
  }
  
  .image-preview,
  .upload-placeholder {
    width: 150px;
    height: 112px;
  }
}
</style>