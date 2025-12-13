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
        <el-form-item label="作品标题" prop="title">
          <el-input 
            v-model="form.title" 
            placeholder="请输入作品标题"
            maxlength="100"
            show-word-limit
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="作品描述" prop="description">
          <el-input 
            v-model="form.description" 
            type="textarea"
            :rows="4"
            placeholder="请输入作品描述"
            maxlength="500"
            show-word-limit
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="12">
        <el-form-item label="项目链接" prop="project_url">
          <el-input 
            v-model="form.project_url" 
            placeholder="https://example.com"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="12">
        <el-form-item label="源码链接" prop="github_url">
          <el-input 
            v-model="form.github_url" 
            placeholder="https://github.com/username/repo"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="作品图片" prop="image_url">
          <ImageUpload 
            v-model="form.image_url"
            :loading="imageUploading"
            @upload="handleImageUpload"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="技术栈" prop="tech_stack">
          <div class="space-y-3">
            <div class="flex flex-wrap gap-2">
              <el-tag
                v-for="(tech, index) in form.tech_stack"
                :key="index"
                closable
                @close="removeTech(index)"
                type="primary"
              >
                {{ tech }}
              </el-tag>
            </div>
            <div class="flex space-x-2">
              <el-input
                v-model="newTech"
                placeholder="添加技术栈标签"
                @keyup.enter="addTech"
                class="flex-1"
              />
              <el-button @click="addTech" :disabled="!newTech.trim()">
                添加
              </el-button>
            </div>
            <div class="text-sm text-gray-500">
              常用技术栈：
              <el-button 
                v-for="tech in commonTechs" 
                :key="tech"
                type="text" 
                size="small"
                @click="addCommonTech(tech)"
                class="p-1"
              >
                {{ tech }}
              </el-button>
            </div>
          </div>
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="开发时间线">
          <div class="space-y-3">
            <div 
              v-for="(milestone, index) in form.development_timeline" 
              :key="index"
              class="flex items-center space-x-3 p-3 border border-gray-200 rounded-lg"
            >
              <el-input 
                v-model="milestone.date" 
                type="date"
                class="w-40"
              />
              <el-input 
                v-model="milestone.description" 
                placeholder="里程碑描述"
                class="flex-1"
              />
              <el-button 
                type="danger" 
                size="small" 
                @click="removeTimeline(index)"
                :icon="Delete"
              />
            </div>
            <el-button @click="addTimeline" type="dashed" class="w-full">
              <el-icon><Plus /></el-icon>
              添加时间线
            </el-button>
          </div>
        </el-form-item>
      </el-col>
      
      <el-col :span="24">
        <el-form-item label="详细内容" prop="content">
          <MarkdownEditor 
            v-model="form.content"
            placeholder="请输入作品的详细介绍（支持Markdown格式）"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="12">
        <el-form-item label="推荐作品">
          <el-switch 
            v-model="form.is_featured"
            active-text="是"
            inactive-text="否"
          />
        </el-form-item>
      </el-col>
      
      <el-col :span="12">
        <el-form-item label="排序权重">
          <el-input-number 
            v-model="form.sort_order"
            :min="0"
            :max="999"
            placeholder="数值越大排序越靠前"
          />
        </el-form-item>
      </el-col>
    </el-row>
    
    <div class="flex justify-end space-x-3 mt-6 pt-6 border-t border-gray-200">
      <el-button @click="$emit('cancel')">取消</el-button>
      <el-button type="primary" :loading="loading" @click="handleSubmit">
        {{ portfolio ? '更新作品' : '创建作品' }}
      </el-button>
    </div>
  </el-form>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { ElMessage, type FormInstance } from 'element-plus'
import { Plus, Delete } from '@element-plus/icons-vue'
import type { Portfolio } from '../../shared/types'
import ImageUpload from './ImageUpload.vue'
import MarkdownEditor from './MarkdownEditor.vue'

interface Props {
  portfolio?: Portfolio | null
  loading?: boolean
}

interface Emits {
  (e: 'submit', data: Partial<Portfolio>): void
  (e: 'cancel'): void
}

const props = withDefaults(defineProps<Props>(), {
  portfolio: null,
  loading: false
})

