from datetime import datetime, timedelta, timezone
from typing import Any, Dict, Optional

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(password: str) -> str:
    """Хеширует пароль используя bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Проверяет соответствие пароля хешу."""
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(
        data: Dict[str, Any],
        expires_delta: Optional[timedelta] = None,
) -> str:
    """
    Создает JWT токен с полями sub, role, iat, exp.

    Args:
        data: Словарь с данными для включения в токен (должен содержать sub и role)
        expires_delta: Время жизни токена, по умолчанию из настроек

    Returns:
        str: Закодированный JWT токен
    """
    to_encode = data.copy()

    # Устанавливаем время создания
    now = datetime.now(timezone.utc)
    to_encode["iat"] = now

    # Устанавливаем время истечения
    if expires_delta:
        expire = now + expires_delta
    else:
        expire = now + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

    to_encode["exp"] = expire

    encoded_jwt = jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALG,
    )

    return encoded_jwt


def decode_token(token: str) -> Dict[str, Any]:
    """
    Декодирует и валидирует JWT токен.

    Args:
        token: JWT токен для декодирования

    Returns:
        Dict[str, Any]: Декодированный payload токена

    Raises:
        JWTError: Если токен невалидный или истек
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
        return payload
    except JWTError:
        raise