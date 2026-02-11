<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white">博客管理</h1>
        <p class="text-gray-600 dark:text-lab-muted mt-1">管理您的博客文章</p>
      </div>
      <el-button type="primary" @click="showCreateDialog = true">
        <el-icon><Plus /></el-icon>
        新建博客
      </el-button>
    </div>

    <!-- 搜索和筛选 -->
    <el-card class="mb-6">
      <div class="flex flex-col md:flex-row gap-4">
        <el-input
          v-model="searchQuery"
          placeholder="搜索博客标题或内容..."
          clearable
          class="flex-1"
          @input="handleSearch"
        >
          <template #prefix>
            <el-icon><Search /></el-icon>
          </template>
        </el-input>
        
        <el-select v-model="statusFilter" placeholder="发布状态" clearable @change="loadBlogs">
          <el-option label="全部" value="" />
          <el-option label="已发布" value="published" />
          <el-option label="草稿" value="draft" />
        </el-select>
        
        <el-select v-model="sortBy" placeholder="排序方式" @change="loadBlogs">
          <el-option label="创建时间" value="created_at" />
          <el-option label="更新时间" value="updated_at" />
          <el-option label="标题" value="title" />
          <el-option label="发布时间" value="published_at" />
        </el-select>
        
        <el-button @click="resetFilters">重置</el-button>
      </div>
    </el-card>

    <!-- 博客列表 -->
    <el-card>
      <el-table 
        v-loading="loading" 
        :data="blogs" 
        stripe
        @sort-change="handleSortChange"
      >
        <el-table-column type="index" label="#" width="60" />
        
        <el-table-column prop="title" label="标题" min-width="250" sortable="custom">
          <template #default="{ row }">
            <div>
              <div class="font-medium text-gray-900 dark:text-white mb-1">{{ row.title }}</div>
              <div class="text-sm text-gray-500 dark:text-lab-muted line-clamp-2">{{ row.excerpt || '暂无摘要' }}</div>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="tags" label="标签" width="200">
          <template #default="{ row }">
            <div class="flex flex-wrap gap-1">
              <el-tag 
                v-for="tag in (row.tags || []).slice(0, 3)" 
                :key="tag" 
                size="small"
                type="info"
              >
                {{ tag }}
              </el-tag>
              <el-tag 
                v-if="(row.tags || []).length > 3" 
                size="small" 
                type="info"
              >
                +{{ (row.tags || []).length - 3 }}
              </el-tag>
            </div>
          </template>
        </el-table-column>
        
        <el-table-column prop="is_published" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.is_published ? 'success' : 'warning'" size="small">
              {{ row.is_published ? '已发布' : '草稿' }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="reading_time" label="阅读时间" width="100">
          <template #default="{ row }">
            <span class="text-sm text-gray-500 dark:text-lab-muted">{{ row.reading_time || 0 }} 分钟</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="created_at" label="创建时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ formatDate(row.created_at) }}
          </template>
        </el-table-column>
        
        <el-table-column prop="published_at" label="发布时间" width="180" sortable="custom">
          <template #default="{ row }">
            {{ row.published_at ? formatDate(row.published_at) : '-' }}
          </template>
        </el-table-column>
        
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <div class="flex space-x-2">
              <el-button type="primary" size="small" @click="editBlog(row)">
                编辑
              </el-button>
              <el-button 
                :type="row.is_published ? 'warning' : 'success'" 
                size="small" 
                @click="togglePublished(row)"
              >
                {{ row.is_published ? '取消发布' : '发布' }}
              </el-button>
              <el-button 
                type="info" 
                size="small" 
                @click="showBlogPreview(row)"
              >
                预览
              </el-button>
              <el-button type="danger" size="small" @click="deleteBlog(row)">
                删除
              </el-button>
            </div>
          </template>
        </el-table-column>
      </el-table>
      
      <!-- 空状态 -->
      <div v-if="!loading && blogs.length === 0" class="text-center py-12">
        <el-icon size="64" class="text-gray-300 dark:text-lab-muted mb-4"><Document /></el-icon>
        <p class="text-gray-500 dark:text-lab-muted mb-4">暂无博客文章</p>
        <el-button type="primary" @click="showCreateDialog = true">
          写第一篇博客
        </el-button>
      </div>
    </el-card>

    <!-- 创建/编辑对话框 -->
    <el-dialog 
      v-model="showCreateDialog" 
      :title="editingBlog ? '编辑博客' : '新建博客'"
      width="90%"
      :fullscreen="isFullscreen"
      @close="resetForm"
    >
      <template #header>
        <div class="flex items-center justify-between">
          <span>{{ editingBlog ? '编辑博客' : '新建博客' }}</span>
          <div class="flex items-center space-x-2">
            <el-button 
              type="text" 
              @click="isFullscreen = !isFullscreen"
              :icon="isFullscreen ? 'Minus' : 'FullScreen'"
            />
          </div>
        </div>
      </template>
      
      <BlogForm
        :blog="editingBlog"
        :loading="formLoading"
        @submit="handleSubmit"
        @cancel="showCreateDialog = false"
        @preview="handlePreview"
      />
    </el-dialog>

    <!-- 预览对话框 -->
    <el-dialog 
      v-model="showPreviewDialog" 
      title="博客预览"
      width="80%"
      :fullscreen="previewFullscreen"
    >
      <template #header>
        <div class="flex items-center justify-between">
          <span>博客预览</span>
          <div class="flex items-center space-x-2">
            <el-button 
              type="text" 
              @click="previewFullscreen = !previewFullscreen"
              :icon="previewFullscreen ? 'Minus' : 'FullScreen'"
            />
          </div>
        </div>
      </template>
      
      <BlogPreview :blog="previewBlog" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, defineAsyncComponent } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Search, 
  Document,
  FullScreen,
  Minus
} from '@element-plus/icons-vue'
import { blogAPI } from '../../shared/api'
import type { Blog } from '../../shared/types'
const BlogForm = defineAsyncComponent(() => import('../components/BlogForm.vue'))
const BlogPreview = defineAsyncComponent(() => import('../components/BlogPreview.vue'))

