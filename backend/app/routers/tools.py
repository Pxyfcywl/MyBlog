"""工具箱 API 路由

提供文档解析（OCR）、规则审查、LLM 智能审查、模型健康检查。

接口设计：
- POST /api/tools/ocr              上传文件，提交批量解析任务
- GET  /api/tools/ocr/{batch_id}   查询解析任务状态和结果
- POST /api/tools/review           规则审查（关键词 + 日期）
- POST /api/tools/llm-review       LLM 智能审查
- GET  /api/tools/health/llm       测试 LLM 连通性
- GET  /api/tools/health/embedding 测试 Embedding 连通性
"""
import os
import shutil
import tempfile

from fastapi import APIRouter, File, UploadFile, HTTPException

from app.services.mineru import MinerUClient
from app.services.reviewer import match_keywords, validate_dates
from app.services.llm import LLMClient
from app.schemas.tool import (
    BatchSubmitOut,
    BatchStatusOut,
    ExtractedFileOut,
    ExtractProgressOut,
    ReviewRequest,
    ReviewOut,
    FileReviewOut,
    KeywordMatchOut,
    DateFindingOut,
    LLMReviewRequest,
    LLMReviewOut,
    HealthCheckOut,
    HealthCheckRequest,
)

router = APIRouter(prefix="/api/tools", tags=["tools"])

# 允许的文件类型
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".ppt", ".pptx",
    ".xls", ".xlsx", ".png", ".jpg", ".jpeg",
    ".jp2", ".webp", ".gif", ".bmp",
}
MAX_FILE_SIZE = 200 * 1024 * 1024  # 200MB


def _validate_file(filename: str, size: int) -> str | None:
    """校验文件类型和大小，返回错误信息或 None。"""
    ext = os.path.splitext(filename)[1].lower()
    if ext not in ALLOWED_EXTENSIONS:
        return f"不支持的文件类型: {ext}"
    if size > MAX_FILE_SIZE:
        return f"文件过大: {size / 1024 / 1024:.1f}MB（上限 200MB）"
    return None


def _get_markdown_from_files(files: list) -> list[dict]:
    """从 MinerU 解析结果中提取 Markdown 内容。

    下载 zip 包并解压出 full.md 文件。
    """
    client = MinerUClient()
    documents = []

    for f in files:
        if f.state != "done" or not f.full_zip_url:
            continue
        try:
            md_dict = client.fetch_markdown_from_zip(f.full_zip_url)
            # 取 full.md（主文件），如果没有就取第一个 md
            content = md_dict.get("full.md") or next(iter(md_dict.values()), "")
            if content:
                documents.append({"file_name": f.file_name, "content": content})
        except Exception:
            continue

    return documents


# ── OCR 端点 ──────────────────────────────────────────

@router.post("/ocr", response_model=BatchSubmitOut)
async def submit_ocr(files: list[UploadFile] = File(...)):
    """上传文件并提交 MinerU 批量解析任务。

    返回 batch_id，前端用此 ID 轮询获取解析结果。
    """
    if not files:
        raise HTTPException(status_code=400, detail="请上传至少一个文件")

    # 校验文件
    for f in files:
        content = await f.read()
        err = _validate_file(f.filename, len(content))
        if err:
            raise HTTPException(status_code=400, detail=err)
        await f.seek(0)

    # 保存到临时目录
    temp_dir = tempfile.mkdtemp(prefix="mineru_")
    file_paths = []

    try:
        for f in files:
            content = await f.read()
            path = os.path.join(temp_dir, f.filename)
            with open(path, "wb") as fp:
                fp.write(content)
            file_paths.append(path)

        client = MinerUClient()
        batch_id = client.submit_batch(file_paths)

    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MinerU 提交失败: {str(e)}")
    finally:
        shutil.rmtree(temp_dir, ignore_errors=True)

    return BatchSubmitOut(batch_id=batch_id, file_count=len(files))


