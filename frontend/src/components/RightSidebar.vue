<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { tagApi } from '../api'
import { useRouter } from 'vue-router'

const router = useRouter()
const tags = ref<any[]>([])

// 头像URL，留空显示默认emoji
const avatarUrl = '../pictures/nomove.png'

onMounted(async () => {
  try {
    const res = await tagApi.list()
    tags.value = res.data.slice(0, 10)  // 取前10个热门标签
  } catch (e) {
    console.error('加载标签失败:', e)
  }
})

function goTag(slug: string) {
  router.push({ path: '/tags', query: { tag: slug } })
}
</script>

<template>
  <aside class="right-sidebar">
    <!-- 个人信息 -->
    <div class="widget profile-widget">
      <div class="avatar-placeholder">
        <img v-if="avatarUrl" :src="avatarUrl" alt="头像" class="avatar-img" />
        <span v-else>🧑‍💻</span>
      </div>
      <h3>hatsuyufei</h3>
      <p class="bio">代码与文字交汇的地方</p>
    </div>

    <!-- 热门标签 -->
    <div class="widget">
      <h3 class="widget-title">🏷️ 热门标签</h3>
      <div class="tag-cloud">
        <button
          v-for="tag in tags"
          :key="tag.slug"
          class="tag-item"
          @click="goTag(tag.slug)"
        >
          {{ tag.name }}
          <span class="count">{{ tag.article_count }}</span>
        </button>
      </div>
      <div v-if="tags.length === 0" class="empty">暂无标签</div>
    </div>

    <!-- 自定义文字 -->
    <div class="widget">
      <h3 class="widget-title">💬 写给自己</h3>
      <p class="custom-text">
        用代码构建世界，用文字记录思考。<br />
        保持好奇，持续学习。
      </p>
    </div>
  </aside>
</template>

<style scoped>
.right-sidebar {
  width: 280px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
  position: sticky;
  top: 2rem;
  height: fit-content;
}

.widget {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
}

.widget-title {
  font-size: 1rem;
  font-weight: 700;
  margin-bottom: 1rem;
  color: var(--color-text);
}

.profile-widget {
  text-align: center;
}

.avatar-placeholder {
  width: 80px;
  height: 80px;
  margin: 0 auto 0.5rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3rem;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.profile-widget h3 {
  font-size: 1.1rem;
  margin-bottom: 0.3rem;
}

.bio {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

.tag-cloud {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
}

.tag-item {
  padding: 0.3rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  background: none;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  transition: all 0.2s;
  display: flex;
  align-items: center;
  gap: 0.3rem;
}

.tag-item:hover {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.tag-item .count {
  font-size: 0.75rem;
  opacity: 0.6;
}

.custom-text {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  line-height: 1.8;
}

.empty {
  text-align: center;
  color: var(--color-text-secondary);
  font-size: 0.85rem;
}

/* 响应式：移动端隐藏右侧栏 */
@media (max-width: 1024px) {
  .right-sidebar {
    display: none;
  }
}
</style>
