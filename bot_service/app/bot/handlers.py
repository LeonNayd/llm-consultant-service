import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message
import redis.asyncio as aioredis

from app.core.config import settings
from app.core.jwt import decode_and_validate
from app.infra.redis import get_redis

logger = logging.getLogger(__name__)

router = Router()


async def _save_token(redis_client: aioredis.Redis, tg_user_id: int, token: str) -> None:
    """
    Сохраняет JWT токен в Redis.

    Args:
        redis_client: Клиент Redis
        tg_user_id: ID пользователя Telegram
        token: JWT токен
    """
    key = f"token:{tg_user_id}"
    await redis_client.set(key, token, ex=86400)
    logger.info(f"Token saved for user {tg_user_id}")


async def _get_token(redis_client: aioredis.Redis, tg_user_id: int) -> str | None:
    """
    Получает JWT токен из Redis.

    Args:
        redis_client: Клиент Redis
        tg_user_id: ID пользователя Telegram

    Returns:
        str | None: JWT токен или None, если не найден
    """
    key = f"token:{tg_user_id}"
    return await redis_client.get(key)


@router.message(Command(commands=["start"]))
async def cmd_start(message: Message) -> None:
    """Обработчик команды /start."""
    await message.answer(
        "Привет! Я бот-консультант с LLM.\n\n"
        "Для начала работы отправь мне свой JWT токен командой:\n"
        "/token <ваш_токен>\n\n"
        "Получить токен можно в Auth Service:\n"
        "1. Зарегистрируйся через /auth/register\n"
        "2. Войди через /auth/login\n"
        "3. Скопируй access_token"
    )


@router.message(Command(commands=["token"]))
async def cmd_token(message: Message) -> None:
    """
    Обработчик команды /token <jwt>.
    Сохраняет JWT токен пользователя в Redis.
    """
    parts = message.text.split(maxsplit=1)

    if len(parts) < 2:
        await message.answer(
            "Пожалуйста, укажи токен после команды:\n"
            "/token <ваш_jwt_токен>"
        )
        return

    token = parts[1].strip()

    try:
        payload = decode_and_validate(token)
        user_id = payload.get("sub")
    except ValueError as e:
        await message.answer(
            f"Токен недействителен: {str(e)}\n"
            "Пожалуйста, получи новый токен в Auth Service."
        )
        return

    try:
        redis_client = await get_redis()
        await _save_token(redis_client, message.from_user.id, token)

        await message.answer(
            f"Токен успешно сохранён!\n"
            f"User ID: {user_id}\n"
            f"Role: {payload.get('role', 'unknown')}\n\n"
            f"Теперь ты можешь отправлять мне вопросы, "
            f"и я буду отвечать с помощью LLM."
        )
    except Exception as e:
        logger.error(f"Failed to save token: {e}")
        await message.answer("Произошла ошибка при сохранении токена. Попробуй позже.")


@router.message()
async def handle_message(message: Message) -> None:
    """
    Обработчик обычных текстовых сообщений.
    Проверяет токен и отправляет запрос к LLM через Celery.
    """
    tg_user_id = message.from_user.id
    prompt = message.text.strip()

    if not prompt:
        await message.answer("Пожалуйста, отправь текстовый вопрос.")
        return

    try:
        redis_client = await get_redis()
        token = await _get_token(redis_client, tg_user_id)
    except Exception as e:
        logger.error(f"Redis error: {e}")
        await message.answer("Произошла ошибка. Попробуй позже.")
        return

    if not token:
        await message.answer(
            "У тебя нет сохранённого токена.\n\n"
            "Пожалуйста, сначала авторизуйся:\n"
            "1. Получи токен в Auth Service\n"
            "2. Отправь его мне командой /token <токен>"
        )
        return

    try:
        payload = decode_and_validate(token)
        logger.info(f"Token valid for user {payload.get('sub')}")
    except ValueError as e:
        await message.answer(
            f"Твой токен недействителен: {str(e)}\n"
            "Пожалуйста, получи новый токен в Auth Service "
            "и отправь его командой /token <токен>"
        )
        await redis_client.delete(f"token:{tg_user_id}")
        return

    try:
        from app.tasks.llm_tasks import llm_request

        llm_request.delay(tg_chat_id=message.chat.id, prompt=prompt)

        await message.answer(
            "Твой запрос принят в обработку. Ожидай ответа...\n"
            "Это может занять некоторое время."
        )
        logger.info(f"Task sent for user {tg_user_id}")
    except Exception as e:
        logger.error(f"Failed to send task: {e}")
        await message.answer(
            "Произошла ошибка при отправке запроса. Попробуй позже."
        )