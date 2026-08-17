from uuid import uuid4

import pytest

from app.database import Base, get_db
from app.dependencies.auth_dependencies import get_current_user
from app.main import app
from app.models import User
from tests.test_database import TestingSessionLocal, test_engine


def override_get_db():
    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture
def test_user() -> User:
    db = TestingSessionLocal()

    try:
        unique_id = uuid4().hex

        user = User(
            email=f"testuser_{unique_id}@example.com",
            username=f"testuser_{unique_id}",
            password_hash="fake_hashed_password",
        )

        db.add(user)
        db.commit()
        db.refresh(user)
        db.expunge(user)

        return user

    finally:
        db.close()


@pytest.fixture
def override_current_user(test_user):
    def _override_get_current_user():
        return test_user

    app.dependency_overrides[get_current_user] = _override_get_current_user

    yield test_user

    app.dependency_overrides.pop(get_current_user, None)


@pytest.fixture(autouse=True)
def setup_test_database():
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    yield

    Base.metadata.drop_all(bind=test_engine)