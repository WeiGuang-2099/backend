"""
Chat service: orchestrates conversation management and LLM calls
"""
import logging
from typing import List, AsyncGenerator, Optional
from sqlalchemy.orm import Session
from app.repositories.conversation_repo import conversation_repository
from app.services.llm_service import llm_service
from app.schemas.conversation import ConversationCreate, ConversationResponse, MessageResponse
from app.agent_repo.agent import AgentRepository
from app.core.exceptions import NotFoundException, ErrorCode

logger = logging.getLogger(__name__)
agent_repository = AgentRepository()


class ChatService:

    def create_conversation(self, db: Session, conv_create: ConversationCreate, user_id: int) -> ConversationResponse:
        # Verify agent exists and belongs to user
        agent = agent_repository.get_agent_by_id(db, conv_create.agent_id)
        if not agent:
            raise NotFoundException("Agent not found", ErrorCode.AGENT_NOT_FOUND)
        if agent.user_id != user_id:
            raise NotFoundException("Agent not found", ErrorCode.AGENT_NOT_FOUND)

        conv = conversation_repository.create_conversation(db, conv_create, user_id)
        return ConversationResponse.model_validate(conv)

    def get_conversations(self, db: Session, agent_id: Optional[int], user_id: int, skip: int = 0, limit: int = 50) -> List[ConversationResponse]:
        if agent_id:
            convs = conversation_repository.get_conversations_by_agent(db, agent_id, user_id, skip, limit)
        else:
            convs = conversation_repository.get_conversations_by_user(db, user_id, skip, limit)
        return [ConversationResponse.model_validate(c) for c in convs]

    def get_messages(self, db: Session, conversation_id: int, user_id: int) -> List[MessageResponse]:
        # Authorization check: conversation must belong to user
        conv = conversation_repository.get_conversation_by_id(db, conversation_id)
        if not conv or conv.user_id != user_id:
            raise NotFoundException("Conversation not found", ErrorCode.PARAM_ERROR)
        messages = conversation_repository.get_messages(db, conversation_id)
        return [MessageResponse.model_validate(m) for m in messages]

    def delete_conversation(self, db: Session, conversation_id: int, user_id: int) -> bool:
        conv = conversation_repository.get_conversation_by_id(db, conversation_id)
        if not conv or conv.user_id != user_id:
            raise NotFoundException("Conversation not found", ErrorCode.PARAM_ERROR)
        return conversation_repository.delete_conversation(db, conversation_id)

    def validate_stream_request(self, db: Session, conversation_id: int, user_id: int):
        """Pre-flight validation for streaming. Raises proper HTTP exceptions before SSE starts."""
        conv = conversation_repository.get_conversation_by_id(db, conversation_id)
        if not conv or conv.user_id != user_id:
            raise NotFoundException("Conversation not found", ErrorCode.PARAM_ERROR)
        agent = agent_repository.get_agent_by_id(db, conv.agent_id)
        if not agent:
            raise NotFoundException("Agent not found", ErrorCode.AGENT_NOT_FOUND)

    async def stream_chat(
        self,
        db: Session,
        conversation_id: int,
        user_id: int,
        user_message: str,
    ) -> AsyncGenerator[str, None]:
        """Stream chat response and persist messages."""
        # Validate conversation
        conv = conversation_repository.get_conversation_by_id(db, conversation_id)
        if not conv or conv.user_id != user_id:
            raise NotFoundException("Conversation not found", ErrorCode.PARAM_ERROR)

        # Get agent config
        agent = agent_repository.get_agent_by_id(db, conv.agent_id)
        if not agent:
            raise NotFoundException("Agent not found", ErrorCode.AGENT_NOT_FOUND)

        # Auto-title on first message
        if not conv.title:
            title = user_message[:20] + ("..." if len(user_message) > 20 else "")
            conversation_repository.update_conversation_title(db, conversation_id, title)

        # Save user message
        conversation_repository.add_message(db, conversation_id, "user", user_message)

        # Build history from existing messages only (exclude the one we just saved)
        history_msgs = conversation_repository.get_messages(db, conversation_id)
        history = [{"role": m.role, "content": m.content} for m in history_msgs[:-1]]

        # Stream response with disconnect protection
        full_response = ""
        try:
            async for token in llm_service.stream_chat(
                system_prompt=agent.system_prompt or f"You are {agent.name}, a helpful AI assistant.",
                history=history,
                user_message=user_message,
                temperature=agent.temperature or 0.7,
                max_tokens=agent.max_tokens or 2048,
            ):
                full_response += token
                yield token
        finally:
            # Persist whatever response we got (full or partial) even on disconnect
            if full_response:
                try:
                    conversation_repository.add_message(db, conversation_id, "assistant", full_response)
                except Exception as e:
                    logger.error(f"Failed to persist response for conversation {conversation_id}: {e}")


chat_service = ChatService()
