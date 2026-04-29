from fastapi import HTTPException, status


class BaseHTTPException(HTTPException):
    """Базовый класс для HTTP исключений сервиса."""
    pass


class UserAlreadyExistsError(BaseHTTPException):
    """Пользователь уже существует (409 Conflict)."""
    def __init__(self, detail: str = "User with this email already exists"):
        super().__init__(
            status_code=status.HTTP_409_CONFLICT,
            detail=detail,
        )


class InvalidCredentialsError(BaseHTTPException):
    """Неверные учетные данные (401 Unauthorized)."""
    def __init__(self, detail: str = "Invalid email or password"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class InvalidTokenError(BaseHTTPException):
    """Невалидный токен (401 Unauthorized)."""
    def __init__(self, detail: str = "Invalid token"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class TokenExpiredError(BaseHTTPException):
    """Токен истек (401 Unauthorized)."""
    def __init__(self, detail: str = "Token has expired"):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers={"WWW-Authenticate": "Bearer"},
        )


class UserNotFoundError(BaseHTTPException):
    """Пользователь не найден (404 Not Found)."""
    def __init__(self, detail: str = "User not found"):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
        )


class PermissionDeniedError(BaseHTTPException):
    """Доступ запрещен (403 Forbidden)."""
    def __init__(self, detail: str = "Permission denied"):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
        )