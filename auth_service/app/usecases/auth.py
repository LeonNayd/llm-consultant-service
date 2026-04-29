from app.core.exceptions import (
    InvalidCredentialsError,
    UserAlreadyExistsError,
    UserNotFoundError,
)
from app.core.security import create_access_token, hash_password, verify_password
from app.repositories.users import UsersRepository
from app.schemas.auth import RegisterRequest


class AuthUseCase:
    """Бизнес-логика аутентификации."""

    def __init__(self, users_repo: UsersRepository):
        self.users_repo = users_repo

    async def register(self, request: RegisterRequest) -> dict:
        """
        Регистрация нового пользователя.

        Args:
            request: Данные для регистрации

        Returns:
            dict: Токен доступа

        Raises:
            UserAlreadyExistsError: Если пользователь уже существует
        """
        existing_user = await self.users_repo.get_by_email(request.email)
        if existing_user:
            raise UserAlreadyExistsError()

        hashed_password = hash_password(request.password)
        user = await self.users_repo.create(
            email=request.email,
            password_hash=hashed_password,
        )

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )

        return {"access_token": access_token, "token_type": "bearer"}

    async def login(self, email: str, password: str) -> dict:
        """
        Вход пользователя.

        Args:
            email: Email пользователя
            password: Пароль пользователя

        Returns:
            dict: Токен доступа

        Raises:
            InvalidCredentialsError: Если email или пароль неверные
        """
        user = await self.users_repo.get_by_email(email)
        if not user:
            raise InvalidCredentialsError()

        if not verify_password(password, user.password_hash):
            raise InvalidCredentialsError()

        access_token = create_access_token(
            data={"sub": str(user.id), "role": user.role}
        )

        return {"access_token": access_token, "token_type": "bearer"}

    async def me(self, user_id: int) -> dict:
        """
        Получение профиля пользователя.

        Args:
            user_id: ID пользователя из токена

        Returns:
            dict: Данные пользователя

        Raises:
            UserNotFoundError: Если пользователь не найден
        """
        user = await self.users_repo.get_by_id(user_id)
        if not user:
            raise UserNotFoundError()

        return user