from app.models.user import UserStatus, UserRole, User


class TestUserStatus:
    def test_active_value(self):
        assert UserStatus.ACTIVE == "active"

    def test_inactive_value(self):
        assert UserStatus.INACTIVE == "inactive"

    def test_only_two_statuses(self):
        assert len(UserStatus) == 2

    def test_string_coercion(self):
        assert str(UserStatus.ACTIVE) == "UserStatus.ACTIVE"


class TestUserRole:
    def test_admin_value(self):
        assert UserRole.ADMIN == "admin"

    def test_manager_value(self):
        assert UserRole.MANAGER == "manager"

    def test_user_value(self):
        assert UserRole.USER == "user"

    def test_only_three_roles(self):
        assert len(UserRole) == 3


class TestUserModel:
    def test_default_status(self, db_session):
        user = User(
            email="status_test@example.com",
            username="statustest",
            hashed_password="hash",
        )
        db_session.add(user)
        db_session.flush()
        assert user.status == UserStatus.ACTIVE

    def test_default_role(self, db_session):
        user = User(
            email="role_test@example.com",
            username="roletest",
            hashed_password="hash",
        )
        db_session.add(user)
        db_session.flush()
        assert user.role == UserRole.USER

    def test_default_is_active(self, db_session):
        user = User(
            email="active_test@example.com",
            username="activetest",
            hashed_password="hash",
        )
        db_session.add(user)
        db_session.flush()
        assert user.is_active is True

    def test_repr(self, db_session):
        user = User(
            email="test@example.com",
            username="testuser",
            hashed_password="hash",
        )
        assert repr(user) == "<User testuser>"

    def test_persist_and_retrieve(self, db_session):
        user = User(
            email="persist_test@example.com",
            username="persisttest",
            hashed_password="hash",
            full_name="Test User",
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        retrieved = db_session.query(User).filter(User.email == "persist_test@example.com").first()
        assert retrieved is not None
        assert retrieved.username == "persisttest"
        assert retrieved.status == UserStatus.ACTIVE
        assert retrieved.role == UserRole.USER
