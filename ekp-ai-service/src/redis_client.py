import redis.asyncio as redis
from typing import Optional, Any
import json

from src.config import settings


class RedisClient:
    _pool: Optional[redis.ConnectionPool] = None
    _client: Optional[redis.Redis] = None

    @classmethod
    async def get_client(cls) -> redis.Redis:
        if cls._client is None:
            cls._pool = redis.ConnectionPool.from_url(
                settings.redis_url,
                decode_responses=True,
                max_connections=50,
            )
            cls._client = redis.Redis(connection_pool=cls._pool)
        return cls._client

    @classmethod
    async def close(cls):
        if cls._client:
            await cls._client.close()
            cls._client = None
        if cls._pool:
            await cls._pool.disconnect()
            cls._pool = None


redis_client = RedisClient()


async def get_redis() -> redis.Redis:
    return await redis_client.get_client()


class CacheService:
    def __init__(self, redis: redis.Redis, prefix: str = "ekp"):
        self.redis = redis
        self.prefix = prefix

    def _key(self, *parts: str) -> str:
        return f"{self.prefix}:{':'.join(parts)}"

    async def get(self, key: str) -> Optional[Any]:
        full_key = self._key(key)
        data = await self.redis.get(full_key)
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: int = 3600,
    ) -> bool:
        full_key = self._key(key)
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        return await self.redis.setex(full_key, ttl, value)

    async def delete(self, key: str) -> bool:
        full_key = self._key(key)
        return await self.redis.delete(full_key) > 0

    async def exists(self, key: str) -> bool:
        full_key = self._key(key)
        return await self.redis.exists(full_key) > 0

    async def incr(self, key: str) -> int:
        full_key = self._key(key)
        return await self.redis.incr(full_key)

    async def expire(self, key: str, ttl: int) -> bool:
        full_key = self._key(key)
        return await self.redis.expire(full_key, ttl)
