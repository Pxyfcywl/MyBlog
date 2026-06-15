<script setup lang="ts">
import { ref, computed, onUnmounted } from 'vue'
import { MdPreview } from 'md-editor-v3'
import 'md-editor-v3/lib/preview.css'
import { toolsApi } from '../api'

// ==================== LLM 配置 ====================
const llmConfig = ref({
  base_url: '',
  api_key: '',
  model: '',
})
const llmConnected = ref(false)
const llmTesting = ref(false)
const llmTestResult = ref('')
const llmTestOk = ref(false)

async function testLlmConnection() {
  llmTesting.value = true
  llmTestResult.value = ''
  llmTestOk.value = false
  try {
    const res = await toolsApi.healthLlm({
      base_url: llmConfig.value.base_url || undefined,
      api_key: llmConfig.value.api_key || undefined,
      model: llmConfig.value.model || undefined,
    })
    llmTestOk.value = res.data.ok
    llmTestResult.value = res.data.detail
    if (res.data.ok) {
      llmConnected.value = true
    }
  } catch (err: any) {
    llmTestOk.value = false
    llmTestResult.value = err.response?.data?.detail || '连接失败'
  } finally {
    llmTesting.value = false
  }
}

// ==================== 解析流程状态 ====================
type Step = 'upload' | 'processing' | 'done' | 'review'
const step = ref<Step>('upload')

// 上传
const selectedFiles = ref<File[]>([])
const uploading = ref(false)
const uploadError = ref('')

// 解析
const batchId = ref('')
const pollTimer = ref<number | null>(null)
const extractState = ref('')
const extractProgress = ref({ total: 0, done: 0, failed: 0, running: 0 })
const extractFiles = ref<{ file_name: string; state: string; err_msg: string }[]>([])

// LLM 审查
const reviewPrompt = ref('')
const reviewLoading = ref(false)
const reviewResult = ref('')
const reviewError = ref('')

// ==================== 文件选择 ====================
function onFileSelect(e: Event) {
  const input = e.target as HTMLInputElement
  if (input.files) {
    selectedFiles.value = Array.from(input.files)
  }
}

function onDrop(e: DragEvent) {
  e.preventDefault()
  if (e.dataTransfer?.files) {
    selectedFiles.value = Array.from(e.dataTransfer.files)
  }
}

function removeFile(index: number) {
  selectedFiles.value.splice(index, 1)
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / (1024 * 1024)).toFixed(1) + ' MB'
}

// ==================== 提交上传 ====================
async function submitUpload() {
  if (selectedFiles.value.length === 0) return
  uploading.value = true
  uploadError.value = ''

  try {
    const res = await toolsApi.submitOcr(selectedFiles.value)
    batchId.value = res.data.batch_id
    step.value = 'processing'
    startPolling()
  } catch (err: any) {
    uploadError.value = err.response?.data?.detail || '上传失败，请重试'
  } finally {
    uploading.value = false
  }
}

// ==================== 轮询状态 ====================
function startPolling() {
  pollStatus()
  pollTimer.value = window.setInterval(pollStatus, 3000)
}

async function pollStatus() {
  try {
    const res = await toolsApi.getOcrStatus(batchId.value)
    const data = res.data
    extractState.value = data.state
    extractProgress.value = data.progress
    extractFiles.value = data.files

    if (data.state === 'done') {
      stopPolling()
      step.value = 'done'
    }
  } catch (err) {
    console.error('轮询失败', err)
  }
}

function stopPolling() {
  if (pollTimer.value) {
    clearInterval(pollTimer.value)
    pollTimer.value = null
  }
}

onUnmounted(stopPolling)

const progressPercent = computed(() => {
  const p = extractProgress.value
  if (!p.total) return 0
  return Math.round(((p.done + p.failed) / p.total) * 100)
})

// ==================== LLM 审查 ====================
const canReview = computed(() => reviewPrompt.value.trim().length > 0 && !reviewLoading.value)

