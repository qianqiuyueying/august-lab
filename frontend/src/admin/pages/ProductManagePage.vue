<template>
  <div class="product-management">
    <!-- 页面头部 -->
    <div class="page-header admin-page-header admin-section">
      <div class="header-content">
        <div class="header-left">
          <h1 class="page-title admin-page-title">产品管理</h1>
          <p class="page-description admin-page-desc">管理和发布Web应用产品</p>
        </div>
        <div class="header-actions">
          <el-button type="primary" @click="openCreateDialog">
            <el-icon><Plus /></el-icon>
            新建产品
          </el-button>
        </div>
      </div>
    </div>

    <!-- 筛选和搜索 -->
    <div class="filters-section admin-section">
      <el-card shadow="never">
        <div class="filters-row">
          <div class="filter-group">
            <el-input
              v-model="searchQuery"
              placeholder="搜索产品名称或描述..."
              clearable
              @input="handleSearch"
              style="width: 300px"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
          </div>
          
          <div class="filter-group">
            <el-select
              v-model="selectedType"
              placeholder="产品类型"
              clearable
              @change="handleFilter"
              style="width: 150px"
            >
              <el-option label="静态网站" value="static" />
              <el-option label="单页应用" value="spa" />
              <el-option label="游戏" value="game" />
              <el-option label="工具" value="tool" />
            </el-select>
          </div>
          
          <div class="filter-group">
            <el-select
              v-model="selectedStatus"
              placeholder="发布状态"
              clearable
              @change="handleFilter"
              style="width: 120px"
            >
              <el-option label="已发布" value="published" />
              <el-option label="草稿" value="draft" />
            </el-select>
          </div>
          
          <div class="filter-actions">
            <el-button @click="resetFilters">重置</el-button>
            <el-button type="primary" @click="loadProducts">刷新</el-button>
          </div>
        </div>
      </el-card>
    </div>

    <!-- 产品列表 -->
    <div class="products-section admin-section">
      <el-card shadow="never">
        <el-table
          v-loading="loading"
          :data="filteredProducts"
          stripe
          @selection-change="handleSelectionChange"
        >
          <el-table-column type="selection" width="55" />
          
          <el-table-column label="产品信息" min-width="300">
            <template #default="{ row }">
              <div class="product-info">
                <div class="product-preview">
                  <img
                    v-if="row.preview_image"
                    :src="row.preview_image"
                    :alt="row.title"
                    class="preview-thumb"
                  />
                  <div v-else class="preview-placeholder">
                    <el-icon size="24"><Document /></el-icon>
                  </div>
                </div>
                <div class="product-details">
                  <h3 class="product-title">{{ row.title }}</h3>
                  <p class="product-description">{{ row.description || '暂无描述' }}</p>
                  <div class="product-meta">
                    <el-tag :type="getTypeTagType(row.product_type)" size="small">
                      {{ getTypeLabel(row.product_type) }}
                    </el-tag>
                    <span class="version">v{{ row.version }}</span>
                  </div>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="技术栈" width="200">
            <template #default="{ row }">
              <div class="tech-stack">
                <el-tag
                  v-for="tech in row.tech_stack?.slice(0, 3)"
                  :key="tech"
                  size="small"
                  class="tech-tag"
                >
                  {{ tech }}
                </el-tag>
                <el-tag
                  v-if="row.tech_stack && row.tech_stack.length > 3"
                  size="small"
                  type="info"
                >
                  +{{ row.tech_stack.length - 3 }}
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="状态" width="120">
            <template #default="{ row }">
              <div class="status-column">
                <el-tag :type="row.is_published ? 'success' : 'warning'" size="small">
                  {{ row.is_published ? '已发布' : '草稿' }}
                </el-tag>
                <el-tag v-if="row.is_featured" type="danger" size="small" class="featured-tag">
                  推荐
                </el-tag>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="文件状态" width="100">
            <template #default="{ row }">
              <el-tag :type="row.file_path ? 'success' : 'info'" size="small">
                {{ row.file_path ? '有文件' : '无文件' }}
              </el-tag>
            </template>
          </el-table-column>
          
          <el-table-column label="统计" width="120">
            <template #default="{ row }">
              <div class="stats-column">
                <div class="stat-item">
                  <el-icon size="14"><View /></el-icon>
                  {{ row.view_count || 0 }}
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column label="创建时间" width="150">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          
          <el-table-column label="操作" width="200" fixed="right">
            <template #default="{ row }">
              <div class="action-buttons">
                <el-button
                  v-if="row.is_published && row.file_path"
                  type="primary"
                  size="small"
                  @click="previewProduct(row)"
                >
                  预览
                </el-button>
                <el-button size="small" @click="editProduct(row)">
                  编辑
                </el-button>
                <el-dropdown>
                  <el-button size="small">
                    更多<el-icon class="el-icon--right"><ArrowDown /></el-icon>
                  </el-button>
                  <template #dropdown>
                    <el-dropdown-menu>
                      <el-dropdown-item @click="() => handleAction('toggle-publish', row)">
                        {{ row.is_published ? '取消发布' : '发布' }}
                      </el-dropdown-item>
                      <el-dropdown-item @click="() => handleAction('toggle-featured', row)">
                        {{ row.is_featured ? '取消推荐' : '设为推荐' }}
                      </el-dropdown-item>
                      <el-dropdown-item @click="() => handleAction('upload-files', row)" :disabled="!row.id">
                        上传文件
                      </el-dropdown-item>
                      <el-dropdown-item @click="() => handleAction('view-files', row)" :disabled="!row.file_path">
                        查看文件
                      </el-dropdown-item>
                      <el-dropdown-item @click="() => handleAction('preview-product', row)">
                        预览测试
                      </el-dropdown-item>
                      <el-dropdown-item @click="() => handleAction('manage-feedback', row)">
                        管理反馈
                      </el-dropdown-item>
                      <el-dropdown-item @click="() => handleAction('duplicate', row)">
                        复制产品
                      </el-dropdown-item>
                      <el-dropdown-item @click="() => handleAction('delete', row)" divided>
                        <span style="color: #f56c6c">删除</span>
                      </el-dropdown-item>
                    </el-dropdown-menu>
                  </template>
                </el-dropdown>
              </div>
            </template>
          </el-table-column>
        </el-table>
        
        <!-- 批量操作 -->
        <div v-if="selectedProducts.length > 0" class="batch-actions">
          <div class="batch-info">
            已选择 {{ selectedProducts.length }} 个产品
          </div>
          <div class="batch-buttons">
            <el-button @click="batchPublish">批量发布</el-button>
            <el-button @click="batchUnpublish">批量取消发布</el-button>
            <el-button type="danger" @click="batchDelete">批量删除</el-button>
          </div>
        </div>
        
        <!-- 分页 -->
        <div class="pagination-wrapper">
          <el-pagination
            v-model="currentPage"
            :page-size="pageSize"
            :page-sizes="[10, 20, 50, 100]"
            :total="totalProducts"
            layout="total, sizes, prev, pager, next, jumper"
            @size-change="handleSizeChange"
            @current-change="handleCurrentChange"
          />
        </div>
      </el-card>
    </div>

    <!-- 创建/编辑产品对话框 -->
    <ProductFormDialog
      v-model="showCreateDialog"
      :product="editingProduct"
      @success="handleProductSaved"
    />
    
    <!-- 文件上传对话框 -->
    <ProductUploadDialog
      v-model="showUploadDialog"
      :product="uploadingProduct"
      @success="handleFileUploaded"
    />
    
    <!-- 文件查看对话框 -->
    <ProductFilesDialog
      v-model="showFilesDialog"
      :product="viewingProduct"
    />
    
    <!-- 产品预览对话框 -->
    <ProductPreviewDialog
      v-model="showPreviewDialog"
      :product="previewingProduct"
      @upload-files="handleUploadFromPreview"
      @product-published="handleProductPublished"
    />
    
    <!-- 产品反馈管理对话框 -->
    <el-dialog
      v-model="showFeedbackDialog"
      :title="`${feedbackProduct?.title} - 用户反馈`"
      width="90%"
      :close-on-click-modal="false"
    >
      <ProductFeedbackManager
        v-if="feedbackProduct"
        :product-id="feedbackProduct.id"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, defineAsyncComponent } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  Plus,
  Search,
  Document,
  View,
  ArrowDown
} from '@element-plus/icons-vue'
import { useProductStore } from '../../frontend/composables/useProductStore'
import type { Product } from '../../shared/types'

