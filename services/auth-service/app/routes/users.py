from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.models.user import User, UserRole
from app.schemas.user import UserUpdateRequest
from app.core.dependencies import get_current_active_user

router = APIRouter(prefix="/users", tags=["users"])


@router.get("/")
async def get_users(db: Session = Depends(get_db)):
    """Get all users"""
    users = db.query(User).all()
    return users


@router.get("/{user_id}")
async def get_user(user_id: int, db: Session = Depends(get_db)):
    """Get user by ID"""
    user = db.query(User).filter(User.id == user_id).first()
    return user


@router.put("/{user_id}")
async def update_user(
    user_id: int,
    update_data: UserUpdateRequest,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
):
    target_user = db.query(User).filter(User.id == user_id).first()
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    is_admin_or_manager = current_user.role in (UserRole.ADMIN, UserRole.MANAGER)
    is_self = current_user.id == user_id

    if not (is_admin_or_manager or is_self):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )

    if update_data.role is not None and not is_admin_or_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or manager can change role"
        )

    if update_data.is_active is not None and not is_admin_or_manager:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only admin or manager can change is_active"
        )

    if update_data.email is not None:
        existing = db.query(User).filter(
            User.email == update_data.email, User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already in use"
            )
        target_user.email = update_data.email

    if update_data.full_name is not None:
        target_user.full_name = update_data.full_name

    if update_data.role is not None:
        target_user.role = update_data.role

    if update_data.is_active is not None:
        target_user.is_active = update_data.is_active

    db.commit()
    db.refresh(target_user)
    return target_user
