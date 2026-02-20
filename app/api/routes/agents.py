"""Agent API routes - 数字人API路由层"""
from fastapi import APIRouter, Depends, Body
from typing import List
from app.schemas.agent import AgentResponse, AgentCreate, AgentUpdate, AgentIdRequest, AgentListRequest
from app.schemas.user import UserResponse
from app.schemas.response import ApiResponse
from app.core.auth import get_current_user
from app.core.exceptions import ParamErrorException
from app.services.agent_service import agent_service

router = APIRouter()


@router.post("", response_model=ApiResponse[AgentResponse])
@router.post("/", response_model=ApiResponse[AgentResponse])
async def create_agent_root(
    agent_create: AgentCreate = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建数字人 - POST /api/v1/agents"""
    result = agent_service.create_agent(agent_create, current_user.id)
    return ApiResponse.success(result)


@router.post("/list", response_model=ApiResponse[List[AgentResponse]])
async def get_agents(
    request: AgentListRequest = Body(default=AgentListRequest()),
    current_user: UserResponse = Depends(get_current_user)
):
    """获取数字人列表"""
    user_id = request.user_id if request.user_id else current_user.id
    result = agent_service.get_agents_by_user_id(user_id, request.skip, request.limit)
    return ApiResponse.success(result)


@router.post("/get", response_model=ApiResponse[AgentResponse])
async def get_agent(
    request: AgentIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """根据ID获取数字人"""
    result = agent_service.get_agent_by_id(request.agent_id, current_user.id)
    return ApiResponse.success(result)


@router.post("/create", response_model=ApiResponse[AgentResponse])
async def create_agent(
    agent_create: AgentCreate = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """创建数字人"""
    result = agent_service.create_agent(agent_create, current_user.id)
    return ApiResponse.success(result)


@router.post("/update", response_model=ApiResponse[AgentResponse])
async def update_agent(
    request: dict = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """更新数字人"""
    agent_id = request.get("agent_id")
    if not agent_id:
        raise ParamErrorException("agent_id is required")

    update_data = {k: v for k, v in request.items() if k != "agent_id"}
    agent_update = AgentUpdate(**update_data)

    result = agent_service.update_agent(agent_id, agent_update, current_user.id)
    return ApiResponse.success(result)


@router.post("/delete", response_model=ApiResponse)
async def delete_agent(
    request: AgentIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user)
):
    """删除数字人"""
    agent_service.delete_agent(request.agent_id, current_user.id)
    return ApiResponse.success(message="Agent deleted successfully")
