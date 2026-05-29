from fastapi import APIRouter, Depends, HTTPException, status, Body
from fastapi.security import HTTPBearer
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import (
    LoginRequest,
    RegisterRequest,
    TokenResponse,
    TokenRefreshRequest,
    PasswordChangeRequest,
    PasswordResetRequest,
    PasswordResetConfirm,
)
from app.core.dependencies import get_current_active_user
from app.models.user import UserStatus
from app.models.user import User
from typing import Dict, Any

router = APIRouter(tags=["authentication"])


@router.post("/register", response_model=Dict[str, Any], status_code=status.HTTP_201_CREATED)
async def register(
        register_data: RegisterRequest,
        db: Session = Depends(get_db)
):
    """
    Регистрация нового пользователя

    - **email**: Email пользователя
    - **username**: Уникальное имя пользователя
    - **password**: Пароль (мин. 8 символов, заглавные, строчные, цифры, спецсимволы)
    """
    auth_service = AuthService(db)
    user = auth_service.register_user(register_data)

    return {
        "message": "User registered successfully",
        "user_id": user.id,
        "email": user.email,
        "username": user.username,
    }


@router.post("/login", response_model=TokenResponse)
async def login(
        login_data: LoginRequest,
        db: Session = Depends(get_db)
):
    """
    Вход в систему

    Возвращает access и refresh токены.
    Access токен используется для доступа к API.
    Refresh токен используется для получения нового access токена.
    """
    auth_service = AuthService(db)

    # Аутентификация пользователя
    user = auth_service.authenticate_user(login_data)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username/email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.status == UserStatus.INACTIVE:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is inactive"
        )

    # Создание токенов
    tokens = auth_service.create_tokens(user, login_data.remember_me)

    return tokens


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
        refresh_data: TokenRefreshRequest,
        db: Session = Depends(get_db)
):
    """
    Обновление access токена

    Используйте refresh токен для получения нового access токена.
    Старый refresh токен будет отозван (ротация токенов).
    """
    auth_service = AuthService(db)

    try:
        tokens = auth_service.refresh_access_token(refresh_data.refresh_token)
        return tokens
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Token refresh failed: {str(e)}"
        )


@router.post("/logout")
async def logout(
        refresh_data: TokenRefreshRequest,
        db: Session = Depends(get_db)
):
    """
    Выход из системы

    Отзывает refresh токен. Access токен продолжит работать до истечения срока.
    """
    auth_service = AuthService(db)

    success = auth_service.revoke_refresh_token(refresh_data.refresh_token)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid refresh token"
        )

    return {"message": "Successfully logged out"}


@router.post("/logout-all")
async def logout_all(
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Выход со всех устройств

    Отзывает все активные refresh токены пользователя.
    """
    auth_service = AuthService(db)
    auth_service.revoke_all_user_tokens(current_user.id)

    return {"message": "Successfully logged out from all devices"}


@router.post("/change-password")
async def change_password(
        password_data: PasswordChangeRequest,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """
    Смена пароля текущего пользователя
    """
    auth_service = AuthService(db)

    # Проверка текущего пароля
    if not auth_service.security.verify_password(
            password_data.current_password,
            current_user.hashed_password
    ):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Current password is incorrect"
        )

    # Обновление пароля
    current_user.hashed_password = auth_service.security.get_password_hash(
        password_data.new_password
    )
    db.commit()

    # Отзыв всех токенов для безопасности
    auth_service.revoke_all_user_tokens(current_user.id)

    return {"message": "Password changed successfully. Please login again."}


@router.post("/forgot-password")
async def forgot_password(
        reset_data: PasswordResetRequest,
        db: Session = Depends(get_db)
):
    """
    Запрос на сброс пароля

    Отправляет токен для сброса пароля на email пользователя.
    """
    auth_service = AuthService(db)
    user = auth_service.get_user_by_email(reset_data.email)

    if user:
        # Генерация токена для сброса пароля
        reset_token = auth_service.security.create_password_reset_token()
        user.password_reset_token = reset_token
        user.password_reset_expires = datetime.utcnow() + timedelta(hours=1)
        db.commit()

        # TODO: Отправить email с токеном
        # send_password_reset_email(user.email, reset_token)

    # Всегда возвращаем одинаковый ответ (предотвращаем утечку информации)
    return {
        "message": "If the email exists, a password reset link has been sent"
    }


@router.post("/reset-password")
async def reset_password(
        reset_data: PasswordResetConfirm,
        db: Session = Depends(get_db)
):
    """
    Сброс пароля по токену
    """
    # Поиск пользователя по токену
    user = db.query(User).filter(
        User.password_reset_token == reset_data.token,
        User.password_reset_expires > datetime.utcnow()
    ).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )

    # Обновление пароля
    auth_service = AuthService(db)
    user.hashed_password = auth_service.security.get_password_hash(reset_data.new_password)
    user.password_reset_token = None
    user.password_reset_expires = None

    # Отзыв всех токенов
    auth_service.revoke_all_user_tokens(user.id)

    db.commit()

    return {"message": "Password reset successfully. Please login with your new password."}


@router.get("/verify-token")
async def verify_token(
        current_user: User = Depends(get_current_active_user)
):
    """
    Проверка валидности токена

    Используется для проверки авторизации на фронтенде.
    """
    return {
        "valid": True,
        "user_id": current_user.id,
        "username": current_user.username,
        "role": current_user.role.value
    }


@router.get("/me")
async def get_current_user_info(
        current_user: User = Depends(get_current_active_user)
):
    """
    Получение информации о текущем пользователе
    """
    return {
        "id": current_user.id,
        "email": current_user.email,
        "username": current_user.username,
        "full_name": current_user.full_name,
        "role": current_user.role.value,
        "status": current_user.status.value,
        "created_at": current_user.created_at,
        "last_login": current_user.last_login
    }