"""Agent service layer - 数字人业务逻辑层"""
from typing import List
from sqlalchemy.orm import Session
from app.schemas.agent import AgentCreate, AgentUpdate, AgentResponse
from app.agent_repo.agent import AgentRepository
from app.core.exceptions import (
    NotFoundException,
    PermissionDeniedException,
    ErrorCode,
    BizException
)


class AgentService:
    """数字人业务逻辑服务类"""

    def __init__(self, agent_repo: AgentRepository):
        """初始化服务

        Args:
            agent_repo: 数字人数据访问层实例
        """
        self._agent_repo = agent_repo

    def get_agents_by_user_id(self, db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[AgentResponse]:
        """获取用户的数字人列表

        Args:
            db: 数据库会话
            user_id: 用户ID
            skip: 跳过数量
            limit: 返回数量限制

        Returns:
            数字人响应列表
        """
        agents = self._agent_repo.get_agents_by_user_id(db, user_id, skip, limit)
        return [AgentResponse.model_validate(a) for a in agents]

    def get_agent_by_id(self, db: Session, agent_id: int, user_id: int) -> AgentResponse:
        """根据ID获取数字人

        Args:
            db: 数据库会话
            agent_id: 数字人ID
            user_id: 当前用户ID

        Returns:
            数字人响应对象

        Raises:
            NotFoundException: 数字人不存在
            PermissionDeniedException: 无权限访问
        """
        agent = self._agent_repo.get_agent_by_id(db, agent_id)
        if not agent:
            raise NotFoundException("Agent not found", ErrorCode.AGENT_NOT_FOUND)
        if agent.user_id != user_id:
            raise PermissionDeniedException("No permission to access this agent")
        return AgentResponse.model_validate(agent)

    def create_agent(self, db: Session, agent_create: AgentCreate, user_id: int) -> AgentResponse:
        """创建数字人

        Args:
            db: 数据库会话
            agent_create: 数字人创建数据
            user_id: 用户ID

        Returns:
            创建的数字人响应对象
        """
        created_agent = self._agent_repo.create_agent(db, agent_create, user_id)
        return AgentResponse.model_validate(created_agent)

    def update_agent(self, db: Session, agent_id: int, agent_update: AgentUpdate, user_id: int) -> AgentResponse:
        """更新数字人

        Args:
            db: 数据库会话
            agent_id: 数字人ID
            agent_update: 更新数据
            user_id: 当前用户ID

        Returns:
            更新后的数字人响应对象

        Raises:
            NotFoundException: 数字人不存在
            PermissionDeniedException: 无权限修改
        """
        existing_agent = self._agent_repo.get_agent_by_id(db, agent_id)
        if not existing_agent:
            raise NotFoundException("Agent not found", ErrorCode.AGENT_NOT_FOUND)
        if existing_agent.user_id != user_id:
            raise PermissionDeniedException("No permission to update this agent")

        updated_agent = self._agent_repo.update_agent(db, agent_id, agent_update)
        if not updated_agent:
            raise BizException(ErrorCode.AGENT_UPDATE_FAILED, "Failed to update agent")
        return AgentResponse.model_validate(updated_agent)

    def delete_agent(self, db: Session, agent_id: int, user_id: int) -> bool:
        """删除数字人

        Args:
            db: 数据库会话
            agent_id: 数字人ID
            user_id: 当前用户ID

        Returns:
            是否删除成功

        Raises:
            NotFoundException: 数字人不存在
            PermissionDeniedException: 无权限删除
        """
        existing_agent = self._agent_repo.get_agent_by_id(db, agent_id)
        if not existing_agent:
            raise NotFoundException("Agent not found", ErrorCode.AGENT_NOT_FOUND)
        if existing_agent.user_id != user_id:
            raise PermissionDeniedException("No permission to delete this agent")

        success = self._agent_repo.delete_agent(db, agent_id)
        if not success:
            raise BizException(ErrorCode.AGENT_DELETE_FAILED, "Failed to delete agent")
        return True


# 创建默认实例供导入使用
agent_service = AgentService(AgentRepository())
