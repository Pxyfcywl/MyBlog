<script setup lang="ts">
import { ref, watch, onMounted, onUnmounted, nextTick, computed } from 'vue'
import * as pdfjsLib from 'pdfjs-dist'
import workerUrl from 'pdfjs-dist/build/pdf.worker.min.mjs?url'

pdfjsLib.GlobalWorkerOptions.workerSrc = workerUrl

interface MatchInfo {
  page: number
  keywordIndex: number
  keyword: string
  index: number
}

const HIGHLIGHT_COLORS = [
  { bg: 'rgba(255, 235, 59, 0.45)', border: '#fbc02d' },
  { bg: 'rgba(76, 175, 80, 0.4)', border: '#388e3c' },
  { bg: 'rgba(33, 150, 243, 0.4)', border: '#1565c0' },
  { bg: 'rgba(255, 152, 0, 0.4)', border: '#e65100' },
  { bg: 'rgba(156, 39, 176, 0.35)', border: '#7b1fa2' },
  { bg: 'rgba(244, 67, 54, 0.35)', border: '#c62828' },
  { bg: 'rgba(0, 188, 212, 0.4)', border: '#00838f' },
  { bg: 'rgba(233, 30, 99, 0.35)', border: '#ad1457' },
]

const props = defineProps<{
  file: File | null
  keywords?: string[]
}>()

const emit = defineEmits<{
  (e: 'match-stats', stats: { keyword: string; count: number }[]): void
}>()

// State
const pdfDoc = ref<any>(null)
const currentPage = ref(1)
const totalPages = ref(0)
const scale = ref(1.5)
const currentViewport = ref<any>(null)
const pageTextContents = ref<Record<number, any>>({})
const matches = ref<MatchInfo[]>([])
const keywordMatchIndex = ref<Record<string, number>>({})
const activeKeywordIdx = ref(-1)
const caseSensitive = ref(false)

// Canvas refs
const pdfCanvas = ref<HTMLCanvasElement | null>(null)
const highlightCanvas = ref<HTMLCanvasElement | null>(null)
const textLayerDiv = ref<HTMLDivElement | null>(null)
const viewerEl = ref<HTMLDivElement | null>(null)

// Computed
const activeKeywords = computed(() => props.keywords?.filter(k => k.trim()) || [])

const zoomLevel = computed(() => Math.round(scale.value * 100) + '%')

const keywordStats = computed(() => {
  return activeKeywords.value.map((kw, i) => {
    const kwMatches = matches.value.filter(m => m.keywordIndex === i)
    const key = String(i)
    const current = keywordMatchIndex.value[key] !== undefined
      ? keywordMatchIndex.value[key] + 1
      : (kwMatches.length > 0 ? 1 : 0)
    return {
      keyword: kw,
      index: i,
      color: HIGHLIGHT_COLORS[i % HIGHLIGHT_COLORS.length],
      total: kwMatches.length,
      current,
      isActive: activeKeywordIdx.value === i,
    }
  })
})

const totalMatchCount = computed(() => matches.value.length)

// Watch file changes
watch(() => props.file, async (newFile) => {
  if (newFile) {
    await loadPdf(newFile)
  } else {
    pdfDoc.value = null
    totalPages.value = 0
    matches.value = []
  }
})

// Watch keywords changes
watch(() => props.keywords, () => {
  if (pdfDoc.value) {
    searchAllKeywords()
  }
}, { deep: true })

// Load PDF
async function loadPdf(file: File) {
  const arrayBuffer = await file.arrayBuffer()
  pdfDoc.value = await pdfjsLib.getDocument({ data: arrayBuffer }).promise
  totalPages.value = pdfDoc.value.numPages
  currentPage.value = 1
  pageTextContents.value = {}
  matches.value = {}
  keywordMatchIndex.value = {}
  activeKeywordIdx.value = -1
  await nextTick()
  await renderCurrentPage()
  if (activeKeywords.value.length > 0) {
    searchAllKeywords()
  }
}

