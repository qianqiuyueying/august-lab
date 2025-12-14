<template>
  <div class="products-page min-h-screen">
    <!-- 页面头部 - 大胆设计 -->
    <div class="page-header relative overflow-hidden">
      <div class="absolute inset-0 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900">
        <div class="absolute inset-0 opacity-30">
          <div class="absolute top-0 left-0 w-96 h-96 bg-purple-500 rounded-full blur-3xl"></div>
          <div class="absolute bottom-0 right-0 w-96 h-96 bg-pink-500 rounded-full blur-3xl"></div>
        </div>
      </div>
      
      <div class="container relative z-10">
        <div class="text-center py-20">
          <div class="inline-block mb-4">
            <span class="text-sm font-bold text-pink-400 uppercase tracking-wider">Products</span>
          </div>
          <h1 class="text-6xl md:text-7xl font-black text-white mb-6 leading-tight">
            我的<span class="bg-gradient-to-r from-pink-400 via-purple-400 to-indigo-400 bg-clip-text text-transparent">产品</span>
          </h1>
          <p class="text-xl text-white/80 max-w-2xl mx-auto">
            探索我开发的各种Web应用和工具，点击即可在线体验
          </p>
        </div>
      </div>
    </div>

    <!-- 产品筛选和搜索 - 玻璃态设计 -->
    <div class="products-filters sticky top-0 z-50 backdrop-blur-xl bg-white/10 border-b border-white/20">
      <div class="container">
        <div class="filters-row py-6">
          <div class="filter-group">
            <label class="text-white/90 font-medium">产品类型</label>
            <select v-model="selectedType" @change="filterProducts" class="filter-select">
              <option value="">全部</option>
              <option value="static">静态网站</option>
              <option value="spa">单页应用</option>
              <option value="game">游戏</option>
              <option value="tool">工具</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label class="text-white/90 font-medium">技术栈</label>
            <select v-model="selectedTech" @change="filterProducts" class="filter-select">
              <option value="">全部</option>
              <option v-for="tech in availableTechs" :key="tech" :value="tech">
                {{ tech }}
              </option>
            </select>
          </div>
          
          <div class="search-group flex-1">
            <div class="relative">
              <svg class="absolute left-4 top-1/2 transform -translate-y-1/2 w-5 h-5 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
              <input
                v-model="searchQuery"
                type="text"
                placeholder="搜索产品..."
                @input="filterProducts"
                class="search-input"
              />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 产品网格 -->
    <div class="products-content bg-gradient-to-b from-slate-900 via-purple-900 to-slate-900 min-h-screen">
      <div class="container py-12">
        <!-- 加载状态 -->
        <div v-if="isLoading" class="loading-state">
          <div class="loading-spinner"></div>
          <p>正在加载产品...</p>
        </div>

        <!-- 错误状态 -->
        <div v-else-if="error" class="error-state">
          <div class="error-icon">⚠️</div>
          <h3>加载失败</h3>
          <p>{{ error }}</p>
          <button @click="loadProducts" class="retry-btn">重试</button>
        </div>

        <!-- 空状态 -->
        <div v-else-if="filteredProducts.length === 0" class="empty-state">
          <div class="empty-icon">📦</div>
          <h3>{{ products.length === 0 ? '暂无产品' : '未找到匹配的产品' }}</h3>
          <p>{{ products.length === 0 ? '还没有发布任何产品' : '尝试调整筛选条件' }}</p>
        </div>

        <!-- 产品列表 -->
        <div v-else class="products-grid">
          <div
            v-for="(product, index) in filteredProducts"
            :key="product.id"
            class="product-card group"
            :style="{ animationDelay: `${index * 50}ms` }"
            @click="launchProduct(product)"
          >
            <div class="h-full bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 overflow-hidden shadow-2xl hover:bg-white/20 transition-all duration-500 transform hover:-translate-y-2 hover:scale-[1.02] cursor-pointer">
              <!-- 产品预览图 -->
              <div class="product-preview relative overflow-hidden bg-gradient-to-br from-pink-500/20 to-purple-500/20 aspect-video">
                <img
                  v-if="product.preview_image"
                  :src="product.preview_image"
                  :alt="product.title"
                  class="preview-image w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div v-else class="preview-placeholder w-full h-full bg-gradient-to-br from-pink-500/30 to-purple-500/30 flex items-center justify-center">
                  <div class="placeholder-icon text-6xl opacity-80">
                    {{ getProductIcon(product.product_type) }}
                  </div>
                </div>
                
                <!-- 产品类型标签 -->
                <div class="product-type-badge absolute top-4 right-4 px-4 py-1.5 rounded-full text-xs font-bold text-white backdrop-blur-md bg-black/30 border border-white/20">
                  {{ getProductTypeLabel(product.product_type) }}
                </div>
                
                <!-- 启动按钮 -->
                <div class="launch-overlay absolute inset-0 bg-gradient-to-t from-black/90 via-black/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 flex items-center justify-center">
                  <div class="transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                    <button class="launch-btn bg-white text-purple-600 px-6 py-3 rounded-xl font-bold shadow-2xl transform scale-90 group-hover:scale-100 transition-transform duration-300 flex items-center gap-2">
                      <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-5 h-5">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                              d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-6V7a2 2 0 00-2-2H5a2 2 0 00-2 2v3m2 13h10a2 2 0 002-2v-3m-2-13h10a2 2 0 012 2v3" />
                      </svg>
                      立即体验
                    </button>
                  </div>
                </div>
              </div>

              <!-- 产品信息 -->
              <div class="product-info p-6 bg-white/5">
                <h3 class="product-title text-xl font-bold text-white mb-3 group-hover:text-pink-300 transition-colors">{{ product.title }}</h3>
                <p class="product-description text-white/70 text-sm leading-relaxed mb-4 line-clamp-2">{{ product.description }}</p>
                
                <!-- 技术栈标签 -->
                <div v-if="product.tech_stack?.length" class="tech-tags mb-4">
                  <span
                    v-for="tech in product.tech_stack.slice(0, 3)"
                    :key="tech"
                    class="tech-tag px-3 py-1 bg-white/20 backdrop-blur-sm text-white text-xs font-medium rounded-full border border-white/30"
                  >
                    {{ tech }}
                  </span>
                  <span v-if="product.tech_stack.length > 3" class="tech-more px-3 py-1 bg-white/10 text-white/60 text-xs font-medium rounded-full">
                    +{{ product.tech_stack.length - 3 }}
                  </span>
                </div>
                
                <!-- 产品统计 -->
                <div class="product-stats flex items-center justify-between pt-4 border-t border-white/20">
                  <span class="stat-item flex items-center gap-1.5 text-xs text-white/60">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-4 h-4">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {{ product.view_count || 0 }} 次体验
                  </span>
                  
                  <span class="stat-item flex items-center gap-1.5 text-xs text-white/60">
                    <svg fill="none" stroke="currentColor" viewBox="0 0 24 24" class="w-4 h-4">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                            d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    {{ formatDate(product.created_at) }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useProductStore } from '../composables/useProductStore'
