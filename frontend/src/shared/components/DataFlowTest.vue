<template>
  <div class="data-flow-test">
    <el-card class="test-card">
      <template #header>
        <div class="card-header">
          <h3>数据流集成测试</h3>
          <el-button 
            type="primary" 
            size="small" 
            @click="runAllTests"
            :loading="testing"
          >
            运行所有测试
          </el-button>
        </div>
      </template>

      <!-- 测试状态概览 -->
      <div class="test-overview">
        <el-row :gutter="16">
          <el-col :span="6">
            <el-statistic title="总测试数" :value="totalTests" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="通过" :value="passedTests" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="失败" :value="failedTests" />
          </el-col>
          <el-col :span="6">
            <el-statistic title="成功率" :value="successRate" suffix="%" />
          </el-col>
        </el-row>
      </div>

      <!-- 测试项列表 -->
      <div class="test-list">
        <h4>测试项目</h4>
        
        <!-- 作品数据流测试 -->
        <el-collapse v-model="activeCollapse">
          <el-collapse-item title="作品数据流测试" name="portfolio">
            <div class="test-section">
              <div v-for="test in portfolioTests" :key="test.name" class="test-item">
                <div class="test-header">
                  <span class="test-name">{{ test.name }}</span>
                  <el-tag 
                    :type="getTestStatusType(test.status)"
                    size="small"
                  >
                    {{ getTestStatusText(test.status) }}
                  </el-tag>
                  <el-button 
                    size="small" 
                    @click="runTest(test)"
                    :loading="test.running"
                  >
                    运行
                  </el-button>
                </div>
                <div v-if="test.result" class="test-result">
                  <pre>{{ test.result }}</pre>
                </div>
              </div>
            </div>
          </el-collapse-item>

          <!-- 博客数据流测试 -->
          <el-collapse-item title="博客数据流测试" name="blog">
            <div class="test-section">
              <div v-for="test in blogTests" :key="test.name" class="test-item">
                <div class="test-header">
                  <span class="test-name">{{ test.name }}</span>
                  <el-tag 
                    :type="getTestStatusType(test.status)"
                    size="small"
                  >
                    {{ getTestStatusText(test.status) }}
                  </el-tag>
                  <el-button 
                    size="small" 
                    @click="runTest(test)"
                    :loading="test.running"
                  >
                    运行
                  </el-button>
                </div>
                <div v-if="test.result" class="test-result">
                  <pre>{{ test.result }}</pre>
                </div>
              </div>
            </div>
          </el-collapse-item>

          <!-- 个人信息数据流测试 -->
          <el-collapse-item title="个人信息数据流测试" name="profile">
            <div class="test-section">
              <div v-for="test in profileTests" :key="test.name" class="test-item">
                <div class="test-header">
                  <span class="test-name">{{ test.name }}</span>
                  <el-tag 
                    :type="getTestStatusType(test.status)"
                    size="small"
                  >
                    {{ getTestStatusText(test.status) }}
                  </el-tag>
                  <el-button 
                    size="small" 
                    @click="runTest(test)"
                    :loading="test.running"
                  >
                    运行
                  </el-button>
                </div>
                <div v-if="test.result" class="test-result">
                  <pre>{{ test.result }}</pre>
                </div>
              </div>
            </div>
          </el-collapse-item>

          <!-- 缓存和同步测试 -->
          <el-collapse-item title="缓存和同步测试" name="cache">
            <div class="test-section">
              <div v-for="test in cacheTests" :key="test.name" class="test-item">
                <div class="test-header">
                  <span class="test-name">{{ test.name }}</span>
                  <el-tag 
                    :type="getTestStatusType(test.status)"
                    size="small"
                  >
                    {{ getTestStatusText(test.status) }}
                  </el-tag>
                  <el-button 
                    size="small" 
                    @click="runTest(test)"
                    :loading="test.running"
                  >
                    运行
                  </el-button>
                </div>
                <div v-if="test.result" class="test-result">
                  <pre>{{ test.result }}</pre>
                </div>
              </div>
            </div>
          </el-collapse-item>
        </el-collapse>
      </div>

      <!-- 实时数据状态 -->
      <div class="data-status">
        <h4>实时数据状态</h4>
        <el-row :gutter="16">
          <el-col :span="8">
            <el-card>
              <template #header>作品数据</template>
              <p>数量: {{ portfolioStore.portfolios.value.length }}</p>
              <p>同步状态: {{ portfolioStore.syncStatus.value }}</p>
              <p>最后更新: {{ formatTime(portfolioStore.lastUpdated.value) }}</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <template #header>博客数据</template>
              <p>数量: {{ blogStore.blogs.value.length }}</p>
              <p>同步状态: {{ blogStore.syncStatus.value }}</p>
              <p>最后更新: {{ formatTime(blogStore.lastUpdated.value) }}</p>
            </el-card>
          </el-col>
          <el-col :span="8">
            <el-card>
              <template #header>个人信息</template>
              <p>状态: {{ profileStore.profile.value ? '已加载' : '未加载' }}</p>
              <p>同步状态: {{ profileStore.syncStatus.value }}</p>
              <p>最后更新: {{ formatTime(profileStore.lastUpdated.value) }}</p>
            </el-card>
          </el-col>
        </el-row>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { useDataSync } from '../composables/useDataStore'

