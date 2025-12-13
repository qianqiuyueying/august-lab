<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900">作品管理</h1>
        <p class="text-gray-600 mt-1">管理您的作品集</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建作品
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <el-input
          v-model="searchQuery"
          placeholder="搜索作品标题或描述..."
          clearable
          class="flex-1"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="statusFilter" placeholder="状态筛选" clearable @change="loadPortfolios">
          <el-option label="全部" value="" />
          <el-option label="推荐" value="featured" />
          <el-option label="普通" value="normal" />
        </el-select>
        
        <el-select v-model="sortBy" placeholder="排序方式" @change="loadPortfolios">
          <el-option label="创建时间" value="created_at" />
          <el-option label="更新时间" value="updated_at" />
          <el-option label="标题" value="title" />
        </el-select>
        
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 作品列表 -->
    <el-card>
      <el-table 
        v-loading="loading" 
        :data="portfolios" 
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column type="index" label="#" width="60" />
        
        <el-table-column prop="title" label="标题" min-width="200" sortable="custom">
          <template #default="{ row }">
            <div class="flex items-center space-x-3">
              <div class="w-12 h-12 rounded-lg overflow-hidden bg-gray-100 flex-shrink-0">
                <img 
                  v-if="row.image_url" 
                  :src="row.image_url" 
                  :alt="row.title"
                  class="w-full h-full object-cover"
                  @error="handleImageError"
                />
                <div v-else class="w-full h-full flex items-center justify-center text-gray-400">
                  <el-icon><Picture /></el-icon>
                </div>
              </div>
              <div>
                <div class="font-medium text-gray-900">{{ row.title }}</div>
                <div class="text-sm text-gray-500 truncate max-w-xs">{{ row.description }}</div>
              </div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="tech_stack" label="技术栈" width="200">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1">
              <el-tag 
                v-for="tech in (row.tech_stack || []).slice(0, 3)" 
                :key="tech" 
                size="small"
                type="info"
              >
                {{ tech }}
              </el-tag>
              <el-tag 
                v-if="(row.tech_stack || []).length > 3" 
                size="small" 
                type="info"
              >
                +{{ (row.tech_stack || []).length - 3 }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_featured" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_featured ? 'success' : 'info'" size="small">
              {{ row.is_featured ? '推荐' : '普通' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <div class="flex space-x-2">
              <el-button type="primary" size="small" @click="editPortfolio(row)">
                编辑
              </el-button>
              <el-button 
                :type="row.is_featured ? 'warning' : 'success'" 
                size="small" 
                @click="toggleFeatured(row)"
              >
                {{ row.is_featured ? '取消推荐' : '设为推荐' }}
              </el-button>
              <el-button type="danger" size="small" @click="deletePortfolio(row)">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 空状态 -->
      <div v-if="!loading && portfolios.length === 0" class="text-center py-12">
        <el-icon size="64" class="text-gray-300 mb-4"><Briefcase /></el-icon>
        <p class="text-gray-500 mb-4">暂无作品</p>
        <el-button type="primary" @click="showCreateDialog = true">
          创建第一个作品
        </el-button>
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingPortfolio ? '编辑作品' : '新建作品'"
      width="800px"
      @close="resetForm"
    >
      <PortfolioForm
        :portfolio="editingPortfolio"
        :loading="formLoading"
        @submit="handleSubmit"
        @cancel="showCreateDialog = false"
      />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineAsyncComponent } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Search, 
  Picture, 
  Briefcase 
} from '@element-plus/icons-vue'
import { portfolioAPI } from '../../shared/api'
import type { Portfolio } from '../../shared/types'
// 将静态导入改为动态导入以解决模块无默认导出的问题
const PortfolioForm = defineAsyncComponent(() => import('../components/PortfolioForm.vue'))

const loading = ref(false)
const formLoading = ref(false)
const showCreateDialog = ref(false)
const editingPortfolio = ref<Portfolio | null>(null)
const portfolios = ref<Portfolio[]>([])

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')

const loadPortfolios = async () => {
  try {
    loading.value = true
    const response = await portfolioAPI.getAll()
    let data = response.data || []
    
    // 应用筛选
    if (statusFilter.value === 'featured') {
      data = data.filter(item => item.is_featured)
    } else if (statusFilter.value === 'normal') {
      data = data.filter(item => !item.is_featured)
    }
    
    // 应用搜索
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      data = data.filter(item => 
        item.title.toLowerCase().includes(query) ||
        (item.description && item.description.toLowerCase().includes(query))
      )
    }
    
    // 应用排序
    data.sort((a, b) => {
      let aValue: any = (a as any)[sortBy.value as keyof Portfolio]
      let bValue: any = (b as any)[sortBy.value as keyof Portfolio]
      
      // 特殊处理日期字段
      if (sortBy.value.includes('_at')) {
        aValue = aValue ? new Date(aValue).getTime() : 0
        bValue = bValue ? new Date(bValue).getTime() : 0
      } else if (typeof aValue === 'string') {
        aValue = aValue.toLowerCase()
        bValue = bValue.toLowerCase()
      }
      
      if (sortOrder.value === 'asc') {
        return aValue > bValue ? 1 : -1
      } else {
        return aValue < bValue ? 1 : -1
      }
    })
    
    portfolios.value = data
  } catch (error) {
    console.error('加载作品列表失败:', error)
    ElMessage.error('加载作品列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadPortfolios()
}

const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  sortBy.value = prop
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
  loadPortfolios()
}

const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  sortBy.value = 'created_at'
  sortOrder.value = 'desc'
  loadPortfolios()
}

