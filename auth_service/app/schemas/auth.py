from pydantic import BaseModel, EmailStr, Field


class RegisterRequest(BaseModel):
    """Схема запроса на регистрацию."""
    email: EmailStr = Field(..., description="Email пользователя")
    password: str = Field(
        ...,
        min_length=6,
        max_length=128,
        description="Пароль пользователя",
    )


class TokenResponse(BaseModel):
    """Схема ответа с токеном доступа."""
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")


class LoginResponse(BaseModel):
    """Схема ответа при входе."""
    access_token: str = Field(..., description="JWT токен доступа")
    token_type: str = Field(default="bearer", description="Тип токена")