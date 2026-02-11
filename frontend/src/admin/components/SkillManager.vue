<template>
  <div class="skill-manager">
    <!-- 技能列表 -->
    <div class="skills-list">
      <div 
        v-for="(skill, index) in skills" 
        :key="index"
        class="skill-item"
      >
        <div class="skill-content">
          <div class="skill-header">
            <el-input 
              v-model="skill.name" 
              placeholder="技能名称"
              size="small"
              class="skill-name-input"
              @blur="updateSkills"
            />
            <el-select 
              v-model="skill.category" 
              placeholder="选择分类"
              size="small"
              class="skill-category-select"
              @change="updateSkills"
            >
              <el-option 
                v-for="category in skillCategories" 
                :key="category.value"
                :label="category.label" 
                :value="category.value" 
              />
            </el-select>
            <el-button 
              type="danger" 
              size="small" 
              @click="removeSkill(index)"
              :icon="Delete"
            />
          </div>
          
          <div class="skill-level">
            <div class="level-label">
              熟练度: {{ skill.level }}%
            </div>
            <el-slider 
              v-model="skill.level" 
              :min="0" 
              :max="100" 
              :step="5"
              @change="updateSkills"
              class="level-slider"
            />
          </div>
          
          <div class="skill-description">
            <el-input 
              v-model="skill.description" 
              type="textarea"
              :rows="2"
              placeholder="技能描述（可选）"
              maxlength="200"
              show-word-limit
              @blur="updateSkills"
            />
          </div>
        </div>
      </div>
      
      <!-- 空状态 -->
      <div v-if="skills.length === 0" class="empty-state">
        <el-icon size="48" class="empty-icon"><Tools /></el-icon>
        <p class="empty-text">暂无技能信息</p>
        <p class="empty-hint">点击下方按钮添加您的技能</p>
      </div>
    </div>
    
    <!-- 添加技能 -->
    <div class="add-skill-section">
      <el-button type="primary" @click="addSkill" :icon="Plus">
        添加技能
      </el-button>
      
      <el-button @click="addFromPreset" :icon="Star">
        从预设添加
      </el-button>
      
      <el-button @click="importSkills" :icon="Upload">
        批量导入
      </el-button>
    </div>
    
    <!-- 技能分类统计 -->
    <div v-if="skills.length > 0" class="skill-stats">
      <h4 class="stats-title">技能分布</h4>
      <div class="stats-grid">
        <div 
          v-for="stat in skillStats" 
          :key="stat.category"
          class="stat-item"
        >
          <div class="stat-label">{{ stat.label }}</div>
          <div class="stat-count">{{ stat.count }} 项</div>
          <div class="stat-avg">平均 {{ stat.avgLevel }}%</div>
        </div>
      </div>
    </div>
    
    <!-- 预设技能对话框 -->
    <el-dialog 
      v-model="showPresetDialog" 
      title="选择预设技能"
      width="600px"
    >
      <div class="preset-skills">
        <div class="preset-category" v-for="category in presetSkills" :key="category.name">
          <h4 class="category-title">{{ category.label }}</h4>
          <div class="preset-skill-grid">
            <el-checkbox 
              v-for="skill in category.skills" 
              :key="skill"
              v-model="selectedPresetSkills"
              :label="skill"
              class="preset-skill-item"
            >
              {{ skill }}
            </el-checkbox>
          </div>
        </div>
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showPresetDialog = false">取消</el-button>
          <el-button type="primary" @click="addSelectedPresetSkills">
            添加选中技能 ({{ selectedPresetSkills.length }})
          </el-button>
        </div>
      </template>
    </el-dialog>
    
    <!-- 批量导入对话框 -->
    <el-dialog 
      v-model="showImportDialog" 
      title="批量导入技能"
      width="500px"
    >
      <div class="import-section">
        <el-alert 
          title="导入格式说明" 
          type="info" 
          :closable="false"
          class="import-alert"
        >
          <p>每行一个技能，格式：技能名称,分类,熟练度</p>
          <p>示例：JavaScript,frontend,90</p>
        </el-alert>
        
        <el-input 
          v-model="importText"
          type="textarea"
          :rows="8"
          placeholder="请输入技能信息，每行一个..."
          class="import-textarea"
        />
      </div>
      
      <template #footer>
        <div class="dialog-footer">
          <el-button @click="showImportDialog = false">取消</el-button>
          <el-button type="primary" @click="processImport">
            导入技能
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import { 
  Plus, 
  Delete, 
  Star, 
  Upload, 
  Tools 
} from '@element-plus/icons-vue'
import type { Skill } from '../../shared/types'

