from app.db import engine, get_session
from sqlmodel import Session


def test_get_session_returns_sesssion():
    actual = next(get_session())
    assert isinstance(actual, Session)
    assert actual.get_bind() == engine
