<script setup lang="ts">
import { ref } from 'vue'

const profile = ref({
  name: 'hatsuyufei',
  avatar: '../pictures/nomove.png', // 填入图片URL，留空显示默认emoji
  bio: '用代码构建世界，用文字记录思考',
  location: '中国',
  social: [
    { name: 'GitHub', url: 'https://github.com/Pxyfcywl/Pxyfcywl', color: '#333' },
    { name: 'Bilibili', url: 'https://space.bilibili.com/390277370?spm_id_from=333.1007.0.0', color: '#00a1d6' },
    { name: 'QQ', url: '1594463152', color: '#12b7f5' },
    { name: 'Email', url: 'hatsuyufei@163.com', color: '#ea4335' },
  ]
})

const features = [
  { icon: '📝', title: 'Markdown 编辑器', desc: '支持 LaTeX 数学公式、代码高亮、图片上传' },
  { icon: '🏷️', title: '标签与分类', desc: '文章支持多标签和分类管理' },
  { icon: '🔍', title: '全局搜索', desc: '支持文章标题和内容模糊搜索' },
  { icon: '🎵', title: '音乐播放器', desc: '内置音乐播放器，支持多种播放模式' },
  { icon: '📄', title: '文档解析', desc: 'MinerU 驱动，PDF/Office 转 Markdown' },
  { icon: '🤖', title: 'AI 智能审查', desc: 'LLM 驱动，支持自定义审查要求' },
]

const changelog = [
  {
    version: 'v0.4.0', date: '2026-06-15',
    items: ['MinerU 文档解析集成（PDF/Office → Markdown）', 'LLM 智能审查（支持自定义审查要求）', '大模型配置面板（可切换 DeepSeek/Mimo/百炼/智谱）', 'Embedding 知识库向量化准备', '文章详情页宽度优化']
  },
  {
    version: 'v0.3.0', date: '2026-06-14',
    items: ['下雨特效 + 雨声白噪音', '百宝箱助手页面（AI链接导航）', '主页分页功能（每页8篇）', 'Docker 一键部署方案', '标签/分类自动清理空项']
  },
  {
    version: 'v0.2.0', date: '2026-06-14',
    items: ['个人主页上线（弧形社交图标）', '音乐播放器集成（本地MP3 + 红色风格）', '全局搜索（Ctrl+K）', '底部版权信息']
  },
  {
    version: 'v0.1.0', date: '2026-06-14',
    items: ['博客核心功能上线', '文章发布/编辑/删除', '标签分类管理', 'LaTeX 公式支持', '代码高亮', '图片上传', '左侧导航栏', 'Hero 首页打字机效果', '30篇文章导入']
  },
]
</script>

