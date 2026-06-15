"""文章相关 API"""
import re
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, or_
from sqlalchemy.orm import selectinload

from app.database import get_db
from app.auth import verify_admin
from app.models.article import Article, Tag, Category, article_tags, article_categories
from app.schemas.article import (
    ArticleCreate, ArticleUpdate,
    ArticleBrief, ArticleDetail, ArticleListResponse,
)


def extract_first_image(content: str) -> str:
    """从 Markdown 内容中提取第一张图片的 URL"""
    match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', content)
    return match.group(1) if match else ''

router = APIRouter(prefix="/api/articles", tags=["articles"])


@router.get("", response_model=ArticleListResponse)
async def list_articles(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    tag: str = Query(None, description="按标签筛选"),
    category: str = Query(None, description="按分类筛选"),
    db: AsyncSession = Depends(get_db),
):
    """文章列表 - 分页，置顶优先，支持按标签/分类筛选"""
    query = select(Article).options(
        selectinload(Article.tags),
        selectinload(Article.categories),
    ).where(Article.is_published == True)

    if tag:
        query = query.where(Article.tags.any(Tag.slug == tag))
    if category:
        query = query.where(Article.categories.any(Category.slug == category))

    # 统计总数
    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    # 排序：置顶优先，然后按创建时间倒序
    query = query.order_by(Article.is_pinned.desc(), Article.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    articles = result.scalars().all()

    return ArticleListResponse(
        items=[ArticleBrief.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/search", response_model=ArticleListResponse)
async def search_articles(
    q: str = Query(..., min_length=1, description="搜索关键词"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
):
    """全文模糊搜索"""
    keyword = f"%{q}%"
    query = select(Article).options(
        selectinload(Article.tags),
        selectinload(Article.categories),
    ).where(
        Article.is_published == True,
        or_(
            Article.title.ilike(keyword),
            Article.content.ilike(keyword),
            Article.summary.ilike(keyword),
        )
    )

    count_query = select(func.count()).select_from(query.subquery())
    total = (await db.execute(count_query)).scalar()

    query = query.order_by(Article.is_pinned.desc(), Article.created_at.desc())
    query = query.offset((page - 1) * page_size).limit(page_size)

    result = await db.execute(query)
    articles = result.scalars().all()

    return ArticleListResponse(
        items=[ArticleBrief.model_validate(a) for a in articles],
        total=total,
        page=page,
        page_size=page_size,
    )


@router.get("/{slug}", response_model=ArticleDetail)
async def get_article(slug: str, db: AsyncSession = Depends(get_db)):
    """根据 slug 获取文章详情"""
    query = select(Article).options(
        selectinload(Article.tags),
        selectinload(Article.categories),
    ).where(Article.slug == slug, Article.is_published == True)

    result = await db.execute(query)
    article = result.scalar_one_or_none()

    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    return ArticleDetail.model_validate(article)


@router.post("", response_model=ArticleDetail, dependencies=[Depends(verify_admin)])
async def create_article(data: ArticleCreate, db: AsyncSession = Depends(get_db)):
    """创建文章（需要管理员密钥）"""
    # 检查 slug 是否已存在
    existing = await db.execute(select(Article).where(Article.slug == data.slug))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail=f"slug '{data.slug}' 已存在")

    # 如果没有提供封面图，自动从内容中提取第一张图片
    cover_image = data.cover_image or extract_first_image(data.content)

    article = Article(
        title=data.title,
        slug=data.slug,
        content=data.content,
        summary=data.summary,
        cover_image=cover_image,
        is_pinned=data.is_pinned,
        is_published=data.is_published,
    )

    # 处理标签
    for name in data.tag_names:
        tag = await _get_or_create_tag(db, name)
        article.tags.append(tag)

    # 处理分类
    for name in data.category_names:
        cat = await _get_or_create_category(db, name)
        article.categories.append(cat)

    db.add(article)
    await db.commit()

    # 重新查询以加载关联的 tags 和 categories
    result = await db.execute(
        select(Article).options(
            selectinload(Article.tags),
            selectinload(Article.categories),
        ).where(Article.id == article.id)
    )
    article = result.scalar_one()

    return ArticleDetail.model_validate(article)


@router.put("/{article_id}", response_model=ArticleDetail, dependencies=[Depends(verify_admin)])
async def update_article(
    article_id: int,
    data: ArticleUpdate,
    db: AsyncSession = Depends(get_db),
):
    """更新文章（需要管理员密钥）"""
    result = await db.execute(
        select(Article).options(
            selectinload(Article.tags),
            selectinload(Article.categories),
        ).where(Article.id == article_id)
    )
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    update_data = data.model_dump(exclude_unset=True)
    tag_names = update_data.pop("tag_names", None)
    category_names = update_data.pop("category_names", None)

    # 如果更新了内容但没有提供封面图，自动从内容中提取
    if "content" in update_data and "cover_image" not in update_data:
        update_data["cover_image"] = extract_first_image(update_data["content"])

    for field, value in update_data.items():
        setattr(article, field, value)

    if tag_names is not None:
        article.tags.clear()
        for name in tag_names:
            tag = await _get_or_create_tag(db, name)
            article.tags.append(tag)

    if category_names is not None:
        article.categories.clear()
        for name in category_names:
            cat = await _get_or_create_category(db, name)
            article.categories.append(cat)

    await db.commit()

    # 重新查询以加载关联的 tags 和 categories
    result = await db.execute(
        select(Article).options(
            selectinload(Article.tags),
            selectinload(Article.categories),
        ).where(Article.id == article.id)
    )
    article = result.scalar_one()

    await _cleanup_empty(db)

    return ArticleDetail.model_validate(article)


@router.delete("/{article_id}", dependencies=[Depends(verify_admin)])
async def delete_article(article_id: int, db: AsyncSession = Depends(get_db)):
    """删除文章（需要管理员密钥）"""
    result = await db.execute(select(Article).where(Article.id == article_id))
    article = result.scalar_one_or_none()
    if not article:
        raise HTTPException(status_code=404, detail="文章不存在")

    await db.delete(article)
    await db.commit()
    await _cleanup_empty(db)
    return {"detail": "删除成功"}


# ---- 内部工具函数 ----

async def _cleanup_empty(db: AsyncSession):
    """删除没有文章关联的标签和分类"""
    # 删除空标签
    await db.execute(
        Tag.__table__.delete().where(
            Tag.id.not_in(select(article_tags.c.tag_id).distinct())
        )
    )
    # 删除空分类
    await db.execute(
        Category.__table__.delete().where(
            Category.id.not_in(select(article_categories.c.category_id).distinct())
        )
    )
    await db.commit()


async def _get_or_create_tag(db: AsyncSession, name: str) -> Tag:
    slug = name.lower().replace(" ", "-")
    result = await db.execute(select(Tag).where(Tag.slug == slug))
    tag = result.scalar_one_or_none()
    if not tag:
        tag = Tag(name=name, slug=slug)
        db.add(tag)
        await db.flush()
    return tag


async def _get_or_create_category(db: AsyncSession, name: str) -> Category:
    slug = name.lower().replace(" ", "-")
    result = await db.execute(select(Category).where(Category.slug == slug))
    cat = result.scalar_one_or_none()
    if not cat:
        cat = Category(name=name, slug=slug)
        db.add(cat)
        await db.flush()
    return cat
