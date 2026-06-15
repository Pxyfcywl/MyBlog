"""密钥认证依赖 - 从 Authorization 头校验 Bearer Token"""
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from app.config import settings

security = HTTPBearer()

router = APIRouter(prefix="/api/auth", tags=["auth"])


async def verify_admin(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """校验管理员密钥"""
    if credentials.credentials != settings.admin_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密钥无效",
        )


@router.get("/verify")
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """验证密钥是否有效 - 供前端调用"""
    if credentials.credentials != settings.admin_secret_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="密钥无效",
        )
    return {"valid": True}
