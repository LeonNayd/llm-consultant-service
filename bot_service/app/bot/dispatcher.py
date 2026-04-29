import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.bot.handlers import router
from app.core.config import settings

logger = logging.getLogger(__name__)


def _build_proxy_url() -> str | None:
    """
    Собирает URL для MTProto прокси из настроек.

    Формат: http://<secret>@<host>:<port>
    Используется для MTProto прокси (не SOCKS5/HTTP).

    Если прокси не настроен — возвращает None.
    """
    host = settings.MT_PROTO_PROXY_HOST
    port = settings.MT_PROTO_PROXY_PORT
    secret = settings.MT_PROTO_PROXY_SECRET

    if not host:
        return None

    if secret:
        return f"http://{secret}@{host}:{port}"
    return f"http://{host}:{port}"


async def start_bot() -> None:
    """Запускает Telegram бота с поддержкой MTProto прокси."""
    proxy_url = _build_proxy_url()

    if proxy_url:
        logger.info(f"Using MTProto proxy: {proxy_url.split('@')[-1] if '@' in proxy_url else proxy_url}")
    else:
        logger.info("No proxy configured, using direct connection")

    if proxy_url:
        session = AiohttpSession(
            proxy=proxy_url,
        )
    else:
        session = AiohttpSession()

    bot = Bot(
        token=settings.TELEGRAM_BOT_TOKEN,
        session=session,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher()

    dp.include_router(router)

    logger.info("Bot started, polling...")

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


async def main() -> None:
    """Точка входа для запуска бота."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        stream=sys.stdout,
    )

    logger.info("Starting Bot Service...")

    try:
        await start_bot()
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
    except Exception as e:
        logger.error(f"Bot crashed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())