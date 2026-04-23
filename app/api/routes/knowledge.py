"""
Knowledge API routes
"""
from fastapi import APIRouter, Depends, UploadFile, File, Query
from sqlalchemy.orm import Session
from app.schemas.knowledge import (
    KnowledgeDocumentResponse, DocumentListRequest, DocumentIdRequest,
    GraphData, GraphNode, EntitySearchRequest,
)
from app.schemas.response import ApiResponse
from app.schemas.user import UserResponse
from app.core.auth import get_current_user
from app.core.database import get_db
from app.services.knowledge_service import knowledge_service

router = APIRouter()

ALLOWED_EXTENSIONS = {".txt", ".md"}
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB


@router.post("/upload", response_model=ApiResponse[dict])
async def upload_document(
    agent_id: int,
    file: UploadFile = File(...),
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    # Validate file extension
    filename = file.filename or ""
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    if f".{ext}" not in ALLOWED_EXTENSIONS:
        return ApiResponse.error("Only .txt and .md files are supported")

    content = await file.read()
    if len(content) > MAX_FILE_SIZE:
        return ApiResponse.error("File size exceeds 5MB limit")

    result = knowledge_service.upload_document(db, agent_id, current_user.id, filename, content)
    return ApiResponse.success(data=result)


@router.post("/documents/list", response_model=ApiResponse[list[KnowledgeDocumentResponse]])
async def list_documents(
    req: DocumentListRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    docs = knowledge_service.get_documents(db, req.agent_id, current_user.id, req.skip, req.limit)
    return ApiResponse.success(data=[KnowledgeDocumentResponse.model_validate(d) for d in docs])


@router.post("/documents/delete", response_model=ApiResponse[bool])
async def delete_document(
    req: DocumentIdRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    success = knowledge_service.delete_document(db, req.document_id, current_user.id)
    return ApiResponse.success(data=success)


@router.get("/graph/{agent_id}", response_model=ApiResponse[GraphData])
async def get_graph(
    agent_id: int,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    data = knowledge_service.get_graph(agent_id)
    return ApiResponse.success(data=GraphData(**data))


@router.post("/graph/search", response_model=ApiResponse[list[GraphNode]])
async def search_entities(
    req: EntitySearchRequest,
    current_user: UserResponse = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    results = knowledge_service.search_entities(req.agent_id, req.query)
    return ApiResponse.success(data=[GraphNode(**r) for r in results])
