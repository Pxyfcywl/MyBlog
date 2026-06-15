<script setup lang="ts">
import { watch, onUnmounted } from 'vue'

const props = defineProps<{ active: boolean }>()

// 雨声音频（内嵌极短循环音频，实际使用时替换为真实雨声文件）
let audio: HTMLAudioElement | null = null

function startRain() {
  if (!audio) {
    // 尝试加载本地雨声文件（放入 public/rain.mp3）
    audio = new Audio('/rain.mp3')
    audio.loop = true
    audio.volume = 0.3
    audio.preload = 'auto'
  }
  audio.play().catch(() => {
    // 浏览器阻止自动播放，需要用户交互后才能播放
    console.warn('雨声播放被浏览器阻止，请点击页面后重试')
  })
}

function stopRain() {
  if (audio) {
    audio.pause()
    audio.currentTime = 0
  }
}

watch(() => props.active, (val) => {
  val ? startRain() : stopRain()
})

onUnmounted(() => {
  if (audio) {
    audio.pause()
    audio = null
  }
})

// 雨滴数据
const drops: { left: number; delay: number; duration: number; opacity: number; width: number }[] = []
for (let i = 0; i < 100; i++) {
  drops.push({
    left: Math.random() * 100,
    delay: Math.random() * 3,
    duration: 0.4 + Math.random() * 0.4,
    opacity: 0.15 + Math.random() * 0.35,
    width: 1 + Math.random() * 1.5,
  })
}
</script>

<template>
  <div class="rain-overlay" :class="{ active }">
    <div
      v-for="(drop, i) in drops"
      :key="i"
      class="raindrop"
      :style="{
        left: drop.left + '%',
        animationDelay: drop.delay + 's',
        animationDuration: drop.duration + 's',
        opacity: drop.opacity,
        width: drop.width + 'px',
      }"
    ></div>
    <!-- 雨雾效果 -->
    <div class="rain-fog"></div>
  </div>
</template>

<style scoped>
.rain-overlay {
  position: fixed;
  inset: 0;
  pointer-events: none;
  z-index: 9990;
  overflow: hidden;
  opacity: 0;
  transition: opacity 1.5s ease;
}

.rain-overlay.active {
  opacity: 1;
}

.raindrop {
  position: absolute;
  top: -30px;
  height: 20px;
  background: linear-gradient(to bottom, transparent, rgba(96, 165, 250, 0.6));
  border-radius: 0 0 2px 2px;
  animation: fall linear infinite;
}

@keyframes fall {
  0% {
    transform: translateY(-30px);
  }
  100% {
    transform: translateY(calc(100vh + 30px));
  }
}

/* 底部雨雾 */
.rain-fog {
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 120px;
  background: linear-gradient(to top, rgba(59, 130, 246, 0.1), transparent);
}
</style>
