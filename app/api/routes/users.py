from fastapi import APIRouter, HTTPException
from typing import List
from app.schemas.user import UserResponse, UserCreate, UserUpdate, UserLogin
from app.core.database import db

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users():
    """获取所有用户"""
    return db.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int):
    """根据ID获取用户"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/", response_model=UserResponse)
async def create_user(user: UserCreate):
    """创建新用户"""
    # 检查用户名是否已存在
    existing_users = db.get_all_users()
    for existing_user in existing_users:
        if existing_user.username == user.username:
            raise HTTPException(status_code=400, detail="Username already exists")
        if existing_user.email == user.email:
            raise HTTPException(status_code=400, detail="Email already exists")
    
    new_user = db.create_user(user)
    return new_user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(user_id: int, user: UserUpdate):
    """更新用户"""
    updated_user = db.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}")
async def delete_user(user_id: int):
    """删除用户"""
    success = db.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}


@router.post("/login")
async def login(user_login: UserLogin):
    """用户登录（简单示例）"""
    users = db.get_all_users()
    for user in users:
        if user.username == user_login.username and user.password == user_login.password:
            return {
                "message": "Login successful",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email
                }
            }
    raise HTTPException(status_code=401, detail="Invalid username or password")
