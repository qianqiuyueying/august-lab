<template>
  <div class="min-h-screen">
    <!-- 主视觉区域 -->
    <section class="hero-responsive bg-gradient-to-br from-primary-50 via-blue-50 to-indigo-50 relative overflow-hidden">
      <!-- 背景装饰 -->
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-10 left-10 w-20 h-20 bg-primary-400 rounded-full blur-xl"></div>
        <div class="absolute top-32 right-20 w-32 h-32 bg-blue-400 rounded-full blur-xl"></div>
        <div class="absolute bottom-20 left-1/4 w-24 h-24 bg-indigo-400 rounded-full blur-xl"></div>
      </div>
      
      <ResponsiveContainer size="xl" class="relative z-10">
        <div class="hero-content">
          <div class="fade-in">
            <h1 class="heading-1 mb-6">
              Hello, I'm <span class="text-primary-600 bg-gradient-to-r from-primary-600 to-blue-600 bg-clip-text text-transparent">August</span>
            </h1>
            <p class="text-responsive-lg text-gray-600 mb-8 max-w-3xl mx-auto lg:mx-0 leading-relaxed">
              一名热爱技术的全栈开发者，专注于创造有意义的数字体验。
              <br class="hidden sm:block">
              致力于用代码构建更美好的世界，让技术服务于人。
            </p>
            <div class="flex-responsive gap-responsive justify-center lg:justify-start">
              <router-link to="/portfolio" class="btn-primary btn-responsive-lg group">
                <span>查看作品</span>
                <svg class="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform duration-200" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </router-link>
              <router-link to="/about" class="btn-outline btn-responsive-lg">
                了解更多
              </router-link>
            </div>
          </div>
        </div>
      </ResponsiveContainer>
    </section>
    
    <!-- 最新作品预览 -->
    <section class="section-padding bg-white">
      <ResponsiveContainer size="xl">
        <div class="text-center mb-12">
          <h2 class="heading-2 mb-4">最新作品</h2>
          <p class="text-responsive-base text-gray-600 max-w-2xl mx-auto">
            展示我最近完成的一些项目，涵盖前端开发、全栈应用和创新实验
          </p>
        </div>
        
        <ErrorBoundary 
          :on-retry="loadPortfolios"
          fallback-title="作品加载失败"
          fallback-message="无法加载作品信息，请检查网络连接后重试"
        >
          <!-- 加载状态 -->
          <SkeletonLoader 
            v-if="portfolioLoading" 
            type="card" 
            :count="3" 
            :show-image="true" 
            :show-actions="false"
            :text-lines="2"
          />
          
          <!-- 作品网格 -->
          <div v-else-if="featuredPortfolios.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 mb-16">
          <div 
            v-for="portfolio in featuredPortfolios" 
            :key="portfolio.id" 
            class="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer transform hover:-translate-y-2"
            @click="goToPortfolioDetail(portfolio.id)"
          >
            <!-- 项目图片 -->
            <div class="relative overflow-hidden bg-gray-100 aspect-video">
              <ResponsiveImage
                v-if="portfolio.image_url"
                :src="portfolio.image_url"
                :alt="portfolio.title"
                aspect-ratio="video"
                class="group-hover:scale-105 transition-transform duration-300"
              />
              <div v-else class="w-full h-48 bg-gradient-to-br from-gray-200 to-gray-300 flex items-center justify-center">
                <svg class="w-12 h-12 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                </svg>
              </div>
              
              <!-- 悬停遮罩 -->
              <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-20 transition-all duration-300 flex items-center justify-center">
                <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                  <div class="bg-white rounded-full p-3 shadow-lg">
                    <svg class="w-6 h-6 text-primary-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                  </div>
                </div>
              </div>
            </div>
            
            <!-- 项目信息 -->
            <div class="p-6 space-y-4">
              <h3 class="heading-5 group-hover:text-primary-600 transition-colors duration-200">
                {{ portfolio.title }}
              </h3>
              <p class="text-gray-600 text-sm leading-relaxed line-clamp-2">
                {{ portfolio.description || '暂无描述' }}
              </p>
              
              <!-- 技术栈标签 -->
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="tech in portfolio.tech_stack.slice(0, 3)" 
                  :key="tech"
                  class="tag tag-primary text-xs"
                >
                  {{ tech }}
                </span>
                <span 
                  v-if="portfolio.tech_stack.length > 3"
                  class="tag tag-secondary text-xs"
                >
                  +{{ portfolio.tech_stack.length - 3 }}
                </span>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="empty-responsive">
          <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
          </svg>
          <h3 class="heading-5 text-gray-500 mb-2">暂无作品</h3>
          <p class="text-gray-400">作品正在准备中，敬请期待</p>
        </div>
        
          <!-- 查看更多按钮 -->
          <div v-if="featuredPortfolios.length > 0" class="text-center">
            <router-link 
              to="/portfolio" 
              class="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              查看所有作品
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 最新产品预览 -->
    <section class="section-padding bg-gradient-to-br from-indigo-50 via-purple-50 to-pink-50">
      <ResponsiveContainer size="xl">
        <div class="text-center mb-12">
          <h2 class="heading-2 mb-4">我的产品</h2>
          <p class="text-responsive-base text-gray-600 max-w-2xl mx-auto">
            体验我开发的Web应用和工具，点击即可在线使用
          </p>
        </div>
        
        <ErrorBoundary 
          :on-retry="loadProducts"
          fallback-title="产品加载失败"
          fallback-message="无法加载产品信息，请检查网络连接后重试"
        >
          <!-- 加载状态 -->
          <SkeletonLoader 
            v-if="productLoading" 
            type="card" 
            :count="3" 
            :show-image="true" 
            :show-actions="true"
            :text-lines="2"
          />
          
          <!-- 产品网格 -->
          <div v-else-if="featuredProducts.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 mb-16">
            <div 
              v-for="product in featuredProducts" 
              :key="product.id" 
              class="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer transform hover:-translate-y-2"
              @click="launchProduct(product)"
            >
              <!-- 产品预览图 -->
              <div class="relative overflow-hidden bg-gradient-to-br from-indigo-100 to-purple-100 aspect-video">
                <ResponsiveImage
                  v-if="product.preview_image"
                  :src="product.preview_image"
                  :alt="product.title"
                  aspect-ratio="video"
                  class="group-hover:scale-105 transition-transform duration-300"
                />
                <div v-else class="w-full h-48 bg-gradient-to-br from-indigo-200 to-purple-200 flex items-center justify-center">
                  <div class="text-6xl opacity-60">
                    {{ getProductIcon(product.product_type) }}
                  </div>
                </div>
                
                <!-- 产品类型标签 -->
                <div class="absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-medium text-white" :class="getProductTypeClass(product.product_type)">
                  {{ getProductTypeLabel(product.product_type) }}
                </div>
                
                <!-- 启动按钮遮罩 -->
                <div class="absolute inset-0 bg-black bg-opacity-0 group-hover:bg-opacity-40 transition-all duration-300 flex items-center justify-center">
                  <div class="opacity-0 group-hover:opacity-100 transition-opacity duration-300">
                    <div class="bg-white rounded-full p-4 shadow-lg transform scale-90 group-hover:scale-100 transition-transform duration-300">
                      <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-6V7a2 2 0 00-2-2H5a2 2 0 00-2 2v3m2 13h10a2 2 0 002-2v-3m-2-13h10a2 2 0 012 2v3" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 产品信息 -->
              <div class="p-6 space-y-4">
                <h3 class="heading-5 group-hover:text-indigo-600 transition-colors duration-200">
                  {{ product.title }}
                </h3>
                <p class="text-gray-600 text-sm leading-relaxed line-clamp-2">
                  {{ product.description || '暂无描述' }}
                </p>
                
                <!-- 技术栈标签 -->
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="tech in product.tech_stack?.slice(0, 3)" 
                    :key="tech"
                    class="tag tag-indigo text-xs"
                  >
                    {{ tech }}
                  </span>
                  <span 
                    v-if="product.tech_stack && product.tech_stack.length > 3"
                    class="tag tag-secondary text-xs"
                  >
                    +{{ product.tech_stack.length - 3 }}
                  </span>
                </div>
                
                <!-- 产品统计 -->
                <div class="flex items-center justify-between text-xs text-gray-500">
                  <div class="flex items-center gap-1">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {{ product.view_count || 0 }} 次体验
                  </div>
                  <div class="bg-indigo-100 text-indigo-700 px-2 py-1 rounded-full font-medium">
                    立即体验
                  </div>
                </div>
              </div>
            </div>
          </div>
          
          <!-- 空状态 -->
          <div v-else class="empty-responsive">
            <div class="text-6xl mb-4">🚀</div>
            <h3 class="heading-5 text-gray-500 mb-2">产品即将上线</h3>
            <p class="text-gray-400">精彩的产品正在开发中，敬请期待</p>
          </div>
          
          <!-- 查看更多按钮 -->
          <div v-if="featuredProducts.length > 0" class="text-center">
            <router-link 
              to="/products" 
              class="inline-flex items-center px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              查看所有产品
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 最新博客预览 -->
    <section class="section-padding bg-gray-50">
      <ResponsiveContainer size="xl">
        <div class="text-center mb-12">
          <h2 class="heading-2 mb-4">最新博客</h2>
          <p class="text-responsive-base text-gray-600 max-w-2xl mx-auto">
            分享技术心得、开发经验和生活感悟
          </p>
        </div>
        
        <ErrorBoundary 
          :on-retry="loadBlogs"
          fallback-title="博客加载失败"
          fallback-message="无法加载博客信息，请检查网络连接后重试"
        >
          <!-- 加载状态 -->
          <SkeletonLoader 
            v-if="blogLoading" 
            type="list" 
            :count="3" 
            :show-avatar="false" 
            :show-meta="true"
            :text-lines="2"
          />
        
        <!-- 博客网格 -->
        <div v-else-if="recentBlogs.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-8 mb-16">
          <article 
            v-for="blog in recentBlogs" 
            :key="blog.id"
            class="bg-white rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer transform hover:-translate-y-2"
            @click="goToBlogDetail(blog.id)"
          >
            <!-- 封面图片 -->
            <div v-if="blog.cover_image" class="relative overflow-hidden aspect-video">
              <ResponsiveImage
                :src="blog.cover_image"
                :alt="blog.title"
                aspect-ratio="video"
                class="group-hover:scale-105 transition-transform duration-300"
              />
            </div>
            
            <!-- 博客信息 -->
            <div class="p-6 space-y-4">
              <!-- 发布时间 -->
              <div class="flex items-center text-sm text-gray-500">
                <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                </svg>
                {{ formatDate(blog.created_at) }}
              </div>
              
              <!-- 标题 -->
              <h3 class="heading-5 group-hover:text-primary-600 transition-colors duration-200 line-clamp-2">
                {{ blog.title }}
              </h3>
              
              <!-- 摘要 -->
              <p class="text-gray-600 text-sm leading-relaxed line-clamp-3">
                {{ blog.summary || extractSummary(blog.content) }}
              </p>
              
              <!-- 标签 -->
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="tag in blog.tags.slice(0, 3)" 
                  :key="tag"
                  class="tag tag-secondary text-xs"
                >
                  {{ tag }}
                </span>
                <span 
                  v-if="blog.tags.length > 3"
                  class="tag tag-secondary text-xs"
                >
                  +{{ blog.tags.length - 3 }}
                </span>
              </div>
            </div>
          </article>
        </div>
        
        <!-- 空状态 -->
        <div v-else class="empty-responsive">
          <svg class="w-16 h-16 text-gray-300 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.746 0 3.332.477 4.5 1.253v13C19.832 18.477 18.246 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
          </svg>
          <h3 class="heading-5 text-gray-500 mb-2">暂无博客</h3>
          <p class="text-gray-400">博客内容正在准备中，敬请期待</p>
        </div>
        
          <!-- 查看更多按钮 -->
          <div v-if="recentBlogs.length > 0" class="text-center">
            <router-link 
              to="/blog" 
              class="inline-flex items-center px-6 py-3 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors duration-200"
            >
              查看所有博客
              <svg class="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 联系我区域 -->
    <section class="section-padding bg-gradient-to-r from-primary-600 to-blue-600 text-white">
      <ResponsiveContainer size="lg">
        <div class="text-center">
          <h2 class="heading-2 mb-4 text-white">让我们一起创造</h2>
          <p class="text-responsive-lg mb-8 opacity-90 max-w-2xl mx-auto">
            有想法？有项目？或者只是想聊聊技术？
            <br class="hidden sm:block">
            随时欢迎与我联系，让我们一起把想法变成现实。
          </p>
          <div class="flex-responsive gap-responsive justify-center">
            <router-link to="/about" class="bg-white text-primary-600 hover:bg-gray-100 btn-responsive-lg font-semibold transition-colors duration-200">
              联系我
            </router-link>
            <a 
              href="mailto:hello@august.lab" 
              class="border-2 border-white text-white hover:bg-white hover:text-primary-600 btn-responsive-lg font-semibold transition-colors duration-200"
            >
              发送邮件
            </a>
          </div>
        </div>
      </ResponsiveContainer>
    </section>
  </div>
