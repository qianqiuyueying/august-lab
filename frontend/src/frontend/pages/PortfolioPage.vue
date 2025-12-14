<template>
  <div class="min-h-screen bg-gradient-to-b from-slate-900 via-purple-900 to-slate-900">
    <!-- 页面头部 - 画廊风格 -->
    <section class="relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
        <div class="absolute inset-0 opacity-30">
          <div class="absolute top-0 right-0 w-96 h-96 bg-purple-500 rounded-full blur-3xl"></div>
          <div class="absolute bottom-0 left-0 w-96 h-96 bg-pink-500 rounded-full blur-3xl"></div>
        </div>
      </div>
      
      <ResponsiveContainer size="xl" class="relative z-10 py-20">
        <div class="text-center">
          <div class="inline-block mb-4">
            <span class="text-sm font-bold text-pink-400 uppercase tracking-wider">Portfolio</span>
          </div>
          <h1 class="text-6xl md:text-7xl font-black text-white mb-6 leading-tight">
            {{ currentTab === 'portfolio' ? '我的' : '在线' }}<span class="bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">{{ currentTab === 'portfolio' ? '作品' : '产品' }}</span>
          </h1>
          <p class="text-xl text-white/80 max-w-3xl mx-auto mb-8">
            {{ currentTab === 'portfolio' 
              ? '这里展示了我在不同技术领域的项目作品，从前端应用到全栈系统，每个项目都承载着我对技术的热情和对用户体验的追求。'
              : '体验我开发的各种Web应用和工具，这些产品可以直接在线使用，展现了从想法到实现的完整过程。'
            }}
          </p>
          
          <!-- 标签切换 - 玻璃态设计 -->
          <div class="flex justify-center">
            <div class="bg-white/10 backdrop-blur-xl p-1 rounded-xl border border-white/20">
              <button
                @click="currentTab = 'portfolio'"
                :class="[
                  'px-8 py-3 rounded-lg font-bold transition-all duration-300',
                  currentTab === 'portfolio'
                    ? 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-lg'
                    : 'text-white/70 hover:text-white'
                ]"
              >
                作品展示
              </button>
              <button
                @click="currentTab = 'products'"
                :class="[
                  'px-8 py-3 rounded-lg font-bold transition-all duration-300',
                  currentTab === 'products'
                    ? 'bg-gradient-to-r from-pink-600 to-purple-600 text-white shadow-lg'
                    : 'text-white/70 hover:text-white'
                ]"
              >
                在线产品
              </button>
            </div>
          </div>
        </div>
      </ResponsiveContainer>
    </section>

    <!-- 内容展示区域 -->
    <section class="py-12">
      <ResponsiveContainer size="xl">
        <!-- 作品展示 -->
        <div v-if="currentTab === 'portfolio'">
          <!-- 排序和筛选控制 -->
          <div v-if="!portfolioLoading && !portfolioError && portfolios.length > 0" class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
          <div class="flex items-center gap-4">
            <label class="text-sm font-medium text-gray-700">排序方式:</label>
            <select 
              v-model="sortBy" 
              @change="sortPortfolios"
              class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
            >
              <option value="display_order">推荐顺序</option>
              <option value="created_at">创建时间</option>
              <option value="title">项目名称</option>
              <option value="featured">精选优先</option>
            </select>
            <button 
              @click="toggleSortOrder"
              class="p-2 text-gray-500 hover:text-gray-700 transition-colors"
              :title="sortOrder === 'desc' ? '降序' : '升序'"
            >
              <svg 
                class="w-4 h-4 transition-transform duration-200" 
                :class="{ 'rotate-180': sortOrder === 'asc' }"
                fill="none" 
                stroke="currentColor" 
                viewBox="0 0 24 24"
              >
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
              </svg>
            </button>
          </div>
          
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500">共 {{ portfolios.length }} 个作品</span>
              <button 
                v-if="hasFilteredResults"
                @click="clearFilters"
                class="text-sm text-primary-600 hover:text-primary-700"
              >
                清除筛选
              </button>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="portfolioLoading" class="loading-responsive text-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500 mx-auto"></div>
            <p class="text-white/60 mt-4">加载作品中...</p>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="portfolioError" class="error-responsive text-center py-20">
            <svg class="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 class="text-2xl font-bold text-red-400 mb-2">加载失败</h3>
            <p class="text-red-300 mb-4">{{ portfolioError }}</p>
            <button @click="loadPortfolios" class="px-6 py-3 bg-gradient-to-r from-pink-600 to-purple-600 text-white font-bold rounded-xl hover:shadow-lg transition-all">
              重试
            </button>
          </div>

          <!-- 作品网格 - 画廊风格 -->
          <ResponsiveGrid v-else-if="sortedPortfolios.length > 0" preset="portfolio">
          <div 
            v-for="(portfolio, index) in sortedPortfolios" 
            :key="portfolio.id"
            class="card-responsive-hover group cursor-pointer h-full rounded-2xl overflow-hidden shadow-2xl transition-all duration-500 transform hover:-translate-y-2 hover:scale-[1.02] flex flex-col p-0"
            :style="{ animationDelay: `${index * 50}ms` }"
            @click="goToDetail(portfolio.id)"
          >
              <!-- 项目图片 -->
              <div class="relative overflow-hidden bg-gradient-to-br from-pink-500/20 to-purple-500/20 aspect-video flex-shrink-0">
                <ResponsiveImage
                  v-if="portfolio.image_url"
                  :src="portfolio.image_url"
                  :alt="portfolio.title"
                  aspect-ratio="video"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                  loading="lazy"
                  @load="onImageLoad(portfolio.id)"
                  @error="onImageError(portfolio.id)"
                />
                <div v-else class="w-full h-full bg-gradient-to-br from-pink-500/30 to-purple-500/30 flex items-center justify-center">
                  <svg class="w-16 h-16 text-white/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                
                <!-- 图片加载状态 -->
                <div 
                  v-if="imageLoadingStates[portfolio.id]" 
                  class="absolute inset-0 bg-slate-900/50 backdrop-blur-sm flex items-center justify-center"
                >
                  <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-pink-500"></div>
                </div>
                
                <!-- 特色标识 -->
                <div v-if="portfolio.is_featured" class="absolute top-4 right-4">
                  <div class="bg-gradient-to-r from-pink-500 to-purple-500 text-white px-3 py-1 rounded-full text-xs font-bold shadow-lg">
                    精选
                  </div>
                </div>
                
                <!-- 悬停遮罩 -->
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-center justify-center">
                  <div class="transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                    <div class="bg-white rounded-full p-4 shadow-2xl transform scale-90 group-hover:scale-100 transition-transform duration-300">
                      <svg class="w-6 h-6 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 项目信息 -->
              <div class="flex-1 flex flex-col p-6 space-y-4 bg-slate-800/80 backdrop-blur-xl">
                <h3 class="text-xl font-bold text-white group-hover:text-pink-300 transition-colors duration-300">
                  {{ portfolio.title }}
                </h3>
                <p class="text-white/80 text-sm leading-relaxed line-clamp-3 flex-1">
                  {{ portfolio.description || '暂无描述' }}
                </p>
                
                <!-- 技术栈标签 -->
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="tech in portfolio.tech_stack" 
                    :key="tech"
                    class="px-3 py-1.5 bg-pink-500/20 backdrop-blur-sm text-pink-200 text-xs font-medium rounded-full border border-pink-400/30 hover:bg-pink-500/30 transition-colors"
                  >
                    {{ tech }}
                  </span>
                </div>
                
                <!-- 项目链接 -->
                <div class="flex items-center gap-4 pt-3 border-t border-white/20 mt-auto">
                  <a 
                    v-if="portfolio.project_url"
                    :href="portfolio.project_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-pink-300 hover:text-pink-200 text-sm font-semibold flex items-center group/link transition-all duration-300"
                    @click.stop
                  >
                    <svg class="w-4 h-4 mr-1.5 group-hover/link:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
                    </svg>
                    预览
                  </a>
                  <a 
                    v-if="portfolio.github_url"
                    :href="portfolio.github_url"
                    target="_blank"
                    rel="noopener noreferrer"
                    class="text-white/70 hover:text-white text-sm font-semibold flex items-center group/link transition-all duration-300"
                    @click.stop
                  >
                    <svg class="w-4 h-4 mr-1.5 group-hover/link:translate-x-1 transition-transform" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                    代码
                  </a>
                </div>
              </div>
          </div>
          </ResponsiveGrid>

          <!-- 空状态 -->
          <div v-else class="empty-responsive text-center py-20">
            <svg class="w-16 h-16 text-white/30 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            <h3 class="text-2xl font-bold text-white/60 mb-2">暂无作品</h3>
            <p class="text-white/40">作品正在准备中，敬请期待</p>
          </div>
        </div>

        <!-- 产品展示 -->
        <div v-else-if="currentTab === 'products'">
          <!-- 产品筛选控制 -->
          <div v-if="!productLoading && !productError && products.length > 0" class="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-8">
            <div class="flex items-center gap-4">
              <label class="text-sm font-medium text-gray-700">产品类型:</label>
              <select 
                v-model="selectedProductType" 
                @change="filterProducts"
                class="px-3 py-2 border border-gray-300 rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
              >
                <option value="">全部类型</option>
                <option value="web_app">Web应用</option>
                <option value="game">游戏</option>
                <option value="tool">工具</option>
                <option value="demo">演示</option>
              </select>
            </div>
            
            <div class="flex items-center gap-2">
              <span class="text-sm text-gray-500">共 {{ filteredProducts.length }} 个产品</span>
              <button 
                v-if="selectedProductType"
                @click="clearProductFilters"
                class="text-sm text-primary-600 hover:text-primary-700"
              >
                清除筛选
              </button>
            </div>
          </div>

          <!-- 加载状态 -->
          <div v-if="productLoading" class="loading-responsive text-center py-20">
            <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-pink-500 mx-auto"></div>
            <p class="text-white/60 mt-4">加载产品中...</p>
          </div>

          <!-- 错误状态 -->
          <div v-else-if="productError" class="error-responsive text-center py-20">
            <svg class="w-16 h-16 text-red-400 mx-auto mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <h3 class="text-2xl font-bold text-red-400 mb-2">加载失败</h3>
            <p class="text-red-300 mb-4">{{ productError }}</p>
            <button @click="loadProducts" class="px-6 py-3 bg-gradient-to-r from-pink-600 to-purple-600 text-white font-bold rounded-xl hover:shadow-lg transition-all">
              重试
            </button>
          </div>

          <!-- 产品网格 -->
          <ResponsiveGrid v-else-if="filteredProducts.length > 0" preset="portfolio">
            <div 
              v-for="(product, index) in filteredProducts" 
              :key="product.id"
              class="card-responsive-hover group cursor-pointer h-full rounded-2xl overflow-hidden shadow-2xl transition-all duration-500 transform hover:-translate-y-2 hover:scale-[1.02] flex flex-col p-0"
              :style="{ animationDelay: `${index * 50}ms` }"
              @click="launchProduct(product)"
            >
                <!-- 产品预览图 -->
                <div class="relative overflow-hidden bg-gradient-to-br from-pink-500/20 to-purple-500/20 aspect-video flex-shrink-0">
                  <ResponsiveImage
                    v-if="product.preview_image"
                    :src="product.preview_image"
                    :alt="product.title"
                    aspect-ratio="video"
                    class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                    loading="lazy"
                  />
                  <div v-else class="w-full h-full bg-gradient-to-br from-pink-500/30 to-purple-500/30 flex items-center justify-center">
                    <div class="text-6xl opacity-80">
                      {{ getProductIcon(product.product_type) }}
                    </div>
                  </div>
                  
                  <!-- 产品类型标签 -->
                  <div class="absolute top-4 right-4 px-4 py-1.5 rounded-full text-xs font-bold text-white backdrop-blur-md bg-black/30 border border-white/20">
                    {{ getProductTypeLabel(product.product_type) }}
                  </div>
                  
                  <!-- 启动按钮遮罩 -->
                  <div class="absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-center justify-center">
                    <div class="transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                      <div class="bg-white rounded-full p-5 shadow-2xl transform scale-90 group-hover:scale-100 transition-transform duration-300">
                        <svg class="w-8 h-8 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-6V7a2 2 0 00-2-2H5a2 2 0 00-2 2v3m2 13h10a2 2 0 002-2v-3m-2-13h10a2 2 0 012 2v3" />
                        </svg>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- 产品信息 -->
                <div class="flex-1 flex flex-col p-6 space-y-4 bg-slate-800/80 backdrop-blur-xl">
                  <h3 class="text-xl font-bold text-white group-hover:text-pink-300 transition-colors duration-300">
                    {{ product.title }}
                  </h3>
                  <p class="text-white/80 text-sm leading-relaxed line-clamp-3 flex-1">
                    {{ product.description || '暂无描述' }}
                  </p>
                  
                  <!-- 技术栈标签 -->
                  <div class="flex flex-wrap gap-2">
                    <span 
                      v-for="tech in product.tech_stack?.slice(0, 3)" 
                      :key="tech"
                      class="px-3 py-1.5 bg-pink-500/20 backdrop-blur-sm text-pink-200 text-xs font-medium rounded-full border border-pink-400/30 hover:bg-pink-500/30 transition-colors"
                    >
                      {{ tech }}
                    </span>
                    <span 
                      v-if="product.tech_stack && product.tech_stack.length > 3"
                      class="px-3 py-1.5 bg-white/10 text-white/60 text-xs font-medium rounded-full"
                    >
                      +{{ product.tech_stack.length - 3 }}
                    </span>
                  </div>
                  
                  <!-- 产品操作 -->
                  <div class="flex items-center justify-between pt-3 border-t border-white/20 mt-auto">
                    <div class="flex items-center gap-1.5 text-xs text-white/70 font-medium">
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                      {{ product.view_count || 0 }} 次体验
                    </div>
                    <div class="px-4 py-1.5 bg-gradient-to-r from-pink-500 to-purple-500 text-white rounded-full font-bold text-xs shadow-lg">
                      立即体验
                    </div>
                  </div>
                </div>
            </div>
          </ResponsiveGrid>

          <!-- 产品空状态 -->
          <div v-else class="empty-responsive text-center py-20">
            <div class="text-6xl mb-4">🚀</div>
            <h3 class="text-2xl font-bold text-white/60 mb-2">{{ selectedProductType ? '暂无此类型产品' : '产品即将上线' }}</h3>
            <p class="text-white/40">{{ selectedProductType ? '尝试选择其他产品类型' : '精彩的产品正在开发中，敬请期待' }}</p>
          </div>
        </div>
      </ResponsiveContainer>
    </section>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import ResponsiveContainer from '../../shared/components/ResponsiveContainer.vue'
