# 提交记录

> 每次 commit 前更新本文档，记录改了哪些文件、改了什么。返工溯源用。

---

## 2026-06-15 文档整理

### 本次改动

| 文件 | 操作 | 说明 |
|------|------|------|
| `README.md` | 修改 | 重写：补充功能列表、环境变量表、路由表、目录结构、数据同步 |
| `CHANGELOG.md` | 新增 | 用户侧版本更新日志 |
| `COMMIT_LOG.md` | 新增 | 本文档，提交级文件变更记录 |
| `docs/server-operations.md` | 新增 | 服务器运维手册（GitHub上传、SSH、构建、数据同步） |
| `docs/发文档.md` | 移动 | 从项目根目录 `发文档.md` 移入 `docs/` |

### 备注
- `发文档.md` 内容无改动，仅位置变更
- 删除根目录的 `发文档.md`

---

## 1b1538f fix nginx upload proxy priority

### 本次改动

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/nginx.conf` | 修改 | `/uploads/` 和 `/music/` 加 `^~` 前缀，修复正则规则拦截图片 404 |

### 备注
- 原因：`~* \.(jpg|png|css|js)...` 正则优先级高于普通 prefix location

---

## 4237b31 skip vue-tsc in build

### 本次改动

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/package.json` | 修改 | build 脚本从 `vue-tsc && vite build` 改为 `vite build` |

### 备注
- 原因：Azure VM 894MB 内存，vue-tsc 类型检查导致构建超时

---

## c35d490 fix avatar path

### 本次改动

| 文件 | 操作 | 说明 |
|------|------|------|
| `frontend/public/pictures/nomove.png` | 新增 | 头像图片复制到 public 目录 |
| `frontend/src/views/Profile.vue` | 修改 | 头像路径从 `../pictures/nomove.png` 改为 `/pictures/nomove.png` |

### 备注
- 原因：相对路径在构建后无法正确解析，改用绝对路径

---

## d3d6bf8 first commit

### 本次改动

全部文件首次提交。

| 目录 | 说明 |
|------|------|
| `backend/` | FastAPI 后端（app/、Dockerfile、requirements.txt） |
| `frontend/` | Vue 3 前端（src/、Dockerfile、nginx.conf） |
| `docker-compose.yml` | 容器编排 |
| `.env.example` | 环境变量模板 |
| `.gitignore` | 排除 .env、blog.db、uploads/、node_modules、__pycache__ |
| `deploy.sh` | 服务器部署脚本 |
| `docs/deploy-azure.md` | Azure 部署指南 |
| `docs/mineru-api.md` | MinerU API 参考 |
| `发文档.md` | LLM/Embedding/MinerU 配置参考 |
