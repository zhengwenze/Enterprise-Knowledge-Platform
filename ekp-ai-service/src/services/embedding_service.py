from typing import List, Optional
import numpy as np

from src.config import settings


class EmbeddingService:
    _instance = None
    _model = None

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
            print(f"嵌入模型加载完成，维度: {self._model.get_sentence_embedding_dimension()}")
        except Exception as e:
            print(f"嵌入模型加载失败: {e}")
            self._model = None

    @property
    def dimension(self) -> int:
        if self._model:
            return self._model.get_sentence_embedding_dimension()
        return settings.embedding_dimension

    @property
    def is_ready(self) -> bool:
        return self._model is not None

    def embed_texts(self, texts: List[str]) -> Optional[List[List[float]]]:
        if not self._model:
            print("嵌入模型未初始化")
            return None

        if not texts:
            return []

        try:
            embeddings = self._model.encode(texts, convert_to_numpy=True)
            return embeddings.tolist()
        except Exception as e:
            print(f"文本嵌入失败: {e}")
            return None

    def embed_single_text(self, text: str) -> Optional[List[float]]:
        if not text:
            return None

        embeddings = self.embed_texts([text])
        return embeddings[0] if embeddings else None

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
        if not self._model:
            return None

        all_embeddings = []
        total_batches = (len(texts) + batch_size - 1) // batch_size

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_num = i // batch_size + 1
            print(f"处理批次 {batch_num}/{total_batches}")

            embeddings = self.embed_texts(batch)
            if embeddings:
                all_embeddings.extend(embeddings)
            else:
                return None

        return all_embeddings
