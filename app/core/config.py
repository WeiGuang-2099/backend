"""
配置管理模块

完全从环境变量读取配置，确保在 Cloud Run 等环境中正确工作
"""
import os
from typing import List, Union

# 先定义默认值
_DEFAULTS = {
    'PROJECT_NAME': 'FastAPI Backend',
    'VERSION': '1.0.0',
    'DESCRIPTION': 'FastAPI backend service',
    'API_PREFIX': '/api/v1',
    'ALLOWED_ORIGINS': 'http://localhost:3000,http://localhost:3001',
    'SECRET_KEY': 'your-secret-key-change-this-in-production-min-32-chars',
    'ALGORITHM': 'HS256',
    'ACCESS_TOKEN_EXPIRE_MINUTES': 30,
    'DATABASE_URL': 'mysql+pymysql://jwt_user:jwt_password@localhost:3306/jwt_auth_db',
}


def get_env(key: str, default=None):
    """从环境变量读取配置，如果不存在则返回默认值"""
    return os.getenv(key, default or _DEFAULTS.get(key))


def get_allowed_origins_list() -> List[str]:
    """获取 ALLOWED_ORIGINS 列表"""
    origins_str = get_env('ALLOWED_ORIGINS')
    if isinstance(origins_str, str):
        return [origin.strip() for origin in origins_str.split(',') if origin.strip()]
    return origins_str


# 向后兼容的 Settings 类（可选使用）
class Settings:
    """Settings 类（向后兼容）"""

    def __init__(self):
        # 在实例化时读取所有环境变量
        self.PROJECT_NAME = get_env('PROJECT_NAME')
        self.VERSION = get_env('VERSION')
        self.DESCRIPTION = get_env('DESCRIPTION')
        self.API_PREFIX = get_env('API_PREFIX')
        self.ALLOWED_ORIGINS = get_env('ALLOWED_ORIGINS')
        self.SECRET_KEY = get_env('SECRET_KEY')
        self.ALGORITHM = get_env('ALGORITHM')
        self.ACCESS_TOKEN_EXPIRE_MINUTES = int(get_env('ACCESS_TOKEN_EXPIRE_MINUTES'))
        self.DATABASE_URL = get_env('DATABASE_URL')

    @property
    def allowed_origins_list(self) -> List[str]:
        return get_allowed_origins_list()


# 延迟初始化的 settings 实例
_settings_instance = None


def get_settings() -> Settings:
    """获取 Settings 实例（延迟初始化）"""
    return Settings()


# 模块级别的延迟加载
def __getattr__(name: str):
    """模块级别的 __getattr__"""
    if name == 'settings':
        return get_settings()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
