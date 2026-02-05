"""
Author: yuheng li a1793138
Date: 2026-01-20 04:48:03
LastEditors: yuheng
LastEditTime: 2026-01-20 05:04:40
FilePath: /task-all/backend/app/schemas/user.py
Description: User schemas for API validation

Copyright (c) 2024 by yuheng li, All Rights Reserved.
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional


class UserBase(BaseModel):
    """用户基础模型"""
    username: str = Field(..., min_length=3, max_length=50, description="用户名")
    email: EmailStr = Field(..., description="邮箱地址")
    full_name: Optional[str] = Field(None, max_length=100, description="全名")


class UserCreate(UserBase):
    """创建用户模型 - 包含密码"""
    password: str = Field(..., min_length=6, max_length=100, description="密码（至少6位）")


class UserRegister(UserCreate):
    """用户注册模型 - 继承自 UserCreate，与 OpenAPI schema 保持一致"""
    pass


class UserUpdate(BaseModel):
    """更新用户模型 - 所有字段可选"""
    full_name: Optional[str] = Field(None, max_length=100)
    password: Optional[str] = Field(None, min_length=6, max_length=100)


class UserResponse(UserBase):
    """用户响应模型 - 不包含密码"""
    id: int
    is_active: bool = True
    is_superuser: bool = False
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str = Field(..., description="用户名或邮箱")
    password: str = Field(..., description="密码")


class Token(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class TokenResponse(BaseModel):
    """Token 响应模型 - 别名"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


class UserWithToken(UserResponse):
    """带 token 的用户响应模型"""
    access_token: str
    token_type: str = "bearer"


class UserIdRequest(BaseModel):
    """用户ID请求模型 - 用于POST方式获取/删除用户"""
    user_id: int = Field(..., description="用户ID")


class UserUpdateRequest(BaseModel):
    """用户更新请求模型 - 用于POST方式更新用户"""
    user_id: int = Field(..., description="用户ID")
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


# 内部使用的完整用户模型（包含密码）
class UserInDB(UserBase):
    """数据库中的完整用户模型 - 仅内部使用"""
    id: int
    password: str  # 应该是哈希后的密码
