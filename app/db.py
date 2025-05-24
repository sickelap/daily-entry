import os

from sqlmodel import SQLModel, create_engine

from .model import *

DB_DSN = os.getenv("DB_DSN", "sqlite:///db.sqlite3")

engine = create_engine(DB_DSN, echo=True)


def get_db():
    return engine


SQLModel.metadata.create_all(engine)
