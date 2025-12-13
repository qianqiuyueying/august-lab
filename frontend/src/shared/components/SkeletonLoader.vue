<template>
  <div class="skeleton-loader" :class="containerClass">
    <!-- 卡片骨架屏 -->
    <div v-if="type === 'card'" class="skeleton-card">
      <div class="skeleton-image" v-if="showImage"></div>
      <div class="skeleton-content">
        <div class="skeleton-title"></div>
        <div class="skeleton-text" v-for="n in textLines" :key="n"></div>
        <div class="skeleton-actions" v-if="showActions">
          <div class="skeleton-button" v-for="n in actionCount" :key="n"></div>
        </div>
      </div>
    </div>

    <!-- 列表骨架屏 -->
    <div v-else-if="type === 'list'" class="skeleton-list">
      <div v-for="n in count" :key="n" class="skeleton-list-item">
        <div class="skeleton-avatar" v-if="showAvatar"></div>
        <div class="skeleton-list-content">
          <div class="skeleton-title"></div>
          <div class="skeleton-text" v-for="i in textLines" :key="i"></div>
        </div>
        <div class="skeleton-meta" v-if="showMeta">
          <div class="skeleton-tag" v-for="i in 2" :key="i"></div>
        </div>
      </div>
    </div>

    <!-- 表格骨架屏 -->
    <div v-else-if="type === 'table'" class="skeleton-table">
      <div class="skeleton-table-header">
        <div v-for="n in columns" :key="n" class="skeleton-table-cell"></div>
      </div>
      <div v-for="n in rows" :key="n" class="skeleton-table-row">
        <div v-for="i in columns" :key="i" class="skeleton-table-cell"></div>
      </div>
    </div>

    <!-- 文章骨架屏 -->
    <div v-else-if="type === 'article'" class="skeleton-article">
      <div class="skeleton-article-header">
        <div class="skeleton-title large"></div>
        <div class="skeleton-meta-info">
          <div class="skeleton-tag" v-for="n in 3" :key="n"></div>
        </div>
      </div>
      <div class="skeleton-image large" v-if="showImage"></div>
      <div class="skeleton-article-content">
        <div class="skeleton-text" v-for="n in 8" :key="n" :style="getRandomWidth()"></div>
      </div>
    </div>

    <!-- 自定义骨架屏 -->
    <div v-else class="skeleton-custom">
      <slot></slot>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'

interface Props {
  type?: 'card' | 'list' | 'table' | 'article' | 'custom'
  count?: number
  showImage?: boolean
  showAvatar?: boolean
  showActions?: boolean
  showMeta?: boolean
  textLines?: number
  actionCount?: number
  columns?: number
  rows?: number
  animated?: boolean
  theme?: 'light' | 'dark'
}

const props = withDefaults(defineProps<Props>(), {
  type: 'card',
  count: 3,
  showImage: true,
  showAvatar: false,
  showActions: true,
  showMeta: true,
  textLines: 3,
  actionCount: 2,
  columns: 4,
  rows: 5,
  animated: true,
  theme: 'light'
})

const containerClass = computed(() => [
  `skeleton-${props.theme}`,
  {
    'skeleton-animated': props.animated
  }
])

const getRandomWidth = () => {
  const widths = ['100%', '95%', '90%', '85%', '80%', '75%']
  return { width: widths[Math.floor(Math.random() * widths.length)] }
}
</script>

<style scoped>
.skeleton-loader {
  @apply w-full;
}

/* 基础骨架样式 */
.skeleton-loader * {
  @apply bg-gray-200 rounded animate-pulse;
}

.skeleton-dark * {
  @apply bg-gray-700;
}

.skeleton-animated * {
  animation: skeleton-loading 1.5s ease-in-out infinite;
}

@keyframes skeleton-loading {
  0% {
    opacity: 1;
  }
  50% {
    opacity: 0.4;
  }
  100% {
    opacity: 1;
  }
}

/* 卡片骨架屏 */
.skeleton-card {
  @apply border border-gray-200 rounded-lg p-4 space-y-4;
}

.skeleton-dark .skeleton-card {
  @apply border-gray-600;
}

.skeleton-image {
  @apply w-full h-48 rounded;
}

.skeleton-image.large {
  @apply h-64;
}

.skeleton-content {
  @apply space-y-3;
}

.skeleton-title {
  @apply h-6 w-3/4 rounded;
}

.skeleton-title.large {
  @apply h-8 w-full;
}

.skeleton-text {
  @apply h-4 rounded;
}

.skeleton-text:nth-child(odd) {
  @apply w-full;
}

.skeleton-text:nth-child(even) {
  @apply w-5/6;
}

.skeleton-actions {
  @apply flex space-x-2 pt-2;
}

.skeleton-button {
  @apply h-8 w-20 rounded;
}

/* 列表骨架屏 */
.skeleton-list {
  @apply space-y-4;
}

.skeleton-list-item {
  @apply flex items-center space-x-4 p-4 border border-gray-200 rounded-lg;
}

.skeleton-dark .skeleton-list-item {
  @apply border-gray-600;
}

.skeleton-avatar {
  @apply w-12 h-12 rounded-full flex-shrink-0;
}

.skeleton-list-content {
  @apply flex-1 space-y-2;
}

.skeleton-meta {
  @apply flex space-x-2;
}

.skeleton-tag {
  @apply h-6 w-16 rounded-full;
}

/* 表格骨架屏 */
.skeleton-table {
  @apply border border-gray-200 rounded-lg overflow-hidden;
}

.skeleton-dark .skeleton-table {
  @apply border-gray-600;
}

.skeleton-table-header {
  @apply flex bg-gray-50 p-4 space-x-4;
}

.skeleton-dark .skeleton-table-header {
  @apply bg-gray-800;
}

.skeleton-table-row {
  @apply flex p-4 space-x-4 border-t border-gray-200;
}

.skeleton-dark .skeleton-table-row {
  @apply border-gray-600;
}

.skeleton-table-cell {
  @apply h-4 flex-1 rounded;
}

/* 文章骨架屏 */
.skeleton-article {
  @apply space-y-6;
}

.skeleton-article-header {
  @apply space-y-4;
}

.skeleton-meta-info {
  @apply flex space-x-2;
}

.skeleton-article-content {
  @apply space-y-3;
}

/* 响应式适配 */
@media (max-width: 768px) {
  .skeleton-card {
    @apply p-3;
  }
  
  .skeleton-image {
    @apply h-32;
  }
  
  .skeleton-list-item {
    @apply p-3;
  }
  
  .skeleton-table-header,
  .skeleton-table-row {
    @apply p-3 space-x-2;
  }
}

@media (max-width: 480px) {
  .skeleton-actions {
    @apply flex-col space-y-2 space-x-0;
  }
  
  .skeleton-button {
    @apply w-full;
  }
  
  .skeleton-meta {
    @apply flex-wrap;
  }
}
</style>