async function submitReview() {
  if (!canReview.value) return
  reviewLoading.value = true
  reviewError.value = ''
  reviewResult.value = ''

  try {
    const res = await toolsApi.llmReview({
      batch_id: batchId.value,
      review_prompt: reviewPrompt.value.trim(),
      base_url: llmConfig.value.base_url || undefined,
      api_key: llmConfig.value.api_key || undefined,
      model: llmConfig.value.model || undefined,
    })
    reviewResult.value = res.data.review_result
  } catch (err: any) {
    reviewError.value = err.response?.data?.detail || '审查失败，请重试'
  } finally {
    reviewLoading.value = false
  }
}

// ==================== 重置 ====================
function resetAll() {
  stopPolling()
  step.value = 'upload'
  selectedFiles.value = []
  batchId.value = ''
  extractState.value = ''
  extractProgress.value = { total: 0, done: 0, failed: 0, running: 0 }
  extractFiles.value = []
  reviewPrompt.value = ''
  reviewResult.value = ''
  reviewError.value = ''
}
</script>

<template>
  <div class="doc-review-page">
    <h1 class="page-title">📄 文档解析与审查</h1>
    <p class="page-desc">上传 PDF / Office 文档，MinerU 解析为 Markdown 后可交由 LLM 进行智能审查</p>

    <!-- Step 0: LLM 配置 -->
    <section class="section">
      <h2 class="section-title">⚙️ 大模型配置</h2>

      <div class="config-card">
        <div class="config-grid">
          <div class="config-field">
            <label>Base URL</label>
            <input
              v-model="llmConfig.base_url"
              type="text"
              placeholder="留空使用服务端默认值"
            />
          </div>
          <div class="config-field">
            <label>API Key</label>
            <input
              v-model="llmConfig.api_key"
              type="password"
              placeholder="留空使用服务端默认值"
            />
          </div>
          <div class="config-field">
            <label>模型名称</label>
            <input
              v-model="llmConfig.model"
              type="text"
              placeholder="留空使用服务端默认值"
            />
          </div>
        </div>

        <div class="config-actions">
          <button
            class="btn btn-primary"
            :disabled="llmTesting"
            @click="testLlmConnection"
          >
            {{ llmTesting ? '测试中...' : '🔌 测试连接' }}
          </button>

          <span v-if="llmTestResult" class="test-result" :class="llmTestOk ? 'ok' : 'fail'">
            {{ llmTestOk ? '✅' : '❌' }} {{ llmTestResult }}
          </span>
        </div>
      </div>
    </section>

    <!-- Step 1: 上传 -->
    <section v-if="step === 'upload'" class="section">
      <h2 class="section-title">📤 上传文件</h2>

      <div
        class="drop-zone"
        :class="{ 'has-files': selectedFiles.length > 0 }"
        @drop.prevent="onDrop"
        @dragover.prevent
      >
        <div v-if="selectedFiles.length === 0" class="drop-hint">
          <span class="drop-icon">📁</span>
          <p>拖拽文件到此处，或</p>
          <label class="btn btn-primary">
            选择文件
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.png,.jpg,.jpeg"
              style="display: none"
              @change="onFileSelect"
            />
          </label>
          <p class="drop-tip">支持 PDF、Word、PPT、Excel、图片，单文件最大 200MB</p>
        </div>

        <div v-else class="file-list">
          <div v-for="(file, i) in selectedFiles" :key="i" class="file-item">
            <span class="file-icon">📎</span>
            <span class="file-name">{{ file.name }}</span>
            <span class="file-size">{{ formatSize(file.size) }}</span>
            <button class="btn-remove" @click="removeFile(i)">✕</button>
          </div>
          <label class="btn btn-secondary btn-add">
            + 添加更多
            <input
              type="file"
              multiple
              accept=".pdf,.doc,.docx,.ppt,.pptx,.xls,.xlsx,.png,.jpg,.jpeg"
              style="display: none"
              @change="onFileSelect"
            />
          </label>
        </div>
      </div>

      <p v-if="uploadError" class="error-text">{{ uploadError }}</p>

      <div class="actions">
        <button
          class="btn btn-primary btn-lg"
          :disabled="selectedFiles.length === 0 || uploading"
          @click="submitUpload"
        >
          {{ uploading ? '提交中...' : '开始解析' }}
        </button>
      </div>
    </section>

    <!-- Step 2: 解析中 -->
    <section v-if="step === 'processing'" class="section">
      <h2 class="section-title">⏳ 解析中</h2>

      <div class="progress-card">
        <div class="progress-bar-wrapper">
          <div
            class="progress-bar"
            :style="{ width: progressPercent + '%' }"
          ></div>
        </div>
        <div class="progress-text">
          {{ extractProgress.done }} / {{ extractProgress.total }} 个文件已完成
          <span v-if="extractProgress.failed > 0" class="text-error">
            （{{ extractProgress.failed }} 个失败）
          </span>
        </div>

        <div class="file-status-list">
          <div
            v-for="file in extractFiles"
            :key="file.file_name"
            class="file-status"
          >
            <span class="status-icon">
              {{ file.state === 'done' ? '✅' : file.state === 'failed' ? '❌' : '⏳' }}
            </span>
            <span class="status-name">{{ file.file_name }}</span>
            <span v-if="file.state === 'failed'" class="status-error">{{ file.err_msg }}</span>
          </div>
        </div>
      </div>
    </section>

    <!-- Step 3: 解析完成 + 审查 -->
    <section v-if="step === 'done' || step === 'review'" class="section">
      <h2 class="section-title">✅ 解析完成</h2>

      <div class="result-header">
        <span class="badge">{{ extractFiles.length }} 个文件</span>
        <button class="btn btn-primary" @click="step = 'review'">🔍 LLM 智能审查</button>
        <button class="btn btn-secondary" @click="resetAll">🔄 重新上传</button>
      </div>

      <!-- 审查区域 -->
      <div v-if="step === 'review'" class="review-section">
        <h3 class="sub-title">🤖 LLM 智能审查</h3>

        <div class="review-input">
          <textarea
            v-model="reviewPrompt"
            class="review-textarea"
            placeholder="请输入审查要求，例如：&#10;- 检查文档中是否有遗漏的条款&#10;- 日期是否在 2024 年内&#10;- 各文件之间描述是否一致"
            rows="4"
          ></textarea>
          <div class="review-actions">
            <button
              class="btn btn-primary"
              :disabled="!canReview"
              @click="submitReview"
            >
              {{ reviewLoading ? '审查中...' : '开始审查' }}
            </button>
          </div>
        </div>

        <p v-if="reviewError" class="error-text">{{ reviewError }}</p>

        <div v-if="reviewResult" class="review-result">
          <h3 class="sub-title">📋 审查结果</h3>
          <div class="review-content">
            <MdPreview :modelValue="reviewResult" previewTheme="github" />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<style scoped>
