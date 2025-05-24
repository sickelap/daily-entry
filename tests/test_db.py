from app.db import engine, get_db, get_session
from sqlmodel import Session


def test_get_db_returns_engine():
    actual = get_db()
    assert actual == engine


def test_get_session_returns_sesssion():
    actual = next(get_session())
    assert isinstance(actual, Session)
    assert actual.get_bind() == engine
