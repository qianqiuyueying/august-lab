<template>
  <div class="flex items-center justify-center" :class="containerClass">
    <div 
      class="animate-spin rounded-full border-2 border-gray-300 border-t-primary-600"
      :class="spinnerClass"
    ></div>
    <span v-if="text" class="ml-2 text-gray-600" :class="textClass">{{ text }}</span>
  </div>
</template>

<script setup lang="ts">
interface Props {
  size?: 'sm' | 'md' | 'lg'
  text?: string
  containerClass?: string
}

const props = withDefaults(defineProps<Props>(), {
  size: 'md'
})

const spinnerClass = computed(() => {
  const sizeClasses = {
    sm: 'w-4 h-4',
    md: 'w-8 h-8',
    lg: 'w-12 h-12'
  }
  return sizeClasses[props.size]
})

const textClass = computed(() => {
  const sizeClasses = {
    sm: 'text-sm',
    md: 'text-base',
    lg: 'text-lg'
  }
  return sizeClasses[props.size]
})
</script>

<script lang="ts">
import { computed } from 'vue'
export default {
  name: 'LoadingSpinner'
}
</script>