.doc-review-page {
  max-width: 960px;
  margin: 0 auto;
  padding: 2rem 1.5rem;
}

.page-title {
  font-size: 1.8rem;
  font-weight: 700;
  margin-bottom: 0.3rem;
}

.page-desc {
  color: var(--color-text-secondary);
  font-size: 0.9rem;
  margin-bottom: 2rem;
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

.sub-title {
  font-size: 1rem;
  font-weight: 600;
  margin-bottom: 0.8rem;
  margin-top: 1.5rem;
}

/* ---- 配置面板 ---- */
.config-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
}

.config-grid {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 1rem;
}

@media (max-width: 768px) {
  .config-grid {
    grid-template-columns: 1fr;
  }
}

.config-field label {
  display: block;
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-text-secondary);
  margin-bottom: 0.3rem;
}

.config-field input {
  width: 100%;
  padding: 0.5rem 0.8rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  background: var(--color-bg);
  color: var(--color-text);
  transition: border-color 0.2s;
}

.config-field input:focus {
  outline: none;
  border-color: var(--color-primary);
}

.config-actions {
  margin-top: 1rem;
  display: flex;
  align-items: center;
  gap: 1rem;
}

.test-result {
  font-size: 0.85rem;
  padding: 0.3rem 0.8rem;
  border-radius: var(--radius-sm);
}

.test-result.ok {
  background: #ecfdf5;
  color: #065f46;
}

