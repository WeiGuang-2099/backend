"""
Author: yuheng li a1793138
Date: 2026-01-20
LastEditors: yuheng
LastEditTime: 2026-01-20
FilePath: /backend/app/schemas/agent.py
Description: Agent schemas for API validation - 数字人API验证模型

Copyright (c) 2026 by yuheng li, All Rights Reserved.
"""
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import datetime


class AgentBase(BaseModel):
    """数字人基础模型"""
    name: str = Field(..., min_length=1, max_length=100, description="数字人名称")
    description: Optional[str] = Field(None, description="数字人描述")
    short_description: Optional[str] = Field(None, max_length=200, description="简短描述")
    avatar_url: Optional[str] = Field(None, max_length=500, description="头像URL")


class AgentCreate(AgentBase):
    """创建数字人模型"""
    agent_type: Optional[str] = Field(None, max_length=50, description="数字人类型")
    skills: Optional[List[str]] = Field(None, description="技能列表")
    permission: Optional[str] = Field("private", max_length=50, description="权限设置")
    conversation_style: Optional[str] = Field(None, max_length=50, description="对话风格")
    personality: Optional[str] = Field(None, max_length=100, description="个性特征")
    voice_id: Optional[str] = Field(None, max_length=100, description="语音ID")
    voice_settings: Optional[Dict[str, Any]] = Field(None, description="语音设置")
    appearance_settings: Optional[Dict[str, Any]] = Field(None, description="外观设置")
    temperature: Optional[float] = Field(0.7, ge=0, le=2, description="AI温度参数")
    max_tokens: Optional[int] = Field(2048, ge=1, le=8192, description="最大token数")
    system_prompt: Optional[str] = Field(None, description="系统提示词")
    is_active: Optional[bool] = Field(True, description="是否激活")


class AgentUpdate(BaseModel):
    """更新数字人模型 - 所有字段可选"""
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = None
    short_description: Optional[str] = Field(None, max_length=200)
    avatar_url: Optional[str] = Field(None, max_length=500)
    agent_type: Optional[str] = Field(None, max_length=50)
    skills: Optional[List[str]] = None
    permission: Optional[str] = Field(None, max_length=50)
    conversation_style: Optional[str] = Field(None, max_length=50)
    personality: Optional[str] = Field(None, max_length=100)
    voice_id: Optional[str] = Field(None, max_length=100)
    voice_settings: Optional[Dict[str, Any]] = None
    appearance_settings: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = Field(None, ge=0, le=2)
    max_tokens: Optional[int] = Field(None, ge=1, le=8192)
    system_prompt: Optional[str] = None
    is_active: Optional[bool] = None


class AgentResponse(AgentBase):
    """数字人响应模型"""
    id: int
    user_id: int
    agent_type: Optional[str] = None
    skills: Optional[List[str]] = None
    permission: Optional[str] = "private"
    conversation_style: Optional[str] = None
    personality: Optional[str] = None
    voice_id: Optional[str] = None
    voice_settings: Optional[Dict[str, Any]] = None
    appearance_settings: Optional[Dict[str, Any]] = None
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048
    system_prompt: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class AgentIdRequest(BaseModel):
    """数字人ID请求模型"""
    agent_id: int = Field(..., description="数字人ID")


class AgentListRequest(BaseModel):
    """数字人列表请求模型"""
    user_id: Optional[int] = Field(None, description="用户ID，不传则获取当前用户的数字人")
    skip: int = Field(0, ge=0, description="跳过数量")
    limit: int = Field(100, ge=1, le=100, description="返回数量")
