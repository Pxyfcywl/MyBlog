# MyBlog - 个人博客系统

Vue 3 + FastAPI + SQLite 个人博客系统，支持 Docker 一键部署到云服务器。

## 功能

### 博客核心
- 📝 文章发布/编辑/删除（Markdown + LaTeX + 代码高亮）
- 🏷️ 标签与分类管理（自动清理空标签/分类）
- 🔍 全局搜索（标题 + 标签）
- 🎵 音乐播放器（APlayer，本地 MP3）
- 🌧️ 下雨白噪音
- 👤 个人主页 + 头像

### AI 工具箱
- 📄 文档解析 — PDF/Office/图片 → Markdown（MinerU API）
- 🤖 AI 智能审查 — LLM 审查解析结果，支持自定义审查提示词
- 📋 人工审核 — AI 审查后进入 PDF 原文查看 + 多关键词搜索 + 结果侧边栏
- 🔧 可配置 LLM 供应商（DeepSeek / Mimo / 阿里云百炼 / 智谱，OpenAI 兼容格式）

## 本地开发

```bash
# 后端
cd backend
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
cp .env.example .env    # 修改密钥
uvicorn app.main:app --reload

# 前端（另一个终端）
cd frontend
npm install
npm run dev
```

打开 http://localhost:5173

## Docker 部署

```bash
# 1. 复制并修改配置
cp .env.example .env
# 编辑 .env 设置你的密钥

# 2. 构建并启动
docker compose up -d --build

# 3. 访问
# 前端: http://你的服务器IP
# 后端API: http://你的服务器IP:8000/docs
```

详细部署指南：[docs/deploy-azure.md](docs/deploy-azure.md)
日常运维操作：[docs/server-operations.md](docs/server-operations.md)

## 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `ADMIN_SECRET_KEY` | 管理员密钥 | `your-secret` |
| `DATABASE_URL` | 数据库连接 | `sqlite+aiosqlite:///./blog.db` |
| `UPLOAD_DIR` | 上传目录 | `./uploads` |
| `FRONTEND_URL` | 前端地址（CORS） | `http://localhost:5173` |
| `MINERU_API_KEY` | MinerU 文档解析 Token | 见 [发文档.md](docs/发文档.md) |
| `LLM_BASE_URL` | LLM 接口地址 | `https://api.deepseek.com` |
| `LLM_API_KEY` | LLM API 密钥 | - |
| `LLM_MODEL_NAME` | LLM 模型名 | `deepseek-v4-pro` |

完整供应商配置：[docs/发文档.md](docs/发文档.md)

## 路由

### 前端页面

| 路径 | 页面 |
|------|------|
| `/` | Hero 首页 |
| `/home` | 文章列表 |
| `/tags` | 标签分类 |
| `/article/:slug` | 文章详情 |
| `/editor` | 文章编辑器 |
| `/profile` | 个人主页 |
| `/toolbox` | 工具箱 |
| `/toolbox/doc-review` | 文档解析 |

### 后端 API

| 路径 | 说明 |
|------|------|
| `/api/articles/` | 文章 CRUD |
| `/api/tags/` | 标签管理 |
| `/api/categories/` | 分类管理 |
| `/api/search/` | 搜索 |
| `/api/tools/ocr` | 文档解析 |
| `/api/tools/review` | 规则审查 |
| `/api/tools/llm-review` | LLM 审查 |
| `/api/tools/health/llm` | LLM 连接测试 |
| `/api/upload/` | 文件上传 |
| `/uploads/*` | 静态文件 |

## 目录结构

```
MyBlog/
├── backend/                # FastAPI 后端
│   ├── app/
│   │   ├── config.py       # 配置（Pydantic Settings）
│   │   ├── main.py         # 入口
│   │   ├── models.py       # SQLAlchemy 模型
│   │   ├── routers/        # 路由
│   │   └── services/       # 业务逻辑（mineru, llm, reviewer）
│   ├── uploads/            # 图片存储
│   ├── music/              # 音乐文件
│   ├── blog.db             # SQLite 数据库
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/               # Vue 3 前端
│   ├── src/
│   │   ├── views/          # 页面组件
│   │   ├── api/            # API 封装
│   │   └── router/         # 路由
│   ├── nginx.conf          # Nginx 配置（^~ 优先级）
│   └── Dockerfile
├── docs/                   # 文档
├── docker-compose.yml
├── .env.example            # 环境变量模板
└── README.md
```

## 数据同步

`git pull` 只同步代码。数据库和图片需要单独同步：

```bash
# 服务器 → 本地
scp -i key.pem -r user@ip:~/MyBlog/backend/blog.db ./backend/
scp -i key.pem -r user@ip:~/MyBlog/backend/uploads ./backend/

# 本地 → 服务器
scp -i key.pem blog.db user@ip:~/MyBlog/backend/
scp -i key.pem -r uploads user@ip:~/MyBlog/backend/
```

详细说明：[docs/server-operations.md](docs/server-operations.md)

## 更新日志

见 [CHANGELOG.md](CHANGELOG.md)，每次提交前更新。