<template>
  <div class="profile-page">
    <div class="profile-layout">
      <!-- 左侧个人信息 -->
      <aside class="profile-sidebar">
        <div class="profile-card">
          <!-- 头像 + 弧形图标 -->
          <div class="avatar-section">
            <div class="avatar-ring">
              <div class="avatar">
              <img v-if="profile.avatar" :src="profile.avatar" alt="头像" class="avatar-img" />
              <span v-else>🧑‍💻</span>
            </div>
              <!-- 弧形排列的社交图标 -->
              <a
                v-for="(s, i) in profile.social"
                :key="s.name"
                :href="s.url || '#'"
                :title="s.name"
                target="_blank"
                class="arc-icon"
                :class="`pos-${i}`"
                :style="{ '--icon-color': s.color }"
                @click="!s.url && $event.preventDefault()"
                v-show="s.url"
              >
                <!-- GitHub -->
                <svg v-if="s.name === 'GitHub'" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z"/>
                </svg>
                <!-- Bilibili -->
                <svg v-else-if="s.name === 'Bilibili'" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M17.813 4.653h.854c1.51.054 2.769.578 3.773 1.574 1.004.995 1.524 2.249 1.56 3.76v7.36c-.036 1.51-.556 2.769-1.56 3.773s-2.262 1.524-3.773 1.56H5.333c-1.51-.036-2.769-.556-3.773-1.56S.036 18.858 0 17.347v-7.36c.036-1.511.556-2.765 1.56-3.76 1.004-.996 2.262-1.52 3.773-1.574h.774l-1.174-1.12a1.234 1.234 0 0 1-.373-.906c0-.356.124-.658.373-.907l.027-.027c.267-.249.573-.373.92-.373.347 0 .653.124.92.373L9.653 4.44c.071.071.134.142.187.213h4.267a.836.836 0 0 1 .16-.213l2.853-2.747c.267-.249.573-.373.92-.373.347 0 .662.124.929.373.249.249.373.551.373.907 0 .355-.124.657-.373.906zM5.333 7.24c-.746.018-1.373.276-1.88.773-.506.498-.769 1.13-.786 1.894v7.52c.017.764.28 1.395.786 1.893.507.498 1.134.756 1.88.773h13.334c.746-.017 1.373-.275 1.88-.773.506-.498.769-1.129.786-1.893v-7.52c-.017-.765-.28-1.396-.786-1.894-.507-.497-1.134-.755-1.88-.773zM8 11.107c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c.017-.391.15-.711.4-.96.249-.249.56-.373.933-.373zm8 0c.373 0 .684.124.933.373.25.249.383.569.4.96v1.173c-.017.391-.15.711-.4.96-.249.25-.56.374-.933.374s-.684-.125-.933-.374c-.25-.249-.383-.569-.4-.96V12.44c.017-.391.15-.711.4-.96.249-.249.56-.373.933-.373z"/>
                </svg>
                <!-- QQ -->
                <svg v-else-if="s.name === 'QQ'" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M21.395 15.035a39.548 39.548 0 00-1.235-2.573c.416-.616.75-1.3 1-2.043.391-1.175.486-2.446.486-3.569 0-3.267-2.048-5.85-5.15-5.85h-5.5c-3.102 0-5.15 2.583-5.15 5.85 0 1.123.095 2.394.486 3.569.25.743.584 1.427 1 2.043a39.548 39.548 0 00-1.235 2.573c-.377 1.082-.526 2.064-.526 2.965 0 1.5.5 2.5 1.5 3 .5.25 1.037.357 1.574.42A37.67 37.67 0 006.5 22.5c0 1 .5 1.5 1.5 1.5.5 0 1-.25 1.5-.75.5-.5 1-1 1.5-1.5.5-.5 1-.75 1.5-.75s1 .25 1.5.75c.5.5 1 1 1.5 1.5.5.5 1 .75 1.5.75 1 0 1.5-.5 1.5-1.5 0-1.036-.194-2.037-.574-2.98.537-.063 1.074-.17 1.574-.42 1-.5 1.5-1.5 1.5-3 0-.901-.149-1.883-.526-2.965z"/>
                </svg>
                <!-- Email -->
                <svg v-else viewBox="0 0 24 24" fill="currentColor">
                  <path d="M20 4H4c-1.1 0-1.99.9-1.99 2L2 18c0 1.1.9 2 2 2h16c1.1 0 2-.9 2-2V6c0-1.1-.9-2-2-2zm0 4l-8 5-8-5V6l8 5 8-5v2z"/>
                </svg>
              </a>
            </div>
          </div>

          <h2 class="name">{{ profile.name }}</h2>
          <p class="bio">{{ profile.bio }}</p>
          <p class="location">📍 {{ profile.location }}</p>
        </div>
      </aside>

      <!-- 右侧内容 -->
      <div class="profile-content">
        <section class="section">
          <h2 class="section-title">🚀 博客功能</h2>
          <div class="feature-grid">
            <div v-for="f in features" :key="f.title" class="feature-card">
              <span class="feature-icon">{{ f.icon }}</span>
              <div>
                <h3>{{ f.title }}</h3>
                <p>{{ f.desc }}</p>
              </div>
            </div>
          </div>
        </section>

        <section class="section">
          <h2 class="section-title">📋 更新日志</h2>
          <div class="changelog">
            <div v-for="log in changelog" :key="log.version" class="log-entry">
              <div class="log-header">
                <span class="log-version">{{ log.version }}</span>
                <span class="log-date">{{ log.date }}</span>
              </div>
              <ul class="log-items">
                <li v-for="item in log.items" :key="item">{{ item }}</li>
              </ul>
            </div>
          </div>
        </section>
      </div>
    </div>
  </div>
