<script setup lang="ts">
import { ref } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

const props = defineProps<{
  visible: boolean
  reviewResult: string
}>()

const emit = defineEmits<{
  (e: 'update:visible', val: boolean): void
}>()

// Copy result
const copied = ref(false)
function copyResult() {
  navigator.clipboard.writeText(props.reviewResult).then(() => {
    copied.value = true
    setTimeout(() => { copied.value = false }, 2000)
  })
}

// Download .md
function downloadMd() {
  const blob = new Blob([props.reviewResult], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `审查结果_${new Date().toISOString().slice(0, 10)}.md`
  a.click()
  URL.revokeObjectURL(url)
}

function close() {
  emit('update:visible', false)
}
</script>

<template>
  <Transition name="sidebar-slide">
    <div v-if="visible" class="review-sidebar">
      <!-- Header -->
      <div class="sidebar-header">
        <h3 class="sidebar-title">📋 AI 审查结果</h3>
        <button class="close-btn" @click="close" title="收起">◀</button>
      </div>

      <!-- Actions -->
      <div class="sidebar-actions">
        <button class="action-btn" @click="copyResult">
          {{ copied ? '✅ 已复制' : '📋 复制' }}
        </button>
        <button class="action-btn" @click="downloadMd">
          💾 下载 .md
        </button>
      </div>

      <!-- Review Result -->
      <div class="sidebar-content scrollbar">
        <div v-if="!reviewResult" class="empty-hint">暂无审查结果</div>
        <MdPreview
          v-else
          :modelValue="reviewResult"
          previewTheme="github"
          class="md-preview"
        />
      </div>
    </div>
  </Transition>
</template>

<style scoped>
.review-sidebar {
  width: 360px;
  height: 100%;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow: hidden;
}

/* Slide transition */
.sidebar-slide-enter-active,
.sidebar-slide-leave-active {
  transition: all 0.3s ease;
}

.sidebar-slide-enter-from,
.sidebar-slide-leave-to {
  margin-left: -360px;
  opacity: 0;
}

.sidebar-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.sidebar-title {
  font-size: 0.95rem;
  font-weight: 700;
  margin: 0;
}

.close-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 4px 8px;
  cursor: pointer;
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  transition: all 0.15s;
}

.close-btn:hover {
  background: var(--color-bg);
  color: var(--color-text);
}

.sidebar-actions {
  display: flex;
  gap: 6px;
  padding: 8px 16px;
  border-bottom: 1px solid var(--color-border);
  flex-shrink: 0;
}

.action-btn {
  flex: 1;
  padding: 6px 10px;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.8rem;
  color: var(--color-text);
  cursor: pointer;
  transition: all 0.15s;
}

.action-btn:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 16px;
}

.empty-hint {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

.md-preview {
  font-size: 0.85rem;
}

/* Scrollbar */
.scrollbar::-webkit-scrollbar {
  width: 5px;
}

.scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.scrollbar::-webkit-scrollbar-thumb {
  background: #ddd;
  border-radius: 3px;
}

.scrollbar::-webkit-scrollbar-thumb:hover {
  background: #ccc;
}
</style>