const loading = ref(false)
const formLoading = ref(false)
const showCreateDialog = ref(false)
const showPreviewDialog = ref(false)
const isFullscreen = ref(false)
const previewFullscreen = ref(false)
const editingBlog = ref<Blog | null>(null)
const previewBlog = ref<Blog | null>(null)
const blogs = ref<Blog[]>([])

// 搜索和筛选
const searchQuery = ref('')
const statusFilter = ref('')
const sortBy = ref('created_at')
const sortOrder = ref<'asc' | 'desc'>('desc')

const loadBlogs = async () => {
  try {
    loading.value = true
    const response = await blogAPI.getAllAdmin()
    let data = response.data || []
    
    // 应用筛选
    if (statusFilter.value === 'published') {
      data = data.filter(item => item.is_published)
    } else if (statusFilter.value === 'draft') {
      data = data.filter(item => !item.is_published)
    }
    
    // 应用搜索
    if (searchQuery.value) {
      const query = searchQuery.value.toLowerCase()
      data = data.filter(item => {
        // 使用类型安全的方式访问可能不存在的属性
        const excerpt = (item as any).excerpt as string | undefined;
        const summary = (item as any).summary as string | undefined;
        
        return item.title.toLowerCase().includes(query) ||
               item.content.toLowerCase().includes(query) ||
               (excerpt && excerpt.toLowerCase().includes(query)) ||
               (summary && summary.toLowerCase().includes(query));
      });
    }
    
    // 应用排序
    data.sort((a, b) => {
      let aValue: any = (a as any)[sortBy.value as keyof Blog]
      let bValue: any = (b as any)[sortBy.value as keyof Blog]
      
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
    
    blogs.value = data
  } catch (error) {
    console.error('加载博客列表失败:', error)
    ElMessage.error('加载博客列表失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadBlogs()
}

const handleSortChange = ({ prop, order }: { prop: string; order: string }) => {
  sortBy.value = prop
  sortOrder.value = order === 'ascending' ? 'asc' : 'desc'
  loadBlogs()
}

const resetFilters = () => {
  searchQuery.value = ''
  statusFilter.value = ''
  sortBy.value = 'created_at'
  sortOrder.value = 'desc'
  loadBlogs()
}

const editBlog = (blog: Blog) => {
  editingBlog.value = { ...blog }
  showCreateDialog.value = true
}

const handleSubmit = async (formData: Partial<Blog>) => {
  try {
    formLoading.value = true
    
    if (editingBlog.value) {
      // 更新博客
      await blogAPI.update(editingBlog.value.id, formData)
      ElMessage.success('博客更新成功')
    } else {
      // 创建博客，确保必填字段存在
      if (formData.title && formData.content) {
        // 转换Partial<Blog>为BlogCreateData类型
        const createData: any = {
          title: formData.title,
          content: formData.content,
          tags: formData.tags || [],
          is_published: formData.is_published || false,
          ...(formData.excerpt && { excerpt: formData.excerpt }),
          ...(formData.summary && { summary: formData.summary }),
          ...(formData.published_at && { published_at: formData.published_at }),
          ...(formData.cover_image && { cover_image: formData.cover_image }),
          ...(formData.reading_time !== undefined && { reading_time: formData.reading_time }),
          ...(formData.sort_order !== undefined && { sort_order: formData.sort_order }),
          ...(formData.seo_title && { seo_title: formData.seo_title }),
          ...(formData.seo_description && { seo_description: formData.seo_description }),
          ...(formData.seo_keywords && { seo_keywords: formData.seo_keywords })
        }
        await blogAPI.create(createData)
        ElMessage.success('博客创建成功')
      } else {
        throw new Error('博客标题和内容不能为空')
      }
    }
    
    showCreateDialog.value = false
    loadBlogs()
  } catch (error) {
    console.error('保存博客失败:', error)
    ElMessage.error('保存博客失败')
  } finally {
    formLoading.value = false
  }
}

const togglePublished = async (blog: Blog) => {
  try {
    const newStatus = !blog.is_published
    const updateData: Partial<Blog> = {
      is_published: newStatus
    }
    
    // 如果是发布操作，设置发布时间
    if (newStatus) {
      updateData.published_at = new Date().toISOString()
    }
    
    await blogAPI.update(blog.id, updateData)
    ElMessage.success(`博客已${newStatus ? '发布' : '取消发布'}`)
    loadBlogs()
  } catch (error) {
    console.error('更新发布状态失败:', error)
    ElMessage.error('更新发布状态失败')
  }
}

const showBlogPreview = (blog: Blog) => {
  previewBlog.value = blog
  showPreviewDialog.value = true
}

const handlePreview = (blog: Partial<Blog>) => {
  previewBlog.value = blog as Blog
  showPreviewDialog.value = true
}

const deleteBlog = async (blog: Blog) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除博客"${blog.title}"吗？此操作不可恢复。`,
      '确认删除',
      {
        confirmButtonText: '确定删除',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    await blogAPI.delete(blog.id)
    ElMessage.success('博客删除成功')
    loadBlogs()
  } catch (error) {
    if (error !== 'cancel') {
      console.error('删除博客失败:', error)
      ElMessage.error('删除博客失败')
    }
  }
}

const resetForm = () => {
  editingBlog.value = null
  isFullscreen.value = false
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

onMounted(() => {
  loadBlogs()
})
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>