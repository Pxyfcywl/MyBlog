# 服务器运维手册

> 日常操作：代码上传、服务器构建、数据同步。

## 前置信息

| 项目 | 值 |
|------|-----|
| 服务器 IP | `20.24.216.189` |
| SSH 用户 | `hatsuyufei` |
| SSH 密钥 | `E:\VibeCoding\hatsuyufei.pem` |
| 项目路径（本地） | `E:\VibeCoding\4-MyBlog` |
| 项目路径（服务器） | `~/MyBlog` |

---

## 一、代码上传到 GitHub

### 1. 本地提交并推送

```powershell
cd E:\VibeCoding\4-MyBlog

# 查看改了什么
git status

# 添加所有改动
git add .

# 提交（写清楚改了什么）
git commit -m "描述你的改动"

# 推送到 GitHub
git push
```

### 2. 常见情况

```powershell
# 新增文件后提交
git add src/views/NewPage.vue
git commit -m "新增页面: NewPage"

# 修改文件后提交
git commit -am "修复了xxx的bug"  # -am 跳过 add（仅限已跟踪的文件）

# 查看提交历史
git log --oneline -10
```

### 3. 注意事项

- `.env` 文件不会被上传（已在 `.gitignore` 中排除）
- `blog.db` 和 `uploads/` 也不会被上传
- 推的是**代码**，不是数据

---

## 二、服务器访问与构建

### 1. SSH 登录服务器

```powershell
# Windows CMD / PowerShell
ssh -i E:\VibeCoding\hatsuyufei.pem hatsuyufei@20.24.216.189

# 如果提示权限问题，先修复
icacls E:\VibeCoding\hatsuyufei.pem /inheritance:r
icacls E:\VibeCoding\hatsuyufei.pem /grant:r "%USERNAME%:R"
```

### 2. 拉取最新代码

```bash
cd ~/MyBlog
git pull
```

### 3. 重新构建部署

```bash
# 构建并重启（改了代码后用这个）
docker compose up -d --build

# 只重启，不重新构建（改了 .env 后用这个）
docker compose restart

# 查看运行状态
docker compose ps

# 查看日志（排错用）
docker compose logs -f backend
docker compose logs -f frontend
```

### 4. 完整更新流程

```bash
cd ~/MyBlog
git pull
docker compose up -d --build
```

---

## 三、数据同步（本地 ↔ 服务器）

> `git pull` 只同步代码，不同步数据。
> 数据包括：`blog.db`（数据库）、`uploads/`（图片和文件）。

### 方向一：服务器 → 本地（拉取）

把服务器上新增的文章和图片拉回本地：

```powershell
# 拉数据库
scp -i E:\VibeCoding\hatsuyufei.pem hatsuyufei@20.24.216.189:~/MyBlog/backend/blog.db E:\VibeCoding\4-MyBlog\backend\blog.db

# 拉图片目录（整个目录）
scp -i E:\VibeCoding\hatsuyufei.pem -r hatsuyufei@20.24.216.189:~/MyBlog/backend/uploads E:\VibeCoding\4-MyBlog\backend\
```

### 方向二：本地 → 服务器（推送）

把本地新增的文章和图片传到服务器：

```powershell
# 推数据库
scp -i E:\VibeCoding\hatsuyufei.pem E:\VibeCoding\4-MyBlog\backend\blog.db hatsuyufei@20.24.216.189:~/MyBlog/backend/blog.db

# 推图片目录
scp -i E:\VibeCoding\hatsuyufei.pem -r E:\VibeCoding\4-MyBlog\backend\uploads hatsuyufei@20.24.216.189:~/MyBlog/backend/
```

### 方向三：只同步单个文件

```powershell
# 传一张图片到服务器
scp -i E:\VibeCoding\hatsuyufei.pem E:\VibeCoding\4-MyBlog\backend\uploads\abc.jpg hatsuyufei@20.24.216.189:~/MyBlog/backend/uploads/

# 从服务器下载一张图片
scp -i E:\VibeCoding\hatsuyufei.pem hatsuyufei@20.24.216.189:~/MyBlog/backend/uploads/abc.jpg E:\VibeCoding\4-MyBlog\backend\uploads\
```

### 同步后注意事项

- 覆盖 `blog.db` 后，服务器上的后端会自动读取新数据（SQLite 文件级）
- 如果不确定，可以重启后端：`docker compose restart backend`
- **覆盖操作不可逆**，建议先备份再覆盖

---

## 四、服务器端数据备份

### 手动备份

```bash
# 登录服务器后
mkdir -p ~/backup
cp ~/MyBlog/backend/blog.db ~/backup/blog_$(date +%Y%m%d).db
cp -r ~/MyBlog/backend/uploads ~/backup/uploads_$(date +%Y%m%d)
```

### 定时自动备份（每天凌晨 3 点）

```bash
crontab -e
```

添加：

```
0 3 * * * cp /home/hatsuyufei/MyBlog/backend/blog.db /home/hatsuyufei/backup/blog_$(date +\%Y\%m\%d).db
```

### 查看备份

```bash
ls ~/backup/
```

---

## 五、常用速查

| 操作 | 命令 |
|------|------|
| 本地推代码 | `git add . && git commit -m "xxx" && git push` |
| 服务器更新 | `cd ~/MyBlog && git pull && docker compose up -d --build` |
| 查看状态 | `docker compose ps` |
| 查看日志 | `docker compose logs -f backend` |
| 重启服务 | `docker compose restart` |
| 拉数据到本地 | `scp -i key.pem -r user@ip:~/MyBlog/backend/blog.db .` |
| 推数据到服务器 | `scp -i key.pem blog.db user@ip:~/MyBlog/backend/` |
| SSH 登录 | `ssh -i key.pem user@ip` |
