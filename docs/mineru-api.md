# MinerU API 调用参考

> 本文档记录项目中 MinerU API 的实际用法，基于精准解析 API 的**批量上传接口**。

## 基本信息

| 项目 | 值 |
|------|-----|
| Base URL | `https://mineru.net/api/v4` |
| 认证方式 | `Authorization: Bearer {token}` |
| Token 来源 | MinerU 后台 → API 管理 → 创建 Token |
| 模型版本 | `vlm`（推荐）/ `pipeline`（默认）/ `MinerU-HTML` |
| 文件限制 | 200MB / 200页 |
| 每日额度 | 1000 页高优先级，超出降速 |

## 项目中的调用流程

```
Step 1: POST /file-urls/batch    → 申请上传链接，拿到 batch_id
Step 2: PUT 文件到上传链接        → 上传文件内容
Step 3: GET /extract-results/batch/{batch_id} → 轮询结果
Step 4: 下载 zip → 解压取 full.md → 得到 Markdown 内容
```

---

## Step 1: 申请上传链接

```
POST https://mineru.net/api/v4/file-urls/batch
```

### 请求头

```
Content-Type: application/json
Authorization: Bearer {token}
```

### 请求体

```json
{
  "files": [
    {"name": "文件1.pdf"},
    {"name": "文件2.pdf"}
  ],
  "model_version": "vlm",
  "is_ocr": true,
  "enable_formula": true,
  "enable_table": true
}
```

| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `files` | array | 是 | 文件名列表，每个元素含 `name` 字段 |
| `model_version` | string | 否 | `vlm`（推荐）/ `pipeline` / `MinerU-HTML` |
| `is_ocr` | bool | 否 | 是否启用 OCR，默认 `false` |
| `enable_formula` | bool | 否 | 公式识别，默认 `true` |
| `enable_table` | bool | 否 | 表格识别，默认 `true` |
| `language` | string | 否 | 文档语言，默认 `ch`（中英文） |

### 响应

```json
{
  "code": 0,
  "data": {
    "batch_id": "2bb2f0ec-a336-4a0a-b61a-****",
    "file_urls": [
      "https://mineru.oss-cn-shanghai.aliyuncs.com/api-upload/****"
    ]
  },
  "msg": "ok"
}
```

- `batch_id`：后续轮询用
- `file_urls`：与 `files` 一一对应的上传地址

---

## Step 2: 上传文件

```
PUT {file_url}
```

直接把文件二进制内容 PUT 到 Step 1 返回的 `file_urls` 地址。

**注意**：
- 不需要 `Authorization` 头
- 不需要设置 `Content-Type`
- 上传链接有效期 **24 小时**
- 上传完成后系统**自动提交**解析任务，无需额外调用

```python
with open("文件.pdf", "rb") as f:
    requests.put(file_url, data=f.read())
```

---

## Step 3: 轮询结果

```
GET https://mineru.net/api/v4/extract-results/batch/{batch_id}
```

### 响应

```json
{
  "code": 0,
  "data": {
    "batch_id": "2bb2f0ec-****",
    "extract_result": [
      {
        "file_name": "文件1.pdf",
        "state": "done",
        "full_zip_url": "https://cdn-mineru.openxlab.org.cn/pdf/****/xxx.zip",
        "err_msg": ""
      },
      {
        "file_name": "文件2.pdf",
        "state": "running",
        "extract_progress": {
          "extracted_pages": 1,
          "total_pages": 5,
          "start_time": "2025-01-20 11:43:20"
        }
      }
    ]
  }
}
```

### state 状态值

| 状态 | 含义 |
|------|------|
| `waiting-file` | 等待文件上传 |
| `pending` | 排队中 |
| `running` | 解析中 |
| `converting` | 格式转换中 |
| `done` | 完成 |
| `failed` | 失败（看 `err_msg`） |

**轮询策略**：每 3 秒查一次，所有文件 `done` 或 `failed` 时结束。

---

## Step 4: 获取 Markdown

结果是一个 **zip 包**，需要下载后解压。

```python
import io, zipfile, httpx

# 下载 zip
resp = httpx.get(full_zip_url)
zip_file = zipfile.ZipFile(io.BytesIO(resp.content))

# 提取 full.md
markdown = zip_file.read("full.md").decode("utf-8")
```

zip 包内通常包含：
- `full.md` — 完整的 Markdown 文本（**我们需要的**）
- `*_content_list.json` — 内容列表
- `*_model.json` — 模型推理结果
- `*_middle.json` — 中间处理结果

---

## 错误码速查

| 错误码 | 含义 | 处理 |
|--------|------|------|
| `A0202` | Token 错误 | 检查 Token 格式：`Bearer {token}` |
| `A0211` | Token 过期 | 重新生成 Token |
| `-500` | 参数错误 | 检查 Content-Type 和参数类型 |
| `-60005` | 文件超 200MB | 压缩或拆分文件 |
| `-60006` | 超 200 页 | 拆分文件 |
| `-60018` | 每日额度用尽 | 等明天或降低优先级继续 |

---

## Agent 轻量解析 API（备用）

无需 Token，但限制更严格（10MB / 20页）。适合快速测试。

```
POST https://mineru.net/api/v1/agent/parse/file   → 获取签名上传 URL
GET  https://mineru.net/api/v1/agent/parse/{task_id} → 查询结果
```

结果直接返回 `markdown_url`（CDN 链接），无需解压 zip。

---

## 我们项目中的代码位置

| 文件 | 职责 |
|------|------|
| `backend/app/services/mineru.py` | MinerU 客户端（提交、轮询、下载） |
| `backend/app/routers/tools.py` | API 路由（`/api/tools/ocr`） |
| `backend/.env` | `MINERU_API_KEY` 配置 |
