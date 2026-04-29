from fastapi import APIRouter

from app.core.config import settings

router = APIRouter()


@router.get("/health", tags=["system"])
async def health_check():
    """Проверка работоспособности сервиса."""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "environment": settings.ENV,
    }