from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole, UserStatus
from app.schemas.user import UserUpdateRequest
from app.core.dependencies import get_current_admin_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Получить всех пользователей (только для админа)"""
    users = db.query(User).all()
    return users


@router.get("/{user_id}")
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_admin_user),
):
    """Получить пользователя по ID (только для админа)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )
    return user


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db),
):
    """Обновить пользователя (роль, статус, email, имя) — только для админа"""
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Пользователь не найден"
        )

    if update_data.email is not None:
        existing = db.query(User).filter(
            User.email == update_data.email, User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email уже используется"
            )
        target_user.email = update_data.email

    if update_data.full_name is not None:
        target_user.full_name = update_data.full_name

    if update_data.role is not None:
        target_user.role = UserRole(update_data.role)

    if update_data.is_active is not None:
        target_user.is_active = update_data.is_active
        target_user.status = UserStatus.ACTIVE if update_data.is_active else UserStatus.INACTIVE

    db.commit()
    db.refresh(target_user)
    return target_user
