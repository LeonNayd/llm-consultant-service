import asyncio
from typing import Generator

import fakeredis.aioredis
import pytest
import pytest_asyncio


@pytest.fixture(scope="session")
def event_loop() -> Generator[asyncio.AbstractEventLoop, None, None]:
    """Создает event loop для тестовой сессии."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def fake_redis():
    """Создает fake Redis клиент для тестов."""
    return fakeredis.aioredis.FakeRedis(decode_responses=True)


@pytest_asyncio.fixture
async def patched_redis(monkeypatch, fake_redis):
    """
    Патчит get_redis в модуле handlers,
    чтобы использовался fake Redis.
    """
    async def _get_fake_redis():
        return fake_redis

    monkeypatch.setattr(
        "app.bot.handlers.get_redis",
        _get_fake_redis,
    )

    return fake_redis