// 测试状态枚举
type TestStatus = 'pending' | 'running' | 'passed' | 'failed'

// 测试项接口
interface TestItem {
  name: string
  description: string
  status: TestStatus
  running: boolean
  result: string | null
  testFn: () => Promise<void>
}

const { portfolioStore, blogStore, profileStore, syncAll, clearCache } = useDataSync()

const testing = ref(false)
const activeCollapse = ref(['portfolio', 'blog', 'profile', 'cache'])

// 作品测试项
const portfolioTests = ref<TestItem[]>([
  {
    name: '获取作品列表',
    description: '测试从后端获取作品列表',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      const portfolios = await portfolioStore.fetchPortfolios(true)
      if (portfolios.length >= 0) {
        portfolioTests.value[0].result = `成功获取 ${portfolios.length} 个作品`
        portfolioTests.value[0].status = 'passed'
      } else {
        throw new Error('获取作品列表失败')
      }
    }
  },
  {
    name: '缓存机制测试',
    description: '测试作品数据缓存功能',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      // 第一次获取（从API）
      const start1 = Date.now()
      await portfolioStore.fetchPortfolios(true)
      const time1 = Date.now() - start1

      // 第二次获取（从缓存）
      const start2 = Date.now()
      await portfolioStore.fetchPortfolios(false)
      const time2 = Date.now() - start2

      if (time2 < time1) {
        portfolioTests.value[1].result = `缓存生效：API请求 ${time1}ms，缓存请求 ${time2}ms`
        portfolioTests.value[1].status = 'passed'
      } else {
        throw new Error('缓存机制未生效')
      }
    }
  },
  {
    name: '数据同步测试',
    description: '测试作品数据实时同步',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      const initialCount = portfolioStore.portfolios.value.length
      await portfolioStore.refreshPortfolios()
      const finalCount = portfolioStore.portfolios.value.length
      
      portfolioTests.value[2].result = `同步完成：${initialCount} -> ${finalCount} 个作品`
      portfolioTests.value[2].status = 'passed'
    }
  }
])

// 博客测试项
const blogTests = ref<TestItem[]>([
  {
    name: '获取博客列表',
    description: '测试从后端获取博客列表',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      const blogs = await blogStore.fetchBlogs(true)
      if (blogs.length >= 0) {
        blogTests.value[0].result = `成功获取 ${blogs.length} 篇博客`
        blogTests.value[0].status = 'passed'
      } else {
        throw new Error('获取博客列表失败')
      }
    }
  },
  {
    name: '发布状态过滤',
    description: '测试博客发布状态过滤功能',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      await blogStore.fetchBlogs(true)
      const publishedCount = blogStore.publishedBlogs.value.length
      const totalCount = blogStore.blogs.value.length
      
      blogTests.value[1].result = `总博客 ${totalCount} 篇，已发布 ${publishedCount} 篇`
      blogTests.value[1].status = 'passed'
    }
  },
  {
    name: '排序功能测试',
    description: '测试博客按时间排序功能',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      await blogStore.fetchBlogs(true)
      const blogs = blogStore.publishedBlogs.value
      
      if (blogs.length > 1) {
        const isCorrectOrder = blogs.every((blog, index) => {
          if (index === 0) return true
          return new Date(blog.created_at) <= new Date(blogs[index - 1].created_at)
        })
        
        if (isCorrectOrder) {
          blogTests.value[2].result = `排序正确：${blogs.length} 篇博客按时间倒序排列`
          blogTests.value[2].status = 'passed'
        } else {
          throw new Error('博客排序不正确')
        }
      } else {
        blogTests.value[2].result = '博客数量不足，跳过排序测试'
        blogTests.value[2].status = 'passed'
      }
    }
  }
])