const emit = defineEmits<Emits>()

const formRef = ref<FormInstance>()
const imageUploading = ref(false)
const newTech = ref('')

const form = reactive({
  title: '',
  description: '',
  content: '',
  project_url: '',
  github_url: '',
  image_url: '',
  tech_stack: [] as string[],
  development_timeline: [] as Array<{ date: string; description: string }>,
  is_featured: false,
  sort_order: 0
})

const rules = {
  title: [
    { required: true, message: '请输入作品标题', trigger: 'blur' },
    { min: 2, max: 100, message: '标题长度应为2-100个字符', trigger: 'blur' }
  ],
  description: [
    { required: true, message: '请输入作品描述', trigger: 'blur' },
    { min: 10, max: 500, message: '描述长度应为10-500个字符', trigger: 'blur' }
  ],
  content: [
    { required: true, message: '请输入作品详细内容', trigger: 'blur' }
  ],
  project_url: [
    { 
      pattern: /^https?:\/\/.+/, 
      message: '请输入有效的URL地址', 
      trigger: 'blur' 
    }
  ],
  github_url: [
    { 
      pattern: /^https?:\/\/(www\.)?github\.com\/.+/, 
      message: '请输入有效的GitHub地址', 
      trigger: 'blur' 
    }
  ]
}

const commonTechs = [
  'Vue.js', 'React', 'Angular', 'TypeScript', 'JavaScript',
  'Node.js', 'Python', 'Java', 'Go', 'Rust',
  'HTML', 'CSS', 'Sass', 'Tailwind CSS', 'Bootstrap',
  'MySQL', 'PostgreSQL', 'MongoDB', 'Redis',
  'Docker', 'Kubernetes', 'AWS', 'Nginx'
]

const addTech = () => {
  const tech = newTech.value.trim()
  if (tech && !form.tech_stack.includes(tech)) {
    form.tech_stack.push(tech)
    newTech.value = ''
  }
}

const removeTech = (index: number) => {
  form.tech_stack.splice(index, 1)
}

const addCommonTech = (tech: string) => {
  if (!form.tech_stack.includes(tech)) {
    form.tech_stack.push(tech)
  }
}

const addTimeline = () => {
  form.development_timeline.push({
    date: '',
    description: ''
  })
}

const removeTimeline = (index: number) => {
  form.development_timeline.splice(index, 1)
}

const handleImageUpload = async (file: File) => {
  try {
    imageUploading.value = true
    // 这里应该调用图片上传API
    // const response = await uploadAPI.uploadImage(file)
    // form.image_url = response.data.url
    
    // 临时模拟上传
    const reader = new FileReader()
    reader.onload = (e) => {
      form.image_url = e.target?.result as string
    }
    reader.readAsDataURL(file)
    
    ElMessage.success('图片上传成功')
  } catch (error) {
    console.error('图片上传失败:', error)
    ElMessage.error('图片上传失败')
  } finally {
    imageUploading.value = false
  }
}

const handleSubmit = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    
    // 验证时间线数据
    const validTimeline = form.development_timeline.filter(
      item => item.date && item.description.trim()
    )
    
    const submitData = {
      ...form,
      development_timeline: validTimeline
    }
    
    emit('submit', submitData)
  } catch (error) {
    console.error('表单验证失败:', error)
  }
}

// 监听props变化，初始化表单
watch(() => props.portfolio, (portfolio) => {
  if (portfolio) {
    Object.assign(form, {
      title: portfolio.title || '',
      description: portfolio.description || '',
      content: portfolio.content || '',
      project_url: portfolio.project_url || '',
      github_url: portfolio.github_url || '',
      image_url: portfolio.image_url || '',
      tech_stack: [...(portfolio.tech_stack || [])],
      development_timeline: [...(portfolio.development_timeline || [])],
      is_featured: portfolio.is_featured || false,
      sort_order: portfolio.sort_order || 0
    })
  } else {
    // 重置表单
    Object.assign(form, {
      title: '',
      description: '',
      content: '',
      project_url: '',
      github_url: '',
      image_url: '',
      tech_stack: [],
      development_timeline: [],
      is_featured: false,
      sort_order: 0
    })
  }
}, { immediate: true })
</script>