from aiogram import Bot
from aiogram.enums import ParseMode

from app.core.config import settings
from app.infra.celery_app import celery_app
from app.services.openrouter_client import call_openrouter


@celery_app.task(name="app.tasks.llm_tasks.llm_request", bind=True)
def llm_request(self, tg_chat_id: int, prompt: str):
    """
    Celery задача: отправляет запрос к OpenRouter LLM
    и пересылает ответ пользователю в Telegram.

    Args:
        tg_chat_id: ID чата Telegram
        prompt: Текст запроса пользователя
    """
    import asyncio

    async def _run():
        try:
            llm_response = await call_openrouter(prompt)

            bot = Bot(
                token=settings.TELEGRAM_BOT_TOKEN,
            )

            await bot.send_message(
                chat_id=tg_chat_id,
                text=f"Ответ LLM:\n\n{llm_response}",
                parse_mode=None,
            )

            await bot.session.close()

        except Exception as e:
            bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
            await bot.send_message(
                chat_id=tg_chat_id,
                text=f"Произошла ошибка при обработке запроса: {str(e)}",
            )
            await bot.session.close()
            raise

    loop = asyncio.new_event_loop()
    try:
        loop.run_until_complete(_run())
    finally:
        loop.close()