// Render page
async function renderCurrentPage() {
  if (!pdfDoc.value) return

  const page = await pdfDoc.value.getPage(currentPage.value)
  const viewport = page.getViewport({ scale: scale.value })
  currentViewport.value = viewport

  const canvas = pdfCanvas.value
  const hlCanvas = highlightCanvas.value
  const textLayer = textLayerDiv.value
  if (!canvas || !hlCanvas || !textLayer) return

  canvas.width = viewport.width
  canvas.height = viewport.height
  hlCanvas.width = viewport.width
  hlCanvas.height = viewport.height
  textLayer.style.width = viewport.width + 'px'
  textLayer.style.height = viewport.height + 'px'

  const ctx = canvas.getContext('2d')!
  await page.render({ canvasContext: ctx, viewport }).promise

  const textContent = await page.getTextContent()
  pageTextContents.value[currentPage.value] = textContent
  renderTextLayer(textContent, viewport)
  drawHighlights()
}

function renderTextLayer(textContent: any, viewport: any) {
  const el = textLayerDiv.value
  if (!el) return
  el.innerHTML = ''

  for (const item of textContent.items) {
    if (!item.str) continue
    const tx = pdfjsLib.Util.transform(viewport.transform, item.transform)
    const fontHeight = Math.sqrt(tx[2] * tx[2] + tx[3] * tx[3])
    const angle = Math.atan2(tx[1], tx[0])

    const span = document.createElement('span')
    span.textContent = item.str
    span.style.left = tx[4] + 'px'
    span.style.top = (tx[5] - fontHeight) + 'px'
    span.style.fontSize = fontHeight + 'px'
    span.style.fontFamily = item.fontName ? item.fontName.replace('+', '') : 'sans-serif'
    if (angle !== 0) span.style.transform = `rotate(${angle}rad)`
    if (item.width > 0) {
      span.style.width = (item.width * viewport.scale) + 'px'
      span.style.letterSpacing = '0px'
    }
    el.appendChild(span)
  }
}

// Draw keyword highlights on current page
function drawHighlights() {
  const hlCanvas = highlightCanvas.value
  const viewport = currentViewport.value
  const textContent = pageTextContents.value[currentPage.value]
  if (!hlCanvas || !viewport || !textContent) return

  const ctx = hlCanvas.getContext('2d')!
  ctx.clearRect(0, 0, hlCanvas.width, hlCanvas.height)

  const keywords = activeKeywords.value
  if (keywords.length === 0) return

  const items = textContent.items
  const fullText = items.map((it: any) => it.str).join('')

  let globalCharOffset = 0
  const itemRanges = items.map((item: any) => {
    const range = {
      item,
      start: globalCharOffset,
      end: globalCharOffset + (item.str ? item.str.length : 0),
    }
    globalCharOffset += item.str ? item.str.length : 0
    return range
  })

  keywords.forEach((keyword, kwIdx) => {
    if (!keyword.trim()) return
    const color = HIGHLIGHT_COLORS[kwIdx % HIGHLIGHT_COLORS.length]
    const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
    const regex = new RegExp(escaped, caseSensitive.value ? 'g' : 'gi')
    let match

    while ((match = regex.exec(fullText)) !== null) {
      const matchStart = match.index
      const matchEnd = matchStart + match[0].length

      for (const range of itemRanges) {
        if (range.end <= matchStart || range.start >= matchEnd) continue
        const item = range.item
        if (!item.str || !item.transform) continue

        const overlapStart = Math.max(matchStart, range.start) - range.start
        const overlapEnd = Math.min(matchEnd, range.end) - range.start
        const itemLen = item.str.length

        const tx = pdfjsLib.Util.transform(viewport.transform, item.transform)
        const fontHeight = Math.sqrt(tx[2] * tx[2] + tx[3] * tx[3])
        const itemWidth = item.width > 0
          ? item.width * viewport.scale
          : fontHeight * item.str.length * 0.6
        const charW = itemWidth / itemLen

        const hlX = tx[4] + charW * overlapStart
        const hlW = charW * (overlapEnd - overlapStart)
        const hlY = tx[5] - fontHeight
        const hlH = fontHeight * 1.05

        ctx.fillStyle = color.bg
        ctx.fillRect(hlX, hlY, hlW, hlH)
        ctx.strokeStyle = color.border
        ctx.lineWidth = 1
        ctx.globalAlpha = 0.6
        ctx.strokeRect(hlX + 0.5, hlY + 0.5, hlW - 1, hlH - 1)
        ctx.globalAlpha = 1.0
      }
    }
  })
}