// 动态导入组件 - 使用defineAsyncComponent正确方式
const ProductFormDialog = defineAsyncComponent(() => import('../components/product/ProductFormDialog.vue'))
const ProductUploadDialog = defineAsyncComponent(() => import('../components/product/ProductUploadDialog.vue'))
const ProductFilesDialog = defineAsyncComponent(() => import('../components/product/ProductFilesDialog.vue'))
const ProductPreviewDialog = defineAsyncComponent(() => import('../components/product/ProductPreviewDialog.vue'))
const ProductFeedbackManager = defineAsyncComponent(() => import('../components/feedback/ProductFeedbackManager.vue'))

// 响应式数据
const loading = ref(false)
const products = ref<Product[]>([])
const selectedProducts = ref<Product[]>([])

// 筛选和搜索
const searchQuery = ref('')
const selectedType = ref('')
const selectedStatus = ref('')

// 分页
const currentPage = ref(1)
const pageSize = ref(20)
const totalProducts = ref(0)

// 对话框状态
const showCreateDialog = ref(false)
const showUploadDialog = ref(false)
const showFilesDialog = ref(false)
const showPreviewDialog = ref(false)
const showFeedbackDialog = ref(false)

// 编辑状态
const editingProduct = ref<Product | null>(null)
const uploadingProduct = ref<Product | null>(null)
const viewingProduct = ref<Product | null>(null)
const previewingProduct = ref<Product | null>(null)
const feedbackProduct = ref<Product | null>(null)

