<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { articleApi } from '../api'
import ArticleCard from '../components/ArticleCard.vue'
import RightSidebar from '../components/RightSidebar.vue'
import Footer from '../components/Footer.vue'

const route = useRoute()
const router = useRouter()

interface Article {
  id: number
  title: string
  slug: string
  summary: string
  cover_image: string
  is_pinned: boolean
  created_at: string
  tags: { id: number; name: string; slug: string }[]
  categories: { id: number; name: string; slug: string }[]
}

const articles = ref<Article[]>([])
const loading = ref(true)
const currentPage = ref(1)
const totalPages = ref(1)
const total = ref(0)
const pageSize = 8

async function loadArticles(page: number) {
  loading.value = true
  try {
    const res = await articleApi.list({ page, page_size: pageSize })
    articles.value = res.data.items
    total.value = res.data.total
    totalPages.value = Math.ceil(res.data.total / pageSize)
    currentPage.value = page
  } catch (e) {
    console.error('加载文章失败:', e)
  } finally {
    loading.value = false
  }
}

function goPage(page: number) {
  if (page < 1 || page > totalPages.value) return
  router.push({ path: '/home', query: { page } })
}

// 生成页码数组（带省略号）
const pageNumbers = ref<(number | string)[]>([])

function buildPageNumbers() {
  const pages: (number | string)[] = []
  const p = currentPage.value
  const t = totalPages.value

  if (t <= 7) {
    for (let i = 1; i <= t; i++) pages.push(i)
  } else {
    pages.push(1)
    if (p > 3) pages.push('...')
    for (let i = Math.max(2, p - 1); i <= Math.min(t - 1, p + 1); i++) {
      pages.push(i)
    }
    if (p < t - 2) pages.push('...')
    pages.push(t)
  }

  pageNumbers.value = pages
}

watch(currentPage, () => buildPageNumbers())

watch(() => route.query.page, (val) => {
  const page = parseInt(val as string) || 1
  if (page !== currentPage.value) {
    loadArticles(page)
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }
})

onMounted(() => {
  const page = parseInt(route.query.page as string) || 1
  loadArticles(page)
})
</script>

<template>
  <div class="home-layout">
    <div class="article-list">
      <h1 class="page-title">最新文章 <span class="total-count">共 {{ total }} 篇</span></h1>

      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="articles.length === 0" class="empty">暂无文章</div>

      <template v-else>
        <ArticleCard
          v-for="(article, index) in articles"
          :key="article.id"
          :article="article"
          :index="(currentPage - 1) * pageSize + index"
        />

        <!-- 分页 -->
        <div class="pagination" v-if="totalPages > 1">
          <button
            class="page-btn"
            :disabled="currentPage <= 1"
            @click="goPage(currentPage - 1)"
          >‹</button>

          <template v-for="(p, i) in pageNumbers" :key="i">
            <span v-if="p === '...'" class="page-dots">…</span>
            <button
              v-else
              class="page-btn"
              :class="{ active: p === currentPage }"
              @click="goPage(p as number)"
            >{{ p }}</button>
          </template>

          <button
            class="page-btn"
            :disabled="currentPage >= totalPages"
            @click="goPage(currentPage + 1)"
          >›</button>
        </div>
      </template>
    </div>
    <RightSidebar />
  </div>
  <Footer />
</template>

<style scoped>
.home-layout {
  display: flex;
  gap: 2rem;
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.article-list {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  color: var(--color-text);
  margin-bottom: 0.5rem;
}

.total-count {
  font-size: 0.9rem;
  font-weight: 400;
  color: var(--color-text-secondary);
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-secondary);
}

/* 分页 */
.pagination {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  margin-top: 1rem;
  padding: 1rem 0;
}

.page-btn {
  min-width: 36px;
  height: 36px;
  padding: 0 0.5rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  justify-content: center;
}

.page-btn:hover:not(:disabled):not(.active) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.page-btn.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.page-btn:disabled {
  opacity: 0.4;
  cursor: not-allowed;
}

.page-dots {
  padding: 0 0.3rem;
  color: var(--color-text-secondary);
}
</style>
