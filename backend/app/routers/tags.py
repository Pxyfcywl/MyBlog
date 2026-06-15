"""标签与分类 API"""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, delete

from app.database import get_db
from app.models.article import Tag, Category, article_tags, article_categories
from app.schemas.article import TagOut, CategoryOut

router = APIRouter(prefix="/api", tags=["tags-categories"])


async def _cleanup_empty_tags(db: AsyncSession):
    """删除没有文章关联的标签"""
    # 找出有关联文章的标签 ID
    result = await db.execute(
        select(Tag.id)
        .outerjoin(article_tags, Tag.id == article_tags.c.tag_id)
        .group_by(Tag.id)
        .having(func.count(article_tags.c.article_id) == 0)
    )
    empty_ids = [row[0] for row in result.all()]
    if empty_ids:
        await db.execute(delete(Tag).where(Tag.id.in_(empty_ids)))
        await db.commit()


async def _cleanup_empty_categories(db: AsyncSession):
    """删除没有文章关联的分类"""
    result = await db.execute(
        select(Category.id)
        .outerjoin(article_categories, Category.id == article_categories.c.category_id)
        .group_by(Category.id)
        .having(func.count(article_categories.c.article_id) == 0)
    )
    empty_ids = [row[0] for row in result.all()]
    if empty_ids:
        await db.execute(delete(Category).where(Category.id.in_(empty_ids)))
        await db.commit()


@router.get("/tags", response_model=list[TagOut])
async def list_tags(db: AsyncSession = Depends(get_db)):
    """标签列表（含文章数量，按文章数降序，自动清理空标签）"""
    await _cleanup_empty_tags(db)

    query = (
        select(Tag, func.count(article_tags.c.article_id).label("article_count"))
        .join(article_tags, Tag.id == article_tags.c.tag_id)
        .group_by(Tag.id)
        .order_by(func.count(article_tags.c.article_id).desc())
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        TagOut(id=tag.id, name=tag.name, slug=tag.slug, article_count=count)
        for tag, count in rows
    ]


@router.get("/categories", response_model=list[CategoryOut])
async def list_categories(db: AsyncSession = Depends(get_db)):
    """分类列表（含文章数量，按文章数降序，自动清理空分类）"""
    await _cleanup_empty_categories(db)

    query = (
        select(Category, func.count(article_categories.c.article_id).label("article_count"))
        .join(article_categories, Category.id == article_categories.c.category_id)
        .group_by(Category.id)
        .order_by(func.count(article_categories.c.article_id).desc())
    )
    result = await db.execute(query)
    rows = result.all()

    return [
        CategoryOut(id=cat.id, name=cat.name, slug=cat.slug, article_count=count)
        for cat, count in rows
    ]
