<script setup lang="ts">
import { useRoute } from 'vue-router'
import { computed } from 'vue'
import SideNav from './components/SideNav.vue'
import MusicPlayer from './components/MusicPlayer.vue'
import SearchBar from './components/SearchBar.vue'
import RainEffect from './components/RainEffect.vue'
import { useAppStore } from './stores/app'

const route = useRoute()
const isHero = computed(() => route.name === 'hero')
const store = useAppStore()
</script>

<template>
  <div class="app-layout" :class="{ 'has-sidenav': !isHero }">
    <SideNav v-if="!isHero" />
    <main class="main-content">
      <!-- 右上角搜索按钮 -->
      <div v-if="!isHero" class="top-bar">
        <SearchBar />
      </div>
      <!-- 呼吸光效背景 -->
      <div class="breath-bg"></div>
      <router-view />
    </main>
    <MusicPlayer v-if="!isHero" />
    <RainEffect v-if="!isHero" :active="store.rainActive" />
  </div>
</template>

<style scoped>
.app-layout {
  min-height: 100vh;
}

.app-layout.has-sidenav {
  display: flex;
}

.main-content {
  flex: 1;
  min-width: 0;
  position: relative;
}

.top-bar {
  position: fixed;
  top: 1rem;
  right: 1.5rem;
  z-index: 40;
}

/* 呼吸光效背景 */
.breath-bg {
  position: fixed;
  inset: 0;
  z-index: -1;
  background: var(--color-bg);
  overflow: hidden;
}

.breath-bg::before,
.breath-bg::after {
  content: '';
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.12;
  animation: breathe 8s ease-in-out infinite;
}

.breath-bg::before {
  width: 600px;
  height: 600px;
  background: #3b82f6;
  top: -200px;
  right: -100px;
}

.breath-bg::after {
  width: 500px;
  height: 500px;
  background: #8b5cf6;
  bottom: -200px;
  left: -100px;
  animation-delay: -4s;
}

@keyframes breathe {
  0%, 100% {
    transform: scale(1) translate(0, 0);
    opacity: 0.06;
  }
  25% {
    transform: scale(1.1) translate(30px, -20px);
    opacity: 0.14;
  }
  50% {
    transform: scale(1.05) translate(-20px, 30px);
    opacity: 0.08;
  }
  75% {
    transform: scale(1.15) translate(-30px, -20px);
    opacity: 0.16;
  }
}
</style>
