<template>
  <div class="blog-preview">
    <div v-if="blog" class="max-w-4xl mx-auto">
      <!-- 博客头部 -->
      <header class="mb-8">
        <h1 class="text-3xl font-bold text-gray-900 mb-4">{{ blog.title }}</h1>
        
        <div class="flex flex-wrap items-center gap-4 text-sm text-gray-600 mb-4">
          <div class="flex items-center">
            <el-icon class="mr-1"><Calendar /></el-icon>
            <span>{{ formatDate(blog.published_at || blog.created_at) }}</span>
          </div>
          
          <div class="flex items-center">
            <el-icon class="mr-1"><Clock /></el-icon>
            <span>{{ blog.reading_time || 1 }} 分钟阅读</span>
          </div>
          
          <div class="flex items-center">
            <el-icon class="mr-1"><View /></el-icon>
            <span>预览模式</span>
          </div>
        </div>
        
        <!-- 标签 -->
        <div v-if="blog.tags && blog.tags.length > 0" class="flex flex-wrap gap-2 mb-6">
          <el-tag 
            v-for="tag in blog.tags" 
            :key="tag" 
            type="primary"
            effect="plain"
          >
            {{ tag }}
          </el-tag>
        </div>
        
        <!-- 摘要 -->
        <div v-if="blog.excerpt" class="text-lg text-gray-700 leading-relaxed mb-8 p-4 bg-gray-50 rounded-lg border-l-4 border-primary-500">
          {{ blog.excerpt }}
        </div>
      </header>
      
      <!-- 博客内容 -->
      <article class="prose prose-lg max-w-none">
        <div class="markdown-content" v-html="renderedContent"></div>
      </article>
      
      <!-- 博客底部信息 -->
      <footer class="mt-12 pt-8 border-t border-gray-200">
        <div class="flex flex-wrap items-center justify-between gap-4">
          <div class="text-sm text-gray-500">
            <p>创建时间：{{ formatDate(blog.created_at) }}</p>
            <p v-if="blog.updated_at && blog.updated_at !== blog.created_at">
              更新时间：{{ formatDate(blog.updated_at) }}
            </p>
          </div>
          
          <div class="flex items-center space-x-4">
            <el-tag :type="blog.is_published ? 'success' : 'warning'">
              {{ blog.is_published ? '已发布' : '草稿' }}
            </el-tag>
            
            <div class="text-sm text-gray-500">
              字数：{{ contentWordCount }}
            </div>
          </div>
        </div>
        
        <!-- SEO信息（仅在有SEO设置时显示） -->
        <div v-if="hasSeoInfo" class="mt-6 p-4 bg-blue-50 rounded-lg">
          <h3 class="text-sm font-medium text-blue-900 mb-2">SEO 信息</h3>
          <div class="space-y-2 text-sm">
            <div v-if="blog.seo_title">
              <span class="font-medium text-blue-800">SEO标题：</span>
              <span class="text-blue-700">{{ blog.seo_title }}</span>
            </div>
            <div v-if="blog.seo_description">
              <span class="font-medium text-blue-800">SEO描述：</span>
              <span class="text-blue-700">{{ blog.seo_description }}</span>
            </div>
            <div v-if="blog.seo_keywords">
              <span class="font-medium text-blue-800">SEO关键词：</span>
              <span class="text-blue-700">{{ blog.seo_keywords }}</span>
            </div>
          </div>
        </div>
      </footer>
    </div>
    
    <div v-else class="text-center py-12">
      <el-icon size="64" class="text-gray-300 mb-4"><Document /></el-icon>
      <p class="text-gray-500">暂无预览内容</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { Calendar, Clock, View, Document } from '@element-plus/icons-vue'
import type { Blog } from '../../shared/types'

interface Props {
  blog?: Blog | null
}

const props = withDefaults(defineProps<Props>(), {
  blog: null
})

const renderedContent = computed(() => {
  if (!props.blog?.content) return ''
  
  try {
    // marked 在同步模式下返回 string，使用类型断言确保类型正确
    const html = marked(props.blog.content) as string
    return DOMPurify.sanitize(html)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return '<p class="text-red-500">内容渲染失败</p>'
  }
})

const contentWordCount = computed(() => {
  if (!props.blog?.content) return 0
  // 简单的中文字符计数
  const chineseChars = (props.blog.content.match(/[\u4e00-\u9fa5]/g) || []).length
  const englishWords = (props.blog.content.match(/[a-zA-Z]+/g) || []).length
  return chineseChars + englishWords
})

const hasSeoInfo = computed(() => {
  return props.blog?.seo_title || props.blog?.seo_description || props.blog?.seo_keywords
})

const formatDate = (dateString: string) => {
  if (!dateString) return ''
  const date = new Date(dateString)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>

<style scoped>
.blog-preview {
  min-height: 400px;
}

.prose {
  color: #374151;
  max-width: none;
}

.markdown-content :deep(h1),
.markdown-content :deep(h2),
.markdown-content :deep(h3),
.markdown-content :deep(h4),
.markdown-content :deep(h5),
.markdown-content :deep(h6) {
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-weight: 600;
  line-height: 1.25;
  color: #111827;
}

.markdown-content :deep(h1) {
  font-size: 2.25rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.markdown-content :deep(h2) {
  font-size: 1.875rem;
  border-bottom: 1px solid #e5e7eb;
  padding-bottom: 0.5rem;
}

.markdown-content :deep(h3) {
  font-size: 1.5rem;
}

.markdown-content :deep(h4) {
  font-size: 1.25rem;
}

.markdown-content :deep(p) {
  margin-bottom: 1rem;
  line-height: 1.75;
}

.markdown-content :deep(ul),
.markdown-content :deep(ol) {
  margin-bottom: 1rem;
  padding-left: 2rem;
}

.markdown-content :deep(li) {
  margin-bottom: 0.5rem;
  line-height: 1.75;
}

.markdown-content :deep(blockquote) {
  margin: 1.5rem 0;
  padding: 0 1rem;
  color: #6b7280;
  border-left: 4px solid #d1d5db;
  font-style: italic;
}

.markdown-content :deep(code) {
  padding: 0.125rem 0.25rem;
  font-size: 0.875rem;
  background-color: #f3f4f6;
  border-radius: 0.25rem;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
}

.markdown-content :deep(pre) {
  margin: 1.5rem 0;
  padding: 1rem;
  background-color: #1f2937;
  color: #f9fafb;
  border-radius: 0.5rem;
  overflow-x: auto;
  font-size: 0.875rem;
  line-height: 1.5;
}

.markdown-content :deep(pre code) {
  background-color: transparent;
  padding: 0;
  color: inherit;
}

.markdown-content :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 0.5rem;
  margin: 1.5rem 0;
}

.markdown-content :deep(table) {
  width: 100%;
  margin: 1.5rem 0;
  border-collapse: collapse;
}

.markdown-content :deep(th),
.markdown-content :deep(td) {
  padding: 0.75rem;
  text-align: left;
  border-bottom: 1px solid #e5e7eb;
}

.markdown-content :deep(th) {
  background-color: #f9fafb;
  font-weight: 600;
}

.markdown-content :deep(a) {
  color: #3b82f6;
  text-decoration: underline;
}

.markdown-content :deep(a:hover) {
  color: #1d4ed8;
}

.markdown-content :deep(hr) {
  margin: 2rem 0;
  border: none;
  border-top: 1px solid #e5e7eb;
}
</style>