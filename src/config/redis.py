import redis.asyncio as redis
from typing import Optional
import json
from src.config.settings import settings


class RedisClient:
    """Redis cache client"""

    def __init__(self):
        self.client: Optional[redis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        self.client = await redis.from_url(
            settings.redis_url,
            encoding="utf-8",
            decode_responses=True
        )

    async def disconnect(self):
        """Disconnect from Redis"""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[dict]:
        """Get value from cache"""
        if not self.client:
            return None

        value = await self.client.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: dict, ttl: int = None):
        """Set value in cache"""
        if not self.client:
            return

        ttl = ttl or settings.cache_ttl
        await self.client.setex(
            key,
            ttl,
            json.dumps(value)
        )

    async def delete(self, key: str):
        """Delete key from cache"""
        if self.client:
            await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            return False
        return await self.client.exists(key) > 0


# Global Redis client instance
redis_client = RedisClient()
