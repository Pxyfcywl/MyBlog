<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { MdEditor } from 'md-editor-v3'
import 'md-editor-v3/lib/style.css'
import { articleApi, uploadApi, authApi } from '../api'
import ConfirmDialog from '../components/ConfirmDialog.vue'

// ==================== 状态管理 ====================
type Mode = 'management' | 'create' | 'edit' | 'delete'
const mode = ref<Mode>('management')

// ---- Slug 生成 ----
function generateSlug(): string {
  const chars = 'abcdefghijklmnopqrstuvwxyz0123456789'
  const timestamp = Date.now().toString(36) // 时间戳转36进制
  let random = ''
  for (let i = 0; i < 4; i++) {
    random += chars[Math.floor(Math.random() * chars.length)]
  }
  return `${timestamp}-${random}`
}

// ---- 认证 ----
const secretKey = ref('')
const isAuthenticated = ref(false)
const authError = ref('')

onMounted(() => {
  const saved = localStorage.getItem('admin_token')
  if (saved) {
    secretKey.value = saved
    verifyKey()
  }
})

async function verifyKey() {
  authError.value = ''
  if (!secretKey.value.trim()) return
  localStorage.setItem('admin_token', secretKey.value.trim())
  try {
    await authApi.verify()
    isAuthenticated.value = true
  } catch {
    authError.value = '密钥错误，请重新输入'
    localStorage.removeItem('admin_token')
    isAuthenticated.value = false
  }
}

function logout() {
  isAuthenticated.value = false
  secretKey.value = ''
  localStorage.removeItem('admin_token')
  mode.value = 'management'
}

