from app.db import engine, get_db


def test_get_db_returns_engine():
    actual = get_db()
    assert actual == engine
