<script setup lang="ts">
import { useRouter } from 'vue-router'

const router = useRouter()

// ==================== 自定义功能 ====================
// 添加方式：在 customTools 数组中加一项
const customTools = [
  { icon: '📄', title: '文档解析', desc: 'PDF/Office 文档解析与 AI 审查', action: '/toolbox/doc-review' },
  { icon: '🤖', title: 'AI 助手', desc: '博客内置 AI 聊天（开发中）', action: '' },
  { icon: '📊', title: '数据统计', desc: '文章阅读量统计（开发中）', action: '' },
]

// ==================== 外部链接 ====================
// 添加方式：在对应分类的 links 数组中加一项
// { name: '显示名称', url: '链接地址', desc: '鼠标悬停说明' }
const linkGroups = [
  {
    title: '🤖 AI 对话',
    links: [
      { name: 'ChatGPT', url: 'https://chat.openai.com', desc: 'OpenAI 旗舰对话模型' },
      { name: 'Gemini', url: 'https://gemini.google.com', desc: 'Google 多模态 AI' },
      { name: 'DeepSeek', url: 'https://chat.deepseek.com', desc: '深度求索对话模型' },
      { name: 'Kimi', url: 'https://kimi.moonshot.cn', desc: '月之暗面长文本 AI' },
      { name: '通义千问', url: 'https://www.qianwen.com/?source=tongyigw', desc: '阿里云大语言模型' },
      { name: '豆包', url: 'https://www.doubao.com', desc: '字节跳动 AI 助手' },
    ]
  },
  {
    title: '🔑 API 控制台',
    links: [
      { name: 'DeepSeek API', url: 'https://platform.deepseek.com', desc: 'DeepSeek 开放平台' },
      { name: 'Mimo API', url: 'https://platform.xiaomimimo.com/console/profile', desc: 'Mimo 开放平台' },
      { name: '阿里云百炼', url: 'https://bailian.console.aliyun.com/cn-beijing?tab=model#/model-market', desc: '阿里云大模型服务平台' },
    ]
  },
  {
    title: '🛠️ 开发工具',
    links: [
      { name: 'GitHub', url: 'https://github.com', desc: '代码托管平台' },
      { name: 'Vercel', url: 'https://vercel.com', desc: '前端部署平台' },
      { name: 'HuggingFace', url: 'https://huggingface.co', desc: 'AI 模型开源社区' },
    ]
  },
]
</script>

<template>
  <div class="toolbox-page">
    <h1 class="page-title">🧰 百宝箱</h1>

    <!-- 自定义功能 -->
    <section class="section">
      <h2 class="section-title">⚡ 我的功能</h2>
      <div class="tool-grid">
        <div
          v-for="tool in customTools"
          :key="tool.title"
          class="tool-card"
          :class="{ disabled: !tool.action }"
          @click="tool.action && router.push(tool.action)"
        >
          <span class="tool-icon">{{ tool.icon }}</span>
          <h3>{{ tool.title }}</h3>
          <p>{{ tool.desc }}</p>
        </div>
      </div>
    </section>

    <!-- 外部链接 -->
    <section v-for="group in linkGroups" :key="group.title" class="section">
      <h2 class="section-title">{{ group.title }}</h2>
      <div class="link-grid">
        <a
          v-for="link in group.links"
          :key="link.name"
          :href="link.url"
          target="_blank"
          rel="noopener noreferrer"
          class="link-card"
          :title="link.desc"
        >
          <span class="link-name">{{ link.name }}</span>
          <span class="link-desc">{{ link.desc }}</span>
          <span class="link-arrow">→</span>
        </a>
      </div>
    </section>
  </div>
</template>

<style scoped>
.toolbox-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

.section {
  margin-bottom: 2rem;
}

.section-title {
  font-size: 1.2rem;
  font-weight: 700;
  margin-bottom: 1rem;
  padding-bottom: 0.5rem;
  border-bottom: 2px solid var(--color-border);
}

/* 自定义功能卡片 */
.tool-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(180px, 1fr));
  gap: 1rem;
}

.tool-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  text-align: center;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  transition: all 0.25s;
  border: 2px solid transparent;
}

.tool-card:hover:not(.disabled) {
  transform: translateY(-3px);
  box-shadow: var(--shadow-hover);
  border-color: var(--color-primary);
}

.tool-card.disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.tool-icon {
  font-size: 2rem;
  display: block;
  margin-bottom: 0.5rem;
}

.tool-card h3 {
  font-size: 1rem;
  margin-bottom: 0.3rem;
}

.tool-card p {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
}

/* 外部链接列表 */
.link-grid {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.link-card {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  padding: 0.7rem 1rem;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  text-decoration: none;
  transition: all 0.2s;
  border: 1px solid var(--color-border);
}

.link-card:hover {
  background: var(--color-bg);
  border-color: var(--color-primary);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.link-name {
  font-weight: 600;
  font-size: 0.95rem;
  color: var(--color-text);
  min-width: 140px;
}

.link-desc {
  flex: 1;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.link-arrow {
  color: var(--color-text-secondary);
  font-size: 1rem;
  transition: transform 0.2s;
}

.link-card:hover .link-arrow {
  transform: translateX(3px);
  color: var(--color-primary);
}
</style>
