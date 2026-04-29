from typing import Any, Dict

from jose import JWTError, jwt

from app.core.config import settings


def decode_and_validate(token: str) -> Dict[str, Any]:
    """
    Декодирует и валидирует JWT токен.

    Проверяет:
    - подпись токена
    - срок действия (exp)
    - наличие sub

    Args:
        token: JWT токен для проверки

    Returns:
        Dict[str, Any]: payload токена

    Raises:
        ValueError: Если токен невалидный, истёк или отсутствует sub
    """
    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALG],
        )
    except JWTError as e:
        raise ValueError(f"Invalid token: {str(e)}")

    if "sub" not in payload:
        raise ValueError("Token missing 'sub' claim")

    return payload