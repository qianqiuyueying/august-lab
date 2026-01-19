<template>
  <div>
    <!-- 页面头部 -->
    <div class="flex items-center justify-between mb-6">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-gray-50">个人信息管理</h1>
        <p class="text-gray-600 dark:text-gray-400 mt-1">管理您的个人资料和联系信息</p>
      </div>
      <div class="flex space-x-3">
        <el-button @click="previewProfile" :disabled="!hasChanges">
          <el-icon><View /></el-icon>
          预览效果
        </el-button>
        <el-button type="primary" @click="saveProfile" :loading="saving" :disabled="!hasChanges">
          <el-icon><Check /></el-icon>
          保存更改
        </el-button>
      </div>
    </div>

    <el-row :gutter="24">
      <!-- 左侧编辑表单 -->
      <el-col :span="16">
        <el-card>
          <template #header>
            <span class="font-semibold">编辑个人信息</span>
          </template>
          
          <el-form 
            ref="formRef"
            :model="form" 
            :rules="rules"
            label-width="120px"
            @submit.prevent="saveProfile"
          >
            <!-- 基本信息 -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-50 mb-4">基本信息</h3>
              
              <el-form-item label="姓名" prop="name">
                <el-input 
                  v-model="form.name" 
                  placeholder="请输入您的姓名"
                  maxlength="50"
                  show-word-limit
                />
              </el-form-item>
              
              <el-form-item label="职位标题" prop="title">
                <el-input 
                  v-model="form.title" 
                  placeholder="例如：全栈开发工程师"
                  maxlength="100"
                  show-word-limit
                />
              </el-form-item>
              
              <el-form-item label="个人简介" prop="bio">
                <RichTextEditor 
                  v-model="form.bio"
                  placeholder="请输入个人简介..."
                  :min-height="200"
                />
              </el-form-item>
            </div>

            <!-- 头像设置 -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-50 mb-4">头像设置</h3>
              
              <el-form-item label="头像" prop="avatar_url">
                <AvatarUpload 
                  v-model="form.avatar_url"
                  :loading="avatarUploading"
                  @upload="handleAvatarUpload"
                />
              </el-form-item>
            </div>

            <!-- 联系信息 -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-50 mb-4">联系信息</h3>
              
              <el-form-item label="邮箱地址" prop="email">
                <el-input 
                  v-model="form.email" 
                  placeholder="your.email@example.com"
                  type="email"
                />
              </el-form-item>
              
              <el-form-item label="电话号码" prop="phone">
                <el-input 
                  v-model="form.phone" 
                  placeholder="+86 138 0000 0000"
                />
              </el-form-item>
              
              <el-form-item label="所在地区" prop="location">
                <el-input 
                  v-model="form.location" 
                  placeholder="例如：北京市朝阳区"
                />
              </el-form-item>
            </div>

            <!-- 社交链接 -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-50 mb-4">社交链接</h3>
              
              <el-form-item label="GitHub" prop="github_url">
                <el-input 
                  v-model="form.github_url" 
                  placeholder="https://github.com/username"
                >
                  <template #prefix>
                    <el-icon><Link /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item label="LinkedIn" prop="linkedin_url">
                <el-input 
                  v-model="form.linkedin_url" 
                  placeholder="https://linkedin.com/in/username"
                >
                  <template #prefix>
                    <el-icon><Link /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item label="Twitter" prop="twitter_url">
                <el-input 
                  v-model="form.twitter_url" 
                  placeholder="https://twitter.com/username"
                >
                  <template #prefix>
                    <el-icon><Link /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
              
              <el-form-item label="个人网站" prop="website_url">
                <el-input 
                  v-model="form.website_url" 
                  placeholder="https://yourwebsite.com"
                >
                  <template #prefix>
                    <el-icon><Link /></el-icon>
                  </template>
                </el-input>
              </el-form-item>
            </div>

            <!-- 技能管理 -->
            <div class="mb-6">
              <h3 class="text-lg font-medium text-gray-900 dark:text-gray-50 mb-4">技能管理</h3>
              
              <SkillManager v-model="form.skills" />
            </div>
          </el-form>
        </el-card>
      </el-col>

      <!-- 右侧实时预览 -->
      <el-col :span="8">
        <div class="sticky top-6">
          <el-card>
            <template #header>
              <span class="font-semibold">实时预览</span>
            </template>
            
            <ProfilePreview :profile="form" />
          </el-card>
        </div>
      </el-col>
    </el-row>

    <!-- 预览对话框 -->
    <el-dialog 
      v-model="showPreviewDialog" 
      title="个人资料预览"
      width="80%"
      :fullscreen="previewFullscreen"
    >
      <template #header>
        <div class="flex items-center justify-between">
          <span>个人资料预览</span>
          <div class="flex items-center space-x-2">
            <el-button 
              type="text" 
              @click="previewFullscreen = !previewFullscreen"
              :icon="previewFullscreen ? 'Minus' : 'FullScreen'"
            />
          </div>
        </div>
      </template>
      
      <ProfilePreview :profile="form" :full-view="true" />
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, watch, defineAsyncComponent } from 'vue'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import { 
  View, 
  Check, 
  Link,
  FullScreen,
  Minus
} from '@element-plus/icons-vue'
import { profileAPI } from '../../shared/api'
import type { Profile, Skill } from '../../shared/types'
// 将静态导入改为动态导入以解决模块无默认导出的问题
const RichTextEditor = defineAsyncComponent(() => import('../components/RichTextEditor.vue'))
const AvatarUpload = defineAsyncComponent(() => import('../components/AvatarUpload.vue'))
const SkillManager = defineAsyncComponent(() => import('../components/SkillManager.vue'))
const ProfilePreview = defineAsyncComponent(() => import('../components/ProfilePreview.vue'))

