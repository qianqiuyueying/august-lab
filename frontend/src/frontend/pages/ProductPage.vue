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
  return typeof id === 'string' ? parseInt(id, 10) : id
})
</script>

<style scoped>
.product-page {
  height: 100vh;
  overflow: hidden;
}
</style>