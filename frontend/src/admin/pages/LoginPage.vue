<template>
  <div class="min-h-screen flex items-center justify-center relative overflow-hidden bg-lab-bg text-white">
    <!-- 背景动画 -->
    <div class="absolute inset-0 z-0">
      <div class="absolute inset-0 opacity-20" style="background-image: linear-gradient(rgba(255, 255, 255, 0.1) 1px, transparent 1px), linear-gradient(90deg, rgba(255, 255, 255, 0.1) 1px, transparent 1px); background-size: 40px 40px;"></div>
      <div class="absolute top-0 left-0 w-full h-1 bg-gradient-to-r from-transparent via-lab-accent to-transparent animate-scan opacity-50"></div>
      <div class="absolute -top-40 -right-40 w-96 h-96 bg-lab-accent/10 rounded-full blur-3xl"></div>
      <div class="absolute -bottom-40 -left-40 w-96 h-96 bg-blue-600/10 rounded-full blur-3xl"></div>
    </div>

    <div class="w-full max-w-md p-8 relative z-10 animate-scale-in">
      <!-- Logo -->
      <div class="text-center mb-10">
        <div class="inline-flex items-center justify-center w-16 h-16 rounded-2xl bg-gradient-to-br from-lab-accent to-blue-600 shadow-[0_0_30px_rgba(0,240,255,0.3)] mb-6 transform hover:scale-105 transition-transform duration-300">
          <span class="text-black font-bold text-3xl font-mono">A</span>
        </div>
        <h1 class="text-3xl font-display font-bold tracking-tight mb-2">
          AUGUST<span class="text-lab-accent">.ADMIN</span>
        </h1>
        <p class="text-lab-muted">Secure Access Portal</p>
      </div>

      <!-- 登录卡片 -->
      <div class="glass-panel rounded-2xl p-8 border border-lab-border shadow-2xl backdrop-blur-xl bg-lab-card/50">
        <el-form 
          ref="loginFormRef"
          :model="loginForm" 
          :rules="rules"
          @submit.prevent="handleLogin"
          class="space-y-6"
        >
          <el-form-item prop="username">
            <div class="relative w-full group">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-lab-muted group-focus-within:text-lab-accent transition-colors">
                <el-icon><User /></el-icon>
              </div>
              <input
                v-model="loginForm.username"
                type="text"
                class="w-full bg-lab-surface border border-lab-border rounded-lg py-3 pl-10 pr-4 text-lab-text placeholder-lab-muted focus:outline-none focus:border-lab-accent focus:ring-1 focus:ring-lab-accent transition-all"
                placeholder="Username"
              />
            </div>
          </el-form-item>
          
          <el-form-item prop="password">
            <div class="relative w-full group">
              <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none text-lab-muted group-focus-within:text-lab-accent transition-colors">
                <el-icon><Lock /></el-icon>
              </div>
              <input
                v-model="loginForm.password"
                type="password"
                class="w-full bg-lab-surface border border-lab-border rounded-lg py-3 pl-10 pr-4 text-lab-text placeholder-lab-muted focus:outline-none focus:border-lab-accent focus:ring-1 focus:ring-lab-accent transition-all"
                placeholder="Password"
                @keyup.enter="handleLogin"
              />
            </div>
          </el-form-item>
          
          <div class="pt-2">
            <button 
              type="button"
              @click="handleLogin"
              :disabled="formState.submitting || loginAttempts >= maxAttempts"
              class="w-full bg-lab-accent hover:bg-lab-accent-hover text-black font-bold py-3 px-4 rounded-lg transition-all transform hover:-translate-y-0.5 hover:shadow-[0_0_20px_rgba(0,240,255,0.4)] disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none disabled:shadow-none flex items-center justify-center gap-2"
            >
              <span v-if="formState.submitting" class="animate-spin rounded-full h-4 w-4 border-2 border-black border-t-transparent"></span>
              {{ formState.submitting ? 'Authenticating...' : 'Sign In' }}
            </button>
          </div>
        </el-form>
      </div>
      
      <div class="mt-8 text-center text-xs text-lab-muted">
        <p>&copy; 2026 August System. All rights reserved.</p>
      </div>
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
      validators.required('Username is required'),
      validators.minLength(3, 'Minimum 3 characters'),
      validators.maxLength(20, 'Maximum 20 characters')
    ],
    password: [
      validators.required('Password is required'),
      validators.minLength(6, 'Minimum 6 characters'),
      validators.maxLength(50, 'Maximum 50 characters')
    ]
  }
)

const rules = {
  username: [
    { required: true, message: 'Username is required', trigger: 'blur' },
    { min: 3, max: 20, message: 'Length should be 3 to 20', trigger: 'blur' }
  ],
  password: [
    { required: true, message: 'Password is required', trigger: 'blur' },
    { min: 6, max: 50, message: 'Length should be 6 to 50', trigger: 'blur' }
  ]
}

const handleLogin = async () => {
  if (loginAttempts.value >= maxAttempts) {
    showWarning('Too many attempts. Please try again later.')
    return
  }
  
  const success = await submitForm(
    async (data) => {
      const response = await authAPI.login({
        username: data.username,
        password: data.password
      })
      
      localStorage.setItem('admin_token', response.data.access_token)
      loginAttempts.value = 0
      
      const redirect = router.currentRoute.value.query.redirect as string
      router.push(redirect || '/admin')
    },
    {
      showSuccess: true,
      successMessage: 'Welcome back!',
      preventDuplicate: true
    }
  )
  
  if (!success) {
    loginAttempts.value++
    loginForm.password = ''
    const remainingAttempts = maxAttempts - loginAttempts.value
    if (remainingAttempts > 0) {
      showWarning(`Login failed. ${remainingAttempts} attempts remaining.`)
    }
  }
}

onMounted(() => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    safeExecute(
      async () => {
        await authAPI.verify()
        router.push('/admin')
      },
      undefined,
      () => {
        localStorage.removeItem('admin_token')
      }
    )
  }
})
</script>

<style scoped>
/* Custom Input Styles to override Element Plus defaults if needed, though we used native inputs */
input:-webkit-autofill,
input:-webkit-autofill:hover, 
input:-webkit-autofill:focus, 
input:-webkit-autofill:active{
    -webkit-box-shadow: 0 0 0 30px #121212 inset !important;
    -webkit-text-fill-color: white !important;
}
</style>