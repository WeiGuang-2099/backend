"""
Conversation and message schemas
"""
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from enum import Enum


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"
    system = "system"


class ConversationCreate(BaseModel):
    agent_id: int
    title: Optional[str] = None


class ConversationResponse(BaseModel):
    id: int
    agent_id: int
    user_id: int
    title: Optional[str]
    is_active: bool
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    model_config = {"from_attributes": True}


class MessageResponse(BaseModel):
    id: int
    conversation_id: int
    role: MessageRole
    content: str
    tokens_used: Optional[int]
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class ChatRequest(BaseModel):
    content: str


class ConversationListRequest(BaseModel):
    agent_id: Optional[int] = None
    skip: int = 0
    limit: int = 50


class ConversationIdRequest(BaseModel):
    conversation_id: int
