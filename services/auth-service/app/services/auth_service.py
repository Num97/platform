from typing import Optional, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User, RefreshToken
from app.core.security import SecurityService
from app.core.config import settings
from app.schemas.auth import RegisterRequest, LoginRequest


class AuthService:
    """Сервис аутентификации и авторизации"""

    def __init__(self, db: Session):
        self.db = db
        self.security = SecurityService()

    def register_user(self, register_data: RegisterRequest) -> User:
        """
        Регистрация нового пользователя

        Args:
            register_data: Данные для регистрации

        Returns:
            Созданный пользователь

        Raises:
            HTTPException: Если пользователь уже существует
        """
        # Проверка существования пользователя
        if self.get_user_by_email(register_data.email):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже зарегистрирован"
            )

        if self.get_user_by_username(register_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Имя пользователя уже занято"
            )

        # Создание пользователя
        user = User(
            email=register_data.email,
            username=register_data.username,
            hashed_password=self.security.get_password_hash(register_data.password),
            full_name=register_data.full_name,
            role=register_data.role,
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)

        return user

    def authenticate_user(self, login_data: LoginRequest) -> Optional[User]:
        """
        Аутентификация пользователя

        Args:
            login_data: Данные для входа

        Returns:
            Пользователь или None
        """
        # Проверяем, является ли username email'ом
        user = self.get_user_by_email(login_data.username)
        if not user:
            user = self.get_user_by_username(login_data.username)

        if not user:
            return None

        if not self.security.verify_password(login_data.password, user.hashed_password):
            return None

        return user

    def create_tokens(self, user: User, remember_me: bool = False) -> dict:
        """
        Создание пары токенов (access + refresh)

        Args:
            user: Пользователь
            remember_me: Продлить время жизни refresh токена

        Returns:
            Словарь с токенами
        """
        # Данные для токенов
        token_data = {
            "sub": str(user.id),
            "username": user.username,
            "email": user.email,
            "role": user.role.value
        }

        # Создание access токена
        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = self.security.create_access_token(
            data=token_data,
            expires_delta=access_token_expires
        )

        # Создание refresh токена
        refresh_token = self.security.create_refresh_token(
            data={"sub": str(user.id), "type": "refresh"},
            remember_me=remember_me
        )

        # Сохранение refresh токена в БД
        db_refresh_token = RefreshToken(
            token=refresh_token,
            user_id=user.id,
            expires_at=datetime.utcnow() + timedelta(
                days=settings.REFRESH_TOKEN_EXPIRE_DAYS * (2 if remember_me else 1)
            )
        )
        self.db.add(db_refresh_token)
        self.db.commit()

        # Обновление last_login
        user.last_login = datetime.utcnow()
        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int(access_token_expires.total_seconds())
        }

    def refresh_access_token(self, refresh_token: str) -> dict:
        """
        Обновление access токена по refresh токену

        Args:
            refresh_token: Refresh токен

        Returns:
            Новые токены
        """
        # Декодируем refresh токен
        payload = self.security.decode_token(refresh_token)
        if not payload or payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Недействительный refresh токен"
            )

        # Проверяем существование токена в БД
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token,
            RefreshToken.is_revoked == False
        ).first()

        if not db_token:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Refresh токен не найден или отозван"
            )

        # Проверяем не истек ли токен
        if db_token.expires_at < datetime.utcnow():
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Срок действия refresh токена истёк"
            )

        # Получаем пользователя
        user = self.get_user_by_id(db_token.user_id)
        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Пользователь не найден или неактивен"
            )

        # Отзываем старый refresh токен (ротация)
        db_token.is_revoked = True

        # Создаем новые токены
        return self.create_tokens(user)

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """Отзыв refresh токена (logout)"""
        db_token = self.db.query(RefreshToken).filter(
            RefreshToken.token == refresh_token
        ).first()

        if db_token:
            db_token.is_revoked = True
            self.db.commit()
            return True
        return False

    def revoke_all_user_tokens(self, user_id: int) -> None:
        """Отзыв всех refresh токенов пользователя"""
        self.db.query(RefreshToken).filter(
            RefreshToken.user_id == user_id,
            RefreshToken.is_revoked == False
        ).update({"is_revoked": True})
        self.db.commit()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Получение пользователя по ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Получение пользователя по email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Получение пользователя по username"""
        return self.db.query(User).filter(User.username == username).first()