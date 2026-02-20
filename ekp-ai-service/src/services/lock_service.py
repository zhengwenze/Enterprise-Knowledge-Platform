import uuid
from typing import Optional
import asyncio

import redis.asyncio as redis


class DistributedLock:
    def __init__(
        self,
        redis: redis.Redis,
        lock_name: str,
        timeout: int = 30,
        retry_interval: float = 0.1,
        retry_times: int = 50,
    ):
        self.redis = redis
        self.lock_name = f"ekp:lock:{lock_name}"
        self.timeout = timeout
        self.retry_interval = retry_interval
        self.retry_times = retry_times
        self.identifier = str(uuid.uuid4())
        self._acquired = False

    async def acquire(self) -> bool:
        for _ in range(self.retry_times):
            acquired = await self.redis.set(
                self.lock_name,
                self.identifier,
                nx=True,
                ex=self.timeout,
            )
            
            if acquired:
                self._acquired = True
                return True
            
            await asyncio.sleep(self.retry_interval)
        
        return False

    async def release(self) -> bool:
        if not self._acquired:
            return False
        
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("del", KEYS[1])
        else
            return 0
        end
        """
        
        result = await self.redis.eval(script, 1, self.lock_name, self.identifier)
        self._acquired = False
        return result == 1

    async def extend(self, additional_time: int) -> bool:
        if not self._acquired:
            return False
        
        script = """
        if redis.call("get", KEYS[1]) == ARGV[1] then
            return redis.call("expire", KEYS[1], ARGV[2])
        else
            return 0
        end
        """
        
        result = await self.redis.eval(
            script,
            1,
            self.lock_name,
            self.identifier,
            self.timeout + additional_time,
        )
        return result == 1

    async def __aenter__(self):
        await self.acquire()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.release()
        return False


class LockService:
    def __init__(self, redis: redis.Redis):
        self.redis = redis

    def create_lock(
        self,
        lock_name: str,
        timeout: int = 30,
        retry_interval: float = 0.1,
        retry_times: int = 50,
    ) -> DistributedLock:
        return DistributedLock(
            redis=self.redis,
            lock_name=lock_name,
            timeout=timeout,
            retry_interval=retry_interval,
            retry_times=retry_times,
        )

    async def with_lock(
        self,
        lock_name: str,
        callback,
        timeout: int = 30,
    ):
        lock = self.create_lock(lock_name, timeout)
        
        try:
            if await lock.acquire():
                return await callback()
            else:
                raise TimeoutError(f"Failed to acquire lock: {lock_name}")
        finally:
            await lock.release()

    async def try_lock(self, lock_name: str, timeout: int = 30) -> Optional[DistributedLock]:
        lock = self.create_lock(lock_name, timeout, retry_times=1)
        
        if await lock.acquire():
            return lock
        return None


class RateLimiter:
    def __init__(self, redis: redis.Redis):
        self.redis = redis
        self.prefix = "ekp:rate_limit"

    def _key(self, identifier: str, action: str) -> str:
        return f"{self.prefix}:{action}:{identifier}"

    async def is_allowed(
        self,
        identifier: str,
        action: str,
        max_requests: int,
        window_seconds: int,
    ) -> bool:
        key = self._key(identifier, action)
        
        current = await self.redis.get(key)
        
        if current is None:
            await self.redis.setex(key, window_seconds, 1)
            return True
        
        if int(current) >= max_requests:
            return False
        
        await self.redis.incr(key)
        return True

    async def get_remaining(
        self,
        identifier: str,
        action: str,
        max_requests: int,
    ) -> int:
        key = self._key(identifier, action)
        current = await self.redis.get(key)
        
        if current is None:
            return max_requests
        
        return max(0, max_requests - int(current))

    async def reset(self, identifier: str, action: str) -> bool:
        key = self._key(identifier, action)
        return await self.redis.delete(key) > 0


class TokenBucket:
    def __init__(self, redis: redis.Redis):
        self.redis = redis
        self.prefix = "ekp:token_bucket"

    def _key(self, identifier: str, action: str) -> str:
        return f"{self.prefix}:{action}:{identifier}"

    async def consume(
        self,
        identifier: str,
        action: str,
        capacity: int,
        refill_rate: float,
        tokens: int = 1,
    ) -> bool:
        key = self._key(identifier, action)
        
        script = """
        local key = KEYS[1]
        local capacity = tonumber(ARGV[1])
        local refill_rate = tonumber(ARGV[2])
        local tokens_requested = tonumber(ARGV[3])
        local now = tonumber(ARGV[4])
        
        local bucket = redis.call('hmget', key, 'tokens', 'last_refill')
        local current_tokens = tonumber(bucket[1]) or capacity
        local last_refill = tonumber(bucket[2]) or now
        
        local elapsed = now - last_refill
        local refilled = elapsed * refill_rate
        current_tokens = math.min(capacity, current_tokens + refilled)
        
        if current_tokens >= tokens_requested then
            current_tokens = current_tokens - tokens_requested
            redis.call('hmset', key, 'tokens', current_tokens, 'last_refill', now)
            redis.call('expire', key, 3600)
            return 1
        else
            return 0
        end
        """
        
        import time
        now = time.time()
        
        result = await self.redis.eval(
            script,
            1,
            key,
            capacity,
            refill_rate,
            tokens,
            now,
        )
        
        return result == 1

    async def get_tokens(
        self,
        identifier: str,
        action: str,
        capacity: int,
        refill_rate: float,
    ) -> float:
        key = self._key(identifier, action)
        
        import time
        now = time.time()
        
        bucket = await self.redis.hmget(key, 'tokens', 'last_refill')
        
        if bucket[0] is None:
            return float(capacity)
        
        current_tokens = float(bucket[0])
        last_refill = float(bucket[1])
        
        elapsed = now - last_refill
        refilled = elapsed * refill_rate
        
        return min(capacity, current_tokens + refilled)
