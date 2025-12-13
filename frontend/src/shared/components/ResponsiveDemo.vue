<!--
响应式布局演示组件
用于展示和测试响应式功能
-->

<template>
  <ResponsiveContainer size="xl" class="section-padding">
    <div class="space-y-12">
      <!-- 标题 -->
      <div class="text-center">
        <h1 class="heading-1 mb-4">响应式布局演示</h1>
        <p class="text-responsive-lg text-gray-600 max-w-3xl mx-auto">
          展示各种响应式组件和布局的使用效果
        </p>
      </div>
      
      <!-- 当前断点信息 -->
      <div class="card-responsive text-center">
        <h2 class="heading-4 mb-4">当前断点信息</h2>
        <div class="grid-responsive-4 text-center">
          <div class="stat-card">
            <div class="text-2xl font-bold text-primary-600">{{ currentBreakpoint }}</div>
            <div class="text-sm text-gray-500">当前断点</div>
          </div>
          <div class="stat-card">
            <div class="text-2xl font-bold text-primary-600">{{ windowWidth }}px</div>
            <div class="text-sm text-gray-500">窗口宽度</div>
          </div>
          <div class="stat-card">
            <div class="text-2xl font-bold text-primary-600">{{ deviceType }}</div>
            <div class="text-sm text-gray-500">设备类型</div>
          </div>
          <div class="stat-card">
            <div class="text-2xl font-bold text-primary-600">{{ isPortrait ? '竖屏' : '横屏' }}</div>
            <div class="text-sm text-gray-500">屏幕方向</div>
          </div>
        </div>
      </div>
      
      <!-- 响应式网格演示 -->
      <section>
        <h2 class="heading-3 mb-6">响应式网格</h2>
        
        <!-- 自动网格 -->
        <div class="mb-8">
          <h3 class="heading-5 mb-4">自动网格 (1-2-3-4-5-6列)</h3>
          <ResponsiveGrid preset="auto" class="mb-4">
            <div v-for="i in 12" :key="i" class="card-responsive-hover text-center">
              <div class="text-lg font-semibold text-primary-600">{{ i }}</div>
              <div class="text-sm text-gray-500">网格项目</div>
            </div>
          </ResponsiveGrid>
        </div>
        
        <!-- 卡片网格 -->
        <div class="mb-8">
          <h3 class="heading-5 mb-4">卡片网格 (1-2-3-4列)</h3>
          <ResponsiveGrid preset="cards">
            <div v-for="i in 8" :key="i" class="card-responsive-hover">
              <div class="w-full h-32 bg-gradient-to-br from-primary-400 to-primary-600 rounded-lg mb-4"></div>
              <h4 class="font-semibold text-gray-900 mb-2">卡片标题 {{ i }}</h4>
              <p class="text-sm text-gray-600">这是一个响应式卡片的描述内容。</p>
            </div>
          </ResponsiveGrid>
        </div>
        
        <!-- 自定义网格 -->
        <div class="mb-8">
          <h3 class="heading-5 mb-4">自定义网格配置</h3>
          <ResponsiveGrid 
            :cols="{ xs: 1, sm: 2, md: 3, lg: 4, xl: 6 }"
            :responsive-gap="{ xs: '1rem', sm: '1.5rem', lg: '2rem' }"
          >
            <div v-for="i in 12" :key="i" class="card-responsive text-center">
              <div class="w-8 h-8 bg-primary-600 rounded-full mx-auto mb-2"></div>
              <div class="text-sm font-medium">项目 {{ i }}</div>
            </div>
          </ResponsiveGrid>
        </div>
      </section>
      
      <!-- 响应式图片演示 -->
      <section>
        <h2 class="heading-3 mb-6">响应式图片</h2>
        <ResponsiveGrid preset="features">
          <div class="card-responsive">
            <h3 class="heading-5 mb-4">正方形图片</h3>
            <ResponsiveImage
              src="https://picsum.photos/400/400"
              alt="正方形示例图片"
              aspect-ratio="square"
              rounded="lg"
              class="mb-4"
            />
            <p class="text-sm text-gray-600">1:1 宽高比的正方形图片</p>
          </div>
          
          <div class="card-responsive">
            <h3 class="heading-5 mb-4">视频比例图片</h3>
            <ResponsiveImage
              src="https://picsum.photos/800/450"
              alt="视频比例示例图片"
              aspect-ratio="video"
              rounded="lg"
              class="mb-4"
            />
            <p class="text-sm text-gray-600">16:9 宽高比的视频比例图片</p>
          </div>
          
          <div class="card-responsive">
            <h3 class="heading-5 mb-4">肖像比例图片</h3>
            <ResponsiveImage
              src="https://picsum.photos/300/400"
              alt="肖像比例示例图片"
              aspect-ratio="portrait"
              rounded="lg"
              class="mb-4"
            />
            <p class="text-sm text-gray-600">3:4 宽高比的肖像比例图片</p>
          </div>
        </ResponsiveGrid>
      </section>
      
      <!-- 响应式文本演示 -->
      <section>
        <h2 class="heading-3 mb-6">响应式文本</h2>
        <div class="space-y-6">
          <div class="card-responsive">
            <h1 class="heading-1 mb-2">主标题 (H1)</h1>
            <h2 class="heading-2 mb-2">副标题 (H2)</h2>
            <h3 class="heading-3 mb-2">三级标题 (H3)</h3>
            <h4 class="heading-4 mb-2">四级标题 (H4)</h4>
            <h5 class="heading-5 mb-2">五级标题 (H5)</h5>
            <h6 class="heading-6 mb-4">六级标题 (H6)</h6>
            
            <p class="text-responsive-lg mb-4">
              这是一个响应式的大号段落文本，会根据屏幕尺寸自动调整字体大小。
            </p>
            <p class="text-responsive-base mb-4">
              这是一个响应式的普通段落文本，在不同设备上有不同的显示效果。
            </p>
            <p class="text-responsive-sm">
              这是一个响应式的小号段落文本，适合用作辅助说明文字。
            </p>
          </div>
        </div>
      </section>
      
      <!-- 响应式布局演示 -->
      <section>
        <h2 class="heading-3 mb-6">响应式布局</h2>
        
        <!-- Flexbox 布局 -->
        <div class="mb-8">
          <h3 class="heading-5 mb-4">响应式 Flexbox</h3>
          <div class="card-responsive">
            <div class="flex-responsive gap-responsive">
              <div class="flex-1 bg-primary-100 padding-responsive rounded-lg">
                <h4 class="font-semibold text-primary-800 mb-2">主要内容</h4>
                <p class="text-primary-700">这个区域在移动端会堆叠显示，在桌面端会并排显示。</p>
              </div>
              <div class="w-full sm:w-80 bg-gray-100 padding-responsive rounded-lg">
                <h4 class="font-semibold text-gray-800 mb-2">侧边栏</h4>
                <p class="text-gray-700">这是一个固定宽度的侧边栏区域。</p>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 侧边栏布局 -->
        <div class="mb-8">
          <h3 class="heading-5 mb-4">侧边栏布局</h3>
          <div class="card-responsive">
            <div class="sidebar-layout">
              <div class="sidebar-main">
                <h4 class="heading-5 mb-4">主要内容区域</h4>
                <p class="text-gray-600 mb-4">
                  这是主要内容区域，在大屏幕上占据大部分空间，在小屏幕上会堆叠在侧边栏下方。
                </p>
                <div class="grid-responsive-2 gap-4">
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h5 class="font-semibold mb-2">内容块 1</h5>
                    <p class="text-sm text-gray-600">这是一个内容块的示例。</p>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h5 class="font-semibold mb-2">内容块 2</h5>
                    <p class="text-sm text-gray-600">这是另一个内容块的示例。</p>
                  </div>
                </div>
              </div>
              <div class="sidebar-aside">
                <h4 class="heading-5 mb-4">侧边栏</h4>
                <div class="space-y-4">
                  <div class="bg-primary-50 p-4 rounded-lg">
                    <h5 class="font-semibold text-primary-800 mb-2">相关链接</h5>
                    <ul class="space-y-1 text-sm text-primary-700">
                      <li><a href="#" class="hover:underline">链接 1</a></li>
                      <li><a href="#" class="hover:underline">链接 2</a></li>
                      <li><a href="#" class="hover:underline">链接 3</a></li>
                    </ul>
                  </div>
                  <div class="bg-gray-50 p-4 rounded-lg">
                    <h5 class="font-semibold text-gray-800 mb-2">其他信息</h5>
                    <p class="text-sm text-gray-600">这里可以放置一些额外的信息或广告内容。</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
      
      <!-- 响应式显示/隐藏演示 -->
      <section>
        <h2 class="heading-3 mb-6">响应式显示/隐藏</h2>
        <div class="card-responsive">
          <div class="space-y-4">
            <div class="show-mobile bg-red-100 text-red-800 p-4 rounded-lg">
              <strong>移动端显示：</strong>这个内容只在移动端显示 (< 768px)
            </div>
            <div class="show-tablet bg-yellow-100 text-yellow-800 p-4 rounded-lg">
              <strong>平板端显示：</strong>这个内容只在平板端显示 (768px - 1024px)
            </div>
            <div class="show-desktop bg-green-100 text-green-800 p-4 rounded-lg">
              <strong>桌面端显示：</strong>这个内容只在桌面端显示 (≥ 768px)
            </div>
          </div>
        </div>
      </section>
    </div>
  </ResponsiveContainer>
</template>

<script setup lang="ts">
import ResponsiveContainer from './ResponsiveContainer.vue'
import ResponsiveGrid from './ResponsiveGrid.vue'
import ResponsiveImage from './ResponsiveImage.vue'
import { useResponsive } from '../composables/useResponsive'

const {
  currentBreakpoint,
  windowWidth,
  deviceType,
  isPortrait,
} = useResponsive()
</script>