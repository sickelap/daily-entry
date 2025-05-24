import os

from app.model import *  # noqa
from sqlmodel import Session, SQLModel, create_engine

DB_DSN = os.getenv("DB_DSN", "sqlite:///db.sqlite3")

engine = create_engine(DB_DSN, echo=True)


def get_session():
    with Session(engine) as session:
        yield session


SQLModel.metadata.create_all(engine)
