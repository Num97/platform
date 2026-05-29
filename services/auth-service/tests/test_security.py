import time
from datetime import timedelta
from app.core.security import SecurityService


class TestPasswordHashing:
    def test_hash_password(self):
        password = "SecretP@ss1"
        hashed = SecurityService.get_password_hash(password)
        assert hashed != password
        assert hashed.startswith("$2b$")

    def test_verify_correct_password(self):
        password = "SecretP@ss1"
        hashed = SecurityService.get_password_hash(password)
        assert SecurityService.verify_password(password, hashed) is True

    def test_verify_wrong_password(self):
        password = "SecretP@ss1"
        hashed = SecurityService.get_password_hash(password)
        assert SecurityService.verify_password("WrongPass1!", hashed) is False

    def test_different_hashes_for_same_password(self):
        password = "SecretP@ss1"
        hash1 = SecurityService.get_password_hash(password)
        hash2 = SecurityService.get_password_hash(password)
        assert hash1 != hash2


class TestTokenCreation:
    def test_create_access_token(self):
        data = {"sub": "1", "username": "test"}
        token = SecurityService.create_access_token(data, expires_delta=timedelta(minutes=15))
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token(self):
        data = {"sub": "1", "type": "refresh"}
        token = SecurityService.create_refresh_token(data, remember_me=False)
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_refresh_token_remember_me(self):
        data = {"sub": "1", "type": "refresh"}
        token = SecurityService.create_refresh_token(data, remember_me=True)
        assert isinstance(token, str)
        assert len(token) > 0


class TestTokenDecoding:
    def test_decode_valid_access_token(self):
        data = {"sub": "1", "username": "testuser", "role": "user"}
        token = SecurityService.create_access_token(data, expires_delta=timedelta(minutes=15))
        payload = SecurityService.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["username"] == "testuser"
        assert payload["type"] == "access"

    def test_decode_valid_refresh_token(self):
        data = {"sub": "1", "type": "refresh"}
        token = SecurityService.create_refresh_token(data)
        payload = SecurityService.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "1"
        assert payload["type"] == "refresh"

    def test_decode_expired_token(self):
        data = {"sub": "1"}
        token = SecurityService.create_access_token(data, expires_delta=timedelta(seconds=-1))
        payload = SecurityService.decode_token(token)
        assert payload is None

    def test_decode_invalid_token(self):
        payload = SecurityService.decode_token("invalid.token.here")
        assert payload is None

    def test_decode_empty_token(self):
        payload = SecurityService.decode_token("")
        assert payload is None


class TestPasswordResetToken:
    def test_create_reset_token(self):
        token = SecurityService.create_password_reset_token()
        assert isinstance(token, str)
        assert len(token) > 0

    def test_reset_tokens_are_unique(self):
        token1 = SecurityService.create_password_reset_token()
        token2 = SecurityService.create_password_reset_token()
        assert token1 != token2
