<script setup lang="ts">
const year = new Date().getFullYear()
</script>

<template>
  <footer class="site-footer">
    <div class="footer-content">
      <p class="copyright">© {{ year }} MyBlog · 用代码构建世界，用文字记录思考</p>
      <p class="tech">
        Powered by
        <span class="tech-tag">Vue 3</span>
        <span class="tech-tag">FastAPI</span>
        <span class="tech-tag">SQLite</span>
      </p>
    </div>
  </footer>
</template>

<style scoped>
.site-footer {
  margin-top: 3rem;
  padding: 2rem 1.5rem;
  border-top: 1px solid var(--color-border);
  text-align: center;
}

.footer-content {
  max-width: 1280px;
  margin: 0 auto;
}

.copyright {
  font-size: 0.85rem;
  color: var(--color-text-secondary);
  margin-bottom: 0.4rem;
}

.tech {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.tech-tag {
  display: inline-block;
  padding: 0.1rem 0.5rem;
  background: var(--color-bg);
  border-radius: 999px;
  font-size: 0.75rem;
  color: var(--color-primary);
}
</style>
