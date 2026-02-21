import os
import asyncio
from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.document import Document, DocumentChunk
from src.services.chunker_service import ChunkerService
from src.services.embedding_service import EmbeddingService
from src.services.vector_store import VectorStore
from src.config import settings


class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.chunker = ChunkerService()
        self.embedding_service = EmbeddingService()
        self.vector_store = VectorStore(db)

    def process_document(self, document_id: int) -> bool:
        return asyncio.run(self.process_document_async(document_id))

    async def process_document_async(self, document_id: int) -> bool:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        try:
            self._update_status(document, "PROCESSING")

            text = await self._extract_text(document.file_path)
            if not text:
                self._update_status(document, "FAILED", "无法提取文档内容")
                return False

            chunks = self.chunker.chunk_text(text)
            if not chunks:
                self._update_status(document, "FAILED", "文档分块失败")
                return False

            chunk_texts = [chunk.content for chunk in chunks]
            embeddings = self.embedding_service.embed_texts(chunk_texts)
            if not embeddings:
                self._update_status(document, "FAILED", "生成嵌入向量失败")
                return False

            db_chunks = []
            for i, chunk in enumerate(chunks):
                db_chunk = DocumentChunk(
                    document_id=document_id,
                    chunk_index=chunk.chunk_index,
                    content=chunk.content,
                    token_count=chunk.token_count,
                )
                self.db.add(db_chunk)
                db_chunks.append(db_chunk)

            self.db.commit()

            for db_chunk, embedding in zip(db_chunks, embeddings):
                self.db.refresh(db_chunk)
                self.vector_store.add_vector(
                    chunk_id=db_chunk.id,
                    document_id=document_id,
                    content=db_chunk.content,
                    embedding=embedding,
                )

            self._update_status(document, "COMPLETED")
            return True

        except Exception as e:
            error_msg = str(e)
            print(f"文档处理错误: {error_msg}")
            self._update_status(document, "FAILED", error_msg)
            return False

    async def _extract_text(self, file_path: str) -> Optional[str]:
        if not os.path.exists(file_path):
            print(f"文件不存在: {file_path}")
            return None

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return await self._extract_pdf_text(file_path)
        elif ext in [".txt", ".md"]:
            return await self._extract_text_file(file_path)
        else:
            print(f"不支持的文件格式: {ext}")
            return None

    async def _extract_pdf_text(self, file_path: str) -> Optional[str]:
        try:
            from pypdf import PdfReader

            reader = PdfReader(file_path)
            text_parts = []
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    text_parts.append(text)

            return "\n\n".join(text_parts)
        except Exception as e:
            print(f"PDF解析错误: {e}")
            return None

    async def _extract_text_file(self, file_path: str) -> Optional[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            print(f"文本文件读取错误: {e}")
            return None

    def _update_status(
        self, document: Document, status: str, error_message: Optional[str] = None
    ) -> None:
        document.status = status
        if error_message:
            document.error_message = error_message
        self.db.commit()

    def get_document_chunks(self, document_id: int) -> List[DocumentChunk]:
        return (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .all()
        )

    def delete_document_chunks(self, document_id: int) -> int:
        self.vector_store.delete_document_vectors(document_id)
        deleted = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .delete()
        )
        self.db.commit()
        return deleted
