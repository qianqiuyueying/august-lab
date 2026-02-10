<template>
  <div class="relative p-1">
    <!-- 角落装饰 -->
    <div class="absolute top-0 left-0 w-4 h-4 border-t-2 border-l-2 border-lab-accent opacity-80"></div>
    <div class="absolute top-0 right-0 w-4 h-4 border-t-2 border-r-2 border-lab-accent opacity-80"></div>
    <div class="absolute bottom-0 left-0 w-4 h-4 border-b-2 border-l-2 border-lab-accent opacity-80"></div>
    <div class="absolute bottom-0 right-0 w-4 h-4 border-b-2 border-r-2 border-lab-accent opacity-80"></div>
    
    <!-- 中间刻度 -->
    <div class="absolute top-0 left-1/2 -translate-x-1/2 w-8 h-1 bg-lab-accent/20"></div>
    <div class="absolute bottom-0 left-1/2 -translate-x-1/2 w-8 h-1 bg-lab-accent/20"></div>
    <div class="absolute left-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-lab-accent/20"></div>
    <div class="absolute right-0 top-1/2 -translate-y-1/2 w-1 h-8 bg-lab-accent/20"></div>

    <!-- 内容插槽 -->
    <div class="relative z-10">
      <slot></slot>
    </div>
  </div>
</template>
