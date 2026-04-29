from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from app.api.deps import get_auth_uc, get_current_user
from app.schemas.auth import RegisterRequest, TokenResponse
from app.schemas.user import UserPublic
from app.usecases.auth import AuthUseCase

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse, status_code=201)
async def register(
        request: RegisterRequest,
        auth_uc: AuthUseCase = Depends(get_auth_uc),
):
    """
    Регистрация нового пользователя.

    Создает нового пользователя и возвращает JWT токен доступа.
    """
    result = await auth_uc.register(request)
    return TokenResponse(**result)


@router.post("/login", response_model=TokenResponse)
async def login(
        form: OAuth2PasswordRequestForm = Depends(),
        auth_uc: AuthUseCase = Depends(get_auth_uc),
):
    """
    Вход пользователя.

    Принимает email и пароль в формате OAuth2, возвращает JWT токен.
    """
    result = await auth_uc.login(email=form.username, password=form.password)
    return TokenResponse(**result)


@router.get("/me", response_model=UserPublic)
async def me(
        current_user=Depends(get_current_user),
):
    """
    Получение профиля текущего пользователя.

    Требует валидный JWT токен в заголовке Authorization.
    """
    return UserPublic.model_validate(current_user)