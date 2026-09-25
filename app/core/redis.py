"""
Redis client - ket noi singleton cho toan bo ung dung.
Su dung redis.Redis (sync) de tuong thich voi FastAPI + thread pool.
"""
import redis

from app.core.config import settings

_redis_client: redis.Redis | None = None


def get_redis() -> redis.Redis:
    """Tra ve Redis client da ket noi (singleton pattern)."""
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
        )
    return _redis_client
