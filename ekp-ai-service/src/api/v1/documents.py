from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List
from pydantic import BaseModel

router = APIRouter()


class DocumentResponse(BaseModel):
    id: int
    title: str
    status: str
    created_at: str


class DocumentListResponse(BaseModel):
    documents: List[DocumentResponse]
    total: int


@router.post("", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    return DocumentResponse(
        id=1,
        title=file.filename or "unknown",
        status="PENDING",
        created_at="2024-01-01T00:00:00Z",
    )


@router.get("", response_model=DocumentListResponse)
async def list_documents(skip: int = 0, limit: int = 10):
    return DocumentListResponse(documents=[], total=0)


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(document_id: int):
    return DocumentResponse(
        id=document_id,
        title="Sample Document",
        status="COMPLETED",
        created_at="2024-01-01T00:00:00Z",
    )