// ==================== 文章列表（修改/删除用） ====================
interface ArticleItem {
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

const articleList = ref<ArticleItem[]>([])
const searchQuery = ref('')
const listLoading = ref(false)
const selectedIds = ref<Set<number>>(new Set())

const filteredArticles = computed(() => {
  if (!searchQuery.value.trim()) return articleList.value
  const q = searchQuery.value.toLowerCase()
  return articleList.value.filter(a =>
    a.title.toLowerCase().includes(q) || a.slug.toLowerCase().includes(q)
  )
})

async function loadArticles() {
  listLoading.value = true
  try {
    const res = await articleApi.list({ page: 1, page_size: 200 })
    articleList.value = res.data.items
  } catch (e) {
    console.error('加载文章列表失败:', e)
  } finally {
    listLoading.value = false
  }
}

function toggleSelect(id: number) {
  if (selectedIds.value.has(id)) {
    selectedIds.value.delete(id)
  } else {
    selectedIds.value.add(id)
  }
}

function selectAll() {
  if (selectedIds.value.size === filteredArticles.value.length) {
    selectedIds.value.clear()
  } else {
    filteredArticles.value.forEach(a => selectedIds.value.add(a.id))
  }
}

// ==================== 新建/编辑文章 ====================
const title = ref('')
const slug = ref('')
const content = ref('# 新文章\n\n开始写作...')
const summary = ref('')
const isPinned = ref(false)
const coverImage = ref('')
const tagInput = ref('')
const tags = ref<string[]>([])
const categoryInput = ref('')
const categories = ref<string[]>([])
const publishing = ref(false)
const message = ref('')
const editingId = ref<number | null>(null) // 非null表示编辑模式

// ---- 封面图上传 ----
const coverInputRef = ref<HTMLInputElement | null>(null)

function triggerCoverUpload() {
  coverInputRef.value?.click()
}

async function handleCoverChange(e: Event) {
  const input = e.target as HTMLInputElement
  if (!input.files?.length) return
  const file = input.files[0]
  try {
    const res = await uploadApi.image(file)
    coverImage.value = res.data.url
  } catch (err: any) {
    message.value = '封面图上传失败: ' + (err.response?.data?.detail || err.message)
  }
  input.value = ''
}

function removeCover() {
  coverImage.value = ''
}

// ---- 标签/分类 ----
function addTag() {
  const name = tagInput.value.trim()
  if (name && !tags.value.includes(name)) {
    tags.value.push(name)
  }
  tagInput.value = ''
}

function removeTag(index: number) {
  tags.value.splice(index, 1)
}

function addCategory() {
  const name = categoryInput.value.trim()
  if (name && !categories.value.includes(name)) {
    categories.value.push(name)
  }
  categoryInput.value = ''
}

function removeCategory(index: number) {
  categories.value.splice(index, 1)
}

// ---- 编辑器内图片上传 ----
async function handleUpload(files: File[], callback: (urls: string[]) => void) {
  const urls: string[] = []
  for (const file of files) {
    try {
      const res = await uploadApi.image(file)
      urls.push(res.data.url)
    } catch (e: any) {
      console.error('图片上传失败:', e.response?.data?.detail || e.message)
    }
  }
  callback(urls)
}

// ---- 进入新建模式 ----
function enterCreate() {
  resetForm()
  editingId.value = null
  mode.value = 'create'
}

// ---- 进入编辑模式 ----
async function enterEdit(article: ArticleItem) {
  editingId.value = article.id
  title.value = article.title
  slug.value = article.slug
  content.value = '' // 先清空，下面异步加载完整内容
  summary.value = article.summary
  coverImage.value = article.cover_image
  isPinned.value = article.is_pinned
  tags.value = article.tags.map(t => t.name)
  categories.value = article.categories.map(c => c.name)
  message.value = ''
  mode.value = 'edit'

  // 加载完整文章内容
  try {
    const res = await articleApi.detail(article.slug)
    content.value = res.data.content
  } catch {
    message.value = '加载文章内容失败'
  }
}

// ---- 进入删除模式 ----
function enterDelete() {
  selectedIds.value.clear()
  searchQuery.value = ''
  loadArticles()
  mode.value = 'delete'
}

// ---- 返回管理面板 ----
function backToManagement() {
  mode.value = 'management'
  message.value = ''
}

// ---- 重置表单 ----
function resetForm() {
  title.value = ''
  slug.value = ''
  content.value = '# 新文章\n\n开始写作...'
  summary.value = ''
  coverImage.value = ''
  tags.value = []
  categories.value = []
  isPinned.value = false
  tagInput.value = ''
  categoryInput.value = ''
  message.value = ''
}

// ---- 发布/更新文章 ----
async function publish() {
  if (!title.value || !slug.value || !content.value) {
    message.value = '标题、slug 和内容不能为空'
    return
  }

  publishing.value = true
  message.value = ''

  const data = {
    title: title.value,
    slug: slug.value,
    content: content.value,
    summary: summary.value,
    cover_image: coverImage.value,
    is_pinned: isPinned.value,
    tag_names: tags.value,
    category_names: categories.value,
  }

  try {
    if (editingId.value !== null) {
      // 更新
      await articleApi.update(editingId.value, data)
      message.value = '更新成功！'
    } else {
      // 新建
      await articleApi.create(data)
      message.value = '发布成功！'
      resetForm()
    }
  } catch (e: any) {
    message.value = '操作失败: ' + (e.response?.data?.detail || e.message)
  } finally {
    publishing.value = false
  }
}

// ---- 批量删除 ----
const deleting = ref(false)
const showDeleteConfirm = ref(false)

function confirmBatchDelete() {
  if (selectedIds.value.size === 0) {
    message.value = '请先选择要删除的文章'
    return
  }
  showDeleteConfirm.value = true
}

async function executeBatchDelete() {
  showDeleteConfirm.value = false
  deleting.value = true
  message.value = ''
  let success = 0
  let failed = 0

  for (const id of selectedIds.value) {
    try {
      await articleApi.delete(id)
      success++
    } catch {
      failed++
    }
  }

  deleting.value = false
  selectedIds.value.clear()
  message.value = failed > 0
    ? `删除完成：成功 ${success} 篇，失败 ${failed} 篇`
    : `成功删除 ${success} 篇文章`

  // 刷新列表
  await loadArticles()
}
</script>

<template>
  <div class="editor-page">
    <h1 class="page-title">📝 文章管理</h1>

    <!-- ===== 认证区域 ===== -->
    <div class="auth-section" v-if="!isAuthenticated">
      <p>请输入管理员密钥</p>
      <div class="auth-input">
        <input
          v-model="secretKey"
          type="password"
          placeholder="输入管理员密钥..."
          @keydown.enter="verifyKey"
        />
        <button @click="verifyKey" :disabled="!secretKey.trim()">确认</button>
      </div>
      <p v-if="authError" class="auth-error">{{ authError }}</p>
    </div>

    <!-- ===== 已认证后的管理面板 ===== -->
    <template v-if="isAuthenticated">
      <div class="auth-status">
        <span>✅ 已认证</span>
        <button class="logout-btn" @click="logout">
          退出认证
        </button>
      </div>

