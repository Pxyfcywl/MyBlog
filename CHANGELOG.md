# 更新日志

> 每次提交前更新本文档，记录改动内容和原因。

---

## v0.6.0 — 2026-06-16

### 新增
- **PDF 人工审核模式** — AI 审查完成后可进入人工审核：左侧 AI 结果侧边栏（Markdown 渲染、复制/下载）+ 右侧 PDF 多关键词搜索工具（iframe 嵌入）
- **PDF 搜索工具集成** — `pdf-search-tool.html` 复制到 `frontend/public/`，通过 iframe 加载，保留原有全部功能（分组、JSON 导入导出、匹配统计）
- **本地草书字体** — Ma Shan Zheng 字体文件下载到 `public/fonts/`，Hero 页打字机效果使用，不依赖 Google Fonts CDN

### 变更
- **Hero 页面背景图路径** — 从 `../public/background.jpg` 修正为 `/background.jpg`，修复服务器部署后背景图 404
- **Hero 页打字机样式** — 从纯色改为蓝紫粉渐变流光效果 + 草书字体
- **pdfjs-dist** — 新增依赖 `pdfjs-dist@4.10.38`（PDF 浏览器渲染，备用）

---

## v0.5.0 — 2026-06-15

### 新增
- **服务器运维手册** `docs/server-operations.md` — GitHub 代码上传、SSH 访问、Docker 构建、数据双向同步（scp）完整流程
- **Agent 记忆系统** — 6 个记忆文件覆盖项目概况、LLM 配置模式、Nginx 踩坑、Azure 部署、数据同步策略

### 变更
- **README.md 重写** — 补充文档解析/AI 审查功能、完整环境变量表、前后端路由表、目录结构、数据同步指引
- **发文档.md 移入 docs/** — 从项目根目录移到 `docs/发文档.md`，根目录不再散落参考文档

---

## v0.4.0 — 2026-06-15

### 新增
- **文档解析功能** `POST /api/tools/ocr` — MinerU API 批量上传 → 轮询 → 下载 zip → 提取 Markdown
- **AI 智能审查** `POST /api/tools/llm-review` — LLM 审查解析结果，支持用户自定义审查提示词
- **LLM 连接测试** `POST /api/tools/health/llm` — 前端可测试 LLM 配置是否可用
- **工具箱页面** `/toolbox` + `/toolbox/doc-review` — 文件拖拽上传、解析进度、LLM 配置面板、审查结果 Markdown 渲染
- **可配置 LLM 供应商** — 前端支持 base_url / api_key / model 三元组输入，支持 DeepSeek / Mimo / 百炼 / 智谱
- **标签分类自动清理** — 标签和分类列表接口返回前自动删除 0 文章的空标签/分类
- **Azure VM 部署** — Docker Compose 部署到 Azure VM（Ubuntu 22.04），含 swap 配置、Nginx 代理
- **部署文档** `docs/deploy-azure.md` — 从零到上线完整指南

### 变更
- **Nginx 配置** — `/uploads/` 和 `/music/` 加 `^~` 前缀，修复正则静态资源规则拦截图片请求的 404 问题
- **构建脚本** — 移除 `vue-tsc`，改为 `vite build`，避免服务器低内存环境下构建超时
- **文章详情页宽度** — `max-width` 从 860px 改为 1000px
- **个人主页** — 更新功能列表、添加 v0.4.0 更新日志
- **Docker Compose** — 环境变量从内联改为 `env_file: ./backend/.env`

### 依赖
- 后端新增 `httpx>=0.27.0`（MinerU API 调用）

---

## v0.3.0 — 初始版本

### 功能
- 文章发布/编辑/删除（Markdown + LaTeX + 代码高亮）
- 标签与分类管理
- 全局搜索
- 音乐播放器（APlayer + 本地 MP3）
- 下雨白噪音
- 个人主页
- Docker Compose 一键部署