interface Props {
  modelValue: Skill[]
}

interface Emits {
  (e: 'update:modelValue', value: Skill[]): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const showPresetDialog = ref(false)
const showImportDialog = ref(false)
const selectedPresetSkills = ref<string[]>([])
const importText = ref('')

const skills = computed({
  get: () => props.modelValue,
  set: (value: Skill[]) => emit('update:modelValue', value)
})

const skillCategories = [
  { label: '前端开发', value: 'frontend' },
  { label: '后端开发', value: 'backend' },
  { label: '移动开发', value: 'mobile' },
  { label: '数据库', value: 'database' },
  { label: '云服务', value: 'cloud' },
  { label: '工具链', value: 'tools' },
  { label: '设计', value: 'design' },
  { label: '其他', value: 'other' }
]

const presetSkills = [
  {
    name: 'frontend',
    label: '前端开发',
    skills: ['JavaScript', 'TypeScript', 'Vue.js', 'React', 'Angular', 'HTML', 'CSS', 'Sass', 'Less', 'Tailwind CSS', 'Bootstrap', 'Webpack', 'Vite', 'ESLint', 'Prettier']
  },
  {
    name: 'backend',
    label: '后端开发',
    skills: ['Node.js', 'Python', 'Java', 'Go', 'Rust', 'C#', 'PHP', 'Ruby', 'Express.js', 'FastAPI', 'Spring Boot', 'Django', 'Flask', 'Laravel']
  },
  {
    name: 'mobile',
    label: '移动开发',
    skills: ['React Native', 'Flutter', 'Swift', 'Kotlin', 'Xamarin', 'Ionic', 'Cordova']
  },
  {
    name: 'database',
    label: '数据库',
    skills: ['MySQL', 'PostgreSQL', 'MongoDB', 'Redis', 'SQLite', 'Oracle', 'SQL Server', 'Elasticsearch']
  },
  {
    name: 'cloud',
    label: '云服务',
    skills: ['AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'Jenkins', 'GitLab CI', 'GitHub Actions']
  },
  {
    name: 'tools',
    label: '工具链',
    skills: ['Git', 'SVN', 'Jira', 'Confluence', 'Figma', 'Sketch', 'Postman', 'VS Code', 'IntelliJ IDEA']
  },
  {
    name: 'design',
    label: '设计',
    skills: ['UI设计', 'UX设计', 'Photoshop', 'Illustrator', 'Figma', 'Sketch', '原型设计', '用户研究']
  }
]

const skillStats = computed(() => {
  const stats = skillCategories.map(category => {
    const categorySkills = skills.value.filter(skill => skill.category === category.value)
    const avgLevel = categorySkills.length > 0 
      ? Math.round(categorySkills.reduce((sum, skill) => sum + skill.level, 0) / categorySkills.length)
      : 0
    
    return {
      category: category.value,
      label: category.label,
      count: categorySkills.length,
      avgLevel
    }
  }).filter(stat => stat.count > 0)
  
  return stats
})

const addSkill = () => {
  const newSkill: Skill = {
    name: '',
    category: 'other',
    level: 50,
    description: ''
  }
  
  skills.value = [...skills.value, newSkill]
}

const removeSkill = (index: number) => {
  skills.value = skills.value.filter((_, i) => i !== index)
}

const updateSkills = () => {
  // 触发更新
  emit('update:modelValue', [...skills.value])
}

const addFromPreset = () => {
  selectedPresetSkills.value = []
  showPresetDialog.value = true
}

const addSelectedPresetSkills = () => {
  const newSkills: Skill[] = selectedPresetSkills.value.map(skillName => {
    // 找到技能所属的分类
    let category = 'other'
    for (const preset of presetSkills) {
      if (preset.skills.includes(skillName)) {
        category = preset.name
        break
      }
    }
    
    return {
      name: skillName,
      category,
      level: 70, // 默认熟练度
      description: ''
    }
  })
  
  // 过滤掉已存在的技能
  const existingSkillNames = skills.value.map(skill => skill.name)
  const uniqueNewSkills = newSkills.filter(skill => !existingSkillNames.includes(skill.name))
  
  if (uniqueNewSkills.length === 0) {
    ElMessage.warning('选中的技能已存在')
  } else {
    skills.value = [...skills.value, ...uniqueNewSkills]
    ElMessage.success(`成功添加 ${uniqueNewSkills.length} 个技能`)
  }
  
  showPresetDialog.value = false
}

const importSkills = () => {
  importText.value = ''
  showImportDialog.value = true
}

const processImport = () => {
  if (!importText.value.trim()) {
    ElMessage.warning('请输入要导入的技能信息')
    return
  }
  
  const lines = importText.value.trim().split('\n')
  const newSkills: Skill[] = []
  const errors: string[] = []
  
  lines.forEach((line, index) => {
    const parts = line.trim().split(',')
    if (parts.length < 2) {
      errors.push(`第 ${index + 1} 行格式错误`)
      return
    }
    
    const name = parts[0].trim()
    const category = parts[1].trim()
    const level = parts[2] ? parseInt(parts[2].trim()) : 50
    const description = parts[3] ? parts[3].trim() : ''
    
    if (!name) {
      errors.push(`第 ${index + 1} 行技能名称不能为空`)
      return
    }
    
    if (!skillCategories.find(cat => cat.value === category)) {
      errors.push(`第 ${index + 1} 行分类 "${category}" 不存在`)
      return
    }
    
    if (isNaN(level) || level < 0 || level > 100) {
      errors.push(`第 ${index + 1} 行熟练度必须是 0-100 的数字`)
      return
    }
    
    newSkills.push({ name, category, level, description })
  })
  
  if (errors.length > 0) {
    ElMessage.error(`导入失败：${errors.join('；')}`)
    return
  }
  
  // 过滤掉已存在的技能
  const existingSkillNames = skills.value.map(skill => skill.name)
  const uniqueNewSkills = newSkills.filter(skill => !existingSkillNames.includes(skill.name))
  
  if (uniqueNewSkills.length === 0) {
    ElMessage.warning('所有技能都已存在')
  } else {
    skills.value = [...skills.value, ...uniqueNewSkills]
    ElMessage.success(`成功导入 ${uniqueNewSkills.length} 个技能`)
  }
  
  showImportDialog.value = false
}
</script>

<style scoped>
.skill-manager {
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.skills-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.skill-item {
  padding: 16px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  background-color: #fafafa;
  transition: all 0.3s;
}

.dark .skill-item {
  background-color: var(--lab-surface);
  border-color: var(--lab-border);
}

.skill-content {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skill-header {
  display: flex;
  align-items: center;
  gap: 12px;
}

.skill-name-input {
  flex: 2;
}

.skill-category-select {
  flex: 1;
}

.skill-level {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.level-label {
  font-size: 14px;
  color: #606266;
  font-weight: 500;
}

.dark .level-label {
  color: var(--lab-muted);
}

.level-slider {
  margin: 0;
}

.skill-description {
  margin-top: 8px;
}

.empty-state {
  text-align: center;
  padding: 40px 20px;
  color: #909399;
}

.empty-icon {
  margin-bottom: 16px;
  color: #c0c4cc;
}

.empty-text {
  margin: 0 0 8px 0;
  font-size: 16px;
  color: #606266;
}

.empty-hint {
  margin: 0;
  font-size: 14px;
}

.add-skill-section {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
}

.skill-stats {
  padding: 16px;
  background-color: #f8f9fa;
  border-radius: 8px;
}

.dark .skill-stats {
  background-color: var(--lab-surface);
}

.stats-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #303133;
}

.dark .stats-title {
  color: var(--lab-text);
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 16px;
}

.stat-item {
  text-align: center;
  padding: 12px;
  background-color: white;
  border-radius: 6px;
  border: 1px solid #e4e7ed;
}

.dark .stat-item {
  background-color: var(--lab-card);
  border-color: var(--lab-border);
}

.stat-label {
  font-size: 14px;
  color: #606266;
  margin-bottom: 4px;
}

.dark .stat-label {
  color: var(--lab-muted);
}

.stat-count {
  font-size: 18px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 2px;
}

.dark .stat-count {
  color: var(--lab-accent);
}

.stat-avg {
  font-size: 12px;
  color: #909399;
}

.preset-skills {
  max-height: 400px;
  overflow-y: auto;
}

.preset-category {
  margin-bottom: 24px;
}

.category-title {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #303133;
  border-bottom: 1px solid #e4e7ed;
  padding-bottom: 8px;
}

.dark .category-title {
  color: var(--lab-text);
  border-bottom-color: var(--lab-border);
}

.preset-skill-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(150px, 1fr));
  gap: 8px;
}

.preset-skill-item {
  margin: 0;
}

.dark .el-checkbox {
  color: var(--lab-text);
}

.import-section {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.import-alert {
  margin-bottom: 16px;
}

.import-alert p {
  margin: 4px 0;
  font-size: 13px;
}

.import-textarea {
  font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
  font-size: 13px;
}

.dialog-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
}
</style>