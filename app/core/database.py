"""
MySQL 数据库连接和操作

注意：表结构管理已迁移到 Alembic。
请使用以下命令管理数据库迁移：
- 创建迁移: alembic revision --autogenerate -m "description"
- 应用迁移: alembic upgrade head
- 回滚迁移: alembic downgrade -1
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from app.core.config import settings

# 创建数据库引擎（添加连接池配置）
engine = create_engine(
    settings.DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,  # 连接前先 ping，确保连接有效
    pool_recycle=3600,   # 1小时回收连接
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """获取数据库会话（用于FastAPI依赖注入）"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_db_session() -> Session:
    """
    获取数据库会话（用于Service层）

    注意：调用方需要负责关闭会话
    """
    return SessionLocal()