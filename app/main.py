from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api.routes import api_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description=settings.DESCRIPTION
)

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.allowed_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 注册路由
app.include_router(api_router, prefix=settings.API_PREFIX)


@app.get("/")
async def root():
    return {
        "message": "Welcome to FastAPI",
        "docs": "/docs",
        "redoc": "/redoc"
    }


@app.get("/debug")
async def debug():
    import os
    from app.core.database import _get_database_url
    try:
        db_url = _get_database_url()
        db_url_preview = db_url[:80] + "..." if len(db_url) > 80 else db_url
    except Exception as e:
        db_url_preview = f"Error: {str(e)}"
    return {
        "DATABASE_URL_from_settings": settings.DATABASE_URL[:50] + "...",
        "DATABASE_URL_from_env": os.getenv("DATABASE_URL", "NOT_SET")[:50] + "...",
        "DATABASE_URL_from_get_db_url": db_url_preview,
        "K_SERVICE": os.getenv("K_SERVICE", "NOT_SET"),
    }


@app.post("/migrate")
async def run_migrations():
    """临时端点：运行数据库迁移（仅用于初始化）"""
    try:
        from alembic.config import Config
        from alembic import command
        import os
        import sys
        from pathlib import Path

        # 获取当前目录
        backend_dir = str(Path(__file__).resolve().parent.parent)
        sys.path.insert(0, backend_dir)

        # 创建 Alembic 配置
        alembic_cfg = Config()
        alembic_cfg.set_main_option("sqlalchemy.url", os.getenv("DATABASE_URL"))
        alembic_cfg.set_main_option("script_location", os.path.join(backend_dir, "alembic"))

        # 运行迁移
        command.upgrade(alembic_cfg, "head")

        return {"status": "success", "message": "Migrations completed successfully"}
    except Exception as e:
        import traceback
        return {"status": "error", "message": str(e), "traceback": traceback.format_exc()}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
