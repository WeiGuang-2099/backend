"""
Author: yuheng li a1793138
Date: 2026-01-20 04:58:37
LastEditors: yuheng 
LastEditTime: 2026-01-20 05:04:40
FilePath: /task-all/backend/app/core/database.py
Description: Simple in-memory database implementation

Copyright (c) 2024 by yuheng li, All Rights Reserved. 
"""
from app.schemas.user import UserInDB, UserCreate, UserUpdate
from typing import Dict, List, Optional


class SimpleDatabase:
    def __init__(self):
        self.users: Dict[int, UserInDB] = {}
        self.user_id_counter = 1
        # 延迟初始化示例数据，避免循环导入
        self._sample_data_initialized = False

    def _ensure_initialized(self):
        """确保示例数据已初始化"""
        if not self._sample_data_initialized:
            self._initialize_with_sample_data()
            self._sample_data_initialized = True
    
    def get_user(self, user_id: int) -> Optional[UserInDB]:
        """根据ID获取用户"""
        self._ensure_initialized()
        return self.users.get(user_id)
    
    def get_all_users(self) -> List[UserInDB]:
        """获取所有用户"""
        self._ensure_initialized()
        return list(self.users.values())

    def create_user(self, user_create: UserCreate) -> UserInDB:
        """创建新用户"""
        # 创建完整的UserInDB对象
        new_user = UserInDB(
            id=self.user_id_counter,
            username=user_create.username,
            email=user_create.email,
            password=user_create.password  # 注意：实际应用中应该hash密码
        )
        self.users[self.user_id_counter] = new_user
        self.user_id_counter += 1
        return new_user
    
    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[UserInDB]:
        """更新用户"""
        user = self.users.get(user_id)
        if not user:
            return None
        
        # 只更新提供的字段
        update_data = user_update.dict(exclude_unset=True)
        updated_user = user.copy(update=update_data)
        self.users[user_id] = updated_user
        return updated_user
    
    def delete_user(self, user_id: int) -> bool:
        """删除用户"""
        if user_id in self.users:
            del self.users[user_id]
            return True
        return False
    
    def _initialize_with_sample_data(self):
        """初始化示例数据（使用加密密码）"""
        # 导入放在这里避免循环导入
        from app.core.security import get_password_hash
        
        sample_users = [
            {
                "username": "john",
                "email": "john@example.com",
                "password": "password123"
            },
            {
                "username": "jane",
                "email": "jane@example.com",
                "password": "password456"
            },
            {
                "username": "alice",
                "email": "alice@example.com",
                "password": "password789"
            }
        ]
        
        for user_data in sample_users:
            # 加密密码
            hashed_password = get_password_hash(user_data["password"])
            
            # 创建用户（使用加密后的密码）
            user_create = UserCreate(
                username=user_data["username"],
                email=user_data["email"],
                password=hashed_password
            )
            self.create_user(user_create)


# 创建全局数据库实例
db = SimpleDatabase()