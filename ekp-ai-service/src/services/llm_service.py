import time
import asyncio
import httpx
from typing import List, Optional
from sqlalchemy.orm import Session

from src.models.document import QASession, QASource
from src.config import settings


class LLMService:
    def __init__(self, db: Session):
        self.db = db
        self.ollama_url = settings.local_llm_url
        self.model = settings.llm_model

    async def call_ollama(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
    ) -> str:
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        async with httpx.AsyncClient(timeout=120.0) as client:
            try:
                response = await client.post(
                    f"{self.ollama_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result.get("message", {}).get("content", "")
            except httpx.ConnectError:
                return "抱歉，无法连接到本地 Ollama 服务。请确保 Ollama 正在运行。"
            except httpx.HTTPStatusError as e:
                return f"抱歉，Ollama 服务返回错误: {e.response.status_code}"
            except Exception as e:
                return f"抱歉，调用本地模型时出现错误: {str(e)}"

    def generate_answer(
        self,
        question: str,
        context: str = "",
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
    ) -> dict:
        return asyncio.run(
            self.generate_answer_async(question, context, document_ids, top_k)
        )

    async def generate_answer_async(
        self,
        question: str,
        context: str = "",
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
    ) -> dict:
        start_time = time.time()

        system_prompt = """你是一个企业知识库助手。请根据提供的知识库内容回答用户问题。
如果知识库中没有相关信息，请明确告知用户，不要编造答案。
回答要简洁、准确、专业。"""

        if context:
            prompt = f"""请根据以下知识库内容回答问题。

知识库内容：
{context}

用户问题：{question}

请给出准确、专业的回答："""
        else:
            prompt = f"""用户问题：{question}

知识库中没有找到相关内容。请告知用户并建议他们上传相关文档或换一种方式提问。"""

        answer = await self.call_ollama(prompt, system_prompt)

        response_time_ms = int((time.time() - start_time) * 1000)

        return {
            "answer": answer,
            "sources": [],
            "model_used": self.model,
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
