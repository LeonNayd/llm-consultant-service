from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import User


class UsersRepository:
    """Репозиторий для работы с пользователями."""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, user_id: int) -> Optional[User]:
        """Получить пользователя по ID."""
        result = await self.session.execute(
            select(User).where(User.id == user_id)
        )
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[User]:
        """Получить пользователя по email."""
        result = await self.session.execute(
            select(User).where(User.email == email)
        )
        return result.scalar_one_or_none()

    async def create(self, email: str, password_hash: str) -> User:
        """Создать нового пользователя."""
        user = User(
            email=email,
            password_hash=password_hash,
            role="user",
        )
        self.session.add(user)
        await self.session.commit()
        await self.session.refresh(user)
        return user