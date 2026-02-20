import os
from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.document import Document, DocumentChunk
from src.services.chunker_service import ChunkerService, TextChunk
from src.config import settings


class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db
        self.chunker = ChunkerService()

    def process_document(self, document_id: int) -> bool:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        try:
            self._update_status(document, "PROCESSING")

            text = self._extract_text(document.file_path)
            if not text:
                self._update_status(document, "FAILED", "无法提取文档内容")
                return False

            chunks = self.chunker.chunk_text(text)
            if not chunks:
                self._update_status(document, "FAILED", "文档内容为空或无法分块")
                return False

            self._save_chunks(document, chunks)

            self._update_status(document, "COMPLETED")
            return True

        except Exception as e:
            self._update_status(document, "FAILED", str(e))
            return False

    def _extract_text(self, file_path: str) -> Optional[str]:
        if not os.path.exists(file_path):
            return None

        ext = os.path.splitext(file_path)[1].lower()

        if ext == ".pdf":
            return self._extract_pdf_text(file_path)
        elif ext == ".txt":
            return self._extract_txt_text(file_path)
        elif ext == ".md":
            return self._extract_txt_text(file_path)
        else:
            return None

    def _extract_pdf_text(self, file_path: str) -> Optional[str]:
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

    def _extract_txt_text(self, file_path: str) -> Optional[str]:
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read()
        except UnicodeDecodeError:
            try:
                with open(file_path, "r", encoding="gbk") as f:
                    return f.read()
            except Exception as e:
                print(f"文本解析错误: {e}")
                return None
        except Exception as e:
            print(f"文件读取错误: {e}")
            return None

    def _save_chunks(self, document: Document, chunks: List[TextChunk]) -> None:
        for chunk in chunks:
            db_chunk = DocumentChunk(
                document_id=document.id,
                content=chunk.content,
                chunk_index=chunk.chunk_index,
                token_count=chunk.token_count,
            )
            self.db.add(db_chunk)
        self.db.commit()

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
        deleted = (
            self.db.query(DocumentChunk)
            .filter(DocumentChunk.document_id == document_id)
            .delete()
        )
        self.db.commit()
        return deleted
