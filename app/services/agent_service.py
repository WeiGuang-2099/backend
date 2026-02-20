"""
Author: yuheng li a1793138
Date: 2026-01-20
LastEditors: yuheng
LastEditTime: 2026-01-20
FilePath: /backend/app/services/agent_service.py
Description: Agent service layer - 数字人业务逻辑层

该层负责处理数字人相关的业务逻辑，自己管理数据库会话。
遵循三层架构原则：API层 -> Service层 -> Repository层
API层不感知数据库，Service层负责获取和管理数据库会话。

Copyright (c) 2026 by yuheng li, All Rights Reserved.
"""
from typing import List, Optional
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from app.agent_repo import agent as agent_repo
from app.core.database import get_db_session


class AgentService:
    """数字人业务逻辑服务类"""

    @staticmethod
    def get_agents_by_user_id(user_id: int, skip: int = 0, limit: int = 100) -> List[AgentResponse]:
        """
        获取用户的数字人列表

        Args:
            user_id: 用户ID
            skip: 跳过数量
            limit: 返回数量

        Returns:
            数字人响应列表
        """
        db = get_db_session()
        try:
            agents = agent_repo.get_agents_by_user_id(db, user_id, skip, limit)
            return [
                AgentResponse(
                    id=a.id,
                    user_id=a.user_id,
                    name=a.name,
                    description=a.description,
                    short_description=a.short_description,
                    avatar_url=a.avatar_url,
                    agent_type=a.agent_type,
                    skills=a.skills,
                    permission=a.permission,
                    conversation_style=a.conversation_style,
                    personality=a.personality,
                    voice_id=a.voice_id,
                    voice_settings=a.voice_settings,
                    appearance_settings=a.appearance_settings,
                    temperature=a.temperature,
                    max_tokens=a.max_tokens,
                    system_prompt=a.system_prompt,
                    is_active=a.is_active,
                    created_at=a.created_at,
                    updated_at=a.updated_at
                ) for a in agents
            ]
        finally:
            db.close()

    @staticmethod
    def get_agent_by_id(agent_id: int, user_id: int) -> Optional[AgentResponse]:
        """
        根据ID获取数字人

        Args:
            agent_id: 数字人ID
            user_id: 用户ID（用于权限校验）

        Returns:
            数字人响应对象，如果不存在或无权限返回None
        """
        db = get_db_session()
        try:
            agent = agent_repo.get_agent_by_id(db, agent_id)
            if not agent:
                return None
            # 权限校验：只能访问自己的数字人
            if agent.user_id != user_id:
                return None
            return AgentResponse(
                id=agent.id,
                user_id=agent.user_id,
                name=agent.name,
                description=agent.description,
                short_description=agent.short_description,
                avatar_url=agent.avatar_url,
                agent_type=agent.agent_type,
                skills=agent.skills,
                permission=agent.permission,
                conversation_style=agent.conversation_style,
                personality=agent.personality,
                voice_id=agent.voice_id,
                voice_settings=agent.voice_settings,
                appearance_settings=agent.appearance_settings,
                temperature=agent.temperature,
                max_tokens=agent.max_tokens,
                system_prompt=agent.system_prompt,
                is_active=agent.is_active,
                created_at=agent.created_at,
                updated_at=agent.updated_at
            )
        finally:
            db.close()

    @staticmethod
    def create_agent(agent_create: AgentCreate, user_id: int) -> AgentResponse:
        """
        创建数字人

        Args:
            agent_create: 数字人创建数据
            user_id: 用户ID

        Returns:
            创建的数字人响应对象
        """
        db = get_db_session()
        try:
            created_agent = agent_repo.create_agent(db, agent_create, user_id)
            return AgentResponse(
                id=created_agent.id,
                user_id=created_agent.user_id,
                name=created_agent.name,
                description=created_agent.description,
                short_description=created_agent.short_description,
                avatar_url=created_agent.avatar_url,
                agent_type=created_agent.agent_type,
                skills=created_agent.skills,
                permission=created_agent.permission,
                conversation_style=created_agent.conversation_style,
                personality=created_agent.personality,
                voice_id=created_agent.voice_id,
                voice_settings=created_agent.voice_settings,
                appearance_settings=created_agent.appearance_settings,
                temperature=created_agent.temperature,
                max_tokens=created_agent.max_tokens,
                system_prompt=created_agent.system_prompt,
                is_active=created_agent.is_active,
                created_at=created_agent.created_at,
                updated_at=created_agent.updated_at
            )
        finally:
            db.close()

    @staticmethod
    def update_agent(agent_id: int, agent_update: AgentUpdate, user_id: int) -> Optional[AgentResponse]:
        """
        更新数字人

        Args:
            agent_id: 数字人ID
            agent_update: 更新数据
            user_id: 用户ID（用于权限校验）

        Returns:
            更新后的数字人响应对象，如果不存在或无权限返回None

        Raises:
            PermissionError: 无权限修改
        """
        db = get_db_session()
        try:
            # 权限校验
            existing_agent = agent_repo.get_agent_by_id(db, agent_id)
            if not existing_agent:
                return None
            if existing_agent.user_id != user_id:
                raise PermissionError("无权限修改此数字人")

            updated_agent = agent_repo.update_agent(db, agent_id, agent_update)
            if not updated_agent:
                return None
            return AgentResponse(
                id=updated_agent.id,
                user_id=updated_agent.user_id,
                name=updated_agent.name,
                description=updated_agent.description,
                short_description=updated_agent.short_description,
                avatar_url=updated_agent.avatar_url,
                agent_type=updated_agent.agent_type,
                skills=updated_agent.skills,
                permission=updated_agent.permission,
                conversation_style=updated_agent.conversation_style,
                personality=updated_agent.personality,
                voice_id=updated_agent.voice_id,
                voice_settings=updated_agent.voice_settings,
                appearance_settings=updated_agent.appearance_settings,
                temperature=updated_agent.temperature,
                max_tokens=updated_agent.max_tokens,
                system_prompt=updated_agent.system_prompt,
                is_active=updated_agent.is_active,
                created_at=updated_agent.created_at,
                updated_at=updated_agent.updated_at
            )
        finally:
            db.close()

    @staticmethod
    def delete_agent(agent_id: int, user_id: int) -> bool:
        """
        删除数字人

        Args:
            agent_id: 数字人ID
            user_id: 用户ID（用于权限校验）

        Returns:
            是否删除成功

        Raises:
            PermissionError: 无权限删除
        """
        db = get_db_session()
        try:
            # 权限校验
            existing_agent = agent_repo.get_agent_by_id(db, agent_id)
            if not existing_agent:
                return False
            if existing_agent.user_id != user_id:
                raise PermissionError("无权限删除此数字人")

            return agent_repo.delete_agent(db, agent_id)
        finally:
            db.close()


# 创建单例实例供导入使用
agent_service = AgentService()