const formRef = ref<FormInstance>()
const loading = ref(false)
const saving = ref(false)
const avatarUploading = ref(false)
const showPreviewDialog = ref(false)
const previewFullscreen = ref(false)
const originalData = ref<Profile | null>(null)

const form = reactive({
  name: '',
  title: '',
  bio: '',
  avatar_url: '',
  email: '',
  phone: '',
  location: '',
  github_url: '',
  linkedin_url: '',
  twitter_url: '',
  website_url: '',
  skills: [] as Skill[]
})

const rules = {
  name: [
    { required: true, message: '请输入姓名', trigger: 'blur' },
    { min: 2, max: 50, message: '姓名长度应为2-50个字符', trigger: 'blur' }
  ],
  title: [
    { required: true, message: '请输入职位标题', trigger: 'blur' },
    { min: 2, max: 100, message: '职位标题长度应为2-100个字符', trigger: 'blur' }
  ],
  bio: [
    { required: true, message: '请输入个人简介', trigger: 'blur' }
  ],
  email: [
    { 
      pattern: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, 
      message: '请输入有效的邮箱地址', 
      trigger: 'blur' 
    }
  ],
  phone: [
    { 
      pattern: /^[\+]?[0-9\s\-\(\)]{10,20}$/, 
      message: '请输入有效的电话号码', 
      trigger: 'blur' 
    }
  ],
  github_url: [
    { 
      pattern: /^https?:\/\/(www\.)?github\.com\/.+/, 
      message: '请输入有效的GitHub地址', 
      trigger: 'blur' 
    }
  ],
  linkedin_url: [
    { 
      pattern: /^https?:\/\/(www\.)?linkedin\.com\/.+/, 
      message: '请输入有效的LinkedIn地址', 
      trigger: 'blur' 
    }
  ],
  twitter_url: [
    { 
      pattern: /^https?:\/\/(www\.)?twitter\.com\/.+/, 
      message: '请输入有效的Twitter地址', 
      trigger: 'blur' 
    }
  ],
  website_url: [
    { 
      pattern: /^https?:\/\/.+/, 
      message: '请输入有效的网站地址', 
      trigger: 'blur' 
    }
  ]
}

