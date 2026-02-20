import pytest
from src.services.chunker_service import ChunkerService, TextChunk


class TestChunkerService:
    def test_chunk_empty_text(self):
        service = ChunkerService(chunk_size=100, chunk_overlap=20)
        result = service.chunk_text("")
        assert result == []

    def test_chunk_whitespace_text(self):
        service = ChunkerService(chunk_size=100, chunk_overlap=20)
        result = service.chunk_text("   \n\n  ")
        assert result == []

    def test_chunk_short_text(self):
        service = ChunkerService(chunk_size=100, chunk_overlap=20)
        text = "这是一个简短的文本。"
        result = service.chunk_text(text)
        assert len(result) == 1
        assert result[0].content == text
        assert result[0].chunk_index == 0

    def test_chunk_long_text(self):
        service = ChunkerService(chunk_size=50, chunk_overlap=10)
        text = "这是第一段内容。" * 20
        result = service.chunk_text(text)
        assert len(result) > 1
        for i, chunk in enumerate(result):
            assert chunk.chunk_index == i

    def test_chunk_preserves_content(self):
        service = ChunkerService(chunk_size=100, chunk_overlap=20)
        text = "这是测试内容。" * 10
        result = service.chunk_text(text)
        combined = "".join(chunk.content for chunk in result)
        assert text in combined or combined in text

    def test_chunk_stats(self):
        service = ChunkerService(chunk_size=100, chunk_overlap=20)
        chunks = [
            TextChunk(content="测试内容一", chunk_index=0, token_count=5),
            TextChunk(content="测试内容二", chunk_index=1, token_count=5),
        ]
        stats = service.get_chunk_stats(chunks)
        assert stats["total_chunks"] == 2
        assert stats["total_tokens"] == 10

    def test_chunk_stats_empty(self):
        service = ChunkerService(chunk_size=100, chunk_overlap=20)
        stats = service.get_chunk_stats([])
        assert stats["total_chunks"] == 0
        assert stats["total_tokens"] == 0

    def test_token_estimation(self):
        service = ChunkerService(chunk_size=100, chunk_overlap=20)
        text = "这是中文测试内容"
        result = service.chunk_text(text)
        assert result[0].token_count > 0
