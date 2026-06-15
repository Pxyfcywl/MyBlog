import axios from 'axios'

const api = axios.create({
  baseURL: '/api',
  timeout: 10000,
})

// 请求拦截器 - 自动带上认证 token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// 响应拦截器 - 统一错误处理
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      console.error('认证失败，请检查密钥')
    }
    return Promise.reject(error)
  }
)

export default api

// ---- 文章 API ----
export const articleApi = {
  list: (params: { page?: number; page_size?: number; tag?: string; category?: string }) =>
    api.get('/articles', { params }),

  detail: (slug: string) => api.get(`/articles/${slug}`),

  search: (q: string, page?: number) =>
    api.get('/articles/search', { params: { q, page } }),

  create: (data: any) => api.post('/articles', data),

  update: (id: number, data: any) => api.put(`/articles/${id}`, data),

  delete: (id: number) => api.delete(`/articles/${id}`),
}

// ---- 标签/分类 API ----
export const tagApi = {
  list: () => api.get('/tags'),
  categories: () => api.get('/categories'),
}

// ---- 上传 API ----
export const uploadApi = {
  image: (file: File) => {
    const formData = new FormData()
    formData.append('file', file)
    return api.post('/upload/image', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
    })
  },
}

// ---- 认证 API ----
export const authApi = {
  verify: () => api.get('/auth/verify'),
}

// ---- 工具箱 API ----
export const toolsApi = {
  // OCR 文件上传
  submitOcr: (files: File[]) => {
    const formData = new FormData()
    files.forEach(f => formData.append('files', f))
    return api.post('/tools/ocr', formData, {
      headers: { 'Content-Type': 'multipart/form-data' },
      timeout: 60000,
    })
  },

  // 查询 OCR 状态
  getOcrStatus: (batchId: string) =>
    api.get(`/tools/ocr/${batchId}`),

  // 规则审查
  review: (data: {
    batch_id: string
    keywords?: string[]
    date_start?: string
    date_end?: string
  }) => api.post('/tools/review', data, { timeout: 120000 }),

  // LLM 智能审查
  llmReview: (data: {
    batch_id: string
    review_prompt: string
    base_url?: string
    api_key?: string
    model?: string
  }) => api.post('/tools/llm-review', data, { timeout: 180000 }),

  // 健康检查（支持自定义配置）
  healthLlm: (data?: { base_url?: string; api_key?: string; model?: string }) =>
    api.post('/tools/health/llm', data || {}, { timeout: 30000 }),
}