</template>

<script setup lang="ts">
import { onMounted, computed, ref } from 'vue'
import { useRouter } from 'vue-router'
import ResponsiveContainer from '../../shared/components/ResponsiveContainer.vue'
import ResponsiveImage from '../../shared/components/ResponsiveImage.vue'
import SkeletonLoader from '../../shared/components/SkeletonLoader.vue'
import ErrorBoundary from '../../shared/components/ErrorBoundary.vue'
import { useDataSync } from '../../shared/composables/useDataStore'
import { useProductStore } from '../composables/useProductStore'
import type { Product } from '../../shared/types'

const router = useRouter()

// 数据存储
const { portfolioStore, blogStore, startAutoSync, stopAutoSync } = useDataSync()
const { fetchProducts } = useProductStore()

// 产品数据
const products = ref<Product[]>([])
const productLoading = ref(false)

// 计算属性
const featuredPortfolios = computed(() => {
  return portfolioStore.featuredPortfolios.value.slice(0, 3)
})

const recentBlogs = computed(() => {
  return blogStore.recentBlogs.value.slice(0, 3)
})

const featuredProducts = computed(() => {
  return products.value.filter(product => product.is_published).slice(0, 3)
})

// 加载状态
const portfolioLoading = computed(() => portfolioStore.loading.value)
const blogLoading = computed(() => blogStore.loading.value)

