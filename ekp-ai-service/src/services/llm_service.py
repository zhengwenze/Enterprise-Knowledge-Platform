import time
import asyncio
from typing import List, Optional
from sqlalchemy.orm import Session

from src.services.rag_anything_service import rag_anything_service
from src.models.document import QASession, QASource
from src.config import settings


class LLMService:
    def __init__(self, db: Session):
        self.db = db

    def generate_answer(
        self,
        question: str,
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
        mode: str = "hybrid",
        vlm_enhanced: bool = False,
    ) -> dict:
        start_time = time.time()

        try:
            answer = asyncio.run(
                rag_anything_service.query(
                    question=question,
                    mode=mode,
                    vlm_enhanced=vlm_enhanced,
                )
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            return {
                "answer": answer,
                "sources": [],
                "model_used": settings.llm_model,
                "tokens_used": 0,
                "response_time_ms": response_time_ms,
            }

        except Exception as e:
            print(f"RAG-Anything 查询失败: {e}")
            response_time_ms = int((time.time() - start_time) * 1000)
            return {
                "answer": f"抱歉，查询时出现错误: {str(e)}",
                "sources": [],
                "model_used": "error",
                "tokens_used": 0,
                "response_time_ms": response_time_ms,
            }

    async def generate_answer_async(
        self,
        question: str,
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
        mode: str = "hybrid",
        vlm_enhanced: bool = False,
    ) -> dict:
        start_time = time.time()

        try:
            answer = await rag_anything_service.query(
                question=question,
                mode=mode,
                vlm_enhanced=vlm_enhanced,
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            return {
                "answer": answer,
                "sources": [],
                "model_used": settings.llm_model,
                "tokens_used": 0,
                "response_time_ms": response_time_ms,
            }

        except Exception as e:
            print(f"RAG-Anything 查询失败: {e}")
            response_time_ms = int((time.time() - start_time) * 1000)
            return {
                "answer": f"抱歉，查询时出现错误: {str(e)}",
                "sources": [],
                "model_used": "error",
                "tokens_used": 0,
                "response_time_ms": response_time_ms,
            }

    async def generate_answer_with_multimodal(
        self,
        question: str,
        multimodal_content: List[dict],
        mode: str = "hybrid",
    ) -> dict:
        start_time = time.time()

        try:
            answer = await rag_anything_service.query_with_multimodal(
                question=question,
                multimodal_content=multimodal_content,
                mode=mode,
            )

            response_time_ms = int((time.time() - start_time) * 1000)

            return {
                "answer": answer,
                "sources": [],
                "model_used": settings.vision_model,
                "tokens_used": 0,
                "response_time_ms": response_time_ms,
            }

        except Exception as e:
            print(f"RAG-Anything 多模态查询失败: {e}")
            response_time_ms = int((time.time() - start_time) * 1000)
            return {
                "answer": f"抱歉，多模态查询时出现错误: {str(e)}",
                "sources": [],
                "model_used": "error",
                "tokens_used": 0,
                "response_time_ms": response_time_ms,
            }

    def save_qa_session(
        self,
        question: str,
        answer: str,
        sources: List[dict],
        model_used: Optional[str] = None,
        tokens_used: int = 0,
        response_time_ms: int = 0,
        user_id: Optional[int] = None,
        document_id: Optional[int] = None,
    ) -> Optional[QASession]:
        try:
            session = QASession(
                user_id=user_id,
                document_id=document_id,
                question=question,
                answer=answer,
                model_used=model_used,
                tokens_used=tokens_used,
                response_time_ms=response_time_ms,
            )
            self.db.add(session)
            self.db.commit()
            self.db.refresh(session)

            for source in sources:
                qa_source = QASource(
                    session_id=session.id,
                    chunk_id=source.get("chunk_id"),
                    relevance_score=source.get("relevance_score"),
                )
                self.db.add(qa_source)

            self.db.commit()
            return session
        except Exception as e:
            print(f"保存QA会话失败: {e}")
            try:
                self.db.rollback()
            except:
                pass
            return None

    def get_qa_history(
        self,
        user_id: Optional[int] = None,
        document_id: Optional[int] = None,
        limit: int = 10,
        offset: int = 0,
    ) -> List[QASession]:
        query = self.db.query(QASession)

        if user_id:
            query = query.filter(QASession.user_id == user_id)
        if document_id:
            query = query.filter(QASession.document_id == document_id)

        return query.order_by(QASession.created_at.desc()).offset(offset).limit(limit).all()
