# LLM Consultant Service

Двухсервисная система LLM-консультаций с JWT-аутентификацией и асинхронной обработкой запросов через очереди сообщений.

---

## Архитектура

Проект состоит из двух независимых сервисов, разделяющих ответственность:

### Auth Service (FastAPI + SQLite)
- Регистрация и аутентификация пользователей
- Хеширование паролей (bcrypt)
- Выпуск и валидация JWT-токенов (HS256)
- Не содержит логики Telegram-бота
- Порт: `8000`

### Bot Service (aiogram + Celery + RabbitMQ + Redis)
- Telegram-бот на aiogram 3.x
- Принимает JWT от пользователя, сохраняет в Redis
- Валидирует токен без обращения к Auth Service
- Отправляет запросы к LLM асинхронно через Celery + RabbitMQ
- Не содержит логики регистрации и не хранит пользователей

---

## Сценарий работы

<img alt="diagram.png" src="screenshots/diagram.png"/>

---

## Стек технологий

| Компонент | Технологии |
|-----------|-----------|
| Auth Service | FastAPI, SQLAlchemy, aiosqlite, python-jose, passlib, bcrypt, pydantic-settings |
| Bot Service | aiogram 3.x, FastAPI, Celery, Redis, httpx, python-jose, pydantic-settings |
| Брокер сообщений | RabbitMQ |
| Кэш/Хранилище | Redis |
| LLM API | OpenRouter |
| Контейнеризация | Docker, Docker Compose |
| Тестирование | pytest, pytest-asyncio, fakeredis, pytest-mock, respx |
| Пакетный менеджер | uv |

---

## Структура проекта

```
llm-consultant-service/
├── auth_service/                  # Сервис аутентификации
│   ├── app/
│   │   ├── api/                   # Роутеры и зависимости FastAPI
│   │   │   ├── deps.py            # Зависимости (get_db, get_current_user)
│   │   │   ├── router.py          # Сборка роутеров
│   │   │   └── routes_auth.py     # Эндпоинты /auth/*
│   │   ├── core/                  # Ядро приложения
│   │   │   ├── config.py          # Настройки (pydantic-settings)
│   │   │   ├── exceptions.py      # HTTP-исключения
│   │   │   └── security.py        # Хеширование паролей, JWT
│   │   ├── db/                    # База данных
│   │   │   ├── base.py            # Базовый класс SQLAlchemy
│   │   │   ├── models.py          # Модель User
│   │   │   └── session.py         # Асинхронные сессии
│   │   ├── repositories/          # Доступ к данным
│   │   │   └── users.py           # UsersRepository
│   │   ├── schemas/               # Pydantic-схемы
│   │   │   ├── auth.py            # RegisterRequest, TokenResponse
│   │   │   └── user.py            # UserPublic
│   │   ├── usecases/              # Бизнес-логика
│   │   │   └── auth.py            # AuthUseCase
│   │   └── main.py                # Точка входа FastAPI
│   ├── tests/
│   │   ├── conftest.py            # Фикстуры (in-memory SQLite)
│   │   ├── test_auth_api.py       # Интеграционные тесты API
│   │   └── test_security.py       # Модульные тесты безопасности
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── .env
│
├── bot_service/                   # Telegram-бот сервис
│   ├── app/
│   │   ├── api/
│   │   │   └── router.py          # Health-check API
│   │   ├── bot/                   # Логика Telegram-бота
│   │   │   ├── dispatcher.py      # Bot, Dispatcher, polling
│   │   │   └── handlers.py        # Обработчики /start, /token, сообщений
│   │   ├── core/                  # Ядро Bot Service
│   │   │   ├── config.py          # Настройки
│   │   │   └── jwt.py             # Валидация JWT
│   │   ├── infra/                 # Инфраструктура
│   │   │   ├── celery_app.py      # Celery приложение
│   │   │   └── redis.py           # Redis клиент (singleton)
│   │   ├── services/              # Внешние сервисы
│   │   │   └── openrouter_client.py  # Клиент OpenRouter API
│   │   ├── tasks/                 # Celery-задачи
│   │   │   └── llm_tasks.py       # Задача запроса к LLM
│   │   └── main.py                # FastAPI приложение
│   ├── tests/
│   │   ├── conftest.py            # Фикстуры (fakeredis)
│   │   ├── test_handlers.py       # Мок-тесты обработчиков бота
│   │   └── test_jwt.py            # Модульные тесты валидации JWT
│   ├── Dockerfile
│   ├── pyproject.toml
│   ├── pytest.ini
│   └── .env
│
├── docker-compose.yml             # Оркестрация всех сервисов
├── .env                    # Переменные окружения для Docker
└── README.md
```

---

## Запуск проекта

### Предварительные требования

