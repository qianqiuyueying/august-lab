<template>
  <div class="profile-preview" :class="{ 'full-view': fullView }">
    <div v-if="profile" class="preview-content">
      <!-- 头像和基本信息 -->
      <div class="profile-header">
        <div class="avatar-section">
          <div class="avatar-container">
            <img 
              v-if="profile.avatar_url" 
              :src="profile.avatar_url" 
              :alt="profile.name"
              class="avatar-image"
            />
            <div v-else class="avatar-placeholder">
              <el-icon size="32"><User /></el-icon>
            </div>
          </div>
        </div>
        
        <div class="basic-info">
          <h2 class="profile-name">{{ profile.name || '未设置姓名' }}</h2>
          <p class="profile-title">{{ profile.title || '未设置职位' }}</p>
          
          <div v-if="profile.location || profile.email || profile.phone" class="contact-info">
            <div v-if="profile.location" class="contact-item">
              <el-icon><Location /></el-icon>
              <span>{{ profile.location }}</span>
            </div>
            <div v-if="profile.email" class="contact-item">
              <el-icon><Message /></el-icon>
              <span>{{ profile.email }}</span>
            </div>
            <div v-if="profile.phone" class="contact-item">
              <el-icon><Phone /></el-icon>
              <span>{{ profile.phone }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 个人简介 -->
      <div v-if="profile.bio" class="bio-section">
        <h3 class="section-title">个人简介</h3>
        <div class="bio-content" v-html="profile.bio"></div>
      </div>
      
      <!-- 社交链接 -->
      <div v-if="hasSocialLinks" class="social-section">
        <h3 class="section-title">社交链接</h3>
        <div class="social-links">
          <a 
            v-if="profile.github_url" 
            :href="profile.github_url" 
            target="_blank"
            class="social-link github"
          >
            <el-icon><Link /></el-icon>
            <span>GitHub</span>
          </a>
          
          <a 
            v-if="profile.linkedin_url" 
            :href="profile.linkedin_url" 
            target="_blank"
            class="social-link linkedin"
          >
            <el-icon><Link /></el-icon>
            <span>LinkedIn</span>
          </a>
          
          <a 
            v-if="profile.twitter_url" 
            :href="profile.twitter_url" 
            target="_blank"
            class="social-link twitter"
          >
            <el-icon><Link /></el-icon>
            <span>Twitter</span>
          </a>
          
          <a 
            v-if="profile.website_url" 
            :href="profile.website_url" 
            target="_blank"
            class="social-link website"
          >
            <el-icon><Link /></el-icon>
            <span>个人网站</span>
          </a>
        </div>
      </div>
      
      <!-- 技能展示 -->
      <div v-if="profile.skills && profile.skills.length > 0" class="skills-section">
        <h3 class="section-title">技能专长</h3>
        
        <!-- 按分类分组显示 -->
        <div class="skills-by-category">
          <div 
            v-for="category in skillsByCategory" 
            :key="category.name"
            class="skill-category"
          >
            <h4 class="category-name">{{ category.label }}</h4>
            <div class="category-skills">
              <div 
                v-for="skill in category.skills" 
                :key="skill.name"
                class="skill-item"
              >
                <div class="skill-header">
                  <span class="skill-name">{{ skill.name }}</span>
                  <span class="skill-level">{{ skill.level }}%</span>
                </div>
                <div class="skill-progress">
                  <div 
                    class="skill-progress-bar" 
                    :style="{ width: skill.level + '%' }"
                  ></div>
                </div>
                <div v-if="skill.description" class="skill-description">
                  {{ skill.description }}
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 统计信息 -->
      <div v-if="fullView && profile.skills && profile.skills.length > 0" class="stats-section">
        <h3 class="section-title">技能统计</h3>
        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-number">{{ profile.skills.length }}</div>
            <div class="stat-label">技能总数</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ averageSkillLevel }}%</div>
            <div class="stat-label">平均熟练度</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ skillCategories.length }}</div>
            <div class="stat-label">技能分类</div>
          </div>
          <div class="stat-card">
            <div class="stat-number">{{ expertSkills.length }}</div>
            <div class="stat-label">专家级技能</div>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 空状态 -->
    <div v-else class="empty-preview">
      <el-icon size="48" class="empty-icon"><User /></el-icon>
      <p class="empty-text">暂无个人信息</p>
      <p class="empty-hint">请填写左侧表单来预览效果</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { 
  User, 
  Location, 
  Message, 
  Phone, 
  Link 
} from '@element-plus/icons-vue'
import type { Profile, Skill } from '../../shared/types'

