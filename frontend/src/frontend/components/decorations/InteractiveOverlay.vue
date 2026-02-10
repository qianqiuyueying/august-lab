<template>
  <div class="fixed inset-0 pointer-events-none z-[100] overflow-hidden">
    <!-- 1. 自定义光标 (Custom Cursor) -->
    <div 
      class="custom-cursor hidden md:block fixed w-6 h-6 rounded-full border border-slate-900 dark:border-lab-accent mix-blend-difference pointer-events-none transition-transform duration-100 ease-out z-[100]"
      :class="{ 'scale-150 bg-slate-900/10 dark:bg-lab-accent/10': isHovering }"
      :style="{ left: `${cursorX}px`, top: `${cursorY}px`, transform: `translate(-50%, -50%) scale(${isHovering ? 1.5 : 1})` }"
    >
      <div class="absolute inset-0 flex items-center justify-center">
        <div class="w-1 h-1 bg-slate-900 dark:bg-lab-accent rounded-full"></div>
      </div>
    </div>

    <!-- 2. 点击特效 (Click Ripples) -->
    <transition-group name="ripple">
      <div
        v-for="ripple in ripples"
        :key="ripple.id"
        class="absolute rounded-full border border-slate-900/30 dark:border-lab-accent/50 pointer-events-none"
        :style="{
          left: `${ripple.x}px`,
          top: `${ripple.y}px`,
          width: `${ripple.size}px`,
          height: `${ripple.size}px`,
          transform: 'translate(-50%, -50%)'
        }"
      ></div>
    </transition-group>

    <!-- 3. 漂浮符号 (Floating Symbols) -->
    <div class="absolute inset-0 w-full h-full">
      <div
        v-for="(symbol, index) in symbols"
        :key="index"
        class="absolute text-slate-400/20 dark:text-lab-accent/20 font-mono text-sm select-none pointer-events-none transition-all duration-[2000ms] ease-in-out"
        :style="{
          left: `${symbol.x}%`,
          top: `${symbol.y}%`,
          fontSize: `${symbol.size}px`,
          animation: `float ${symbol.duration}s infinite ease-in-out alternate`,
          animationDelay: `${symbol.delay}s`,
          transform: `rotate(${symbol.rotation}deg)`
        }"
      >
        {{ symbol.char }}
      </div>
    </div>

    <!-- 4. 看板娘 (Mascot) - 'Bot-01' -->
    <div
      class="fixed bottom-8 right-8 pointer-events-auto transition-all duration-500 ease-in-out transform"
      :class="[
        mascotState === 'hidden' ? 'translate-y-20 opacity-0' : 'translate-y-0 opacity-100',
        mascotState === 'peeking' ? 'translate-x-10' : '',
        mascotState === 'jumping' ? 'animate-bounce-custom' : ''
      ]"
      @mouseenter="interactMascot"
      @click="jumpMascot"
    >
      <!-- 机器人身体 -->
      <div class="relative w-16 h-16 group cursor-pointer">
        <!-- 悬浮动画容器 -->
        <div class="animate-float-slow w-full h-full">
          <!-- 主体 -->
          <div class="absolute inset-0 bg-white dark:bg-[#1f2833] border-2 border-slate-900 dark:border-lab-accent rounded-xl shadow-lg flex items-center justify-center overflow-hidden transition-colors duration-300">
            <!-- 脸部屏幕 -->
            <div class="w-10 h-8 bg-slate-900 dark:bg-black rounded-md flex items-center justify-center gap-1 p-1 relative overflow-hidden">
              <!-- 扫描线效果 -->
              <div class="absolute inset-0 bg-gradient-to-b from-transparent via-lab-accent/10 to-transparent animate-scan"></div>
              
              <!-- 眼睛 (根据状态变化) -->
              <template v-if="mascotMood === 'happy'">
                <div class="w-2 h-2 bg-lab-accent rounded-full animate-blink"></div>
                <div class="w-2 h-2 bg-lab-accent rounded-full animate-blink delay-75"></div>
              </template>
              <template v-else-if="mascotMood === 'sleeping'">
                <div class="text-lab-accent text-[8px] font-bold">zZ</div>
              </template>
              <template v-else-if="mascotMood === 'surprised'">
                <div class="w-3 h-3 border-2 border-lab-accent rounded-full"></div>
                <div class="w-3 h-3 border-2 border-lab-accent rounded-full"></div>
              </template>
              <template v-else> <!-- Normal -->
                <div class="w-1.5 h-3 bg-lab-accent rounded-sm animate-blink"></div>
                <div class="w-1.5 h-3 bg-lab-accent rounded-sm animate-blink delay-100"></div>
              </template>
            </div>
          </div>

          <!-- 天线 -->
          <div class="absolute -top-3 left-1/2 -translate-x-1/2 w-1 h-3 bg-slate-900 dark:bg-lab-accent"></div>
          <div class="absolute -top-4 left-1/2 -translate-x-1/2 w-2 h-2 bg-red-500 rounded-full animate-pulse shadow-[0_0_5px_rgba(239,68,68,0.8)]"></div>
          
          <!-- 手臂 (简单的悬浮圆点) -->
          <div class="absolute top-1/2 -left-2 w-3 h-3 bg-slate-900 dark:bg-lab-accent rounded-full animate-wave-left"></div>
          <div class="absolute top-1/2 -right-2 w-3 h-3 bg-slate-900 dark:bg-lab-accent rounded-full animate-wave-right"></div>
        </div>
        
        <!-- 对话气泡 -->
        <transition name="pop">
          <div v-if="showBubble" class="absolute -top-12 right-0 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 px-3 py-1 rounded-lg shadow-md text-xs font-mono whitespace-nowrap dark:text-gray-200">
            {{ bubbleText }}
            <div class="absolute bottom-[-5px] right-4 w-2 h-2 bg-white dark:bg-slate-800 border-b border-r border-slate-200 dark:border-slate-700 transform rotate-45"></div>
          </div>
        </transition>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, onUnmounted, reactive } from 'vue'

