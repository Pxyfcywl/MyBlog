#!/bin/bash
# 博客部署脚本
# 用法：在服务器上 cd ~/MyBlog && bash deploy.sh

set -e

echo "=============================="
echo "  MyBlog 部署脚本"
echo "=============================="

# 检查 Docker
if ! command -v docker &> /dev/null; then
    echo "[!] Docker 未安装，正在安装..."
    curl -fsSL https://get.docker.com | sudo sh
    sudo usermod -aG docker $USER
    echo "[+] Docker 安装完成，请重新登录后再次运行此脚本"
    exit 0
fi

# 检查 .env
if [ ! -f backend/.env ]; then
    echo "[!] backend/.env 不存在，请先创建："
    echo ""
    echo "cat > backend/.env << 'EOF'"
    echo "ADMIN_SECRET_KEY=你的密钥"
    echo "DATABASE_URL=sqlite+aiosqlite:///./blog.db"
    echo "UPLOAD_DIR=./uploads"
    echo "FRONTEND_URL=http://你的服务器IP"
    echo "MINERU_API_KEY=你的key"
    echo "LLM_BASE_URL=https://open.bigmodel.cn/api/paas/v4"
    echo "LLM_API_KEY=你的key"
    echo "LLM_MODEL_NAME=glm-4-flash"
    echo "EOF"
    echo ""
    exit 1
fi

# 拉取最新代码
echo "[1/3] 拉取最新代码..."
git pull

# 构建并启动
echo "[2/3] 构建并启动容器..."
docker compose up -d --build

# 验证
echo "[3/3] 验证服务..."
sleep 3
if docker compose ps | grep -q "Up"; then
    echo ""
    echo "=============================="
    echo "  部署成功！"
    echo "  访问: http://$(hostname -I | awk '{print $1}')"
    echo "=============================="
else
    echo "[!] 容器未正常启动，请查看日志："
    echo "    docker compose logs"
fi
