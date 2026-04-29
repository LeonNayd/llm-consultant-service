from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI

from app.api.router import router
from app.core.config import settings
from app.infra.redis import close_redis


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Управление жизненным циклом приложения.
    """
    yield
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)