class TestGetUsers:
    def test_get_all_users_empty(self, client, db_session):
        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        assert response.json() == []

    def test_get_all_users(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "u1@example.com",
            "username": "user1",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        client.post("/api/v1/auth/register", json={
            "email": "u2@example.com",
            "username": "user2",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })

        response = client.get("/api/v1/users/")
        assert response.status_code == 200
        users = response.json()
        assert len(users) == 2
        usernames = [u["username"] for u in users]
        assert "user1" in usernames
        assert "user2" in usernames


class TestGetUserById:
    def test_get_user_success(self, client, db_session):
        reg_resp = client.post("/api/v1/auth/register", json={
            "email": "getuser@example.com",
            "username": "getuser",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        user_id = reg_resp.json()["user_id"]

        response = client.get(f"/api/v1/users/{user_id}")
        assert response.status_code == 200
        assert response.json()["username"] == "getuser"
        assert response.json()["email"] == "getuser@example.com"

    def test_get_user_not_found(self, client, db_session):
        response = client.get("/api/v1/users/99999")
        assert response.status_code == 200
        assert response.json() is None


class TestForgotResetPassword:
    def test_forgot_password(self, client, db_session):
        client.post("/api/v1/auth/register", json={
            "email": "forgot@example.com",
            "username": "forgot",
            "password": "StrongP@ss1",
            "password_confirm": "StrongP@ss1",
        })
        response = client.post("/api/v1/auth/forgot-password", json={
            "email": "forgot@example.com",
        })
        assert response.status_code == 200

    def test_forgot_password_nonexistent_email(self, client, db_session):
        response = client.post("/api/v1/auth/forgot-password", json={
            "email": "nonexistent@example.com",
        })
        assert response.status_code == 200