interface Props {
  profile?: Partial<Profile> | null
  fullView?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  profile: null,
  fullView: false
})

const skillCategories = [
  { value: 'frontend', label: '前端开发' },
  { value: 'backend', label: '后端开发' },
  { value: 'mobile', label: '移动开发' },
  { value: 'database', label: '数据库' },
  { value: 'cloud', label: '云服务' },
  { value: 'tools', label: '工具链' },
  { value: 'design', label: '设计' },
  { value: 'other', label: '其他' }
]

const hasSocialLinks = computed(() => {
  return props.profile?.github_url || 
         props.profile?.linkedin_url || 
         props.profile?.twitter_url || 
         props.profile?.website_url
})

const skillsByCategory = computed(() => {
  if (!props.profile || !props.profile.skills) return []
  
  const categories = skillCategories.map(category => ({
    name: category.value,
    label: category.label,
    skills: props.profile!.skills!.filter(skill => skill.category === category.value) || []
  })).filter(category => category.skills.length > 0)
  
  return categories
})

const averageSkillLevel = computed(() => {
  if (!props.profile?.skills || props.profile.skills.length === 0) return 0
  
  const total = props.profile.skills.reduce((sum, skill) => sum + skill.level, 0)
  return Math.round(total / props.profile.skills.length)
})

const expertSkills = computed(() => {
  if (!props.profile?.skills) return []
  return props.profile.skills.filter(skill => skill.level >= 80)
})
</script>

<style scoped>
.profile-preview {
  background-color: white;
  border-radius: 8px;
  overflow: hidden;
  transition: all 0.3s;
}

.dark .profile-preview {
  background-color: var(--lab-card);
  border: 1px solid var(--lab-border);
}

.profile-preview.full-view {
  max-width: none;
}

.preview-content {
  padding: 20px;
}

.profile-header {
  display: flex;
  align-items: flex-start;
  gap: 20px;
  margin-bottom: 24px;
  padding-bottom: 20px;
  border-bottom: 1px solid #e4e7ed;
}

.dark .profile-header {
  border-bottom-color: var(--lab-border);
}

.avatar-section {
  flex-shrink: 0;
}

.avatar-container {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  border: 3px solid #e4e7ed;
}

.dark .avatar-container {
  border-color: var(--lab-border);
}

