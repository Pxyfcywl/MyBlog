"""应用配置管理 - 从 .env 文件读取配置"""
from pydantic_settings import BaseSettings
from pathlib import Path


class Settings(BaseSettings):
    admin_secret_key: str = "change-me"
    database_url: str = "sqlite+aiosqlite:///./blog.db"
    upload_dir: str = "./uploads"
    frontend_url: str = "http://localhost:5173"
    mineru_api_key: str = ""

    # LLM 审查配置（OpenAI 兼容接口）
    llm_base_url: str = "https://open.bigmodel.cn/api/paas/v4"
    llm_api_key: str = ""
    llm_model_name: str = "glm-4-flash"

    class Config:
        env_file = ".env"


settings = Settings()

# 确保上传目录存在
Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
