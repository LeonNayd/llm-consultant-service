from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Управление жизненным циклом приложения.
    Создает таблицы БД при запуске.
    """
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    yield

    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/health", tags=["system"])
async def health_check():
    """Проверка работоспособности сервиса."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENV,
    }