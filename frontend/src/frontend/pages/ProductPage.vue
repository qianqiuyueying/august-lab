<template>
  <div class="product-page">
    <!-- 产品容器 -->
    <ProductContainer
      :product-id="productId"
      :show-navbar="true"
      :show-status-bar="true"
      :allow-fullscreen="true"
      :auto-load="true"
    />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { useRoute } from 'vue-router'
import ProductContainer from '../components/product/ProductContainer.vue'

interface Props {
  id?: string | number
}

const props = defineProps<Props>()
const route = useRoute()

// 计算产品ID
const productId = computed(() => {
  // 优先使用props中的id，然后使用路由参数
  const id = props.id || route.params.id
  
  if (id === undefined) {
    return undefined
  }
  
  if (typeof id === 'number') {
    return id
  }
  
  if (typeof id === 'string') {
    const parsed = parseInt(id, 10)
    return isNaN(parsed) ? undefined : parsed
  }
  
  // 处理数组情况（取第一个元素）
  if (Array.isArray(id) && id.length > 0) {
    const firstId = id[0]
    if (typeof firstId === 'string') {
      const parsed = parseInt(firstId, 10)
      return isNaN(parsed) ? undefined : parsed
    }
    return typeof firstId === 'number' ? firstId : undefined
  }
  
  return undefined
})
</script>

<style scoped>
.product-page {
  height: 100vh;
  overflow: hidden;
}
</style>