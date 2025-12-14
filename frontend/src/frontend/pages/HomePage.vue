<template>
  <div class="min-h-screen">
    <!-- 主视觉区域 - 大胆现代风格 -->
    <section class="hero-section relative min-h-screen flex items-center overflow-hidden">
      <!-- 动态背景 -->
      <div class="absolute inset-0 bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
        <div class="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxnIGZpbGw9IiNmZmYiIGZpbGwtb3BhY2l0eT0iMC4wNSI+PGNpcmNsZSBjeD0iMzAiIGN5PSIzMCIgcj0iMiIvPjwvZz48L2c+PC9zdmc+')] opacity-30"></div>
      </div>
      
      <!-- 3D 浮动元素 -->
      <div class="absolute inset-0 overflow-hidden">
        <div class="absolute top-20 left-10 w-72 h-72 bg-purple-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob"></div>
        <div class="absolute top-40 right-10 w-72 h-72 bg-pink-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-2000"></div>
        <div class="absolute -bottom-8 left-1/2 w-72 h-72 bg-blue-500 rounded-full mix-blend-multiply filter blur-3xl opacity-20 animate-blob animation-delay-4000"></div>
      </div>
      
      <!-- 内容区域 -->
      <ResponsiveContainer size="xl" class="relative z-10 py-16 md:py-24 lg:py-32">
        <div class="max-w-7xl mx-auto">
          <div class="grid lg:grid-cols-12 gap-8 lg:gap-12 items-center">
            <!-- 左侧文字内容 - 占据更多空间 -->
            <div class="lg:col-span-7 text-center lg:text-left space-y-6 md:space-y-8">
              <!-- 装饰性标签 -->
              <div class="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur-md rounded-full border border-white/20 mb-2">
                <span class="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                <span class="text-white/90 text-sm font-medium">全栈开发者 · 在线</span>
              </div>
              
              <!-- 主标题 - 优化字体大小和间距 -->
              <h1 class="text-5xl sm:text-6xl md:text-7xl lg:text-8xl font-black leading-[1.1] tracking-tight">
                <span class="block text-white mb-1 md:mb-2">Hello,</span>
                <span class="block bg-gradient-to-r from-purple-400 via-pink-400 to-blue-400 bg-clip-text text-transparent">
                  I'm August
                </span>
              </h1>
              
              <!-- 副标题 - 优化行高和间距 -->
              <p class="text-lg md:text-xl lg:text-2xl text-white/80 leading-relaxed max-w-xl mx-auto lg:mx-0">
                用代码创造数字体验
                <br class="hidden md:block">
                <span class="text-white/60 text-base md:text-lg lg:text-xl">让技术与创意完美融合</span>
              </p>
              
              <!-- CTA 按钮组 - 优化间距和大小 -->
              <div class="flex flex-col sm:flex-row gap-3 md:gap-4 pt-2">
                <router-link 
                  to="/portfolio" 
                  class="group relative px-6 md:px-8 py-3 md:py-4 bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl font-bold text-white text-base md:text-lg shadow-2xl shadow-purple-500/50 hover:shadow-purple-500/70 transition-all duration-300 transform hover:scale-105 overflow-hidden"
                >
                  <span class="relative z-10 flex items-center justify-center gap-2">
                    探索作品
                    <svg class="w-4 h-4 md:w-5 md:h-5 group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                    </svg>
                  </span>
                  <div class="absolute inset-0 bg-gradient-to-r from-pink-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity"></div>
                </router-link>
                
                <router-link 
                  to="/about" 
                  class="px-6 md:px-8 py-3 md:py-4 bg-white/10 backdrop-blur-md border-2 border-white/30 rounded-xl font-bold text-white text-base md:text-lg hover:bg-white/20 transition-all duration-300 transform hover:scale-105"
                >
                  了解更多
                </router-link>
              </div>
              
              <!-- 社交链接 - 优化布局 -->
              <div class="flex flex-col sm:flex-row items-center sm:items-center gap-4 sm:gap-6 pt-2">
                <span class="text-white/60 text-sm">关注我</span>
                <div class="flex gap-3 md:gap-4">
                  <a href="#" class="w-10 h-10 md:w-12 md:h-12 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center border border-white/20 hover:bg-white/20 transition-all hover:scale-110">
                    <svg class="w-5 h-5 md:w-6 md:h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/>
                    </svg>
                  </a>
                  <a href="#" class="w-10 h-10 md:w-12 md:h-12 bg-white/10 backdrop-blur-md rounded-lg flex items-center justify-center border border-white/20 hover:bg-white/20 transition-all hover:scale-110">
                    <svg class="w-5 h-5 md:w-6 md:h-6 text-white" fill="currentColor" viewBox="0 0 24 24">
                      <path d="M23.953 4.57a10 10 0 01-2.825.775 4.958 4.958 0 002.163-2.723c-.951.555-2.005.959-3.127 1.184a4.92 4.92 0 00-8.384 4.482C7.69 8.095 4.067 6.13 1.64 3.162a4.822 4.822 0 00-.666 2.475c0 1.71.87 3.213 2.188 4.096a4.904 4.904 0 01-2.228-.616v.06a4.923 4.923 0 003.946 4.827 4.996 4.996 0 01-2.212.085 4.936 4.936 0 004.604 3.417 9.867 9.867 0 01-6.102 2.105c-.39 0-.779-.023-1.17-.067a13.995 13.995 0 007.557 2.209c9.053 0 13.998-7.496 13.998-13.985 0-.21 0-.42-.015-.63A9.935 9.935 0 0024 4.59z"/>
                    </svg>
                  </a>
                </div>
              </div>
            </div>
            
            <!-- 右侧视觉元素 - 优化尺寸和位置 -->
            <div class="lg:col-span-5 hidden lg:block relative">
              <div class="relative w-full max-w-md mx-auto aspect-square">
                <!-- 3D 卡片效果 - 优化层次 -->
                <div class="absolute inset-0 bg-gradient-to-br from-purple-500/20 to-pink-500/20 rounded-3xl backdrop-blur-xl border border-white/20 transform rotate-6 hover:rotate-3 transition-transform duration-500 shadow-2xl"></div>
                <div class="absolute inset-0 bg-gradient-to-br from-blue-500/20 to-purple-500/20 rounded-3xl backdrop-blur-xl border border-white/20 transform -rotate-6 hover:-rotate-3 transition-transform duration-500 shadow-2xl"></div>
                <div class="absolute inset-4 bg-gradient-to-br from-white/10 to-white/5 rounded-2xl backdrop-blur-2xl border border-white/20 flex items-center justify-center shadow-inner">
                  <div class="text-7xl md:text-8xl">💻</div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </ResponsiveContainer>
      
      <!-- 滚动提示 -->
      <div class="absolute bottom-8 left-1/2 transform -translate-x-1/2 z-10 animate-bounce">
        <svg class="w-6 h-6 text-white/60" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 14l-7 7m0 0l-7-7m7 7V3" />
        </svg>
      </div>
    </section>
    
    <!-- 最新作品预览 - 创意布局 -->
    <section class="section-padding bg-gradient-to-b from-slate-50 to-white relative overflow-hidden">
      <!-- 背景装饰 -->
      <div class="absolute top-0 right-0 w-96 h-96 bg-purple-200 rounded-full blur-3xl opacity-20"></div>
      <div class="absolute bottom-0 left-0 w-96 h-96 bg-blue-200 rounded-full blur-3xl opacity-20"></div>
      
      <ResponsiveContainer size="xl" class="relative z-10">
        <!-- 标题区域 - 不对称设计 -->
        <div class="mb-16">
          <div class="inline-block mb-4">
            <span class="text-sm font-bold text-purple-600 uppercase tracking-wider">Portfolio</span>
          </div>
          <h2 class="text-5xl md:text-6xl font-black text-gray-900 mb-6 leading-tight">
            精选<span class="bg-gradient-to-r from-purple-600 to-pink-600 bg-clip-text text-transparent">作品</span>
          </h2>
          <p class="text-lg text-gray-600 max-w-2xl">
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
            <div class="h-full bg-white rounded-2xl overflow-hidden shadow-lg hover:shadow-2xl transition-all duration-500 transform hover:-translate-y-2 border border-gray-100">
              <!-- 项目图片 -->
              <div class="relative overflow-hidden bg-gradient-to-br from-purple-100 to-pink-100" :class="idx === 1 ? 'h-64' : 'aspect-video'">
                <ResponsiveImage
                  v-if="portfolio.image_url"
                  :src="portfolio.image_url"
                  :alt="portfolio.title"
                  :aspect-ratio="idx === 1 ? undefined : 'video'"
                  class="w-full h-full object-cover group-hover:scale-110 transition-transform duration-700"
                />
                <div v-else class="w-full h-full bg-gradient-to-br from-purple-200 to-pink-200 flex items-center justify-center">
                  <svg class="w-16 h-16 text-purple-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
                  </svg>
                </div>
                
                <!-- 渐变遮罩 -->
                <div class="absolute inset-0 bg-gradient-to-t from-black/80 via-black/20 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
                
                <!-- 特色标签 -->
                <div v-if="idx === 0" class="absolute top-4 left-4 px-3 py-1 bg-purple-600 text-white text-xs font-bold rounded-full">
                  精选
                </div>
              </div>
              
              <!-- 项目信息 -->
              <div class="p-6 space-y-4 bg-white">
                <div class="flex items-start justify-between">
                  <h3 class="text-xl font-bold text-gray-900 group-hover:text-purple-600 transition-colors">
                    {{ portfolio.title }}
                  </h3>
                  <svg class="w-5 h-5 text-gray-400 group-hover:text-purple-600 group-hover:translate-x-1 transition-all" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
                  </svg>
                </div>
                <p class="text-gray-600 text-sm leading-relaxed" :class="idx === 1 ? '' : 'line-clamp-2'">
                  {{ portfolio.description || '暂无描述' }}
                </p>
                
                <!-- 技术栈标签 -->
                <div class="flex flex-wrap gap-2 pt-2">
                  <span 
                    v-for="tech in portfolio.tech_stack.slice(0, 3)" 
                    :key="tech"
                    class="px-3 py-1 bg-gradient-to-r from-purple-50 to-pink-50 text-purple-700 text-xs font-medium rounded-full border border-purple-100"
                  >
                    {{ tech }}
                  </span>
                  <span 
                    v-if="portfolio.tech_stack.length > 3"
                    class="px-3 py-1 bg-gray-100 text-gray-600 text-xs font-medium rounded-full"
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
          <div v-if="featuredPortfolios.length > 0" class="text-center">
            <router-link 
              to="/portfolio" 
              class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            >
              查看所有作品
              <svg class="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 最新产品预览 - 优化间距和布局 -->
    <section class="py-16 md:py-20 lg:py-24 bg-gradient-to-br from-indigo-900 via-purple-900 to-pink-900 text-white relative overflow-hidden">
      <!-- 动态背景 - 优化透明度 -->
      <div class="absolute inset-0 opacity-20 md:opacity-30">
        <div class="absolute top-0 left-0 w-full h-full bg-[radial-gradient(circle_at_50%_50%,rgba(255,255,255,0.1),transparent_50%)]"></div>
      </div>
      
      <ResponsiveContainer size="xl" class="relative z-10">
        <div class="text-center mb-12 md:mb-16">
          <div class="inline-block mb-3 md:mb-4">
            <span class="text-xs md:text-sm font-bold text-pink-400 uppercase tracking-wider">Products</span>
          </div>
          <h2 class="text-4xl sm:text-5xl md:text-6xl font-black mb-4 md:mb-6 leading-tight">
            在线<span class="bg-gradient-to-r from-pink-400 to-yellow-400 bg-clip-text text-transparent">产品</span>
          </h2>
          <p class="text-base md:text-lg text-white/80 max-w-2xl mx-auto px-4">
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
              <div class="h-full bg-white/10 backdrop-blur-xl rounded-2xl border border-white/20 overflow-hidden shadow-2xl hover:bg-white/20 transition-all duration-500 transform hover:-translate-y-2 hover:scale-[1.02]">
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
                <div class="absolute inset-0 bg-gradient-to-t from-black/70 via-black/20 to-black/0 opacity-0 group-hover:opacity-100 transition-all duration-500 flex items-center justify-center">
                  <div class="transform translate-y-4 group-hover:translate-y-0 transition-transform duration-500">
                    <div class="bg-white rounded-full p-5 shadow-2xl transform scale-90 group-hover:scale-100 transition-transform duration-300 ring-4 ring-white/50">
                      <svg class="w-8 h-8 text-indigo-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14.828 14.828a4 4 0 01-5.656 0M9 10h1m4 0h1m-6 4h1m4 0h1m6-6V7a2 2 0 00-2-2H5a2 2 0 00-2 2v3m2 13h10a2 2 0 002-2v-3m-2-13h10a2 2 0 012 2v3" />
                      </svg>
                    </div>
                  </div>
                </div>
              </div>
              
              <!-- 产品信息 -->
              <div class="p-6 space-y-4">
                <h3 class="text-xl font-bold text-white group-hover:text-pink-300 transition-colors">
                  {{ product.title }}
                </h3>
                <p class="text-white/70 text-sm leading-relaxed line-clamp-2">
                  {{ product.description || '暂无描述' }}
                </p>
                
                <!-- 技术栈标签 -->
                <div class="flex flex-wrap gap-2">
                  <span 
                    v-for="tech in product.tech_stack?.slice(0, 3)" 
                    :key="tech"
                    class="px-3 py-1 bg-white/20 backdrop-blur-sm text-white text-xs font-medium rounded-full border border-white/30"
                  >
                    {{ tech }}
                  </span>
                  <span 
                    v-if="product.tech_stack && product.tech_stack.length > 3"
                    class="px-3 py-1 bg-white/10 text-white/60 text-xs font-medium rounded-full"
                  >
                    +{{ product.tech_stack.length - 3 }}
                  </span>
                </div>
                
                <!-- 产品统计 -->
                <div class="flex items-center justify-between pt-3 border-t border-white/20">
                  <div class="flex items-center gap-1.5 text-xs text-white/60">
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
              :to="{ path: '/portfolio', query: { tab: 'products' } }" 
              class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-indigo-600 to-purple-600 hover:from-indigo-700 hover:to-purple-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            >
              查看所有产品
              <svg class="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 最新博客预览 - 优化布局 -->
    <section class="py-16 md:py-20 lg:py-24 bg-gray-50">
      <ResponsiveContainer size="xl">
        <div class="text-center mb-10 md:mb-12">
          <div class="inline-block mb-3 md:mb-4">
            <span class="text-xs md:text-sm font-bold text-blue-600 uppercase tracking-wider">Blog</span>
          </div>
          <h2 class="text-4xl sm:text-5xl md:text-6xl font-black text-gray-900 mb-4 md:mb-6 leading-tight">
            最新<span class="bg-gradient-to-r from-blue-600 to-cyan-600 bg-clip-text text-transparent">博客</span>
          </h2>
          <p class="text-base md:text-lg text-gray-600 max-w-2xl mx-auto px-4">
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
            class="bg-white rounded-xl shadow-md hover:shadow-2xl transition-all duration-500 overflow-hidden group cursor-pointer transform hover:-translate-y-3 hover:scale-[1.02] border border-gray-100 hover:border-primary-200"
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
              class="inline-flex items-center px-8 py-4 bg-gradient-to-r from-blue-600 to-cyan-600 hover:from-blue-700 hover:to-cyan-700 text-white font-semibold rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 transform hover:scale-105"
            >
              查看所有博客
              <svg class="w-5 h-5 ml-2 transform group-hover:translate-x-1 transition-transform" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17 8l4 4m0 0l-4 4m4-4H3" />
              </svg>
            </router-link>
          </div>
        </ErrorBoundary>
      </ResponsiveContainer>
    </section>
    
    <!-- 联系我区域 - 优化布局和间距 -->
    <section class="py-16 md:py-20 lg:py-24 bg-gradient-to-br from-primary-600 via-blue-600 to-indigo-600 text-white relative overflow-hidden">
      <!-- 背景装饰 - 优化透明度 -->
      <div class="absolute inset-0 opacity-10 md:opacity-20">
        <div class="absolute top-0 left-0 w-64 h-64 bg-white rounded-full blur-3xl"></div>
        <div class="absolute bottom-0 right-0 w-96 h-96 bg-white rounded-full blur-3xl"></div>
      </div>
      
      <ResponsiveContainer size="lg" class="relative z-10">
        <div class="text-center px-4">
          <h2 class="text-3xl sm:text-4xl md:text-5xl font-black mb-4 md:mb-6 text-white drop-shadow-lg">
            让我们一起创造
          </h2>
          <p class="text-base md:text-lg lg:text-xl mb-8 md:mb-10 opacity-95 max-w-2xl mx-auto drop-shadow-md leading-relaxed">
            有想法？有项目？或者只是想聊聊技术？
            <br class="hidden sm:block">
            随时欢迎与我联系，让我们一起把想法变成现实。
          </p>
          <div class="flex flex-col sm:flex-row gap-4 justify-center items-center">
            <router-link to="/about" class="w-full sm:w-auto bg-white text-primary-600 hover:bg-gray-50 font-semibold transition-all duration-300 shadow-xl hover:shadow-2xl transform hover:scale-105 rounded-xl px-8 py-4 text-base md:text-lg">
              联系我
            </router-link>
            <a 
              href="mailto:hello@august.lab" 
              class="w-full sm:w-auto border-2 border-white text-white hover:bg-white hover:text-primary-600 font-semibold transition-all duration-300 shadow-xl hover:shadow-2xl transform hover:scale-105 rounded-xl px-8 py-4 text-base md:text-lg"
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