from typing import List, Optional
from sqlalchemy.orm import Session

from src.services.embedding_service import EmbeddingService
from src.services.vector_store import VectorStore, SearchResult
from src.models.document import Document


class RetrieverService:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore(db)

    def retrieve_relevant_chunks(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
        min_score: float = 0.0,
    ) -> List[SearchResult]:
        if not query or not query.strip():
            return []

        query_embedding = self.embedding_service.embed_single_text(query)
        if not query_embedding:
            return []

        results = self.vector_store.search(
            query_embedding=query_embedding,
            top_k=top_k,
            document_ids=document_ids,
        )

        if min_score > 0:
            results = [r for r in results if r.score >= min_score]

        return results

    def retrieve_with_context(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
    ) -> dict:
        results = self.retrieve_relevant_chunks(query, top_k, document_ids)

        context_parts = []
        sources = []

        for i, result in enumerate(results):
            context_parts.append(f"[{i + 1}] {result.content}")
            sources.append(
                {
                    "chunk_id": result.chunk_id,
                    "document_id": result.document_id,
                    "document_title": result.document_title,
                    "content": result.content[:200] + "..." if len(result.content) > 200 else result.content,
                    "relevance_score": result.score,
                }
            )

        context = "\n\n".join(context_parts)

        return {
            "context": context,
            "sources": sources,
            "total_chunks": len(results),
        }

    def get_available_documents(self) -> List[dict]:
        documents = (
            self.db.query(Document)
            .filter(Document.status == "COMPLETED")
            .order_by(Document.created_at.desc())
            .all()
        )

        return [
            {
                "id": doc.id,
                "title": doc.title,
                "created_at": doc.created_at.isoformat() if doc.created_at else None,
                "vector_count": self.vector_store.get_document_vector_count(doc.id),
            }
            for doc in documents
        ]

    def search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
    ) -> List[dict]:
        results = self.retrieve_relevant_chunks(query, top_k, document_ids)
        return [
            {
                "id": r.chunk_id,
                "document_id": r.document_id,
                "document_title": r.document_title,
                "content": r.content,
                "similarity": r.score,
            }
            for r in results
        ]

    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
        keyword_weight: float = 0.3,
    ) -> List[SearchResult]:
        vector_results = self.retrieve_relevant_chunks(query, top_k * 2, document_ids)

        query_lower = query.lower()
        keyword_scores = {}

        for result in vector_results:
            content_lower = result.content.lower()
            keyword_count = content_lower.count(query_lower)
            keyword_scores[result.chunk_id] = min(keyword_count / 10, 1.0)

        for result in vector_results:
            vector_score = result.score
            keyword_score = keyword_scores.get(result.chunk_id, 0)
            result.score = (1 - keyword_weight) * vector_score + keyword_weight * keyword_score

        vector_results.sort(key=lambda x: x.score, reverse=True)

        return vector_results[:top_k]
