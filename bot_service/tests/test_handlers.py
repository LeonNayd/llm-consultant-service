"""
Тесты обработчиков Telegram бота с моками.
"""
from unittest.mock import AsyncMock, MagicMock

import pytest
from aiogram.types import Message

from app.bot.handlers import cmd_token, handle_message


def make_message(text: str, user_id: int = 12345, chat_id: int = 67890):
    """Создает мок-сообщение для тестов."""
    message = MagicMock(spec=Message)
    message.text = text
    message.from_user = MagicMock()
    message.from_user.id = user_id
    message.chat = MagicMock()
    message.chat.id = chat_id
    message.answer = AsyncMock()
    return message


class TestTokenHandler:
    """Тесты обработчика /token."""

    @pytest.mark.asyncio
    async def test_token_saved_to_redis(self, patched_redis):
        """Токен должен сохраняться в Redis."""
        from app.core.config import settings
        from jose import jwt

        # Создаем тестовый токен
        payload = {"sub": "42", "role": "user"}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)

        message = make_message(f"/token {token}", user_id=12345)

        await cmd_token(message)

        saved_token = await patched_redis.get("token:12345")
        assert saved_token == token

    @pytest.mark.asyncio
    async def test_invalid_token_not_saved(self, patched_redis):
        """Невалидный токен не должен сохраняться."""
        message = make_message("/token invalid_token", user_id=12345)

        await cmd_token(message)

        saved_token = await patched_redis.get("token:12345")
        assert saved_token is None

    @pytest.mark.asyncio
    async def test_missing_token_shows_help(self, patched_redis):
        """Команда /token без токена должна показать справку."""
        message = make_message("/token", user_id=12345)

        await cmd_token(message)

        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "укажи токен" in call_text.lower()


class TestMessageHandler:
    """Тесты обработчика текстовых сообщений."""

    @pytest.mark.asyncio
    async def test_no_token_shows_instruction(self, patched_redis):
        """Если токена нет, бот должен показать инструкцию."""
        message = make_message("Привет, бот!", user_id=99999)

        await handle_message(message)

        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "нет сохранённого токена" in call_text.lower()

    @pytest.mark.asyncio
    async def test_with_token_calls_celery(self, patched_redis):
        """С валидным токеном должен вызываться Celery."""
        from unittest.mock import patch

        from app.core.config import settings
        from jose import jwt

        # Сохраняем валидный токен
        payload = {"sub": "42", "role": "user"}
        token = jwt.encode(payload, settings.JWT_SECRET, algorithm=settings.JWT_ALG)
        await patched_redis.set("token:12345", token)

        message = make_message("Как дела?", user_id=12345, chat_id=67890)

        with patch("app.tasks.llm_tasks.llm_request.delay") as mock_delay:
            await handle_message(message)

            mock_delay.assert_called_once_with(
                tg_chat_id=67890,
                prompt="Как дела?",
            )

        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "принят в обработку" in call_text.lower()

    @pytest.mark.asyncio
    async def test_invalid_token_in_redis_shows_error(self, patched_redis):
        """Если в Redis невалидный токен, бот должен сообщить об ошибке."""
        await patched_redis.set("token:12345", "invalid_token")

        message = make_message("Вопрос", user_id=12345)

        await handle_message(message)

        message.answer.assert_called_once()
        call_text = message.answer.call_args[0][0]
        assert "недействителен" in call_text.lower()