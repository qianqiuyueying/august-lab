<template>
  <div class="avatar-upload">
    <div class="avatar-container">
      <!-- 头像预览 -->
      <div class="avatar-preview" @click="triggerUpload">
        <img 
          v-if="modelValue" 
          :src="modelValue" 
          alt="头像预览"
          class="avatar-image"
        />
        <div v-else class="avatar-placeholder">
          <el-icon size="48" class="upload-icon">
            <component :is="loading ? 'Loading' : 'Plus'" />
          </el-icon>
          <div class="upload-text">点击上传头像</div>
        </div>
        
        <!-- 悬停遮罩 -->
        <div v-if="modelValue" class="avatar-overlay">
          <el-icon size="24" class="overlay-icon">
            <component :is="loading ? 'Loading' : 'Camera'" />
          </el-icon>
          <div class="overlay-text">{{ loading ? '上传中...' : '更换头像' }}</div>
        </div>
      </div>
      
      <!-- 操作按钮 -->
      <div class="avatar-actions">
        <el-button size="small" @click="triggerUpload" :loading="loading">
          <el-icon><Upload /></el-icon>
          {{ modelValue ? '更换头像' : '上传头像' }}
        </el-button>
        
        <el-button 
          v-if="modelValue" 
          size="small" 
          type="danger" 
          @click="removeAvatar"
          :disabled="loading"
        >
          <el-icon><Delete /></el-icon>
          删除头像
        </el-button>
      </div>
    </div>
    
    <!-- 文件输入 -->
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      style="display: none"
      @change="handleFileChange"
    />
    
    <!-- 上传提示 -->
    <div class="upload-tips">
      <p class="tip-text">支持 JPG、PNG、GIF 格式</p>
      <p class="tip-text">建议尺寸：200x200 像素，大小不超过 2MB</p>
    </div>
    
    <!-- 裁剪对话框 -->
    <el-dialog 
      v-model="showCropDialog" 
      title="裁剪头像"
      width="600px"
      @close="cancelCrop"
    >
      <div class="crop-container">
        <div class="crop-preview">
          <img 
            ref="cropImage"
            :src="cropImageSrc"
            alt="裁剪预览"
            class="crop-image"
          />
        </div>
        
        <div class="crop-controls">
          <div class="crop-info">
            <p>拖拽调整裁剪区域，滚轮缩放图片</p>
          </div>
          
          <div class="crop-actions">
            <el-button @click="cancelCrop">取消</el-button>
            <el-button type="primary" @click="confirmCrop" :loading="cropping">
              确认裁剪
            </el-button>
          </div>
        </div>
      </div>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, nextTick } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { 
  Plus, 
  Camera, 
  Upload, 
  Delete, 
  Loading 
} from '@element-plus/icons-vue'

interface Props {
  modelValue?: string
  loading?: boolean
  maxSize?: number // MB
  cropAspectRatio?: number
}

interface Emits {
  (e: 'update:modelValue', value: string): void
  (e: 'upload', file: File): void
  (e: 'remove'): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  loading: false,
  maxSize: 2,
  cropAspectRatio: 1
})

const emit = defineEmits<Emits>()

const fileInput = ref<HTMLInputElement>()
const cropImage = ref<HTMLImageElement>()
const showCropDialog = ref(false)
const cropImageSrc = ref('')
const cropping = ref(false)
const currentFile = ref<File | null>(null)

// 简单的裁剪状态（实际项目中可以使用专业的裁剪库如 cropperjs）
const cropData = ref({
  x: 0,
  y: 0,
  width: 200,
  height: 200,
  scale: 1
})

const triggerUpload = () => {
  if (props.loading) return
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
  
  // 验证文件大小
  if (file.size > props.maxSize * 1024 * 1024) {
    ElMessage.error(`图片大小不能超过 ${props.maxSize}MB`)
    return
  }
  
  currentFile.value = file
  
  // 显示裁剪对话框
  const reader = new FileReader()
  reader.onload = (e) => {
    cropImageSrc.value = e.target?.result as string
    showCropDialog.value = true
    
    nextTick(() => {
      initCrop()
    })
  }
  reader.readAsDataURL(file)
  
  // 清空input值，允许重复选择同一文件
  target.value = ''
}

