from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 项目基本信息
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI backend service"
    API_PREFIX: str = "/api/v1"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["*"]
    
    # 数据库配置（示例）
    # DATABASE_URL: str = "sqlite:///./test.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