      <!-- ===== 管理面板主页 ===== -->
      <div v-if="mode === 'management'" class="management-panel">
        <div class="action-cards">
          <div class="action-card" @click="enterCreate">
            <div class="action-icon">✏️</div>
            <h3>新建文章</h3>
            <p>撰写并发布一篇新文章</p>
          </div>
          <div class="action-card" @click="loadArticles(); mode = 'edit'">
            <div class="action-icon">📝</div>
            <h3>修改文章</h3>
            <p>查找并编辑已有文章</p>
          </div>
          <div class="action-card delete-card" @click="enterDelete">
            <div class="action-icon">🗑️</div>
            <h3>删除文章</h3>
            <p>批量选择并删除文章</p>
          </div>
        </div>
      </div>

      <!-- ===== 文章列表（修改/删除共用，编辑表单未打开时显示） ===== -->
      <div v-if="(mode === 'edit' || mode === 'delete') && editingId === null" class="list-section">
        <div class="list-header">
          <button class="back-btn" @click="backToManagement">← 返回</button>
          <h2>{{ mode === 'edit' ? '选择文章进行编辑' : '选择文章进行删除' }}</h2>
          <div class="search-box">
            <input v-model="searchQuery" placeholder="🔍 搜索文章标题或slug..." />
          </div>
        </div>

        <div v-if="listLoading" class="loading">加载中...</div>

        <template v-else>
          <!-- 删除模式：全选 + 批量删除 -->
          <div v-if="mode === 'delete'" class="batch-bar">
            <label class="select-all">
              <input
                type="checkbox"
                :checked="selectedIds.size === filteredArticles.length && filteredArticles.length > 0"
                @change="selectAll"
              />
              全选 (已选 {{ selectedIds.size }} 篇)
            </label>
            <button
              class="batch-delete-btn"
              :disabled="selectedIds.size === 0 || deleting"
              @click="confirmBatchDelete"
            >
              {{ deleting ? '删除中...' : `删除选中 (${selectedIds.size})` }}
            </button>
          </div>

          <div class="article-list-scroll">
            <div
              v-for="article in filteredArticles"
              :key="article.id"
              class="list-item"
              :class="{ selected: selectedIds.has(article.id) }"
              @click="mode === 'edit' ? enterEdit(article) : toggleSelect(article.id)"
            >
              <input
                v-if="mode === 'delete'"
                type="checkbox"
                :checked="selectedIds.has(article.id)"
                @click.stop
                @change="toggleSelect(article.id)"
                class="item-check"
              />
              <span v-if="article.is_pinned" class="pin-icon">📌</span>
              <span class="item-title">{{ article.title }}</span>
              <span class="item-date">{{ new Date(article.created_at).toLocaleDateString('zh-CN') }}</span>
              <button v-if="mode === 'edit'" class="item-edit-btn" @click.stop="enterEdit(article)">编辑</button>
            </div>
            <div v-if="filteredArticles.length === 0" class="empty">
              {{ searchQuery ? '没有找到匹配的文章' : '暂无文章' }}
            </div>
          </div>
        </template>
      </div>

      <!-- ===== 新建/编辑表单 ===== -->
      <div v-if="mode === 'create' || (mode === 'edit' && editingId !== null)" class="editor-form">
        <div class="form-header">
          <button class="back-btn" @click="editingId !== null ? editingId = null : backToManagement()">← 返回</button>
          <h2>{{ editingId !== null ? '编辑文章' : '新建文章' }}</h2>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>标题</label>
            <input v-model="title" placeholder="文章标题" />
          </div>
          <div class="form-group">
            <label>Slug (URL路径)</label>
            <div class="slug-input">
              <input v-model="slug" placeholder="my-article-slug" />
              <button class="gen-btn" @click="slug = generateSlug()" title="一键生成">🎲</button>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>摘要</label>
          <input v-model="summary" placeholder="一句话描述（可选）" />
        </div>

        <!-- 封面图 -->
        <div class="form-group">
          <label>封面图</label>
          <div class="cover-upload">
            <input ref="coverInputRef" type="file" accept="image/*" style="display: none" @change="handleCoverChange" />
            <div v-if="coverImage" class="cover-preview">
              <img :src="coverImage" alt="封面预览" />
              <button class="remove-cover" @click="removeCover">✕</button>
            </div>
            <button v-else class="cover-btn" @click="triggerCoverUpload">📷 选择封面图</button>
          </div>
        </div>

        <div class="form-row">
          <div class="form-group">
            <label>标签</label>
            <div class="tag-input">
              <input v-model="tagInput" placeholder="输入后回车" @keydown.enter.prevent="addTag" />
              <span v-for="(tag, i) in tags" :key="i" class="tag-chip">
                {{ tag }} <button @click="removeTag(i)">×</button>
              </span>
            </div>
          </div>
          <div class="form-group">
            <label>分类</label>
            <div class="tag-input">
              <input v-model="categoryInput" placeholder="输入后回车" @keydown.enter.prevent="addCategory" />
              <span v-for="(cat, i) in categories" :key="i" class="tag-chip category-chip">
                {{ cat }} <button @click="removeCategory(i)">×</button>
              </span>
            </div>
          </div>
        </div>

