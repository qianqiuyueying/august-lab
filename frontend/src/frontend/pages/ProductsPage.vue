<template>
  <div class="products-page">
    <!-- 页面头部 -->
    <div class="page-header">
      <div class="container">
        <h1 class="page-title">我的产品</h1>
        <p class="page-description">
          探索我开发的各种Web应用和工具，点击即可在线体验
        </p>
      </div>
    </div>

    <!-- 产品筛选和搜索 -->
    <div class="products-filters">
      <div class="container">
        <div class="filters-row">
          <div class="filter-group">
            <label>产品类型：</label>
            <select v-model="selectedType" @change="filterProducts">
              <option value="">全部</option>
              <option value="static">静态网站</option>
              <option value="spa">单页应用</option>
              <option value="game">游戏</option>
              <option value="tool">工具</option>
            </select>
          </div>
          
          <div class="filter-group">
            <label>技术栈：</label>
            <select v-model="selectedTech" @change="filterProducts">
              <option value="">全部</option>
              <option v-for="tech in availableTechs" :key="tech" :value="tech">
                {{ tech }}
              </option>
            </select>
          </div>
          
          <div class="search-group">
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

    <!-- 产品网格 -->
    <div class="products-content">
      <div class="container">
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
            v-for="product in filteredProducts"
            :key="product.id"
            class="product-card"
            @click="launchProduct(product)"
          >
            <!-- 产品预览图 -->
            <div class="product-preview">
              <img
                v-if="product.preview_image"
                :src="product.preview_image"
                :alt="product.title"
                class="preview-image"
              />
              <div v-else class="preview-placeholder">
                <div class="placeholder-icon">
                  {{ getProductIcon(product.product_type) }}
                </div>
              </div>
              
              <!-- 产品类型标签 -->
              <div class="product-type-badge" :class="`type-${product.product_type}`">
                {{ getProductTypeLabel(product.product_type) }}
              </div>
              
              <!-- 启动按钮 -->
              <div class="launch-overlay">
                <button class="launch-btn">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-6V7a2 2 0 00-2-2H5a2 2 0 00-2 2v3m2 13h10a2 2 0 002-2v-3m-2-13h10a2 2 0 012 2v3" />
                  </svg>
                  立即体验
                </button>
              </div>
            </div>

            <!-- 产品信息 -->
            <div class="product-info">
              <h3 class="product-title">{{ product.title }}</h3>
              <p class="product-description">{{ product.description }}</p>
              
              <!-- 技术栈标签 -->
              <div v-if="product.tech_stack?.length" class="tech-tags">
                <span
                  v-for="tech in product.tech_stack.slice(0, 3)"
                  :key="tech"
                  class="tech-tag"
                >
                  {{ tech }}
                </span>
                <span v-if="product.tech_stack.length > 3" class="tech-more">
                  +{{ product.tech_stack.length - 3 }}
                </span>
              </div>
              
              <!-- 产品统计 -->
              <div class="product-stats">
                <span class="stat-item">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" 
                          d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                  </svg>
                  {{ product.view_count || 0 }}
                </span>
                
                <span class="stat-item">
                  <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
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
      product.description.toLowerCase().includes(query) ||
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
  // 跳转到产品详情页
  router.push(`/product/${product.id}`)
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
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.page-header {
  padding: 4rem 0 2rem;
  text-align: center;
  color: white;
}

.container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 0 1rem;
}

.page-title {
  font-size: 3rem;
  font-weight: 700;
  margin-bottom: 1rem;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.page-description {
  font-size: 1.25rem;
  opacity: 0.9;
  max-width: 600px;
  margin: 0 auto;
}

.products-filters {
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  padding: 1.5rem 0;
  margin-bottom: 2rem;
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

.filter-group select {
  padding: 0.5rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
}

.filter-group select option {
  background: #374151;
  color: white;
}

.search-group {
  margin-left: auto;
}

.search-input {
  padding: 0.5rem 1rem;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 0.375rem;
  background: rgba(255, 255, 255, 0.1);
  color: white;
  backdrop-filter: blur(10px);
  width: 250px;
}

.search-input::placeholder {
  color: rgba(255, 255, 255, 0.7);
}

.products-content {
  padding-bottom: 4rem;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: 4rem 2rem;
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
  background: white;
  border-radius: 1rem;
  overflow: hidden;
  box-shadow: 0 10px 30px rgba(0, 0, 0, 0.2);
  transition: all 0.3s ease;
  cursor: pointer;
}

.product-card:hover {
  transform: translateY(-8px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
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
  padding: 0.75rem 1.5rem;
  border-radius: 0.5rem;
  font-weight: 500;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  transition: all 0.2s;
}

.launch-btn:hover {
  transform: scale(1.05);
}

.launch-btn svg {
  width: 1.25rem;
  height: 1.25rem;
}

.product-info {
  padding: 1.5rem;
}

.product-title {
  font-size: 1.25rem;
  font-weight: 600;
  color: #1f2937;
  margin-bottom: 0.5rem;
}

.product-description {
  color: #6b7280;
  margin-bottom: 1rem;
  line-height: 1.5;
}

.tech-tags {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}

.tech-tag {
  background: #f3f4f6;
  color: #374151;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
  font-weight: 500;
}

.tech-more {
  background: #e5e7eb;
  color: #6b7280;
  padding: 0.25rem 0.5rem;
  border-radius: 0.25rem;
  font-size: 0.75rem;
}

.product-stats {
  display: flex;
  gap: 1rem;
  color: #9ca3af;
  font-size: 0.875rem;
}

.stat-item {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.stat-item svg {
  width: 1rem;
  height: 1rem;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .page-title {
    font-size: 2rem;
  }
  
  .filters-row {
    flex-direction: column;
    align-items: stretch;
    gap: 1rem;
  }
  
  .search-group {
    margin-left: 0;
  }
  
  .search-input {
    width: 100%;
  }
  
  .products-grid {
    grid-template-columns: 1fr;
    gap: 1rem;
  }
  
  .product-card {
    margin: 0 1rem;
  }
}
</style>