// 使用组合式函数
const productStore = useProductStore()
const { fetchProducts, createProduct, updateProduct, deleteProduct } = productStore

// 计算属性
const filteredProducts = computed(() => {
  let filtered = products.value

  // 搜索过滤
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(product =>
      product.title.toLowerCase().includes(query) ||
      product.description?.toLowerCase().includes(query)
    )
  }

  // 类型过滤
  if (selectedType.value) {
    filtered = filtered.filter(product => product.product_type === selectedType.value)
  }

  // 状态过滤
  if (selectedStatus.value) {
    if (selectedStatus.value === 'published') {
      filtered = filtered.filter(product => product.is_published)
    } else if (selectedStatus.value === 'draft') {
      filtered = filtered.filter(product => !product.is_published)
    }
  }

  return filtered
})

// 方法
const loadProducts = async () => {
  loading.value = true
  try {
    // 管理员页面显示所有产品（包括未发布的）
    products.value = await fetchProducts({ published_only: false })
    totalProducts.value = products.value.length
  } catch (error: any) {
    ElMessage.error(error.message || '加载产品失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  currentPage.value = 1
}

const handleFilter = () => {
  currentPage.value = 1
}

const resetFilters = () => {
  searchQuery.value = ''
  selectedType.value = ''
  selectedStatus.value = ''
  currentPage.value = 1
}

const handleSelectionChange = (selection: Product[]) => {
  selectedProducts.value = selection
}

const handleSizeChange = (size: number) => {
  pageSize.value = size
  currentPage.value = 1
}

const handleCurrentChange = (page: number) => {
  currentPage.value = page
}

// 添加获取当前行的方法
const currentRow = ref<Product | null>(null)

const setCurrentRow = (row: Product) => {
  currentRow.value = row
}

const getCurrentRow = (): Product | null => {
  return currentRow.value
}

const editProduct = (product: Product) => {
  editingProduct.value = { ...product }
  showCreateDialog.value = true
}

const openCreateDialog = () => {
  editingProduct.value = null
  showCreateDialog.value = true
}

const previewProduct = (product: Product) => {
  previewingProduct.value = product
  showPreviewDialog.value = true
}

type ActionType =
  | 'toggle-publish'
  | 'toggle-featured'
  | 'upload-files'
  | 'view-files'
  | 'preview-product'
  | 'manage-feedback'
  | 'duplicate'
  | 'delete'

const handleAction = async (command: ActionType, product: Product) => {
  switch (command) {
    case 'toggle-publish':
      await togglePublish(product)
      break
    case 'toggle-featured':
      await toggleFeatured(product)
      break
    case 'upload-files':
      uploadingProduct.value = product
      showUploadDialog.value = true
      break
    case 'view-files':
      viewingProduct.value = product
      showFilesDialog.value = true
      break
    case 'preview-product':
      previewingProduct.value = product
      showPreviewDialog.value = true
      break
    case 'manage-feedback':
      manageFeedback(product)
      break
    case 'duplicate':
      await duplicateProduct(product)
      break
    case 'delete':
      await confirmDelete(product)
      break
  }
}

const togglePublish = async (product: Product) => {
  try {
    await updateProduct(product.id, {
      is_published: !product.is_published
    })
    product.is_published = !product.is_published
    ElMessage.success(product.is_published ? '产品已发布' : '产品已取消发布')
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const toggleFeatured = async (product: Product) => {
  try {
    await updateProduct(product.id, {
      is_featured: !product.is_featured
    })
    product.is_featured = !product.is_featured
    ElMessage.success(product.is_featured ? '已设为推荐' : '已取消推荐')
  } catch (error: any) {
    ElMessage.error(error.message || '操作失败')
  }
}

const manageFeedback = (product: Product) => {
  feedbackProduct.value = product
  showFeedbackDialog.value = true
}

const duplicateProduct = async (product: Product) => {
  try {
    const newProduct: any = {
      ...product,
      title: `${product.title} (副本)`,
      is_published: false,
      is_featured: false
    }
    delete newProduct.id
    delete newProduct.created_at
    delete newProduct.updated_at
    delete newProduct.file_path

    await createProduct(newProduct)
    ElMessage.success('产品复制成功')
    await loadProducts()
  } catch (error: any) {
    ElMessage.error(error.message || '复制失败')
  }
}

const confirmDelete = async (product: Product) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除产品"${product.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await deleteProduct(product.id)
    ElMessage.success('产品删除成功')
    await loadProducts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  }
}

const batchPublish = async () => {
  try {
    await Promise.all(
      selectedProducts.value.map(product =>
        updateProduct(product.id, { is_published: true })
      )
    )
    ElMessage.success(`已发布 ${selectedProducts.value.length} 个产品`)
    await loadProducts()
  } catch (error: any) {
    ElMessage.error(error.message || '批量发布失败')
  }
}

const batchUnpublish = async () => {
  try {
    await Promise.all(
      selectedProducts.value.map(product =>
        updateProduct(product.id, { is_published: false })
      )
    )
    ElMessage.success(`已取消发布 ${selectedProducts.value.length} 个产品`)
    await loadProducts()
  } catch (error: any) {
    ElMessage.error(error.message || '批量取消发布失败')
  }
}

const batchDelete = async () => {
  try {
    await ElMessageBox.confirm(
      `确定要删除选中的 ${selectedProducts.value.length} 个产品吗？此操作不可恢复。`,
      '确认批量删除',
      {
        confirmButtonText: '删除',
        cancelButtonText: '取消',
        type: 'warning',
        confirmButtonClass: 'el-button--danger'
      }
    )
    
    await Promise.all(
      selectedProducts.value.map(product => deleteProduct(product.id))
    )
    ElMessage.success(`已删除 ${selectedProducts.value.length} 个产品`)
    await loadProducts()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '批量删除失败')
    }
  }
}