import ResponsiveGrid from '../../shared/components/ResponsiveGrid.vue'
import ResponsiveImage from '../../shared/components/ResponsiveImage.vue'
import { portfolioAPI } from '../../shared/api'
import { useProductStore } from '../composables/useProductStore'
import type { Portfolio, Product } from '../../shared/types'

const router = useRouter()
const route = useRoute()

// 使用组合式函数
const { fetchProducts } = useProductStore()

// 响应式数据 - 从 URL 参数初始化标签
const currentTab = ref<'portfolio' | 'products'>(
  (route.query.tab === 'products' ? 'products' : 'portfolio') as 'portfolio' | 'products'
)

// 作品相关数据
const portfolios = ref<Portfolio[]>([])
const portfolioLoading = ref(true)
const portfolioError = ref<string | null>(null)
const sortBy = ref<'display_order' | 'created_at' | 'title' | 'featured'>('display_order')
const sortOrder = ref<'asc' | 'desc'>('desc')
const imageLoadingStates = ref<Record<number, boolean>>({})
const imageErrorStates = ref<Record<number, boolean>>({})

// 产品相关数据
const products = ref<Product[]>([])
const productLoading = ref(false)
const productError = ref<string | null>(null)
const selectedProductType = ref('')

// 计算属性
const sortedPortfolios = computed(() => {
  const sorted = [...portfolios.value].sort((a, b) => {
    let comparison = 0
    
    switch (sortBy.value) {
      case 'display_order':
        comparison = (a.display_order ?? 0) - (b.display_order ?? 0)
        break
      case 'created_at':
        comparison = new Date(a.created_at).getTime() - new Date(b.created_at).getTime()
        break
      case 'title':
        comparison = a.title.localeCompare(b.title, 'zh-CN')
        break
      case 'featured':
        // 精选优先，然后按display_order排序
        if (a.is_featured && !b.is_featured) return -1
        if (!a.is_featured && b.is_featured) return 1
        comparison = (a.display_order ?? 0) - (b.display_order ?? 0)
        break
    }
    
    return sortOrder.value === 'desc' ? -comparison : comparison
  })
  
  return sorted
})

