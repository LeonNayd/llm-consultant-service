import time

from app.core.security import (
    create_access_token,
    decode_token,
    hash_password,
    verify_password,
)


class TestPasswordHashing:
    """Тесты хеширования и проверки паролей."""

    def test_hash_password_returns_different_string(self):
        """Хеш должен отличаться от исходного пароля."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert hashed != password
        assert len(hashed) > 0

    def test_hash_password_is_deterministic_for_verify(self):
        """Один и тот же пароль должен проходить verify."""
        password = "test_password_123"
        hashed = hash_password(password)

        assert verify_password(password, hashed) is True

    def test_verify_password_rejects_wrong_password(self):
        """Неверный пароль не должен проходить verify."""
        password = "test_password_123"
        wrong_password = "wrong_password_456"
        hashed = hash_password(password)

        assert verify_password(wrong_password, hashed) is False

    def test_hash_password_generates_unique_hashes(self):
        """Каждый вызов hash_password должен генерировать уникальный хеш."""
        password = "test_password_123"
        hash1 = hash_password(password)
        hash2 = hash_password(password)

        assert hash1 != hash2

        assert verify_password(password, hash1) is True
        assert verify_password(password, hash2) is True


class TestJWT:
    """Тесты создания и декодирования JWT токенов."""

    def test_create_and_decode_token(self):
        """Токен должен успешно создаваться и декодироваться."""
        data = {"sub": "1", "role": "user"}

        token = create_access_token(data)
        payload = decode_token(token)

        assert payload["sub"] == "1"
        assert payload["role"] == "user"

    def test_token_contains_required_fields(self):
        """Токен должен содержать все обязательные поля."""
        data = {"sub": "123", "role": "admin"}

        token = create_access_token(data)
        payload = decode_token(token)

        assert "sub" in payload
        assert "role" in payload
        assert "iat" in payload
        assert "exp" in payload
        assert payload["sub"] == "123"
        assert payload["role"] == "admin"

    def test_token_expiration(self):
        """Токен должен корректно обрабатывать истечение срока."""
        from datetime import timedelta

        data = {"sub": "1", "role": "user"}

        token = create_access_token(data, expires_delta=timedelta(seconds=1))

        payload = decode_token(token)
        assert payload["sub"] == "1"

        time.sleep(2)

        from jose import JWTError
        try:
            decode_token(token)
            assert False, "Should have raised JWTError"
        except JWTError:
            pass

    def test_invalid_token_raises_error(self):
        """Невалидный токен должен вызывать ошибку."""
        from jose import JWTError

        try:
            decode_token("invalid_token_string")
            assert False, "Should have raised JWTError"
        except JWTError:
            pass

    def test_token_with_different_roles(self):
        """Токен должен сохранять разные роли."""
        for role in ["user", "admin", "moderator"]:
            data = {"sub": "1", "role": role}
            token = create_access_token(data)
            payload = decode_token(token)

            assert payload["role"] == role