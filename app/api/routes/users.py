from fastapi import APIRouter, HTTPException, Depends, status
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user import UserResponse, UserUpdate
from app.core.database import get_db
from app.core.auth import get_current_user
from app.core.security import get_password_hash
from app.crud import user as crud_user

router = APIRouter()


@router.get("/", response_model=List[UserResponse])
async def get_users(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """获取所有用户（需要认证）"""
    users = crud_user.get_all_users(db)
    return [UserResponse(id=u.id, username=u.username, email=u.email) for u in users]


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """根据ID获取用户（需要认证）"""
    user = crud_user.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=user.id, username=user.username, email=user.email)


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int, 
    user: UserUpdate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """更新用户（需要认证）"""
    # 如果更新密码，需要哈希加密
    if user.password:
        user.password = get_password_hash(user.password)
    
    updated_user = crud_user.update_user(db, user_id, user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return UserResponse(id=updated_user.id, username=updated_user.username, email=updated_user.email)


@router.delete("/{user_id}")
async def delete_user(
    user_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """删除用户（需要认证）"""
    success = crud_user.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
