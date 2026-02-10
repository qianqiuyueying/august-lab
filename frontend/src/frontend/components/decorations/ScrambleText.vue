<template>
  <span class="font-mono inline-block">
    {{ displayText }}
  </span>
</template>

<script setup lang="ts">
import { ref, watch, onMounted } from 'vue'

const props = defineProps<{
  text: string
  revealDuration?: number
  scrambleSpeed?: number
}>()

const displayText = ref('')
const chars = '!<>-_\\/[]{}—=+*^?#________'

const scramble = () => {
  const targetText = props.text
  const duration = props.revealDuration || 1500
  const speed = props.scrambleSpeed || 50
  const steps = duration / speed
  let currentStep = 0
  
  const interval = setInterval(() => {
    let result = ''
    for (let i = 0; i < targetText.length; i++) {
      if (i < (currentStep / steps) * targetText.length) {
        result += targetText[i]
      } else {
        result += chars[Math.floor(Math.random() * chars.length)]
      }
    }
    displayText.value = result
    currentStep++
    
    if (currentStep > steps) {
      clearInterval(interval)
      displayText.value = targetText
    }
  }, speed)
}

watch(() => props.text, scramble)
onMounted(scramble)
</script>
