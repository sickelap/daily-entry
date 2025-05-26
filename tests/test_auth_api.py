from uuid import UUID

from fastapi.testclient import TestClient
from sqlmodel import Session, select


from app import config
from .conftest import TEST_USER_PASSWORD, TEST_USER_EMAIL
from app.model import UserEntity


def isuuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except Exception:
        return False


def login_user(client, email=TEST_USER_EMAIL, password=TEST_USER_PASSWORD):
    payload = {"email": email, "password": password}
    response = client.post(f"{config.API_PREFIX}{config.LOGIN_URI}", json=payload)
    return response.json()


def test_register_user(client: TestClient, session: Session):
    payload = {"email": "user@local.host", "password": "userpw"}
    response = client.post(f"{config.API_PREFIX}{config.REGISTER_URI}", json=payload)
    assert response.status_code == 200
    assert len(response.json().keys()) == 2
    assert "access_token" in response.json().keys()
    assert "refresh_token" in response.json().keys()
    user_in_db = session.exec(
        select(UserEntity).where(UserEntity.email == "user@local.host")
    ).one_or_none()
    assert user_in_db is not None


def test_register_user_with_same_email(client: TestClient):
    payload = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    response = client.post(f"{config.API_PREFIX}{config.REGISTER_URI}", json=payload)
    assert response.status_code == 409


def test_login_user(client: TestClient):
    payload = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    response = client.post(f"{config.API_PREFIX}{config.LOGIN_URI}", json=payload)
    assert response.status_code == 200
    assert len(response.json().keys()) == 2
    assert "access_token" in response.json().keys()
    assert "refresh_token" in response.json().keys()


def test_login_user_with_invalid_credentials(client: TestClient):
    payload = {"email": "bob@bob.inc", "password": "bobpw"}
    response = client.post(f"{config.API_PREFIX}{config.LOGIN_URI}", json=payload)
    assert response.status_code == 401


def test_refresh_token(client):
    tokens = login_user(client)
    response = client.post(
        f"{config.API_PREFIX}{config.REFRESH_TOKEN_URI}",
        headers={"Authorization": f"Bearer {tokens['refresh_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["access_token"] != tokens["access_token"]
    assert response.json()["refresh_token"] != tokens["refresh_token"]


def test_refresh_with_access_token(client):
    tokens = login_user(client)
    response = client.post(
        f"{config.API_PREFIX}{config.REFRESH_TOKEN_URI}",
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 403