        <div class="form-group">
          <label><input type="checkbox" v-model="isPinned" /> 置顶</label>
        </div>

        <div class="form-group">
          <label>内容 (Markdown)</label>
          <MdEditor v-model="content" language="zh-CN" style="height: 500px" :onUploadImg="handleUpload" />
        </div>

        <div class="form-actions">
          <button class="publish-btn" @click="publish" :disabled="publishing">
            {{ publishing ? '提交中...' : (editingId !== null ? '保存修改' : '发布文章') }}
          </button>
          <span v-if="message" class="message" :class="{ error: message.includes('失败') || message.includes('错误') }">
            {{ message }}
          </span>
        </div>
      </div>
    </template>

    <!-- 确认删除弹窗 -->
    <ConfirmDialog
      :visible="showDeleteConfirm"
      title="确认删除"
      :message="`确定要删除选中的 ${selectedIds.size} 篇文章吗？此操作不可撤销。`"
      confirmText="删除"
      cancelText="取消"
      type="danger"
      @confirm="executeBatchDelete"
      @cancel="showDeleteConfirm = false"
    />
  </div>
</template>

<style scoped>
.editor-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 1.5rem;
}

/* ===== 认证 ===== */
.auth-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 2rem;
  box-shadow: var(--shadow-card);
  text-align: center;
}

.auth-section p {
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
}

.auth-input {
  display: flex;
  gap: 0.8rem;
  max-width: 400px;
  margin: 0 auto;
}

.auth-input input {
  flex: 1;
  padding: 0.6rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  outline: none;
}

.auth-input input:focus { border-color: var(--color-primary); }

.auth-input button {
  padding: 0.6rem 1.5rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 600;
}

.auth-input button:disabled { opacity: 0.5; cursor: not-allowed; }

.auth-error { color: #ef4444; font-size: 0.85rem; margin-top: 0.8rem; }

.auth-status {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  font-size: 0.9rem;
  color: #10b981;
}

.logout-btn {
  background: none;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  padding: 0.3rem 0.8rem;
  cursor: pointer;
  font-size: 0.85rem;
  color: var(--color-text-secondary);
}

.logout-btn:hover { border-color: #ef4444; color: #ef4444; }

/* ===== 管理面板 ===== */
.management-panel {
  margin-top: 1rem;
}

.action-cards {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 1.5rem;
}

.action-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 2rem 1.5rem;
  box-shadow: var(--shadow-card);
  cursor: pointer;
  text-align: center;
  transition: all 0.25s;
  border: 2px solid transparent;
}

.action-card:hover {
  transform: translateY(-4px);
  box-shadow: var(--shadow-hover);
  border-color: var(--color-primary);
}

.action-card.delete-card:hover {
  border-color: #ef4444;
}

.action-icon {
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.action-card h3 {
  font-size: 1.2rem;
  margin-bottom: 0.5rem;
}

.action-card p {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
}

/* ===== 文章列表 ===== */
.list-section {
  margin-top: 1rem;
}

.list-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}

.list-header h2 {
  font-size: 1.3rem;
  flex: 1;
}

.search-box input {
  padding: 0.5rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: 999px;
  font-size: 0.9rem;
  outline: none;
  width: 250px;
}

.search-box input:focus { border-color: var(--color-primary); }

.back-btn {
  padding: 0.4rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  transition: all 0.2s;
}

.back-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }

.batch-bar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0.8rem 1rem;
  background: var(--color-surface);
  border-radius: var(--radius-sm);
  margin-bottom: 1rem;
  box-shadow: var(--shadow-card);
}

.select-all {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  cursor: pointer;
  font-size: 0.9rem;
}

.batch-delete-btn {
  padding: 0.5rem 1.5rem;
  background: #ef4444;
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-weight: 600;
  transition: background 0.2s;
}

