"""
Agent CRUD 操作
"""
from sqlalchemy.orm import Session
from app.models.agent import Agent
from app.schemas.agent import AgentCreate, AgentUpdate
from typing import Optional, List


def get_agent_by_id(db: Session, agent_id: int) -> Optional[Agent]:
    """根据 ID 获取数字人"""
    return db.query(Agent).filter(Agent.id == agent_id).first()


def get_agents_by_user_id(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[Agent]:
    """根据用户ID获取数字人列表"""
    return db.query(Agent).filter(Agent.user_id == user_id).offset(skip).limit(limit).all()


def get_all_agents(db: Session, skip: int = 0, limit: int = 100) -> List[Agent]:
    """获取所有数字人"""
    return db.query(Agent).offset(skip).limit(limit).all()


def count_agents_by_user_id(db: Session, user_id: int) -> int:
    """统计用户的数字人数量"""
    return db.query(Agent).filter(Agent.user_id == user_id).count()


def create_agent(db: Session, agent: AgentCreate, user_id: int) -> Agent:
    """创建数字人"""
    db_agent = Agent(
        user_id=user_id,
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
        is_active=agent.is_active
    )
    db.add(db_agent)
    db.commit()
    db.refresh(db_agent)
    return db_agent


def update_agent(db: Session, agent_id: int, agent_update: AgentUpdate) -> Optional[Agent]:
    """更新数字人"""
    db_agent = get_agent_by_id(db, agent_id)
    if not db_agent:
        return None

    update_data = agent_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_agent, field, value)

    db.commit()
    db.refresh(db_agent)
    return db_agent


def delete_agent(db: Session, agent_id: int) -> bool:
    """删除数字人"""
    db_agent = get_agent_by_id(db, agent_id)
    if not db_agent:
        return False

    db.delete(db_agent)
    db.commit()
    return True
