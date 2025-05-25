from uuid import UUID


from app import config
from app.model import UserEntity
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from tests.conftest import (
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
)


def isuuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except Exception:
        return False


def test_register_user(client: TestClient, session: Session):
    payload = {"email": "user@local.host", "password": "userpw"}
    response = client.post(f"{config.API_PREFIX}{config.REGISTER_URI}", json=payload)
    assert response.status_code == 201
    assert response.headers.get(config.AUTH_HEADER) is not None
    assert isuuid(response.headers.get(config.AUTH_HEADER))
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
    assert isuuid(response.json().get(config.AUTH_HEADER)), "not a token"


def test_login_user_with_invalid_credentials(client: TestClient):
    payload = {"email": "bob@bob.inc", "password": "bobpw"}
    response = client.post(f"{config.API_PREFIX}{config.LOGIN_URI}", json=payload)
    assert response.status_code == 401


def test_rotate_token(client, session):
    user = UserEntity(email="jack@local.host", password="jackpw")
    session.add(user)
    session.commit()
    session.refresh(user)

    headers = {config.AUTH_HEADER: str(user.token)}
    response = client.post(
        f"{config.API_PREFIX}{config.REFRESH_TOKEN_URI}", headers=headers
    )
    assert response.status_code == 200
    refreshed_token = response.json().get(config.AUTH_HEADER)
    assert isuuid(refreshed_token), "not a token"
    assert refreshed_token != user.token
