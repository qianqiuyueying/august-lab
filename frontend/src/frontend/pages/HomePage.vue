<template>
  <div class="min-h-screen">
    <!-- 主视觉区域 - 简洁专业风格 -->
    <section class="hero-section relative min-h-screen flex items-center overflow-hidden bg-gradient-to-br from-primary-50 via-white to-primary-50/50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900">
      <!-- 背景装饰 - 更简洁 -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute top-0 right-0 w-96 h-96 bg-primary-200/30 dark:bg-primary-900/20 rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 left-0 w-96 h-96 bg-primary-300/20 dark:bg-primary-800/20 rounded-full blur-3xl"></div>
      </div>
      
      <!-- 内容区域 -->
      <ResponsiveContainer size="xl" class="relative z-10 py-20 md:py-28 lg:py-32">
        <div class="max-w-5xl mx-auto">
          <div class="text-center space-y-8 md:space-y-10">
            <!-- 装饰性标签 -->
            <div class="inline-flex items-center gap-2 px-4 py-2 bg-primary-100 dark:bg-primary-900/30 rounded-full border border-primary-200 dark:border-primary-800">
              <span class="w-2 h-2 bg-success-500 rounded-full animate-pulse"></span>
              <span class="text-sm font-medium text-primary-700 dark:text-primary-300">全栈开发者 · 在线</span>
            </div>
            
            <!-- 主标题 -->
            <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-bold leading-tight tracking-tight">
              <span class="block text-gray-900 dark:text-gray-50 mb-2">Hello,</span>
              <span class="block text-primary-500 dark:text-primary-400">
                I'm August
              </span>
            </h1>
            
            <!-- 副标题 -->
            <p class="text-xl md:text-2xl lg:text-3xl text-gray-600 dark:text-gray-300 leading-relaxed max-w-3xl mx-auto">
              用代码创造数字体验
              <br class="hidden md:block">
              <span class="text-lg md:text-xl text-gray-500 dark:text-gray-400">让技术与创意完美融合</span>
            </p>
            
            <!-- CTA 按钮组 -->
            <div class="flex flex-col sm:flex-row gap-4 justify-center pt-4">
              <router-link 
                to="/portfolio" 
                class="btn-primary inline-flex items-center justify-center gap-2 group"
              >
                探索作品
                <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                </svg>
              </router-link>
              
              <router-link 
                to="/about" 
                class="btn-secondary inline-flex items-center justify-center"
              >
                了解更多
              </router-link>
            </div>
            
            <!-- 社交链接 -->
            <div class="flex flex-col sm:flex-row items-center justify-center gap-6 pt-6">
              <span class="text-sm text-gray-500 dark:text-gray-400">关注我</span>
              <div class="flex gap-4">
                <a 
                  href="#" 
                  class="w-12 h-12 bg-white dark:bg-gray-800 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all hover:scale-110 shadow-sm"
                  aria-label="GitHub"
                >
                  <svg class="w-6 h-6 text-gray-700 dark:text-gray-300" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                  </svg>
                </a>
                <a 
                  href="#" 
                  class="w-12 h-12 bg-white dark:bg-gray-800 rounded-lg flex items-center justify-center border border-gray-200 dark:border-gray-700 hover:border-primary-500 dark:hover:border-primary-500 hover:bg-primary-50 dark:hover:bg-primary-900/20 transition-all hover:scale-110 shadow-sm"
                  aria-label="Twitter"
                >
                  <svg class="w-6 h-6 text-gray-700 dark:text-gray-300" fill="currentColor" viewBox="0 0 24 24">
                    <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                  </svg>
                </a>
              </div>
            </div>
          </div>
        </div>
      </ResponsiveContainer>
      
      <!-- 滚动提示 -->
      <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-10 animate-bounce">
        <svg class="w-6 h-6 text-gray-400 dark:text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </section>
    
    <!-- 最新作品预览 -->
    <section class="section-padding bg-white dark:bg-gray-900 relative overflow-hidden">
      <ResponsiveContainer size="xl" class="relative z-10">
        <!-- 标题区域 -->
        <div class="text-center mb-16">
          <div class="inline-block mb-4">
            <span class="text-sm font-semibold text-primary-600 dark:text-primary-400 uppercase tracking-wider">Portfolio</span>
          </div>
          <h2 class="text-4xl md:text-5xl lg:text-6xl font-bold text-gray-900 dark:text-gray-50 mb-4 leading-tight">
            精选<span class="text-primary-500 dark:text-primary-400">作品</span>
          </h2>
          <p class="text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto">
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
          
          <!-- 作品网格 - 优化间距和响应式 -->
          <div v-else-if="featuredPortfolios.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 md:gap-8 mb-12 md:mb-16">
          <div 
            v-for="(portfolio, idx) in featuredPortfolios" 
            :key="portfolio.id" 
            class="group cursor-pointer"
            :class="{
              'md:col-span-2 xl:col-span-1': idx === 0,
              'xl:row-span-2': idx === 1
            }"
            @click="goToPortfolioDetail(portfolio.id)"
          >
            <div class="h-full bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-200 dark:border-gray-700">
              <!-- 项目图片 -->
              <div class="relative overflow-hidden bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20" :class="idx === 1 ? 'h-64' : 'aspect-video'">
                <ResponsiveImage
                  v-if="portfolio.image_url"
                  :src="portfolio.image_url"
                  :alt="portfolio.title"
                  :aspect-ratio="idx === 1 ? undefined : 'video'"
                  class="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500"
                />
                <div v-else class="w-full h-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/30 dark:to-primary-800/30 flex items-center justify-center">
                  <svg class="w-16 h-16 text-primary-400 dark:text-primary-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                
                <!-- 特色标签 -->
                <div v-if="idx === 0" class="absolute top-4 left-4 px-3 py-1 bg-primary-500 text-white text-xs font-semibold rounded-full shadow-md">
                  精选
                </div>
              </div>
              
              <!-- 项目信息 -->
              <div class="p-6 space-y-4 bg-white dark:bg-gray-800">
                <div class="flex items-start justify-between">
                  <h3 class="text-xl font-bold text-gray-900 dark:text-gray-50 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors">
                    {{ portfolio.title }}
                  </h3>
                  <svg class="w-5 h-5 text-gray-400 dark:text-gray-500 group-hover:text-primary-500 dark:group-hover:text-primary-400 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
                <p class="text-gray-600 dark:text-gray-400 text-sm leading-relaxed" :class="idx === 1 ? '' : 'line-clamp-2'">
                  {{ portfolio.description || '暂无描述' }}
                </p>
                
                <!-- 技术栈标签 -->
                <div class="flex flex-wrap gap-2 pt-2">
                  <span 
                    v-for="tech in portfolio.tech_stack.slice(0, 3)" 
                    :key="tech"
                    class="px-3 py-1 bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-xs font-medium rounded-full border border-primary-200 dark:border-primary-800"
                  >
                    {{ tech }}
                  </span>
                  <span 
                    v-if="portfolio.tech_stack.length > 3"
                    class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-medium rounded-full"
                  >
                    +{{ portfolio.tech_stack.length - 3 }}
                  </span>
                </div>
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
          <div v-if="featuredPortfolios.length > 0" class="text-center mt-12">
            <router-link 
              to="/portfolio" 
              class="btn-primary inline-flex items-center gap-2"
            >
              查看所有作品
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 最新产品预览 -->
    <section class="py-16 md:py-20 lg:py-24 bg-gray-50 dark:bg-gray-800 relative overflow-hidden">
      <ResponsiveContainer size="xl" class="relative z-10">
        <div class="text-center mb-12 md:mb-16">
          <div class="inline-block mb-4">
            <span class="text-sm font-semibold text-primary-600 dark:text-primary-400 uppercase tracking-wider">Products</span>
          </div>
          <h2 class="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 dark:text-gray-50 mb-4 leading-tight">
            在线<span class="text-primary-500 dark:text-primary-400">产品</span>
          </h2>
          <p class="text-base md:text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto px-4">
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
          
          <!-- 产品网格 - 优化间距 -->
          <div v-else-if="featuredProducts.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 md:gap-8 mb-12 md:mb-16">
            <div 
              v-for="product in featuredProducts" 
              :key="product.id" 
              class="group cursor-pointer"
              @click="launchProduct(product)"
            >
              <div class="h-full bg-white dark:bg-gray-800 rounded-xl overflow-hidden shadow-md hover:shadow-xl transition-all duration-300 transform hover:-translate-y-1 border border-gray-200 dark:border-gray-700">
              <!-- 产品预览图 -->
              <div class="relative overflow-hidden bg-gradient-to-br from-primary-50 to-primary-100 dark:from-primary-900/20 dark:to-primary-800/20 aspect-video">
                <ResponsiveImage
                  v-if="product.preview_image"
                  :src="product.preview_image"
                  :alt="product.title"
                  aspect-ratio="video"
                  class="group-hover:scale-105 transition-transform duration-500"
                />
                <div v-else class="w-full h-full bg-gradient-to-br from-primary-100 to-primary-200 dark:from-primary-900/30 dark:to-primary-800/30 flex items-center justify-center">
                  <div class="text-6xl opacity-60">
                    {{ getProductIcon(product.product_type) }}
                  </div>
                </div>
                
                <!-- 产品类型标签 -->
                <div class="absolute top-3 right-3 px-3 py-1 rounded-full text-xs font-semibold text-white shadow-md" :class="getProductTypeClass(product.product_type)">
                  {{ getProductTypeLabel(product.product_type) }}
                </div>
              </div>
              
              <!-- 产品信息 -->
              <div class="p-6 space-y-4 bg-white dark:bg-gray-800">
                <h3 class="text-xl font-bold text-gray-900 dark:text-gray-50 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors">
                  {{ product.title }}
                </h3>
                <p class="text-gray-600 dark:text-gray-400 text-sm leading-relaxed line-clamp-2">
                  {{ product.description || '暂无描述' }}
                </p>
                
                <!-- 技术栈标签 -->
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="tech in product.tech_stack?.slice(0, 3)" 
                    :key="tech"
                    class="px-3 py-1 bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-xs font-medium rounded-full border border-primary-200 dark:border-primary-800"
                  >
                    {{ tech }}
                  </span>
                  <span 
                    v-if="product.tech_stack && product.tech_stack.length > 3"
                    class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-medium rounded-full"
                  >
                    +{{ product.tech_stack.length - 3 }}
                  </span>
                </div>
                
                <!-- 产品统计 -->
                <div class="flex items-center justify-between pt-3 border-t border-gray-200 dark:border-gray-700">
                  <div class="flex items-center gap-1.5 text-xs text-gray-500 dark:text-gray-400">
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                    </svg>
                    {{ product.view_count || 0 }} 次体验
                  </div>
                  <div class="px-4 py-1.5 bg-primary-500 text-white rounded-full font-semibold text-xs shadow-md">
                    立即体验
                  </div>
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
          <div v-if="featuredProducts.length > 0" class="text-center mt-12">
            <router-link 
              :to="{ path: '/portfolio', query: { tab: 'products' } }" 
              class="btn-primary inline-flex items-center gap-2"
            >
              查看所有产品
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 最新博客预览 -->
    <section class="py-16 md:py-20 lg:py-24 bg-white dark:bg-gray-900">
      <ResponsiveContainer size="xl">
        <div class="text-center mb-12 md:mb-16">
          <div class="inline-block mb-4">
            <span class="text-sm font-semibold text-primary-600 dark:text-primary-400 uppercase tracking-wider">Blog</span>
          </div>
          <h2 class="text-4xl sm:text-5xl md:text-6xl font-bold text-gray-900 dark:text-gray-50 mb-4 leading-tight">
            最新<span class="text-primary-500 dark:text-primary-400">博客</span>
          </h2>
          <p class="text-base md:text-lg text-gray-600 dark:text-gray-400 max-w-2xl mx-auto px-4">
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
        
        <!-- 博客网格 - 优化间距 -->
        <div v-else-if="recentBlogs.length > 0" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 md:gap-8 mb-12 md:mb-16">
          <article 
            v-for="(blog, idx) in recentBlogs" 
            :key="blog.id"
            class="bg-white dark:bg-gray-800 rounded-xl shadow-md hover:shadow-xl transition-all duration-300 overflow-hidden group cursor-pointer transform hover:-translate-y-1 border border-gray-200 dark:border-gray-700 hover:border-primary-300 dark:hover:border-primary-600"
            :style="{ animationDelay: `${idx * 100}ms` }"
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
              <h3 class="text-lg font-bold text-gray-900 dark:text-gray-50 group-hover:text-primary-500 dark:group-hover:text-primary-400 transition-colors duration-200 line-clamp-2">
                {{ blog.title }}
              </h3>
              
              <!-- 摘要 -->
              <p class="text-gray-600 dark:text-gray-400 text-sm leading-relaxed line-clamp-3">
                {{ blog.summary || extractSummary(blog.content) }}
              </p>
              
              <!-- 标签 -->
              <div class="flex flex-wrap gap-2">
                <span 
                  v-for="tag in blog.tags.slice(0, 3)" 
                  :key="tag"
                  class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-medium rounded-full"
                >
                  {{ tag }}
                </span>
                <span 
                  v-if="blog.tags.length > 3"
                  class="px-3 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-400 text-xs font-medium rounded-full"
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
          <div v-if="recentBlogs.length > 0" class="text-center mt-12">
            <router-link 
              to="/blog" 
              class="btn-primary inline-flex items-center gap-2"
            >
              查看所有博客
              <svg class="w-5 h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 联系我区域 -->
    <section class="py-16 md:py-20 lg:py-24 bg-primary-500 dark:bg-primary-600 text-white relative overflow-hidden">
      <!-- 背景装饰 -->
      <div class="absolute inset-0 opacity-10">
        <div class="absolute top-0 left-0 w-64 h-64 bg-white rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
      </div>
      
      <ResponsiveContainer size="lg" class="relative z-10">
        <div class="text-center px-4">
          <h2 class="text-3xl sm:text-4xl md:text-5xl font-bold mb-4 md:mb-6 text-white">
            让我们一起创造
          </h2>
          <p class="text-base md:text-lg lg:text-xl mb-8 md:mb-10 opacity-95 max-w-2xl mx-auto leading-relaxed">
            有想法？有项目？或者只是想聊聊技术？
            <br class="hidden sm:block">
            随时欢迎与我联系，让我们一起把想法变成现实。
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <router-link 
              to="/about" 
              class="w-full sm:w-auto bg-white text-primary-600 hover:bg-gray-50 font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 rounded-lg px-8 py-4 text-base md:text-lg"
            >
              联系我
            </router-link>
            <a 
              href="mailto:hello@august.lab" 
              class="w-full sm:w-auto border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold transition-all duration-300 shadow-lg hover:shadow-xl transform hover:scale-105 rounded-lg px-8 py-4 text-base md:text-lg"
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
  router.push({
    path: `/product/${product.id}`,
    query: { from: 'home' }
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

/* 3D Blob 动画 */
@keyframes blob {
  0%, 100% {
    transform: translate(0px, 0px) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.animate-blob {
  animation: blob 7s infinite;
}

.animation-delay-2000 {
  animation-delay: 2s;
}

.animation-delay-4000 {
  animation-delay: 4s;
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

.grid > div {
  animation: fadeInUp 0.6s ease-out backwards;
}
</style>