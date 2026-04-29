import httpx

from app.core.config import settings


async def call_openrouter(prompt: str) -> str:
    """
    Отправляет запрос к OpenRouter API и возвращает ответ.

    Args:
        prompt: Текст запроса

    Returns:
        str: Ответ от LLM

    Raises:
        httpx.HTTPError: При ошибках сетевого взаимодействия
        ValueError: При некорректном ответе от API
    """
    headers = {
        "Authorization": f"Bearer {settings.OPENROUTER_API_KEY}",
        "Content-Type": "application/json",
        "HTTP-Referer": settings.OPENROUTER_SITE_URL,
        "X-Title": settings.OPENROUTER_APP_NAME,
    }

    payload = {
        "model": settings.OPENROUTER_MODEL,
        "messages": [
            {
                "role": "user",
                "content": prompt,
            }
        ],
    }

    url = f"{settings.OPENROUTER_BASE_URL}/chat/completions"

    async with httpx.AsyncClient(timeout=120.0) as client:
        response = await client.post(url, json=payload, headers=headers)

        if response.status_code != 200:
            raise ValueError(
                f"OpenRouter API error: {response.status_code} - {response.text}"
            )

        data = response.json()

        try:
            content = data["choices"][0]["message"]["content"]
            return content
        except (KeyError, IndexError) as e:
            raise ValueError(f"Unexpected response format: {data}") from e