const initCrop = () => {
  // 这里可以初始化裁剪功能
  // 实际项目中建议使用 cropperjs 等专业库
  if (cropImage.value) {
    // 简单的拖拽和缩放实现
    let isDragging = false
    let startX = 0
    let startY = 0
    
    cropImage.value.addEventListener('mousedown', (e) => {
      isDragging = true
      startX = e.clientX - cropData.value.x
      startY = e.clientY - cropData.value.y
    })
    
    document.addEventListener('mousemove', (e) => {
      if (!isDragging) return
      cropData.value.x = e.clientX - startX
      cropData.value.y = e.clientY - startY
    })
    
    document.addEventListener('mouseup', () => {
      isDragging = false
    })
    
    // 滚轮缩放
    cropImage.value.addEventListener('wheel', (e) => {
      e.preventDefault()
      const delta = e.deltaY > 0 ? 0.9 : 1.1
      cropData.value.scale = Math.max(0.1, Math.min(3, cropData.value.scale * delta))
    })
  }
}

const confirmCrop = async () => {
  if (!currentFile.value) return
  
  try {
    cropping.value = true
    
    // 这里应该进行实际的图片裁剪
    // 简化处理：直接使用原图
    emit('upload', currentFile.value)
    
    showCropDialog.value = false
  } catch (error) {
    console.error('裁剪失败:', error)
    ElMessage.error('裁剪失败')
  } finally {
    cropping.value = false
  }
}

const cancelCrop = () => {
  showCropDialog.value = false
  cropImageSrc.value = ''
  currentFile.value = null
}

const removeAvatar = async () => {
  try {
    await ElMessageBox.confirm(
      '确定要删除头像吗？',
      '确认删除',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )
    
    emit('update:modelValue', '')
    emit('remove')
    ElMessage.success('头像已删除')
  } catch (error) {
    // 用户取消删除
  }
}
</script>

<style scoped>
.avatar-upload {
  display: flex;
  flex-direction: column;
  align-items: flex-start;
  gap: 16px;
}

.avatar-container {
  display: flex;
  align-items: flex-start;
  gap: 16px;
}

.avatar-preview {
  position: relative;
  width: 120px;
  height: 120px;
  border: 2px dashed #dcdfe6;
  border-radius: 50%;
  overflow: hidden;
  cursor: pointer;
  transition: all 0.3s;
  background-color: #fafafa;
}

.avatar-preview:hover {
  border-color: #409eff;
  background-color: #f0f9ff;
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #8c939d;
}

.upload-icon {
  margin-bottom: 8px;
}

.upload-text {
  font-size: 12px;
  text-align: center;
}

.avatar-overlay {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.6);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: white;
  opacity: 0;
  transition: opacity 0.3s;
}

.avatar-preview:hover .avatar-overlay {
  opacity: 1;
}

.overlay-icon {
  margin-bottom: 4px;
}

.overlay-text {
  font-size: 12px;
  text-align: center;
}

.avatar-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.upload-tips {
  margin-top: 8px;
}

.tip-text {
  margin: 0;
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.crop-container {
  display: flex;
  gap: 20px;
}

.crop-preview {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: center;
  background-color: #f5f7fa;
  border-radius: 4px;
  min-height: 300px;
}

.crop-image {
  max-width: 100%;
  max-height: 300px;
  cursor: move;
  user-select: none;
}

.crop-controls {
  width: 200px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.crop-info {
  padding: 12px;
  background-color: #f0f9ff;
  border-radius: 4px;
  font-size: 12px;
  color: #606266;
}

.crop-actions {
  display: flex;
  gap: 8px;
}

.crop-actions .el-button {
  flex: 1;
}
</style>