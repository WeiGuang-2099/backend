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


class UserCreate(UserBase):
    """创建用户模型 - 包含密码"""
    password: str = Field(..., min_length=6, description="密码（至少6位）")


class UserUpdate(BaseModel):
    """更新用户模型 - 所有字段可选"""
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    email: Optional[EmailStr] = None
    password: Optional[str] = Field(None, min_length=6)


class UserResponse(UserBase):
    """用户响应模型 - 不包含密码"""
    id: int
    
    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    """用户登录模型"""
    username: str
    password: str


class TokenResponse(BaseModel):
    """Token 响应模型"""
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# 内部使用的完整用户模型（包含密码）
class UserInDB(UserBase):
    """数据库中的完整用户模型 - 仅内部使用"""
    id: int
    password: str  # 应该是哈希后的密码
