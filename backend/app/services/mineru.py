"""MinerU 文档解析 API 客户端

支持两种模式：
- 精准解析 API（需要 Token，支持大文件 200MB/200页，批量）
- Agent 轻量解析 API（免 Token，IP 限频，10MB/20页）

当前默认使用精准解析的批量上传接口。
"""
import io
import os
import time
import zipfile
from dataclasses import dataclass, field

import httpx

from app.config import settings

MINERU_API_BASE = "https://mineru.net/api/v4"
MINERU_AGENT_BASE = "https://mineru.net/api/v1/agent"

REQUEST_TIMEOUT = 30  # 提交任务超时
POLL_TIMEOUT = 300    # 轮询结果超时（秒）
POLL_INTERVAL = 3     # 轮询间隔（秒）


@dataclass
class ExtractedFile:
    """单个文件的解析结果"""
    file_name: str
    state: str  # done / running / pending / failed / waiting-file / converting
    full_zip_url: str = ""
    markdown_url: str = ""
    err_msg: str = ""
    extract_progress: dict = field(default_factory=dict)


class MinerUClient:
    """MinerU API 客户端"""

    def __init__(self, token: str = "", use_agent: bool = False):
        self.token = token or settings.mineru_api_key
        self.use_agent = use_agent

    # ── 精准解析：批量上传 ──────────────────────────────────

    def submit_batch(self, file_paths: list[str]) -> str:
        """批量上传本地文件，返回 batch_id。

        流程：
        1. POST /file-urls/batch → 拿到 upload URLs + batch_id
        2. PUT 每个文件到对应的 upload URL
        """
        files_payload = []
        for path in file_paths:
            name = os.path.basename(path)
            files_payload.append({"name": name})

        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            # Step 1: 申请上传链接
            resp = client.post(
                f"{MINERU_API_BASE}/file-urls/batch",
                headers=self._headers(),
                json={
                    "files": files_payload,
                    "model_version": "vlm",
                    "is_ocr": True,
                    "enable_formula": True,
                    "enable_table": True,
                },
            )
            resp.raise_for_status()
            result = resp.json()

            if result.get("code") != 0:
                raise RuntimeError(f"MinerU 申请上传链接失败: {result.get('msg')}")

            batch_id = result["data"]["batch_id"]
            upload_urls = result["data"]["file_urls"]

            # Step 2: 上传文件
            for path, upload_url in zip(file_paths, upload_urls):
                with open(path, "rb") as f:
                    upload_resp = client.put(upload_url, content=f.read())
                    if upload_resp.status_code != 200:
                        raise RuntimeError(
                            f"文件上传失败 ({os.path.basename(path)}): "
                            f"HTTP {upload_resp.status_code}"
                        )

        return batch_id

    def poll_batch(self, batch_id: str) -> tuple[str, list[ExtractedFile]]:
        """轮询批量任务结果，返回 (state, files)。

        state: "done" / "running" / "pending" / "converting"
        只有当所有文件都 done 或 failed 时才返回 state="done"。
        """
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            resp = client.get(
                f"{MINERU_API_BASE}/extract-results/batch/{batch_id}",
                headers=self._headers(),
            )
            resp.raise_for_status()
            result = resp.json()

        if result.get("code") != 0:
            raise RuntimeError(f"MinerU 查询失败: {result.get('msg')}")

        data = result.get("data", {})
        extract_results = data.get("extract_result", [])

        files = []
        all_done = True
        any_failed = False

        for item in extract_results:
            ef = ExtractedFile(
                file_name=item.get("file_name", ""),
                state=item.get("state", "unknown"),
                full_zip_url=item.get("full_zip_url", ""),
                err_msg=item.get("err_msg", ""),
                extract_progress=item.get("extract_progress", {}),
            )
            files.append(ef)
            if ef.state not in ("done", "failed"):
                all_done = False
            if ef.state == "failed":
                any_failed = True

        if all_done:
            return ("done", files)
        return ("running", files)

    def extract_batch_sync(
        self, file_paths: list[str], timeout: int = POLL_TIMEOUT
    ) -> list[ExtractedFile]:
        """提交批量任务并阻塞等待结果，返回解析结果列表。"""
        batch_id = self.submit_batch(file_paths)
        start = time.time()

        while time.time() - start < timeout:
            state, files = self.poll_batch(batch_id)
            if state == "done":
                return files
            time.sleep(POLL_INTERVAL)

        raise TimeoutError(f"MinerU 解析超时 ({timeout}s)，batch_id: {batch_id}")

    # ── 结果下载 ──────────────────────────────────────────

    @staticmethod
    def fetch_markdown_from_zip(zip_url: str) -> dict[str, str]:
        """下载 MinerU 的 zip 结果包，解压出所有 Markdown 文件。

        Returns:
            {文件名: Markdown内容} 的字典。
            通常包含一个 "full.md"，也可能有其他 md 文件。
        """
        with httpx.Client(timeout=120) as client:
            resp = client.get(zip_url)
            resp.raise_for_status()

        md_files = {}
        with zipfile.ZipFile(io.BytesIO(resp.content)) as zf:
            for name in zf.namelist():
                # 匹配所有 .md 文件（full.md 或带前缀的 xxx_full.md）
                if name.endswith(".md"):
                    # 去掉目录前缀，只保留文件名
                    basename = os.path.basename(name)
                    if basename:
                        md_files[basename] = zf.read(name).decode("utf-8")

        if not md_files:
            raise RuntimeError(f"zip 包中未找到 .md 文件，zip 内容: {zf.namelist()}")

        return md_files

    @staticmethod
    def fetch_markdown_direct(url: str) -> str:
        """直接从 URL 下载 Markdown 文本（用于 Agent 模式返回的 CDN 链接）。"""
        with httpx.Client(timeout=60) as client:
            resp = client.get(url)
            resp.raise_for_status()
            return resp.text

    # ── Agent 轻量解析（备用） ─────────────────────────────

    def submit_agent_file(self, file_path: str) -> tuple[str, str]:
        """Agent 模式：获取签名上传 URL，返回 (task_id, file_url)。"""
        file_name = os.path.basename(file_path)
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            resp = client.post(
                f"{MINERU_AGENT_BASE}/parse/file",
                json={"file_name": file_name, "is_ocr": True},
            )
            resp.raise_for_status()
            result = resp.json()

        if result.get("code") != 0:
            raise RuntimeError(f"Agent API 失败: {result.get('msg')}")

        return result["data"]["task_id"], result["data"]["file_url"]

    def poll_agent_task(self, task_id: str) -> ExtractedFile:
        """Agent 模式：查询任务状态。"""
        with httpx.Client(timeout=REQUEST_TIMEOUT) as client:
            resp = client.get(f"{MINERU_AGENT_BASE}/parse/{task_id}")
            resp.raise_for_status()
            result = resp.json()

        if result.get("code") != 0:
            raise RuntimeError(f"Agent 查询失败: {result.get('msg')}")

        data = result.get("data", {})
        return ExtractedFile(
            file_name="",
            state=data.get("state", "unknown"),
            markdown_url=data.get("markdown_url", ""),
            err_msg=data.get("err_msg", ""),
        )

    # ── 内部方法 ──────────────────────────────────────────

    def _headers(self) -> dict:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.token}",
        }
