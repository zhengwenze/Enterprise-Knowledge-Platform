from typing import List, Optional
import numpy as np
import httpx

from src.config import settings


class EmbeddingService:
    _instance = None
    _model = None
    _use_ollama = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None and not self._use_ollama:
            self._initialize_model()

    def _initialize_model(self):
        try:
            from sentence_transformers import SentenceTransformer

            model_name = settings.embedding_model
            print(f"正在加载嵌入模型: {model_name}")
            self._model = SentenceTransformer(model_name)
            print(f"嵌入模型加载完成，维度: {self._model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"嵌入模型加载失败: {e}")
            self._model = None

    @property
    def dimension(self) -> int:
        return settings.embedding_dimension

    @property
    def is_ready(self) -> bool:
        return True

    def _get_ollama_embedding(self, text: str) -> Optional[List[float]]:
        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.post(
                    f"{settings.local_llm_url}/api/embeddings",
                    json={
                        "model": settings.llm_model,
                        "prompt": text,
                    },
                )
                response.raise_for_status()
                result = response.json()
                return result.get("embedding", [])
        except Exception as e:
            print(f"Ollama 嵌入失败: {e}")
            return None

    def embed_texts(self, texts: List[str]) -> Optional[List[List[float]]]:
        if not texts:
            return []

        embeddings = []
        for text in texts:
            emb = self._get_ollama_embedding(text)
            if emb:
                embeddings.append(emb)
            else:
                return None

        return embeddings

    def embed_single_text(self, text: str) -> Optional[List[float]]:
        if not text:
            return None

        return self._get_ollama_embedding(text)

    def compute_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        vec1 = np.array(embedding1)
        vec2 = np.array(embedding2)

        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return float(dot_product / (norm1 * norm2))

    def batch_embed_with_progress(
        self, texts: List[str], batch_size: int = 32
    ) -> Optional[List[List[float]]]:
        all_embeddings = []
        total = len(texts)

        for i, text in enumerate(texts):
            print(f"处理文本 {i + 1}/{total}")
            emb = self._get_ollama_embedding(text)
            if emb:
                all_embeddings.append(emb)
            else:
                return None

        return all_embeddings
