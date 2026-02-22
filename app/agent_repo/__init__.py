"""
Agent Repository Layer - 数字人数据访问层
"""
from app.agent_repo.agent import (
    AgentRepository,
    agent_repository,
)


def get_agent_repository() -> AgentRepository:
    """获取 AgentRepository 实例的工厂函数，用于依赖注入"""
    return agent_repository


__all__ = [
    "AgentRepository",
    "agent_repository",
    "get_agent_repository",
]
