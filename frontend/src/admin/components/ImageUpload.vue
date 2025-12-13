<template>
  <div class="image-upload">
    <div v-if="modelValue" class="uploaded-image">
      <div class="image-preview">
        <img :src="modelValue" alt="预览图" />
        <div class="image-overlay">
          <el-button type="primary" size="small" @click="triggerUpload">
            <el-icon><Edit /></el-icon>
            更换图片
          </el-button>
          <el-button type="danger" size="small" @click="removeImage">
            <el-icon><Delete /></el-icon>
            删除图片
          </el-button>
        </div>
      </div>
    </div>
    
    <div v-else class="upload-area" @click="triggerUpload">
      <div class="upload-content">
        <el-icon size="48" class="upload-icon">
          <component :is="loading ? 'Loading' : 'Plus'" />
        </el-icon>
        <div class="upload-text">
          <p>点击上传图片</p>
          <p class="upload-hint">支持 JPG、PNG、GIF 格式，大小不超过 5MB</p>
        </div>
      </div>
    </div>
    
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { Plus, Edit, Delete, Loading } from '@element-plus/icons-vue'

interface Props {
  modelValue?: string
  loading?: boolean
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'upload', file: File): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  loading: false
})

const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement>()

const triggerUpload = () => {
  fileInput.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  
  if (!file) return
  
  // 验证文件类型
  if (!file.type.startsWith('image/')) {
    ElMessage.error('请选择图片文件')
    return
  }
  
  // 验证文件大小 (5MB)
  if (file.size > 5 * 1024 * 1024) {
    ElMessage.error('图片大小不能超过 5MB')
    return
  }
  
  emit('upload', file)
  
  // 清空input值，允许重复选择同一文件
  target.value = ''
}

const removeImage = () => {
  emit('update:modelValue', '')
}
</script>

<style scoped>
.image-upload {
  width: 100%;
}

.upload-area {
  border: 2px dashed #d9d9d9;
  border-radius: 8px;
  padding: 40px 20px;
  text-align: center;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fafafa;
}

.upload-area:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.upload-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 16px;
}

.upload-icon {
  color: #8c939d;
}

.upload-text p {
  margin: 0;
  color: #606266;
}

.upload-hint {
  font-size: 12px;
  color: #909399;
}

.uploaded-image {
  position: relative;
  display: inline-block;
}

.image-preview {
  position: relative;
  width: 200px;
  height: 150px;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid #dcdfe6;
}

.image-preview img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.image-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  opacity: 0;
  transition: opacity 0.3s;
}

.image-preview:hover .image-overlay {
  opacity: 1;
}
</style>