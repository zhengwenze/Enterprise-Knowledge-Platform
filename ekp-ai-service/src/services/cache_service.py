from typing import Optional, List, Dict, Any
import json
import hashlib

import redis.asyncio as redis


class QACacheService:
    def __init__(self, redis: redis.Redis):
        self.redis = redis
        self.prefix = "ekp:qa_cache"
        self.default_ttl = 3600  # 1小时
        self.hot_questions_ttl = 86400  # 24小时

    def _cache_key(self, question: str, mode: str = "hybrid") -> str:
        question_hash = hashlib.md5(question.encode()).hexdigest()
        return f"{self.prefix}:answer:{mode}:{question_hash}"

    def _hot_key(self) -> str:
        return f"{self.prefix}:hot_questions"

    def _stats_key(self, question: str) -> str:
        question_hash = hashlib.md5(question.encode()).hexdigest()
        return f"{self.prefix}:stats:{question_hash}"

    async def get_cached_answer(
        self,
        question: str,
        mode: str = "hybrid",
    ) -> Optional[Dict[str, Any]]:
        key = self._cache_key(question, mode)
        data = await self.redis.get(key)
        
        if data:
            await self._record_hit(question)
            return json.loads(data)
        return None

    async def cache_answer(
        self,
        question: str,
        answer: str,
        sources: List[Dict],
        mode: str = "hybrid",
        ttl: Optional[int] = None,
    ) -> bool:
        key = self._cache_key(question, mode)
        
        cache_data = {
            "question": question,
            "answer": answer,
            "sources": sources,
            "mode": mode,
            "cached_at": __import__('datetime').datetime.now().isoformat(),
        }
        
        ttl = ttl or self.default_ttl
        return await self.redis.setex(
            key,
            ttl,
            json.dumps(cache_data, ensure_ascii=False),
        )

    async def _record_hit(self, question: str):
        stats_key = self._stats_key(question)
        await self.redis.incr(stats_key)
        await self.redis.expire(stats_key, 86400)

    async def get_question_stats(self, question: str) -> int:
        stats_key = self._stats_key(question)
        count = await self.redis.get(stats_key)
        return int(count) if count else 0

    async def add_to_hot_questions(
        self,
        question: str,
        answer: str,
    ) -> bool:
        key = self._hot_key()
        
        hot_item = {
            "question": question,
            "answer": answer[:200] + "..." if len(answer) > 200 else answer,
            "updated_at": __import__('datetime').datetime.now().isoformat(),
        }
        
        await self.redis.zadd(
            key,
            {json.dumps(hot_item, ensure_ascii=False): 1},
        )
        
        await self.redis.zremrangebyrank(key, 0, -51)
        
        return True

    async def increment_hot_score(self, question: str):
        key = self._hot_key()
        
        for member in await self.redis.zrange(key, 0, -1):
            data = json.loads(member)
            if data.get("question") == question:
                await self.redis.zincrby(key, 1, member)
                break

    async def get_hot_questions(self, limit: int = 10) -> List[Dict[str, Any]]:
        key = self._hot_key()
        
        results = await self.redis.zrevrange(key, 0, limit - 1, withscores=True)
        
        return [
            {**json.loads(member), "score": score}
            for member, score in results
        ]

    async def invalidate_cache(
        self,
        question: str,
        mode: str = "hybrid",
    ) -> bool:
        key = self._cache_key(question, mode)
        return await self.redis.delete(key) > 0

    async def clear_all_cache(self) -> bool:
        keys = await self.redis.keys(f"{self.prefix}:answer:*")
        if keys:
            return await self.redis.delete(*keys) > 0
        return True


class DocumentCacheService:
    def __init__(self, redis: redis.Redis):
        self.redis = redis
        self.prefix = "ekp:doc_cache"
        self.list_ttl = 300  # 5分钟
        self.detail_ttl = 600  # 10分钟

    def _list_key(self, page: int = 1, status: str = None) -> str:
        return f"{self.prefix}:list:page:{page}:status:{status or 'all'}"

    def _detail_key(self, doc_id: int) -> str:
        return f"{self.prefix}:detail:{doc_id}"

    def _chunks_key(self, doc_id: int) -> str:
        return f"{self.prefix}:chunks:{doc_id}"

    async def get_document_list(
        self,
        page: int = 1,
        status: str = None,
    ) -> Optional[List[Dict]]:
        key = self._list_key(page, status)
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def cache_document_list(
        self,
        page: int,
        status: str,
        documents: List[Dict],
    ) -> bool:
        key = self._list_key(page, status)
        return await self.redis.setex(
            key,
            self.list_ttl,
            json.dumps(documents, ensure_ascii=False),
        )

    async def invalidate_list_cache(self) -> bool:
        keys = await self.redis.keys(f"{self.prefix}:list:*")
        if keys:
            return await self.redis.delete(*keys) > 0
        return True

    async def get_document_detail(self, doc_id: int) -> Optional[Dict]:
        key = self._detail_key(doc_id)
        data = await self.redis.get(key)
        return json.loads(data) if data else None

    async def cache_document_detail(
        self,
        doc_id: int,
        document: Dict,
    ) -> bool:
        key = self._detail_key(doc_id)
        return await self.redis.setex(
            key,
            self.detail_ttl,
            json.dumps(document, ensure_ascii=False),
        )

    async def invalidate_document_cache(self, doc_id: int) -> bool:
        keys = [
            self._detail_key(doc_id),
            self._chunks_key(doc_id),
        ]
        return await self.redis.delete(*keys) > 0
