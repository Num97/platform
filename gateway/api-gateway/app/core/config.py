from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv(encoding="utf-8")


class Settings(BaseSettings):
    model_config = SettingsConfigDict(case_sensitive=True)

    PROJECT_NAME: str = "API Gateway"
    VERSION: str = "1.0.0"
    DEBUG: bool = True

    GATEWAY_HOST: str = "0.0.0.0"
    GATEWAY_PORT: int = 8000

    SECRET_KEY: str = "change-me-in-production-use-env-or-env-file"
    ALGORITHM: str = "HS256"

    AUTH_SERVICE_URL: str = "http://auth-service:8001"

    RATE_LIMIT_ENABLED: bool = True
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 60

    BACKEND_CORS_ORIGINS: list[str] = ["http://localhost:3000", "http://localhost:80", "http://localhost"]


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
