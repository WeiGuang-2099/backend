"""
Knowledge service: document parsing, LLM extraction, graph management
"""
import json
import logging
import os
import asyncio
from typing import List, Dict, Optional
from sqlalchemy.orm import Session
from app.repositories.knowledge_repo import knowledge_repository
from app.repositories.document_repo import document_repository
from app.agent_repo.agent import AgentRepository
from app.services.llm_service import llm_service
from app.core.exceptions import NotFoundException, ErrorCode

logger = logging.getLogger(__name__)
agent_repository = AgentRepository()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

EXTRACTION_PROMPT = """You are a knowledge graph construction assistant. Extract entities and their relationships from the following text.

Output strict JSON only (no markdown, no explanation):
{
  "entities": [
    {{"name": "entity name", "type": "Person|Organization|Technology|Concept|Event|Location", "description": "brief description"}}
  ],
  "relations": [
    {{"from": "source entity name", "to": "target entity name", "relation": "relationship type", "description": "relationship description"}}
  ]
}

Text:
{content}"""


def asyncio_run(coro):
    """Run async coroutine synchronously."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


class KnowledgeService:

    def upload_document(self, db: Session, agent_id: int, user_id: int, filename: str, content: bytes) -> dict:
        """Upload and process a document."""
        # Validate agent ownership
        agent = agent_repository.get_agent_by_id(db, agent_id)
        if not agent or agent.user_id != user_id:
            raise NotFoundException("Agent not found", ErrorCode.AGENT_NOT_FOUND)

        file_size = len(content)

        # Save to MySQL
        doc = document_repository.create(db, agent_id, user_id, filename, file_size)

        # Save file to disk
        file_path = os.path.join(UPLOAD_DIR, f"{doc.id}_{filename}")
        with open(file_path, "wb") as f:
            f.write(content)

        # Process asynchronously (in background for now, synchronous for simplicity)
        try:
            text = content.decode("utf-8")
            entity_count = self._process_document(db, doc.id, agent_id, text)
            document_repository.update_status(db, doc.id, "completed", entity_count)
        except Exception as e:
            logger.error(f"Failed to process document {doc.id}: {e}")
            document_repository.update_status(db, doc.id, "failed", 0)

        doc = document_repository.get_by_id(db, doc.id)
        return {"id": doc.id, "filename": doc.filename, "status": doc.status, "entity_count": doc.entity_count}

    def _process_document(self, db: Session, doc_id: int, agent_id: int, text: str) -> int:
        """Split text into chunks and extract entities/relations via LLM."""
        chunks = self._split_text(text, chunk_size=800)
        all_entities = []
        all_relations = []

        for chunk in chunks:
            try:
                result = self._extract_with_llm(chunk)
                all_entities.extend(result.get("entities", []))
                all_relations.extend(result.get("relations", []))
            except Exception as e:
                logger.warning(f"LLM extraction failed for chunk in doc {doc_id}: {e}")
                continue

        # Deduplicate entities by name
        seen = set()
        unique_entities = []
        for e in all_entities:
            key = e["name"].lower().strip()
            if key not in seen:
                seen.add(key)
                unique_entities.append(e)

        # Store in Neo4j
        if unique_entities:
            count = knowledge_repository.store_entities_and_relations(
                document_id=doc_id,
                agent_id=agent_id,
                entities=unique_entities,
                relations=all_relations,
            )
            return count
        return 0

    def _split_text(self, text: str, chunk_size: int = 800) -> List[str]:
        """Split text into chunks by paragraphs."""
        paragraphs = text.split("\n\n")
        chunks = []
        current_chunk = ""

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            if len(current_chunk) + len(para) > chunk_size and current_chunk:
                chunks.append(current_chunk.strip())
                current_chunk = para
            else:
                current_chunk += "\n\n" + para if current_chunk else para

        if current_chunk.strip():
            chunks.append(current_chunk.strip())

        return chunks if chunks else [text[:chunk_size]]

    def _extract_with_llm(self, content: str) -> dict:
        """Call LLM to extract entities and relations from text."""
        prompt = EXTRACTION_PROMPT.format(content=content)
        response = asyncio_run(llm_service.chat(
            system_prompt="You are a knowledge graph construction assistant. Always respond with valid JSON only.",
            history=[],
            user_message=prompt,
            temperature=0.1,
            max_tokens=2000,
        ))
        # Parse JSON from response (handle markdown code blocks)
        response = response.strip()
        if response.startswith("```"):
            response = response.split("```")[1]
            if response.startswith("json"):
                response = response[4:]
            response = response.strip()
        return json.loads(response)

    def get_documents(self, db: Session, agent_id: int, user_id: int, skip: int = 0, limit: int = 50) -> list:
        return document_repository.get_by_agent(db, agent_id, user_id, skip, limit)

    def delete_document(self, db: Session, doc_id: int, user_id: int) -> bool:
        doc = document_repository.get_by_id(db, doc_id)
        if not doc or doc.user_id != user_id:
            raise NotFoundException("Document not found", ErrorCode.PARAM_ERROR)
        # Clean up Neo4j
        knowledge_repository.delete_document_data(doc_id)
        # Clean up file
        file_path = os.path.join(UPLOAD_DIR, f"{doc_id}_{doc.filename}")
        if os.path.exists(file_path):
            os.remove(file_path)
        return document_repository.delete(db, doc_id)

    def get_graph(self, agent_id: int) -> dict:
        return knowledge_repository.get_graph_data(agent_id)

    def search_entities(self, agent_id: int, query: str) -> list:
        return knowledge_repository.search_entities(agent_id, query)


knowledge_service = KnowledgeService()
