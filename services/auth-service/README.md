# Auth Service

Сервис аутентификации и авторизации на FastAPI. JWT-токены, refresh-ротация, управление пользователями.

## Стек

- **Python 3.12+**
- **FastAPI** — веб-фреймворк
- **SQLAlchemy 2.0** — ORM
- **Alembic** — миграции БД
- **PostgreSQL** — база данных
- **python-jose** — JWT
- **bcrypt/passlib** — хеширование паролей

## Быстрый старт

### 1. Клонирование и настройка

```bash
git clone <repo-url>
cd auth-service
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Конфигурация

Создай `.env` на основе `.env.example`:

```bash
copy .env.example .env
```

Замени `SECRET_KEY` на случайную строку:

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```

### 3. База данных

Подними PostgreSQL (например через Docker):

```bash
docker run -d \
  --name auth-postgres \
  -e POSTGRES_USER=auth_user \
  -e POSTGRES_PASSWORD=auth_pass \
  -e POSTGRES_DB=auth_db \
  -p 5433:5432 \
  postgres:16
```

Примени миграции:

```bash
alembic upgrade head
```

### 4. Запуск

```bash
python -m app.main
```

Сервис доступен на `http://localhost:8001`.  
Swagger-документация: `http://localhost:8001/docs`.

## API

Базовый путь: `/api/auth`

### Аутентификация

| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| `POST` | `/auth/register` | Открытый | Регистрация |
| `POST` | `/auth/login` | Открытый | Вход, возвращает `access_token` и `refresh_token` |
| `POST` | `/auth/refresh` | Открытый | Обновить `access_token` по `refresh_token` |
| `POST` | `/auth/logout` | Открытый | Отозвать `refresh_token` |
| `POST` | `/auth/logout-all` | 🔒 | Отозвать все refresh-токены |
| `GET`  | `/auth/me` | 🔒 | Информация о текущем пользователе |
| `GET`  | `/auth/verify-token` | 🔒 | Проверить валидность токена |
| `POST` | `/auth/change-password` | 🔒 | Сменить пароль |
| `POST` | `/auth/forgot-password` | Открытый | Запросить сброс пароля |
| `POST` | `/auth/reset-password` | Открытый | Сбросить пароль по токену |

### Пользователи

| Метод | Путь | Доступ | Описание |
|-------|------|--------|----------|
| `GET`  | `/users/` | Открытый | Список пользователей |
| `GET`  | `/users/{id}` | Открытый | Пользователь по ID |
| `PUT`  | `/users/{id}` | 🔒 | Редактировать пользователя |

#### PUT /users/{id} — права

| Роль | Что можно менять |
|------|-----------------|
| `ADMIN`, `MANAGER` | `email`, `full_name`, `role`, `is_active` любого пользователя |
| Сам пользователь | `email`, `full_name` (только свои) |
| Остальные | 403 |

### Системные

| Метод | Путь | Описание |
|-------|------|----------|
| `GET` | `/` | Информация о сервисе |
| `GET` | `/health` | Health check |

## Роли и статусы

**Роли** (`UserRole`):

| Роль | Описание |
|------|----------|
| `admin` | Администратор — полный доступ |
| `manager` | Менеджер — управление пользователями |
| `user` | Обычный пользователь (по умолчанию) |

**Статусы** (`UserStatus`):

| Статус | Описание |
|--------|----------|
| `active` | Активен (по умолчанию) |
| `inactive` | Деактивирован — вход запрещён (403) |

## Аутентификация

Передавай токен в заголовке:

```
Authorization: Bearer <access_token>
```

- `access_token` живёт 30 минут (настраивается в `ACCESS_TOKEN_EXPIRE_MINUTES`)
- `refresh_token` живёт 7 дней (или 14 при `remember_me: true`)
- При обновлении используется ротация: старый refresh-токен отзывается

## Миграции

```bash
# Новая миграция после изменения моделей
alembic revision --autogenerate -m "описание"

# Применить миграции
alembic upgrade head

# Откатить на шаг
alembic downgrade -1

# История миграций
alembic history
```

## Тесты

```bash
.venv\Scripts\python.exe -m pytest tests/ -v
```

## Переменные окружения

| Переменная | По умолчанию | Описание |
|-----------|-------------|----------|
| `DATABASE_URL` | `postgresql+psycopg2://user:pass@localhost:5432/db` | Строка подключения к PostgreSQL |
| `SECRET_KEY` | `change-me-in-production...` | Ключ подписи JWT |
| `ALGORITHM` | `HS256` | Алгоритм JWT |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Время жизни access-токена (мин) |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Время жизни refresh-токена (дни) |
| `DEBUG` | `True` | Режим отладки |
| `SERVICE_PORT` | `8001` | Порт сервиса |

## Структура проекта

```
.
├── alembic/              # Миграции
│   ├── versions/         # Файлы миграций
│   ├── env.py            # Конфигурация alembic
│   └── script.py.mako    # Шаблон миграций
├── app/
│   ├── core/             # Конфиг, безопасность, зависимости
│   │   ├── config.py     # Настройки (Settings)
│   │   ├── security.py   # Хеширование, JWT
│   │   └── dependencies.py  # FastAPI-зависимости
│   ├── db/               # База данных
│   │   ├── base.py       # Декларативная база
│   │   └── session.py    # SQLAlchemy сессия
│   ├── models/           # Модели SQLAlchemy
│   │   └── user.py       # User, RefreshToken, перечисления
│   ├── routes/           # Роутеры FastAPI
│   │   ├── auth.py       # /auth/*
│   │   └── users.py      # /users/*
│   ├── schemas/          # Pydantic-схемы
│   │   ├── auth.py       # Запросы/ответы аутентификации
│   │   └── user.py       # Схемы пользователей
│   ├── services/         # Бизнес-логика
│   │   └── auth_service.py
│   └── main.py           # Точка входа
├── tests/                # Тесты
│   ├── conftest.py       # Фикстуры
│   ├── test_models.py    # Модели
│   ├── test_schemas.py   # Схемы
│   ├── test_security.py  # Безопасность
│   ├── test_auth_routes.py   # Эндпоинты /auth
│   └── test_users_routes.py  # Эндпоинты /users
├── .env.example          # Шаблон конфигурации
├── .gitignore
├── alembic.ini
├── requirements.txt
└── Dockerfile
```
