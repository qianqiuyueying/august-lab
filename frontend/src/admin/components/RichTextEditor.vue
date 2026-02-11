<template>
  <div class="rich-text-editor">
    <!-- 工具栏 -->
    <div class="toolbar">
      <div class="toolbar-group">
        <el-button-group>
          <el-button 
            size="small" 
            @click="execCommand('bold')" 
            :class="{ active: isActive('bold') }"
            title="粗体"
          >
            <strong>B</strong>
          </el-button>
          <el-button 
            size="small" 
            @click="execCommand('italic')" 
            :class="{ active: isActive('italic') }"
            title="斜体"
          >
            <em>I</em>
          </el-button>
          <el-button 
            size="small" 
            @click="execCommand('underline')" 
            :class="{ active: isActive('underline') }"
            title="下划线"
          >
            <u>U</u>
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-group">
        <el-select 
          v-model="currentFontSize" 
          @change="changeFontSize"
          size="small"
          style="width: 80px"
        >
          <el-option label="12px" value="1" />
          <el-option label="14px" value="2" />
          <el-option label="16px" value="3" />
          <el-option label="18px" value="4" />
          <el-option label="24px" value="5" />
          <el-option label="32px" value="6" />
          <el-option label="48px" value="7" />
        </el-select>
      </div>
      
      <div class="toolbar-group">
        <el-button-group>
          <el-button 
            size="small" 
            @click="execCommand('justifyLeft')" 
            :class="{ active: isActive('justifyLeft') }"
            title="左对齐"
          >
            ←
          </el-button>
          <el-button 
            size="small" 
            @click="execCommand('justifyCenter')" 
            :class="{ active: isActive('justifyCenter') }"
            title="居中对齐"
          >
            ↔
          </el-button>
          <el-button 
            size="small" 
            @click="execCommand('justifyRight')" 
            :class="{ active: isActive('justifyRight') }"
            title="右对齐"
          >
            →
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-group">
        <el-button-group>
          <el-button 
            size="small" 
            @click="execCommand('insertUnorderedList')" 
            :class="{ active: isActive('insertUnorderedList') }"
            title="无序列表"
          >
            <el-icon><List /></el-icon>
          </el-button>
          <el-button 
            size="small" 
            @click="execCommand('insertOrderedList')" 
            :class="{ active: isActive('insertOrderedList') }"
            title="有序列表"
          >
            <el-icon><Tickets /></el-icon>
          </el-button>
        </el-button-group>
      </div>
      
      <div class="toolbar-group">
        <el-button 
          size="small" 
          @click="insertLink" 
          title="插入链接"
        >
          <el-icon><Link /></el-icon>
        </el-button>
        <el-button 
          size="small" 
          @click="removeFormat" 
          title="清除格式"
        >
          <el-icon><RefreshLeft /></el-icon>
        </el-button>
      </div>
      
      <div class="toolbar-group">
        <input 
          ref="colorInput"
          type="color" 
          @change="changeTextColor"
          style="display: none"
        />
        <el-button 
          size="small" 
          @click="colorInput?.click()" 
          title="文字颜色"
        >
          <el-icon><Brush /></el-icon>
        </el-button>
      </div>
    </div>
    
    <!-- 编辑器 -->
    <div 
      ref="editorRef"
      class="editor-content"
      :style="{ minHeight: minHeight + 'px' }"
      contenteditable="true"
      @input="handleInput"
      @keydown="handleKeydown"
      @mouseup="updateToolbar"
      @keyup="updateToolbar"
      v-html="content"
    ></div>
    
    <!-- 字数统计 -->
    <div class="editor-footer">
      <div class="word-count">
        字符数: {{ wordCount }} / {{ maxLength || '无限制' }}
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, nextTick, onMounted, watch } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  List, 
  Tickets, 
  Link, 
  RefreshLeft,
  Brush
} from '@element-plus/icons-vue'

interface Props {
  modelValue?: string
  placeholder?: string
  minHeight?: number
  maxLength?: number
  disabled?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'change', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  placeholder: '请输入内容...',
  minHeight: 200,
  maxLength: undefined,
  disabled: false
})

const emit = defineEmits<Emits>()

const editorRef = ref<HTMLDivElement>()
const colorInput = ref<HTMLInputElement>()
const currentFontSize = ref('3')

const content = computed({
  get: () => props.modelValue,
  set: (value: string) => {
    emit('update:modelValue', value)
    emit('change', value)
  }
})

const wordCount = computed(() => {
  const text = editorRef.value?.innerText || ''
  return text.length
})

