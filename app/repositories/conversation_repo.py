"""
Conversation CRUD operations
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.schemas.conversation import MessageRole
from app.models.conversation import Conversation, Message
from app.schemas.conversation import ConversationCreate


class ConversationRepository:
    def get_conversation_by_id(self, db: Session, conversation_id: int) -> Optional[Conversation]:
        return db.query(Conversation).filter(Conversation.id == conversation_id).first()

    def get_conversations_by_agent(self, db: Session, agent_id: int, user_id: int, skip: int = 0, limit: int = 50) -> List[Conversation]:
        return (
            db.query(Conversation)
            .filter(Conversation.agent_id == agent_id, Conversation.user_id == user_id, Conversation.is_active == True)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def get_conversations_by_user(self, db: Session, user_id: int, skip: int = 0, limit: int = 50) -> List[Conversation]:
        return (
            db.query(Conversation)
            .filter(Conversation.user_id == user_id, Conversation.is_active == True)
            .order_by(Conversation.updated_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create_conversation(self, db: Session, conv_create: ConversationCreate, user_id: int) -> Conversation:
        conv = Conversation(
            agent_id=conv_create.agent_id,
            user_id=user_id,
            title=conv_create.title,
        )
        db.add(conv)
        db.commit()
        db.refresh(conv)
        return conv

    def delete_conversation(self, db: Session, conversation_id: int) -> bool:
        conv = self.get_conversation_by_id(db, conversation_id)
        if not conv:
            return False
        conv.is_active = False
        db.commit()
        return True

    def get_messages(self, db: Session, conversation_id: int, skip: int = 0, limit: int = 100) -> List[Message]:
        return (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.asc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def add_message(self, db: Session, conversation_id: int, role: str, content: str, tokens_used: Optional[int] = None) -> Message:
        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            tokens_used=tokens_used,
        )
        db.add(msg)
        db.commit()
        db.refresh(msg)
        return msg

    def update_conversation_title(self, db: Session, conversation_id: int, title: str) -> Optional[Conversation]:
        conv = self.get_conversation_by_id(db, conversation_id)
        if not conv:
            return None
        conv.title = title
        db.commit()
        db.refresh(conv)
        return conv


conversation_repository = ConversationRepository()
