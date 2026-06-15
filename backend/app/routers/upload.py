"""图片上传 API"""
import uuid
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from app.auth import verify_admin
from app.config import settings

router = APIRouter(prefix="/api/upload", tags=["upload"])

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


@router.post("/image", dependencies=[Depends(verify_admin)])
async def upload_image(file: UploadFile = File(...)):
    """上传图片，返回访问 URL（需要管理员密钥）"""
    ext = Path(file.filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail=f"不支持的图片格式: {ext}")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="文件大小不能超过 10MB")

    # 生成唯一文件名，避免冲突
    filename = f"{uuid.uuid4().hex}{ext}"
    filepath = Path(settings.upload_dir) / filename

    with open(filepath, "wb") as f:
        f.write(content)

    return {
        "url": f"/uploads/{filename}",
        "filename": filename,
    }
