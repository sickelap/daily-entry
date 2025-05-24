from typing import Annotated, Optional

from app.db import get_db
from app.model import User
from fastapi import Depends, Header
from sqlalchemy import Engine
from sqlmodel import Session, select


def get_user(
    db: Annotated[Engine, Depends(get_db)],
    token: Annotated[str | None, Header()] = None,
) -> Optional[User]:
    if not token:
        return None
    with Session(db) as session:
        stmt = select(User).where(User.token == token)
        return session.exec(stmt).one_or_none()
