from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    # 项目基本信息
    PROJECT_NAME: str = "FastAPI Backend"
    VERSION: str = "1.0.0"
    DESCRIPTION: str = "FastAPI backend service"
    API_PREFIX: str = "/api/v1"
    
    # CORS配置
    ALLOWED_ORIGINS: List[str] = ["http://localhost:3000", "http://localhost:3001"]
    
    # JWT 配置
    SECRET_KEY: str = "your-secret-key-change-this-in-production-min-32-chars"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # 数据库配置（示例）
    # DATABASE_URL: str = "sqlite:///./test.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
