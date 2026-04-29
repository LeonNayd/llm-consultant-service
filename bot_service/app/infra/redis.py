import redis.asyncio as aioredis

from app.core.config import settings

_redis_client: aioredis.Redis | None = None


async def get_redis() -> aioredis.Redis:
    """
    Возвращает singleton-экземпляр Redis клиента.

    Returns:
        aioredis.Redis: Асинхронный клиент Redis
    """
    global _redis_client
    if _redis_client is None:
        _redis_client = aioredis.from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _redis_client


async def close_redis() -> None:
    """Закрывает соединение с Redis."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None