- **Python 3.11+**
- **Docker** и **Docker Compose**
- **uv** (пакетный менеджер)
- **Telegram Bot Token** (получить у [@BotFather](https://t.me/BotFather))
- **OpenRouter API Key** (получить на [openrouter.ai](https://openrouter.ai))
- **VPN** (если Telegram заблокирован в вашем регионе)

---

### Способ 1: Полный запуск в Docker

1. **Клонируйте репозиторий:**
```bash
git clone <repo-url>
cd llm-consultant-service
```

2. **Настройте переменные окружения:**
```bash
cp .env
```

Отредактируйте `.env`:
```env
AUTH_JWT_SECRET=ваш_секретный_ключ
AUTH_JWT_ALG=HS256
AUTH_ACCESS_TOKEN_EXPIRE_MINUTES=60

BOT_TELEGRAM_TOKEN=ваш_токен_бота
BOT_JWT_SECRET=ваш_секретный_ключ
BOT_JWT_ALG=HS256
BOT_OPENROUTER_API_KEY=ваш_ключ_openrouter
BOT_OPENROUTER_MODEL=google/gemini-2.0-flash-001
```

3. **Запустите все сервисы:**
```bash
docker compose up -d
```

4. **Проверьте статус:**
```bash
docker compose ps
```

Должны быть запущены: `rabbitmq`, `redis`, `auth-service`, `celery-worker`, `bot-service`.

5. **Проверьте логи:**
```bash
docker compose logs -f
```

6. **Остановка:**
```bash
docker compose down
```

---

### Способ 2: Смешанный запуск (инфраструктура в Docker, бот на хосте)

Используйте, если Telegram заблокирован и Docker не может использовать системный VPN.

1. **Запустите инфраструктуру:**
```bash
docker compose up -d rabbitmq redis auth-service
```

2. **Запустите Celery worker локально:**
```bash
cd bot_service
uv sync
uv run celery -A app.infra.celery_app worker --loglevel=info
```

3. **Запустите бота локально (с VPN):**
```bash
cd bot_service
uv run python -m app.bot.dispatcher
```

---

### Способ 3: Полностью локальный запуск (без Docker)

1. **Установите и запустите RabbitMQ и Redis** (через Docker или нативно):
```bash
# Через Docker
docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:3-management
docker run -d --name redis -p 6379:6379 redis:7-alpine
```

2. **Настройте .env в bot_service:**
```env
REDIS_URL=redis://localhost:6379/0
RABBITMQ_URL=amqp://guest:guest@localhost:5672//
```

3. **Запустите Auth Service:**
```bash
cd auth_service
uv sync
uv run uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

4. **Запустите Celery Worker:**
```bash
cd bot_service
uv sync
uv run celery -A app.infra.celery_app worker --loglevel=info
```

5. **Запустите бота:**
```bash
cd bot_service
uv run python -m app.bot.dispatcher
```

---

## API Endpoints

### Auth Service (http://localhost:8000)

| Метод | Путь | Описание | Авторизация |
|-------|------|----------|-------------|
| `POST` | `/auth/register` | Регистрация пользователя | Нет |
| `POST` | `/auth/login` | Вход (OAuth2 form-data) | Нет |
| `GET` | `/auth/me` | Профиль текущего пользователя | Bearer JWT |
| `GET` | `/health` | Проверка работоспособности | Нет |

**Swagger UI:** http://localhost:8000/docs

### Bot Service (http://localhost:8001)

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/health` | Проверка работоспособности |

---

## Использование

### 1. Получите JWT токен

Откройте http://localhost:8000/docs:

**Регистрация:**
```json
POST /auth/register
{
  "email": "naydanov@email.com",
  "password": "pass123"
}
```

Ответ:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIs...",
  "token_type": "bearer"
}
```

**Вход:**
```
POST /auth/login
username: naydanov@email.com
password: pass123
```

### 2. Отправьте токен боту

В Telegram найдите бота и отправьте:

```
/start
```

```
/token eyJhbGciOiJIUzI1NiIs...
```

Бот ответит: «Токен успешно сохранён!»

### 3. Задайте вопрос

Просто напишите текст, например:
```
Что такое LLM?
```

Бот примет запрос и через несколько секунд пришлёт ответ от LLM.

---

## Тестирование

### Auth Service (19 тестов)

```bash
cd auth_service
uv run pytest tests/ -v
```

Покрытие:
- Модульные тесты: хеширование паролей, создание/декодирование JWT
- Интеграционные тесты: регистрация, логин, /auth/me
- Негативные тесты: дубликат, неверный пароль, истекший токен

### Bot Service (11 тестов)

```bash
cd bot_service
uv run pytest tests/ -v
```

Покрытие:
- Модульные тесты: валидация JWT (подпись, срок, sub)
- Мок-тесты: обработчики бота с fakeredis и pytest-mock
- Проверка цепочки: токен → Redis → Celery → ответ

---

## Демонстрация работы

### Auth Service (Swagger)

| Скриншот                          | Описание                 |
|-----------------------------------|--------------------------|
| <img alt="register.png" src="screenshots/register.png"/> | Регистрация пользователя |
| <img alt="login.png" src="screenshots/login.png"/>  | Получение JWT токена     |
| <img alt="auth.png" src="screenshots/auth.png"/>    | Профиль пользователя     |

### Telegram Bot

| Скриншот                            | Описание                                                                                                                                                               |
|-------------------------------------|------------------------------------------------------------------------------------------------------------------------------------------------------------------------|
| <img alt="llm_bot.png" src="screenshots/llm_bot.png"/> | Демонстрация возможностей бота: <br> • Запуск бота `/start` <br> • Обработка невалидных токенов <br> • Сохранение токена командой `/token` <br> • Вопросы и ответы LLM |

### RabbitMQ

| Скриншот | Описание           |
|----------|--------------------|
| <img alt="rabbitmq_overview.png" src="screenshots/rabbitmq_overview.png"/> | RabbitQM обзор     |
| <img alt="rabbitmq_queues.png" src="screenshots/rabbitmq_queues.png"/> | RabbitQM сообщения |

### Тестирование

| Скриншот | Описание                |
|----------|-------------------------|
| <img alt="auth_service_tests.png" src="screenshots/auth_service_tests.png"/> | Auth Service: 19 тестов |
| <img alt="bot_service_tests.png" src="screenshots/bot_service_tests.png"/> | Bot Service: 11 тестов  |

---