</template>

<style scoped>
.profile-page {
  max-width: 1280px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.profile-layout {
  display: flex;
  gap: 2rem;
}

/* 左侧 */
.profile-sidebar {
  width: 280px;
  flex-shrink: 0;
  position: sticky;
  top: 2rem;
  height: fit-content;
}

.profile-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-card);
  text-align: center;
}

/* 头像 + 弧形图标 */
.avatar-section {
  display: flex;
  justify-content: center;
  margin-bottom: 1.2rem;
}

.avatar-ring {
  position: relative;
  width: 180px;
  height: 120px;
}

.avatar {
  width: 90px;
  height: 90px;
  position: absolute;
  top: 0;
  left: 50%;
  transform: translateX(-50%);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 3.5rem;
}

.avatar-img {
  width: 100%;
  height: 100%;
  border-radius: 50%;
  object-fit: cover;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
}

/* 弧形排列的社交图标 */
.arc-icon {
  position: absolute;
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #fff;
  text-decoration: none;
  transition: all 0.3s ease;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
  cursor: pointer;
}

.arc-icon svg {
  width: 18px;
  height: 18px;
}

.arc-icon:hover {
  transform: scale(1.2) translateY(-3px);
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.25);
}

/* 弧形位置 — 4个图标从左到右排列成弧形 */
.pos-0 {
  background: #333;
  left: 5px;
  top: 60px;
}

.pos-1 {
  background: #00a1d6;
  left: 38px;
  top: 80px;
}

.pos-2 {
  background: #12b7f5;
  right: 38px;
  top: 80px;
}

.pos-3 {
  background: #ea4335;
  right: 5px;
  top: 60px;
}

.name {
  font-size: 1.4rem;
  font-weight: 700;
  margin-bottom: 0.5rem;
}

.bio {
  font-size: 0.95rem;
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin-bottom: 0.5rem;
}

.location {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

/* 右侧内容 */
.profile-content {
  flex: 1;
  min-width: 0;
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem 2rem;
  box-shadow: var(--shadow-card);
}

.section-title {
  font-size: 1.3rem;
  font-weight: 700;
  margin-bottom: 1.2rem;
}

.feature-grid {
  display: flex;
  flex-direction: column;
  gap: 0.8rem;
}

.feature-card {
  display: flex;
  align-items: flex-start;
  gap: 1rem;
  padding: 0.8rem;
  border-radius: var(--radius-sm);
  transition: background 0.2s;
}

.feature-card:hover {
  background: var(--color-bg);
}

.feature-icon {
  font-size: 1.5rem;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
}

.feature-card h3 {
  font-size: 1rem;
  margin-bottom: 0.2rem;
}

.feature-card p {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.changelog {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.log-entry {
  padding-left: 1.2rem;
  border-left: 3px solid var(--color-primary);
}

.log-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 0.5rem;
}

.log-version {
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-primary);
}

.log-date {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.log-items {
  list-style: none;
  padding: 0;
}

.log-items li {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  padding: 0.15rem 0;
  padding-left: 1rem;
  position: relative;
}

.log-items li::before {
  content: '•';
  position: absolute;
  left: 0;
  color: var(--color-primary);
}

@media (max-width: 768px) {
  .profile-layout {
    flex-direction: column;
  }
  .profile-sidebar {
    width: 100%;
    position: static;
  }
}
</style>
