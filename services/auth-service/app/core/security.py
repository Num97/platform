from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import JWTError, jwt
from passlib.context import CryptContext
from app.core.config import settings

# Контекст для хеширования паролей
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class SecurityService:
    """Сервис безопасности"""

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Проверка пароля"""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Хеширование пароля"""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: Dict[str, Any], expires_delta: Optional[timedelta] = None) -> str:
        """
        Создание JWT access токена

        Args:
            data: Данные для включения в токен
            expires_delta: Время жизни токена

        Returns:
            Закодированный JWT токен
        """
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "access",
            "jti": SecurityService._generate_token_id()
        })

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def create_refresh_token(data: Dict[str, Any], remember_me: bool = False) -> str:
        """
        Создание refresh токена

        Args:
            data: Данные для включения в токен
            remember_me: Продлить время жизни токена

        Returns:
            Закодированный refresh токен
        """
        to_encode = data.copy()

        # Долгоживущий токен если remember_me
        expire_days = settings.REFRESH_TOKEN_EXPIRE_DAYS * 2 if remember_me else settings.REFRESH_TOKEN_EXPIRE_DAYS
        expire = datetime.utcnow() + timedelta(days=expire_days)

        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "type": "refresh",
            "jti": SecurityService._generate_token_id()
        })

        return jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        """
        Декодирование JWT токена

        Args:
            token: JWT токен

        Returns:
            Декодированные данные или None
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM],
                options={"verify_exp": True}
            )
            return payload
        except JWTError as e:
            print(f"Token decode error: {e}")
            return None

    @staticmethod
    def _generate_token_id() -> str:
        """Генерация уникального ID токена"""
        import uuid
        return str(uuid.uuid4())

    @staticmethod
    def create_password_reset_token() -> str:
        """Создание токена для сброса пароля"""
        import secrets
        return secrets.token_urlsafe(32)