@router.get("/ocr/{batch_id}", response_model=BatchStatusOut)
async def get_ocr_status(batch_id: str):
    """查询 MinerU 批量解析任务状态。"""
    try:
        client = MinerUClient()
        state, files = client.poll_batch(batch_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MinerU 查询失败: {str(e)}")

    files_out = []
    counts = {"done": 0, "failed": 0, "running": 0}

    for f in files:
        files_out.append(ExtractedFileOut(
            file_name=f.file_name,
            state=f.state,
            full_zip_url=f.full_zip_url,
            markdown_url=f.markdown_url,
            err_msg=f.err_msg,
        ))
        if f.state == "done":
            counts["done"] += 1
        elif f.state == "failed":
            counts["failed"] += 1
        else:
            counts["running"] += 1

    return BatchStatusOut(
        batch_id=batch_id,
        state=state,
        files=files_out,
        progress=ExtractProgressOut(
            total=len(files),
            done=counts["done"],
            failed=counts["failed"],
            running=counts["running"],
        ),
    )


# ── 规则审查 ──────────────────────────────────────────

@router.post("/review", response_model=ReviewOut)
async def review_files(req: ReviewRequest):
    """对已解析的文件执行审查（关键词匹配 + 日期校验）。"""
    try:
        client = MinerUClient()
        state, files = client.poll_batch(req.batch_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MinerU 查询失败: {str(e)}")

    if state != "done":
        raise HTTPException(
            status_code=409,
            detail=f"解析尚未完成（当前状态: {state}），请稍后再试",
        )

    # 从 zip 中提取 Markdown
    documents = _get_markdown_from_files(files)

    results = []
    done_count = 0
    fail_count = 0

    for f in files:
        if f.state == "failed":
            fail_count += 1
            results.append(FileReviewOut(
                file_name=f.file_name,
                keyword_matches=[],
                date_findings=[],
                error=f.err_msg or "解析失败",
            ))
            continue

        if f.state != "done":
            continue

        done_count += 1

        # 从已提取的 documents 中找对应内容
        content = ""
        for doc in documents:
            if doc["file_name"] == f.file_name:
                content = doc["content"]
                break

        if not content:
            results.append(FileReviewOut(
                file_name=f.file_name,
                keyword_matches=[],
                date_findings=[],
                error="无法提取 Markdown 内容",
            ))
            continue

        kw_matches = match_keywords(content, req.keywords)
        date_findings = validate_dates(content, req.date_start, req.date_end)

        results.append(FileReviewOut(
            file_name=f.file_name,
            keyword_matches=[
                KeywordMatchOut(
                    keyword=m.keyword,
                    line_number=m.line_number,
                    context=m.context,
                )
                for m in kw_matches
            ],
            date_findings=[
                DateFindingOut(
                    date_str=d.date_str,
                    parsed=d.parsed,
                    line_number=d.line_number,
                    context=d.context,
                    in_range=d.in_range,
                )
                for d in date_findings
            ],
        ))

    return ReviewOut(
        batch_id=req.batch_id,
        state="done",
        files_total=len(files),
        files_done=done_count,
        files_failed=fail_count,
        results=results,
    )


# ── LLM 智能审查 ──────────────────────────────────────

@router.post("/llm-review", response_model=LLMReviewOut)
async def llm_review_files(req: LLMReviewRequest):
    """用 LLM 对已解析的文件执行智能审查。

    用户提供自由文本的审查要求，LLM 阅读文档后给出结构化审查结果。
    支持配置 base_url / api_key / model 使用不同的 LLM 服务。
    """
    try:
        client = MinerUClient()
        state, files = client.poll_batch(req.batch_id)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"MinerU 查询失败: {str(e)}")

    if state != "done":
        raise HTTPException(
            status_code=409,
            detail=f"解析尚未完成（当前状态: {state}），请稍后再试",
        )

    # 从 zip 中提取 Markdown
    documents = _get_markdown_from_files(files)

    if not documents:
        raise HTTPException(status_code=404, detail="没有可用的解析结果")

    # 调用 LLM 审查
    try:
        llm = LLMClient(
            base_url=req.base_url,
            api_key=req.api_key,
            model=req.model,
        )
        result = llm.review_documents(documents, req.review_prompt)
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"LLM 审查失败: {str(e)}")

    return LLMReviewOut(
        batch_id=req.batch_id,
        files_count=len(documents),
        review_result=result,
    )


# ── 健康检查 ──────────────────────────────────────────

@router.post("/health/llm", response_model=HealthCheckOut)
async def health_check_llm(req: HealthCheckRequest):
    """测试 LLM 服务是否可用。

    支持传入自定义 base_url / api_key / model，不传则使用服务端默认配置。
    """
    try:
        llm = LLMClient(
            base_url=req.base_url,
            api_key=req.api_key,
            model=req.model,
        )
        reply = llm.chat(
            [{"role": "user", "content": "回复OK两个字"}],
            max_tokens=10,
        )
        return HealthCheckOut(
            ok=True,
            service="LLM",
            detail=f"模型: {llm.model}, 回复: {reply.strip()[:50]}",
        )
    except Exception as e:
        return HealthCheckOut(ok=False, service="LLM", detail=str(e))
