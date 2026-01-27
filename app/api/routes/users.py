"""
Author: yuheng li a1793138
Date: 2026-01-27
LastEditors: yuheng
LastEditTime: 2026-01-27
FilePath: /backend/app/api/routes/users.py
Description: User API routes - 用户API路由层

该层只负责处理HTTP请求和响应，所有业务逻辑由Service层处理。
遵循三层架构原则：API层 -> Service层 -> Repository层

Copyright (c) 2026 by yuheng li, All Rights Reserved.
"""
from fastapi import APIRouter, HTTPException, Depends, status, Body
from sqlalchemy.orm import Session
from typing import List
from app.schemas.user import UserResponse, UserUpdate, UserIdRequest, UserUpdateRequest
from app.core.database import get_db
from app.core.auth import get_current_user
from app.services.user_service import user_service

router = APIRouter()


@router.post("/list", response_model=List[UserResponse])
async def get_users(
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    获取所有用户（需要认证）
    
    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理，业务逻辑由Service层处理
    """
    return user_service.get_all_users(db)


@router.post("/get", response_model=UserResponse)
async def get_user(
    request: UserIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    根据ID获取用户（需要认证）
    
    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理和异常转换，业务逻辑由Service层处理
    """
    user = user_service.get_user_by_id(db, request.user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.post("/update", response_model=UserResponse)
async def update_user(
    request: UserUpdateRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    更新用户（需要认证）
    
    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理和异常转换，业务逻辑（如密码加密、重复检查）由Service层处理
    """
    try:
        # 构建 UserUpdate 对象
        user_update = UserUpdate(
            username=request.username,
            email=request.email,
            password=request.password
        )
        
        # 调用Service层处理业务逻辑
        updated_user = user_service.update_user(db, request.user_id, user_update)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User not found")
        return updated_user
    except ValueError as e:
        # 将业务逻辑异常转换为HTTP异常
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/delete")
async def delete_user(
    request: UserIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    删除用户（需要认证）
    
    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理和异常转换，业务逻辑由Service层处理
    """
    success = user_service.delete_user(db, request.user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")
    return {"message": "User deleted successfully"}