// --- 光标逻辑 ---
const cursorX = ref(0)
const cursorY = ref(0)
const isHovering = ref(false)

const updateCursor = (e: MouseEvent) => {
  cursorX.value = e.clientX
  cursorY.value = e.clientY
  
  // 检测是否悬停在可交互元素上
  const target = e.target as HTMLElement
  const clickable = target.closest('a, button, input, select, textarea, .cursor-pointer')
  isHovering.value = !!clickable
}

// --- 点击波纹逻辑 ---
interface Ripple {
  id: number
  x: number
  y: number
  size: number
}
const ripples = ref<Ripple[]>([])
let rippleId = 0

const createRipple = (e: MouseEvent) => {
  const id = rippleId++
  ripples.value.push({
    id,
    x: e.clientX,
    y: e.clientY,
    size: 20
  })

  // 移除波纹
  setTimeout(() => {
    ripples.value = ripples.value.filter(r => r.id !== id)
  }, 600)
}

// --- 漂浮符号逻辑 ---
const symbols = ref([
  { char: '{ }', x: 10, y: 20, size: 24, duration: 4, delay: 0, rotation: 15 },
  { char: '</>', x: 80, y: 15, size: 20, duration: 5, delay: 1, rotation: -10 },
  { char: '//', x: 20, y: 80, size: 28, duration: 6, delay: 2, rotation: 5 },
  { char: '01', x: 90, y: 70, size: 18, duration: 7, delay: 0.5, rotation: 0 },
  { char: '⚡', x: 50, y: 50, size: 30, duration: 8, delay: 1.5, rotation: 20 },
  { char: '⚙️', x: 15, y: 40, size: 22, duration: 5.5, delay: 3, rotation: 45 },
])

// --- 看板娘逻辑 ---
type MascotState = 'hidden' | 'visible' | 'peeking' | 'jumping'
type MascotMood = 'normal' | 'happy' | 'sleeping' | 'surprised'

const mascotState = ref<MascotState>('hidden') // 默认隐藏，偶尔出现
const mascotMood = ref<MascotMood>('normal')
const showBubble = ref(false)
const bubbleText = ref('系统正常运行中...')

