"""
Knowledge schemas
"""
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class DocStatus(str, Enum):
    processing = "processing"
    completed = "completed"
    failed = "failed"


class KnowledgeDocumentResponse(BaseModel):
    id: int
    agent_id: int
    user_id: int
    filename: str
    file_size: int
    status: DocStatus
    entity_count: int
    created_at: Optional[datetime]

    model_config = {"from_attributes": True}


class DocumentListRequest(BaseModel):
    agent_id: int
    skip: int = Field(0, ge=0)
    limit: int = Field(50, ge=1, le=100)


class DocumentIdRequest(BaseModel):
    document_id: int


class GraphNode(BaseModel):
    id: str
    name: str
    type: str
    description: Optional[str] = None


class GraphEdge(BaseModel):
    source: str
    target: str
    relation: str
    description: Optional[str] = None


class GraphData(BaseModel):
    nodes: List[GraphNode]
    edges: List[GraphEdge]


class EntitySearchRequest(BaseModel):
    agent_id: int
    query: str = Field(..., min_length=1, max_length=200)