// Search all keywords across all pages
async function searchAllKeywords() {
  if (!pdfDoc.value) return

  const keywords = activeKeywords.value
  const allMatches: MatchInfo[] = []

  if (keywords.length === 0) {
    matches.value = []
    drawHighlights()
    emitMatchStats()
    return
  }

  // Ensure all pages have text content
  for (let p = 1; p <= totalPages.value; p++) {
    if (!pageTextContents.value[p]) {
      const page = await pdfDoc.value.getPage(p)
      const textContent = await page.getTextContent()
      pageTextContents.value[p] = textContent
    }
  }

  for (let p = 1; p <= totalPages.value; p++) {
    const textContent = pageTextContents.value[p]
    if (!textContent) continue
    const fullText = textContent.items.map((it: any) => it.str).join('')

    keywords.forEach((keyword, kwIdx) => {
      if (!keyword.trim()) return
      const escaped = keyword.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')
      const regex = new RegExp(escaped, caseSensitive.value ? 'g' : 'gi')
      let m
      while ((m = regex.exec(fullText)) !== null) {
        allMatches.push({
          page: p,
          keywordIndex: kwIdx,
          keyword,
          index: m.index,
        })
      }
    })
  }

  matches.value = allMatches
  keywordMatchIndex.value = {}
  activeKeywordIdx.value = -1
  drawHighlights()
  emitMatchStats()
}

function emitMatchStats() {
  const stats = activeKeywords.value.map((kw, i) => ({
    keyword: kw,
    count: matches.value.filter(m => m.keywordIndex === i).length,
  }))
  emit('match-stats', stats)
}

// Match navigation
function activateKeyword(idx: number) {
  if (activeKeywordIdx.value === idx) {
    activeKeywordIdx.value = -1
  } else {
    activeKeywordIdx.value = idx
    const kwMatches = matches.value.filter(m => m.keywordIndex === idx)
    if (kwMatches.length > 0 && keywordMatchIndex.value[String(idx)] === undefined) {
      keywordMatchIndex.value[String(idx)] = 0
      goToMatch(idx)
    }
  }
}

function prevMatch(idx: number) {
  const key = String(idx)
  const current = keywordMatchIndex.value[key] || 0
  if (current > 0) {
    keywordMatchIndex.value[key] = current - 1
    goToMatch(idx)
  }
}

function nextMatch(idx: number) {
  const key = String(idx)
  const kwMatches = matches.value.filter(m => m.keywordIndex === idx)
  const current = keywordMatchIndex.value[key] || 0
  if (current < kwMatches.length - 1) {
    keywordMatchIndex.value[key] = current + 1
    goToMatch(idx)
  }
}

