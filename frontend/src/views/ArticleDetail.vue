<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { articleApi } from '../api'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'

const route = useRoute()
const article = ref<any>(null)
const loading = ref(true)

onMounted(async () => {
  try {
    const slug = route.params.slug as string
    const res = await articleApi.detail(slug)
    article.value = res.data
  } catch (e) {
    console.error('加载文章失败:', e)
  } finally {
    loading.value = false
  }
})
</script>

<template>
  <div class="article-detail">
    <div v-if="loading" class="loading">加载中...</div>
    <div v-else-if="!article" class="empty">文章不存在</div>
    <template v-else>
      <!-- 封面图 -->
      <div v-if="article.cover_image" class="cover-image">
        <img :src="article.cover_image" :alt="article.title" />
      </div>

      <header class="article-header">
        <h1>{{ article.title }}</h1>
        <div class="meta">
          <span>📅 {{ new Date(article.created_at).toLocaleDateString('zh-CN') }}</span>
          <span v-for="tag in article.tags" :key="tag.id" class="tag">#{{ tag.name }}</span>
        </div>
      </header>

      <div class="article-body">
        <MdPreview :modelValue="article.content" language="zh-CN" />
      </div>
    </template>
  </div>
</template>

<style scoped>
.article-detail {
  max-width: 1000px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.cover-image {
  width: 100%;
  margin-bottom: 2rem;
  border-radius: var(--radius-lg);
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.cover-image img {
  width: 100%;
  height: auto;
  max-height: 450px;
  object-fit: cover;
  display: block;
}

.article-header {
  margin-bottom: 2rem;
}

.article-header h1 {
  font-size: 2.2rem;
  font-weight: 800;
  line-height: 1.3;
  margin-bottom: 1rem;
}

.meta {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.tag {
  color: var(--color-primary);
}

.article-body {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-card);
}

/* 文章内图片居中 */
.article-body :deep(img) {
  display: block;
  margin: 1.5rem auto;
  max-width: 100%;
  height: auto;
  border-radius: var(--radius-sm);
}

/* 文章内代码块样式 */
.article-body :deep(pre) {
  border-radius: var(--radius-sm);
  overflow-x: auto;
}

/* 文章内数学公式 */
.article-body :deep(.katex-display) {
  overflow-x: auto;
  padding: 0.5rem 0;
}

.loading, .empty {
  text-align: center;
  padding: 3rem;
  color: var(--color-text-secondary);
}
</style>
