"""
Author: yuheng li a1793138
Date: 2026-01-27
LastEditors: yuheng
LastEditTime: 2026-01-27
FilePath: /backend/app/api/routes/auth.py
Description: Authentication API routes - 认证相关路由层

该层只负责处理HTTP请求和响应，认证业务逻辑由Service层处理。
遵循三层架构原则：API层 -> Service层 -> Repository层
API层不感知数据库，数据库会话由Service层内部管理。

Copyright (c) 2026 by yuheng li, All Rights Reserved.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from app.schemas.user import UserLogin, UserRegister, UserCreate, UserResponse, TokenResponse, UserWithToken
from app.core.security import create_access_token
from app.core.auth import get_current_user
from app.services.user_service import user_service

router = APIRouter()


@router.post("/register", response_model=UserWithToken, status_code=status.HTTP_201_CREATED)
async def register(user: UserRegister):
    """
    用户注册

    API层只负责请求处理和异常转换，
    所有业务逻辑（重复检查、密码加密）由Service层处理

    Args:
        user: 用户注册信息

    Returns:
        UserWithToken: 包含 access_token 和用户信息

    Raises:
        HTTPException: 用户名或邮箱已存在时返回 400
    """
    try:
        # 调用Service层处理注册业务逻辑
        new_user = user_service.register_user(user)

        # API层只负责生成Token和返回响应
        access_token = create_access_token(
            data={"sub": str(new_user.id), "username": new_user.username}
        )

        # 返回 UserWithToken 格式
        return UserWithToken(
            access_token=access_token,
            token_type="bearer",
            id=new_user.id,
            username=new_user.username,
            email=new_user.email,
            full_name=new_user.full_name,
            is_active=new_user.is_active,
            is_superuser=new_user.is_superuser,
            created_at=new_user.created_at,
            updated_at=new_user.updated_at
        )
    except ValueError as e:
        # 将业务逻辑异常转换为HTTP异常
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/login", response_model=UserWithToken)
async def login(user_login: UserLogin):
    """
    用户登录

    API层只负责请求处理和异常转换，
    认证逻辑（查找用户、验证密码）由Service层处理

    Args:
        user_login: 登录凭证（用户名和密码）

    Returns:
        UserWithToken: 包含 access_token 和用户信息

    Raises:
        HTTPException: 凭证无效时返回 401
    """
    # 调用Service层处理认证业务逻辑
    user = user_service.authenticate_user(user_login.username, user_login.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )

    # API层只负责生成Token和返回响应
    access_token = create_access_token(
        data={"sub": str(user.id), "username": user.username}
    )

    return UserWithToken(
        access_token=access_token,
        token_type="bearer",
        id=user.id,
        username=user.username,
        email=user.email,
        full_name=user.full_name,
        is_active=user.is_active,
        is_superuser=user.is_superuser,
        created_at=user.created_at,
        updated_at=user.updated_at
    )


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: UserResponse = Depends(get_current_user)):
    """
    获取当前登录用户的信息（需要认证）
    
    Args:
        current_user: 通过 JWT Token 解析出的当前用户
        
    Returns:
        UserResponse: 当前用户信息
    """
    return current_user


@router.post("/logout")
async def logout(current_user: UserResponse = Depends(get_current_user)):
    """
    用户登出（前端需要删除本地存储的 token）
    
    注意：JWT 是无状态的，服务端不需要做任何处理，
    只需前端删除存储的 token 即可
    
    Returns:
        dict: 成功消息
    """
    return {"message": "Logout successful"}
