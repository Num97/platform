import pytest
from pydantic import ValidationError
from app.schemas.auth import RegisterRequest, LoginRequest, PasswordChangeRequest


class TestRegisterRequest:
    def test_valid_data(self):
        data = {
            "email": "test@example.com",
            "username": "john_doe",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        }
        req = RegisterRequest(**data)
        assert req.email == "test@example.com"
        assert req.username == "john_doe"

    def test_username_to_lowercase(self):
        data = {
            "email": "test@example.com",
            "username": "John_Doe",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        }
        req = RegisterRequest(**data)
        assert req.username == "john_doe"

    def test_username_too_short(self):
        data = {
            "email": "test@example.com",
            "username": "ab",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)

    def test_invalid_email(self):
        data = {
            "email": "not-an-email",
            "username": "john_doe",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)

    def test_passwords_do_not_match(self):
        data = {
            "email": "test@example.com",
            "username": "john_doe",
            "password": "StrongP@ss1",
            "password_confirm": "DifferentP@ss1",
        }
        with pytest.raises(ValidationError) as exc:
            RegisterRequest(**data)
        errors = exc.value.errors()
        assert any("Passwords do not match" in str(e["msg"]) for e in errors)

    def test_password_no_uppercase(self):
        data = {
            "email": "test@example.com",
            "username": "john_doe",
            "password": "weakpass1!",
            "password_confirm": "weakpass1!",
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)

    def test_password_no_lowercase(self):
        data = {
            "email": "test@example.com",
            "username": "john_doe",
            "password": "STRONGPASS1!",
            "password_confirm": "STRONGPASS1!",
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)

    def test_password_no_digit(self):
        data = {
            "email": "test@example.com",
            "username": "john_doe",
            "password": "StrongPass!",
            "password_confirm": "StrongPass!",
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)

    def test_password_no_special_char(self):
        data = {
            "email": "test@example.com",
            "username": "john_doe",
            "password": "StrongPass1",
            "password_confirm": "StrongPass1",
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)

    def test_password_too_short(self):
        data = {
            "email": "test@example.com",
            "username": "john_doe",
            "password": "Sh@rt1",
            "password_confirm": "Sh@rt1",
        }
        with pytest.raises(ValidationError):
            RegisterRequest(**data)


class TestLoginRequest:
    def test_valid_data(self):
        data = {
            "username": "john_doe",
            "password": "StrongP@ssw0rd",
        }
        req = LoginRequest(**data)
        assert req.username == "john_doe"
        assert req.password == "StrongP@ssw0rd"
        assert req.remember_me is False

    def test_remember_me_true(self):
        data = {
            "username": "john_doe",
            "password": "StrongP@ssw0rd",
            "remember_me": True,
        }
        req = LoginRequest(**data)
        assert req.remember_me is True

    def test_username_too_short(self):
        data = {
            "username": "ab",
            "password": "StrongP@ssw0rd",
        }
        with pytest.raises(ValidationError):
            LoginRequest(**data)


class TestPasswordChangeRequest:
    def test_valid_data(self):
        data = {
            "current_password": "OldP@ss1",
            "new_password": "NewStr0ng!",
            "new_password_confirm": "NewStr0ng!",
        }
        req = PasswordChangeRequest(**data)
        assert req.current_password == "OldP@ss1"

    def test_passwords_do_not_match(self):
        data = {
            "current_password": "OldP@ss1",
            "new_password": "NewStr0ng!",
            "new_password_confirm": "Different!",
        }
        with pytest.raises(ValidationError):
            PasswordChangeRequest(**data)
