<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { tagApi, articleApi } from '../api'
import ArticleCard from '../components/ArticleCard.vue'

const activeTab = ref<'tags' | 'categories'>('tags')
const tags = ref<any[]>([])
const categories = ref<any[]>([])
const selectedTag = ref<string | null>(null)
const selectedCategory = ref<string | null>(null)
const articles = ref<any[]>([])
const loading = ref(false)

onMounted(async () => {
  const [tagRes, catRes] = await Promise.all([
    tagApi.list(),
    tagApi.categories(),
  ])
  tags.value = tagRes.data
  categories.value = catRes.data
})

const items = computed(() => activeTab.value === 'tags' ? tags.value : categories.value)

async function selectItem(slug: string) {
  if (activeTab.value === 'tags') {
    selectedTag.value = selectedTag.value === slug ? null : slug
    selectedCategory.value = null
  } else {
    selectedCategory.value = selectedCategory.value === slug ? null : slug
    selectedTag.value = null
  }
  await fetchArticles()
}

async function fetchArticles() {
  loading.value = true
  try {
    const params: any = { page: 1, page_size: 50 }
    if (selectedTag.value) params.tag = selectedTag.value
    if (selectedCategory.value) params.category = selectedCategory.value
    const res = await articleApi.list(params)
    articles.value = res.data.items
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="tags-page">
    <h1 class="page-title">标签与分类</h1>

    <div class="tab-switch">
      <button :class="{ active: activeTab === 'tags' }" @click="activeTab = 'tags'; selectedTag = null; selectedCategory = null; articles = []">
        标签
      </button>
      <button :class="{ active: activeTab === 'categories' }" @click="activeTab = 'categories'; selectedTag = null; selectedCategory = null; articles = []">
        分类
      </button>
    </div>

    <div class="item-list">
      <button
        v-for="item in items"
        :key="item.slug"
        class="item-chip"
        :class="{ selected: (activeTab === 'tags' ? selectedTag : selectedCategory) === item.slug }"
        @click="selectItem(item.slug)"
      >
        {{ item.name }}
        <span class="count">{{ item.article_count }}</span>
      </button>
      <div v-if="items.length === 0" class="empty">暂无{{ activeTab === 'tags' ? '标签' : '分类' }}</div>
    </div>

    <div v-if="selectedTag || selectedCategory" class="article-grid">
      <div v-if="loading" class="loading">加载中...</div>
      <ArticleCard
        v-for="(article, index) in articles"
        :key="article.id"
        :article="article"
        :index="index"
      />
      <div v-if="!loading && articles.length === 0" class="empty">该{{ activeTab === 'tags' ? '标签' : '分类' }}下暂无文章</div>
    </div>
  </div>
</template>

<style scoped>
.tags-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.tab-switch {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1.5rem;
}

.tab-switch button {
  padding: 0.5rem 1.5rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
  cursor: pointer;
  font-size: 0.95rem;
  transition: all 0.2s;
}

.tab-switch button.active {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.item-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
  margin-bottom: 2rem;
}

.item-chip {
  padding: 0.5rem 1.2rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: var(--color-surface);
  cursor: pointer;
  font-size: 0.9rem;
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.5rem;
}

.item-chip:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.item-chip.selected {
  background: var(--color-primary);
  color: #fff;
  border-color: var(--color-primary);
}

.item-chip .count {
  font-size: 0.8rem;
  opacity: 0.7;
}

.article-grid {
  display: flex;
  flex-direction: column;
  gap: 2rem;
  margin-top: 1rem;
}

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}
</style>
