"""
MySQL 数据库连接和操作
"""
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.exc import OperationalError
from app.core.config import settings
from app.models.user import Base
import time

# 创建数据库引擎（添加连接池配置）
engine = create_engine(
    settings.DATABASE_URL, 
    echo=True,
    pool_pre_ping=True,  # 连接前先 ping，确保连接有效
    pool_recycle=3600,   # 1小时回收连接
)

# 创建会话工厂
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def init_db(retries=5, delay=2):
    """
    初始化数据库：创建所有表
    
    Args:
        retries: 重试次数
        delay: 重试间隔（秒）
    """
    for attempt in range(retries):
        try:
            print(f"正在连接数据库... (尝试 {attempt + 1}/{retries})")
            Base.metadata.create_all(bind=engine)
            print("数据库连接成功，表已创建")
            return
        except OperationalError as e:
            if attempt < retries - 1:
                print(f"连接失败，{delay}秒后重试... 错误: {e}")
                time.sleep(delay)
            else:
                print(f"数据库连接失败，请检查：")
                print(f"   1. MySQL 是否已启动: docker-compose ps")
                print(f"   2. 端口 3306 是否可用")
                print(f"   3. 连接信息是否正确: {settings.DATABASE_URL}")
                raise


def get_db():
    """获取数据库会话"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()