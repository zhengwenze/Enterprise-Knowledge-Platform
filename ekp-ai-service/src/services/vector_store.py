from typing import List, Optional, Dict, Any
from dataclasses import dataclass
from sqlalchemy import text
from sqlalchemy.orm import Session
import numpy as np

from src.models.document import DocumentVector, DocumentChunk
from src.services.embedding_service import EmbeddingService
from src.config import settings


@dataclass
class SearchResult:
    chunk_id: int
    document_id: int
    content: str
    score: float
    document_title: Optional[str] = None


class VectorStore:
    def __init__(self, db: Session):
        self.db = db
        self.embedding_service = EmbeddingService()

    def add_vectors(
        self,
        document_id: int,
        chunks: List[DocumentChunk],
        embeddings: List[List[float]],
    ) -> int:
        if len(chunks) != len(embeddings):
            raise ValueError("chunks和embeddings数量不匹配")

        added_count = 0
        for chunk, embedding in zip(chunks, embeddings):
            vector = DocumentVector(
                document_id=document_id,
                chunk_id=chunk.id,
                content=chunk.content,
                embedding=embedding,
            )
            self.db.add(vector)
            added_count += 1

        self.db.commit()
        return added_count

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
    ) -> List[SearchResult]:
        query_vector = np.array(query_embedding)

        sql = """
            SELECT 
                dv.id,
                dv.document_id,
                dv.chunk_id,
                dv.content,
                dv.embedding,
                d.title as document_title
            FROM document_vectors dv
            LEFT JOIN documents d ON dv.document_id = d.id
        """

        if document_ids:
            placeholders = ",".join([f":id{i}" for i in range(len(document_ids))])
            sql += f" WHERE dv.document_id IN ({placeholders})"

        sql += " ORDER BY dv.embedding <=> :query_vector LIMIT :limit"

        params = {"query_vector": query_vector.tolist(), "limit": top_k}
        if document_ids:
            for i, doc_id in enumerate(document_ids):
                params[f"id{i}"] = doc_id

        try:
            results = self.db.execute(text(sql), params)
            search_results = []

            for row in results:
                search_results.append(
                    SearchResult(
                        chunk_id=row.chunk_id,
                        document_id=row.document_id,
                        content=row.content,
                        score=1 - float(row.score) if row.score else 0.0,
                        document_title=row.document_title,
                    )
                )

            return search_results
        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []

    def search_by_text(
        self,
        query: str,
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
    ) -> List[SearchResult]:
        query_embedding = self.embedding_service.embed_single_text(query)
        if not query_embedding:
            return []

        return self.search(query_embedding, top_k, document_ids)

    def delete_document_vectors(self, document_id: int) -> int:
        deleted = (
            self.db.query(DocumentVector)
            .filter(DocumentVector.document_id == document_id)
            .delete()
        )
        self.db.commit()
        return deleted

    def get_document_vector_count(self, document_id: int) -> int:
        return (
            self.db.query(DocumentVector)
            .filter(DocumentVector.document_id == document_id)
            .count()
        )

    def get_all_document_ids(self) -> List[int]:
        results = self.db.query(DocumentVector.document_id).distinct().all()
        return [r[0] for r in results]