// 检查是否有未保存的更改
const hasChanges = computed(() => {
  if (!originalData.value) return false
  
  const current = JSON.stringify(form)
  const original = JSON.stringify({
    name: originalData.value.name || '',
    title: originalData.value.title || '',
    bio: originalData.value.bio || '',
    avatar_url: originalData.value.avatar_url || '',
    email: originalData.value.email || '',
    phone: originalData.value.phone || '',
    location: originalData.value.location || '',
    github_url: originalData.value.github_url || '',
    linkedin_url: originalData.value.linkedin_url || '',
    twitter_url: originalData.value.twitter_url || '',
    website_url: originalData.value.website_url || '',
    skills: originalData.value.skills || []
  })
  
  return current !== original
})

const loadProfile = async () => {
  try {
    loading.value = true
    const response = await profileAPI.get()
    const profile = response.data
    
    if (profile) {
      // 保存原始数据
      originalData.value = profile
      
      // 填充表单，使用类型安全的方式访问可能不存在的属性
      Object.assign(form, {
        name: profile.name || '',
        title: profile.title || '',
        bio: profile.bio || '',
        avatar_url: profile.avatar_url || '',
        email: (profile as any).email || '',
        phone: (profile as any).phone || '',
        location: (profile as any).location || '',
        github_url: profile.github_url || '',
        linkedin_url: profile.linkedin_url || '',
        twitter_url: profile.twitter_url || '',
        website_url: (profile as any).website_url || '',
        skills: profile.skills || []
      })
    }
  } catch (error) {
    console.error('加载个人信息失败:', error)
    ElMessage.error('加载个人信息失败')
  } finally {
    loading.value = false
  }
}

const handleAvatarUpload = async (file: File) => {
  try {
    avatarUploading.value = true
    // 这里应该调用头像上传API
    // const response = await uploadAPI.uploadAvatar(file)
    // form.avatar_url = response.data.url
    
    // 临时模拟上传
    const reader = new FileReader()
    reader.onload = (e) => {
      form.avatar_url = e.target?.result as string
    }
    reader.readAsDataURL(file)
    
    ElMessage.success('头像上传成功')
  } catch (error) {
    console.error('头像上传失败:', error)
    ElMessage.error('头像上传失败')
  } finally {
    avatarUploading.value = false
  }
}

const saveProfile = async () => {
  if (!formRef.value) return
  
  try {
    await formRef.value.validate()
    saving.value = true
    
    const profileData = { ...form }
    await profileAPI.update(profileData)
    
    // 更新原始数据
    originalData.value = { ...profileData } as Profile
    
    ElMessage.success('个人信息保存成功')
  } catch (error) {
    if (error !== 'validation failed') {
      console.error('保存个人信息失败:', error)
      ElMessage.error('保存个人信息失败')
    }
  } finally {
    saving.value = false
  }
}

const previewProfile = () => {
  showPreviewDialog.value = true
}

// 页面离开前检查未保存的更改
const checkUnsavedChanges = () => {
  if (hasChanges.value) {
    return ElMessageBox.confirm(
      '您有未保存的更改，确定要离开吗？',
      '确认离开',
      {
        confirmButtonText: '离开',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
  }
  return Promise.resolve()
}

// 监听表单变化，提供实时反馈
watch(() => form.email, (newEmail) => {
  if (newEmail && !/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(newEmail)) {
    // 可以在这里添加实时验证反馈
  }
})

onMounted(() => {
  loadProfile()
})

// 页面卸载前检查
window.addEventListener('beforeunload', (e) => {
  if (hasChanges.value) {
    e.preventDefault()
    e.returnValue = ''
  }
})
</script>

<style scoped>
.sticky {
  position: sticky;
}
</style>