import type { Product } from '../../shared/types'

const router = useRouter()

// 响应式数据
const products = ref<Product[]>([])
const isLoading = ref(false)
const error = ref<string | null>(null)
const selectedType = ref('')
const selectedTech = ref('')
const searchQuery = ref('')

// 使用组合式函数
const { fetchProducts } = useProductStore()

// 计算属性
const availableTechs = computed(() => {
  const techs = new Set<string>()
  products.value.forEach(product => {
    product.tech_stack?.forEach(tech => techs.add(tech))
  })
  return Array.from(techs).sort()
})

const filteredProducts = computed(() => {
  let filtered = products.value.filter(product => product.is_published)
  
  // 按类型筛选
  if (selectedType.value) {
    filtered = filtered.filter(product => product.product_type === selectedType.value)
  }
  
  // 按技术栈筛选
  if (selectedTech.value) {
    filtered = filtered.filter(product => 
      product.tech_stack?.includes(selectedTech.value)
    )
  }
  
  // 按搜索关键词筛选
  if (searchQuery.value) {
    const query = searchQuery.value.toLowerCase()
    filtered = filtered.filter(product =>
      product.title.toLowerCase().includes(query) ||
      (product.description?.toLowerCase().includes(query) ?? false) ||
      product.tech_stack?.some(tech => tech.toLowerCase().includes(query))
    )
  }
  
  return filtered
})

// 方法
const loadProducts = async () => {
  isLoading.value = true
  error.value = null
  
  try {
    const data = await fetchProducts()
    products.value = data
  } catch (err: any) {
    error.value = err.message || '加载产品失败'
    console.error('加载产品失败:', err)
  } finally {
    isLoading.value = false
  }
}

const filterProducts = () => {
  // 筛选逻辑已在计算属性中处理
}

const launchProduct = (product: Product) => {
  // 跳转到产品详情页，传递来源信息
  router.push({
    path: `/product/${product.id}`,
    query: { from: 'products' }
  })
}

const getProductIcon = (type: string) => {
  const icons = {
    static: '🌐',
    spa: '⚡',
    game: '🎮',
    tool: '🔧'
  }
  return icons[type as keyof typeof icons] || '📦'
}

const getProductTypeLabel = (type: string) => {
  const labels = {
    static: '静态网站',
    spa: '单页应用',
    game: '游戏',
    tool: '工具'
  }
  return labels[type as keyof typeof labels] || type
}

