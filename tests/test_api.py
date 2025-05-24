from uuid import UUID

from app.config import AUTH_HEADER
from app.model import Stats, User
from dateutil import parser
from fastapi.testclient import TestClient
from sqlmodel import Session, select
from tests.conftest import (
    INVALID_TOKEN,
    TEST_USER_EMAIL,
    TEST_USER_PASSWORD,
    VALID_TOKEN,
)


def isuuid(value: str) -> bool:
    try:
        UUID(value)
        return True
    except Exception:
        return False


def test_get_stats_anonymous(client):
    response = client.get("/stats")
    assert response.status_code == 403


def test_get_stats_with_token(client):
    response = client.get("/stats", headers={AUTH_HEADER: VALID_TOKEN})
    assert response.status_code == 200


def test_get_stats_with_invalid_token(client):
    response = client.get("/stats", headers={AUTH_HEADER: INVALID_TOKEN})
    assert response.status_code == 403


def test_add_stat(client, session):
    headers = {AUTH_HEADER: VALID_TOKEN}
    payload = {"value": 123.4}
    response = client.post("/stats", headers=headers, json=payload)
    assert response.status_code == 200
    stats = session.exec(
        select(Stats).join(User).where(User.token == UUID(VALID_TOKEN))
    ).all()
    assert stats is not None
    assert len(stats) == 1
    assert float(stats[0].value) == 123.4


def test_import_stats(client, session):
    headers = {AUTH_HEADER: VALID_TOKEN}
    payload = [
        {"timestamp": 1, "value": 123.4},
        {"timestamp": 2, "value": 123.5},
        {"timestamp": 3, "value": 123.6},
    ]
    response = client.post("/import", headers=headers, json=payload)
    assert response.status_code == 200
    stats_in_db = session.exec(
        select(Stats).join(User).where(User.token == UUID(VALID_TOKEN))
    ).all()
    assert stats_in_db is not None
    assert len(stats_in_db) == len(payload)
    for index, entry in enumerate(payload):
        assert entry["timestamp"] == stats_in_db[index].timestamp
        assert entry["value"] == float(stats_in_db[index].value)


def test_import_stats_with_string_timestamps(client, session):
    headers = {AUTH_HEADER: VALID_TOKEN}
    payload = [
        {"timestamp": "01/11/2025 08:01:55", "value": 123.4},
        {"timestamp": "02/11/2025 09:19:28", "value": 123.5},
        {"timestamp": "03/11/2025 10:11:11", "value": 123.6},
    ]
    response = client.post("/import", headers=headers, json=payload)
    assert response.status_code == 200
    stats_in_db = session.exec(
        select(Stats).join(User).where(User.token == UUID(VALID_TOKEN))
    ).all()
    assert stats_in_db is not None
    assert len(stats_in_db) == len(payload)
    for index, entry in enumerate(payload):
        parsed_timestamp = int(
            parser.parse(entry["timestamp"], dayfirst=True).timestamp()
        )
        assert parsed_timestamp == stats_in_db[index].timestamp
        assert entry["value"] == float(stats_in_db[index].value)


def test_register_user(client: TestClient, session: Session):
    payload = {"email": "user@local.host", "password": "userpw"}
    response = client.post("/register", json=payload)
    assert response.status_code == 201
    assert response.headers.get(AUTH_HEADER) is not None
    assert isuuid(response.headers.get(AUTH_HEADER))
    user_in_db = session.exec(
        select(User).where(User.email == "user@local.host")
    ).one_or_none()
    assert user_in_db is not None


def test_register_user_with_same_email(client: TestClient):
    payload = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    response = client.post("/register", json=payload)
    assert response.status_code == 409


def test_login_user(client: TestClient):
    payload = {"email": TEST_USER_EMAIL, "password": TEST_USER_PASSWORD}
    response = client.post("/token", json=payload)
    assert response.status_code == 200
    assert isuuid(response.json().get(AUTH_HEADER)), "not a token"


def test_login_user_with_invalid_credentials(client: TestClient):
    payload = {"email": "bob@bob.inc", "password": "bobpw"}
    response = client.post("/token", json=payload)
    assert response.status_code == 401


def test_rotate_token(client: TestClient):
    headers = {AUTH_HEADER: VALID_TOKEN}
    response = client.post("/token/rotate", headers=headers)
    assert response.status_code == 200
    refreshed_token = response.json().get(AUTH_HEADER)
    assert isuuid(refreshed_token), "not a token"
    assert refreshed_token != VALID_TOKEN
