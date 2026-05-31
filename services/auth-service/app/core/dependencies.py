from typing import Optional
from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.core.security import SecurityService
from app.models.user import User
from app.services.auth_service import AuthService

security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
        authorization: Optional[HTTPAuthorizationCredentials] = Depends(security_scheme),
        x_api_key: Optional[str] = Header(None),
        db: Session = Depends(get_db)
) -> User:
    """
    Получение текущего пользователя из токена.

    Поддерживает:
    - Bearer токен в Authorization заголовке
    - API ключ для сервис-сервис взаимодействия
    """
    # Проверка API ключа для межсервисного взаимодействия
    if x_api_key:
        # TODO: Реализовать проверку API ключей
        pass

    # Проверка Bearer токена
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Не авторизован",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authorization.credentials
    payload = SecurityService.decode_token(token)

    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительные учётные данные",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Проверка типа токена
    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Неверный тип токена"
        )

    user_id = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Недействительный токен"
        )

    # Получение пользователя
    auth_service = AuthService(db)
    user = auth_service.get_user_by_id(int(user_id))

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Пользователь не найден"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )

    return user


async def get_current_active_user(
        current_user: User = Depends(get_current_user)
) -> User:
    """Проверка что пользователь активен"""
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Пользователь неактивен"
        )
    return current_user


async def get_current_admin_user(
        current_user: User = Depends(get_current_active_user)
) -> User:
    """Проверка что пользователь администратор"""
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user


async def get_current_manager_or_admin(
        current_user: User = Depends(get_current_active_user)
) -> User:
    """Проверка что пользователь менеджер или администратор"""
    if current_user.role not in ("admin", "manager"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Недостаточно прав"
        )
    return current_user