from uuid import uuid4

import pytest
from app.db import get_db
from app.main import app
from app.model import User
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

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
