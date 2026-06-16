# 问题排查指南

> 记录开发和部署中遇到的问题及解决方案，方便日后快速定位。

---

## 1. 服务器部署后 Hero 背景图 404

**现象：** 本地开发正常，部署到服务器后 Hero 页面背景图加载不出来。

**原因：** Vite 中 `public/` 目录的文件构建后从根路径 `/` 提供服务。使用相对路径 `../public/background.jpg` 在开发模式下可以工作，但构建后路径失效。

**解决：** 使用绝对路径 `/background.jpg`，不要用 `../public/background.jpg`。

```js
// ❌ 错误
const bgImage = '../public/background.jpg'

// ✅ 正确
const bgImage = '/background.jpg'
```

---

## 2. nginx 上传图片报 413 Request Entity Too Large

**现象：** 服务器上传封面图或文章内图片时返回 413 错误。

**原因：** nginx 默认 `client_max_body_size` 为 1MB，超过此大小的请求会被拒绝。

**解决：** 在 `frontend/nginx.conf` 的 `server` 块中添加：

```nginx
client_max_body_size 200m;
```

同时建议给 API 代理加超时配置，避免大文件上传超时：

```nginx
location /api/ {
    proxy_pass http://backend:8000;
    proxy_read_timeout 300s;
    proxy_send_timeout 300s;
}
```

---

## 3. iframe 嵌入 HTML 工具导致博客嵌套

**现象：** 在 Vue 页面中用 `<iframe src="xxx.html">` 嵌入独立 HTML 工具，点击工具内的"返回"按钮后，博客页面在 iframe 内再次加载，形成嵌套。

**原因：** 被嵌入的 HTML 文件中有指向 `index.html` 的链接，在 iframe 内点击会在 iframe 内部导航，而不是跳出 iframe。

**解决：** 在嵌入的 HTML 文件中移除或禁用返回按钮。人工审核模式通过 Vue 工具栏的"← 返回"按钮退出，不需要 HTML 内部的导航。

---

## 4. Google Fonts 中文字体在国内加载慢

**现象：** 使用 Google Fonts CDN 引入中文字体（如 Ma Shan Zheng），在国内服务器上加载缓慢或超时。

**原因：** Google Fonts 在国内访问不稳定，且中文字体被拆成多个 unicode-range 子集（100+ 个请求），加载链路长。

**解决：** 将字体文件下载到本地 `frontend/public/fonts/` 目录，通过 `@font-face` 本地引用：

```css
@font-face {
  font-family: 'Ma Shan Zheng';
  src: url('/fonts/MaShanZheng-Regular.ttf') format('truetype');
  font-weight: 400;
  font-display: swap;
}
```

字体下载：浏览器访问 [Google Fonts](https://fonts.google.com/specimen/Ma+Shan+Zheng)，点击 "Download family"。

---

## 5. scp 数据同步

**现象：** `git pull` 更新代码后，服务器上的文章和图片没有同步到本地。

**原因：** `blog.db` 和 `uploads/` 在 `.gitignore` 中，不随代码同步。

**解决：** 使用 `scp` 单独同步：

```bash
# 服务器 → 本地
scp -i key.pem -r user@ip:~/MyBlog/backend/blog.db ./backend/
scp -i key.pem -r user@ip:~/MyBlog/backend/uploads ./backend/

# 本地 → 服务器
scp -i key.pem ./backend/blog.db user@ip:~/MyBlog/backend/
scp -i key.pem -r ./backend/uploads user@ip:~/MyBlog/backend/
```

覆盖服务器数据库后需重启后端：

```bash
ssh -i key.pem user@ip "cd ~/MyBlog && docker compose restart backend"
```

---

## 6. 图片路径与数据库的对应关系

**疑问：** 本地和服务器分别上传过图片，文件名会不会冲突？下载回来后图片和文章能对上吗？

**机制：** 图片上传时服务端用 UUID 重命名（`upload.py` 中 `uuid.uuid4().hex + ext`），返回 `/uploads/uuid.jpg` 路径存入文章 Markdown。与原始文件名无关。

**结论：** 只要 `blog.db` 和 `uploads/` 一起下载，路径一定对上。不需要担心文件名冲突。

---

## 7. Docker 构建 OOM（内存不足）

**现象：** 服务器上 `docker compose up --build` 卡住或失败。

**原因：** Azure VM 仅 894MB RAM，Docker 构建时内存不足。

**解决：**
1. 创建 swap：`sudo fallocate -l 1G /swapfile && sudo mkswap /swapfile && sudo swapon /swapfile`
2. 构建脚本已移除 `vue-tsc`（占内存大），改为直接 `vite build`

验证 swap 是否存在：`swapon --show`

---

## 8. Nginx 静态资源规则拦截上传文件

**现象：** 文章中的图片返回 404，但文件确实存在于 `uploads/` 目录。

**原因：** nginx 的正则规则 `~* \.(jpg|png|css|js)...` 优先级高于普通 prefix `/uploads/`，导致图片请求被当作静态文件处理而非代理到后端。

**解决：** 使用 `^~` 前缀强制优先匹配：

```nginx
location ^~ /uploads/ { proxy_pass http://backend:8000; }
location ^~ /music/   { proxy_pass http://backend:8000; }
```

---