.test-result.fail {
  background: #fef2f2;
  color: #991b1b;
}

/* ---- 拖拽上传区域 ---- */
.drop-zone {
  background: var(--color-surface);
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  padding: 2.5rem;
  text-align: center;
  transition: all 0.25s;
}

.drop-zone:hover {
  border-color: var(--color-primary);
}

.drop-zone.has-files {
  text-align: left;
  padding: 1.5rem;
}

.drop-hint {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
}

.drop-icon {
  font-size: 3rem;
}

.drop-tip {
  font-size: 0.8rem;
  color: var(--color-text-secondary);
  margin-top: 0.3rem;
}

/* ---- 文件列表 ---- */
.file-list {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.6rem 0.8rem;
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
}

.file-icon {
  font-size: 1.1rem;
}

.file-name {
  flex: 1;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: var(--color-text-secondary);
  font-size: 0.8rem;
}

.btn-remove {
  background: none;
  border: none;
  color: var(--color-text-secondary);
  cursor: pointer;
  font-size: 1rem;
  padding: 0.2rem;
}

.btn-remove:hover {
  color: #ef4444;
}

.btn-add {
  margin-top: 0.3rem;
  font-size: 0.85rem;
}

/* ---- 进度 ---- */
.progress-card {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
}

.progress-bar-wrapper {
  height: 8px;
  background: var(--color-bg);
  border-radius: 4px;
  overflow: hidden;
  margin-bottom: 0.8rem;
}

.progress-bar {
  height: 100%;
  background: var(--color-primary);
  border-radius: 4px;
  transition: width 0.5s ease;
}

.progress-text {
  font-size: 0.9rem;
  color: var(--color-text-secondary);
  margin-bottom: 1rem;
}

.text-error {
  color: #ef4444;
}

.file-status-list {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.file-status {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.85rem;
}

.status-icon {
  font-size: 1rem;
}

.status-name {
  font-weight: 500;
}

.status-error {
  color: #ef4444;
  font-size: 0.8rem;
}

/* ---- 结果头部 ---- */
.result-header {
  display: flex;
  align-items: center;
  gap: 0.8rem;
  margin-bottom: 1.5rem;
}

.badge {
  background: var(--color-primary);
  color: white;
  padding: 0.25rem 0.8rem;
  border-radius: 999px;
  font-size: 0.8rem;
  font-weight: 600;
}

/* ---- 审查区域 ---- */
.review-section {
  background: var(--color-surface);
  border-radius: var(--radius-lg);
  padding: 1.5rem;
  box-shadow: var(--shadow-card);
  margin-top: 1rem;
}

.review-textarea {
  width: 100%;
  padding: 0.8rem 1rem;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-family: inherit;
  resize: vertical;
  background: var(--color-bg);
  color: var(--color-text);
  transition: border-color 0.2s;
}

.review-textarea:focus {
  outline: none;
  border-color: var(--color-primary);
}

.review-actions {
  margin-top: 0.8rem;
  display: flex;
  gap: 0.8rem;
}

.review-result {
  margin-top: 1rem;
}

.review-content {
  background: var(--color-bg);
  border-radius: var(--radius-sm);
  padding: 1rem;
  overflow: auto;
  max-height: 600px;
}

/* ---- 按钮 ---- */
.btn {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  gap: 0.4rem;
  padding: 0.5rem 1.2rem;
  border-radius: var(--radius-sm);
  font-size: 0.9rem;
  font-weight: 500;
  border: none;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--color-primary);
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: var(--color-primary-hover);
}

.btn-secondary {
  background: var(--color-bg);
  color: var(--color-text);
  border: 1px solid var(--color-border);
}

.btn-secondary:hover:not(:disabled) {
  border-color: var(--color-primary);
  color: var(--color-primary);
}

.btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.btn-lg {
  padding: 0.7rem 2rem;
  font-size: 1rem;
}

/* ---- 错误 ---- */
.error-text {
  color: #ef4444;
  font-size: 0.85rem;
  margin-top: 0.5rem;
}

.actions {
  margin-top: 1.5rem;
  display: flex;
  gap: 0.8rem;
}
</style>
