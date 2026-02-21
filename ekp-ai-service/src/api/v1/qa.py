from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel
import asyncio

from src.services.llm_service import LLMService
from src.services.retriever_service import RetrieverService
from src.database import SyncSessionLocal

router = APIRouter()


class QARequest(BaseModel):
    question: str
    document_ids: Optional[List[int]] = None
    top_k: int = 5


class QASource(BaseModel):
    chunk_id: int
    document_id: int
    document_title: Optional[str] = None
    content: str
    relevance_score: float


class QAResponse(BaseModel):
    session_id: int
    question: str
    answer: str
    sources: List[QASource]
    model_used: Optional[str] = None
    tokens_used: int = 0
    response_time_ms: int = 0


class QAHistoryResponse(BaseModel):
    sessions: List[QAResponse]
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


def get_llm_service(db=Depends(get_db)) -> LLMService:
    return LLMService(db)


def get_retriever_service(db=Depends(get_db)) -> RetrieverService:
    return RetrieverService(db)


@router.post("", response_model=QAResponse)
async def ask_question(
    request: QARequest,
    llm_service: LLMService = Depends(get_llm_service),
    retriever_service: RetrieverService = Depends(get_retriever_service),
):
    if not request.question or not request.question.strip():
        raise HTTPException(status_code=400, detail="问题不能为空")

    context = ""
    sources = []
    
    try:
        chunks = retriever_service.search(
            query=request.question,
            top_k=request.top_k,
            document_ids=request.document_ids,
        )
        
        if chunks:
            context_parts = []
            for chunk in chunks:
                context_parts.append(chunk.get("content", ""))
                sources.append({
                    "chunk_id": chunk.get("id", 0),
                    "document_id": chunk.get("document_id", 0),
                    "document_title": chunk.get("document_title"),
                    "content": chunk.get("content", "")[:200] + "...",
                    "relevance_score": chunk.get("similarity", 0.0),
                })
            context = "\n\n---\n\n".join(context_parts)
    except Exception as e:
        print(f"检索失败: {e}")

    result = await llm_service.generate_answer_async(
        question=request.question,
        context=context,
        document_ids=request.document_ids,
        top_k=request.top_k,
    )

    session = llm_service.save_qa_session(
        question=request.question,
        answer=result["answer"],
        sources=sources,
        model_used=result.get("model_used"),
        tokens_used=result.get("tokens_used", 0),
        response_time_ms=result.get("response_time_ms", 0),
    )

    qa_sources = [
        QASource(
            chunk_id=s.get("chunk_id", 0),
            document_id=s.get("document_id", 0),
            document_title=s.get("document_title"),
            content=s.get("content", ""),
            relevance_score=s.get("relevance_score", 0.0),
        )
        for s in sources
    ]

    return QAResponse(
        session_id=session.id if session else 0,
        question=request.question,
        answer=result["answer"],
        sources=qa_sources,
        model_used=result.get("model_used"),
        tokens_used=result.get("tokens_used", 0),
        response_time_ms=result.get("response_time_ms", 0),
    )


@router.get("/{session_id}", response_model=QAResponse)
async def get_qa_session(
    session_id: int,
    llm_service: LLMService = Depends(get_llm_service),
):
    from src.models.document import QASession, QASource

    session = llm_service.db.query(QASession).filter(QASession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="问答会话不存在")

    sources = (
        llm_service.db.query(QASource).filter(QASource.session_id == session_id).all()
    )

    return QAResponse(
        session_id=session.id,
        question=session.question,
        answer=session.answer or "",
        sources=[
            QASource(
                chunk_id=s.chunk_id,
                document_id=0,
                content="",
                relevance_score=s.relevance_score or 0.0,
            )
            for s in sources
        ],
        model_used=session.model_used,
        tokens_used=session.tokens_used or 0,
        response_time_ms=session.response_time_ms or 0,
    )


@router.get("/history/list", response_model=QAHistoryResponse)
async def get_qa_history(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    document_id: Optional[int] = Query(None),
    llm_service: LLMService = Depends(get_llm_service),
):
    from src.models.document import QASession

    sessions = llm_service.get_qa_history(
        document_id=document_id,
        limit=limit,
        offset=skip,
    )

    total = llm_service.db.query(QASession).count()

    return QAHistoryResponse(
        sessions=[
            QAResponse(
                session_id=s.id,
                question=s.question,
                answer=s.answer or "",
                sources=[],
                model_used=s.model_used,
                tokens_used=s.tokens_used or 0,
                response_time_ms=s.response_time_ms or 0,
            )
            for s in sessions
        ],
        total=total,
    )
