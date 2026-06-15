<script setup lang="ts">
import { ref, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'

const router = useRouter()
const showContent = ref(false)

// 自定义背景图片URL，留空使用默认渐变
const bgImage = '../public/background.jpg'

const lines = [
  '你好，欢迎来到我的博客',
  '这里是代码与文字交汇的地方',
  '向下滚动 进入博客',
]
const currentLine = ref(0)
const currentText = ref('')
const isDeleting = ref(false)

let typeTimer: number

function typeEffect() {
  const line = lines[currentLine.value]
  if (!isDeleting.value) {
    currentText.value = line.substring(0, currentText.value.length + 1)
    if (currentText.value === line) {
      setTimeout(() => { isDeleting.value = true }, 2000)
    }
  } else {
    currentText.value = line.substring(0, currentText.value.length - 1)
    if (currentText.value === '') {
      isDeleting.value = false
      currentLine.value = (currentLine.value + 1) % lines.length
    }
  }
  typeTimer = window.setTimeout(typeEffect, isDeleting.value ? 40 : 80)
}

let scrollAccum = 0
let scrollTimer: number

function handleWheel(e: WheelEvent) {
  if (e.deltaY > 0) {
    scrollAccum += e.deltaY
    clearTimeout(scrollTimer)
    scrollTimer = window.setTimeout(() => { scrollAccum = 0 }, 200)
    if (scrollAccum > 120) {
      router.push('/home')
    }
  }
}

onMounted(() => {
  setTimeout(() => { showContent.value = true }, 300)
  typeEffect()
})

onUnmounted(() => {
  clearTimeout(typeTimer)
  clearTimeout(scrollTimer)
})
</script>

<template>
  <div class="hero" @wheel="handleWheel" :style="bgImage ? { backgroundImage: `url(${bgImage})` } : {}">
    <div class="hero-overlay"></div>
    <div class="hero-content" :class="{ visible: showContent }">
      <div class="typewriter">
        <span class="typed-text">{{ currentText }}</span>
        <span class="cursor">|</span>
      </div>
    </div>
    <div class="scroll-hint">↓</div>
  </div>
</template>

<style scoped>
.hero {
  position: relative;
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #0f172a 0%, #1e293b 50%, #0f172a 100%);
  background-size: cover;
  background-position: center;
  overflow: hidden;
}

.hero-overlay {
  position: absolute;
  inset: 0;
  background: radial-gradient(ellipse at center, rgba(59, 130, 246, 0.1) 0%, transparent 70%);
}

.hero-content {
  position: relative;
  z-index: 1;
  text-align: center;
  opacity: 0;
  transform: translateY(30px);
  transition: all 0.8s ease;
}

.hero-content.visible {
  opacity: 1;
  transform: translateY(0);
}

.typewriter {
  font-size: 2rem;
  min-height: 2.5rem;
  text-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  background: linear-gradient(90deg, #60a5fa, #a78bfa, #f472b6, #60a5fa);
  background-size: 200% 100%;
  background-clip: text;
  -webkit-background-clip: text;
  color: transparent;
  animation: gradientShift 4s linear infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  100% { background-position: 200% 50%; }
}

.cursor {
  animation: blink 0.8s infinite;
  color: var(--color-primary);
}

@keyframes blink {
  0%, 50% { opacity: 1; }
  51%, 100% { opacity: 0; }
}

.scroll-hint {
  position: absolute;
  bottom: 2rem;
  left: 50%;
  transform: translateX(-50%);
  color: #64748b;
  font-size: 1rem;
  animation: bounce 2s infinite;
}

@keyframes bounce {
  0%, 100% { transform: translateX(-50%) translateY(0); }
  50% { transform: translateX(-50%) translateY(-6px); }
}
</style>
