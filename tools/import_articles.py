"""
文章导入工具
扫描指定目录的 .md 文件，解析 frontmatter，导入数据库
图片复制到后端 uploads 目录，更新引用路径
"""
import os
import re
import sys
import shutil
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

# Windows 终端编码兼容
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# ---- 配置 ----
ARTICLES_DIR = r"D:\code\blog1\articles"
DB_PATH = os.path.join(os.path.dirname(__file__), "..", "backend", "blog.db")
UPLOADS_DIR = os.path.join(os.path.dirname(__file__), "..", "backend", "uploads")

# ---- 工具函数 ----

def parse_frontmatter(content: str) -> tuple[dict, str]:
    """解析 YAML frontmatter，返回 (metadata, body)"""
    meta = {}
    body = content

    match = re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)', content, re.DOTALL)
    if match:
        fm_text = match.group(1)
        body = match.group(2)

        for line in fm_text.strip().split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                key = key.strip()
                val = val.strip()

                # 解析列表 [tag1, tag2]
                if val.startswith('[') and val.endswith(']'):
                    val = [v.strip() for v in val[1:-1].split(',') if v.strip()]
                # 解析布尔
                elif val.lower() in ('true', 'false'):
                    val = val.lower() == 'true'
                # 解析日期
                elif re.match(r'\d{4}-\d{2}-\d{2}', val):
                    try:
                        val = datetime.strptime(val, '%Y-%m-%d')
                    except ValueError:
                        pass

                meta[key] = val

    return meta, body.strip()


def slugify(text: str) -> str:
    """生成 URL 友好的 slug"""
    # 用文件名的数字前缀或标题生成
    text = text.lower().strip()
    # 替换中文和特殊字符为连字符
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text).strip('-')
    return text[:100]  # 限制长度


def generate_summary(body: str, max_len: int = 200) -> str:
    """从正文提取摘要（第一个非空段落）"""
    for para in body.split('\n\n'):
        para = para.strip()
        # 跳过标题行和图片行
        if para.startswith('#') or para.startswith('![') or not para:
            continue
        # 清理 markdown 语法
        clean = re.sub(r'[*_`\[\]()!]', '', para)
        clean = re.sub(r'\$.*?\$', '[公式]', clean)
        return clean[:max_len]
    return ''


def copy_and_update_images(body: str, article_dir: Path, article_name: str) -> str:
    """复制图片到 uploads 目录，更新 markdown 中的图片路径"""
    os.makedirs(UPLOADS_DIR, exist_ok=True)

    # 匹配 markdown 图片语法: ![alt](path)
    def replace_image(match):
        alt = match.group(1)
        img_path = match.group(2)

        # 跳过已经是绝对 URL 的图片
        if img_path.startswith('http://') or img_path.startswith('https://'):
            return match.group(0)

        # 解析图片文件的绝对路径
        src_file = article_dir / img_path

        # 修复：如果图片路径以文件夹名开头，去掉一层避免双重路径
        if not src_file.exists():
            parts = Path(img_path).parts
            if len(parts) > 1 and parts[0] == article_dir.name:
                alt_path = article_dir / Path(*parts[1:])
                if alt_path.exists():
                    src_file = alt_path

        if not src_file.exists():
            print(f"  ⚠ 图片不存在: {src_file}")
            return match.group(0)

        # 用内容 hash 作为文件名，避免冲突
        with open(src_file, 'rb') as f:
            file_hash = hashlib.md5(f.read()).hexdigest()[:12]

        ext = src_file.suffix
        new_name = f"{file_hash}{ext}"
        dst = Path(UPLOADS_DIR) / new_name

        if not dst.exists():
            shutil.copy2(src_file, dst)
            print(f"  📷 复制图片: {src_file.name} → {new_name}")

        return f"![{alt}](/uploads/{new_name})"

    return re.sub(r'!\[([^\]]*)\]\(([^)]+)\)', replace_image, body)