const hasFilteredResults = computed(() => {
  return sortBy.value !== 'display_order' || sortOrder.value !== 'desc'
})

const filteredProducts = computed(() => {
  let filtered = products.value.filter(product => product.is_published)
  
  if (selectedProductType.value) {
    filtered = filtered.filter(product => product.product_type === selectedProductType.value)
  }
  
  return filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime())
})

// 方法
const loadPortfolios = async () => {
  try {
    portfolioLoading.value = true
    portfolioError.value = null
    const response = await portfolioAPI.getAll()
    portfolios.value = response.data
    
    // 初始化图片加载状态
    portfolios.value.forEach(portfolio => {
      if (portfolio.image_url) {
        imageLoadingStates.value[portfolio.id] = true
      }
    })
  } catch (err) {
    console.error('加载作品失败:', err)
    portfolioError.value = '加载作品失败，请稍后重试'
  } finally {
    portfolioLoading.value = false
  }
}

const loadProducts = async () => {
  try {
    productLoading.value = true
    productError.value = null
    products.value = await fetchProducts()
  } catch (err: any) {
    console.error('加载产品失败:', err)
    productError.value = err.message || '加载产品失败，请稍后重试'
  } finally {
    productLoading.value = false
  }
}

const sortPortfolios = () => {
  // 排序逻辑已在计算属性中处理
}

