<template>
  <div class="min-h-screen bg-slate-50 dark:bg-[#0b0c10] py-12 md:py-20 relative overflow-hidden font-mono">
    <!-- 背景扫描线 -->
    <div class="absolute inset-0 pointer-events-none opacity-5 dark:opacity-10 bg-[length:40px_40px] bg-grid-pattern dark:bg-grid-pattern-dark z-0"></div>

    <div class="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <!-- 页面头部 -->
      <header class="mb-16 border-b-2 border-slate-200 dark:border-slate-800 pb-8">
        <div class="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <div class="flex items-center gap-3 mb-4">
               <div class="w-3 h-3 bg-lab-accent rounded-sm animate-pulse"></div>
               <span class="text-xs font-bold uppercase tracking-widest text-slate-500 dark:text-slate-400">Identity Matrix</span>
            </div>
            <h1 class="text-4xl md:text-6xl font-black uppercase tracking-tighter text-slate-900 dark:text-white">
              <span class="text-transparent bg-clip-text bg-gradient-to-r from-lab-accent to-lab-darkAccent">About</span> Me
            </h1>
          </div>
          
          <!-- ID 卡片装饰 -->
          <div class="hidden md:block">
             <div class="bg-slate-100 dark:bg-slate-900 border border-slate-200 dark:border-slate-800 p-4 min-w-[200px] transform rotate-3 hover:rotate-0 transition-transform duration-300">
                <div class="flex justify-between items-center mb-2 border-b border-slate-300 dark:border-slate-700 pb-2">
                   <span class="text-[10px] font-bold">ID_CARD</span>
                   <div class="w-2 h-2 bg-green-500 rounded-full"></div>
                </div>
                <div class="text-xs space-y-1">
                   <div class="flex justify-between"><span class="text-slate-500">NAME:</span> <span>AUGUST</span></div>
                   <div class="flex justify-between"><span class="text-slate-500">ROLE:</span> <span>DEV</span></div>
                   <div class="flex justify-between"><span class="text-slate-500">LEVEL:</span> <span>ADMIN</span></div>
                </div>
                <div class="mt-2 pt-2 border-t border-slate-300 dark:border-slate-700">
                   <div class="h-8 bg-slate-300 dark:bg-slate-700 w-full opacity-50 barcode"></div>
                </div>
             </div>
          </div>
        </div>
      </header>

      <!-- 主要内容区 -->
      <div v-if="!loading && profile" class="grid grid-cols-1 lg:grid-cols-12 gap-12">
        <!-- 左侧：个人档案 -->
        <div class="lg:col-span-4 space-y-8">
           <!-- 头像卡片 -->
           <div class="bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 p-1 relative group overflow-hidden">
              <div class="relative aspect-square bg-slate-100 dark:bg-slate-900 overflow-hidden">
                 <!-- 占位符或实际头像 -->
                 <div class="w-full h-full flex items-center justify-center bg-gradient-to-br from-slate-200 to-slate-300 dark:from-slate-800 dark:to-slate-900">
                    <span class="text-6xl">👨‍💻</span>
                 </div>
                 
                 <!-- 扫描线动画 -->
                 <div class="absolute inset-0 bg-lab-accent/20 h-1 top-0 animate-scan"></div>
                 
                 <!-- 角标 -->
                 <div class="absolute top-2 left-2 text-[10px] bg-black text-white px-1 font-bold">IMG_001</div>
              </div>
              
              <!-- 个人基本信息 -->
              <div class="p-6 text-center border-t border-slate-200 dark:border-slate-800 mt-1">
                 <h2 class="text-2xl font-black uppercase mb-1">{{ profile.name }}</h2>
                 <p class="text-lab-darkAccent text-sm font-bold uppercase tracking-widest mb-4">{{ profile.title }}</p>
                 
                 <div class="flex justify-center gap-4">
                    <a v-if="profile.github_url" :href="profile.github_url" target="_blank" class="p-2 bg-slate-100 dark:bg-slate-800 hover:bg-lab-accent hover:text-black transition-colors">
                       <span class="sr-only">GitHub</span>
                       <svg class="w-5 h-5" fill="currentColor" viewBox="0 0 24 24"><path d="M12 0c-6.626 0-12 5.373-12 12 0 5.302 3.438 9.8 8.207 11.387.599.111.793-.261.793-.577v-2.234c-3.338.726-4.033-1.416-4.033-1.416-.546-1.387-1.333-1.756-1.333-1.756-1.089-.745.083-.729.083-.729 1.205.084 1.839 1.237 1.839 1.237 1.07 1.834 2.807 1.304 3.492.997.107-.775.418-1.305.762-1.604-2.665-.305-5.467-1.334-5.467-5.931 0-1.311.469-2.381 1.236-3.221-.124-.303-.535-1.524.117-3.176 0 0 1.008-.322 3.301 1.23.957-.266 1.983-.399 3.003-.404 1.02.005 2.047.138 3.006.404 2.291-1.552 3.297-1.23 3.297-1.23.653 1.653.242 2.874.118 3.176.77.84 1.235 1.911 1.235 3.221 0 4.609-2.807 5.624-5.479 5.921.43.372.823 1.102.823 2.222v3.293c0 .319.192.694.801.576 4.765-1.589 8.199-6.086 8.199-11.386 0-6.627-5.373-12-12-12z"/></svg>
                    </a>
                    <a href="mailto:hello@august.lab" class="p-2 bg-slate-100 dark:bg-slate-800 hover:bg-lab-accent hover:text-black transition-colors">
                       <span class="sr-only">Email</span>
                       <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 4.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z" /></svg>
                    </a>
                 </div>
              </div>
           </div>

           <!-- 联系终端 -->
           <div class="bg-slate-900 text-slate-300 p-6 font-mono text-sm border-l-4 border-lab-accent">
              <div class="mb-4 text-xs text-slate-500 uppercase">>> Contact_Protocol</div>
              <div class="space-y-2">
                 <p><span class="text-lab-accent">$</span> echo "Let's build together"</p>
                 <p><span class="text-lab-accent">$</span> mail -s "Project Inquiry"</p>
                 <a href="mailto:hello@august.lab" class="inline-block mt-2 px-4 py-2 border border-lab-accent text-lab-accent hover:bg-lab-accent hover:text-black transition-colors uppercase font-bold">
                    INITIATE_CONTACT
                 </a>
              </div>
           </div>
        </div>

        <!-- 右侧：详细信息 -->
        <div class="lg:col-span-8 space-y-12">
           <!-- Bio -->
           <section>
              <h2 class="text-2xl font-bold uppercase mb-6 flex items-center gap-2">
                 <span class="w-2 h-2 bg-lab-accent"></span>
                 Bio_Data
              </h2>
              <div class="bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 p-8 leading-relaxed text-slate-600 dark:text-slate-300 text-lg">
                 <div v-html="renderedBio"></div>
              </div>
           </section>

           <!-- 技能矩阵 -->
           <section>
              <h2 class="text-2xl font-bold uppercase mb-6 flex items-center gap-2">
                 <span class="w-2 h-2 bg-lab-accent"></span>
                 Skill_Matrix
              </h2>
              
              <div v-if="skillsByCategory" class="grid grid-cols-1 md:grid-cols-2 gap-8">
                 <div v-for="(skills, category) in skillsByCategory" :key="category" class="bg-white dark:bg-[#1f2833] border border-slate-200 dark:border-slate-800 p-6">
                    <h3 class="font-bold uppercase mb-4 text-sm tracking-wider border-b border-slate-100 dark:border-slate-700 pb-2">
                       {{ getCategoryDisplayName(category) }}
                    </h3>
                    <div class="space-y-4">
                       <div v-for="skill in skills" :key="skill.name">
                          <div class="flex justify-between text-xs mb-1">
                             <span class="font-bold">{{ skill.name }}</span>
                             <span class="text-lab-darkAccent">{{ skill.level }}%</span>
                          </div>
                          <div class="h-1.5 bg-slate-100 dark:bg-slate-800 w-full overflow-hidden">
                             <div 
                                class="h-full bg-lab-accent transition-all duration-1000 ease-out"
                                :style="{ width: animatedSkills[skill.name] + '%' }"
                             ></div>
                          </div>
                       </div>
                    </div>
                 </div>
              </div>
           </section>
        </div>
      </div>
      
      <!-- 加载状态 -->
      <div v-if="loading" class="flex flex-col items-center justify-center py-20 text-slate-400 font-mono">
         <div class="animate-spin h-8 w-8 border-2 border-lab-accent border-t-transparent rounded-full mb-4"></div>
         <p>> LOADING_PROFILE...</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { profileAPI } from '../../shared/api'
