<script setup lang="ts">
import { ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { articleApi } from '../api'

const router = useRouter()
const showSearch = ref(false)
const query = ref('')
const results = ref<any[]>([])
const loading = ref(false)
let debounceTimer: number

function openSearch() {
  showSearch.value = true
  query.value = ''
  results.value = []
  // 自动聚焦
  setTimeout(() => {
    const input = document.querySelector('.search-input') as HTMLInputElement
    input?.focus()
  }, 100)
}

function closeSearch() {
  showSearch.value = false
  query.value = ''
  results.value = []
}

watch(query, (val) => {
  clearTimeout(debounceTimer)
  if (!val.trim()) {
    results.value = []
    return
  }
  debounceTimer = window.setTimeout(async () => {
    loading.value = true
    try {
      const res = await articleApi.search(val.trim(), 1)
      results.value = res.data.items
    } catch {
      results.value = []
    } finally {
      loading.value = false
    }
  }, 300)
})

function goArticle(slug: string) {
  closeSearch()
  router.push(`/article/${slug}`)
}

// 快捷键：Ctrl+K 打开搜索
function handleKeydown(e: KeyboardEvent) {
  if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
    e.preventDefault()
    showSearch.value ? closeSearch() : openSearch()
  }
  if (e.key === 'Escape' && showSearch.value) {
    closeSearch()
  }
}

// 暴露 openSearch 给父组件
defineExpose({ openSearch })
</script>

<template>
  <!-- 搜索按钮 -->
  <button class="search-trigger" @click="openSearch" title="搜索 (Ctrl+K)">
    🔍
  </button>

  <!-- 搜索弹窗 -->
  <Teleport to="body">
    <div v-if="showSearch" class="search-overlay" @click.self="closeSearch">
      <div class="search-modal">
        <div class="search-header">
          <span class="search-icon">🔍</span>
          <input
            v-model="query"
            class="search-input"
            placeholder="搜索文章标题或内容..."
            @keydown.escape="closeSearch"
          />
          <button class="search-close" @click="closeSearch">✕</button>
        </div>

        <div class="search-body">
          <div v-if="loading" class="search-status">搜索中...</div>
          <div v-else-if="query && results.length === 0" class="search-status">没有找到相关文章</div>
          <div v-else-if="!query" class="search-hint">输入关键词开始搜索</div>

          <div v-else class="search-results">
            <div
              v-for="article in results"
              :key="article.id"
              class="result-item"
              @click="goArticle(article.slug)"
            >
              <div class="result-title">
                <span v-if="article.is_pinned" class="pin">📌</span>
                {{ article.title }}
              </div>
              <div class="result-summary">{{ article.summary }}</div>
              <div class="result-tags">
                <span v-for="tag in article.tags.slice(0, 3)" :key="tag.id" class="tag">#{{ tag.name }}</span>
              </div>
            </div>
          </div>
        </div>

        <div class="search-footer">
          <span>按 <kbd>Esc</kbd> 关闭</span>
          <span>按 <kbd>Enter</kbd> 打开第一条结果</span>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<style scoped>
.search-trigger {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  border: 1px solid var(--color-border);
  background: var(--color-surface);
  cursor: pointer;
  font-size: 1rem;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all 0.2s;
}

.search-trigger:hover {
  background: var(--color-bg);
  border-color: var(--color-primary);
}

.search-overlay {
  position: fixed;
  inset: 0;
  background: rgba(0, 0, 0, 0.5);
  z-index: 9999;
  display: flex;
  align-items: flex-start;
  justify-content: center;
  padding-top: 15vh;
  backdrop-filter: blur(2px);
}

.search-modal {
  width: 560px;
  max-width: 90vw;
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
  overflow: hidden;
  display: flex;
  flex-direction: column;
  max-height: 70vh;
}

.search-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 1rem 1.2rem;
  border-bottom: 1px solid var(--color-border);
}

.search-icon {
  font-size: 1.1rem;
  flex-shrink: 0;
}

.search-input {
  flex: 1;
  border: none;
  outline: none;
  font-size: 1rem;
  background: none;
  color: var(--color-text);
}

.search-input::placeholder {
  color: var(--color-text-secondary);
}

.search-close {
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: var(--color-bg);
  cursor: pointer;
  font-size: 0.85rem;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.search-close:hover {
  background: var(--color-border);
}

.search-body {
  flex: 1;
  overflow-y: auto;
  padding: 0.5rem 0;
}

.search-status,
.search-hint {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
  font-size: 0.9rem;
}

.search-results {
  display: flex;
  flex-direction: column;
}

.result-item {
  padding: 0.8rem 1.2rem;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid var(--color-border);
}

.result-item:last-child {
  border-bottom: none;
}

.result-item:hover {
  background: var(--color-bg);
}

.result-title {
  font-weight: 600;
  font-size: 0.95rem;
  margin-bottom: 0.3rem;
}

.pin {
  font-size: 0.8rem;
}

.result-summary {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
  margin-bottom: 0.3rem;
}

.result-tags {
  display: flex;
  gap: 0.5rem;
}

.tag {
  font-size: 0.75rem;
  color: var(--color-primary);
}

.search-footer {
  display: flex;
  gap: 1.5rem;
  justify-content: center;
  padding: 0.6rem;
  border-top: 1px solid var(--color-border);
  font-size: 0.75rem;
  color: var(--color-text-secondary);
}

kbd {
  padding: 0.1rem 0.4rem;
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  border-radius: 3px;
  font-size: 0.7rem;
  font-family: monospace;
}
</style>