const toggleSortOrder = () => {
  sortOrder.value = sortOrder.value === 'desc' ? 'asc' : 'desc'
}

const clearFilters = () => {
  sortBy.value = 'display_order'
  sortOrder.value = 'desc'
}

const filterProducts = () => {
  // 筛选逻辑已在计算属性中处理
}

const clearProductFilters = () => {
  selectedProductType.value = ''
}

const launchProduct = (product: Product) => {
  router.push({
    path: `/product/${product.id}`,
    query: { from: 'portfolio' }
  })
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

const onImageLoad = (portfolioId: number) => {
  imageLoadingStates.value[portfolioId] = false
  imageErrorStates.value[portfolioId] = false
}

const onImageError = (portfolioId: number) => {
  imageLoadingStates.value[portfolioId] = false
  imageErrorStates.value[portfolioId] = true
}

const goToDetail = (id: number) => {
  router.push(`/portfolio/${id}`)
}

// 监听标签切换
watch(currentTab, (newTab) => {
  // 更新 URL 查询参数（不触发页面刷新）
  router.replace({
    path: route.path,
    query: { ...route.query, tab: newTab }
  })
  
  // 如果切换到产品标签且产品列表为空，则加载产品
  if (newTab === 'products' && products.value.length === 0) {
    loadProducts()
  }
})

// 监听路由查询参数变化（支持浏览器前进后退）
watch(() => route.query.tab, (newTab) => {
  if (newTab === 'products' && currentTab.value !== 'products') {
    currentTab.value = 'products'
  } else if (newTab !== 'products' && currentTab.value !== 'portfolio') {
    currentTab.value = 'portfolio'
  }
})

// 生命周期
onMounted(() => {
  loadPortfolios()
  
  // 如果 URL 参数指定了 products 标签，则加载产品数据
  if (currentTab.value === 'products') {
    loadProducts()
  }
})
</script>

<style scoped>
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.card-responsive-hover:hover {
  transform: translateY(-8px);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.animate-spin {
  animation: spin 1s linear infinite;
}

/* 产品标签样式 */
.tag-indigo {
  background: #e0e7ff;
  color: #3730a3;
}

/* 卡片入场动画 */
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

.card-responsive-hover {
  animation: fadeInUp 0.6s ease-out backwards;
}
</style>