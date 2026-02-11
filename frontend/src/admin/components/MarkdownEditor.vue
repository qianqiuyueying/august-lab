<template>
  <div class="markdown-editor">
    <div class="editor-toolbar">
      <div class="toolbar-left">
        <el-button-group>
          <el-button 
            :type="mode === 'edit' ? 'primary' : 'default'"
            size="small"
            @click="mode = 'edit'"
          >
            <el-icon><Edit /></el-icon>
            编辑
          </el-button>
          <el-button 
            :type="mode === 'preview' ? 'primary' : 'default'"
            size="small"
            @click="mode = 'preview'"
          >
            <el-icon><View /></el-icon>
            预览
          </el-button>
          <el-button 
            :type="mode === 'split' ? 'primary' : 'default'"
            size="small"
            @click="mode = 'split'"
          >
            <el-icon><Operation /></el-icon>
            分屏
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-right">
        <el-button-group>
          <el-button size="small" @click="insertMarkdown('**', '**')" title="粗体">
            <strong>B</strong>
          </el-button>
          <el-button size="small" @click="insertMarkdown('*', '*')" title="斜体">
            <em>I</em>
          </el-button>
          <el-button size="small" @click="insertMarkdown('`', '`')" title="代码">
            <el-icon><Tickets /></el-icon>
          </el-button>
          <el-button size="small" @click="insertMarkdown('[', '](url)')" title="链接">
            <el-icon><Link /></el-icon>
          </el-button>
          <el-button size="small" @click="insertMarkdown('![', '](url)')" title="图片">
            <el-icon><Picture /></el-icon>
          </el-button>
        </el-button-group>
      </div>
    </div>
    
    <div class="editor-content" :class="mode">
      <!-- 编辑区域 -->
      <div v-show="mode === 'edit' || mode === 'split'" class="editor-pane">
        <el-input
          ref="textareaRef"
          v-model="content"
          type="textarea"
          :placeholder="placeholder"
          :rows="20"
          resize="none"
          @input="handleInput"
          @keydown="handleKeydown"
        />
      </div>
      
      <!-- 预览区域 -->
      <div v-show="mode === 'preview' || mode === 'split'" class="preview-pane">
        <div class="markdown-body" v-html="renderedContent"></div>
      </div>
    </div>
    
    <div class="editor-footer">
      <div class="word-count">
        字符数: {{ content.length }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick } from 'vue'
import { marked } from 'marked'
import DOMPurify from 'dompurify'
import { 
  Edit, 
  View, 
  Operation, 
  Tickets, 
  Link, 
  Picture 
} from '@element-plus/icons-vue'

interface Props {
  modelValue?: string
  placeholder?: string
}

interface Emits {
  (e: 'update:modelValue', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '请输入内容...'
})

const emit = defineEmits<Emits>()

const textareaRef = ref()
const mode = ref<'edit' | 'preview' | 'split'>('edit')

const content = computed({
  get: () => props.modelValue,
  set: (value: string) => emit('update:modelValue', value)
})

const renderedContent = computed(() => {
  if (!content.value) return '<p class="empty-content">暂无内容</p>'
  
  try {
    // marked 在同步模式下返回 string，使用类型断言确保类型正确
    const html = marked(content.value) as string
    return DOMPurify.sanitize(html)
  } catch (error) {
    console.error('Markdown渲染失败:', error)
    return '<p class="error-content">内容渲染失败</p>'
  }
})

const handleInput = (value: string) => {
  content.value = value
}

const handleKeydown = (event: KeyboardEvent) => {
  // Tab键插入缩进
  if (event.key === 'Tab') {
    event.preventDefault()
    insertText('  ')
  }
  
  // Ctrl+B 粗体
  if (event.ctrlKey && event.key === 'b') {
    event.preventDefault()
    insertMarkdown('**', '**')
  }
  
  // Ctrl+I 斜体
  if (event.ctrlKey && event.key === 'i') {
    event.preventDefault()
    insertMarkdown('*', '*')
  }
}

const insertText = (text: string) => {
  const textarea = textareaRef.value?.textarea
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const value = content.value
  
  content.value = value.substring(0, start) + text + value.substring(end)
  
  nextTick(() => {
    textarea.focus()
    textarea.setSelectionRange(start + text.length, start + text.length)
  })
}

const insertMarkdown = (prefix: string, suffix: string) => {
  const textarea = textareaRef.value?.textarea
  if (!textarea) return
  
  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const value = content.value
  const selectedText = value.substring(start, end)
  
  const newText = prefix + selectedText + suffix
  content.value = value.substring(0, start) + newText + value.substring(end)
  
  nextTick(() => {
    textarea.focus()
    if (selectedText) {
      // 如果有选中文本，选中插入的内容
      textarea.setSelectionRange(start, start + newText.length)
    } else {
      // 如果没有选中文本，光标定位到前缀后面
      textarea.setSelectionRange(start + prefix.length, start + prefix.length)
    }
  })
}
</script>

<style scoped>
.markdown-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  transition: all 0.3s;
}

