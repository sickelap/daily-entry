from uuid import UUID, uuid4

import pytest
from app.db import get_session
from app.main import app
from app.model import User
from app.service import hash_password
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

VALID_TOKEN = "bf9cf100-5ea6-485f-be35-4ccedc6ddc84"
INVALID_TOKEN = "00000000-0000-0000-0000-000000000000"
TEST_USER_EMAIL = "test@email.com"
TEST_USER_PASSWORD = "testpw"


@pytest.fixture(scope="session")
def session():
    _engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(_engine)
    with Session(_engine) as session:
        app.dependency_overrides[get_session] = lambda: session
        yield session
        app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def client(session):
    session.add(
        User(
            id=uuid4(),
            email=TEST_USER_EMAIL,
            password=hash_password(TEST_USER_PASSWORD),
            token=UUID(VALID_TOKEN),
        )
    )
    session.commit()
    return TestClient(app)