def make_unique_slug(db: sqlite3.Connection, base_slug: str, article_name: str) -> str:
    """确保 slug 唯一"""
    # 用文件名前缀（如 01、02）作为 slug 的一部分
    prefix = re.match(r'^(\d+)', article_name)
    if prefix:
        slug = f"{prefix.group(1)}-{base_slug}"
    else:
        slug = base_slug

    # 检查是否已存在
    existing = db.execute("SELECT COUNT(*) FROM articles WHERE slug = ?", (slug,)).fetchone()[0]
    if existing > 0:
        slug = f"{slug}-{existing + 1}"

    return slug


def get_or_create_tag(db: sqlite3.Connection, name: str) -> int:
    """获取或创建标签，返回 id"""
    slug = slugify(name)
    row = db.execute("SELECT id FROM tags WHERE slug = ?", (slug,)).fetchone()
    if row:
        return row[0]

    db.execute("INSERT INTO tags (name, slug) VALUES (?, ?)", (name, slug))
    return db.execute("SELECT last_insert_rowid()").fetchone()[0]


# ---- 主逻辑 ----

def main():
    articles_path = Path(ARTICLES_DIR)
    db_path = Path(DB_PATH).resolve()

    if not articles_path.exists():
        print(f"❌ 文章目录不存在: {articles_path}")
        sys.exit(1)

    if not db_path.exists():
        print(f"❌ 数据库不存在: {db_path}")
        print("请先启动后端让其自动创建数据库: cd backend && uvicorn app.main:app")
        sys.exit(1)

    # 收集所有 .md 文件
    md_files = sorted(articles_path.glob("*.md"))
    print(f"📂 找到 {len(md_files)} 个 .md 文件\n")

    conn = sqlite3.connect(str(db_path))
    imported = 0
    skipped = 0

    for md_file in md_files:
        print(f"📝 处理: {md_file.name}")

        # 读取文件内容
        content = md_file.read_text(encoding='utf-8')
        meta, body = parse_frontmatter(content)

        # 提取元数据
        title = meta.get('title', md_file.stem)
        date = meta.get('date', datetime.now())
        tags = meta.get('tags', [])
        is_pinned = meta.get('favorite', False)
        summary = meta.get('summary', generate_summary(body))

        # 生成 slug
        slug = make_unique_slug(conn, slugify(title), md_file.stem)

        # 检查是否已导入（通过标题判断）
        existing = conn.execute(
            "SELECT COUNT(*) FROM articles WHERE title = ?", (title,)
        ).fetchone()[0]
        if existing > 0:
            print(f"  ⏭ 已存在，跳过")
            skipped += 1
            continue

        # 处理图片（如果有同名文件夹）
        article_dir = articles_path / md_file.stem
        if article_dir.is_dir():
            body = copy_and_update_images(body, article_dir, md_file.stem)

        # 处理封面图（第一张图片）
        cover_match = re.search(r'!\[[^\]]*\]\(([^)]+)\)', body)
        cover_image = cover_match.group(1) if cover_match else ''

        # 插入文章
        created_at = date if isinstance(date, datetime) else datetime.now()
        conn.execute(
            """INSERT INTO articles
               (title, slug, content, summary, cover_image, is_pinned, is_published, created_at, updated_at)
               VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)""",
            (title, slug, body, summary, cover_image, is_pinned,
             created_at.strftime('%Y-%m-%d %H:%M:%S'),
             created_at.strftime('%Y-%m-%d %H:%M:%S'))
        )
        article_id = conn.execute("SELECT last_insert_rowid()").fetchone()[0]

        # 关联标签
        for tag_name in tags:
            tag_id = get_or_create_tag(conn, tag_name)
            conn.execute(
                "INSERT OR IGNORE INTO article_tags (article_id, tag_id) VALUES (?, ?)",
                (article_id, tag_id)
            )

        conn.commit()
        print(f"  ✅ 导入成功: {title} (slug: {slug}, 标签: {tags})")
        imported += 1

    conn.close()

    print(f"\n{'='*50}")
    print(f"📊 导入完成: 成功 {imported} 篇, 跳过 {skipped} 篇, 总计 {len(md_files)} 篇")


if __name__ == '__main__':
    main()
