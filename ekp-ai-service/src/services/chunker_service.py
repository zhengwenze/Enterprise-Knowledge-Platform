from typing import List
from dataclasses import dataclass

from langchain.text_splitter import RecursiveCharacterTextSplitter

from src.config import settings


@dataclass
class TextChunk:
    content: str
    chunk_index: int
    token_count: int


class ChunkerService:
    def __init__(
        self,
        chunk_size: int = None,
        chunk_overlap: int = None,
    ):
        self.chunk_size = chunk_size or settings.chunk_size
        self.chunk_overlap = chunk_overlap or settings.chunk_overlap
        self._splitter = None

    @property
    def splitter(self) -> RecursiveCharacterTextSplitter:
        if self._splitter is None:
            self._splitter = RecursiveCharacterTextSplitter(
                chunk_size=self.chunk_size,
                chunk_overlap=self.chunk_overlap,
                length_function=len,
                separators=["\n\n", "\n", "。", "！", "？", "；", "，", " ", ""],
            )
        return self._splitter

    def chunk_text(self, text: str) -> List[TextChunk]:
        if not text or not text.strip():
            return []

        chunks = self.splitter.split_text(text)

        result = []
        for index, chunk_content in enumerate(chunks):
            token_count = self._estimate_token_count(chunk_content)
            result.append(
                TextChunk(
                    content=chunk_content,
                    chunk_index=index,
                    token_count=token_count,
                )
            )

        return result

    def _estimate_token_count(self, text: str) -> int:
        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        other_chars = len(text) - chinese_chars
        return chinese_chars + other_chars // 4

    def get_chunk_stats(self, chunks: List[TextChunk]) -> dict:
        if not chunks:
            return {
                "total_chunks": 0,
                "total_tokens": 0,
                "avg_chunk_size": 0,
                "min_chunk_size": 0,
                "max_chunk_size": 0,
            }

        sizes = [len(chunk.content) for chunk in chunks]
        return {
            "total_chunks": len(chunks),
            "total_tokens": sum(chunk.token_count for chunk in chunks),
            "avg_chunk_size": sum(sizes) // len(sizes),
            "min_chunk_size": min(sizes),
            "max_chunk_size": max(sizes),
        }