const execCommand = (command: string, value?: string) => {
  if (props.disabled) return
  
  document.execCommand(command, false, value)
  editorRef.value?.focus()
  updateContent()
}

const isActive = (command: string): boolean => {
  try {
    return document.queryCommandState(command)
  } catch {
    return false
  }
}

const changeFontSize = (size: string) => {
  execCommand('fontSize', size)
}

const changeTextColor = (event: Event) => {
  const target = event.target as HTMLInputElement
  execCommand('foreColor', target.value)
}

const insertLink = () => {
  const url = prompt('请输入链接地址:')
  if (url) {
    execCommand('createLink', url)
  }
}

const removeFormat = () => {
  execCommand('removeFormat')
  execCommand('unlink')
}

const handleInput = () => {
  updateContent()
}

const handleKeydown = (event: KeyboardEvent) => {
  if (props.disabled) {
    event.preventDefault()
    return
  }
  
  // 检查字符限制
  if (props.maxLength && wordCount.value >= props.maxLength) {
    // 允许删除和导航键
    const allowedKeys = ['Backspace', 'Delete', 'ArrowLeft', 'ArrowRight', 'ArrowUp', 'ArrowDown']
    if (!allowedKeys.includes(event.key) && !event.ctrlKey && !event.metaKey) {
      event.preventDefault()
      ElMessage.warning(`内容长度不能超过 ${props.maxLength} 个字符`)
      return
    }
  }
  
  // 快捷键支持
  if (event.ctrlKey || event.metaKey) {
    switch (event.key) {
      case 'b':
        event.preventDefault()
        execCommand('bold')
        break
      case 'i':
        event.preventDefault()
        execCommand('italic')
        break
      case 'u':
        event.preventDefault()
        execCommand('underline')
        break
      case 'z':
        if (event.shiftKey) {
          event.preventDefault()
          execCommand('redo')
        } else {
          event.preventDefault()
          execCommand('undo')
        }
        break
    }
  }
}

const updateContent = () => {
  if (!editorRef.value) return
  
  const html = editorRef.value.innerHTML
  content.value = html
}

const updateToolbar = () => {
  // 更新工具栏状态
  nextTick(() => {
    // 这里可以添加更多工具栏状态更新逻辑
  })
}

const setContent = (html: string) => {
  if (editorRef.value) {
    editorRef.value.innerHTML = html
  }
}

// 监听外部内容变化
watch(() => props.modelValue, (newValue) => {
  if (editorRef.value && editorRef.value.innerHTML !== newValue) {
    setContent(newValue)
  }
})

onMounted(() => {
  if (editorRef.value) {
    // 设置初始内容
    if (props.modelValue) {
      setContent(props.modelValue)
    } else if (props.placeholder) {
      editorRef.value.setAttribute('data-placeholder', props.placeholder)
    }
    
    // 禁用拼写检查
    editorRef.value.setAttribute('spellcheck', 'false')
  }
})
</script>

<style scoped>
.rich-text-editor {
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  overflow: hidden;
  transition: all 0.3s;
}

.toolbar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background-color: #f5f7fa;
  border-bottom: 1px solid #dcdfe6;
  flex-wrap: wrap;
  transition: background-color 0.3s, border-color 0.3s;
}

.toolbar-group {
  display: flex;
  align-items: center;
}

.toolbar .el-button.active {
  background-color: #409eff;
  color: white;
  border-color: #409eff;
}

.editor-content {
  padding: 12px;
  outline: none;
  line-height: 1.6;
  font-size: 14px;
  color: #606266;
  background-color: #fff;
  overflow-y: auto;
  transition: background-color 0.3s, color 0.3s;
}

.editor-content:empty:before {
  content: attr(data-placeholder);
  color: #c0c4cc;
  font-style: italic;
}

.editor-content:focus {
  outline: none;
}

/* 编辑器内容样式 */
.editor-content :deep(p) {
  margin: 0 0 8px 0;
}

.editor-content :deep(ul),
.editor-content :deep(ol) {
  margin: 8px 0;
  padding-left: 20px;
}

.editor-content :deep(li) {
  margin: 4px 0;
}

.editor-content :deep(a) {
  color: #409eff;
  text-decoration: underline;
}

.editor-content :deep(strong) {
  font-weight: bold;
}

.editor-content :deep(em) {
  font-style: italic;
}

.editor-content :deep(u) {
  text-decoration: underline;
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

/* 禁用状态 */
.rich-text-editor.disabled .editor-content {
  background-color: #f5f7fa;
  color: #c0c4cc;
  cursor: not-allowed;
}

.rich-text-editor.disabled .toolbar {
  opacity: 0.6;
  pointer-events: none;
}
</style>