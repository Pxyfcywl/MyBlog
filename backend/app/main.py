"""FastAPI 博客后端入口"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.database import engine
from app.models import Base
from app.routers import articles, tags, upload, tools
from app.auth import router as auth_router

app = FastAPI(title="MyBlog API", version="0.1.0")

# CORS - 允许前端跨域访问
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(articles.router)
app.include_router(tags.router)
app.include_router(upload.router)
app.include_router(auth_router)
app.include_router(tools.router)

# 静态文件服务 - 图片上传目录 + 音乐目录
app.mount("/uploads", StaticFiles(directory=settings.upload_dir), name="uploads")
app.mount("/music", StaticFiles(directory="music"), name="music")


@app.on_event("startup")
async def startup():
    """启动时自动创建数据库表"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.get("/")
async def root():
    return {"message": "MyBlog API is running", "docs": "/docs"}


@app.get("/api/music/list")
async def list_music():
    """列出 music 目录下的所有音频文件"""
    import os
    from urllib.parse import quote
    music_dir = "music"
    if not os.path.exists(music_dir):
        return []
    files = []
    for f in sorted(os.listdir(music_dir)):
        if f.lower().endswith(('.mp3', '.wav', '.ogg', '.flac', '.m4a')):
            name = os.path.splitext(f)[0]
            files.append({
                "name": name,
                "artist": "本地音乐",
                "url": f"/music/{quote(f)}",
            })
    return files