async function goToMatch(kwIdx: number) {
  const kwMatches = matches.value.filter(m => m.keywordIndex === kwIdx)
  const matchIdx = keywordMatchIndex.value[String(kwIdx)] || 0
  const match = kwMatches[matchIdx]
  if (!match) return

  if (match.page !== currentPage.value) {
    currentPage.value = match.page
    await renderCurrentPage()
  }

  // Scroll to match position
  const textContent = pageTextContents.value[currentPage.value]
  const viewport = currentViewport.value
  if (!textContent || !viewport) return

  const items = textContent.items
  let globalCharOffset = 0
  let found = false

  for (const item of items) {
    if (!item.str || !item.transform) {
      globalCharOffset += (item.str || '').length
      continue
    }
    const itemStart = globalCharOffset
    const itemEnd = globalCharOffset + item.str.length

    if (match.index >= itemStart && match.index < itemEnd) {
      const tx = pdfjsLib.Util.transform(viewport.transform, item.transform)
      const targetY = tx[5]
      const container = viewerEl.value
      if (container) {
        const canvasRect = pdfCanvas.value?.getBoundingClientRect()
        if (canvasRect) {
          const viewerRect = container.getBoundingClientRect()
          const matchScreenY = canvasRect.top + targetY - viewerRect.top
          const targetScrollTop = container.scrollTop + matchScreenY - viewerRect.height / 2
          container.scrollTo({ top: Math.max(0, targetScrollTop), behavior: 'smooth' })
        }
      }
      found = true
      break
    }
    globalCharOffset += item.str.length
  }
}

// Page navigation
function prevPage() {
  if (currentPage.value > 1) {
    currentPage.value--
    renderCurrentPage()
  }
}

function nextPage() {
  if (currentPage.value < totalPages.value) {
    currentPage.value++
    renderCurrentPage()
  }
}

// Zoom
function zoomIn() {
  scale.value = Math.min(scale.value + 0.25, 3)
  renderCurrentPage()
}

function zoomOut() {
  scale.value = Math.max(scale.value - 0.25, 0.5)
  renderCurrentPage()
}

// Keyboard navigation
function onKeyDown(e: KeyboardEvent) {
  if (e.key === 'ArrowLeft' || e.key === 'ArrowUp') {
    e.preventDefault()
    prevPage()
  } else if (e.key === 'ArrowRight' || e.key === 'ArrowDown') {
    e.preventDefault()
    nextPage()
  }
}

onMounted(() => {
  document.addEventListener('keydown', onKeyDown)
  if (props.file) loadPdf(props.file)
})

onUnmounted(() => {
  document.removeEventListener('keydown', onKeyDown)
})

// Expose methods for parent
defineExpose({ searchAllKeywords })
</script>

<template>
  <div class="pdf-viewer-container">
    <!-- Toolbar -->
    <div class="viewer-toolbar">
      <div class="zoom-controls">
        <button class="tb-btn" @click="zoomOut" title="缩小">−</button>
        <span class="zoom-level">{{ zoomLevel }}</span>
        <button class="tb-btn" @click="zoomIn" title="放大">+</button>
      </div>
      <div class="page-info">
        第 {{ currentPage }} / {{ totalPages }} 页
      </div>
      <div class="page-controls">
        <button class="tb-btn" @click="prevPage" :disabled="currentPage <= 1">◀</button>
        <button class="tb-btn" @click="nextPage" :disabled="currentPage >= totalPages">▶</button>
      </div>
    </div>

    <!-- PDF Canvas -->
    <div class="viewer-canvas-area" ref="viewerEl">
      <div v-if="!pdfDoc" class="viewer-placeholder">
        <span class="placeholder-icon">📄</span>
        <p>等待加载 PDF 文件</p>
      </div>
      <div v-else class="page-wrapper">
        <div class="page-container">
          <canvas ref="pdfCanvas"></canvas>
          <canvas ref="highlightCanvas" class="highlight-canvas"></canvas>
          <div ref="textLayerDiv" class="text-layer"></div>
        </div>
      </div>
    </div>

    <!-- Keyword Stats Bar -->
    <div v-if="keywordStats.length > 0" class="stats-bar">
      <div class="kw-stats-list">
        <div
          v-for="stat in keywordStats"
          :key="stat.index"
          class="kw-stat-item"
          :class="{ active: stat.isActive }"
          @click="activateKeyword(stat.index)"
        >
          <span class="kw-dot" :style="{ background: stat.color.border }"></span>
          <span class="kw-name">{{ stat.keyword }}</span>
          <span class="kw-count">{{ stat.current }}/{{ stat.total }}</span>
          <div v-if="stat.isActive && stat.total > 0" class="kw-nav">
            <button @click.stop="prevMatch(stat.index)" :disabled="stat.current <= 1">◀</button>
            <button @click.stop="nextMatch(stat.index)" :disabled="stat.current >= stat.total">▶</button>
          </div>
        </div>
      </div>
      <span class="stats-info">共 {{ totalMatchCount }} 个匹配</span>
    </div>
  </div>