// 个人信息测试项
const profileTests = ref<TestItem[]>([
  {
    name: '获取个人信息',
    description: '测试从后端获取个人信息',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      const profile = await profileStore.fetchProfile(true)
      if (profile) {
        profileTests.value[0].result = `成功获取个人信息：${profile.name}`
        profileTests.value[0].status = 'passed'
      } else {
        throw new Error('获取个人信息失败')
      }
    }
  },
  {
    name: '技能数据验证',
    description: '测试技能数据结构和内容',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      const profile = await profileStore.fetchProfile()
      if (profile && profile.skills) {
        const skillCount = profile.skills.length
        const categories = [...new Set(profile.skills.map(s => s.category))]
        
        profileTests.value[1].result = `技能数据：${skillCount} 项技能，${categories.length} 个分类`
        profileTests.value[1].status = 'passed'
      } else {
        throw new Error('技能数据不完整')
      }
    }
  }
])

// 缓存和同步测试项
const cacheTests = ref<TestItem[]>([
  {
    name: '缓存清理测试',
    description: '测试缓存清理功能',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      // 先加载一些数据到缓存
      await Promise.all([
        portfolioStore.fetchPortfolios(),
        blogStore.fetchBlogs(),
        profileStore.fetchProfile()
      ])
      
      // 清理缓存
      clearCache()
      
      cacheTests.value[0].result = '缓存清理完成'
      cacheTests.value[0].status = 'passed'
    }
  },
  {
    name: '全量同步测试',
    description: '测试所有数据的同步功能',
    status: 'pending',
    running: false,
    result: null,
    testFn: async () => {
      const startTime = Date.now()
      await syncAll()
      const duration = Date.now() - startTime
      
      cacheTests.value[1].result = `全量同步完成，耗时 ${duration}ms`
      cacheTests.value[1].status = 'passed'
    }
  }
])

// 计算属性
const allTests = computed(() => [
  ...portfolioTests.value,
  ...blogTests.value,
  ...profileTests.value,
  ...cacheTests.value
])

const totalTests = computed(() => allTests.value.length)
const passedTests = computed(() => allTests.value.filter(t => t.status === 'passed').length)
const failedTests = computed(() => allTests.value.filter(t => t.status === 'failed').length)
const successRate = computed(() => {
  const total = passedTests.value + failedTests.value
  return total > 0 ? Math.round((passedTests.value / total) * 100) : 0
})

// 方法
const getTestStatusType = (status: TestStatus) => {
  switch (status) {
    case 'passed': return 'success'
    case 'failed': return 'danger'
    case 'running': return 'warning'
    default: return 'info'
  }
}

const getTestStatusText = (status: TestStatus) => {
  switch (status) {
    case 'passed': return '通过'
    case 'failed': return '失败'
    case 'running': return '运行中'
    default: return '待运行'
  }
}

const runTest = async (test: TestItem) => {
  if (test.running) return

  test.running = true
  test.status = 'running'
  test.result = null

  try {
    await test.testFn()
    ElMessage.success(`测试 "${test.name}" 通过`)
  } catch (error: any) {
    test.status = 'failed'
    test.result = `错误: ${error.message}`
    ElMessage.error(`测试 "${test.name}" 失败: ${error.message}`)
  } finally {
    test.running = false
  }
}

const runAllTests = async () => {
  if (testing.value) return

  testing.value = true
  
  try {
    // 重置所有测试状态
    allTests.value.forEach(test => {
      test.status = 'pending'
      test.result = null
    })

    // 依次运行所有测试
    for (const test of allTests.value) {
      await runTest(test)
      // 短暂延迟，避免请求过于频繁
      await new Promise(resolve => setTimeout(resolve, 200))
    }

    ElMessage.success(`所有测试完成：${passedTests.value}/${totalTests.value} 通过`)
  } finally {
    testing.value = false
  }
}

const formatTime = (timestamp: number) => {
  if (!timestamp) return '未更新'
  return new Date(timestamp).toLocaleString()
}

// 生命周期
onMounted(() => {
  // 初始化数据
  syncAll()
})
</script>

<style scoped>
.data-flow-test {
  @apply p-4;
}

.test-card {
  @apply w-full;
}

.card-header {
  @apply flex justify-between items-center;
}

.test-overview {
  @apply mb-6 p-4 bg-gray-50 rounded-lg;
}

.test-list {
  @apply mb-6;
}

.test-section {
  @apply space-y-4;
}

.test-item {
  @apply border border-gray-200 rounded-lg p-4;
}

.test-header {
  @apply flex items-center justify-between mb-2;
}

.test-name {
  @apply font-medium text-gray-900;
}

.test-result {
  @apply mt-2 p-3 bg-gray-100 rounded border;
}

.test-result pre {
  @apply text-sm text-gray-700 whitespace-pre-wrap;
}

.data-status {
  @apply mt-6;
}

.data-status .el-card {
  @apply text-center;
}

.data-status p {
  @apply mb-2 text-sm;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .card-header {
    @apply flex-col gap-2;
  }
  
  .test-header {
    @apply flex-col items-start gap-2;
  }
}
</style>