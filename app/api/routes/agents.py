"""
Author: yuheng li a1793138
Date: 2026-01-20
LastEditors: yuheng
LastEditTime: 2026-01-20
FilePath: /backend/app/api/routes/agents.py
Description: Agent API routes - 数字人API路由层

该层只负责处理HTTP请求和响应，所有业务逻辑由Service层处理。
遵循三层架构原则：API层 -> Service层 -> Repository层
API层不感知数据库，数据库会话由Service层内部管理。

Copyright (c) 2026 by yuheng li, All Rights Reserved.
"""
from fastapi import APIRouter, HTTPException, Depends, Body
from typing import List
from app.schemas.agent import AgentResponse, AgentCreate, AgentUpdate, AgentIdRequest, AgentListRequest
from app.schemas.user import UserResponse
from app.core.auth import get_current_user
from app.services.agent_service import agent_service

router = APIRouter()


@router.post("/list", response_model=List[AgentResponse])
async def get_agents(
    request: AgentListRequest = Body(default=AgentListRequest()),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    获取数字人列表（需要认证）

    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理，业务逻辑由Service层处理
    """
    user_id = request.user_id if request.user_id else current_user.id
    return agent_service.get_agents_by_user_id(user_id, request.skip, request.limit)


@router.post("/get", response_model=AgentResponse)
async def get_agent(
    request: AgentIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    根据ID获取数字人（需要认证）

    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理和异常转换，业务逻辑由Service层处理
    """
    agent = agent_service.get_agent_by_id(request.agent_id, current_user.id)
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found or no permission")
    return agent


@router.post("/create", response_model=AgentResponse)
async def create_agent(
    agent_create: AgentCreate = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    创建数字人（需要认证）

    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理，业务逻辑由Service层处理
    """
    return agent_service.create_agent(agent_create, current_user.id)


@router.post("/update", response_model=AgentResponse)
async def update_agent(
    request: dict = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    更新数字人（需要认证）

    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理和异常转换，业务逻辑由Service层处理
    """
    agent_id = request.get("agent_id")
    if not agent_id:
        raise HTTPException(status_code=400, detail="agent_id is required")

    # 构建更新对象，排除agent_id
    update_data = {k: v for k, v in request.items() if k != "agent_id"}
    agent_update = AgentUpdate(**update_data)

    try:
        updated_agent = agent_service.update_agent(agent_id, agent_update, current_user.id)
        if not updated_agent:
            raise HTTPException(status_code=404, detail="Agent not found")
        return updated_agent
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))


@router.post("/delete")
async def delete_agent(
    request: AgentIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """
    删除数字人（需要认证）

    使用POST方式以便后续RPC调用兼容
    API层只负责请求处理和异常转换，业务逻辑由Service层处理
    """
    try:
        success = agent_service.delete_agent(request.agent_id, current_user.id)
        if not success:
            raise HTTPException(status_code=404, detail="Agent not found")
        return {"message": "Agent deleted successfully"}
    except PermissionError as e:
        raise HTTPException(status_code=403, detail=str(e))