// 方法
const loadPortfolios = async () => {
  await portfolioStore.fetchPortfolios()
}

const loadBlogs = async () => {
  await blogStore.fetchBlogs()
}

const loadProducts = async () => {
  productLoading.value = true
  try {
    products.value = await fetchProducts()
  } catch (error) {
    console.error('加载产品失败:', error)
  } finally {
    productLoading.value = false
  }
}

const goToPortfolioDetail = (id: number) => {
  router.push(`/portfolio/${id}`)
}

const goToBlogDetail = (id: number) => {
  router.push(`/blog/${id}`)
}

const launchProduct = (product: Product) => {
  router.push(`/product/${product.id}`)
}

const getProductIcon = (type: string) => {
  const icons = {
    web_app: '🌐',
    game: '🎮',
    tool: '🔧',
    demo: '🎯'
  }
  return icons[type as keyof typeof icons] || '📦'
}

const getProductTypeLabel = (type: string) => {
  const labels = {
    web_app: 'Web应用',
    game: '游戏',
    tool: '工具',
    demo: '演示'
  }
  return labels[type as keyof typeof labels] || type
}

const getProductTypeClass = (type: string) => {
  const classes = {
    web_app: 'bg-blue-500',
    game: 'bg-red-500',
    tool: 'bg-green-500',
    demo: 'bg-yellow-500'
  }
  return classes[type as keyof typeof classes] || 'bg-gray-500'
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
}

