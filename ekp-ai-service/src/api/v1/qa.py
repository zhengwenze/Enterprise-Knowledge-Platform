from fastapi import APIRouter
from typing import List, Optional
from pydantic import BaseModel

router = APIRouter()


class QARequest(BaseModel):
    question: str
    document_ids: Optional[List[int]] = None
    top_k: int = 5


class QAResponse(BaseModel):
    session_id: int
    question: str
    answer: str
    sources: List[dict]


class QAHistoryResponse(BaseModel):
    sessions: List[QAResponse]
    total: int


@router.post("", response_model=QAResponse)
async def ask_question(request: QARequest):
    return QAResponse(
        session_id=1,
        question=request.question,
        answer="This is a placeholder answer. The RAG pipeline will be implemented.",
        sources=[],
    )


@router.get("/{session_id}", response_model=QAResponse)
async def get_qa_session(session_id: int):
    return QAResponse(
        session_id=session_id,
        question="Sample question",
        answer="Sample answer",
        sources=[],
    )
