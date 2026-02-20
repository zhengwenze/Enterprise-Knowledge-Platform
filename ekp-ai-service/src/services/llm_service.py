import time
from typing import List, Optional
from sqlalchemy.orm import Session

from src.services.retriever_service import RetrieverService
from src.models.document import QASession, QASource
from src.config import settings


class LLMService:
    def __init__(self, db: Session):
        self.db = db
        self.retriever = RetrieverService(db)
        self._client = None

    def _get_client(self):
        if self._client is None:
            try:
                from openai import OpenAI

                self._client = OpenAI(api_key=settings.openai_api_key)
            except Exception as e:
                print(f"OpenAI客户端初始化失败: {e}")
                self._client = None
        return self._client

    def _build_prompt(self, question: str, context: str) -> str:
        return f"""你是一个专业的知识库问答助手。请根据以下参考资料回答用户的问题。

要求：
1. 只使用参考资料中的信息回答问题
2. 如果参考资料中没有相关信息，请明确告知用户
3. 回答要简洁、准确、有条理
4. 可以引用参考资料中的具体内容

参考资料：
{context}

用户问题：{question}

请回答："""

    def generate_answer(
        self,
        question: str,
        document_ids: Optional[List[int]] = None,
        top_k: int = 5,
        model: str = "gpt-3.5-turbo",
    ) -> dict:
        start_time = time.time()

        retrieval_result = self.retriever.retrieve_with_context(
            query=question,
            top_k=top_k,
            document_ids=document_ids,
        )

        context = retrieval_result["context"]
        sources = retrieval_result["sources"]

        if not context:
            return {
                "answer": "抱歉，我在知识库中没有找到与您问题相关的内容。请尝试换一种方式提问，或者上传相关文档。",
                "sources": [],
                "model_used": None,
                "tokens_used": 0,
                "response_time_ms": int((time.time() - start_time) * 1000),
            }

        prompt = self._build_prompt(question, context)

        client = self._get_client()
        if not client:
            answer = self._generate_fallback_answer(question, context)
            tokens_used = 0
            model_used = "fallback"
        else:
            try:
                response = client.chat.completions.create(
                    model=model,
                    messages=[
                        {
                            "role": "system",
                            "content": "你是一个专业的知识库问答助手，擅长根据提供的资料准确回答问题。",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    max_tokens=1000,
                    temperature=0.7,
                )

                answer = response.choices[0].message.content
                tokens_used = response.usage.total_tokens if response.usage else 0
                model_used = model

            except Exception as e:
                print(f"LLM调用失败: {e}")
                answer = self._generate_fallback_answer(question, context)
                tokens_used = 0
                model_used = "fallback"

        response_time_ms = int((time.time() - start_time) * 1000)

        return {
            "answer": answer,
            "sources": sources,
            "model_used": model_used,
            "tokens_used": tokens_used,
            "response_time_ms": response_time_ms,
        }

    def _generate_fallback_answer(self, question: str, context: str) -> str:
        return f"根据知识库中的相关内容，我找到了以下信息：\n\n{context[:500]}...\n\n（注：由于LLM服务暂时不可用，以上是直接返回的相关内容片段）"

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
    ) -> QASession:
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
