from typing import Annotated, List, Optional

from app.db import get_db
from app.model import StatAddRequest, StatImportEntry, Stats, User
from fastapi import Depends, Header, HTTPException
from sqlalchemy import Engine
from sqlmodel import Session, select


def get_user(
    db: Annotated[Engine, Depends(get_db)],
    token: Annotated[str | None, Header()] = None,
) -> Optional[User]:
    if not token:
        raise HTTPException(status_code=403)
    with Session(db) as session:
        stmt = select(User).where(User.token == token)
        user = session.exec(stmt).one_or_none()
        if not user:
            raise HTTPException(status_code=403)
        return user


def add_user_stat(db: Engine, user: User, payload: StatAddRequest):
    with Session(db) as session:
        stat = Stats(user=user, value=payload.value)
        session.add(stat)
        session.commit()


def import_user_stats(db: Engine, user: User, payload: List[StatImportEntry]):
    with Session(db) as session:
        for entry in payload:
            stat = Stats(user=user, value=entry.value, timestamp=entry.timestamp)
            session.add(stat)
        session.commit()