.batch-delete-btn:hover:not(:disabled) { background: #dc2626; }
.batch-delete-btn:disabled { opacity: 0.5; cursor: not-allowed; }

/* Slug 输入 */
.slug-input {
  display: flex;
  gap: 0.5rem;
}

.slug-input input {
  flex: 1;
}

.gen-btn {
  padding: 0 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
  cursor: pointer;
  font-size: 1.1rem;
  transition: all 0.2s;
}

.gen-btn:hover {
  border-color: var(--color-primary);
  background: var(--color-bg);
}

/* 文章滚动列表 */
.article-list-scroll {
  max-height: 480px;
  overflow-y: auto;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  background: var(--color-surface);
}

.list-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 1rem;
  cursor: pointer;
  transition: background 0.15s;
  border-bottom: 1px solid var(--color-border);
}

.list-item:last-child {
  border-bottom: none;
}

.list-item:hover {
  background: var(--color-bg);
}

.list-item.selected {
  background: #f0f7ff;
}

.item-check {
  width: 16px;
  height: 16px;
  cursor: pointer;
  flex-shrink: 0;
}

.pin-icon {
  font-size: 0.85rem;
  flex-shrink: 0;
}

.item-title {
  flex: 1;
  font-size: 0.95rem;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.item-date {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  flex-shrink: 0;
}

.item-edit-btn {
  padding: 0.25rem 0.8rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  cursor: pointer;
  font-size: 0.8rem;
  flex-shrink: 0;
  opacity: 0;
  transition: opacity 0.15s;
}

.list-item:hover .item-edit-btn {
  opacity: 1;
}

/* ===== 编辑表单 ===== */
.editor-form {
  margin-top: 1rem;
}

.form-header {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1.5rem;
}

.form-header h2 { font-size: 1.3rem; }

.editor-form .form-row {
  display: flex;
  gap: 1rem;
  margin-bottom: 1.2rem;
}

.editor-form .form-row .form-group { flex: 1; }

.form-group {
  margin-bottom: 1.2rem;
}

.form-group label {
  display: block;
  font-size: 0.9rem;
  font-weight: 600;
  margin-bottom: 0.4rem;
  color: var(--color-text-secondary);
}

.form-group input[type="text"],
.form-group input:not([type]):not([type="checkbox"]) {
  width: 100%;
  padding: 0.6rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.95rem;
  outline: none;
}

.form-group input:focus { border-color: var(--color-primary); }

.slug-input input {
  flex: 1;
  min-width: 0;
}

.tag-input {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  align-items: center;
}

.tag-input input {
  flex: 1;
  min-width: 120px;
  padding: 0.5rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  outline: none;
}

.tag-chip {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.2rem 0.8rem;
  background: var(--color-primary);
  color: #fff;
  border-radius: 999px;
  font-size: 0.85rem;
}

.category-chip { background: #10b981; }

.tag-chip button {
  background: none;
  border: none;
  color: #fff;
  cursor: pointer;
  font-size: 1rem;
  padding: 0;
  line-height: 1;
}

/* 封面图 */
.cover-upload { display: flex; align-items: flex-start; }

.cover-preview {
  position: relative;
  max-width: 300px;
  border-radius: var(--radius-sm);
  overflow: hidden;
  box-shadow: var(--shadow-card);
}

.cover-preview img { width: 100%; height: auto; display: block; }

.remove-cover {
  position: absolute;
  top: 0.5rem;
  right: 0.5rem;
  width: 28px;
  height: 28px;
  border-radius: 50%;
  border: none;
  background: rgba(0, 0, 0, 0.6);
  color: #fff;
  cursor: pointer;
  font-size: 0.9rem;
  display: flex;
  align-items: center;
  justify-content: center;
}

.remove-cover:hover { background: rgba(239, 68, 68, 0.8); }

.cover-btn {
  padding: 0.8rem 1.5rem;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-sm);
  background: none;
  cursor: pointer;
  font-size: 0.95rem;
  color: var(--color-text-secondary);
}

.cover-btn:hover { border-color: var(--color-primary); color: var(--color-primary); }

.form-actions {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-top: 0.5rem;
}

.publish-btn {
  padding: 0.7rem 2rem;
  background: var(--color-primary);
  color: #fff;
  border: none;
  border-radius: var(--radius-sm);
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
}

.publish-btn:hover:not(:disabled) { background: var(--color-primary-hover); }
.publish-btn:disabled { opacity: 0.6; cursor: not-allowed; }

.message { font-size: 0.9rem; color: #10b981; }
.message.error { color: #ef4444; }

.loading, .empty {
  text-align: center;
  padding: 2rem;
  color: var(--color-text-secondary);
}

/* ===== 响应式 ===== */
@media (max-width: 768px) {
  .action-cards { grid-template-columns: 1fr; }
  .form-row { flex-direction: column; gap: 0; }
  .list-header { flex-direction: column; align-items: stretch; }
  .search-box input { width: 100%; }
}
</style>