import type { Profile, Skill } from '../../shared/types'

// State
const profile = ref<Profile | null>(null)
const loading = ref(true)
const animatedSkills = ref<Record<string, number>>({})

// Computed
const skillsByCategory = computed(() => {
  if (!profile.value?.skills) return {}
  const categories: Record<string, Skill[]> = {}
  profile.value.skills.forEach(skill => {
    if (!categories[skill.category]) categories[skill.category] = []
    categories[skill.category].push(skill)
  })
  // Sort by level desc
  Object.keys(categories).forEach(cat => categories[cat].sort((a, b) => b.level - a.level))
  return categories
})

const renderedBio = computed(() => {
  if (!profile.value?.bio) return '<p>LOADING_BIO_ERROR: DATA_MISSING</p>'
  return profile.value.bio.split('\n').map(p => `<p class="mb-4">${p}</p>`).join('')
})

// Methods
const getCategoryDisplayName = (cat: string) => {
  const map: Record<string, string> = {
    'frontend': 'FRONTEND_DEV', 'backend': 'BACKEND_OPS', 'database': 'DATA_STORE',
    'devops': 'INFRASTRUCTURE', 'tools': 'TOOLCHAIN', 'design': 'UI/UX_DESIGN'
  }
  return map[cat] || cat.toUpperCase()
}

