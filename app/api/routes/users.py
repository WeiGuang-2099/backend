from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from app.schemas.user import UserResponse, UserCreate, UserUpdate
from app.core.database import db
from app.core.auth import get_current_user
from app.core.security import get_password_hash

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(current_user: UserResponse = Depends(get_current_user)):
    """获取所有用户（需要认证）"""
    return db.get_all_users()


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(user_id: int, current_user: UserResponse = Depends(get_current_user)):
    """根据ID获取用户（需要认证）"""
    user = db.get_user(user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user: UserUpdate,
    current_user: UserResponse = Depends(get_current_user)
):
    """更新用户（需要认证）"""
    # 如果更新密码，需要哈希加密
    if user.password:
        user.password = get_password_hash(user.password)
    
    updated_user = db.update_user(user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user)
):
    """删除用户（需要认证）"""
    success = db.delete_user(user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
