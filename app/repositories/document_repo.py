"""
Knowledge document MySQL repository
"""
from typing import Optional, List
from sqlalchemy.orm import Session
from app.models.knowledge import KnowledgeDocument


class DocumentRepository:
    def get_by_id(self, db: Session, doc_id: int) -> Optional[KnowledgeDocument]:
        return db.query(KnowledgeDocument).filter(KnowledgeDocument.id == doc_id).first()

    def get_by_agent(self, db: Session, agent_id: int, user_id: int, skip: int = 0, limit: int = 50) -> List[KnowledgeDocument]:
        return (
            db.query(KnowledgeDocument)
            .filter(KnowledgeDocument.agent_id == agent_id, KnowledgeDocument.user_id == user_id)
            .order_by(KnowledgeDocument.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )

    def create(self, db: Session, agent_id: int, user_id: int, filename: str, file_size: int) -> KnowledgeDocument:
        doc = KnowledgeDocument(
            agent_id=agent_id,
            user_id=user_id,
            filename=filename,
            file_size=file_size,
            status="processing",
        )
        db.add(doc)
        db.commit()
        db.refresh(doc)
        return doc

    def update_status(self, db: Session, doc_id: int, status: str, entity_count: int = 0) -> Optional[KnowledgeDocument]:
        doc = self.get_by_id(db, doc_id)
        if not doc:
            return None
        doc.status = status
        doc.entity_count = entity_count
        db.commit()
        db.refresh(doc)
        return doc

    def delete(self, db: Session, doc_id: int) -> bool:
        doc = self.get_by_id(db, doc_id)
        if not doc:
            return False
        db.delete(doc)
        db.commit()
        return True


document_repository = DocumentRepository()