</template>

<style scoped>
.pdf-viewer-container {
  display: flex;
  flex-direction: column;
  height: 100%;
  background: var(--color-bg);
  border-radius: var(--radius-md);
  overflow: hidden;
}

.viewer-toolbar {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  background: var(--color-surface);
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.zoom-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.zoom-level {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  min-width: 40px;
  text-align: center;
}

.page-info {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  flex: 1;
  text-align: center;
}

.page-controls {
  display: flex;
  align-items: center;
  gap: 4px;
}

.tb-btn {
  padding: 4px 10px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--color-text);
  transition: all 0.15s;
}

.tb-btn:hover:not(:disabled) {
  background: var(--color-primary);
  color: white;
  border-color: var(--color-primary);
}

.tb-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.viewer-canvas-area {
  flex: 1;
  overflow: auto;
  padding: 16px;
  display: flex;
  justify-content: center;
}

.viewer-placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: var(--color-text-secondary);
  user-select: none;
}

.placeholder-icon {
  font-size: 3rem;
  margin-bottom: 0.8rem;
  opacity: 0.5;
}

.page-wrapper {
  display: flex;
  flex-direction: column;
  align-items: center;
}

.page-container {
  position: relative;
  background: white;
  box-shadow: 0 2px 16px rgba(0, 0, 0, 0.12);
  line-height: 0;
}

.highlight-canvas {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.text-layer {
  position: absolute;
  left: 0;
  top: 0;
  right: 0;
  bottom: 0;
  overflow: hidden;
  line-height: 1;
}

.text-layer :deep(> span) {
  color: transparent;
  position: absolute;
  white-space: pre;
  transform-origin: 0% 0%;
}

.text-layer :deep(::selection) {
  background: rgba(100, 149, 237, 0.3);
}

/* Stats Bar */
.stats-bar {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 6px 12px;
  background: var(--color-surface);
  border-top: 1px solid var(--color-border);
  flex-shrink: 0;
  overflow-x: auto;
}

.kw-stats-list {
  display: flex;
  align-items: center;
  gap: 6px;
  flex: 1;
}

.kw-stat-item {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 3px 8px;
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  cursor: pointer;
  transition: all 0.15s;
  user-select: none;
  white-space: nowrap;
  font-size: 0.75rem;
}

.kw-stat-item:hover {
  background: #eef0f3;
}

.kw-stat-item.active {
  background: #eef0ff;
  box-shadow: 0 0 0 1px var(--color-primary, #3b82f6)40;
}

.kw-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  flex-shrink: 0;
}

.kw-name {
  font-weight: 500;
  color: var(--color-text);
  max-width: 80px;
  overflow: hidden;
  text-overflow: ellipsis;
}

.kw-count {
  color: var(--color-text-secondary);
}

.kw-nav {
  display: flex;
  gap: 2px;
  margin-left: 2px;
}

.kw-nav button {
  background: var(--color-primary);
  color: white;
  border: none;
  width: 18px;
  height: 18px;
  border-radius: 3px;
  font-size: 9px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.kw-nav button:hover:not(:disabled) {
  opacity: 0.85;
}

.kw-nav button:disabled {
  background: #ccc;
  cursor: not-allowed;
}

.stats-info {
  font-size: 0.7rem;
  color: var(--color-text-secondary);
  white-space: nowrap;
}
</style>
