<template>
  <div class="min-h-screen bg-gray-50">
    <!-- 加载状态 -->
    <div v-if="loading" class="min-h-screen flex items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
    </div>

    <!-- 错误状态 -->
    <div v-else-if="error" class="min-h-screen flex items-center justify-center">
      <div class="text-center">
        <h3 class="text-lg font-semibold text-red-600 mb-2">加载失败</h3>
        <p class="text-red-500 mb-4">{{ error }}</p>
        <button @click="loadProfile" class="btn-primary">重试</button>
      </div>
    </div>

    <!-- 关于我内容 -->
    <div v-else class="section-padding">
      <ResponsiveContainer size="xl">
        <!-- 个人介绍 -->
        <section class="bg-white rounded-xl shadow-sm p-8 mb-8">
          <div class="flex flex-col lg:flex-row items-center lg:items-start gap-8">
            <!-- 头像 -->
            <div class="w-32 h-32 bg-gradient-to-br from-primary-400 to-blue-500 rounded-full flex items-center justify-center">
              <svg class="w-16 h-16 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            
            <!-- 个人信息 -->
            <div class="flex-1 text-center lg:text-left">
              <h1 class="heading-1 mb-4">{{ profile?.name || 'August' }}</h1>
              <p class="text-xl text-primary-600 font-medium mb-6">
                {{ profile?.title || '全栈开发者 & 技术爱好者' }}
              </p>
              <div class="text-gray-600 leading-relaxed" v-html="renderedBio"></div>
            </div>
          </div>
        </section>

        <!-- 技能展示 -->
        <section class="bg-white rounded-xl shadow-sm p-8 mb-8">
          <h2 class="heading-2 mb-8 text-center">技能专长</h2>
          
          <div v-if="skillsByCategory && Object.keys(skillsByCategory).length > 0" class="space-y-8">
            <div v-for="(skills, category) in skillsByCategory" :key="category">
              <h3 class="heading-4 mb-6 text-center">{{ getCategoryDisplayName(category) }}</h3>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div v-for="skill in skills" :key="skill.name" class="p-4 rounded-lg border border-gray-100">
                  <div class="flex items-center justify-between mb-2">
                    <span class="font-medium text-gray-900">{{ skill.name }}</span>
                    <span class="text-sm text-gray-500">{{ skill.level }}%</span>
                  </div>
                  <div class="w-full bg-gray-200 rounded-full h-3">
                    <div 
                      class="h-full rounded-full bg-gradient-to-r from-primary-500 to-blue-500 transition-all duration-1000"
                      :style="{ width: animatedSkills[skill.name] + '%' }"
                    ></div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- 技能为空时的占位符 -->
          <div v-else class="text-center py-12">
            <p class="text-gray-500">技能信息正在完善中</p>
          </div>
        </section>

        <!-- 联系方式 -->
        <section class="bg-white rounded-xl shadow-sm p-8">
          <h2 class="heading-2 mb-8 text-center">联系我</h2>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
            <!-- Email -->
            <a href="mailto:hello@august.lab" class="contact-card">
              <div class="w-12 h-12 bg-red-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-red-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" />
                </svg>
              </div>
              <div>
                <div class="font-semibold text-gray-900">邮箱</div>
                <div class="text-sm text-gray-600">hello@august.lab</div>
              </div>
            </a>

            <!-- GitHub -->
            <a v-if="profile?.github_url" :href="profile.github_url" target="_blank" class="contact-card">
              <div class="w-12 h-12 bg-gray-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-gray-800" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                </svg>
              </div>
              <div>
                <div class="font-semibold text-gray-900">GitHub</div>
                <div class="text-sm text-gray-600">查看我的代码</div>
              </div>
            </a>

            <!-- LinkedIn -->
            <a v-if="profile?.linkedin_url" :href="profile.linkedin_url" target="_blank" class="contact-card">
              <div class="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-blue-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M20.447 20.452h-3.554v-5.569c0-1.328-.027-3.037-1.852-3.037-1.853 0-2.136 1.445-2.136 2.939v5.667H9.351V9h3.414v1.561h.046c.477-.9 1.637-1.85 3.37-1.85 3.601 0 4.267 2.37 4.267 5.455v6.286zM5.337 7.433c-1.144 0-2.063-.926-2.063-2.065 0-1.138.92-2.063 2.063-2.063 1.14 0 2.064.925 2.064 2.063 0 1.139-.925 2.065-2.064 2.065zm1.782 13.019H3.555V9h3.564v11.452zM22.225 0H1.771C.792 0 0 .774 0 1.729v20.542C0 23.227.792 24 1.771 24h20.451C23.2 24 24 23.227 24 22.271V1.729C24 .774 23.2 0 22.222 0h.003z"/>
                </svg>
              </div>
              <div>
                <div class="font-semibold text-gray-900">LinkedIn</div>
                <div class="text-sm text-gray-600">职业档案</div>
              </div>
            </a>

            <!-- Twitter -->
            <a v-if="profile?.twitter_url" :href="profile.twitter_url" target="_blank" class="contact-card">
              <div class="w-12 h-12 bg-sky-100 rounded-lg flex items-center justify-center">
                <svg class="w-6 h-6 text-sky-600" fill="currentColor" viewBox="0 0 24 24">
                  <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                </svg>
              </div>
              <div>
                <div class="font-semibold text-gray-900">Twitter</div>
                <div class="text-sm text-gray-600">关注动态</div>
              </div>
            </a>
          </div>

          <!-- 联系提示 -->
          <div class="mt-8 p-6 bg-gradient-to-r from-primary-50 to-blue-50 rounded-lg">
            <div class="text-center">
              <h3 class="text-lg font-semibold text-primary-800 mb-2">让我们一起合作</h3>
              <p class="text-primary-700 mb-4">有项目想法？技术问题？或者只是想聊聊技术？随时欢迎与我联系！</p>
              <a href="mailto:hello@august.lab" class="btn-primary">发送邮件</a>
            </div>
          </div>
        </section>
      </ResponsiveContainer>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import ResponsiveContainer from '../../shared/components/ResponsiveContainer.vue'
