from typing import List, Optional
from dataclasses import dataclass
from sqlalchemy.orm import Session
import psycopg2
from psycopg2 import sql

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
        self._conn = None

    def _get_connection(self):
        if self._conn is None or self._conn.closed:
            db_url = settings.database_url
            self._conn = psycopg2.connect(db_url)
        return self._conn

    def add_vector(
        self,
        chunk_id: int,
        document_id: int,
        content: str,
        embedding: List[float],
    ) -> Optional[dict]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        try:
            cursor.execute("""
                INSERT INTO document_vectors (document_id, chunk_id, content, embedding)
                VALUES (%s, %s, %s, %s::vector)
                RETURNING id, document_id, chunk_id, content, created_at
            """, (document_id, chunk_id, content, embedding_str))
            
            result = cursor.fetchone()
            conn.commit()
            return {
                "id": result[0],
                "document_id": result[1],
                "chunk_id": result[2],
                "content": result[3],
                "created_at": result[4]
            }
        except Exception as e:
            print(f"添加向量失败: {e}")
            conn.rollback()
            return None
        finally:
            cursor.close()

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
            result = self.add_vector(
                chunk_id=chunk.id,
                document_id=document_id,
                content=chunk.content,
                embedding=embedding,
            )
            if result:
                added_count += 1

        return added_count

    def search(
        self,
        query_embedding: List[float],
        top_k: int = 5,
        document_ids: Optional[List[int]] = None,
    ) -> List[SearchResult]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        embedding_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
        
        try:
            if document_ids:
                cursor.execute("""
                    SELECT 
                        dv.id,
                        dv.document_id,
                        dv.chunk_id,
                        dv.content,
                        1 - (dv.embedding <=> %s::vector) as score,
                        d.title as document_title
                    FROM document_vectors dv
                    LEFT JOIN documents d ON dv.document_id = d.id
                    WHERE dv.document_id = ANY(%s)
                    ORDER BY dv.embedding <=> %s::vector
                    LIMIT %s
                """, (embedding_str, document_ids, embedding_str, top_k))
            else:
                cursor.execute("""
                    SELECT 
                        dv.id,
                        dv.document_id,
                        dv.chunk_id,
                        dv.content,
                        1 - (dv.embedding <=> %s::vector) as score,
                        d.title as document_title
                    FROM document_vectors dv
                    LEFT JOIN documents d ON dv.document_id = d.id
                    ORDER BY dv.embedding <=> %s::vector
                    LIMIT %s
                """, (embedding_str, embedding_str, top_k))
            
            search_results = []
            for row in cursor.fetchall():
                search_results.append(
                    SearchResult(
                        chunk_id=row[2],
                        document_id=row[1],
                        content=row[3],
                        score=float(row[4]) if row[4] else 0.0,
                        document_title=row[5],
                    )
                )

            return search_results
        except Exception as e:
            print(f"向量搜索失败: {e}")
            return []
        finally:
            cursor.close()

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
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "DELETE FROM document_vectors WHERE document_id = %s",
                (document_id,)
            )
            deleted = cursor.rowcount
            conn.commit()
            return deleted
        except Exception as e:
            print(f"删除向量失败: {e}")
            conn.rollback()
            return 0
        finally:
            cursor.close()

    def get_document_vector_count(self, document_id: int) -> int:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "SELECT COUNT(*) FROM document_vectors WHERE document_id = %s",
                (document_id,)
            )
            return cursor.fetchone()[0]
        finally:
            cursor.close()

    def get_all_document_ids(self) -> List[int]:
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT DISTINCT document_id FROM document_vectors")
            return [row[0] for row in cursor.fetchall()]
        finally:
            cursor.close()
