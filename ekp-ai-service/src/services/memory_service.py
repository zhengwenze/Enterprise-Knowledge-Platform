from typing import List, Dict, Any, Optional
from datetime import datetime
import json

import redis.asyncio as redis


class WorkingMemoryService:
    def __init__(self, redis: redis.Redis):
        self.redis = redis
        self.prefix = "ekp:memory"
        self.default_ttl = 3600  # 1小时
        self.max_messages = 50

    def _session_key(self, session_id: str) -> str:
        return f"{self.prefix}:session:{session_id}"

    def _user_sessions_key(self, user_id: int) -> str:
        return f"{self.prefix}:user:{user_id}:sessions"

    async def add_message(
        self,
        session_id: str,
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> bool:
        key = self._session_key(session_id)
        
        message = {
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata or {},
        }
        
        await self.redis.rpush(key, json.dumps(message, ensure_ascii=False))
        await self.redis.expire(key, self.default_ttl)
        
        list_len = await self.redis.llen(key)
        if list_len > self.max_messages:
            await self.redis.ltrim(key, -self.max_messages, -1)
        
        return True

    async def get_messages(
        self,
        session_id: str,
        limit: int = 20,
    ) -> List[Dict[str, Any]]:
        key = self._session_key(session_id)
        
        messages = await self.redis.lrange(key, -limit, -1)
        
        return [json.loads(msg) for msg in messages]

    async def get_all_messages(self, session_id: str) -> List[Dict[str, Any]]:
        key = self._session_key(session_id)
        messages = await self.redis.lrange(key, 0, -1)
        return [json.loads(msg) for msg in messages]

    async def clear_session(self, session_id: str) -> bool:
        key = self._session_key(session_id)
        return await self.redis.delete(key) > 0

    async def set_session_ttl(self, session_id: str, ttl: int) -> bool:
        key = self._session_key(session_id)
        return await self.redis.expire(key, ttl)

    async def get_message_count(self, session_id: str) -> int:
        key = self._session_key(session_id)
        return await self.redis.llen(key)

    async def set_context(
        self,
        session_id: str,
        context_key: str,
        value: Any,
        ttl: Optional[int] = None,
    ) -> bool:
        key = f"{self.prefix}:context:{session_id}:{context_key}"
        ttl = ttl or self.default_ttl
        
        if isinstance(value, (dict, list)):
            value = json.dumps(value, ensure_ascii=False)
        
        return await self.redis.setex(key, ttl, value)

    async def get_context(
        self,
        session_id: str,
        context_key: str,
    ) -> Optional[Any]:
        key = f"{self.prefix}:context:{session_id}:{context_key}"
        data = await self.redis.get(key)
        
        if data:
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return None

    async def register_user_session(
        self,
        user_id: int,
        session_id: str,
        ttl: int = 86400 * 7,  # 7天
    ) -> bool:
        key = self._user_sessions_key(user_id)
        await self.redis.sadd(key, session_id)
        await self.redis.expire(key, ttl)
        return True

    async def get_user_sessions(self, user_id: int) -> List[str]:
        key = self._user_sessions_key(user_id)
        return list(await self.redis.smembers(key))
