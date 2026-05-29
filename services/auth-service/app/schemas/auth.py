from pydantic import BaseModel, EmailStr, Field, validator
from typing import Optional
from datetime import datetime


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
    username: str = Field(..., min_length=3, max_length=100, description="Username or email")
    password: str = Field(..., min_length=8, max_length=128)
    remember_me: bool = Field(False, description="Extend refresh token lifetime")

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
    username: str = Field(..., min_length=3, max_length=100, pattern=r"^[a-zA-Z0-9_-]+$")
    password: str = Field(..., min_length=8, max_length=128)
    password_confirm: str
    full_name: Optional[str] = Field(None, max_length=255)

    @validator('username')
    def username_alphanumeric(cls, v):
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Username must be alphanumeric')
        return v.lower()

    @validator('password_confirm')
    def passwords_match(cls, v, values):
        if 'password' in values and v != values['password']:
            raise ValueError('Passwords do not match')
        return v

    @validator('password')
    def password_strength(cls, v):
        if not any(c.isupper() for c in v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not any(c.islower() for c in v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not any(c.isdigit() for c in v):
            raise ValueError('Password must contain at least one digit')
        if not any(c in '!@#$%^&*()_+-=[]{}|;:,.<>?' for c in v):
            raise ValueError('Password must contain at least one special character')
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