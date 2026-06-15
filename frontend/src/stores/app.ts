import { defineStore } from 'pinia'
import { ref } from 'vue'

export const useAppStore = defineStore('app', () => {
  const musicPlaying = ref(false)
  const rainActive = ref(false)

  function toggleMusic() {
    musicPlaying.value = !musicPlaying.value
  }

  function toggleRain() {
    rainActive.value = !rainActive.value
  }

  return { musicPlaying, rainActive, toggleMusic, toggleRain }
})
