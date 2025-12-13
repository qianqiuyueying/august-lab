<template>
  <div class="text-center py-12" :class="containerClass">
    <div class="w-16 h-16 mx-auto mb-4 text-gray-400">
      <slot name="icon">
        <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path 
            stroke-linecap="round" 
            stroke-linejoin="round" 
            stroke-width="2" 
            d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
          />
        </svg>
      </slot>
    </div>
    
    <h3 class="text-lg font-medium text-gray-900 mb-2">
      {{ title || '暂无数据' }}
    </h3>
    
    <p class="text-gray-600 mb-6 max-w-sm mx-auto">
      {{ description || '当前没有任何内容，请稍后再试或添加新内容。' }}
    </p>
    
    <slot name="action">
      <button 
        v-if="actionText && actionHandler"
        @click="actionHandler"
        class="inline-flex items-center px-4 py-2 bg-primary-600 text-white text-sm font-medium rounded-md hover:bg-primary-700 transition-colors duration-200"
      >
        {{ actionText }}
      </button>
    </slot>
  </div>
</template>

<script setup lang="ts">
interface Props {
  title?: string
  description?: string
  actionText?: string
  actionHandler?: () => void
  containerClass?: string
}

defineProps<Props>()
</script>

<script lang="ts">
export default {
  name: 'EmptyState'
}
</script>