const extractSummary = (content: string, maxLength: number = 150) => {
  // 移除Markdown标记和HTML标签
  const plainText = content
    .replace(/[#*`_~\[\]()]/g, '')
    .replace(/<[^>]*>/g, '')
    .trim()
  
  if (plainText.length <= maxLength) {
    return plainText
  }
  
  return plainText.substring(0, maxLength) + '...'
}

// 生命周期
onMounted(async () => {
  // 启动自动同步
  startAutoSync()
  
  // 初始加载数据
  await Promise.all([
    loadPortfolios(),
    loadBlogs(),
    loadProducts()
  ])
})

// 组件卸载时停止自动同步
import { onUnmounted } from 'vue'
onUnmounted(() => {
  stopAutoSync()
})
</script>

<style scoped>
/* 自定义样式 */
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 渐变文字效果 */
.bg-clip-text {
  -webkit-background-clip: text;
  background-clip: text;
}

/* 按钮悬停效果 */
.btn-primary:hover svg {
  transform: translateX(4px);
}

/* 产品标签样式 */
.tag-indigo {
  background: #e0e7ff;
  color: #3730a3;
}

/* 卡片悬停效果增强 */
.card-responsive-hover:hover {
  transform: translateY(-4px);
}

/* 动画效果 */
@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translateY(30px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

.fade-in {
  animation: fadeInUp 0.8s ease-out;
}

/* 响应式调整 */
@media (max-width: 768px) {
  .hero-content {
    text-align: center;
  }
}

/* 加载动画 */
@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* 背景装饰动画 */
@keyframes float {
  0%, 100% {
    transform: translateY(0px);
  }
  50% {
    transform: translateY(-20px);
  }
}

.hero-responsive .absolute {
  animation: float 6s ease-in-out infinite;
}

.hero-responsive .absolute:nth-child(2) {
  animation-delay: -2s;
}

.hero-responsive .absolute:nth-child(3) {
  animation-delay: -4s;
}
</style>