"""
Author: yuheng li a1793138
Date: 2026-01-27
LastEditors: yuheng
LastEditTime: 2026-01-27
FilePath: /backend/app/services/user_service.py
Description: User service layer - 用户业务逻辑层

该层负责处理用户相关的业务逻辑，不直接操作数据库。
遵循三层架构原则：API层 -> Service层 -> Repository层

Copyright (c) 2026 by yuheng li, All Rights Reserved.
"""
from sqlalchemy.orm import Session
from typing import List, Optional
from app.schemas.user import UserCreate, UserUpdate, UserResponse
from app.user_repo import user as user_repo
from app.core.security import get_password_hash, verify_password


class UserService:
    """用户业务逻辑服务类"""
    
    @staticmethod
    def get_all_users(db: Session) -> List[UserResponse]:
        """
        获取所有用户
        
        Args:
            db: 数据库会话
            
        Returns:
            用户响应列表
        """
        users = user_repo.get_all_users(db)
        return [UserResponse(id=u.id, username=u.username, email=u.email) for u in users]
    
    @staticmethod
    def get_user_by_id(db: Session, user_id: int) -> Optional[UserResponse]:
        """
        根据ID获取用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            用户响应对象，如果不存在返回None
        """
        user = user_repo.get_user_by_id(db, user_id)
        if not user:
            return None
        return UserResponse(id=user.id, username=user.username, email=user.email)
    
    @staticmethod
    def create_user(db: Session, user_create: UserCreate) -> UserResponse:
        """
        创建新用户（包含业务逻辑：检查重复、密码加密）
        
        Args:
            db: 数据库会话
            user_create: 用户创建数据
            
        Returns:
            创建的用户响应对象
            
        Raises:
            ValueError: 用户名或邮箱已存在
        """
        # 业务逻辑：检查用户名是否已存在
        existing_user = user_repo.get_user_by_username(db, user_create.username)
        if existing_user:
            raise ValueError(f"用户名 '{user_create.username}' 已存在")
        
        # 业务逻辑：检查邮箱是否已存在
        existing_email = user_repo.get_user_by_email(db, user_create.email)
        if existing_email:
            raise ValueError(f"邮箱 '{user_create.email}' 已被注册")
        
        # 业务逻辑：密码加密
        hashed_password = get_password_hash(user_create.password)
        user_create.password = hashed_password
        
        # 调用Repository层创建用户
        created_user = user_repo.create_user(db, user_create)
        return UserResponse(
            id=created_user.id,
            username=created_user.username,
            email=created_user.email
        )
    
    @staticmethod
    def update_user(db: Session, user_id: int, user_update: UserUpdate) -> Optional[UserResponse]:
        """
        更新用户（包含业务逻辑：密码加密、重复检查）
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            user_update: 更新数据
            
        Returns:
            更新后的用户响应对象，如果用户不存在返回None
            
        Raises:
            ValueError: 用户名或邮箱已被其他用户使用
        """
        # 检查用户是否存在
        existing_user = user_repo.get_user_by_id(db, user_id)
        if not existing_user:
            return None
        
        # 业务逻辑：如果更新用户名，检查是否重复
        if user_update.username and user_update.username != existing_user.username:
            duplicate_username = user_repo.get_user_by_username(db, user_update.username)
            if duplicate_username:
                raise ValueError(f"用户名 '{user_update.username}' 已被使用")
        
        # 业务逻辑：如果更新邮箱，检查是否重复
        if user_update.email and user_update.email != existing_user.email:
            duplicate_email = user_repo.get_user_by_email(db, user_update.email)
            if duplicate_email:
                raise ValueError(f"邮箱 '{user_update.email}' 已被使用")
        
        # 业务逻辑：如果更新密码，需要加密
        if user_update.password:
            user_update.password = get_password_hash(user_update.password)
        
        # 调用Repository层更新用户
        updated_user = user_repo.update_user(db, user_id, user_update)
        if not updated_user:
            return None
            
        return UserResponse(
            id=updated_user.id,
            username=updated_user.username,
            email=updated_user.email
        )
    
    @staticmethod
    def delete_user(db: Session, user_id: int) -> bool:
        """
        删除用户
        
        Args:
            db: 数据库会话
            user_id: 用户ID
            
        Returns:
            是否删除成功
        """
        return user_repo.delete_user(db, user_id)
    
    @staticmethod
    def register_user(db: Session, user_create: UserCreate) -> UserResponse:
        """
        注册新用户（包含完整的业务逻辑）
        
        该方法与 create_user 类似，但更侧重于用户注册场景，
        可以在此添加额外的注册相关业务逻辑（如发送欢迎邮件等）
        
        Args:
            db: 数据库会话
            user_create: 用户注册数据
            
        Returns:
            注册成功的用户响应对象
            
        Raises:
            ValueError: 用户名或邮箱已存在
        """
        return UserService.create_user(db, user_create)
    
    @staticmethod
    def authenticate_user(db: Session, username: str, password: str) -> Optional[UserResponse]:
        """
        用户认证（业务逻辑：验证密码）
        
        Args:
            db: 数据库会话
            username: 用户名
            password: 密码（明文）
            
        Returns:
            认证成功返回用户响应对象，失败返回None
        """
        user = user_repo.get_user_by_username(db, username)
        if not user:
            return None
        
        # 业务逻辑：验证密码
        if not verify_password(password, user.password):
            return None
        
        return UserResponse(id=user.id, username=user.username, email=user.email)


# 创建单例实例供导入使用
user_service = UserService()
