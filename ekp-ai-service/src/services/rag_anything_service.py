import asyncio
import os
from typing import Optional, List, Dict, Any
from pathlib import Path

from src.config import settings


class RAGAnythingService:
    _instance = None
    _rag = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.working_dir = settings.rag_working_dir
            self.api_key = settings.openai_api_key
            self.base_url = settings.openai_base_url
            self.llm_model = settings.llm_model
            self.vision_model = settings.vision_model
            self.embedding_model = settings.embedding_model
            self.use_local_llm = settings.use_local_llm
            self.local_llm_url = settings.local_llm_url
            self._initialized = True

    async def initialize(self):
        if self._rag is not None:
            return self._rag

        try:
            from raganything import RAGAnything, RAGAnythingConfig
            from lightrag.llm.openai import openai_complete_if_cache, openai_embed
            from lightrag.utils import EmbeddingFunc

            os.makedirs(self.working_dir, exist_ok=True)

            config = RAGAnythingConfig(
                working_dir=self.working_dir,
                parser="mineru",
                parse_method="auto",
                enable_image_processing=True,
                enable_table_processing=True,
                enable_equation_processing=True,
            )

            if self.use_local_llm:
                llm_model_func = self._create_local_llm_func()
                vision_model_func = self._create_local_llm_func()
                embedding_func = self._create_local_embedding_func()
            else:
                llm_model_func = self._create_openai_llm_func()
                vision_model_func = self._create_openai_vision_func()
                embedding_func = self._create_openai_embedding_func()

            self._rag = RAGAnything(
                config=config,
                llm_model_func=llm_model_func,
                vision_model_func=vision_model_func,
                embedding_func=embedding_func,
            )

            print("RAG-Anything 初始化成功！")
            return self._rag

        except Exception as e:
            print(f"RAG-Anything 初始化失败: {e}")
            raise

    def _create_openai_llm_func(self):
        from lightrag.llm.openai import openai_complete_if_cache

        def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
            return openai_complete_if_cache(
                self.llm_model,
                prompt,
                system_prompt=system_prompt,
                history_messages=history_messages,
                api_key=self.api_key,
                base_url=self.base_url,
                **kwargs,
            )
        return llm_model_func

    def _create_openai_vision_func(self):
        from lightrag.llm.openai import openai_complete_if_cache

        def vision_model_func(
            prompt, system_prompt=None, history_messages=[], image_data=None, messages=None, **kwargs
        ):
            if messages:
                return openai_complete_if_cache(
                    self.vision_model,
                    "",
                    system_prompt=None,
                    history_messages=[],
                    messages=messages,
                    api_key=self.api_key,
                    base_url=self.base_url,
                    **kwargs,
                )
            elif image_data:
                return openai_complete_if_cache(
                    self.vision_model,
                    "",
                    system_prompt=None,
                    history_messages=[],
                    messages=[
                        {"role": "system", "content": system_prompt} if system_prompt else None,
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                                },
                            ],
                        } if image_data else {"role": "user", "content": prompt},
                    ],
                    api_key=self.api_key,
                    base_url=self.base_url,
                    **kwargs,
                )
            else:
                return self._create_openai_llm_func()(prompt, system_prompt, history_messages, **kwargs)
        return vision_model_func

    def _create_openai_embedding_func(self):
        from lightrag.llm.openai import openai_embed
        from lightrag.utils import EmbeddingFunc

        return EmbeddingFunc(
            embedding_dim=3072,
            max_token_size=8192,
            func=lambda texts: openai_embed(
                texts,
                model=self.embedding_model,
                api_key=self.api_key,
                base_url=self.base_url,
            ),
        )

    def _create_local_llm_func(self):
        import httpx

        async def llm_model_func(prompt, system_prompt=None, history_messages=[], **kwargs):
            messages = []
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            for msg in history_messages:
                messages.append(msg)
            messages.append({"role": "user", "content": prompt})

            async with httpx.AsyncClient(timeout=120.0) as client:
                response = await client.post(
                    f"{self.local_llm_url}/api/chat",
                    json={
                        "model": self.llm_model,
                        "messages": messages,
                        "stream": False,
                    },
                )
                result = response.json()
                return result.get("message", {}).get("content", "")

        return llm_model_func

    def _create_local_embedding_func(self):
        from lightrag.utils import EmbeddingFunc
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer('BAAI/bge-large-zh')

        async def embed_func(texts):
            embeddings = model.encode(texts, normalize_embeddings=True)
            return embeddings.tolist()

        return EmbeddingFunc(
            embedding_dim=1024,
            max_token_size=8192,
            func=embed_func,
        )

    async def process_document(
        self,
        file_path: str,
        output_dir: Optional[str] = None,
        parse_method: str = "auto",
    ) -> Dict[str, Any]:
        rag = await self.initialize()

        try:
            result = await rag.process_document_complete(
                file_path=file_path,
                output_dir=output_dir or "./output",
                parse_method=parse_method,
                display_stats=True,
            )
            return {"status": "success", "result": result}
        except Exception as e:
            print(f"文档处理失败: {e}")
            return {"status": "error", "error": str(e)}

    async def query(
        self,
        question: str,
        mode: str = "hybrid",
        vlm_enhanced: bool = False,
    ) -> str:
        rag = await self.initialize()

        try:
            result = await rag.aquery(
                question,
                mode=mode,
                vlm_enhanced=vlm_enhanced,
            )
            return result
        except Exception as e:
            print(f"查询失败: {e}")
            return f"抱歉，查询时出现错误: {str(e)}"

    async def query_with_multimodal(
        self,
        question: str,
        multimodal_content: List[Dict[str, Any]],
        mode: str = "hybrid",
    ) -> str:
        rag = await self.initialize()

        try:
            result = await rag.aquery_with_multimodal(
                question,
                multimodal_content=multimodal_content,
                mode=mode,
            )
            return result
        except Exception as e:
            print(f"多模态查询失败: {e}")
            return f"抱歉，多模态查询时出现错误: {str(e)}"

    async def insert_content_list(
        self,
        content_list: List[Dict[str, Any]],
        file_path: str,
        doc_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        rag = await self.initialize()

        try:
            await rag.insert_content_list(
                content_list=content_list,
                file_path=file_path,
                doc_id=doc_id,
                display_stats=True,
            )
            return {"status": "success"}
        except Exception as e:
            print(f"内容插入失败: {e}")
            return {"status": "error", "error": str(e)}

    @property
    def is_ready(self) -> bool:
        return self._rag is not None


rag_anything_service = RAGAnythingService()
