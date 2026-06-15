# Azure VM 部署指南

> Ubuntu 22.04 + Docker Compose，从零到上线。

## 一、服务器准备

### 1. SSH 登录

```bash
ssh azureuser@你的服务器公网IP
```

### 2. 安装 Docker

```bash
# 更新系统
sudo apt update && sudo apt upgrade -y

# 安装 Docker
curl -fsSL https://get.docker.com | sudo sh

# 把当前用户加入 docker 组（免 sudo）
sudo usermod -aG docker $USER
newgrp docker

# 验证
docker --version
docker compose version
```

### 3. 安装 Git

```bash
sudo apt install git -y
```

---

## 二、部署项目

### 1. 克隆代码

```bash
cd ~
git clone https://github.com/你的用户名/MyBlog.git
cd MyBlog
```

### 2. 创建 .env 文件

```bash
cat > backend/.env << 'EOF'
ADMIN_SECRET_KEY=你的管理员密钥
DATABASE_URL=sqlite+aiosqlite:///./blog.db
UPLOAD_DIR=./uploads
FRONTEND_URL=http://你的服务器公网IP
MINERU_API_KEY=你的MinerU密钥
LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4
LLM_API_KEY=你的智谱密钥
LLM_MODEL_NAME=glm-4-flash
EOF
```

### 3. 构建并启动

```bash
docker compose up -d --build
```

### 4. 验证

```bash
# 查看容器状态
docker compose ps

# 查看日志
docker compose logs -f

# 测试访问
curl http://localhost
```

浏览器打开 `http://你的服务器公网IP` 即可访问。

---

## 三、Azure 网络配置

在 Azure 门户 → 虚拟机 → 网络 → 入站端口规则，放行：

| 端口 | 协议 | 用途 |
|------|------|------|
| 22 | TCP | SSH |
| 80 | TCP | HTTP（前端） |
| 8000 | TCP | API（可选，前端已代理） |

---

## 四、后续更新

每次改完代码推到 GitHub 后：

```bash
cd ~/MyBlog
git pull
docker compose up -d --build
```

---

## 五、数据备份

SQLite 数据库在 `backend/blog.db`，定期备份：

```bash
# 手动备份
cp ~/MyBlog/backend/blog.db ~/backup/blog_$(date +%Y%m%d).db

# 定时备份（每天凌晨 3 点）
crontab -e
# 添加：
0 3 * * * cp /home/azureuser/MyBlog/backend/blog.db /home/azureuser/backup/blog_$(date +\%Y\%m\%d).db
```

---

## 六、常用命令

```bash
# 查看日志
docker compose logs -f backend
docker compose logs -f frontend

# 重启
docker compose restart

# 停止
docker compose down

# 进入容器调试
docker exec -it myblog-backend bash
docker exec -it myblog-frontend sh
```
