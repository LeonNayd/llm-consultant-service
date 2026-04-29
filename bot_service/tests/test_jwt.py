"""
Модульные тесты для проверки JWT в Bot Service.
"""
import pytest
from jose import jwt

from app.core.config import settings
from app.core.jwt import decode_and_validate


class TestJWTValidation:
    """Тесты валидации JWT токенов."""

    def test_valid_token_decodes_correctly(self):
        """Валидный токен должен успешно декодироваться."""
        payload = {
            "sub": "42",
            "role": "user",
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

        decoded = decode_and_validate(token)

        assert decoded["sub"] == "42"
        assert decoded["role"] == "user"

    def test_invalid_token_raises_error(self):
        """Невалидная строка должна вызывать ошибку."""
        with pytest.raises(ValueError, match="Invalid token"):
            decode_and_validate("not_a_valid_token_at_all")

    def test_token_without_sub_raises_error(self):
        """Токен без sub должен вызывать ошибку."""
        payload = {
            "role": "user",
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

        with pytest.raises(ValueError, match="missing 'sub'"):
            decode_and_validate(token)

    def test_token_with_wrong_secret_raises_error(self):
        """Токен с неправильным секретом должен вызывать ошибку."""
        payload = {
            "sub": "42",
            "role": "user",
        }
        token = jwt.encode(payload, "wrong_secret", algorithm=settings.JWT_ALG)

        with pytest.raises(ValueError, match="Invalid token"):
            decode_and_validate(token)

    def test_expired_token_raises_error(self):
        """Истекший токен должен вызывать ошибку."""
        from datetime import datetime, timedelta, timezone

        payload = {
            "sub": "42",
            "role": "user",
            "exp": datetime.now(timezone.utc) - timedelta(hours=1),
        }
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

        with pytest.raises(ValueError, match="Invalid token"):
            decode_and_validate(token)