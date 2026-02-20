import os
import uuid
from datetime import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc

from src.models.document import Document
from src.config import settings


class DocumentService:
    UPLOAD_DIR = "uploads"
    ALLOWED_EXTENSIONS = {".pdf", ".txt", ".docx", ".md"}
    MAX_FILE_SIZE = 50 * 1024 * 1024

    def __init__(self, db: Session):
        self.db = db
        self._ensure_upload_dir()

    def _ensure_upload_dir(self):
        os.makedirs(self.UPLOAD_DIR, exist_ok=True)

    def _get_file_extension(self, filename: str) -> str:
        return os.path.splitext(filename)[1].lower()

    def _generate_file_path(self, filename: str) -> str:
        ext = self._get_file_extension(filename)
        unique_name = f"{uuid.uuid4()}{ext}"
        return os.path.join(self.UPLOAD_DIR, unique_name)

    def validate_file(self, filename: str, file_size: int) -> tuple[bool, str]:
        ext = self._get_file_extension(filename)
        if ext not in self.ALLOWED_EXTENSIONS:
            return False, f"不支持的文件类型: {ext}。支持的类型: {', '.join(self.ALLOWED_EXTENSIONS)}"

        if file_size > self.MAX_FILE_SIZE:
            return False, f"文件大小超过限制: {file_size / (1024 * 1024):.2f}MB > {self.MAX_FILE_SIZE / (1024 * 1024)}MB"

        return True, ""

    async def save_upload_file(self, file_content: bytes, filename: str) -> str:
        file_path = self._generate_file_path(filename)
        with open(file_path, "wb") as f:
            f.write(file_content)
        return file_path

    def create_document(
        self,
        title: str,
        file_path: str,
        file_size: int,
        file_type: str,
        created_by: Optional[int] = None,
    ) -> Document:
        document = Document(
            title=title,
            file_path=file_path,
            file_size=file_size,
            file_type=file_type,
            status="PENDING",
            created_by=created_by,
        )
        self.db.add(document)
        self.db.commit()
        self.db.refresh(document)
        return document

    def get_document(self, document_id: int) -> Optional[Document]:
        return self.db.query(Document).filter(Document.id == document_id).first()

    def list_documents(
        self, skip: int = 0, limit: int = 10, status: Optional[str] = None
    ) -> tuple[List[Document], int]:
        query = self.db.query(Document)

        if status:
            query = query.filter(Document.status == status)

        total = query.count()
        documents = query.order_by(desc(Document.created_at)).offset(skip).limit(limit).all()

        return documents, total

    def update_document_status(
        self, document_id: int, status: str, error_message: Optional[str] = None
    ) -> Optional[Document]:
        document = self.get_document(document_id)
        if document:
            document.status = status
            if error_message:
                document.error_message = error_message
            self.db.commit()
            self.db.refresh(document)
        return document

    def delete_document(self, document_id: int) -> bool:
        document = self.get_document(document_id)
        if document:
            if document.file_path and os.path.exists(document.file_path):
                os.remove(document.file_path)
            self.db.delete(document)
            self.db.commit()
            return True
        return False
