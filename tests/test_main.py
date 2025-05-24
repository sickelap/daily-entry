from uuid import uuid4

import pytest
from app.config import AUTH_HEADER
from app.db import get_db
from app.main import app
from app.model import Stats, User
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

VALID_TOKEN = "11111111-1111-1111-1111-111111111111"
INVALID_TOKEN = "00000000-0000-0000-0000-000000000000"


@pytest.fixture(scope="session")
def engine():
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(_engine)
    app.dependency_overrides[get_db] = lambda: _engine
    yield _engine
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client(engine):
    with Session(engine) as session:
        session.add(User(id=uuid4(), token=VALID_TOKEN))
        session.commit()
    return TestClient(app)


def test_get_stats_anonymous(client):
    response = client.get("/stats")
    assert response.status_code == 403


def test_get_stats_with_token(client):
    response = client.get("/stats", headers={AUTH_HEADER: VALID_TOKEN})
    assert response.status_code == 200


def test_get_stats_with_invalid_token(client):
    response = client.get("/stats", headers={AUTH_HEADER: INVALID_TOKEN})
    assert response.status_code == 403


def test_add_stat(client, engine):
    headers = {AUTH_HEADER: VALID_TOKEN}
    payload = {"value": 80.0}
    response = client.post("/stats", headers=headers, json=payload)
    assert response.status_code == 200
    with Session(engine) as session:
        stats = session.exec(
            select(Stats).join(User).where(User.token == VALID_TOKEN)
        ).all()
    assert stats is not None


def test_add_stat_using_invalid_token(client):
    headers = {AUTH_HEADER: INVALID_TOKEN}
    payload = {"value": 80.0}
    response = client.post("/stats", headers=headers, json=payload)
    assert response.status_code == 403