.editor-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  transition: background-color 0.3s, border-color 0.3s;
}

.editor-content {
  display: flex;
  min-height: 400px;
  background-color: #fff;
  transition: background-color 0.3s;
}

.editor-content.edit .editor-pane {
  width: 100%;
}

.editor-content.preview .preview-pane {
  width: 100%;
}

.editor-content.split .editor-pane,
.editor-content.split .preview-pane {
  width: 50%;
}

.editor-pane {
  border-right: 1px solid #dcdfe6;
  transition: border-color 0.3s;
}

.editor-pane :deep(.el-textarea__inner) {
  border: none;
  border-radius: 0;
  resize: none;
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 14px;
  line-height: 1.6;
  background-color: transparent;
  color: inherit;
}

.preview-pane {
  padding: 16px;
  overflow-y: auto;
  background-color: #fff;
  transition: background-color 0.3s;
}

.markdown-body {
  line-height: 1.6;
  color: #333;
  transition: color 0.3s;
}

.markdown-body :deep(h1),
.markdown-body :deep(h2),
.markdown-body :deep(h3),
.markdown-body :deep(h4),
.markdown-body :deep(h5),
.markdown-body :deep(h6) {
  margin-top: 24px;
  margin-bottom: 16px;
  font-weight: 600;
  line-height: 1.25;
}

.markdown-body :deep(h1) {
  font-size: 2em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body :deep(h2) {
  font-size: 1.5em;
  border-bottom: 1px solid #eaecef;
  padding-bottom: 0.3em;
}

.markdown-body :deep(p) {
  margin-bottom: 16px;
}

.markdown-body :deep(code) {
  padding: 0.2em 0.4em;
  margin: 0;
  font-size: 85%;
  background-color: rgba(175, 184, 193, 0.2);
  border-radius: 6px;
}

.markdown-body :deep(pre) {
  padding: 16px;
  overflow: auto;
  font-size: 85%;
  line-height: 1.45;
  background-color: #f6f8fa;
  border-radius: 6px;
  margin-bottom: 16px;
}

.markdown-body :deep(blockquote) {
  padding: 0 1em;
  color: #6a737d;
  border-left: 0.25em solid #dfe2e5;
  margin-bottom: 16px;
}

.markdown-body :deep(ul),
.markdown-body :deep(ol) {
  padding-left: 2em;
  margin-bottom: 16px;
}

.markdown-body :deep(li) {
  margin-bottom: 0.25em;
}

.markdown-body :deep(img) {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.markdown-body :deep(table) {
  border-collapse: collapse;
  margin-bottom: 16px;
  width: 100%;
}

.markdown-body :deep(th),
.markdown-body :deep(td) {
  padding: 6px 13px;
  border: 1px solid #dfe2e5;
}

.markdown-body :deep(th) {
  background-color: #f6f8fa;
  font-weight: 600;
}

.empty-content,
.error-content {
  color: #909399;
  text-align: center;
  padding: 40px 20px;
  font-style: italic;
}

.error-content {
  color: #f56c6c;
}

.editor-footer {
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-top: 1px solid #dcdfe6;
  text-align: right;
  transition: background-color 0.3s, border-color 0.3s;
}

.word-count {
  font-size: 12px;
  color: #909399;
}
</style>

<style>
/* 深色模式：编辑弹窗内预览区域（不受 scoped 覆盖） */
.dark .markdown-editor .preview-pane {
  background-color: var(--lab-bg) !important;
}

.dark .markdown-editor .markdown-body {
  color: var(--lab-text) !important;
}

.dark .markdown-editor .markdown-body h1,
.dark .markdown-editor .markdown-body h2,
.dark .markdown-editor .markdown-body h3,
.dark .markdown-editor .markdown-body h4,
.dark .markdown-editor .markdown-body h5,
.dark .markdown-editor .markdown-body h6 {
  color: var(--lab-text) !important;
  border-bottom-color: var(--lab-border) !important;
}

.dark .markdown-editor .markdown-body p {
  color: var(--lab-text) !important;
}

.dark .markdown-editor .markdown-body code {
  background-color: rgba(255, 255, 255, 0.1) !important;
  color: var(--lab-text) !important;
}

.dark .markdown-editor .markdown-body pre {
  background-color: #161b22 !important;
  color: var(--lab-text) !important;
}

.dark .markdown-editor .markdown-body pre code {
  color: inherit !important;
}

.dark .markdown-editor .markdown-body blockquote {
  color: var(--lab-muted) !important;
  border-left-color: var(--lab-border) !important;
}

.dark .markdown-editor .markdown-body th,
.dark .markdown-editor .markdown-body td {
  border-color: var(--lab-border) !important;
  color: var(--lab-text) !important;
}

.dark .markdown-editor .markdown-body th {
  background-color: #161b22 !important;
}

.dark .markdown-editor .markdown-body a {
  color: var(--lab-accent) !important;
}

.dark .markdown-editor .empty-content,
.dark .markdown-editor .error-content {
  color: var(--lab-muted) !important;
}

.dark .markdown-editor .error-content {
  color: #f56c6c !important;
}
</style>