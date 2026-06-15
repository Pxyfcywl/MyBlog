"""Pydantic 数据校验 Schema"""
from pydantic import BaseModel
from datetime import datetime
from typing import Optional


# ---- 标签 ----
class TagCreate(BaseModel):
    name: str
    slug: str


class TagOut(TagCreate):
    id: int
    article_count: int = 0

    class Config:
        from_attributes = True


# ---- 分类 ----
class CategoryCreate(BaseModel):
    name: str
    slug: str


class CategoryOut(CategoryCreate):
    id: int
    article_count: int = 0

    class Config:
        from_attributes = True


# ---- 文章 ----
class ArticleCreate(BaseModel):
    title: str
    slug: str
    content: str
    summary: str = ""
    cover_image: str = ""
    is_pinned: bool = False
    is_published: bool = True
    tag_names: list[str] = []
    category_names: list[str] = []


class ArticleUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    content: Optional[str] = None
    summary: Optional[str] = None
    cover_image: Optional[str] = None
    is_pinned: Optional[bool] = None
    is_published: Optional[bool] = None
    tag_names: Optional[list[str]] = None
    category_names: Optional[list[str]] = None


class ArticleBrief(BaseModel):
    """文章列表中的简要信息"""
    id: int
    title: str
    slug: str
    summary: str
    cover_image: str
    is_pinned: bool
    created_at: datetime
    tags: list[TagOut] = []
    categories: list[CategoryOut] = []

    class Config:
        from_attributes = True


class ArticleDetail(ArticleBrief):
    """文章详情，包含完整 Markdown 内容"""
    content: str
    updated_at: Optional[datetime] = None


class ArticleListResponse(BaseModel):
    """分页文章列表响应"""
    items: list[ArticleBrief]
    total: int
    page: int
    page_size: int
