"""Agent API routes - 数字人API路由层"""
from fastapi import APIRouter, Depends, Body
from sqlalchemy.orm import Session
from typing import List
from app.schemas.agent import AgentResponse, AgentCreate, AgentUpdate, AgentIdRequest, AgentListRequest
from app.schemas.user import UserResponse
from app.schemas.response import ApiResponse
from app.core.auth import get_current_user
from app.core.database import get_db
from app.core.exceptions import ParamErrorException
from app.services.agent_service import AgentService
from app.agent_repo.agent import AgentRepository


router = APIRouter()


def get_agent_repository() -> AgentRepository:
    """获取 AgentRepository 实例的工厂函数"""
    return AgentRepository()


def get_agent_service(
    agent_repo: AgentRepository = Depends(get_agent_repository)
) -> AgentService:
    """获取 AgentService 实例的工厂函数，用于依赖注入"""
    return AgentService(agent_repo)


@router.post("", response_model=ApiResponse[AgentResponse])
@router.post("/", response_model=ApiResponse[AgentResponse])
async def create_agent_root(
    agent_create: AgentCreate = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service)
):
    """创建数字人 - POST /api/v1/agents"""
    result = agent_service.create_agent(db, agent_create, current_user.id)
    return ApiResponse.success(result)


@router.post("/list", response_model=ApiResponse[List[AgentResponse]])
async def get_agents(
    request: AgentListRequest = Body(default=AgentListRequest()),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service)
):
    """获取数字人列表"""
    user_id = request.user_id if request.user_id else current_user.id
    result = agent_service.get_agents_by_user_id(db, user_id, request.skip, request.limit)
    return ApiResponse.success(result)


@router.post("/get", response_model=ApiResponse[AgentResponse])
async def get_agent(
    request: AgentIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service)
):
    """根据ID获取数字人"""
    result = agent_service.get_agent_by_id(db, request.agent_id, current_user.id)
    return ApiResponse.success(result)


@router.post("/create", response_model=ApiResponse[AgentResponse])
async def create_agent(
    agent_create: AgentCreate = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service)
):
    """创建数字人"""
    result = agent_service.create_agent(db, agent_create, current_user.id)
    return ApiResponse.success(result)


@router.post("/update", response_model=ApiResponse[AgentResponse])
async def update_agent(
    request: dict = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service)
):
    """更新数字人"""
    agent_id = request.get("agent_id")
    if not agent_id:
        raise ParamErrorException("agent_id is required")

    update_data = {k: v for k, v in request.items() if k != "agent_id"}
    agent_update = AgentUpdate(**update_data)

    result = agent_service.update_agent(db, agent_id, agent_update, current_user.id)
    return ApiResponse.success(result)


@router.post("/delete", response_model=ApiResponse)
async def delete_agent(
    request: AgentIdRequest = Body(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
    agent_service: AgentService = Depends(get_agent_service)
):
    """删除数字人"""
    agent_service.delete_agent(db, request.agent_id, current_user.id)
    return ApiResponse.success(message="Agent deleted successfully")