const handleProductSaved = () => {
  showCreateDialog.value = false
  editingProduct.value = null
  loadProducts()
}

const handleFileUploaded = () => {
  showUploadDialog.value = false
  uploadingProduct.value = null
  loadProducts()
}

const handleUploadFromPreview = () => {
  if (previewingProduct.value) {
    uploadingProduct.value = previewingProduct.value
    showPreviewDialog.value = false
    showUploadDialog.value = true
  }
}

const handleProductPublished = () => {
  ElMessage.success('产品发布成功')
  loadProducts()
}

// 工具方法
const getTypeLabel = (type: string) => {
  const labels = {
    static: '静态网站',
    spa: '单页应用',
    game: '游戏',
    tool: '工具'
  }
  return labels[type as keyof typeof labels] || type
}

const getTypeTagType = (type: string) => {
  const types = {
    static: 'primary',
    spa: 'success',
    game: 'danger',
    tool: 'warning'
  }
  return types[type as keyof typeof types] || 'info'
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// 生命周期
onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.product-management {
  padding: 24px;
}

.page-header {
  margin-bottom: 24px;
}

.header-content {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
}

.page-title {
  font-size: 24px;
  font-weight: 600;
  margin: 0 0 8px 0;
}

:deep(.dark) .page-title {
  color: #f3f4f6;
}

:deep(.dark) .page-title {
  color: #f3f4f6;
}

.page-description {
  margin: 0;
}

:deep(.dark) .page-description {
  color: #9ca3af;
}

.filters-section {
  margin-bottom: 24px;
}

.filters-row {
  display: flex;
  align-items: center;
  gap: 16px;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.filter-actions {
  margin-left: auto;
  display: flex;
  gap: 8px;
}

.products-section {
  margin-bottom: 24px;
}

.product-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.product-preview {
  flex-shrink: 0;
}

.preview-thumb {
  width: 60px;
  height: 40px;
  object-fit: cover;
  border-radius: 4px;
  border: 1px solid #e5e7eb;
}

.preview-placeholder {
  width: 60px;
  height: 40px;
  background: #f3f4f6;
  border: 1px solid #e5e7eb;
  border-radius: 4px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
}

.product-details {
  flex: 1;
  min-width: 0;
}

.product-title {
  font-size: 16px;
  font-weight: 600;
  margin: 0 0 4px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.dark) .product-title {
  color: #f3f4f6;
}

.product-description {
  font-size: 14px;
  margin: 0 0 8px 0;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

:deep(.dark) .product-description {
  color: #9ca3af;
}

.product-meta {
  display: flex;
  align-items: center;
  gap: 8px;
}

.version {
  font-size: 12px;
  color: #9ca3af;
}

.tech-stack {
  display: flex;
  flex-wrap: wrap;
  gap: 4px;
}

.tech-tag {
  margin: 0;
}

.status-column {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.featured-tag {
  margin-top: 4px;
}

.stats-column {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
}

:deep(.dark) .stat-item {
  color: #9ca3af;
}

.action-buttons {
  display: flex;
  gap: 8px;
  align-items: center;
}

.batch-actions {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  margin-top: 16px;
}

:deep(.dark) .batch-actions {
  background: #111827;
  border-top: 1px solid #374151;
}

:deep(.dark) .batch-actions {
  background: #111827;
  border-top: 1px solid #374151;
}

.batch-info {
  font-size: 14px;
}

:deep(.dark) .batch-info {
  color: #d1d5db;
}

.batch-buttons {
  display: flex;
  gap: 8px;
}

.pagination-wrapper {
  display: flex;
  justify-content: center;
  margin-top: 24px;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .product-management {
    padding: 16px;
  }
  
  .header-content {
    flex-direction: column;
    gap: 16px;
    align-items: stretch;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: stretch;
  }
  
  .filter-actions {
    margin-left: 0;
    justify-content: flex-end;
  }
  
  .batch-actions {
    flex-direction: column;
    gap: 12px;
    align-items: stretch;
  }
  
  .batch-buttons {
    justify-content: center;
  }
}
</style>