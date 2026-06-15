<script setup lang="ts">
import { ref, onMounted, onUnmounted, watch, nextTick } from 'vue'
import { useAppStore } from '../stores/app'
import APlayer from 'aplayer'
import 'aplayer/dist/APlayer.min.css'

const store = useAppStore()
const playerRef = ref<HTMLDivElement | null>(null)
let player: any = null

const SILENT = 'data:audio/mp3;base64,SUQzBAAAAAAAI1RTU0UAAAAPAAADTGF2ZjU4Ljc2LjEwMAAAAAAAAAAAAAAA//tQAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAWGluZwAAAA8AAAACAAABhgC7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7u7//////////////////////////////////////////////////////////////////8AAAAATGF2YzU4LjEzAAAAAAAAAAAAAAAAJAAAAAAAAAAAAYYoRB0AAAAAAAAAAAAAAAAAAAAA//tQAAAPpABtAGsAABIAABpJlMmUyZTJlMmUyZTJlMmUyZTJlMmUyZTJlMmUyZTJlMmUyZTJlMmUyZTJlMmUyZTJlMmUyZTJlMmUyZQ=='

const songList = ref<{ name: string; artist: string; url: string }[]>([])
const currentIndex = ref(0)
const showList = ref(false)
const isPlaying = ref(false)
const playMode = ref<'list' | 'single' | 'random'>('list')

const modeIcons = {
  list: { icon: '→', label: '顺序播放' },
  single: { icon: '↻', label: '单曲循环' },
  random: { icon: '⤮', label: '随机播放' },
}

const currentSong = ref({ name: '暂无歌曲', artist: '', url: '' })

async function loadMusic() {
  try {
    const res = await fetch('/api/music/list')
    if (res.ok) {
      const data = await res.json()
      if (data.length > 0) {
        songList.value = data
        currentSong.value = data[0]
      }
    }
  } catch {}
}

function initPlayer() {
  if (!playerRef.value || player) return

  const audio = songList.value.length > 0
    ? songList.value.map(s => ({ name: s.name, artist: s.artist, url: s.url, cover: '' }))
    : [{ name: '暂无歌曲', artist: '请将MP3放入music目录', url: SILENT, cover: '' }]

  player = new APlayer({
    container: playerRef.value,
    mini: false,
    autoplay: false,
    theme: '#ef4444',
    loop: 'one',
    order: 'list',
    preload: 'auto',
    volume: 0.7,
    mutex: true,
    listFolded: true,
    listMaxHeight: '0px',
    audio,
  })

  player.on('play', () => {
    isPlaying.value = true
    store.musicPlaying = true
    currentIndex.value = player.list.index
    if (songList.value[player.list.index]) {
      currentSong.value = songList.value[player.list.index]
    }
  })

  player.on('pause', () => {
    isPlaying.value = false
    store.musicPlaying = false
  })

  // 阻止出错自动跳歌
  player.on('error', (e: any) => {
    console.warn('音频加载失败，停止播放')
    player.pause()
    isPlaying.value = false
    store.musicPlaying = false
    // 重置 APlayer 内部跳歌定时器
    if (player.timer) {
      clearTimeout(player.timer)
      player.timer = null
    }
  })
}

function togglePlay() {
  if (!player) return
  player.toggle()
}

function toggleMode() {
  const modes: ('list' | 'single' | 'random')[] = ['list', 'single', 'random']
  const i = modes.indexOf(playMode.value)
  playMode.value = modes[(i + 1) % modes.length]
}

function prevSong() {
  if (songList.value.length === 0) return
  if (playMode.value === 'random') {
    currentIndex.value = Math.floor(Math.random() * songList.value.length)
  } else {
    currentIndex.value = currentIndex.value > 0 ? currentIndex.value - 1 : songList.value.length - 1
  }
  currentSong.value = songList.value[currentIndex.value]
  if (player) { player.list.switch(currentIndex.value); player.play() }
}

function nextSong() {
  if (songList.value.length === 0) return
  if (playMode.value === 'random') {
    currentIndex.value = Math.floor(Math.random() * songList.value.length)
  } else {
    currentIndex.value = currentIndex.value < songList.value.length - 1 ? currentIndex.value + 1 : 0
  }
  currentSong.value = songList.value[currentIndex.value]
  if (player) { player.list.switch(currentIndex.value); player.play() }
}

function playSong(index: number) {
  if (songList.value.length === 0) return
  currentIndex.value = index
  currentSong.value = songList.value[index]
  showList.value = false
  if (player) { player.list.switch(index); player.play() }
}

function blockScroll(e: WheelEvent) { e.stopPropagation() }

onMounted(async () => {
  await loadMusic()
  nextTick(() => { initPlayer() })
})