import { profileAPI } from '../../shared/api'
import type { Profile, Skill } from '../../shared/types'

// 响应式数据
const profile = ref<Profile | null>(null)
const loading = ref(true)
const error = ref<string | null>(null)
const animatedSkills = ref<Record<string, number>>({})

// 计算属性
const skillsByCategory = computed(() => {
  if (!profile.value?.skills) return {}
  
  const categories: Record<string, Skill[]> = {}
  
  profile.value.skills.forEach(skill => {
    if (!categories[skill.category]) {
      categories[skill.category] = []
    }
    categories[skill.category].push(skill)
  })
  
  // 按技能等级排序
  Object.keys(categories).forEach(category => {
    categories[category].sort((a, b) => b.level - a.level)
  })
  
  return categories
})

const renderedBio = computed(() => {
  if (!profile.value?.bio) {
    return `
      <p>我是一名热爱技术的全栈开发者，专注于创造有意义的数字体验。</p>
      <p>致力于用代码构建更美好的世界，让技术服务于人。在工作之余，我也喜欢写博客、参与开源项目，与技术社区保持交流。</p>
    `
  }
  
  return profile.value.bio
    .split('\n')
    .map(paragraph => `<p>${paragraph}</p>`)
    .join('')
})

// 方法
const loadProfile = async () => {
  try {
    loading.value = true
    error.value = null
    const response = await profileAPI.get()
    profile.value = response.data
    
    // 初始化技能动画
    if (profile.value.skills) {
      profile.value.skills.forEach(skill => {
        animatedSkills.value[skill.name] = 0
      })
      
      nextTick(() => {
        setTimeout(() => {
          animateSkills()
        }, 500)
      })
    }
  } catch (err) {
    console.error('加载个人信息失败:', err)
    error.value = '加载个人信息失败，请稍后重试'
  } finally {
    loading.value = false
  }
}

const animateSkills = () => {
  if (!profile.value?.skills) return
  
  profile.value.skills.forEach((skill, index) => {
    setTimeout(() => {
      animatedSkills.value[skill.name] = skill.level
    }, index * 200)
  })
}

const getCategoryDisplayName = (category: string) => {
  const categoryNames: Record<string, string> = {
    'frontend': '前端开发',
    'backend': '后端开发',
    'database': '数据库',
    'devops': '运维部署',
    'tools': '开发工具',
    'design': '设计工具',
    'mobile': '移动开发',
    'other': '其他技能'
  }
  
  return categoryNames[category] || category
}

// 生命周期
onMounted(() => {
  loadProfile()
})
</script>

<style scoped>
.contact-card {
  @apply flex items-center gap-4 p-6 rounded-xl border border-gray-200 hover:border-primary-300 hover:shadow-md transition-all duration-300 cursor-pointer;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}
</style>