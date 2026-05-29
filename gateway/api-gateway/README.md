# API Gateway

Единая точка входа для микросервисов платформы. Маршрутизация, rate limiting, валидация JWT-токенов на уровне шлюза.

## Стек

- **Python 3.12+**
- **FastAPI** — веб-фреймворк
- **httpx** — асинхронный HTTP-клиент для проксирования
- **python-jose** — проверка JWT
- **pydantic-settings** — конфигурация

## Быстрый старт

### 1. Клонирование и настройка

```bash
cd gateway/api-gateway
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Конфигурация

Создай `.env` на основе `.env.example` (из корня проекта или скопируй в текущую директорию):

```bash
copy ..\..\.env.example .env
```

Убедись что `SECRET_KEY` совпадает с auth-service.

### 3. Запуск

```bash
python -m app.main
```

Шлюз доступен на `http://localhost:8000`.  
Swagger: `http://localhost:8000/docs`.

## API

### Открытые маршруты — проксируются на auth-service без токена

| Метод | Путь | Описание |
|-------|------|----------|
| `POST` | `/api/v1/auth/register` | Регистрация |
| `POST` | `/api/v1/auth/login` | Вход |
| `POST` | `/api/v1/auth/refresh` | Обновление токенов |
| `POST` | `/api/v1/auth/logout` | Выход |
| `POST` | `/api/v1/auth/forgot-password` | Запрос сброса пароля |
| `POST` | `/api/v1/auth/reset-password` | Сброс пароля |

### Защищённые маршруты — требуют `Authorization: Bearer <token>`

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/api/v1/auth/me` | Данные текущего пользователя |
| `GET` | `/api/v1/auth/verify-token` | Проверка токена |
| `POST` | `/api/v1/auth/logout-all` | Выход со всех устройств |
| `POST` | `/api/v1/auth/change-password` | Смена пароля |
| `GET` | `/api/v1/users/` | Список пользователей |
| `GET` | `/api/v1/users/{id}` | Пользователь по ID |
| `PUT` | `/api/v1/users/{id}` | Редактирование пользователя |

### Системные

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Информация о шлюзе |
| `GET` | `/health` | Health check |
| `GET` | `/docs` | Swagger UI |
| `GET` | `/redoc` | ReDoc |

## Rate Limiting

По умолчанию: **100 запросов в 60 секунд** с одного IP. Настраивается через переменные окружения:

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `RATE_LIMIT_ENABLED` | `True` | Включить/отключить |
| `RATE_LIMIT_REQUESTS` | `100` | Лимит запросов |
| `RATE_LIMIT_WINDOW` | `60` | Окно в секундах |

При превышении возвращается `429 Too Many Requests`.

## CORS

CORS-заголовки включены. Источники по умолчанию: `http://localhost:3000`, `http://localhost:80`, `http://localhost`.

Настройка через `BACKEND_CORS_ORIGINS`.

## Переменные окружения

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `PROJECT_NAME` | `API Gateway` | Название сервиса |
| `VERSION` | `1.0.0` | Версия |
| `DEBUG` | `True` | Режим отладки |
| `GATEWAY_HOST` | `0.0.0.0` | Хост шлюза |
| `GATEWAY_PORT` | `8000` | Порт шлюза |
| `SECRET_KEY` | — | Секретный ключ JWT (должен совпадать с auth-service) |
| `ALGORITHM` | `HS256` | Алгоритм JWT |
| `AUTH_SERVICE_URL` | `http://auth-service:8001` | URL auth-сервиса |
| `BACKEND_CORS_ORIGINS` | `["http://localhost:3000", ...]` | Разрешённые CORS-источники |

## Заголовки ответов

| Заголовок | Описание |
|-----------|----------|
| `X-Request-ID` | Идентификатор запроса |
| `X-Gateway-Time` | Время обработки запроса шлюзом в секундах |

## Структура проекта

```
.
├── app/
│   ├── core/
│   │   ├── config.py         # Настройки (Settings)
│   │   └── dependencies.py   # Проверка JWT-токенов
│   ├── middleware/
│   │   └── rate_limit.py     # In-memory rate limiter
│   ├── routes/
│   │   └── proxy.py          # Прокси-маршрутизация
│   └── main.py               # Точка входа
├── tests/
│   └── test_proxy.py
├── requirements.txt
├── Dockerfile
└── pyproject.toml
```
