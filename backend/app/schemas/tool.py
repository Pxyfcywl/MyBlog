"""工具箱相关 Pydantic 模型"""
from pydantic import BaseModel


# ── OCR / 文档解析 ──────────────────────────────────────

class ExtractedFileOut(BaseModel):
    """单个文件的解析结果"""
    file_name: str
    state: str           # done / running / pending / failed / converting
    full_zip_url: str = ""
    markdown_url: str = ""
    err_msg: str = ""


class ExtractProgressOut(BaseModel):
    """提取进度信息"""
    total: int
    done: int
    failed: int
    running: int


class BatchSubmitOut(BaseModel):
    """提交批量解析任务的响应"""
    batch_id: str
    file_count: int


class BatchStatusOut(BaseModel):
    """批量任务状态查询响应"""
    batch_id: str
    state: str                               # done / running
    files: list[ExtractedFileOut]
    progress: ExtractProgressOut


# ── 审查 ──────────────────────────────────────────────

class ReviewRequest(BaseModel):
    """审查请求"""
    batch_id: str
    keywords: list[str] = []
    date_start: str | None = None            # YYYY-MM-DD
    date_end: str | None = None              # YYYY-MM-DD


class KeywordMatchOut(BaseModel):
    """关键词匹配结果"""
    keyword: str
    line_number: int
    context: str


class DateFindingOut(BaseModel):
    """日期校验结果"""
    date_str: str
    parsed: str
    line_number: int
    context: str
    in_range: bool


class FileReviewOut(BaseModel):
    """单个文件的审查结果"""
    file_name: str
    keyword_matches: list[KeywordMatchOut]
    date_findings: list[DateFindingOut]
    error: str = ""


class ReviewOut(BaseModel):
    """审查结果总览"""
    batch_id: str
    state: str
    files_total: int
    files_done: int
    files_failed: int
    results: list[FileReviewOut]


# ── LLM 智能审查 ──────────────────────────────────────

class LLMReviewRequest(BaseModel):
    """LLM 智能审查请求

    base_url / api_key / model 均可选，不填则使用服务端默认配置。
    """
    batch_id: str
    review_prompt: str                           # 用户的审查要求（自由文本）
    base_url: str | None = None                  # LLM 服务地址
    api_key: str | None = None                   # LLM API Key
    model: str | None = None                     # 模型名称


class LLMReviewOut(BaseModel):
    """LLM 智能审查结果"""
    batch_id: str
    files_count: int                             # 参与审查的文件数
    review_result: str                           # LLM 返回的审查文本（Markdown）


# ── 健康检查 ──────────────────────────────────────────

class HealthCheckOut(BaseModel):
    """模型健康检查结果"""
    ok: bool
    service: str                                 # "LLM" / "Embedding"
    detail: str


class HealthCheckRequest(BaseModel):
    """健康检查请求（支持自定义配置）"""
    base_url: str | None = None
    api_key: str | None = None
    model: str | None = None
