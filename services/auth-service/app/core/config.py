from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv(encoding="utf-8")


class Settings(BaseSettings):
    # Project
    PROJECT_NAME: str = "Auth Service"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1/auth"
    DEBUG: bool = True

    # Database
    DATABASE_URL: str = "postgresql+psycopg2://user:pass@localhost:5432/db"

    # JWT
    SECRET_KEY: str = "change-me-in-production-use-env-or-env-file"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # Service Discovery
    SERVICE_NAME: str = "auth-service"
    SERVICE_HOST: str = "0.0.0.0"
    SERVICE_PORT: int = 8001

    class Config:
        case_sensitive = True


@lru_cache()
def get_settings() -> Settings:
    return Settings()


settings = get_settings()