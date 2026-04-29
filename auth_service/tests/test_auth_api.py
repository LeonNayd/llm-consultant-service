import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
class TestAuthAPI:
    """Интеграционные тесты API аутентификации."""

    async def test_register_user_success(self, client: AsyncClient):
        """Успешная регистрация нового пользователя."""
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "testpassword123",
            },
        )

        assert response.status_code == 201
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    async def test_register_duplicate_user_fails(self, client: AsyncClient):
        """Повторная регистрация с тем же email должна вернуть 409."""
        await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "testpassword123",
            },
        )

        response = await client.post(
            "/auth/register",
            json={
                "email": "duplicate@example.com",
                "password": "testpassword123",
            },
        )

        assert response.status_code == 409
        assert "already exists" in response.json()["detail"].lower()

    async def test_login_success(self, client: AsyncClient):
        """Успешный вход с правильными учетными данными."""
        await client.post(
            "/auth/register",
            json={
                "email": "login_test@example.com",
                "password": "testpassword123",
            },
        )

        response = await client.post(
            "/auth/login",
            data={
                "username": "login_test@example.com",
                "password": "testpassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    async def test_login_with_wrong_password(self, client: AsyncClient):
        """Вход с неверным паролем должен вернуть 401."""
        await client.post(
            "/auth/register",
            json={
                "email": "wrong_pass@example.com",
                "password": "correctpassword123",
            },
        )

        response = await client.post(
            "/auth/login",
            data={
                "username": "wrong_pass@example.com",
                "password": "wrongpassword123",
            },
        )

        assert response.status_code == 401

    async def test_login_nonexistent_user(self, client: AsyncClient):
        """Вход с несуществующим email должен вернуть 401."""
        response = await client.post(
            "/auth/login",
            data={
                "username": "nonexistent@example.com",
                "password": "somepassword123",
            },
        )

        assert response.status_code == 401

    async def test_get_me_with_valid_token(self, client: AsyncClient):
        """Получение профиля с валидным токеном."""
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "me_test@example.com",
                "password": "testpassword123",
            },
        )

        token = register_response.json()["access_token"]

        response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == "me_test@example.com"
        assert data["role"] == "user"
        assert "id" in data
        assert "password_hash" not in data

    async def test_get_me_without_token(self, client: AsyncClient):
        """Запрос /auth/me без токена должен вернуть 403 (HTTPBearer)."""
        response = await client.get("/auth/me")

        assert response.status_code in [401, 403]

    async def test_get_me_with_invalid_token(self, client: AsyncClient):
        """Запрос /auth/me с невалидным токеном должен вернуть 401."""
        response = await client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid_token_here"},
        )

        assert response.status_code == 401

    async def test_full_auth_flow(self, client: AsyncClient):
        """Полный сценарий: регистрация -> логин -> профиль."""
        register_response = await client.post(
            "/auth/register",
            json={
                "email": "full_flow@example.com",
                "password": "testpassword123",
            },
        )
        assert register_response.status_code == 201

        duplicate_response = await client.post(
            "/auth/register",
            json={
                "email": "full_flow@example.com",
                "password": "testpassword123",
            },
        )
        assert duplicate_response.status_code == 409

        login_response = await client.post(
            "/auth/login",
            data={
                "username": "full_flow@example.com",
                "password": "testpassword123",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        me_response = await client.get(
            "/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me_response.status_code == 200
        user_data = me_response.json()
        assert user_data["email"] == "full_flow@example.com"
        assert "password_hash" not in user_data

        wrong_login_response = await client.post(
            "/auth/login",
            data={
                "username": "full_flow@example.com",
                "password": "wrongpassword",
            },
        )
        assert wrong_login_response.status_code == 401

    async def test_health_check(self, client: AsyncClient):
        """Проверка health check эндпоинта."""
        response = await client.get("/health")

        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"