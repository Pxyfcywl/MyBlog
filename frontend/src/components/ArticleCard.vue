<script setup lang="ts">
import { useRouter } from 'vue-router'

const props = defineProps<{
  article: {
    id: number
    title: string
    slug: string
    summary: string
    cover_image: string
    is_pinned: boolean
    created_at: string
    tags: { id: number; name: string; slug: string }[]
  }
  index: number
}>()

const router = useRouter()

function goDetail() {
  router.push(`/article/${props.article.slug}`)
}

const isOdd = props.index % 2 === 0
</script>

<template>
  <article class="card" :class="{ odd: isOdd, even: !isOdd, 'no-image': !article.cover_image }" @click="goDetail">
    <div class="card-grid">
      <div class="card-media" v-if="article.cover_image">
        <img :src="article.cover_image" :alt="article.title" loading="lazy" />
      </div>
      <div class="card-content" :class="{ 'full-width': !article.cover_image }">
        <div class="pin-badge" v-if="article.is_pinned">📌 置顶</div>
        <h2 class="article-title">{{ article.title }}</h2>
        <p class="article-excerpt">{{ article.summary }}</p>
        <div class="article-meta">
          <span>📅 {{ new Date(article.created_at).toLocaleDateString('zh-CN') }}</span>
          <span v-for="tag in article.tags.slice(0, 3)" :key="tag.id" class="tag">#{{ tag.name }}</span>
          <span class="read-more">阅读全文 →</span>
        </div>
      </div>
    </div>
  </article>
</template>

<style scoped>
.card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  box-shadow: var(--shadow-card);
  transition: transform 0.25s ease, box-shadow 0.3s ease;
  overflow: visible;
  cursor: pointer;
}

.card:hover {
  transform: translateY(-6px);
  box-shadow: var(--shadow-hover);
}

.card-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0;
  align-items: start;
  overflow: visible;
}

.card-media {
  position: relative;
  overflow: visible;
  display: flex;
  line-height: 0;
  z-index: 1;
}

.card-media img {
  width: 100%;
  height: auto;
  border-radius: 1.25rem;
  box-shadow: 0 20px 30px -12px rgba(0, 0, 0, 0.2);
  transition: filter 0.2s ease, transform 0.2s ease;
  display: block;
  aspect-ratio: 4 / 3;
  object-fit: cover;
  background-color: #eef2ff;
}

/* 奇数卡片：图片在左，左上角倾斜 */
.odd .card-media {
  justify-content: flex-start;
  transform-origin: top left;
  transform: rotate(-4deg) translateY(-8px) translateX(-4px);
}

/* 偶数卡片：图片在右，右上角倾斜 */
.even .card-grid {
  direction: ltr;
}
.even .card-content {
  order: 1;
}
.even .card-media {
  order: 2;
  justify-content: flex-end;
  transform-origin: top right;
  transform: rotate(4deg) translateY(-8px) translateX(4px);
}

.card-content {
  padding: 1.8rem 2rem 2rem 1.8rem;
  position: relative;
  z-index: 2;
}

.pin-badge {
  font-size: 0.8rem;
  color: var(--color-primary);
  margin-bottom: 0.5rem;
}

.article-title {
  font-size: 1.65rem;
  font-weight: 700;
  line-height: 1.3;
  margin-bottom: 0.85rem;
  color: var(--color-text);
}

.article-excerpt {
  font-size: 1rem;
  color: #334155;
  line-height: 1.6;
  margin-bottom: 1rem;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-meta {
  display: flex;
  align-items: center;
  gap: 1rem;
  font-size: 0.8rem;
  color: #5b6e8c;
  border-top: 1px solid #e9eef3;
  padding-top: 1rem;
  flex-wrap: wrap;
}

.tag {
  color: var(--color-primary);
}

.read-more {
  color: var(--color-primary);
  font-weight: 500;
  margin-left: auto;
  transition: gap 0.2s;
}

/* 响应式 */
@media (max-width: 768px) {
  .card-grid {
    grid-template-columns: 1fr;
  }
  .odd .card-media,
  .even .card-media {
    order: 1;
    transform: none;
    justify-content: center;
    padding: 1rem 1rem 0 1rem;
  }
  .even .card-content,
  .odd .card-content {
    order: 2;
  }
  .card-media img {
    max-width: 90%;
    margin: 0 auto;
  }
  .article-title {
    font-size: 1.3rem;
  }
}

/* 无封面图时 */
.no-image .card-grid {
  grid-template-columns: 1fr;
}

.card-content.full-width {
  grid-column: 1 / -1;
}
</style>
