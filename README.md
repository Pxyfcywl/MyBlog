# MyBlog - 个人博客系统

Vue 3 + FastAPI + SQLite 个人博客系统

## 功能

- 📝 文章发布/编辑/删除（Markdown + LaTeX + 代码高亮）
- 🏷️ 标签与分类管理
- 🔍 全局搜索
- 🎵 音乐播放器（本地歌曲）
- 🌧️ 下雨白噪音
- 👤 个人主页

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

## Docker 一键部署

```bash
# 1. 复制并修改配置
cp .env.example .env
# 编辑 .env 设置你的密钥

# 2. 构建并启动
docker-compose up -d --build

# 3. 访问
# 前端: http://你的服务器IP
# 后端API: http://你的服务器IP:8000/docs
```

## 目录结构

```
MyBlog/
├── backend/           # FastAPI 后端
│   ├── app/           # 应用代码
│   ├── uploads/       # 图片存储
│   ├── music/         # 音乐文件（放MP3到这里）
│   ├── blog.db        # SQLite 数据库
│   └── Dockerfile
├── frontend/          # Vue 3 前端
│   ├── src/           # 源码
│   └── Dockerfile
├── docker-compose.yml
└── README.md
```

## 添加音乐

将 MP3 文件放入 `backend/music/` 目录，重启后端即可在播放器中看到。

## 发布文章

1. 访问 /editor
2. 输入管理员密钥
3. 新建/编辑/删除文章
