from app.models.user import User, UserRole, UserStatus


class TestRegister:
    def test_register_success(self, client, db_session):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        assert response.status_code == 201
        data = response.json()
        assert data["message"] == "User registered successfully"
        assert data["user_id"] is not None
        assert data["email"] == "test@example.com"
        assert data["username"] == "testuser"

    def test_register_duplicate_email(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "username": "user1",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        response = client.post("/api/v1/auth/register", json={
            "email": "dup@example.com",
            "username": "user2",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        assert response.status_code == 400
        assert "Email already registered" in response.json()["detail"]

    def test_register_duplicate_username(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "a@example.com",
            "username": "duplicate",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        response = client.post("/api/v1/auth/register", json={
            "email": "b@example.com",
            "username": "duplicate",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        assert response.status_code == 400
        assert "Username already taken" in response.json()["detail"]

    def test_register_weak_password(self, client, db_session):
        response = client.post("/api/v1/auth/register", json={
            "email": "test@example.com",
            "username": "testuser",
            "password": "weak",
            "password_confirm": "weak",
        })
        assert response.status_code == 422


class TestLogin:
    def test_login_success(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "login@example.com",
            "username": "loginuser",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        response = client.post("/api/v1/auth/login", json={
            "username": "loginuser",
            "password": "StrongP@ss1",
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_with_email(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "emaillogin@example.com",
            "username": "elogin",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        response = client.post("/api/v1/auth/login", json={
            "username": "emaillogin@example.com",
            "password": "StrongP@ss1",
        })
        assert response.status_code == 200

    def test_login_wrong_password(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "wrong@example.com",
            "username": "wrongpass",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        response = client.post("/api/v1/auth/login", json={
            "username": "wrongpass",
            "password": "WrongPassword1!",
        })
        assert response.status_code == 401

    def test_login_nonexistent_user(self, client, db_session):
        response = client.post("/api/v1/auth/login", json={
            "username": "nonexistent",
            "password": "SomePass1!",
        })
        assert response.status_code == 401

    def test_login_inactive_user(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "inactive@example.com",
            "username": "inactive",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        user = db_session.query(User).filter(User.username == "inactive").first()
        user.status = UserStatus.INACTIVE
        db_session.commit()

        response = client.post("/api/v1/auth/login", json={
            "username": "inactive",
            "password": "StrongP@ss1",
        })
        assert response.status_code == 403
        assert "Account is inactive" in response.json()["detail"]


class TestTokenRefresh:
    def test_refresh_success(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "refresh@example.com",
            "username": "refreshuser",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "refreshuser",
            "password": "StrongP@ss1",
        })
        refresh_token = login_resp.json()["refresh_token"]

        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data

    def test_refresh_invalid_token(self, client, db_session):
        response = client.post("/api/v1/auth/refresh", json={
            "refresh_token": "invalid.token.here",
        })
        assert response.status_code == 401


class TestLogout:
    def test_logout_success(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "logout@example.com",
            "username": "logoutuser",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "logoutuser",
            "password": "StrongP@ss1",
        })
        refresh_token = login_resp.json()["refresh_token"]

        response = client.post("/api/v1/auth/logout", json={
            "refresh_token": refresh_token,
        })
        assert response.status_code == 200
        assert response.json()["message"] == "Successfully logged out"

    def test_logout_invalid_token(self, client, db_session):
        response = client.post("/api/v1/auth/logout", json={
            "refresh_token": "invalid.token",
        })
        assert response.status_code == 400


class TestMe:
    def test_me_success(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "me@example.com",
            "username": "meuser",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "meuser",
            "password": "StrongP@ss1",
        })
        token = login_resp.json()["access_token"]

        response = client.get("/api/v1/auth/me", headers={
            "Authorization": f"Bearer {token}",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["username"] == "meuser"
        assert data["email"] == "me@example.com"
        assert data["role"] == "user"
        assert data["status"] == "active"

    def test_me_no_auth(self, client, db_session):
        response = client.get("/api/v1/auth/me")
        assert response.status_code == 401


class TestVerifyToken:
    def test_verify_token_valid(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "verify@example.com",
            "username": "verifyuser",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "verifyuser",
            "password": "StrongP@ss1",
        })
        token = login_resp.json()["access_token"]

        response = client.get("/api/v1/auth/verify-token", headers={
            "Authorization": f"Bearer {token}",
        })
        assert response.status_code == 200
        data = response.json()
        assert data["valid"] is True
        assert data["username"] == "verifyuser"


class TestChangePassword:
    def test_change_password_success(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "changepass@example.com",
            "username": "changepass",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "changepass",
            "password": "StrongP@ss1",
        })
        token = login_resp.json()["access_token"]

        response = client.post("/api/v1/auth/change-password", json={
            "current_password": "StrongP@ss1",
            "new_password": "NewStr0ngP@ss!",
            "new_password_confirm": "NewStr0ngP@ss!",
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 200

        login_resp2 = client.post("/api/v1/auth/login", json={
            "username": "changepass",
            "password": "NewStr0ngP@ss!",
        })
        assert login_resp2.status_code == 200

    def test_change_password_wrong_current(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "wrongcurr@example.com",
            "username": "wrongcurr",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        login_resp = client.post("/api/v1/auth/login", json={
            "username": "wrongcurr",
            "password": "StrongP@ss1",
        })
        token = login_resp.json()["access_token"]

        response = client.post("/api/v1/auth/change-password", json={
            "current_password": "WrongPass1!",
            "new_password": "NewStr0ngP@ss!",
            "new_password_confirm": "NewStr0ngP@ss!",
        }, headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 400
