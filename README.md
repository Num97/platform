# Platform

Микросервисная платформа на FastAPI. API Gateway + сервис аутентификации.

## Архитектура

```
                  ┌──────────────────┐
    :8000 ──────► │   API Gateway    │
                  │  (FastAPI)       │
                  │  · rate limiting │
                  │  · JWT verify    │
                  │  · CORS          │
                  └────────┬─────────┘
                           │ httpx proxy
                  ┌────────▼─────────┐
    :8001 ──────► │  Auth Service    │
                  │  (FastAPI)       │
                  │  · JWT tokens    │
                  │  · registration  │
                  │  · user CRUD     │
                  └────────┬─────────┘
                           │ SQLAlchemy
                  ┌────────▼─────────┐
                  │  PostgreSQL 16   │
                  └──────────────────┘
```

## Сервисы

| Сервис | Порт | Описание |
|--------|------|----------|
| [API Gateway](./gateway/api-gateway/) | 8000 | Проксирование, rate limit, проверка JWT |
| [Auth Service](./services/auth-service/) | 8001 | Аутентификация, пользователи, JWT-токены |
| PostgreSQL | 5433 | База данных |

## Быстрый старт (Docker Compose)

```bash
# Клонирование
git clone <repo-url>
cd platform

# Создать .env из шаблона
copy .env.example .env

# Сгенерировать SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(64))"

# Запустить все сервисы
docker compose up -d --build
```

Сервисы будут доступны:
- API Gateway: `http://localhost:8000`
- Auth Service: `http://localhost:8001`
- Swagger UI: `http://localhost:8000/docs`

## Первый запуск (миграции БД)

Первый раз нужно применить миграции внутри auth-service:

```bash
cd services/auth-service
copy .env.example .env

pip install -r requirements.txt
alembic upgrade head
```

Или через API:

```bash
docker compose exec auth-service alembic upgrade head
```

## Разработка без Docker

### Auth Service

```bash
cd services/auth-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
alembic upgrade head
python -m app.main
```

### API Gateway

```bash
cd gateway/api-gateway
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy ..\..\.env.example .env
python -m app.main
```

## Переменные окружения

Все переменные задаются в `.env` файле в корне проекта.

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `SECRET_KEY` | — | **Ключ JWT** — должен быть одинаковым во всех сервисах |
| `ALGORITHM` | `HS256` | Алгоритм подписи JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Время жизни access-токена (мин) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Время жизни refresh-токена (дни) |
| `DEBUG` | `True` | Режим отладки |
| `GATEWAY_HOST` | `0.0.0.0` | Хост шлюза |
| `GATEWAY_PORT` | `8000` | Порт шлюза |
| `SERVICE_HOST` | `0.0.0.0` | Хост auth-сервиса |
| `SERVICE_PORT` | `8001` | Порт auth-сервиса |
| `DATABASE_URL` | — | Строка подключения к PostgreSQL |
| `POSTGRES_USER` | `auth_user` | Пользователь БД |
| `POSTGRES_PASSWORD` | `auth_pass` | Пароль БД |
| `POSTGRES_DB` | `auth_db` | База данных |
| `AUTH_SERVICE_URL` | `http://auth-service:8001` | URL auth-сервиса для шлюза |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000", ...]` | CORS-источники |
| `RATE_LIMIT_ENABLED` | `True` | Rate limiting |
| `RATE_LIMIT_REQUESTS` | `100` | Лимит запросов на IP |
| `RATE_LIMIT_WINDOW` | `60` | Окно rate-limit (сек) |

## Структура проекта

```
.
├── gateway/
│   ├── api-gateway/          # API Gateway (FastAPI)
│   │   ├── app/
│   │   │   ├── core/         # Конфиг, зависимости
│   │   │   ├── middleware/   # Rate limiter
│   │   │   ├── routes/       # Прокси-маршрутизация
│   │   │   └── main.py       # Точка входа
│   │   ├── tests/
│   │   ├── requirements.txt
│   │   └── Dockerfile
│   └── nginx/                # Nginx (заглушка)
├── services/
│   └── auth-service/         # Сервис аутентификации (FastAPI)
│       ├── app/
│       │   ├── core/         # Конфиг, безопасность, зависимости
│       │   ├── db/           # SQLAlchemy база и сессия
│       │   ├── models/       # Модели БД
│       │   ├── routes/       # Эндпоинты /auth, /users
│       │   ├── schemas/      # Pydantic-схемы
│       │   ├── services/     # Бизнес-логика
│       │   └── main.py       # Точка входа
│       ├── alembic/          # Миграции БД
│       ├── tests/
│       ├── requirements.txt
│       ├── Dockerfile
│       ├── docker-compose.yml
│       └── README.md
├── .env.example              # Шаблон переменных окружения
├── .gitignore
├── .gitattributes
└── docker-compose.yml        # Запуск всей платформы
```