const formatDate = (dateString: string) => {
  const date = new Date(dateString)
  return date.toLocaleDateString('zh-CN', {
    year: 'numeric',
    month: 'short',
    day: 'numeric'
  })
}

// 生命周期
onMounted(() => {
  loadProducts()
})
</script>

<style scoped>
.products-page {
  min-height: 100vh;
  background: #0f172a;
}

.page-header {
  padding: 5rem 0 3rem;
  text-align: center;
  color: white;
  position: relative;
  z-index: 10;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-title {
  font-size: 3.5rem;
  font-weight: 800;
  margin-bottom: 1.5rem;
  text-shadow: 0 4px 12px rgba(0, 0, 0, 0.3);
  background: linear-gradient(to right, #ffffff, #e0e7ff);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
  animation: fadeInUp 0.8s ease-out;
}

.page-description {
  font-size: 1.25rem;
  opacity: 0.95;
  max-width: 600px;
  margin: 0 auto;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.2);
  animation: fadeInUp 0.8s ease-out 0.2s backwards;
}

.products-filters {
  position: relative;
}

.filters-row {
  display: flex;
  gap: 2rem;
  align-items: center;
  flex-wrap: wrap;
}

.filter-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: white;
}

.filter-group label {
  font-weight: 500;
  white-space: nowrap;
}

.filter-select {
  padding: 0.75rem 1rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
  transition: all 0.3s ease;
  font-weight: 500;
  min-width: 150px;
}

.filter-select:hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.15);
}

.filter-select:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.filter-select option {
  background: #1e293b;
  color: white;
}

.filter-group select option {
  background: #374151;
  color: white;
}

.search-group {
  margin-left: auto;
}

.search-input {
  padding: 0.75rem 1rem 0.75rem 3rem;
  border: 2px solid rgba(255, 255, 255, 0.2);
  border-radius: 0.75rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
  width: 100%;
  transition: all 0.3s ease;
  font-weight: 500;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.5);
}

.search-input:hover {
  border-color: rgba(255, 255, 255, 0.4);
  background: rgba(255, 255, 255, 0.15);
}

.search-input:focus {
  outline: none;
  border-color: rgba(255, 255, 255, 0.6);
  background: rgba(255, 255, 255, 0.2);
  box-shadow: 0 0 0 3px rgba(255, 255, 255, 0.1);
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.products-content {
  padding-bottom: 4rem;
  position: relative;
  z-index: 10;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 6rem 2rem;
  color: white;
}

.loading-spinner {
  width: 3rem;
  height: 3rem;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top: 3px solid white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto 1rem;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

.error-icon,
.empty-icon {
  font-size: 4rem;
  margin-bottom: 1rem;
}

.retry-btn {
  background: white;
  color: #667eea;
  border: none;
  padding: 0.75rem 1.5rem;
  border-radius: 0.375rem;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.retry-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.2);
}

.products-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 2rem;
}

.product-card {
  animation: fadeInUp 0.6s ease-out backwards;
}

.product-preview {
  position: relative;
  height: 200px;
  overflow: hidden;
}

.preview-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.preview-placeholder {
  width: 100%;
  height: 100%;
  background: linear-gradient(135deg, #f3f4f6 0%, #e5e7eb 100%);
  display: flex;
  align-items: center;
  justify-content: center;
}

.placeholder-icon {
  font-size: 4rem;
  opacity: 0.5;
}

.product-type-badge {
  position: absolute;
  top: 1rem;
  right: 1rem;
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.75rem;
  font-weight: 500;
  color: white;
}

.type-static { background: #3b82f6; }
.type-spa { background: #8b5cf6; }
.type-game { background: #ef4444; }
.type-tool { background: #10b981; }

.launch-overlay {
  position: absolute;
  inset: 0;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  align-items: center;
  justify-content: center;
  opacity: 0;
  transition: opacity 0.3s;
}

.product-card:hover .launch-overlay {
  opacity: 1;
}

.launch-btn {
  background: white;
  color: #374151;
  border: none;
  padding: 0.875rem 2rem;
  border-radius: 0.75rem;
  font-weight: 600;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  cursor: pointer;
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
  transform: translateY(10px);
}

.product-card:hover .launch-btn {
  transform: translateY(0) scale(1.05);
}

.launch-btn:hover {
  transform: scale(1.1);
  box-shadow: 0 6px 20px rgba(0, 0, 0, 0.25);
}

.launch-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.product-info {
  position: relative;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

/* 动画 */
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

/* 响应式设计 */
@media (max-width: 768px) {
  .filters-row {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .filter-group {
    width: 100%;
  }
  
  .filter-select {
    width: 100%;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
    gap: 1.5rem;
  }
}
</style>