const editPortfolio = (portfolio: Portfolio) => {
  editingPortfolio.value = { ...portfolio }
  showCreateDialog.value = true
}

const handleSubmit = async (formData: Partial<Portfolio>) => {
  try {
    formLoading.value = true
    
    if (editingPortfolio.value) {
      // 更新作品
      await portfolioAPI.update(editingPortfolio.value.id, formData)
      ElMessage.success('作品更新成功')
    } else {
      // 创建作品，确保必填字段存在
      if (formData.title) {
        // 转换Partial<Portfolio>为PortfolioCreateData类型
        const createData: any = {
          title: formData.title,
          tech_stack: formData.tech_stack || [],
          is_featured: formData.is_featured || false,
          ...(formData.description && { description: formData.description }),
          ...(formData.content && { content: formData.content }),
          ...(formData.project_url && { project_url: formData.project_url }),
          ...(formData.github_url && { github_url: formData.github_url }),
          ...(formData.image_url && { image_url: formData.image_url }),
          ...(formData.development_timeline && { development_timeline: formData.development_timeline }),
          ...(formData.display_order !== undefined && { display_order: formData.display_order }),
          ...(formData.sort_order !== undefined && { sort_order: formData.sort_order })
        }
        await portfolioAPI.create(createData)
        ElMessage.success('作品创建成功')
      } else {
        throw new Error('作品标题不能为空')
      }
    }
    
    showCreateDialog.value = false
    loadPortfolios()
  } catch (error) {
    console.error('保存作品失败:', error)
    ElMessage.error('保存作品失败')
  } finally {
    formLoading.value = false
  }
}

const toggleFeatured = async (portfolio: Portfolio) => {
  try {
    await portfolioAPI.update(portfolio.id, {
      is_featured: !portfolio.is_featured
    })
    ElMessage.success(`已${portfolio.is_featured ? '取消推荐' : '设为推荐'}`)
    loadPortfolios()
  } catch (error) {
    console.error('更新推荐状态失败:', error)
    ElMessage.error('更新推荐状态失败')
  }
}

const deletePortfolio = async (portfolio: Portfolio) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除作品"${portfolio.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await portfolioAPI.delete(portfolio.id)
    ElMessage.success('作品删除成功')
    loadPortfolios()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除作品失败:', error)
      ElMessage.error('删除作品失败')
    }
  }
}

const resetForm = () => {
  editingPortfolio.value = null
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const handleImageError = (event: Event) => {
  const img = event.target as HTMLImageElement
  img.style.display = 'none'
}

onMounted(() => {
  loadPortfolios()
})
</script>