onUnmounted(() => {
  if (player) { player.destroy(); player = null }
})
</script>

<template>
  <div class="music-panel" :class="{ visible: store.musicPlaying }">
    <!-- 当前歌曲 -->
    <div class="now-playing">
      <span class="np-icon">♪</span>
      <div class="np-info">
        <span class="np-name">{{ currentSong.name }}</span>
        <span class="np-artist">{{ currentSong.artist }}</span>
      </div>
    </div>

    <!-- 控制栏 -->
    <div class="player-controls">
      <button class="ctrl-btn mode-btn" @click="toggleMode" :title="modeIcons[playMode].label">
        {{ modeIcons[playMode].icon }}
      </button>
      <button class="ctrl-btn" @click="prevSong" title="上一首">⏮</button>
      <button class="ctrl-btn play-btn" @click="togglePlay">{{ isPlaying ? '⏸' : '▶' }}</button>
      <button class="ctrl-btn" @click="nextSong" title="下一首">⏭</button>
      <button class="ctrl-btn list-btn" @click="showList = !showList" title="播放列表">≡</button>
    </div>

    <!-- 歌曲列表 -->
    <div class="song-list" v-show="showList" @wheel="blockScroll">
      <div class="list-header">播放列表 ({{ songList.length }}首) · {{ modeIcons[playMode].label }}</div>
      <div v-if="songList.length === 0" class="list-empty">将 MP3 文件放入 backend/music/ 目录</div>
      <div
        v-for="(song, i) in songList"
        :key="i"
        class="song-item"
        :class="{ active: currentIndex === i }"
        @click="playSong(i)"
      >
        <span class="song-idx">{{ currentIndex === i && isPlaying ? '♪' : i + 1 }}</span>
        <div class="song-info">
          <span class="song-name">{{ song.name }}</span>
          <span class="song-artist">{{ song.artist }}</span>
        </div>
      </div>
    </div>

    <div ref="playerRef" class="aplayer-mount"></div>
  </div>
</template>

<style scoped>
.music-panel {
  position: fixed;
  bottom: -500px;
  left: 72px;
  width: 320px;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
  z-index: 1000;
  overflow: hidden;
  opacity: 0;
  transition: bottom 0.35s cubic-bezier(0.4, 0, 0.2, 1), opacity 0.3s ease;
  pointer-events: none;
}

.music-panel.visible {
  bottom: 1.5rem;
  opacity: 1;
  pointer-events: auto;
}

.aplayer-mount { height: 0; overflow: hidden; }
.aplayer-mount :deep(.aplayer) { display: none; }

.now-playing {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.7rem 1rem;
  background: linear-gradient(135deg, #7f1d1d, #991b1b);
  color: #fff;
}

.np-icon {
  font-size: 1.3rem;
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #ef4444;
  border-radius: 50%;
  flex-shrink: 0;
}

.np-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }

.np-name {
  font-size: 0.95rem;
  font-weight: 600;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.np-artist { font-size: 0.75rem; color: #94a3b8; }

.player-controls {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.6rem 0.8rem;
  background: #7f1d1d;
}

.ctrl-btn {
  width: 38px;
  height: 38px;
  border-radius: 50%;
  border: none;
  background: rgba(255, 255, 255, 0.1);
  color: #fff;
  font-size: 1rem;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.ctrl-btn:hover { background: rgba(255, 255, 255, 0.25); }

.play-btn {
  width: 46px;
  height: 46px;
  font-size: 1.3rem;
  background: #ef4444;
}

.play-btn:hover { background: #dc2626; }

.mode-btn, .list-btn {
  width: 34px;
  height: 34px;
  background: transparent;
  color: #94a3b8;
  font-size: 1.2rem;
}

.mode-btn:hover, .list-btn:hover { color: #fff; }

.song-list {
  max-height: 240px;
  overflow-y: auto;
  overscroll-behavior: contain;
  background: var(--color-surface);
}

.list-header {
  padding: 0.5rem 0.8rem;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  background: var(--color-bg);
  border-bottom: 1px solid var(--color-border);
  position: sticky;
  top: 0;
  z-index: 1;
}

.list-empty {
  padding: 1.5rem;
  text-align: center;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.song-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.5rem 0.8rem;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid var(--color-border);
}

.song-item:last-child { border-bottom: none; }
.song-item:hover { background: var(--color-bg); }
.song-item.active { background: #fef2f2; }

.song-idx {
  width: 24px;
  text-align: center;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.song-item.active .song-idx { color: #ef4444; font-weight: 700; }

.song-info { flex: 1; min-width: 0; display: flex; flex-direction: column; }

.song-name {
  font-size: 0.9rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.song-artist { font-size: 0.75rem; color: var(--color-text-secondary); }
</style>