.avatar-image {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.avatar-placeholder {
  width: 100%;
  height: 100%;
  background-color: #f5f7fa;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #c0c4cc;
}

.dark .avatar-placeholder {
  background-color: var(--lab-surface);
  color: var(--lab-muted);
}

.basic-info {
  flex: 1;
}

.profile-name {
  margin: 0 0 8px 0;
  font-size: 24px;
  font-weight: 600;
  color: #303133;
}

.dark .profile-name {
  color: var(--lab-text);
}

.profile-title {
  margin: 0 0 16px 0;
  font-size: 16px;
  color: #606266;
  font-weight: 500;
}

.dark .profile-title {
  color: var(--lab-muted);
}

.contact-info {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.contact-item {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 14px;
  color: #606266;
}

.dark .contact-item {
  color: var(--lab-muted);
}

.contact-item .el-icon {
  color: #909399;
}

.section-title {
  margin: 0 0 16px 0;
  font-size: 18px;
  font-weight: 600;
  color: #303133;
  border-bottom: 2px solid #409eff;
  padding-bottom: 8px;
}

.dark .section-title {
  color: var(--lab-text);
  border-bottom-color: var(--lab-accent);
}

.bio-section {
  margin-bottom: 24px;
}

.bio-content {
  line-height: 1.6;
  color: #606266;
}

.dark .bio-content {
  color: var(--lab-muted);
}

.bio-content :deep(p) {
  margin: 0 0 12px 0;
}

.bio-content :deep(strong) {
  color: #303133;
  font-weight: 600;
}

.dark .bio-content :deep(strong) {
  color: var(--lab-text);
}

.bio-content :deep(em) {
  font-style: italic;
}

.bio-content :deep(ul),
.bio-content :deep(ol) {
  margin: 12px 0;
  padding-left: 20px;
}

.social-section {
  margin-bottom: 24px;
}

.social-links {
  display: flex;
  flex-wrap: wrap;
  gap: 12px;
}

.social-link {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 16px;
  border: 1px solid #e4e7ed;
  border-radius: 20px;
  text-decoration: none;
  color: #606266;
  font-size: 14px;
  transition: all 0.3s;
}

.dark .social-link {
  border-color: var(--lab-border);
  color: var(--lab-muted);
  background-color: var(--lab-surface);
}

.social-link:hover {
  border-color: #409eff;
  color: #409eff;
  background-color: #f0f9ff;
}

.dark .social-link:hover {
  border-color: var(--lab-accent);
  color: var(--lab-accent);
  background-color: rgba(0, 240, 255, 0.1);
}

.social-link.github:hover {
  border-color: #333;
  color: #333;
  background-color: #f6f8fa;
}

.dark .social-link.github:hover {
  border-color: #fff;
  color: #fff;
  background-color: rgba(255, 255, 255, 0.1);
}

.social-link.linkedin:hover {
  border-color: #0077b5;
  color: #0077b5;
  background-color: #f0f8ff;
}

.social-link.twitter:hover {
  border-color: #1da1f2;
  color: #1da1f2;
  background-color: #f0f9ff;
}

.skills-section {
  margin-bottom: 24px;
}

.skills-by-category {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.skill-category {
  background-color: #fafafa;
  border-radius: 8px;
  padding: 16px;
}

.dark .skill-category {
  background-color: var(--lab-surface);
}

.category-name {
  margin: 0 0 12px 0;
  font-size: 16px;
  font-weight: 600;
  color: #409eff;
}

.dark .category-name {
  color: var(--lab-accent);
}

.category-skills {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.skill-item {
  background-color: white;
  border-radius: 6px;
  padding: 12px;
  border: 1px solid #e4e7ed;
}

.dark .skill-item {
  background-color: var(--lab-card);
  border-color: var(--lab-border);
}

.skill-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.skill-name {
  font-weight: 500;
  color: #303133;
}

.dark .skill-name {
  color: var(--lab-text);
}

.skill-level {
  font-size: 12px;
  color: #909399;
  font-weight: 600;
}

.dark .skill-level {
  color: var(--lab-muted);
}

.skill-progress {
  height: 6px;
  background-color: #f0f2f5;
  border-radius: 3px;
  overflow: hidden;
  margin-bottom: 8px;
}

.dark .skill-progress {
  background-color: rgba(255, 255, 255, 0.1);
}

.skill-progress-bar {
  height: 100%;
  background: linear-gradient(90deg, #409eff 0%, #67c23a 100%);
  border-radius: 3px;
  transition: width 0.3s ease;
}

.dark .skill-progress-bar {
  background: linear-gradient(90deg, var(--lab-accent) 0%, #00ff94 100%);
}

.skill-description {
  font-size: 12px;
  color: #909399;
  line-height: 1.4;
}

.stats-section {
  margin-bottom: 24px;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(120px, 1fr));
  gap: 16px;
}

.stat-card {
  text-align: center;
  padding: 16px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #e4e7ed;
}

.dark .stat-card {
  background-color: var(--lab-surface);
  border-color: var(--lab-border);
}

.stat-number {
  font-size: 24px;
  font-weight: 600;
  color: #409eff;
  margin-bottom: 4px;
}

.dark .stat-number {
  color: var(--lab-accent);
}

.stat-label {
  font-size: 12px;
  color: #909399;
}

.empty-preview {
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

/* 全视图模式下的样式调整 */
.profile-preview.full-view .preview-content {
  padding: 32px;
  max-width: 800px;
  margin: 0 auto;
}

.profile-preview.full-view .profile-header {
  flex-direction: column;
  align-items: center;
  text-align: center;
}

.profile-preview.full-view .avatar-container {
  width: 120px;
  height: 120px;
}

.profile-preview.full-view .contact-info {
  flex-direction: row;
  justify-content: center;
  flex-wrap: wrap;
  gap: 16px;
}

.profile-preview.full-view .social-links {
  justify-content: center;
}

.profile-preview.full-view .stats-grid {
  grid-template-columns: repeat(4, 1fr);
}
</style>