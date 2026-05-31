from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime
from ..models.user import UserRole


class TokenResponse(BaseModel):
    """Ответ с токенами"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int

    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIs...",
                "refresh_token": "eyJhbGciOiJIUzI1NiIs...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class LoginRequest(BaseModel):
    """Запрос на вход"""
    username: str = Field(..., min_length=4, max_length=100, description="Имя пользователя или email")
    password: str = Field(..., min_length=4, max_length=128)
    remember_me: bool = Field(False, description="Продлить время жизни refresh токена")

    class Config:
        json_schema_extra = {
            "example": {
                "username": "john_doe",
                "password": "StrongP@ssw0rd",
                "remember_me": True
            }
        }


class RegisterRequest(BaseModel):
    """Запрос на регистрацию"""
    email: EmailStr
    username: str = Field(..., min_length=4, max_length=100)
    password: str = Field(..., min_length=4, max_length=128)
    password_confirm: str
    full_name: Optional[str] = Field(None, max_length=255)
    role: UserRole = Field(UserRole.USER, description="Роль пользователя")

    @validator('username')
    def username_valid(cls, v):
        if len(v) < 4:
            raise ValueError('Имя пользователя должно быть не менее 4 символов')
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Имя пользователя должно содержать только буквы, цифры, - и _')
        return v.lower()

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Пароли не совпадают')
        return v

    @validator('password')
    def password_latin(cls, v):
        if not all(c.isascii() and (c.isalpha() or c.isdigit() or c in '!@#$%^&*()_+-=[]{}|;:,.<>?') for c in v):
            raise ValueError('Пароль должен содержать только латиницу, цифры и спецсимволы')
        return v

    class Config:
        json_schema_extra = {
            "example": {
                "email": "john@example.com",
                "username": "john_doe",
                "password": "StrongP@ssw0rd",
                "password_confirm": "StrongP@ssw0rd",
                "full_name": "John Doe"
            }
        }


class TokenRefreshRequest(BaseModel):
    """Запрос на обновление токена"""
    refresh_token: str

    class Config:
        json_schema_extra = {
            "example": {
                "refresh_token": "eyJhbGciOiJIUzI1NiIs..."
            }
        }


class PasswordChangeRequest(BaseModel):
    """Запрос на смену пароля"""
    current_password: str
    new_password: str = Field(..., min_length=8, max_length=128)
    new_password_confirm: str

    @validator('new_password_confirm')
    def passwords_match(cls, v, values):
        if 'new_password' in values and v != values['new_password']:
            raise ValueError('Passwords do not match')
        return v


class PasswordResetRequest(BaseModel):
    """Запрос на сброс пароля"""
    email: EmailStr


class PasswordResetConfirm(BaseModel):
    """Подтверждение сброса пароля"""
    token: str
    new_password: str
    new_password_confirm: str