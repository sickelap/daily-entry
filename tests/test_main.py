from uuid import uuid4

import pytest
from app.config import AUTH_HEADER
from app.db import get_db
from app.main import app
from app.model import Stats, User
from dateutil import parser
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine, select

VALID_TOKEN = "11111111-1111-1111-1111-111111111111"
INVALID_TOKEN = "00000000-0000-0000-0000-000000000000"


@pytest.fixture
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


@pytest.fixture
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
    payload = {"value": 123.4}
    response = client.post("/stats", headers=headers, json=payload)
    assert response.status_code == 200
    with Session(engine) as session:
        stats = session.exec(
            select(Stats).join(User).where(User.token == VALID_TOKEN)
        ).all()
        assert stats is not None
        assert len(stats) == 1
        assert float(stats[0].value) == 123.4


def test_import_stats(client, engine):
    headers = {AUTH_HEADER: VALID_TOKEN}
    payload = [
        {"timestamp": 1, "value": 123.4},
        {"timestamp": 2, "value": 123.5},
        {"timestamp": 3, "value": 123.6},
    ]
    response = client.post("/import", headers=headers, json=payload)
    assert response.status_code == 200
    with Session(engine) as session:
        stats_in_db = session.exec(
            select(Stats).join(User).where(User.token == VALID_TOKEN)
        ).all()
        assert stats_in_db is not None
        assert len(stats_in_db) == len(payload)
        for index, entry in enumerate(payload):
            assert entry["timestamp"] == stats_in_db[index].timestamp
            assert entry["value"] == float(stats_in_db[index].value)


def test_import_stats_with_string_timestamps(client, engine):
    headers = {AUTH_HEADER: VALID_TOKEN}
    payload = [
        {"timestamp": "01/11/2025 08:01:55", "value": 123.4},
        {"timestamp": "02/11/2025 09:19:28", "value": 123.5},
        {"timestamp": "03/11/2025 10:11:11", "value": 123.6},
    ]
    response = client.post("/import", headers=headers, json=payload)
    assert response.status_code == 200
    with Session(engine) as session:
        stats_in_db = session.exec(
            select(Stats).join(User).where(User.token == VALID_TOKEN)
        ).all()
        assert stats_in_db is not None
        assert len(stats_in_db) == len(payload)
        for index, entry in enumerate(payload):
            parsed_timestamp = int(
                parser.parse(entry["timestamp"], dayfirst=True).timestamp()
            )
            assert parsed_timestamp == stats_in_db[index].timestamp
            assert entry["value"] == float(stats_in_db[index].value)
