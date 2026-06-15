"""文件审查服务

提供基于规则的审查能力：
1. 关键词匹配 — 用户输入关键词列表，在 Markdown 中查找
2. 日期范围校验 — 提取文档中的日期，检查是否在指定范围内

后续可扩展：语义矛盾检测（需接入 LLM）
"""
import re
from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class KeywordMatch:
    """单个关键词匹配结果"""
    keyword: str
    line_number: int
    context: str          # 匹配行的上下文（前后各截取一些）


@dataclass
class DateFinding:
    """日期校验结果"""
    date_str: str         # 原始日期字符串
    parsed: str           # 解析后的标准格式
    line_number: int
    context: str
    in_range: bool        # 是否在范围内


@dataclass
class FileReviewResult:
    """单个文件的审查结果"""
    file_name: str
    keyword_matches: list[KeywordMatch] = field(default_factory=list)
    date_findings: list[DateFinding] = field(default_factory=list)
    error: str = ""


# ── 日期解析 ──────────────────────────────────────────

# 支持的日期格式
DATE_PATTERNS = [
    # 2024-01-15 / 2024.01.15 / 2024/01/15
    (r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", "%Y-%m-%d"),
    # 2024年1月15日
    (r"(\d{4})年(\d{1,2})月(\d{1,2})日", "%Y年%m月%d日"),
    # 01/15/2024 (美式)
    (r"(\d{1,2})/(\d{1,2})/(\d{4})", "US_STYLE"),
    # 20240115 (紧凑格式)
    (r"\b(\d{4})(\d{2})(\d{2})\b", "COMPACT"),
]

# 用于从上下文中提取日期的组合正则
_DATE_REGEX = re.compile(
    r"\d{4}[-./]\d{1,2}[-./]\d{1,2}"
    r"|\d{4}年\d{1,2}月\d{1,2}日"
    r"|\d{1,2}/\d{1,2}/\d{4}"
    r"|\b\d{8}\b"
)


def _parse_date_str(date_str: str) -> datetime | None:
    """尝试解析各种格式的日期字符串，返回 datetime 或 None。"""
    # 标准格式 2024-01-15
    m = re.match(r"(\d{4})[-./](\d{1,2})[-./](\d{1,2})", date_str)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # 中文格式 2024年1月15日
    m = re.match(r"(\d{4})年(\d{1,2})月(\d{1,2})日", date_str)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    # 美式 01/15/2024
    m = re.match(r"(\d{1,2})/(\d{1,2})/(\d{4})", date_str)
    if m:
        try:
            return datetime(int(m.group(3)), int(m.group(1)), int(m.group(2)))
        except ValueError:
            pass

    # 紧凑 20240115
    m = re.match(r"(\d{4})(\d{2})(\d{2})$", date_str)
    if m:
        try:
            return datetime(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            pass

    return None


def _extract_context(lines: list[str], line_idx: int, window: int = 1) -> str:
    """提取某行的上下文（前后各 window 行）。"""
    start = max(0, line_idx - window)
    end = min(len(lines), line_idx + window + 1)
    return "\n".join(lines[start:end]).strip()


# ── 关键词匹配 ──────────────────────────────────────────

def match_keywords(
    content: str,
    keywords: list[str],
    context_window: int = 1,
) -> list[KeywordMatch]:
    """在 Markdown 内容中查找关键词。

    Args:
        content: Markdown 文本
        keywords: 要查找的关键词列表
        context_window: 上下文行数（前后各几行）

    Returns:
        匹配结果列表
    """
    if not keywords or not content:
        return []

    lines = content.split("\n")
    matches = []

    for line_idx, line in enumerate(lines):
        line_lower = line.lower()
        for kw in keywords:
            if kw.lower() in line_lower:
                ctx = _extract_context(lines, line_idx, context_window)
                matches.append(KeywordMatch(
                    keyword=kw,
                    line_number=line_idx + 1,
                    context=ctx,
                ))

    return matches


# ── 日期校验 ──────────────────────────────────────────

def validate_dates(
    content: str,
    date_start: str | None = None,
    date_end: str | None = None,
) -> list[DateFinding]:
    """提取文档中的日期并校验是否在指定范围内。

    Args:
        content: Markdown 文本
        date_start: 范围起始日期（格式 YYYY-MM-DD），None 表示不限
        date_end: 范围结束日期（格式 YYYY-MM-DD），None 表示不限

    Returns:
        日期校验结果列表
    """
    if not content:
        return []

    range_start = _parse_date_str(date_start) if date_start else None
    range_end = _parse_date_str(date_end) if date_end else None

    lines = content.split("\n")
    findings = []

    for line_idx, line in enumerate(lines):
        for m in _DATE_REGEX.finditer(line):
            date_str = m.group()
            parsed = _parse_date_str(date_str)
            if parsed is None:
                continue

            in_range = True
            if range_start and parsed < range_start:
                in_range = False
            if range_end and parsed > range_end:
                in_range = False

            ctx = _extract_context(lines, line_idx, window=0)
            findings.append(DateFinding(
                date_str=date_str,
                parsed=parsed.strftime("%Y-%m-%d"),
                line_number=line_idx + 1,
                context=ctx,
                in_range=in_range,
            ))

    return findings


# ── 便捷函数 ──────────────────────────────────────────

def review_content(
    content: str,
    keywords: list[str] | None = None,
    date_start: str | None = None,
    date_end: str | None = None,
) -> tuple[list[KeywordMatch], list[DateFinding]]:
    """一次性执行所有审查，返回 (关键词匹配, 日期校验)。"""
    kw_matches = match_keywords(content, keywords or [])
    date_findings = validate_dates(content, date_start, date_end)
    return kw_matches, date_findings
