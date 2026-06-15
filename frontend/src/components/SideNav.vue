<script setup lang="ts">
import { useAppStore } from '../stores/app'
import { useRouter, useRoute } from 'vue-router'

const store = useAppStore()
const router = useRouter()
const route = useRoute()

const navItems = [
  { icon: '🏠', label: '首页', to: '/home' },
  { icon: '🏷️', label: '标签分类', to: '/tags' },
  { icon: '✍️', label: '发布', to: '/editor' },
  { icon: '👤', label: '个人主页', to: '/profile' },
  { icon: '🧰', label: '百宝箱', to: '/toolbox' },
]

function navigate(to: string) {
  router.push(to)
}
</script>

<template>
  <nav class="sidenav">
    <!-- 顶部：回到 Hero -->
    <button class="nav-item top-btn" @click="router.push('/')" title="回到首页">
      🌙
    </button>

    <!-- 导航图标 -->
    <div class="nav-items">
      <button
        v-for="item in navItems"
        :key="item.to"
        class="nav-item"
        :class="{ active: route.path === item.to }"
        @click="navigate(item.to)"
        :title="item.label"
      >
        {{ item.icon }}
      </button>
    </div>

    <!-- 底部按钮 -->
    <div class="nav-bottom">
      <button
        class="nav-item"
        :class="{ active: store.rainActive }"
        @click="store.toggleRain"
        title="下雨白噪音"
      >
        {{ store.rainActive ? '🌧️' : '💧' }}
      </button>
      <button
        class="nav-item"
        :class="{ active: store.musicPlaying }"
        @click="store.toggleMusic"
        title="音乐播放器"
      >
        {{ store.musicPlaying ? '🎵' : '🎶' }}
      </button>
    </div>
  </nav>
</template>

<style scoped>
.sidenav {
  width: 56px;
  min-height: 100vh;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  padding: 0.8rem 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  position: sticky;
  top: 0;
  height: 100vh;
  z-index: 50;
}

.top-btn {
  margin-bottom: 0.8rem;
  font-size: 1.1rem;
}

.nav-items {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
}

.nav-item {
  width: 44px;
  height: 44px;
  border: none;
  background: none;
  border-radius: 50%;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.25rem;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.nav-item:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.nav-item.active {
  background: var(--color-primary);
  color: #fff;
}

.nav-bottom {
  margin-top: auto;
  padding-top: 0.5rem;
  display: flex;
  flex-direction: column;
  align-items: center;
}

@media (max-width: 768px) {
  .sidenav {
    display: none;
  }
}
</style>
