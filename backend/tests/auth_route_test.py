from uuid import uuid4

import pytest
from fastapi.testclient import TestClient

from app.dependencies.auth_dependencies import get_current_user
from app.main import app

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_current_user_override():
    app.dependency_overrides.pop(get_current_user, None)

    yield

    app.dependency_overrides.pop(get_current_user, None)


def unique_user_data():
    unique_id = uuid4().hex

    return {
        "email": f"authtest_{unique_id}@example.com",
        "username": f"authtestuser_{unique_id}",
        "password": "testpassword123",
    }


def register_test_user(
    email: str | None = None,
    username: str | None = None,
    password: str = "testpassword123",
):
    user_data = unique_user_data()

    if email is not None:
        user_data["email"] = email

    if username is not None:
        user_data["username"] = username

    user_data["password"] = password

    response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert response.status_code == 201

    return {
        "response": response.json(),
        "email": user_data["email"],
        "username": user_data["username"],
        "password": user_data["password"],
    }


def login_test_user(
    username: str,
    password: str,
):
    return client.post(
        "/auth/login",
        data={
            "username": username,
            "password": password,
        },
    )


def test_register_user():
    user_data = unique_user_data()

    response = client.post(
        "/auth/register",
        json=user_data,
    )

    assert response.status_code == 201

    data = response.json()
    assert data["email"] == user_data["email"]
    assert data["username"] == user_data["username"]
    assert "id" in data
    assert "password" not in data
    assert "password_hash" not in data


def test_register_duplicate_email_returns_409():
    user = register_test_user()

    response = client.post(
        "/auth/register",
        json={
            "email": user["email"],
            "username": f"different_username_{uuid4().hex}",
            "password": "testpassword123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email or username already exists."


def test_register_duplicate_username_returns_409():
    user = register_test_user()

    response = client.post(
        "/auth/register",
        json={
            "email": f"different_email_{uuid4().hex}@example.com",
            "username": user["username"],
            "password": "testpassword123",
        },
    )

    assert response.status_code == 409
    assert response.json()["detail"] == "User with this email or username already exists."


def test_login_with_username_returns_access_token():
    user = register_test_user()

    response = login_test_user(
        username=user["username"],
        password=user["password"],
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_email_returns_access_token():
    user = register_test_user()

    response = login_test_user(
        username=user["email"],
        password=user["password"],
    )

    assert response.status_code == 200

    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_with_wrong_password_returns_401():
    user = register_test_user()

    response = login_test_user(
        username=user["username"],
        password="wrongpassword",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username/email or password"


def test_login_with_missing_user_returns_401():
    response = login_test_user(
        username=f"missing_user_{uuid4().hex}",
        password="testpassword123",
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Incorrect username/email or password"


def test_auth_me_with_valid_token_returns_current_user():
    user = register_test_user()

    login_response = login_test_user(
        username=user["username"],
        password=user["password"],
    )

    assert login_response.status_code == 200

    token = login_response.json()["access_token"]

    response = client.get(
        "/auth/me",
        headers={
            "Authorization": f"Bearer {token}",
        },
    )

    assert response.status_code == 200

    data = response.json()
    assert data["id"] == user["response"]["id"]
    assert data["email"] == user["email"]
    assert data["username"] == user["username"]
    assert "password" not in data
    assert "password_hash" not in data


def test_auth_me_without_token_returns_401():
    response = client.get("/auth/me")

    assert response.status_code == 401


def test_auth_me_with_invalid_token_returns_401():
    response = client.get(
        "/auth/me",
        headers={
            "Authorization": "Bearer invalidtoken",
        },
    )

    assert response.status_code == 401
    assert response.json()["detail"] == "Could not validate credentials"