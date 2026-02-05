<template>
  <div class="min-h-screen bg-gradient-to-br from-primary-50 via-white to-primary-50/50 dark:from-slate-900 dark:via-slate-800 dark:to-slate-900 flex items-center justify-center px-4">
    <div class="max-w-md w-full space-y-8">
      <div class="text-center">
        <div class="flex items-center justify-center space-x-2 mb-6">
          <div class="w-10 h-10 bg-primary-500 rounded-lg flex items-center justify-center shadow-md">
            <span class="text-white font-bold">A</span>
          </div>
          <span class="text-2xl font-bold text-gray-900 dark:text-gray-50">管理后台</span>
        </div>
        <h2 class="text-xl text-gray-600 dark:text-gray-400">登录到管理系统</h2>
      </div>
      
      <el-card class="shadow-xl border border-gray-200 dark:border-slate-700/50">
        <el-form 
          ref="loginFormRef"
          :model="loginForm" 
          :rules="rules"
          @submit.prevent="handleLogin"
        >
          <el-form-item prop="username">
            <el-input
              v-model="loginForm.username"
              placeholder="用户名"
              size="large"
              :prefix-icon="User"
            />
          </el-form-item>
          
          <el-form-item prop="password">
            <el-input
              v-model="loginForm.password"
              type="password"
              placeholder="密码"
              size="large"
              :prefix-icon="Lock"
              show-password
              @keyup.enter="handleLogin"
            />
          </el-form-item>
          
          <el-form-item>
            <el-button 
              type="primary" 
              size="large" 
              :loading="formState.submitting"
              :disabled="loginAttempts >= maxAttempts"
              @click="handleLogin"
              class="w-full"
            >
              {{ formState.submitting ? '登录中...' : '登录' }}
            </el-button>
          </el-form-item>
        </el-form>
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { User, Lock } from '@element-plus/icons-vue'
import { authAPI } from '../../shared/api'
import { useFormValidation, validators } from '../../shared/composables/useFormValidation'
import { useUserFeedback } from '../../shared/composables/useUserFeedback'
import { useErrorHandler } from '../../shared/composables/useErrorHandler'

const router = useRouter()
const loginFormRef = ref<FormInstance>()
const loginAttempts = ref(0)
const maxAttempts = 5

// 用户反馈和错误处理
const { showSuccess, showError, showWarning, withFeedback } = useUserFeedback()
const { handleError, safeExecute } = useErrorHandler()

// 表单验证
const {
  formData: loginForm,
  formState,
  submitForm,
  resetForm
} = useFormValidation(
  {
    username: '',
    password: ''
  },
  {
    username: [
      validators.required('请输入用户名'),
      validators.minLength(3, '用户名至少需要3个字符'),
      validators.maxLength(20, '用户名最多20个字符')
    ],
    password: [
      validators.required('请输入密码'),
      validators.minLength(6, '密码至少需要6个字符'),
      validators.maxLength(50, '密码最多50个字符')
    ]
  }
)

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度应为3-20个字符', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, max: 50, message: '密码长度应为6-50个字符', trigger: 'blur' }
  ]
}



const handleLogin = async () => {
  // 检查登录尝试次数
  if (loginAttempts.value >= maxAttempts) {
    showWarning('登录尝试次数过多，请稍后再试')
    return
  }
  
  const success = await submitForm(
    async (data) => {
      // 调用登录API
      const response = await authAPI.login({
        username: data.username,
        password: data.password
      })
      
      // 保存登录状态
      localStorage.setItem('admin_token', response.data.access_token)
      
      // 重置登录尝试次数
      loginAttempts.value = 0
      
      // 跳转到管理后台
      const redirect = router.currentRoute.value.query.redirect as string
      router.push(redirect || '/admin')
    },
    {
      showSuccess: true,
      successMessage: '登录成功，正在跳转...',
      preventDuplicate: true
    }
  )
  
  if (!success) {
    loginAttempts.value++
    
    // 清空密码字段
    loginForm.password = ''
    
    // 显示剩余尝试次数
    const remainingAttempts = maxAttempts - loginAttempts.value
    if (remainingAttempts > 0) {
      showWarning(`登录失败，还可尝试 ${remainingAttempts} 次`)
    }
  }
}

// 检查是否已经登录
onMounted(() => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    // 验证token有效性
    safeExecute(
      async () => {
        await authAPI.verify()
        router.push('/admin')
      },
      undefined,
      () => {
        // token无效，清除
        localStorage.removeItem('admin_token')
      }
    )
  }
})
</script>