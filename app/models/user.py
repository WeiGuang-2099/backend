"""
Author: yuheng li a1793138
Date: 2026-01-27
LastEditors: yuheng
LastEditTime: 2026-01-27
FilePath: /backend/app/models/user.py
Description: User model for database - 用户数据库模型定义

Copyright (c) 2026 by yuheng li, All Rights Reserved.
"""
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class User(Base):
    """
    用户数据模型 - 数据库表定义
    
    该模型定义了用户表的结构，所有字段都包含 comment 以便在数据库中生成表注释。
    这些注释对于数据库维护和理解表结构非常重要。
    """
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True, comment="用户唯一标识ID")
    username = Column(String(50), unique=True, index=True, nullable=False, comment="用户名，唯一且不能为空")
    email = Column(String(100), unique=True, index=True, nullable=False, comment="用户邮箱地址，唯一且不能为空")
    password = Column(String(255), nullable=False, comment="用户密码（bcrypt哈希加密后存储）")
