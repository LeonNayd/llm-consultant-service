from typing import AsyncGenerator

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.exceptions import InvalidTokenError, TokenExpiredError
from app.core.security import decode_token
from app.db.session import get_db
from app.repositories.users import UsersRepository
from app.usecases.auth import AuthUseCase

bearer_scheme = HTTPBearer()


async def get_users_repo(
        db: AsyncSession = Depends(get_db),
) -> UsersRepository:
    """Зависимость для получения репозитория пользователей."""
    return UsersRepository(db)


async def get_auth_uc(
        users_repo: UsersRepository = Depends(get_users_repo),
) -> AuthUseCase:
    """Зависимость для получения use case аутентификации."""
    return AuthUseCase(users_repo)


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
        users_repo: UsersRepository = Depends(get_users_repo),
):
    """
    Зависимость для получения текущего пользователя по токену.

    Извлекает токен из заголовка Authorization, декодирует его
    и возвращает объект пользователя.

    Raises:
        InvalidTokenError: Если токен невалидный
        TokenExpiredError: Если токен истек
        UserNotFoundError: Если пользователь не найден
    """
    token = credentials.credentials

    try:
        payload = decode_token(token)
    except JWTError as e:
        if "expired" in str(e).lower():
            raise TokenExpiredError()
        raise InvalidTokenError()

    user_id = payload.get("sub")
    if not user_id:
        raise InvalidTokenError(detail="Token missing 'sub' claim")

    try:
        user_id = int(user_id)
    except ValueError:
        raise InvalidTokenError(detail="Invalid user ID in token")

    user = await users_repo.get_by_id(user_id)
    if not user:
        raise InvalidTokenError(detail="User from token not found")

    return user