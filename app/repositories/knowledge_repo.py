"""
Neo4j knowledge graph repository
"""
import os
import logging
from typing import List, Dict, Optional
from neo4j import GraphDatabase

logger = logging.getLogger(__name__)


class KnowledgeRepository:
    def __init__(self):
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "knowledge_graph_password")
        self._driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self._driver.close()

    def _get_session(self):
        return self._driver.session()

    def store_entities_and_relations(
        self,
        document_id: int,
        agent_id: int,
        entities: List[Dict],
        relations: List[Dict],
    ) -> int:
        """Store extracted entities and relations. Returns count of entities stored."""
        entity_count = 0
        with self._get_session() as session:
            # Create document node
            session.run(
                "MERGE (d:Document {id: $doc_id}) SET d.agent_id = $agent_id",
                doc_id=document_id,
                agent_id=agent_id,
            )

            # Create entity nodes
            for entity in entities:
                session.run(
                    """
                    MERGE (e:Entity {name: $name, document_id: $doc_id})
                    SET e.type = $type, e.description = $desc, e.agent_id = $agent_id
                    WITH e
                    MATCH (d:Document {id: $doc_id})
                    MERGE (d)-[:CONTAINS]->(e)
                    """,
                    name=entity["name"],
                    type=entity.get("type", "Concept"),
                    desc=entity.get("description", ""),
                    doc_id=document_id,
                    agent_id=agent_id,
                )
                entity_count += 1

            # Create relationships
            for rel in relations:
                session.run(
                    """
                    MATCH (e1:Entity {name: $from_name, document_id: $doc_id})
                    MATCH (e2:Entity {name: $to_name, document_id: $doc_id})
                    MERGE (e1)-[:RELATED_TO {relation: $relation, description: $desc}]->(e2)
                    """,
                    from_name=rel["from"],
                    to_name=rel["to"],
                    relation=rel.get("relation", "RELATED_TO"),
                    desc=rel.get("description", ""),
                    doc_id=document_id,
                )

        return entity_count

    def get_graph_data(self, agent_id: int) -> Dict:
        """Get all nodes and edges for an agent's knowledge graph."""
        nodes = []
        edges = []

        with self._get_session() as session:
            # Get all entities for this agent
            result = session.run(
                "MATCH (e:Entity {agent_id: $agent_id}) RETURN e.name AS name, e.type AS type, e.description AS description, e.document_id AS doc_id",
                agent_id=agent_id,
            )
            seen = set()
            for record in result:
                name = record["name"]
                if name not in seen:
                    nodes.append({
                        "id": name,
                        "name": name,
                        "type": record["type"] or "Concept",
                        "description": record["description"],
                    })
                    seen.add(name)

            # Get all relations for this agent
            result = session.run(
                """
                MATCH (e1:Entity {agent_id: $agent_id})-[r:RELATED_TO]->(e2:Entity {agent_id: $agent_id})
                RETURN e1.name AS source, e2.name AS target, r.relation AS relation, r.description AS description
                """,
                agent_id=agent_id,
            )
            for record in result:
                edges.append({
                    "source": record["source"],
                    "target": record["target"],
                    "relation": record["relation"],
                    "description": record["description"],
                })

        return {"nodes": nodes, "edges": edges}

    def search_entities(self, agent_id: int, query: str) -> List[Dict]:
        """Search entities by name (case-insensitive partial match)."""
        with self._get_session() as session:
            result = session.run(
                """
                MATCH (e:Entity {agent_id: $agent_id})
                WHERE e.name CONTAINS $query
                RETURN e.name AS name, e.type AS type, e.description AS description
                LIMIT 20
                """,
                agent_id=agent_id,
                query=query,
            )
            return [{"id": r["name"], "name": r["name"], "type": r["type"], "description": r["description"]} for r in result]

    def delete_document_data(self, document_id: int) -> bool:
        """Delete all entities and relations for a document."""
        with self._get_session() as session:
            session.run(
                """
                MATCH (e:Entity {document_id: $doc_id})
                DETACH DELETE e
                """,
                doc_id=document_id,
            )
            session.run(
                "MATCH (d:Document {id: $doc_id}) DELETE d",
                doc_id=document_id,
            )
        return True


knowledge_repository = KnowledgeRepository()