const loadProfile = async () => {
  try {
    loading.value = true
    const response = await profileAPI.get()
    profile.value = response.data
    
    // Initialize animation
    if (profile.value.skills) {
      profile.value.skills.forEach(s => animatedSkills.value[s.name] = 0)
      nextTick(() => {
        setTimeout(() => {
          profile.value?.skills.forEach(s => animatedSkills.value[s.name] = s.level)
        }, 500)
      })
    }
  } catch (err) {
    console.error('System Error:', err)
  } finally {
    loading.value = false
  }
}

onMounted(loadProfile)
</script>

<style scoped>
.barcode {
  background-image: linear-gradient(90deg, 
    #000 10%, transparent 10%, transparent 15%, 
    #000 15%, #000 18%, transparent 18%, transparent 25%,
    #000 25%, #000 30%, transparent 30%, transparent 35%,
    #000 35%, #000 45%, transparent 45%, transparent 50%,
    #000 50%, #000 60%, transparent 60%, transparent 65%,
    #000 65%, #000 75%, transparent 75%, transparent 80%,
    #000 80%, #000 90%, transparent 90%
  );
}
.dark .barcode {
  background-image: linear-gradient(90deg, 
    #fff 10%, transparent 10%, transparent 15%, 
    #fff 15%, #fff 18%, transparent 18%, transparent 25%,
    #fff 25%, #fff 30%, transparent 30%, transparent 35%,
    #fff 35%, #fff 45%, transparent 45%, transparent 50%,
    #fff 50%, #fff 60%, transparent 60%, transparent 65%,
    #fff 65%, #fff 75%, transparent 75%, transparent 80%,
    #fff 80%, #fff 90%, transparent 90%
  );
}
</style>
