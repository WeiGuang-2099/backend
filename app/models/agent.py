"""
Author: yuheng li a1793138
Date: 2026-01-20
LastEditors: yuheng
LastEditTime: 2026-01-20
FilePath: /backend/app/models/agent.py
Description: Agent model for database - 数字人数据库模型定义

Copyright (c) 2026 by yuheng li, All Rights Reserved.
"""
from sqlalchemy import Column, Integer, String, Text, Boolean, Float, DateTime, ForeignKey, TypeDecorator
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
import json


class JSONText(TypeDecorator):
    """
    自定义 JSON 类型，兼容 MySQL，能够处理空字符串
    """
    impl = Text
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return None
        return json.dumps(value)

    def process_result_value(self, value, dialect):
        if value is None or value == '':
            return None
        return json.loads(value)


Base = declarative_base()


class Agent(Base):
    """
    数字人数据模型 - 数据库表定义

    该模型定义了数字人表的结构，包含数字人的基本信息、AI配置等。
    """
    __tablename__ = "agents"

    id = Column(Integer, primary_key=True, index=True, comment="数字人唯一标识ID")
    user_id = Column(Integer, ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True, comment="所属用户ID")
    name = Column(String(100), nullable=False, comment="数字人名称")
    description = Column(Text, nullable=True, comment="数字人描述")
    short_description = Column(String(200), nullable=True, comment="简短描述")
    avatar_url = Column(String(500), nullable=True, comment="头像URL")

    # 类型与技能
    agent_type = Column(String(50), nullable=True, comment="数字人类型")
    skills = Column(JSONText, nullable=True, comment="技能列表")
    permission = Column(String(50), default='private', comment="权限设置")

    # 对话配置
    conversation_style = Column(String(50), nullable=True, comment="对话风格")
    personality = Column(String(100), nullable=True, comment="个性特征")

    # AI配置
    voice_id = Column(String(100), nullable=True, comment="语音ID")
    voice_settings = Column(JSONText, nullable=True, comment="语音设置")
    appearance_settings = Column(JSONText, nullable=True, comment="外观设置")
    temperature = Column(Float, default=0.7, comment="AI温度参数")
    max_tokens = Column(Integer, default=2048, comment="最大token数")
    system_prompt = Column(Text, nullable=True, comment="系统提示词")

    # 状态
    is_active = Column(Boolean, default=True, comment="是否激活")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), comment="创建时间")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), comment="更新时间")
