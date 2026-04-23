"""
Chat API routes
"""
import json
import logging
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sse_starlette.sse import EventSourceResponse
from app.schemas.conversation import (
    ConversationCreate, ConversationResponse, ConversationListRequest,
    ConversationIdRequest, MessageResponse, ChatRequest,
)
from app.schemas.response import ApiResponse
from app.schemas.user import UserResponse
from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.chat_service import chat_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/conversations", response_model=ApiResponse[ConversationResponse])
async def create_conversation(
    conv_create: ConversationCreate,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    conv = chat_service.create_conversation(db, conv_create, current_user.id)
    return ApiResponse.success(data=conv)


@router.post("/conversations/list", response_model=ApiResponse[list[ConversationResponse]])
async def list_conversations(
    req: ConversationListRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    convs = chat_service.get_conversations(db, req.agent_id, current_user.id, req.skip, req.limit)
    return ApiResponse.success(data=convs)


@router.get("/conversations/{conversation_id}/messages", response_model=ApiResponse[list[MessageResponse]])
async def get_messages(
    conversation_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    messages = chat_service.get_messages(db, conversation_id, current_user.id)
    return ApiResponse.success(data=messages)


@router.post("/conversations/delete", response_model=ApiResponse[bool])
async def delete_conversation(
    req: ConversationIdRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = chat_service.delete_conversation(db, req.conversation_id, current_user.id)
    return ApiResponse.success(data=success)


@router.post("/conversations/{conversation_id}/stream")
async def stream_chat(
    conversation_id: int,
    chat_request: ChatRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """SSE streaming chat endpoint."""
    # Pre-flight validation: raise proper HTTP errors before entering SSE
    chat_service.validate_stream_request(db, conversation_id, current_user.id)

    async def event_generator():
        try:
            async for token in chat_service.stream_chat(
                db=db,
                conversation_id=conversation_id,
                user_id=current_user.id,
                user_message=chat_request.content,
            ):
                yield {"event": "message", "data": json.dumps({"token": token})}
            yield {"event": "done", "data": json.dumps({"status": "complete"})}
        except Exception as e:
            logger.error(f"Stream error for conversation {conversation_id}: {e}", exc_info=True)
            yield {"event": "error", "data": json.dumps({"error": "Stream interrupted"})}

    return EventSourceResponse(event_generator())
