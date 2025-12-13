<template>
  <el-form 
    ref="formRef"
    :model="form" 
    :rules="rules"
    label-width="100px"
    @submit.prevent="handleSubmit"
  >
    <el-row :gutter="20">
      <el-col :span="24">
        <el-form-item label="博客标题" prop="title">
          <el-input 
            v-model="form.title" 
            placeholder="请输入博客标题"
            maxlength="200"
            show-word-limit
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="博客摘要" prop="excerpt">
          <el-input 
            v-model="form.excerpt" 
            type="textarea"
            :rows="3"
            placeholder="请输入博客摘要（可选，如不填写将自动从内容中提取）"
            maxlength="300"
            show-word-limit
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="标签" prop="tags">
          <div class="space-y-3">
            <div class="flex flex-wrap gap-2">
              <el-tag
                v-for="(tag, index) in form.tags"
                :key="index"
                closable
                @close="removeTag(index)"
                type="primary"
              >
                {{ tag }}
              </el-tag>
            </div>
            <div class="flex space-x-2">
              <el-input
                v-model="newTag"
                placeholder="添加标签"
                @keyup.enter="addTag"
                class="flex-1"
              />
              <el-button @click="addTag" :disabled="!newTag.trim()">
                添加
              </el-button>
            </div>
            <div class="text-sm text-gray-500">
              常用标签：
              <el-button 
                v-for="tag in commonTags" 
                :key="tag"
                type="text" 
                size="small"
                @click="addCommonTag(tag)"
                class="p-1"
              >
                {{ tag }}
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="博客内容" prop="content">
          <MarkdownEditor 
            v-model="form.content"
            placeholder="请输入博客内容（支持Markdown格式）"
            @input="updateReadingTime"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="8">
        <el-form-item label="发布状态">
          <el-switch 
            v-model="form.is_published"
            active-text="发布"
            inactive-text="草稿"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="8">
        <el-form-item label="阅读时间">
          <el-input-number 
            v-model="form.reading_time"
            :min="1"
            :max="999"
            placeholder="分钟"
          />
          <span class="ml-2 text-sm text-gray-500">分钟（自动计算：{{ calculatedReadingTime }}）</span>
        </el-form-item>
      </el-col>
      
      <el-col :span="8">
        <el-form-item label="排序权重">
          <el-input-number 
            v-model="form.sort_order"
            :min="0"
            :max="999"
            placeholder="数值越大排序越靠前"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="24" v-if="form.is_published">
        <el-form-item label="发布时间">
          <el-date-picker
            v-model="publishedDate"
            type="datetime"
            placeholder="选择发布时间"
            format="YYYY-MM-DD HH:mm:ss"
            value-format="YYYY-MM-DD HH:mm:ss"
            @change="updatePublishedAt"
          />
          <span class="ml-2 text-sm text-gray-500">留空则使用当前时间</span>
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="SEO设置">
          <el-collapse>
            <el-collapse-item title="搜索引擎优化" name="seo">
              <el-row :gutter="20">
                <el-col :span="24">
                  <el-form-item label="SEO标题">
                    <el-input 
                      v-model="form.seo_title" 
                      placeholder="SEO标题（留空则使用博客标题）"
                      maxlength="60"
                      show-word-limit
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="SEO描述">
                    <el-input 
                      v-model="form.seo_description" 
                      type="textarea"
                      :rows="3"
                      placeholder="SEO描述（留空则使用博客摘要）"
                      maxlength="160"
                      show-word-limit
                    />
                  </el-form-item>
                </el-col>
                <el-col :span="24">
                  <el-form-item label="SEO关键词">
                    <el-input 
                      v-model="form.seo_keywords" 
                      placeholder="SEO关键词，用逗号分隔"
                    />
                  </el-form-item>
                </el-col>
              </el-row>
            </el-collapse-item>
          </el-collapse>
        </el-form-item>
      </el-col>
    </el-row>
    
    <div class="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button @click="handlePreview" :disabled="!form.title || !form.content">
        预览
      </el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ blog ? '更新博客' : '创建博客' }}
      </el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch, computed } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import type { Blog } from '../../shared/types'
import MarkdownEditor from './MarkdownEditor.vue'

interface Props {
  blog?: Blog | null
  loading?: boolean
}