// 随机出现逻辑
const startMascotLoop = () => {
  // 初始延迟出现
  setTimeout(() => {
    mascotState.value = 'visible'
    showBubbleText('系统启动完毕')
    
    // 5秒后隐藏
    setTimeout(() => {
       mascotState.value = 'hidden'
    }, 5000)
  }, 2000)

  // 循环检查
  setInterval(() => {
    const random = Math.random()
    
    // 如果当前隐藏，有 30% 概率出现
    if (mascotState.value === 'hidden') {
      if (random > 0.7) {
        mascotState.value = 'visible'
        // 随机停留 5-10 秒
        setTimeout(() => {
          // 只有当用户没有在交互时才隐藏（这里简单处理，直接隐藏）
           mascotState.value = 'hidden'
        }, 5000 + Math.random() * 5000)
      }
    } 
    // 如果当前显示，有 40% 概率做动作
    else if (mascotState.value === 'visible') {
       if (random > 0.6) {
          // 随机动作
          if (random > 0.8) {
             mascotMood.value = 'sleeping'
             showBubbleText('Zzz...')
             setTimeout(() => { mascotMood.value = 'normal' }, 3000)
          } else {
             mascotState.value = 'peeking' // 往旁边躲一下
             setTimeout(() => { mascotState.value = 'visible' }, 2000)
          }
       }
    }
  }, 5000)
}

const showBubbleText = (text: string) => {
  bubbleText.value = text
  showBubble.value = true
  setTimeout(() => {
    showBubble.value = false
  }, 3000)
}

const interactMascot = () => {
  mascotMood.value = 'happy'
  showBubbleText('你好呀！')
  setTimeout(() => {
    mascotMood.value = 'normal'
  }, 2000)
}

const jumpMascot = () => {
  mascotState.value = 'jumping'
  mascotMood.value = 'surprised'
  showBubbleText('哇！')
  createConfetti() // 简单的粒子效果
  setTimeout(() => {
    mascotState.value = 'visible'
    mascotMood.value = 'normal'
  }, 1000)
}

// 简单的五彩纸屑效果
const createConfetti = () => {
    // 这里可以是一个简单的小逻辑，或者留空
}

onMounted(() => {
  window.addEventListener('mousemove', updateCursor)
  window.addEventListener('click', createRipple)
  // 初始进场 logic moved to startMascotLoop
  startMascotLoop()
})

onUnmounted(() => {
  window.removeEventListener('mousemove', updateCursor)
  window.removeEventListener('click', createRipple)
})
</script>

<style scoped>
/* 浮动动画 */
@keyframes float {
  0% { transform: translateY(0px) rotate(0deg); }
  50% { transform: translateY(-20px) rotate(5deg); }
  100% { transform: translateY(0px) rotate(0deg); }
}

@keyframes float-slow {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-5px); }
}
.animate-float-slow {
  animation: float-slow 3s ease-in-out infinite;
}

/* 眨眼动画 */
@keyframes blink {
  0%, 90%, 100% { transform: scaleY(1); }
  95% { transform: scaleY(0.1); }
}
.animate-blink {
  animation: blink 4s infinite;
}

/* 扫描线动画 */
@keyframes scan {
  0% { transform: translateY(-100%); }
  100% { transform: translateY(100%); }
}
.animate-scan {
  animation: scan 2s linear infinite;
}

/* 波纹动画 */
.ripple-enter-active {
  transition: all 0.6s ease-out;
}
.ripple-enter-from {
  opacity: 1;
  transform: scale(0);
}
.ripple-enter-to {
  opacity: 0;
  transform: scale(2.5);
}
.ripple-leave-active {
  transition: all 0.1s ease-out;
}
.ripple-leave-to {
  opacity: 0;
}

/* 气泡动画 */
.pop-enter-active, .pop-leave-active {
  transition: all 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275);
}
.pop-enter-from, .pop-leave-to {
  opacity: 0;
  transform: scale(0.5) translateY(10px);
}

/* 自定义跳跃 */
@keyframes bounce-custom {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-20px); }
}
.animate-bounce-custom {
  animation: bounce-custom 0.5s ease-in-out;
}

/* 手臂摆动 */
@keyframes wave-left {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(-10deg); }
}
@keyframes wave-right {
    0%, 100% { transform: rotate(0deg); }
    50% { transform: rotate(10deg); }
}
.animate-wave-left { animation: wave-left 2s infinite ease-in-out; }
.animate-wave-right { animation: wave-right 2s infinite ease-in-out; }
</style>