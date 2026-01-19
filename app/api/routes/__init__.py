from fastapi import APIRouter
from app.api.routes import items, users

api_router = APIRouter()

# 注册各个模块的路由
api_router.include_router(items.router, prefix="/items", tags=["items"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