interface Emits {
  (e: 'submit', data: Partial<Blog>): void
  (e: 'cancel'): void
  (e: 'preview', data: Partial<Blog>): void
}

const props = withDefaults(defineProps<Props>(), {
  blog: null,
  loading: false
})

const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const newTag = ref('')
const publishedDate = ref('')

const form = reactive({
  title: '',
  excerpt: '',
  content: '',
  tags: [] as string[],
  is_published: false,
  reading_time: 1,
  sort_order: 0,
  published_at: '',
  seo_title: '',
  seo_description: '',
  seo_keywords: ''
})

const rules = {
  title: [
    { required: true, message: '请输入博客标题', trigger: 'blur' },
    { min: 2, max: 200, message: '标题长度应为2-200个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入博客内容', trigger: 'blur' },
    { min: 10, message: '内容长度至少10个字符', trigger: 'blur' }
  ]
}

const commonTags = [
  '前端开发', '后端开发', '全栈开发', 'Vue.js', 'React', 'Angular',
  'JavaScript', 'TypeScript', 'Node.js', 'Python', 'Java',
  '数据库', 'MySQL', 'MongoDB', 'Redis',
  '架构设计', '性能优化', '代码规范', '最佳实践',
  '工具推荐', '学习笔记', '项目总结', '技术分享'
]

// 计算阅读时间（基于内容长度，平均每分钟200字）
const calculatedReadingTime = computed(() => {
  const contentLength = form.content.length
  const wordsPerMinute = 200
  const time = Math.max(1, Math.ceil(contentLength / wordsPerMinute))
  return time
})

const addTag = () => {
  const tag = newTag.value.trim()
  if (tag && !form.tags.includes(tag)) {
    form.tags.push(tag)
    newTag.value = ''
  }
}

const removeTag = (index: number) => {
  form.tags.splice(index, 1)
}

const addCommonTag = (tag: string) => {
  if (!form.tags.includes(tag)) {
    form.tags.push(tag)
  }
}

const updateReadingTime = () => {
  // 自动更新阅读时间
  form.reading_time = calculatedReadingTime.value
}

const updatePublishedAt = (value: string) => {
  form.published_at = value || ''
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 如果没有摘要，从内容中自动提取
    if (!form.excerpt && form.content) {
      const plainText = form.content.replace(/[#*`\[\]()]/g, '').trim()
      form.excerpt = plainText.substring(0, 200) + (plainText.length > 200 ? '...' : '')
    }
    
    // 如果发布但没有设置发布时间，使用当前时间
    if (form.is_published && !form.published_at) {
      form.published_at = new Date().toISOString()
    }
    
    // 如果取消发布，清空发布时间
    if (!form.is_published) {
      form.published_at = ''
    }
    
    const submitData = { ...form }
    emit('submit', submitData)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

const handlePreview = () => {
  if (!form.title || !form.content) {
    ElMessage.warning('请先填写标题和内容')
    return
  }
  
  // 生成预览数据
  const previewData = {
    ...form,
    excerpt: form.excerpt || (form.content.replace(/[#*`\[\]()]/g, '').trim().substring(0, 200) + '...'),
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  }
  
  emit('preview', previewData)
}

// 监听props变化，初始化表单
watch(() => props.blog, (blog) => {
  if (blog) {
    Object.assign(form, {
      title: blog.title || '',
      excerpt: blog.excerpt || '',
      content: blog.content || '',
      tags: [...(blog.tags || [])],
      is_published: blog.is_published || false,
      reading_time: blog.reading_time || 1,
      sort_order: blog.sort_order || 0,
      published_at: blog.published_at || '',
      seo_title: blog.seo_title || '',
      seo_description: blog.seo_description || '',
      seo_keywords: blog.seo_keywords || ''
    })
    
    // 设置发布时间选择器的值
    publishedDate.value = blog.published_at || ''
  } else {
    // 重置表单
    Object.assign(form, {
      title: '',
      excerpt: '',
      content: '',
      tags: [],
      is_published: false,
      reading_time: 1,
      sort_order: 0,
      published_at: '',
      seo_title: '',
      seo_description: '',
      seo_keywords: ''
    })
    publishedDate.value = ''
  }
}, { immediate: true })

// 监听内容变化，自动更新阅读时间
watch(() => form.content, () => {
  updateReadingTime()
})
</script>