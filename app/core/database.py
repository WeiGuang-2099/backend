"""
MySQL 数据库连接和操作

注意：表结构管理已迁移到 Alembic。
请使用以下命令管理数据库迁移：
- 创建迁移: alembic revision --autogenerate -m "description"
- 应用迁移: alembic upgrade head
- 回滚迁移: alembic downgrade -1
"""
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session


# 全局变量
_engine = None
_SessionLocal = None
_last_database_url = None


def _get_database_url():
    """获取数据库 URL（直接从环境变量读取，避免模块加载顺序问题）"""
    # 直接从环境变量读取（不使用 fallback）
    database_url = os.getenv("DATABASE_URL")
    if database_url:
        return database_url

    # 如果环境变量没有设置，抛出错误（而不是使用默认值）
    raise ValueError(
        "DATABASE_URL environment variable is not set! "
        "Please set DATABASE_URL before accessing the database."
    )


def _init_db():
    """初始化数据库连接（每次调用都检查 URL 是否变化）"""
    global _engine, _SessionLocal, _last_database_url

    current_url = _get_database_url()

    # 调试：记录当前使用的 URL
    import sys
    print(f"[DEBUG] _init_db called with URL: {current_url[:80]}...", file=sys.stderr)
    print(f"[DEBUG] _last_database_url: {_last_database_url}", file=sys.stderr)

    # 如果 URL 发生变化，或者引擎未初始化，则重新创建
    if _engine is None or current_url != _last_database_url:
        print(f"[DEBUG] Creating new engine with URL: {current_url[:80]}...", file=sys.stderr)
        _engine = create_engine(
            current_url,
            echo=True,
            pool_pre_ping=True,
            pool_recycle=3600,
        )
        _SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=_engine)
        _last_database_url = current_url
    else:
        print(f"[DEBUG] Reusing existing engine", file=sys.stderr)


def get_engine():
    """获取数据库引擎"""
    _init_db()
    return _engine


def get_session_factory():
    """获取会话工厂"""
    _init_db()
    return _SessionLocal


def get_db():
    """获取数据库会话（用于FastAPI依赖注入）"""
    _init_db()
    db = _SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    获取数据库会话（用于Service层）

    注意：调用方需要负责关闭会话
    """
    _init_db()
    return _SessionLocal()


# 导出常用的函数和属性
__all__ = [
    'get_engine',
    'get_session_factory',
    'get_db',
    'get_db_session',
    'engine',
    'SessionLocal',
]


# 使用 __getattr__ 实现模块级别的延迟加载
# 当访问 engine 或 SessionLocal 时，返回实际的值
def __getattr__(name: str):
    """模块级别的 __getattr__，用于延迟加载属性"""
    if name == 'engine':
        return get_engine()
    elif name == 'SessionLocal':
        return get_session_factory()
    raise AttributeError(f"module '{__name__}' has no attribute '{name}'")
