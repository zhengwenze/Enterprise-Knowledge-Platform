import os
import asyncio
from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.document import Document, DocumentChunk
from src.services.rag_anything_service import rag_anything_service
from src.config import settings


class DocumentProcessor:
    def __init__(self, db: Session):
        self.db = db

    def process_document(self, document_id: int) -> bool:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        try:
            self._update_status(document, "PROCESSING")

            result = asyncio.run(self._process_with_rag_anything(document.file_path))

            if result.get("status") != "success":
                error_msg = result.get("error", "文档处理失败")
                self._update_status(document, "FAILED", error_msg)
                return False

            self._update_status(document, "COMPLETED")
            return True

        except Exception as e:
            error_msg = str(e)
            print(f"文档处理错误: {error_msg}")
            self._update_status(document, "FAILED", error_msg)
            return False

    async def _process_with_rag_anything(self, file_path: str) -> dict:
        output_dir = os.path.join(settings.rag_working_dir, "output")
        os.makedirs(output_dir, exist_ok=True)

        result = await rag_anything_service.process_document(
            file_path=file_path,
            output_dir=output_dir,
            parse_method=settings.rag_parse_method,
        )

        return result

    async def process_document_async(self, document_id: int) -> bool:
        document = self.db.query(Document).filter(Document.id == document_id).first()
        if not document:
            return False

        try:
            self._update_status(document, "PROCESSING")

            result = await self._process_with_rag_anything(document.file_path)

            if result.get("status") != "success":
                error_msg = result.get("error", "文档处理失败")
                self._update_status(document, "FAILED", error_msg)
                return False

            self._update_status(document, "COMPLETED")
            return True

        except Exception as e:
            error_msg = str(e)
            print(f"文档处理错误: {error_msg}")
            self._update_status(document, "FAILED", error_msg)
            return False

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
