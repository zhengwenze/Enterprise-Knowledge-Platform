from typing import List
from dataclasses import dataclass
import re

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

    def chunk_text(self, text: str) -> List[TextChunk]:
        if not text or not text.strip():
            return []

        paragraphs = re.split(r'\n\s*\n', text)
        
        chunks = []
        current_chunk = ""
        chunk_index = 0

        for para in paragraphs:
            para = para.strip()
            if not para:
                continue

            if len(current_chunk) + len(para) + 2 <= self.chunk_size:
                current_chunk += "\n\n" + para if current_chunk else para
            else:
                if current_chunk:
                    token_count = self._estimate_token_count(current_chunk)
                    chunks.append(
                        TextChunk(
                            content=current_chunk,
                            chunk_index=chunk_index,
                            token_count=token_count,
                        )
                    )
                    chunk_index += 1

                if len(para) > self.chunk_size:
                    sub_chunks = self._split_long_paragraph(para, chunk_index)
                    chunks.extend(sub_chunks)
                    chunk_index += len(sub_chunks)
                    current_chunk = ""
                else:
                    current_chunk = para

        if current_chunk:
            token_count = self._estimate_token_count(current_chunk)
            chunks.append(
                TextChunk(
                    content=current_chunk,
                    chunk_index=chunk_index,
                    token_count=token_count,
                )
            )

        return chunks

    def _split_long_paragraph(self, text: str, start_index: int) -> List[TextChunk]:
        chunks = []
        sentences = re.split(r'([。！？；\n])', text)
        
        current_chunk = ""
        chunk_index = start_index

        for i in range(0, len(sentences), 2):
            sentence = sentences[i]
            delimiter = sentences[i + 1] if i + 1 < len(sentences) else ""
            full_sentence = sentence + delimiter

            if len(current_chunk) + len(full_sentence) <= self.chunk_size:
                current_chunk += full_sentence
            else:
                if current_chunk:
                    token_count = self._estimate_token_count(current_chunk)
                    chunks.append(
                        TextChunk(
                            content=current_chunk,
                            chunk_index=chunk_index,
                            token_count=token_count,
                        )
                    )
                    chunk_index += 1

                if len(full_sentence) > self.chunk_size:
                    for j in range(0, len(full_sentence), self.chunk_size):
                        sub = full_sentence[j:j + self.chunk_size]
                        token_count = self._estimate_token_count(sub)
                        chunks.append(
                            TextChunk(
                                content=sub,
                                chunk_index=chunk_index,
                                token_count=token_count,
                            )
                        )
                        chunk_index += 1
                    current_chunk = ""
                else:
                    current_chunk = full_sentence

        if current_chunk:
            token_count = self._estimate_token_count(current_chunk)
            chunks.append(
                TextChunk(
                    content=current_chunk,
                    chunk_index=chunk_index,
                    token_count=token_count,
                )
            )

        return chunks

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
