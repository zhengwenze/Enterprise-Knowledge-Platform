import os
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
from pydantic import BaseModel
from datetime import datetime

from src.services.document_service import DocumentService
from src.services.document_processor import DocumentProcessor
from src.database import SyncSessionLocal

router = APIRouter()


class DocumentResponse(BaseModel):
    id: int
    title: str
    status: str
    created_at: str
    file_size: Optional[int] = None
    file_type: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentDetailResponse(BaseModel):
    id: int
    title: str
    status: str
    created_at: str
    file_path: Optional[str] = None
    file_size: Optional[int] = None
    file_type: Optional[str] = None
    error_message: Optional[str] = None

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


def get_db():
    db = SyncSessionLocal()
    try:
        yield db
    except Exception as e:
        db.rollback()
        raise
    finally:
        db.close()


def get_document_service(db=Depends(get_db)) -> DocumentService:
    return DocumentService(db)


@router.post("", response_model=DocumentResponse, status_code=201)
async def upload_document(
    file: UploadFile = File(...),
    service: DocumentService = Depends(get_document_service),
):
    content = await file.read()
    file_size = len(content)
    filename = file.filename or "unknown"

    is_valid, error_msg = service.validate_file(filename, file_size)
    if not is_valid:
        raise HTTPException(status_code=400, detail=error_msg)

    file_path = await service.save_upload_file(content, filename)
    file_type = os.path.splitext(filename)[1].lower()

    document = service.create_document(
        title=filename,
        file_path=file_path,
        file_size=file_size,
        file_type=file_type,
    )

    import asyncio
    async def process_document_async():
        try:
            db = SyncSessionLocal()
            processor = DocumentProcessor(db)
            await processor.process_document_async(document.id)
            db.close()
        except Exception as e:
            print(f"文档处理错误: {e}")

    asyncio.create_task(process_document_async())

    return DocumentResponse(
        id=document.id,
        title=document.title,
        status=document.status,
        created_at=document.created_at.isoformat() if document.created_at else "",
        file_size=document.file_size,
        file_type=document.file_type,
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    status: Optional[str] = Query(None),
    service: DocumentService = Depends(get_document_service),
):
    documents, total = service.list_documents(skip=skip, limit=limit, status=status)

    return DocumentListResponse(
        documents=[
            DocumentResponse(
                id=doc.id,
                title=doc.title,
                status=doc.status,
                created_at=doc.created_at.isoformat() if doc.created_at else "",
                file_size=doc.file_size,
                file_type=doc.file_type,
            )
            for doc in documents
        ],
        total=total,
    )


@router.get("/{document_id}", response_model=DocumentDetailResponse)
async def get_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
):
    document = service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="文档不存在")

    return DocumentDetailResponse(
        id=document.id,
        title=document.title,
        status=document.status,
        created_at=document.created_at.isoformat() if document.created_at else "",
        file_path=document.file_path,
        file_size=document.file_size,
        file_type=document.file_type,
        error_message=document.error_message,
    )


@router.delete("/{document_id}", status_code=204)
async def delete_document(
    document_id: int,
    service: DocumentService = Depends(get_document_service),
):
    success = service.delete_document(document_id)
    if not success:
        raise HTTPException(status_code=404, detail="文档不存在")
    return None
