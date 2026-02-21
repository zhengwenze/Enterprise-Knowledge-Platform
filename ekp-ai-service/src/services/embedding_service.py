from typing import List, Optional
import numpy as np
import httpx

from src.config import settings


class EmbeddingService:
    _instance = None
    _model = None
    _use_local = True

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if self._model is None:
            self._initialize_model()

    def _initialize_model(self):
        try:
            from sentence_transformers import SentenceTransformer

            model_name = settings.embedding_model
            print(f"正在加载嵌入模型: {model_name}")
            self._model = SentenceTransformer(model_name)
            self._dimension = self._model.get_sentence_embedding_dimension()
            print(f"嵌入模型加载完成，维度: {self._dimension}")
        except Exception as e:
            print(f"嵌入模型加载失败: {e}")
            self._model = None
            self._dimension = settings.embedding_dimension

    @property
    def dimension(self) -> int:
        if self._model:
            return self._dimension
        return settings.embedding_dimension

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    def embed_texts(self, texts: List[str]) -> Optional[List[List[float]]]:
        if not texts:
            return []

        if self._model is None:
            print("嵌入模型未初始化")
            return None

        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            print(f"嵌入生成失败: {e}")
            return None

    def embed_single_text(self, text: str) -> Optional[List[float]]:
        if not text:
            return None

        if self._model is None:
            print("嵌入模型未初始化")
            return None

        try:
            embedding = self._model.encode(text, convert_to_numpy=True)
            return embedding.tolist()
        except Exception as e:
            print(f"嵌入生成失败: {e}")
            return None

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
        if self._model is None:
            print("嵌入模型未初始化")
            return None

        try:
            all_embeddings = []
            total = len(texts)

            for i in range(0, total, batch_size):
                batch = texts[i:i + batch_size]
                print(f"处理文本批次 {i // batch_size + 1}/{(total + batch_size - 1) // batch_size}")
                embeddings = self._model.encode(batch, convert_to_numpy=True)
                all_embeddings.extend(embeddings.tolist())

            return all_embeddings
        except Exception as e:
            print(f"批量嵌入生成失败: {e}")
            return None
